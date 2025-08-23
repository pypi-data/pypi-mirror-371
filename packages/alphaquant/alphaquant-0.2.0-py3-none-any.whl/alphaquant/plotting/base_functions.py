
import alphaquant.diffquant.diffutils as utils
import alphaquant.config.variables as aq_variables

# Cell
import pandas as pd
import numpy as np
import matplotlib.colors
import matplotlib.pyplot as plt


class AlphaPeptColorMap():
    def __init__(self):
        self.colorlist_hex  = ["#3FC5F0", "#42DEE1", "#7BEDC5", "#FFD479", "#16212B"]
        self.colorlist = [matplotlib.colors.to_rgba(x) for x in self.colorlist_hex]

        self.colormap_linear = matplotlib.colors.LinearSegmentedColormap.from_list("alphapept",self.colorlist)
        self.colormap_discrete = matplotlib.colors.LinearSegmentedColormap.from_list("alphapept",self.colorlist, N=5)

class ClusterColorMap():
    def __init__(self):
        self.colorlist_hex = [    "#D32F2F",  # Crimson Red
                    "#FFA000",  # Burnt Orange
                    "#FFEB3B",  # Golden Yellow
                    "#4CAF50",  # Grass Green
                    "#00BCD4",  # Cyan Blue
                    "#303F9F",  # Cobalt Blue
                    "#7B1FA2",  # Deep Purple
                    "#E91E63",  # Rose Pink
                    "#795548",  # Mocha Brown
                    "#607D8B"   # Slate Grey
                    ]
        self.colorlist = [matplotlib.colors.to_rgba(x) for x in self.colorlist_hex]

class AlphaPeptColorMapAdapted():
    def __init__(self):
        self.colorlist_hex  =  [
    "#3FB7E4",  # Vivid Sky Blue (Slightly desaturated)
    "#7BEDC5",  # Medium Aquamarine
    "#EBCB70",  # Mustard (Slightly less bright)
    "#16212B",  # Gunmetal
    "#CA9ECB",  # Soft Lilac (Slightly more saturated)
    "#708090",  # Slate Gray
    "#3391A6",  # Deep Cerulean (Slightly lightened)
    "#AEDDE9",  # Powder Blue (Slightly warmer)
    "#5F9EA0",  # Cadet Blue
    "#E77D7D"   # Light Coral (Slightly desaturated)
]
        self.colorlist = [matplotlib.colors.to_rgba(x) for x in self.colorlist_hex]

class AlphaQuantColorMap():
    def __init__(self):
        self.colorlist_hex  = ["#d8674e",  # Cadmium Red
        "#45a6ce",  # Steel Blue
        "#fdb73b",  # Cadmium Yellow
        "#a6d1f1",  # Baby Blue
        "#b04e8d",  # Tiffany Rose
        "#6e79b9",  # Periwinkle
        "#fcdf3b",  # Goldenrod
        "#50C878",  # Emerald Green
        "#808080",  # Grey instead of Amber
        "#FF7F50",  # Coral
        "#0F52BA",  # Egyptian Blue
        "#9966CC",  # Amethyst
        "#40E0D0"   # Turquoise
        ]
        self.colorlist = [matplotlib.colors.to_rgba(x) for x in self.colorlist_hex]


def rgba_list_to_hex_list(rgba_list):
    hex_list = []
    for rgba in rgba_list:
        # Convert each value to a 0-255 scale, then to hex, and finally concatenate.
        hex_code = '#' + ''.join([f"{int(c*255):02X}" for c in rgba[:3]])
        hex_list.append(hex_code)
    return hex_list

# Cell
import matplotlib.pyplot as plt
import numpy as np

def plot_pvals(result_df):
    pvals = result_df["peptide_pval"].to_list()
    plt.hist(pvals,99,cumulative=True,density=True, histtype='step')
    x = np.linspace(0,1,100)
    plt.plot(x, x)
    plt.show()

# Cell
from scipy.stats import norm
import matplotlib.pyplot as plt

def plot_bgdist(bgdist):
    fc2counts_rescaled = tranform_fc2count_to_fc_space(bgdist.fc2counts, bgdist.cumulative[-1],1/100.0)

    plt.bar(list(fc2counts_rescaled.keys()), fc2counts_rescaled.values(),width=0.01,color='g')
    axes2 = plt.twinx()
    x = np.linspace(-4, 4, 1000)
    axes2.plot(x, norm.pdf(x, 0, bgdist.SD)/1.15)
    axes2.set_ylim(0.0, 0.4)
    plt.show()

def tranform_fc2count_to_fc_space(fc2counts, num_fcs, rescale_factor):
    fc2counts_fcscales = {}
    for fc, count in fc2counts.items():
        fc2counts_fcscales[fc*rescale_factor] = count/num_fcs

    return fc2counts_fcscales

# Cell

import matplotlib.pyplot as plt
from scipy import stats
import itertools

def plot_withincond_fcs(normed_intensity_df, cut_extremes = True):
    """takes a normalized intensity dataframe and plots the fold change distribution between all samples. Column = sample, row = ion"""

    samplecombs = list(itertools.combinations(normed_intensity_df.columns, 2))

    for spair in samplecombs:#compare all pairs of samples
        s1 = spair[0]
        s2 = spair[1]
        diff_fcs = normed_intensity_df[s1].to_numpy() - normed_intensity_df[s2].to_numpy() #calculate fold changes by subtracting log2 intensities of both samples

        if cut_extremes:
            cutoff = max(abs(np.nanquantile(diff_fcs,0.025)), abs(np.nanquantile(diff_fcs, 0.975))) #determine 2.5% - 97.5% interval, i.e. remove extremes
            range = (-cutoff, cutoff)
        else:
            range = None
        plt.hist(diff_fcs,80,density=True, histtype='step',range=range) #set the cutoffs to focus the visualization
        plt.xlabel("log2 peptide fcs")

    plt.show()

# Cell
from anytree.exporter import DotExporter
import anytree

def get_iontree_img(root, protein,saveloc = None):
    protein_node = anytree.findall_by_attr(root, protein, maxlevel=2)[0]
    exporter = DotExporter(protein_node, nodenamefunc=lambda n: f"{get_nodename(n)}\ncluster{n.cluster}\n{n.is_included}")
    exporter.to_picture(saveloc)

def get_nodename(node):
    parentname = node.parent.name
    shortened_name = node.name.replace(parentname, "")
    return shortened_name

# Cell

import matplotlib.pyplot as plt
from scipy import stats


# Cell
import matplotlib.pyplot as plt
def scatter_df_columns(merged_df, log_axes = False):
    col = (0.2, 0.4, 0.6, 0.1)
    ref_columns = list(filter(lambda x : "_ref" in x, merged_df.columns.to_list())) #filter the reference columns from the merged df

    for ref in ref_columns:
        compare = ref.replace("_ref", "")
        ax_p = merged_df.plot.scatter(x=ref,y=compare, color = col)
        corr = merged_df[ref].corr(merged_df[compare])
        plt.title(f"{ref} vs. {compare} corr {corr}")
        x = np.linspace(0,merged_df[ref].max(),100)
        plt.plot(x, x)
        if log_axes:
            plt.xscale('log')
            plt.yscale('log')
        plt.show()

# Cell
import matplotlib.pyplot as plt
def plot_cumhist_dfcols(merged_df):
    col = (0.2, 0.4, 0.6, 0.4)
    ref_columns = list(filter(lambda x : "_ref" in x, merged_df.columns.to_list())) #filter the reference columns from the merged df

    for ref in ref_columns:
        compare = ref.replace("_ref", "")
        plt.hist(merged_df[ref], 100, density=True, histtype='step', label='reference')
        plt.hist(merged_df[compare], 100, density=True, histtype='step',label='compare')
        corr = merged_df[ref].corr(merged_df[compare])
        plt.title(f"{ref} vs. {compare} corr {corr}")
        plt.show()

# Cell

# Cell
import matplotlib.pyplot as plt
import seaborn as sns

def plot_fold_change(df, key1, key2):
    to_plot = df.copy()
    to_plot[f'Ratio ({key1}/{key2})'] = np.log2(to_plot[key1] / to_plot[key2])
    to_plot[f'Inten_{key1}'] = np.log10(to_plot[key1])

    species = 'Human'
    val = to_plot.loc[to_plot['species']==species, f'Ratio ({key1}/{key2})'].values
    val = val[~np.isnan(val)&~np.isinf(val)&~np.isneginf(val)]
    print(f'Species={species}, n={len(val)}, median={np.median(val)}, dev={np.std(val)}')
    species='Ecoli'
    val = to_plot.loc[to_plot['species']==species, f'Ratio ({key1}/{key2})'].values
    val = val[~np.isnan(val)&~np.isinf(val)&~np.isneginf(val)]
    print(f'species={species}, n={len(val)}, median={np.median(val)}, dev={np.std(val)}')

    plt.figure(figsize=(7,7))
    ax = sns.scatterplot(x=f'Ratio ({key1}/{key2})', y=f'Inten_{key1}', hue="species", data=to_plot, alpha=0.5)
    plt.title('Fold Change')
    plt.xlim([-4.5, 6.5])
    #plt.ylim([6,11.5])
    plt.show()


# Cell

import matplotlib.pyplot as plt

import numpy as np




# Cell
import anytree
import time
def get_melted_protein_ion_intensity_table(protein, diffresults_df, normed_df, sample2cond, condpair_root_node = None,ion_header = 'quant_id', protein_header = 'protein'):
    t_start = time.time()
    diffresults_line = diffresults_df.loc[protein]
    value_vars = set.intersection(set(normed_df.columns), set(sample2cond.keys()))
    protein_df = normed_df.xs(protein, level = 0)
    df_melted = pd.melt(protein_df.reset_index(), value_vars= value_vars, id_vars=[ion_header], value_name="intensity", var_name="sample")
    df_melted["condition"] = [sample2cond.get(x) for x in df_melted["sample"]]
    t_melted = time.time()
    #if ion clustering has been performed, add cluster information
    if condpair_root_node != None:

        protein_node = anytree.findall_by_attr(condpair_root_node, protein, maxlevel=2)[0]
        ions_sorted = [x.name for x in protein_node.leaves]
        ion2is_included = {x.name : x.cluster==0 for x in protein_node.leaves} #written as dict because identical ion has multiple columns
        ions_in_df = set(df_melted[ion_header]) - set(ions_sorted)
        if len(ions_in_df)>0:
            Exception("Clustered ions and observed ions differ!")

        df_melted = df_melted.set_index(ion_header)
        df_melted = df_melted.loc[ions_sorted]
        df_melted["is_included"] = [ion2is_included.get(x) for x in df_melted.index]
        df_melted = df_melted.reset_index()
    t_annotated = time.time()
    print(f"times melted protein intensities:\n t_melted: {t_melted - t_start} \n t_annotated: {t_annotated - t_melted}")
    return df_melted, diffresults_line

# Cell

import time
def get_betweencond_fcs_table(melted_df, c1, c2, ion_header = "quant_id"):
    t_start = time.time()
    has_clust_info = "is_included" in melted_df.columns
    melted_df = melted_df.set_index(["condition"])
    sorted_ions = melted_df[aq_variables.QUANT_ID]
    c1_df = melted_df.loc[c1]
    c2_df = melted_df.loc[c2]
    ions = set(c1_df[ion_header]).intersection(set(c2_df[ion_header]))
    sorted_ions = [x for x in sorted_ions if x in ions]
    c1_df = c1_df.set_index([ion_header]).sort_index()
    c2_df = c2_df.set_index([ion_header]).sort_index()
    result_ions = []
    result_fcs = []
    result_included = []
    t_localized_index_set = time.time()
    for ion in sorted_ions:
        is_included = c1_df.loc[ion]["is_included"][0] if has_clust_info else True

        ions1 = c1_df.loc[[ion]]["intensity"]
        ions2 = c2_df.loc[[ion]]["intensity"]
        fcs = [x-y for x,y in itertools.product(ions1, ions2)]
        result_ions.extend([ion for x in range(len(fcs))])
        result_fcs.extend(fcs)
        result_included.extend([is_included for x in range(len(fcs))])
    t_list_created = time.time()
    res_df = pd.DataFrame({ion_header: result_ions, "log2fc": result_fcs, "is_included" : result_included})
    print(f"times betweencond fcs table:\n t_localized_index_set: {t_localized_index_set - t_start} \n t_list_created: {t_list_created - t_localized_index_set}")
    return res_df

# Cell

def beeswarm_ion_plot(df_melted, diffresults_protein, only_boxplot = False,saveloc = None):
    """takes pre-formatted long-format dataframe which contains all ion intensities for a given protein.
      Columns are QUANT_ID, "intensity", "condition". Also takes results of the protein differential analysis as a series
      to annotate the plot"""

    #get annotations from diffresults
    fdr = float(diffresults_protein.at["fdr"])
    log2fc = float(diffresults_protein.at["log2fc"])
    protein = diffresults_protein.name

    #define greyscale color palette for the two conditions
    pal2 = [(0.94, 0.94, 0.94),(1.0, 1.0, 1.0)]

    #searborn standard functions
    if only_boxplot:
        ax = sns.boxplot(x=aq_variables.QUANT_ID, y="intensity", hue="condition", data=df_melted, palette="Set2", dodge=True)
    else:
        ax = sns.boxplot(x=aq_variables.QUANT_ID, y="intensity", hue="condition", data=df_melted, palette=pal2)
        ax = sns.stripplot(x=aq_variables.QUANT_ID, y="intensity", hue="condition", data=df_melted, palette="Set2", dodge=True)#size = 10/len(protein_df.index)

    #annotate and format
    handles, labels = ax.get_legend_handles_labels()

    l = plt.legend(handles[2:4], labels[2:4])

    plt.xticks(rotation=90)
    if "gene" in diffresults_protein.index:
        gene = diffresults_line.at["gene"]
        plt.title(f"{gene} ({protein}) FDR: {fdr:.1e}")
    else:
        plt.title(f"{protein} FDR: {fdr:.1e} log2FC: {log2fc:.1f}")
    if saveloc is not None:
        plt.savefig(saveloc)

    plt.show()


# Cell

import seaborn as sns
import matplotlib.pyplot as plt

def foldchange_ion_plot(df_melted, diffresults_protein, saveloc = None):
    """takes pre-formatted long-format dataframe which contains all between condition fold changes. All ions of a given protein
    are visualized, the columns are aq_variables.QUANT_ID and "log2fc".  Also takes results of the protein differential analysis as a series
      to annotate the plot"""
    #get annotations from diffresults
    fdr = float(diffresults_protein.at["fdr"])
    protein = diffresults_protein.name

    #define greyscale color palette
    pal2 = [(0.94, 0.94, 0.94),(1.0, 1.0, 1.0)]

    #specify color for included proteins
    my_pal = {row[aq_variables.QUANT_ID]: "lightblue" if row["is_included"] else "grey" for _,row in df_melted.iterrows()}

    #plot with seaborn standard functions
    ax = sns.boxplot(x=aq_variables.QUANT_ID, y="log2fc", data=df_melted, color = "white")
    ax = sns.stripplot(x=aq_variables.QUANT_ID, y="log2fc", data=df_melted, palette= my_pal)

    #annotate and format
    handles, labels = ax.get_legend_handles_labels()
    ax.axhline(y = 0, color='black', linewidth=2, alpha=.7, linestyle = "dashed")
    l = plt.legend(handles[2:4], labels[2:4])
    plt.xticks(rotation=90)
    if "gene" in diffresults_protein.index:
        gene = diffresults_line.at["gene"]
        plt.title(f"{gene} ({protein}) FDR: {fdr:.1e}")
    else:
        plt.title(f"{protein} FDR: {fdr:.1e}")
    if saveloc is not None:
        plt.savefig(saveloc)

    plt.show()



# Cell
import numpy.ma as ma
import scipy.cluster.hierarchy as hierarchy

def compare_direction(array1, array2):
    identical_elements  = array1 == array2
    num_same_direction = np.sum(identical_elements)
    return num_same_direction

def compare_correlation(array1, array2):
    corr = ma.corrcoef(ma.masked_invalid(array1), ma.masked_invalid(array2))[0][1]
    return corr

def get_condensed_distance_matrix(arrays, compare_function):

    res = np.ones(int(len(arrays) * (len(arrays)-1)/2))
    count = 0
    for i in range(len(arrays)):
        for j in range(i+1, len(arrays)):
            array1 = arrays[i]
            array2 = arrays[j]
            distance = 1/compare_function(array1, array2)
            res[count] = distance
            count+=1

    return res

def clustersort_numerical_arrays(arrays, names , cluster_method ='average',compare_function = compare_direction):
    condensed_distance_matrix = get_condensed_distance_matrix(arrays, compare_function)
    linkage_matrix = hierarchy.linkage(condensed_distance_matrix, method = cluster_method)
    sorted_array_idxs = hierarchy.leaves_list(linkage_matrix)

    sorted_array = [arrays[x] for x in sorted_array_idxs]
    sorted_names = [names[x] for x in sorted_array_idxs]
    return sorted_array, sorted_names, linkage_matrix

# Cell
import numpy as np
def compare_direction(array1, array2):
    identical_elements  = array1 == array2
    num_same_direction = np.sum(identical_elements)
    return num_same_direction

# Cell
import numpy.ma as ma
def compare_correlation(array1, array2):
    corr = ma.corrcoef(ma.masked_invalid(array1), ma.masked_invalid(array2))[0][1]
    return corr

# Cell

import scipy.cluster.hierarchy as hierarchy
import scipy.spatial.distance as dist
def clustersort_numerical_arrays(arrays, names , cluster_method ='average',compare_function = compare_direction):
    #condensed_distance_matrix = get_condensed_distance_matrix(arrays, compare_function)
    condensed_distance_matrix = dist.pdist(arrays, lambda u, v: 1/(compare_function(u,v)+1))
    linkage_matrix = hierarchy.linkage(condensed_distance_matrix, method = cluster_method)
    sorted_array_idxs = hierarchy.leaves_list(linkage_matrix)

    sorted_array = np.array([arrays[x] for x in sorted_array_idxs])
    sorted_names = np.array([names[x] for x in sorted_array_idxs])
    return sorted_array, sorted_names, linkage_matrix

# Cell

import pandas as pd
import numpy as np
import os
def get_clustered_dataframe(overview_df, cluster_method ='average',compare_function = compare_direction, clust_rows = True, clust_columns = True):

    df_numbered = overview_df.select_dtypes(include=np.number)
    contains_floats = ['float' in str(x) for x in df_numbered.dtypes]
    type = 'float' if True in contains_floats else 'int'
    df_numbered = df_numbered.astype(type) #ensure that the df has no mixed types

    rows = df_numbered.to_numpy()
    rownames = list(df_numbered.index)
    colnames = list(df_numbered.columns)

    if clust_rows:
        if(len(rownames)>10000):
            print(f"large number of rows, skipping cluster step of rows to avoid long runtime.")
        else:
            print(f"clustering on {len(rownames)} rows")
            rows, rownames, _ = clustersort_numerical_arrays(rows, rownames, cluster_method, compare_function)
    if clust_columns:
        if(len(colnames)>10000):
            print(f"large number of columns, skipping cluster step of columns to avoid long runtime")
        else:
            print(f"clustering on {len(colnames)} columns")
            columns, colnames,_ = clustersort_numerical_arrays(rows.T, colnames, cluster_method, compare_function)
            rows = columns.T
    print("finished clustering")
    df_clustered = pd.DataFrame(rows, index= rownames)
    df_clustered.columns = colnames
    return df_clustered

# Cell
import re
import os
def get_sample_overview_dataframe(results_folder = os.path.join(".", "results"), regulated_object = "protein",condpairs_to_compare = [], show_fcs = False, name_transformation_function = None):
    """
    goes through the results folder and extracts up- and downregulated genes for each (specified) condition comparison
    """

    if len(condpairs_to_compare) == 0:
        condpairs_to_compare = [f.replace(".results.tsv", "").split(aq_variables.CONDITION_PAIR_SEPARATOR) for f in os.listdir(results_folder) if re.match(r'.*results.tsv', f)]

    dfs = []
    count = 0
    for row in condpairs_to_compare:
        c1 = row[0]
        c2 = row[1]
        results = get_diffresult_dataframe(c1, c2, results_folder)
        if(type(results) == type(None)):
            continue
        site_df = results
        prot2fc = dict(zip(site_df[regulated_object], site_df["log2fc"]))
        positive_sites = list(set(site_df[(site_df["fdr"]<0.05) & (site_df["log2fc"]>0.5)][regulated_object]))
        negative_sites = list(set(site_df[(site_df["fdr"]<0.05) & (site_df["log2fc"]<-0.5)][regulated_object]))

        if show_fcs:
            df_local = pd.DataFrame([[prot2fc.get(x) for x in positive_sites]+[prot2fc.get(x) for x in negative_sites]],columns=positive_sites+negative_sites)
        else:
            df_local = pd.DataFrame([[1 for x in positive_sites]+[-1 for x in negative_sites]],columns=positive_sites+negative_sites)
        df_local["condpair"] = utils.get_condpairname([c1, c2])
        #df_loc["num_regulated"] = len(positive_sites) + len(negative_sites)
        dfs.append(df_local)
        #print(count)
        count+=1

    result_df = pd.concat(dfs)
    result_df = result_df.replace(np.nan, 0).set_index("condpair")
    if name_transformation_function is not None:
        result_df = name_transformation_function(result_df)

    return result_df

def reformat_dataframe_header(df):
    header_genes = [x.split("_")[0] for x in df.columns]
    header_proteins = [x.split("_")[1] for x in df.columns]
    header_sitenums = [x.split("_")[2] for x in df.columns]

    header_df = pd.DataFrame.from_dict(data= {'gene_name': header_genes, 'protein' : header_proteins, 'site_id': header_sitenums}, columns=df.columns, orient='index')
    return pd.concat([header_df, df])

# Cell
import pandas as pd
import os
import numpy as np

def get_diffresult_dataframe(cond1, cond2, results_folder = os.path.join(".", "results")):
    """
    reads the results dataframe for a given condpair
    """
    condpair = utils.get_condpairname([cond1, cond2])
    diffresults = os.path.join(results_folder, f"{condpair}.results.tsv")

    try:
        diffprots = pd.read_csv(diffresults, sep = "\t")
    except:
        print(f"no quantfiles found for {condpair}!")
        return None
    diffprots = diffprots[(diffprots["condition_pair"] == condpair)]

    diffprots["-log10fdr"] = -np.log10(diffprots["fdr"])
    #diffprots = diffprots.set_index("protein")

    return diffprots

# Cell
import alphaquant.utils.utils as aqutils
import alphaquant.diffquant.diffutils as aqdiffutils
import numpy as np

def get_diffresult_dict_ckg_format(cond1, cond2, results_folder = os.path.join(".", "results")):
    """
    ckg wrapper, reads the results dataframe for a given condpair and reformats it to the ckg volcano plot input format
    """
    result_df = get_diffresult_dataframe(cond1, cond2, results_folder)
    log2fcs = result_df["log2fc"].to_numpy()
    logged_fdrs = result_df["-log10fdr"].to_numpy()
    min_fdr = np.min(logged_fdrs)
    result_ckg_dict = {}
    result_ckg_dict[("volcano", aqutils.get_condpairname([cond1, cond2]))] = {"x": log2fcs, "y" : np.array([1.2,3.3,1,3,4,5,6]), "pvalue" : min_fdr, "text" : "testext", "color" : "grey",'is_samr':False, 'annotations' : []}
    return result_ckg_dict

# Cell
import pandas as pd
def subset_normed_peptides_df_to_condition(cond, sample2cond_df, normed_df):
    columns_to_keep = set(sample2cond_df[sample2cond_df["condition"]==cond]["sample"]).intersection(set(normed_df.columns))
    columns_to_drop = set(normed_df.columns) - columns_to_keep
    subset_df = normed_df.drop(columns = columns_to_drop)
    return subset_df

# Cell
import pandas as pd
import os
import numpy as np

def get_normed_peptides_dataframe(cond1, cond2, results_folder = os.path.join(".", "results")):
    condpair = utils.get_condpairname([cond1, cond2])
    normed_peptides_tsv = os.path.join(results_folder, f"{condpair}.normed.tsv")
    try:
        normed_peptides = pd.read_csv(normed_peptides_tsv, sep = "\t")
    except:
        print(f"no normed peptides found for {condpair}!")
        return None

    numeric_cols = list(normed_peptides.select_dtypes(include=np.number).columns)
    #available_vals = list(set(samplemap_df["sample"].values).intersection(set(normed_peptides.columns)))
    normed_peptides[numeric_cols] = np.log2(normed_peptides[numeric_cols].replace(0, np.nan))
    normed_peptides = normed_peptides.set_index(["protein", aq_variables.QUANT_ID])
    return normed_peptides

# Cell
import pandas as pd

def initialize_sample2cond(samplemap):
    samplemap_df = pd.read_csv(samplemap, sep = "\t")
    sample2cond = dict(zip(samplemap_df["sample"], samplemap_df["condition"]))
    return samplemap_df, sample2cond

# Cell
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def plot_volcano_plotly(
    result_df,
    fc_header = "log2fc",
    fdr_header = "fdr",
    significance_cutoff = 0.05,
    log2fc_cutoff = 0.5,
    ybound = None,
    xbound = None,
    color='darkgrey',
    marker_size=5,
    name=None,
    opacity=0.9,
    marker_symbol='circle'
):
    result_df[fdr_header] = result_df[fdr_header].replace(0, np.min(result_df[fdr_header].replace(0, 1.0)))
    sighits_down = sum((result_df[fdr_header]<significance_cutoff) & (result_df[fc_header] <= -log2fc_cutoff))
    sighits_up = sum((result_df[fdr_header]<significance_cutoff) & (result_df[fc_header] >= log2fc_cutoff))
    result_df_significant = result_df[
        ((result_df[fdr_header] < significance_cutoff) & (result_df[fc_header] <= -log2fc_cutoff)) |
        ((result_df[fdr_header] < significance_cutoff) & (result_df[fc_header] >= log2fc_cutoff))
    ]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            name='',
            x=result_df[fc_header],
            y=result_df['-log10fdr'],
            mode='markers',
            text=result_df['protein'],
            marker=dict(
                size=marker_size,
                symbol=marker_symbol,
                color=color,
                opacity=opacity,
                line=dict(
                    width=1,
                    color='#202020'
                ),
                showscale=False
            ),
            hovertemplate =
                '<b>protein:</b> %{text}'
                '<br><b>log2fc</b>: %{x:.2f}'+
                '<br><b>-log10fdr</b>: %{y:.2f}<br>',
        )
    )
    fig.add_trace(
        go.Scatter(
            name='',
            x=result_df_significant[fc_header],
            y=result_df_significant['-log10fdr'],
            mode='markers',
            text=result_df_significant['protein'],
            marker=dict(
                size=marker_size,
                symbol=marker_symbol,
                color=AlphaQuantColorMap().colorlist_hex[1],
                opacity=opacity,
                line=dict(
                    width=1,
                    color='#202020'
                ),
                showscale=False
            ),
            hovertemplate =
                '<b>protein:</b> %{text}'
                '<br><b>log2fc</b>: %{x:.2f}'+
                '<br><b>-log10fdr</b>: %{y:.2f}<br>',
        )
    )
    fig.add_hline(
        y=-np.log10(significance_cutoff),
        line_width=1,
        line_dash="dash",
        line_color=AlphaQuantColorMap().colorlist_hex[1]
    )
    fig.add_vline(
        x=log2fc_cutoff,
        line_width=1,
        line_dash="dash",
        line_color=AlphaQuantColorMap().colorlist_hex[1]
    )
    fig.add_vline(
        x=-log2fc_cutoff,
        line_width=1,
        line_dash="dash",
        line_color=AlphaQuantColorMap().colorlist_hex[1]
    )

    maxfc = max(abs(result_df[fc_header])) + 0.5
    fig.update_layout(
        height=500,
        width=870,
        template='plotly_white',
        title=dict(
            text=f"{sighits_down} down, {sighits_up} up of {len(result_df)}",
            font=dict(size=14, color='black', family='Arial, sans-serif'),
            y=0.92,
            x=0.5,
            xanchor='center',
            yanchor='middle',
        ),
        hovermode='closest',
        xaxis=dict(
            range=[-maxfc,maxfc],
            title=dict(
                text='log2 fold change',
                font=dict(size=14, color='black', family='Arial, sans-serif'),
            )
        ),
        yaxis=dict(
            title=dict(
                text='-log10 FDR',
                font=dict(size=14, color='black', family='Arial, sans-serif'),
            ),
            range=[-0.1, max(-np.log10(result_df[fdr_header])) + 0.5],
        ),
        showlegend=False,
    )

    return fig

# Cell
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import itertools

def plot_withincond_fcs_plotly(
    normed_intensity_df,
    title,
    cut_extremes = True
):
    """takes a normalized intensity dataframe and plots the fold change distribution between all samples. Column = sample, row = ion"""
    fig = go.Figure()
    samplecombs = list(itertools.combinations(normed_intensity_df.columns, 2))
    cutoff_common = 0
    for spair in samplecombs:#compare all pairs of samples
        s1 = spair[0]
        s2 = spair[1]
        diff_fcs = normed_intensity_df[s1].to_numpy() - normed_intensity_df[s2].to_numpy() #calculate fold changes by subtracting log2 intensities of both samples

        if cut_extremes:
            cutoff_cur = max(abs(np.nanquantile(diff_fcs,0.025)), abs(np.nanquantile(diff_fcs, 0.975))) #determine 2.5% - 97.5% interval, i.e. remove extremes
            if cutoff_cur and cutoff_cur > cutoff_common:
                cutoff_common = cutoff_cur

        n, bins, _ = plt.hist(diff_fcs, 250, density=True, histtype='step')
        fig.add_trace(
            go.Scatter(
                x=bins,
                y=n,
                mode='lines',
                line=dict(
                    shape='hvh',
                    width = 0.5
                )
            )
        )
    fig.update_layout(
        xaxis = dict(
            title="log2 peptide fcs",
            range=(-cutoff_common, cutoff_common)
        ),
        barmode='stack',
        template='plotly_white',
        showlegend=False,
        title = dict(
                text=title,
                font=dict(size=16, color='black', family='Arial, sans-serif'),
                y=0.91,
                x=0.5,
                xanchor='center',
                yanchor='middle',
            ),
        height=400,
        width=870,
    )
    return fig

# Cell
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

def plot_betweencond_fcs_plotly(
    df_c1_normed,
    df_c2_normed,
    title,
    merge_samples = True
):
    """takes normalized intensity dataframes of each condition and plots the distribution of direct peptide fold changes between conditions"""
    fig = go.Figure()
    if merge_samples: #samples can be merged to median intensity
        df_c1_normed = df_c1_normed.median(axis = 1, skipna = True).to_frame()
        df_c2_normed = df_c2_normed.median(axis = 1, skipna = True).to_frame()

    both_idx = df_c1_normed.index.intersection(df_c2_normed.index)
    df1 = df_c1_normed.loc[both_idx]
    df2 = df_c2_normed.loc[both_idx]
    cutoff_common = 0

    fig.add_vline(
        x=0,
        line_width=1,
        line_dash="dash",
        line_color="red"
    ) #the data is normalized around 0, draw in helper line

    for col1 in df1.columns:
        for col2 in df2.columns:
            diff_fcs = df1[col1].to_numpy() - df2[col2].to_numpy() #calculate fold changes by subtracting log2 intensities of both conditions
            cutoff_cur = max(abs(np.nanquantile(diff_fcs,0.025)), abs(np.nanquantile(diff_fcs, 0.975))) #determine 2.5% - 97.5% interval, i.e. remove extremes
            if cutoff_cur and cutoff_cur > cutoff_common:
                cutoff_common = cutoff_cur

            n, bins, _ = plt.hist(diff_fcs, 100, density=True, histtype='step')
            fig.add_trace(
                go.Scatter(
                    x=bins,
                    y=n,
                    mode='lines',
                    line=dict(
                        shape='hvh'
                    )
                )
            )

    fig.update_layout(
        xaxis = dict(
            title="log2(fc)",
            range=(-cutoff_common, cutoff_common)
        ),
        barmode='stack',
        template='plotly_white',
        showlegend=False,
        title = dict(
            text=title,
            y=0.90,
            x=0.5,
            xanchor='center',
            yanchor='middle',
        ),
        height=400,
        width=870,
    )
    return fig

# Cell
def beeswarm_ion_plot_plotly(
    df_melted,
    diffresults_protein,
):
    """takes pre-formatted long-format dataframe which contains all ion intensities for a given protein.
      Columns are QUANT_ID, "intensity", "condition". Also takes results of the protein differential analysis as a series
      to annotate the plot"""

    fig = go.Figure()

    #get annotations from diffresults
    fdr = float(diffresults_protein.at["fdr"])
    fc = float(diffresults_protein.at["log2fc"])
    protein = diffresults_protein.name

    for cond, color, line_color in zip(df_melted.condition.unique(), ['#FF7F0E', '#2CA02C'], ['#808080', '#a6a6a6']):
        data = df_melted[df_melted.condition == cond]

        fig.add_trace(
            go.Box(
                x=data.ion,
                y=data.intensity,
                boxpoints='all',
                name=cond,
                line=dict(
                    color=line_color
                ),
                marker=dict(
                    color=color,
                    opacity=0.3
                ),
                pointpos=0
            )
        )


    if "gene" in diffresults_protein.index:
        gene = diffresults_line.at["gene"]
        title = f"{gene} ({protein}) FDR: {fdr:.1e} log2FC: {fc:.2f}"
    else:
        title = f"{protein} FDR: {fdr:.1e} log2FC: {fc:.2f}"

    fig.update_layout(
        xaxis_title='ion',
        yaxis_title='intensity',
        boxmode='group', # group together boxes of the different traces for each value of x
        template='plotly_white',
        title = dict(
            text=title,
            #y=0.85,
            x=0.5,
            xanchor='center',
            yanchor='middle',
        ),
        titlefont=dict(
            size=14,
            color='black',
            family='Arial, sans-serif'
        ),
        legend=dict(
            title='conditions:',
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1
        ),
        height=300,
    )

    return fig

# Cell
from matplotlib.pyplot import cm
import anytree

def foldchange_ion_plot_plotly(
    df_melted,
    diffresults_protein,
    protein_node = None,
    level = 'seq'
):
    """takes pre-formatted long-format dataframe which contains all between condition fold changes. All ions of a given protein
    are visualized, the columns are QUANT_ID and "log2fc".  Also takes results of the protein differential analysis as a series
      to annotate the plot"""

    fig = go.Figure()

    #get annotations from diffresults
    fdr = float(diffresults_protein.at["fdr"])
    fc = float(diffresults_protein.at["log2fc"])
    protein = diffresults_protein.name

    fig.add_hline(
        y=0,
        line_width=2,
        opacity=.7,
        line_dash="dash",
        line_color="black"
    )

    if protein_node is not None:
        clust2col, clust2ions = get_color2ions(protein_node, level)
    else:
        clust2col = {-1 : 'lightblue'}
        clust2ions = {-1 : [x for x in df_melted[aq_variables.QUANT_ID].drop_duplicates()]}



    for clust in sorted(clust2ions.keys()):
        ions = clust2ions.get(clust)
        color = clust2col.get(clust)

        df_subset = df_melted[[x in ions for x in df_melted[aq_variables.QUANT_ID]]]

        fig.add_trace(
            go.Box(
                x=df_subset.ion,
                y=df_subset.log2fc,

                boxpoints='all',
                line=dict(
                    color=color
                ),
                marker=dict(
                    color=color,
                    opacity=0.7
                ),
                pointpos=0,
                name = clust
            )
        )

    if "gene" in diffresults_protein.index:
        gene = diffresults_line.at["gene"]
        title = f"{gene} ({protein}) FDR: {fdr:.1e} log2FC: {fc:.2f}"
    else:
        title = f"{protein} FDR: {fdr:.1e} log2FC: {fc:.2f}"

    fig.update_layout(
        xaxis_title='ion',
        yaxis_title='log2fc',
        template='plotly_white',
        title = dict(
            text=title,
            y=0.85,
            x=0.5,
            xanchor='center',
            yanchor='middle',
        ),
        titlefont=dict(
            size=14,
            color='black',
            family='Arial, sans-serif'
        ),
        height=300,
    )

    return fig

def get_color2ions(protein_node, level):
    clust2ions = {}

    relevant_subnodes = anytree.findall(protein_node,filter_ = lambda x : x.type == level)
    excluded_leaves = []

    for subnode in relevant_subnodes:
        clust = subnode.cluster
        clust2ions[clust] = clust2ions.get(clust, []) + [x.name for x in subnode.leaves if subnode.type in x.inclusion_levels]
        excluded_leaves.extend([x.name for x in subnode.leaves if subnode.type not in x.inclusion_levels])

    colors= cm.rainbow(np.linspace(0, 1, len(clust2ions.keys())))
    clust2col =  {clust:convert_to_plotly_color_format(col) for clust, col in zip(sorted(clust2ions.keys()), colors)}
    clust2ions[-1] = excluded_leaves
    clust2col[-1] = 'lightgrey'
    #color2ions = {convert_to_plotly_color_format(clust2col.get(x)) : clust2ions.get(x) for x in clust2ions.keys()}

    return clust2col, clust2ions

def convert_to_plotly_color_format(color_array):
    return f"rgb({int(color_array[0]*250)},{int(color_array[1]*250)},{int(color_array[2]*250)})"


# Cell

import seaborn as sns
def make_mz_fc_boxplot(merged_df, ion_nodes):
    merged_df = merged_df.copy()
    ion2fc = {node.name:node.fc for node in ion_nodes}
    merged_df["log2fc"] = [ion2fc.get(ion) for ion in merged_df[aq_variables.QUANT_ID]]
    #merged_df = merged_df[merged_df["log2fc"] >0]
    #merged_df = merged_df[merged_df["EG.ApexRT"] <80]
    transf_fc = list(2**merged_df["log2fc"])
    merged_df["fc"]  = transf_fc
    merged_df['mz_cathegory'] = [assign_mz_cathegory(mz) for mz in merged_df["FG.PrecMz"]]
    sns.boxplot(x = 'mz_cathegory', y = "log2fc",data = merged_df)
    plt.ylim(-2, 2)
    plt.show()


def assign_mz_cathegory(mz_val):
    if mz_val<400:
        return 400
    if mz_val < 500:
        return 500
    if mz_val < 600:
        return 600
    if mz_val < 700:
        return 700
    if mz_val < 800:
        return 800
    if mz_val < 900:
        return 900
    if mz_val < 1000:
        return 1000
    if mz_val < 1100:
        return 1100
    else:
        return 1200

# Cell
import matplotlib.pyplot as plt

def plot_fc_histogram_ml_filtered(y_test, y_pred, fc_cutoff, show_filtered):
    if show_filtered:
        fcs = [y_test[i] for i in range(len(y_test)) if y_pred[i]>fc_cutoff]
        if len(fcs)==0:
            return
    else:
        fcs = [y_test[i] for i in range(len(y_test)) if y_pred[i]<fc_cutoff]

    #is_logged = min(fcs)<0
    #if not is_logged:
     #   fcs = np.log2(np.array(fcs))
    percent_survived = round(len(fcs)/len(y_test), 2)
    print(f"{percent_survived} of fcs retained of {len(fcs)} total")
    plt.hist(fcs, 60, density=True, histtype='step',cumulative=False)
    plt.xlim(-1.8, 1.8)

def plot_log_loss_score(loss_score, y_test, loss_score_cutoff = 0):
    plt.hist(loss_score, 60, density=False, histtype='step',cumulative=False)
    plt.show()
    if loss_score_cutoff > 0:
        fcs = [y_test[i] for i in range(len(y_test)) if loss_score[i]>loss_score_cutoff]
        print(f"{len(fcs)} retained of {len(y_test)}")
        plt.hist(fcs, 60, density=True, histtype='step',cumulative=False)
        plt.show()
    plt.scatter(y_test, loss_score, color='blue', alpha=0.3)
    plt.show()

# Cell
from sklearn.metrics import mean_squared_error, r2_score
import seaborn as sns

def scatter_ml_regression_perturbation_aware(y_test, y_pred, ionnames, nodes, results_dir = None):
    y_test, y_pred = [np.array(y_test), np.array(y_pred)]
    perturbed_ions = {x.name  for x in nodes if hasattr(x, "perturbation_added")}
    is_unperturbed_vec = [x for x in range(len(ionnames)) if ionnames[x] not in perturbed_ions]
    y_unpert_test = y_test[is_unperturbed_vec]
    y_unpert_pred = y_pred[is_unperturbed_vec]

    fig_perturb, ax_perturb = plt.subplots()


    sns.regplot(x = y_unpert_test, y = y_unpert_pred, scatter_kws=dict(alpha=0.1), ax = ax_perturb)

    if len(perturbed_ions)>0:
        is_perturbed_vec = [x for x in range(len(ionnames)) if ionnames[x] in perturbed_ions]
        y_pert_test = y_test[is_perturbed_vec]
        y_pert_pred = y_pred[is_perturbed_vec]
        sns.scatterplot(x = y_pert_test, y = y_pert_pred, alpha=0.1, label="perturbed", color = sns.color_palette()[1], ax = ax_perturb)
        plot_perturbed_unperturbed_fcs(fcs_perturbed=y_pert_test,fcs_unperturbed=y_unpert_test, results_dir = results_dir)
        plot_perturbed_unperturbed_fcs(fcs_perturbed=[x.fc for x in nodes if hasattr(x, "perturbation_added")], fcs_unperturbed=[x.fc for x in nodes if not hasattr(x, "perturbation_added")])
        plot_perturbation_histogram([x for x in nodes if hasattr(x, "perturbation_added")], results_dir)


    err = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    ax_perturb.set_title(f"MSE: {err:.2f}, R2: {r2:.2f}")

    if results_dir is not None:
        fig_perturb.savefig(f"{results_dir}/ml_regression.pdf")
    plt.show()


def scatter_ml_regression(y_test, y_pred, results_dir = None):
    fig, ax = plt.subplots()

    sns.regplot(x = y_test, y = y_pred, scatter_kws=dict(alpha=0.1), ax = ax)
    err = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    ax.set_title(f"MSE: {err:.2f}, R2: {r2:.2f}")

    if results_dir is not None:
        fig.savefig(f"{results_dir}/ml_regression.pdf")
    plt.show()



def plot_perturbation_histogram(perturbed_nodes, results_dir):
    fig, ax = plt.subplots()
    perturbations = [x.perturbation_added for x in perturbed_nodes]
    ax.hist(perturbations, 60, density=True, histtype='step',cumulative=True)
    if results_dir is not None:
        ax.figure.savefig(f"{results_dir}/perturbation_histogram.pdf")

def plot_perturbed_unperturbed_fcs(fcs_perturbed, fcs_unperturbed, results_dir = None):
    fig, ax = plt.subplots()
    ax.hist(bins = 60, x=fcs_unperturbed, label= 'unperturbed',density=True, histtype='step')
    ax.hist(bins = 60, x= fcs_perturbed,label='perturbed', density=True, histtype='step')
    if results_dir is not None:
        ax.figure.savefig(f"{results_dir}/compare_pertubed_unperturbed.pdf")


def plot_ml_fc_histograms(y_test, y_pred, cutoff, results_dir = None):

    plot_fc_histogram_ml_filtered(y_test, y_pred, cutoff, show_filtered=False)
    if results_dir is not None:
        plt.savefig(f"{results_dir}/observed_offsets_ml_filtered.pdf")
    plt.show()
    plot_fc_histogram_ml_filtered(y_test, y_pred, cutoff, show_filtered=True)
    if results_dir is not None:
        plt.savefig(f"{results_dir}/observed_offsets_nofilt.pdf")
    plt.show()

# Cell
import seaborn as sns
import numpy as np

def plot_fc_intensity_scatter(result_df, name, ax = None,expected_log2fc = None, tolerance_interval = 0.5, xlim_lower = -1, xlim_upper = 3.5):
    result_df["log_median_intensity"] = np.log10(result_df["median_intensity"])
    if ax == None:
        ax = sns.scatterplot( x="log2fc", y="log_median_intensity", data=result_df, alpha=0.2)
    else:
        sns.scatterplot(x="log2fc", y="log_median_intensity", data=result_df, alpha=0.2, ax = ax)
    if expected_log2fc is not None:
        ax.vlines(expected_log2fc, 3.8, 11)
        ax.vlines(expected_log2fc-tolerance_interval, 3.8, 11, linestyles = 'dotted')
        ax.vlines(expected_log2fc+tolerance_interval, 3.8, 11, linestyles = 'dotted')
        ax.set(xlim = (xlim_lower, expected_log2fc + xlim_upper))
    std = np.std(result_df['log2fc'].values)
    mean = np.mean(result_df['log2fc'].values)
    ax.set_title(f'{name}\n mean {mean:.2f}, std {std:.2f}, nums {len(result_df["log2fc"])}')
    #ax.set(xlim = (-2, 6))
    #ax.set(ylim = (3.8, 11))
    #plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    if ax == None:
        plt.show()

# Cell
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_violin_plots_log2fcs(names, dfs, ax = None):
    df_fcs_longformat = get_longformat_df(names, dfs)
    sns.violinplot(x='variable', y='value', data=df_fcs_longformat, scale='width', ax = ax)
    #sns.stripplot(x='variable', y='value', data=df_fcs_longformat, ax = ax, alpha = 0.35, color = 'lightgrey')
    if ax == None:
        plt.show()

def plot_beeswarm_plot_log2fcs(names, dfs, ax = None):
    df_fcs_longformat = get_longformat_df(names, dfs)
    sns.boxplot(x='variable', y='value', data=df_fcs_longformat, ax = ax)
    sns.stripplot(x='variable', y='value', data=df_fcs_longformat, ax = ax, alpha = 0.35)
    if ax == None:
        plt.show()

def get_longformat_df(names, dfs):
    methods = []
    fcs = []
    for idx in range(len(names)):
        df = dfs[idx]
        name = names[idx]
        fcs_local = list(df["log2fc"])
        fcs.extend(fcs_local)
        methods.extend([name for x in range(len(fcs_local))])
    df_fcs_longformat = pd.DataFrame({'variable' : methods, 'value' : fcs})
    return df_fcs_longformat

# Cell
from matplotlib import pyplot as plt
import numpy as np

def plot_feature_importances(coef, names, top_n = np.inf, print_out_name = False, results_dir = None):
    imp,names = filter_sort_top_n(coef, names, top_n)
    fig, ax = plt.subplots()
    ax.set_title('Feature Importances')
    ax.barh(range(len(names)), imp, align='center')
    ax.set_yticks(range(len(names)), names)
    if results_dir is not None:
        fig.savefig(f"{results_dir}/ml_feature_importances.pdf")
    plt.show()


def filter_sort_top_n(imp, names, top_n):
    tuplelist = list(zip(imp, names))
    tuplelist.sort(key = lambda x : abs(x[0]),reverse=True)
    tuplelist = tuplelist[:top_n]
    imp = [x[0] for x in tuplelist]
    names = [x[1] for x in tuplelist]
    return imp, names

# Cell

import numpy as np
import matplotlib.pyplot as plt

def visualize_gaussian_mixture_fit(gmm, y_pred):

    data = np.array(y_pred) ##loading univariate data.

    plt.figure()
    plt.hist(data, bins=50, histtype='stepfilled', density=True, alpha=0.5)
    plt.xlim(min(y_pred), max(y_pred))
    f_axis = data.copy().ravel()
    f_axis.sort()
    a = []
    weight_mean_cov = list(zip(gmm.weights_, gmm.means_, gmm.covariances_))
    weight_mean_cov.sort(key = lambda x : x[0], reverse=True)
    for weight, mean, covar in weight_mean_cov:
        a.append(weight*norm.pdf(f_axis, mean, np.sqrt(covar)).ravel())
        plt.plot(f_axis, a[-1])
    plt.plot(f_axis, np.array(a).sum(axis =0), 'k-')
    plt.xlabel('Variable')
    plt.ylabel('PDF')
    plt.tight_layout()
    plt.show()

# Cell

import numpy as np
import matplotlib.pyplot as plt

def visualize_gaussian_nomix_subfit(mean, var, y_pred, y_subset):

    data = np.array(y_pred) ##loading univariate data.

    plt.figure()
    plt.hist(data, bins=50, histtype='stepfilled', density=True, alpha=0.5)
    plt.xlim(min(y_pred), max(y_pred))
    f_axis = data.copy().ravel()
    f_axis.sort()
    a = []
    weight = len(y_subset)/len(y_pred)

    a.append(weight*norm.pdf(f_axis, mean, np.sqrt(var)).ravel())
    plt.plot(f_axis, a[-1])
    plt.plot(f_axis, np.array(a).sum(axis =0), 'k-')
    plt.xlabel('Variable')
    plt.ylabel('PDF')
    plt.tight_layout()
    plt.show()

# Cell
import matplotlib.pyplot as plt

def visualize_filtered_non_filtered_precursors(all_precursors, ml_score = None):

    fcs_unfilt = [x.fc for x in all_precursors]
    if ml_score is not None:
        fcs_filt = [x.fc for x in all_precursors if abs(x.ml_score)<ml_score]
    else:
        fcs_filt = [x.fc for x in all_precursors if not x.ml_excluded]
    plt.hist([x.ml_score for x in all_precursors],  histtype='step', bins=60)
    plt.show()
    plt.hist(fcs_unfilt, histtype='step', bins=60, label=f"unfilt ({len(fcs_unfilt)})", density=True)
    plt.hist(fcs_filt, histtype='step', bins=60, label = f"filt ({len(fcs_filt)})", density=True)
    #plt.xlim(-2, 2)
    plt.legend()
    plt.show()

# Cell
import seaborn as sns
import matplotlib.pyplot as plt
def plot_fcs_node(nodes, percentile, node_filterfunction = None):
    if node_filterfunction is not None:
        nodes = [x for x in nodes if node_filterfunction(x)]
    nodes_sorted = sorted(nodes,key= lambda x : abs(x.ml_score))
    nodes_sorted = nodes_sorted[:int(len(nodes_sorted)*percentile)]
    sns.stripplot(data = [x.fc for x in nodes_sorted])
   # plt.show()




# Cell

import matplotlib.pyplot as plt
import numpy as np
from sklearn import metrics
import random
import seaborn as sns




def plot_predictability_roc_curve( true_falses, ml_scores, reference_scores, ax = None, percentile_cutoff_indication = None):

    if percentile_cutoff_indication is not None:
        ax.axhline(percentile_cutoff_indication, color = 'lightgrey')
    plot_roc_curve(true_falses, ml_scores, "AlphaQuant score", ax)
    plot_roc_curve(true_falses, reference_scores, f"reference score", ax)
    true_falses = random.sample(true_falses, len(true_falses))
    plot_roc_curve(true_falses, ml_scores, f"random score", ax)
    ax.set_title('ROC curve')
    ax.set_xlabel('FPR')
    ax.set_ylabel('TPR')
    ax.legend()


def plot_predictability_precision_recall_curve( true_falses, ml_scores, reference_scores, ax = None, percentile_cutoff_indication = None):

    if percentile_cutoff_indication is not None:
        ax.axvline(percentile_cutoff_indication, color = 'lightgrey')
    plot_precision_recall_curve(true_falses, ml_scores, "AlphaQuant score", ax)
    plot_precision_recall_curve(true_falses, reference_scores, "reference score", ax)
    true_falses = random.sample(true_falses, len(true_falses))
    plot_precision_recall_curve(true_falses, ml_scores, "random score", ax)
    ax.set_title('Precision-recall curve')
    ax.set_xlabel('recall')
    ax.set_ylabel('precision')
    ax.legend()


def plot_outlier_fraction(node_df, reference_df, expected_log2fc, outlier_thresholds, ax = None):
    thresholds = []
    aq_fractions = []
    reference_fractions = []
    for threshold in outlier_thresholds:
        thresholds.append(threshold)
        aq_fractions.append(aqdiffutils.count_fraction_outliers_from_expected_fc(node_df,threshold, expected_log2fc))
        reference_fractions.append(aqdiffutils.count_fraction_outliers_from_expected_fc(reference_df, threshold,expected_log2fc))
    df = pd.DataFrame({'threshold' :thresholds, 'AlphaQuant' : aq_fractions, 'reference' : reference_fractions})
    df_unpiv = df.melt(id_vars = ['threshold'])
    sns.barplot(x = "threshold", y = 'value', hue = 'variable', data = df_unpiv, ax = ax)







def get_true_false_to_ml_scores(nodes, expected_fc, fc_cutoff_bad = 1, fc_cutoff_good = 0.3, reverse = False):
    true_falses = []
    ml_scores = []
    reference_scores = []
    fcs = []

    for node in nodes:
        fc_diff = abs(node.fc - expected_fc)
        if fc_diff>fc_cutoff_bad:
            true_falses.append(False)
            ml_scores.append(1/abs(node.ml_score))
            reference_scores.append(node.default_quality_score)
            fcs.append(node.fc)
        if fc_diff<fc_cutoff_good:
            true_falses.append(True)
            ml_scores.append(1/abs(node.ml_score))
            reference_scores.append(node.default_quality_score)
            fcs.append(node.fc)

    if reverse:
        true_falses = [not x for x in true_falses]
        ml_scores = [1/x for x in ml_scores]

    print(f"num trues{sum(true_falses)}\tnum falses {len(true_falses) - sum(true_falses)}")

    return true_falses, ml_scores, reference_scores, fcs

def plot_true_false_fcs_of_test_set(fcs, true_falses, ax):
    plot_dict = {'fcs': fcs, 'true_false' : true_falses}
    sns.stripplot(data = plot_dict, x = "true_false", y = 'fcs', ax=ax, palette=[sns.color_palette()[3], sns.color_palette()[0]])
    ax.set_ylabel('log2FC')
    ax.set_xlabel('Cathegory for ROC curve')

def plot_fc_dist_of_test_set(fcs, ax):
    ax.hist(fcs, 60, density=True, histtype='step')
    ax.set_xlabel('log2FC')
    median = np.median(fcs)
    plt.axvline(x=median)
    ax.set_title(f'FC distribution of set, median {median}')



def plot_roc_curve(true_falses, scores, name, ax):
    fpr, tpr, _ = metrics.roc_curve(true_falses,  scores)
    if ax is not None:
        ax.plot(fpr,tpr, label = name)
    else:
        plt.plot(fpr,tpr, label = name)
        plt.legend()
        plt.show()

def plot_precision_recall_curve(true_falses, scores, name, ax):
    precision, recall, _ = metrics.precision_recall_curve(true_falses, scores)
    if ax is not None:
        ax.plot(recall, precision, label = name)
    else:
        plt.plot(recall, precision, label = name)
        plt.legend()
        plt.show()



# Cell
import alphaquant.plotting.base_functions as aqviz

import anytree
import matplotlib.pyplot as plt

def compare_fcs_unperturbed_vs_perturbed_and_clustered(results_dir_unperturbed, results_dir_perturbed, results_dir_perturbed_unclustered):
    ctree_unperturbed = aqutils.read_condpair_tree("S1_filtered", "S2_filtered",results_folder=results_dir_unperturbed)
    ctree_perturbed = aqutils.read_condpair_tree("S1_annot", "S2_annot", results_folder = results_dir_perturbed)
    results_df_perturbed_unclustered =  aqviz.get_diffresult_dataframe("S1", "S2", results_dir_perturbed_unclustered)
    fcs_unperturbed = [x.fc for x in ctree_unperturbed.children]
    fcs_perturbed = [x.fc for x in ctree_perturbed.children]
    fcs_perturbed_unclustered = results_df_perturbed_unclustered["log2fc"]
    plt.hist(fcs_unperturbed,label = "unperturbed", cumulative=True, bins=50, histtype='step')
    plt.hist(fcs_perturbed,label = "perturbed", cumulative=True, bins=50, histtype='step')
    plt.hist(fcs_perturbed_unclustered,label = "perturbed_unclustered", cumulative=True, bins=50, histtype='step')
    plt.legend()
    plt.show()


def rgb_to_hex(rgb):
    if len(rgb) == 3:
        return "#{:02x}{:02x}{:02x}".format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    elif len(rgb) == 4:
        return "#{:02x}{:02x}{:02x}{:02x}".format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255), int(rgb[3] * 255))
    else:
        raise ValueError("RGB input not recognized")


