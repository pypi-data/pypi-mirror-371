
import alphaquant.diffquant.diffutils as aqutils
import pathlib
import alphaquant.multicond.multicond_ptmnorm as aq_multicond_ptmnorm
import statsmodels.stats.multitest as mt
import alphaquant.resources.database_loader as aq_resource_dbloader

import alphaquant.config.config as aqconfig
import logging
aqconfig.setup_logging()
LOGGER = logging.getLogger(__name__)



class PTMResultsNormalizer():
    def __init__(self, results_dir_ptm, results_dir_proteome, organism = "human"):
        self._table_localizer = PTMtableLocalizer(results_dir_ptm, results_dir_proteome, organism)
        self.results_dir_protnormed = f"{results_dir_ptm}_protnormed"
        self._create_results_dir()
        self._write_normalized_tables_diffquant(organism)
        self._write_normalized_tables_multicond()
        LOGGER.info(f"wrote proteome normalized tables to: {self.results_dir_protnormed}")

    def _write_normalized_tables_diffquant(self, organism):
        for ptm_file, protfile in self._table_localizer.get_ptmfile2protfile().items():
            if protfile == None:
                LOGGER.info(f"could not localize protfile for {ptm_file}, skipping")
                continue
            table_normalizer = PTMtableNormalizer(ptm_file, protfile, organism)
            df_normed = table_normalizer.results_df
            if len(df_normed.index)> 0:
                df_summary = table_normalizer.info_df
                df_normed = self._update_fdr_column_normed_df(df_normed)
                self._write_normed_df(df_normed, ptm_file)
                self._write_summary_df(df_summary, ptm_file)

    def _write_normalized_tables_multicond(self):
        aq_multicond_ptmnorm.combine_results_tables_if_they_exist(self.results_dir_protnormed)


    def _create_results_dir(self):
        aqutils.create_or_replace_folder(self.results_dir_protnormed)

    def _update_fdr_column_normed_df(self, df_normed):
        pvals = df_normed["p_value"].tolist()
        fdrs = mt.multipletests(pvals, method='fdr_bh', is_sorted=False, returnsorted=False)[1]
        df_normed["fdr"] = fdrs
        return df_normed


    def _write_normed_df(self,df_normed, ptmfile):
        ptmfile2name = self._table_localizer.get_ptmfile2name()
        name = ptmfile2name.get(ptmfile)
        df_normed.to_csv(f"{self.results_dir_protnormed}/{name}.results.tsv", sep = "\t")

    def _write_summary_df(self,df_summary, ptmfile):
        ptmfile2name = self._table_localizer.get_ptmfile2name()
        name = ptmfile2name.get(ptmfile)
        df_summary.to_csv(f"{self.results_dir_protnormed}/{name}.summary.tsv", sep = "\t", header = False)


class PTMtableLocalizer():
    def __init__(self, results_dir_ptm, results_dir_proteome, organism = "human"):
        self._files = PTMFiles(results_dir_ptm=results_dir_ptm, results_dir_proteome=results_dir_proteome, organism=organism)
        self._name2ptmfile = self._get_name2ptmfile()
        self._name2protfile = self._get_name2protfile()

    def get_ptmfile2protfile(self):
        phosfile2protfile = {self._name2ptmfile.get(x): self._name2protfile.get(x) for x in self._name2ptmfile.keys()}
        return phosfile2protfile

    def get_ptmfile2name(self):
        return {v: k for k, v in self._name2ptmfile.items()}


    def _get_name2ptmfile(self):
        return self._get_name2file(self._files.ptm_result_files)

    def _get_name2protfile(self):
        return self._get_name2file(self._files.proteome_result_files)

    @staticmethod
    def _get_name2file(filenames):
        name2file = {}
        for file in filenames:
            path = pathlib.Path(file)
            if path.name.endswith('.results.tsv'):
                name = path.name.replace('.results.tsv', '')
                name2file.update({name: file})
        return name2file


import alphaquant.ptm.ptmsite_mapping as aqptm
class PTMFiles():
    def __init__(self, results_dir_ptm, results_dir_proteome, organism = "human"):
        self._results_dir_ptm = results_dir_ptm
        self._results_dir_proteome = results_dir_proteome
        self._organism = organism

        self.ptm_result_files = self._get_ptm_result_files()
        self.proteome_result_files = self._get_proteome_result_files()

    def _get_ptm_result_files(self):
        return glob.glob(f'{self._results_dir_ptm}/*.results.tsv')

    def _get_proteome_result_files(self):
        return glob.glob(f'{self._results_dir_proteome}/*.results.tsv')

class PTMtableNormalizer():
    def __init__(self,  ptm_file, proteome_file, organism = "human"):
        self._prepared_tables = PTMtablePreparer(ptm_file, proteome_file, organism)
        self.results_df = self._prepared_tables.ptm_df.copy() #use ptm table as template for the output table and update with normalized fcs and p_values
        self.info_df = None

        self._number_of_excluded_ptms = 0
        self._number_of_included_ptms = 0

        self._normalize_with_proteome()
        self._define_info_df()

    def _normalize_with_proteome(self):
        for ptm in self.results_df.index:
            self._update_ptm_infos(ptm)

    def _define_info_df(self):
        info_dict = {}
        info_dict["number_ptms_w_no_matching_protein"] = self._number_of_excluded_ptms
        info_dict["number_ptms_w_matching_protein"] = len(self.results_df.index)
        info_dict["number_proteins_in_ptm_dataset"] = len(set([x.split("_")[1] for x in self._prepared_tables.ptm_df.index]))
        info_dict["number_proteins_in_proteome_dataset"] = self._prepared_tables.proteome_df.shape[0]
        self.info_df = pd.DataFrame.from_dict(info_dict, orient = "index", columns = ["value"])

    def _update_ptm_infos(self, ptm):
        regulation_infos = self._prepared_tables.get_protein_regulation_infos(ptm)
        if regulation_infos is None:
            self.results_df = self.results_df.drop(labels = [ptm])
            self._number_of_excluded_ptms += 1
        else:
            p_value_damper = PvalDamper(regulation_infos)
            dampened_p_value = p_value_damper.get_p_value()
            self._update_values_for_output_table(ptm, dampened_p_value, regulation_infos.diff_fc)


    def _update_values_for_output_table(self, ptm, dampened_p_value, log2fc):
        self.results_df.loc[ptm, "p_value"] = dampened_p_value
        self.results_df.loc[ptm, "log2fc"] = log2fc

    def __get_ptm_list__(self):
        list(self._prepared_tables.ptm_df.index)


# Cell
import glob
import re
import pandas as pd
class PTMtablePreparer():
    def __init__(self, ptm_file, proteome_file, organism):

        self.ptm_df = pd.read_csv(ptm_file, sep = "\t")
        self.proteome_df = pd.read_csv(proteome_file, sep = "\t")
        self._organism = organism
        self._map_ids_proteome_df_to_ptm_df()
        self.output_df = self.ptm_df.copy()


    def _map_ids_proteome_df_to_ptm_df(self):
        id_mapper = ProteinToPTMMapper(self.ptm_df, self.proteome_df, self._organism)
        self.ptm_df = id_mapper.ptm_df.set_index("protein")
        self.proteome_df = id_mapper.proteome_df.set_index("gene")


    def get_protein_regulation_infos(self, ptmsite):
        ptm_row = self.ptm_df.loc[ptmsite]
        gene_name = ptm_row["gene"]
        if gene_name not in self.proteome_df.index:
            return None
        protein_rows = self.proteome_df.loc[[gene_name]] #the proteome df is indexed by the gene name that maps to the ptm
        if len(protein_rows.index) >1:
            LOGGER.warning(f"more than one match found for gene {gene_name}, excluding ptm {ptmsite} from normalization as this might be due to ambiguous gene names")
            return None
        protein_row = protein_rows.iloc[0]

        ptm_p_value = self._get_p_value_from_table_row(ptm_row)
        ptm_fc = self._get_fc_from_table_row(ptm_row)
        protein_p_value = self._get_p_value_from_table_row(protein_row)
        protein_fc = self._get_fc_from_table_row(protein_row)
        reginfos = RegulationInfos(log2fc_ptm=ptm_fc, p_value_ptm=ptm_p_value, log2fc_protein=protein_fc,p_value_protein=protein_p_value)

        return reginfos



    @staticmethod
    def _match_ptm_df_to_ptm_prots(ptm_df,ptm_prots):
        return ptm_df[[x != None for x in ptm_prots]]

    @staticmethod
    def _get_p_value_from_table_row(row):
        return float(row["p_value"])

    @staticmethod
    def _get_fc_from_table_row(row):
        return float(row["log2fc"])


class ProteinToPTMMapper():
    def __init__(self, ptm_df, proteome_df, organism):
        """both PTM and proteome df get a "gene" column. The uniprot synonyms are used to map the gene names in the proteome df to the PTM df
        """
        self.ptm_df = ptm_df
        self.proteome_df = proteome_df

        self._gene2reference = None #gene2reference maps every variation of a gene name to a reference gene name. This way, differing gene names in the two dataframes can still be mapped
        self._organism = organism

        self._define_gene2reference_dict()
        self._add_genename_column_ptm_df()
        self._map_gene_names_in_proteome_df_to_ptm_df()


    def _define_gene2reference_dict(self):
        uniprot_file = aq_resource_dbloader.get_uniprot_path(organism=self._organism)
        uniprot_gene_names_str = pd.read_csv(uniprot_file, sep = "\t")["Gene Names"].astype(str).to_list()
        uniprot_gene_names = [x.split(" ") for x in uniprot_gene_names_str]
        gene2synonyms_mapping_dict = {}
        for gene_list in uniprot_gene_names:
            for gene in gene_list:
                gene2synonyms_mapping_dict[gene] = gene_list
        self._gene2reference = self._invert_gene2synonyms_mapping_dict(gene2synonyms_mapping_dict)

    @staticmethod
    def _invert_gene2synonyms_mapping_dict(gene2sysnonyms_subset):
        inverted_dict = {}
        for key, value_list in gene2sysnonyms_subset.items():
            for item in value_list:
                inverted_dict[item] = key  # Map each list element back to the reference gene (key)
        return inverted_dict

    def _add_genename_column_ptm_df(self):
        self.ptm_df["gene"] = self._get_ptm_proteins(self.ptm_df)
        self.ptm_df = self.ptm_df[[x != None for x in self.ptm_df["gene"]]]
        return self.ptm_df

    def _get_ptm_proteins(self, ptm_df):
        genes = []
        for ptm_id in ptm_df["protein"]:
            gene = self._extract_gene_from_ptmname(ptm_id)
            genes.append(gene)
        return genes

    @staticmethod
    def _extract_gene_from_ptmname(ptm_id):
        if ptm_id == None:
            return None
        elif len(ptm_id.split("_"))<2:
            return None
        else:
            return ptm_id.split("_")[0]

    def _map_gene_names_in_proteome_df_to_ptm_df(self):
        self.proteome_df["gene"] = self.proteome_df["protein"] #The proteome df has a column "protein" that contains the gene names. This is because "protein" is the general identifier for the thing that all peptides are mapped to.
        genes_ptm = set(self.ptm_df["gene"])
        genes_proteome = set(self.proteome_df["gene"])
        if len(set(self._gene2reference.keys()).intersection(genes_proteome)) <2:
            LOGGER.warning("virtually no overlap between gene names in the proteome and uniprot gene names. Please double check that gene symbols were used as protein identifiers the proteome dataset. Additionally, check that the organism is correct.")

        intersecting_genes = genes_ptm.intersection(genes_proteome)
        unmapped_genes_ptm = genes_ptm - intersecting_genes

        #map the unmapped genes in the PTM dataset to the reference gene names. This might recover some of the genes that were not mapped in the first round
        unmapped_mask_proteome = self.proteome_df["gene"].isin(unmapped_genes_ptm)
        unmapped_mask_ptm = self.ptm_df["gene"].isin(unmapped_genes_ptm)



        self.proteome_df.loc[unmapped_mask_proteome, "gene"] = self.proteome_df.loc[unmapped_mask_proteome, "gene"].map(self._gene2reference)
        self.ptm_df.loc[unmapped_mask_ptm, "gene"] = self.ptm_df.loc[unmapped_mask_ptm, "gene"].map(self._gene2reference)

        genes_ptm_round2 = set(self.ptm_df["gene"])
        genes_proteome_round2 = set(self.proteome_df["gene"])
        intersecting_genes_round2 = genes_ptm_round2.intersection(genes_proteome_round2)

        self.proteome_df = self.proteome_df[self.proteome_df["gene"].isin(intersecting_genes_round2)]

        LOGGER.info(f"{len(intersecting_genes_round2)} of {len(genes_ptm_round2)} genes in PTM dataset could be mapped to the proteome dataset.")




# Cell
import math
import numpy as np

class RegulationInfos():
    def __init__(self, log2fc_ptm, p_value_ptm,log2fc_protein, p_value_protein):
        self.log2fc_ptm = log2fc_ptm
        self.log2fc_protein = log2fc_protein
        self.p_value_ptm = p_value_ptm
        self.p_value_protein = p_value_protein
        self.diff_fc = self._get_protnormed_fc()
        self.switched_regulation_direction = not self._check_if_regulation_stayed_the_same()

    def _get_protnormed_fc(self):
        return self.log2fc_ptm - self.log2fc_protein

    def _check_if_regulation_stayed_the_same(self):
        return np.sign(self.log2fc_ptm) == np.sign(self.diff_fc)



import math
class PvalDamper():
    """The p_value is taken from the regulation of the phosphopeptides. If the protein is regulated
    similar to the phosphopeptide, we for the moment use a very simple heuristic to correct the p_value down:

    1) We only consider phosphopeptides where the fold change has become less strong, i.e. 'dampened' and where the "damping" protein was regulated significantly
    2) We correct the logged(!) p_value up with an exponnential function and then transform it back to a new p_value. This means a exponential decrease in the significance
    """
    def __init__(self, regulation_infos):
        self._regulation_infos = regulation_infos

    def get_p_value(self):
        return self._dampen_p_value_if_needed()

    def _dampen_p_value_if_needed(self):
        if self._check_if_needs_damping():
            return self._get_adjusted_p_value()
        else:
            return self._regulation_infos.p_value_ptm

    def _check_if_needs_damping(self):
        if self._regulation_infos.p_value_protein<0.05:
            if np.sign(self._regulation_infos.log2fc_ptm) == np.sign(self._regulation_infos.log2fc_protein):
                return True
        return False

    def _get_adjusted_p_value(self):
        if self._regulation_infos.switched_regulation_direction:
            return 1.0
        else:
            return self._calculate_damping_factor()

    def _calculate_damping_factor(self):
        factor = self._calculate_order_of_magnitude_damping_factor()
        p_value_new = 10**(math.log10(self._regulation_infos.p_value_ptm)*factor)
        return min(p_value_new, 1)

    def _calculate_order_of_magnitude_damping_factor(self):
        ratio_old_new = self._regulation_infos.diff_fc/self._regulation_infos.log2fc_ptm #must be smaller than 1
        return ratio_old_new
