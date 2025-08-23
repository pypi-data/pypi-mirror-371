import param
import panel as pn
import pandas as pd
import os
import itertools
import glob
import re

import alphaquant.plotting.fcviz as aq_plot_fcviz
import alphaquant.plotting.alphamapviz as aq_plot_proteoform
import alphaquant.utils.proteoform_utils as aq_proteoform_utils
import alphaquant.config.variables as aq_variables
import alphaquant.ui.dashboad_parts_utils as aq_dashboard_utils

class ProteoformPlottingTab(param.Parameterized):
    """
    A param-based Panel class for proteoform visualization.
    """
    # Public Parameters
    results_dir = param.String(doc="Path to the results folder containing *_VS_*.results.tsv files")
    samplemap_file = param.String(doc="Path to the samplemap file")

    # Dynamic widgets
    condpairname_select = param.ClassSelector(class_=pn.widgets.Select)
    protein_input = param.ClassSelector(class_=pn.widgets.AutocompleteInput)

    # Add new parameter for the selected proteoform
    selected_proteoform = param.String(default='')

    # Add new widgets for organism and protein identifier
    organism_select = pn.widgets.Select(
        name="Organism",
        options=['Human', 'Mouse', 'Yeast'],
        value='Human',
        width=200
    )

    protein_id_select = pn.widgets.Select(
        name="Protein Identifier",
        options=['gene_symbol', 'uniprot_id'],
        value='gene_symbol',
        width=200
    )

    # Add load button
    load_button = pn.widgets.Button(
        name="Load Selected Condition Pair",
        button_type="primary",
        width=200,
        disabled=True  # Start disabled
    )

    def __init__(self, state, **params):
        super().__init__(**params)
        self.state = state

        # Create all widgets first
        self.condpairname_select = pn.widgets.Select(
            name="Select Condition Pair",
            options=["No conditions"],
            width=300
        )

        # Add Plot Protein button
        self.plot_protein_button = pn.widgets.Button(
            name="Plot Protein",
            button_type="primary",
            width=200,
            disabled=True  # Start disabled
        )
        self.plot_protein_button.on_click(self._on_plot_protein_clicked)

        # Add load button
        self.load_button = pn.widgets.Button(
            name="Load Selected Condition Pair",
            button_type="primary",
            width=200,
            disabled=True  # Start disabled
        )
        self.load_button.on_click(self._on_load_button_clicked)

        self.protein_input = pn.widgets.AutocompleteInput(
            name='Select Protein',
            placeholder="Type protein name or click a row in the table above to visualize peptide fold changes...",
            min_characters=0,
            disabled=True,
            width=400,
            margin=(5, 5, 5, 5)
        )
        self.protein_input.param.watch(self._on_protein_selected, 'value')


        # Input fields for paths
        self.results_dir_input = pn.widgets.TextInput(
            name='Results Directory:',
            value=self.results_dir,
            placeholder='Enter path to results directory',
            width=600
        )
        self.results_dir_input.param.watch(self.on_results_dir_changed, 'value')

        # Add proteoform table
        self.proteoform_table = pn.widgets.Tabulator(
            pagination='remote',
            page_size=10,
            sizing_mode='stretch_width',
            height=300,
            selectable=1,
            selection=[],
            show_index=False,
        )
        self.proteoform_table.on_click(self._on_proteoform_selected)

        # Plot panes
        self.proteoform_plot_pane = pn.Column(
            pn.pane.Markdown("### Visualization will appear here when you Plot Protein"),
            sizing_mode='stretch_width'
        )

        # Create container for elements that should be hidden initially AFTER all widgets are created
        self.table_warning_pane = pn.pane.Markdown("", sizing_mode='stretch_width')  # Warning pane for table
        self.viz_warning_pane = pn.pane.Markdown("", sizing_mode='stretch_width')    # Warning pane for visualization

        # Add second load button for AlphaMap
        self.load_alphamap_button = pn.widgets.Button(
            name="Initialize AlphaMap",
            button_type="primary",
            width=300,
            disabled=True
        )
        self.load_alphamap_button.on_click(self._on_load_alphamap_clicked)

        # Add loading indicator
        self.loading_indicator = pn.indicators.LoadingSpinner(
            value=False,
            size=20,  # Small size
            color='primary',
            visible=False
        )

        # Create a separate container for visualization elements
        self.visualization_elements = pn.Column(
            self.protein_input,
            pn.Row(self.plot_protein_button),
            self.proteoform_plot_pane,
            visible=False
        )

        # Add section titles
        self.proteoform_section_title = pn.pane.Markdown(
            "## Proteoform Overview",
            sizing_mode='stretch_width'
        )

        self.visualization_section_title = pn.pane.Markdown(
            "## Detail Plots",
            sizing_mode='stretch_width'
        )


        self.hidden_elements = pn.Column(
            self.proteoform_section_title,
            self.proteoform_table,
            self.table_warning_pane,
            pn.layout.Divider(),
            self.visualization_section_title,
            pn.Row(self.organism_select, self.protein_id_select),
            pn.Row(self.load_alphamap_button, self.loading_indicator),
            self.viz_warning_pane,
            self.visualization_elements,
            visible=False
        )

        # Construct layout
        self.main_layout = pn.Column(
            "## Outlier Peptide Visualization",
            self.results_dir_input,
            self.samplemap_file,
            self.condpairname_select,
            self.load_button,
            pn.layout.Divider(),
            self.hidden_elements,
            sizing_mode='stretch_width'
        )

        # Initialize if directory provided
        self._extract_cond_pairs()

    def panel(self):
        """Return the main panel layout."""
        return self.main_layout

    def on_results_dir_changed(self, event):
        """Handle changes to results directory."""
        print("\n=== Proteoform Plot: Results Dir Changed ===")
        print(f"Received event type: {type(event)}")
        print(f"Received event value: {event}")
        if hasattr(event, 'new'):
            print(f"Event has 'new' attribute: {event.new}")
        if event.new:
            self.results_dir = event.new
            self.samplemap_file = aq_dashboard_utils.get_samplemap_file_path(self.results_dir)
            self._extract_cond_pairs()
        print("=== Finished Handling Results Dir Change ===\n")

    def _extract_cond_pairs(self):
        """Look for '*_VS_*.proteoforms.tsv' in the results_dir and update the condition pairs."""
        if not self.results_dir or not os.path.isdir(self.results_dir):
            self.condpairname_select.options = ["No conditions"]
            self.load_button.disabled = True  # Disable button
            return

        pattern = os.path.join(self.results_dir, f"*{aq_variables.CONDITION_PAIR_SEPARATOR}*.proteoforms.tsv")
        files = glob.glob(pattern)

        cond_pairs = []
        for f in files:
            basename = os.path.basename(f)
            match = re.match(f'(.*?){aq_variables.CONDITION_PAIR_SEPARATOR}(.*?)\.proteoforms\.tsv$', basename)
            if match:
                cond1, cond2 = match.group(1), match.group(2)
                cond_pairs.append((cond1, cond2))

        if cond_pairs:
            pairs_str = [f"{c1}{aq_variables.CONDITION_PAIR_SEPARATOR}{c2}" for c1, c2 in cond_pairs]
            self.condpairname_select.options = ["No conditions"] + pairs_str
            self.load_button.disabled = False  # Enable button when pairs are available
        else:
            self.condpairname_select.options = ["No conditions"]
            self.load_button.disabled = True  # Disable button

    def _on_load_button_clicked(self, event):
        """Handle load button click."""
        if not self.condpairname_select.value or self.condpairname_select.value == "No conditions":
            return

        try:
            condition1, condition2 = self.condpairname_select.value.split(aq_variables.CONDITION_PAIR_SEPARATOR)
            results_file = os.path.join(
                self.results_dir,
                f"{condition1}{aq_variables.CONDITION_PAIR_SEPARATOR}{condition2}.proteoforms.tsv"
            )

            # Load and filter proteoforms
            proteoforms_df = pd.read_csv(results_file, sep='\t')
            filtered_df = aq_proteoform_utils.filter_proteoform_df(proteoforms_df)

            # Drop specified columns
            columns_to_drop = ['is_reference', 'peptides', 'log2fc',
                             'proteoform_pval', 'proteoform_fcfc', 'fcdiff',
                             'proteoform_fdr']
            filtered_df = filtered_df.drop(columns=[col for col in columns_to_drop if col in filtered_df.columns])

            # Update table
            self.proteoform_table.value = filtered_df

            # Update protein input options
            protein_ids = filtered_df['protein'].unique().tolist()
            self.protein_input.options = protein_ids
            self.protein_input.disabled = False

            # Show the hidden elements and enable AlphaMap button
            self.hidden_elements.visible = True
            self.load_alphamap_button.disabled = False
            self.visualization_elements.visible = False  # Keep visualization hidden until AlphaMap button is clicked

        except Exception as e:
            print("Error occurred:", str(e))
            print("Exception type:", type(e))
            import traceback
            print("Traceback:", traceback.format_exc())
            self.protein_input.disabled = True
            self.protein_input.options = []
            error_msg = f"Error loading proteoforms file: {str(e)}"
            self.proteoform_plot_pane.clear()
            self.proteoform_plot_pane.append(pn.pane.Markdown(f"### Error\n{error_msg}"))
            # Keep hidden elements invisible if data loading failed
            self.hidden_elements.visible = False
            self.load_alphamap_button.disabled = True
            self.visualization_elements.visible = False

    def _on_condpair_selected(self, event):
        """Handle condition pair selection."""
        # Reset visibility when condition pair changes
        self.hidden_elements.visible = False

    def _on_protein_selected(self, event):
        """Handle protein selection."""
        if event.new:
            # Enable the Plot Protein button when a protein is selected
            self.plot_protein_button.disabled = False
            # Clear existing plots
            self.proteoform_plot_pane.clear()
            self.proteoform_plot_pane.append(pn.pane.Markdown("### Click 'Plot Protein' to visualize the data"))

    def _update_condition_pairs_from_df(self, df):
        """Update condition pairs based on the samplemap DataFrame."""
        if 'condition' in df.columns:
            unique_conditions = df['condition'].dropna().unique()
            pairs = [(c1, c2) for c1, c2 in itertools.permutations(unique_conditions, 2)]
            pairs_str = [f"{c1}{aq_variables.CONDITION_PAIR_SEPARATOR}{c2}" for c1, c2 in pairs]
            self.condpairname_select.options = ["No conditions"] + pairs_str

    def _load_protein_identifiers(self, results_file):
        """Load protein identifiers from results file and update the protein input widget."""
        try:
            proteoforms_df = pd.read_csv(results_file, sep='\t')
            protein_ids = sorted(proteoforms_df['gene_symbol'].unique().tolist())
            self.protein_input.options = protein_ids
            self.protein_input.disabled = False
            return protein_ids
        except Exception as e:
            self.protein_input.disabled = True
            self.protein_input.options = []
            raise Exception(f"Failed to load protein identifiers: {str(e)}")

    def _on_proteoform_selected(self, event):
        """Handle proteoform selection from table."""
        print(f"_on_proteoform_selected called with event: {event}")
        print(f"Event type: {type(event)}")
        print(f"Event attributes: {dir(event)}")

        if hasattr(event, 'row'):
            print(f"Row index: {event.row}")
            row_data = self.proteoform_table.value.iloc[event.row]
            print(f"Row data: {row_data}")
            selected_protein = row_data.get('protein')
            print(f"Selected protein: {selected_protein}")

            if selected_protein:
                print("Setting protein_input.value...")
                # Just update the value and let the existing watcher handle it
                self.protein_input.value = selected_protein

    def _on_load_alphamap_clicked(self, event):
        """Handle AlphaMap load button click."""
        self.loading_indicator.visible = True  # Show spinner
        self.loading_indicator.value = True

        try:
            # Initialize visualizers
            condition1, condition2 = self.condpairname_select.value.split(aq_variables.CONDITION_PAIR_SEPARATOR)

            self.amap_visualizer = aq_plot_proteoform.AlphaMapVisualizer(
                condition1=condition1,
                condition2=condition2,
                results_directory=self.results_dir,
                samplemap_file=self.samplemap_file,
                protein_identifier=self.protein_id_select.value,
                organism=self.organism_select.value
            )

            self.fc_visualizer = aq_plot_fcviz.FoldChangeVisualizer(
                condition1=condition1,
                condition2=condition2,
                results_directory=self.results_dir,
                samplemap_file=self.samplemap_file,
                organism=self.organism_select.value,
                protein_identifier=self.protein_id_select.value,
                order_along_protein_sequence=True,
                figsize=(6, 4)
            )

            # Show visualization elements
            self.visualization_elements.visible = True
            self.viz_warning_pane.object = ""  # Clear any previous warnings

        except Exception as viz_error:
            print("Error initializing visualizers:", str(viz_error))
            print("Exception type:", type(viz_error))
            import traceback
            print("Traceback:", traceback.format_exc())
            error_msg = "Warning: Visualization features could not be initialized with the selected settings."
            self.viz_warning_pane.object = f"### Note\n{error_msg}"
            self.visualization_elements.visible = False

        finally:
            self.loading_indicator.value = False
            self.loading_indicator.visible = False  # Hide spinner when done

    def _on_plot_protein_clicked(self, event):
        """Handle Plot Protein button click."""
        if not self.protein_input.value:
            return

        # Clear existing plots
        self.proteoform_plot_pane.clear()

        try:
            # Get sequence plot from AlphaMapVisualizer
            _, alphamap_go_fig = self.amap_visualizer.visualize_protein(self.protein_input.value)

            # Get fold change plot from FoldChangeVisualizer
            fc_fig = self.fc_visualizer.plot_protein(self.protein_input.value)

            # Add both plots to the pane
            if fc_fig:
                self.proteoform_plot_pane.append(pn.pane.Matplotlib(fc_fig, tight=True))
            if alphamap_go_fig:
                self.proteoform_plot_pane.append(pn.pane.Plotly(alphamap_go_fig))
        except AttributeError:
            # This happens if visualizers weren't initialized
            self.proteoform_plot_pane.append(pn.pane.Markdown("### Visualization not available\nVisualization components could not be initialized. Table view is still available."))
        except Exception as e:
            # Handle other potential errors
            self.proteoform_plot_pane.append(pn.pane.Markdown(f"### Error generating visualization, please check that the correct organism and protein identifier are selected\n{str(e)}"))

