
from ..run_pipeline import run_pipeline
from ..config.variables import QUANT_ID

import alphaquant.config.config as aqconfig
import logging
aqconfig.setup_logging()
LOGGER = logging.getLogger(__name__)

# Cell
import pandas as pd
def get_tps_fps(result_df, prot2org_file, thresh = 0.05, fc_thresh = 0.3):
    annotated = annotate_dataframe(result_df, prot2org_file)
    condpairs = result_df["condpair"].drop_duplicates()


    for condpair in condpairs:
        annotated_condpair = annotated[annotated["condpair"]==condpair]
        num_tps = sum(annotated_condpair["TP"])
        num_fps = sum(annotated_condpair["FP"])
        annotated_fcfilt = annotated_condpair[annotated["log2fc"] >fc_thresh]
        num_regulated_prots = sum(annotated_fcfilt["fdr"]<thresh)
        num_true_positives = sum(annotated_fcfilt["TP"] &(annotated_fcfilt["fdr"]<0.05))
        num_false_positives = sum(annotated_fcfilt["FP"] &(annotated_fcfilt["fdr"]<0.05))
        fpr = num_false_positives/num_regulated_prots

        LOGGER.info(f'condpair {condpair}')
        LOGGER.info(f"total TPs {num_tps}")
        LOGGER.info(f"total FPs {num_fps}")
        LOGGER.info(f'regulated {num_regulated_prots}')
        LOGGER.info(f'false positives {num_false_positives}')
        LOGGER.info(f'true positives {num_true_positives}')
        LOGGER.info(f'regulated control {num_false_positives+num_true_positives}')
        LOGGER.info(f'FPR {fpr}')

        assert fpr < 0.06


def annotate_dataframe(result_df, prot2org_file):
    prot2org = pd.read_csv(prot2org_file, sep = "\t")
    prot2org["FP"] = (prot2org["organism"] == "Homo sapiens")
    prot2org["TP"] = (prot2org["organism"] == "Saccharomyces cerevisiae")
    prot2org = prot2org[(prot2org["FP"] | prot2org["TP"])]
    LOGGER.info(f"df size before {len(result_df.index)}")
    annotated = pd.merge(result_df, prot2org, how='inner', on = "protein")
    LOGGER.info(f"df size after {len(annotated.index)}")
    return annotated

# Cell
import pandas as pd
import matplotlib.pyplot as plt
def compare_to_reference(result_df, reference_file, condpair):#put in condpair as tuple
    result_df = result_df[result_df["condpair"]==condpair]

    ref_df = pd.read_csv(reference_file, sep = "\t")
    merged = pd.merge(result_df, ref_df, how='inner', on = "protein",suffixes = ["", "_ref"])
    ax_p = merged.plot.scatter(x='pval_ref',y='pval')
    plt.show()
    ax_fc = merged.plot.scatter(x='log2FC_ref',y='fc')
    plt.show()
    ax_fdr = merged.plot.scatter(x='fdr_ref',y='fdr')
    plt.show()

# Cell
import pandas as pd
import matplotlib.pyplot as plt
def compare_normalization(ref_normalization_file, norm1_df, norm2_df):
    ref_normed = pd.read_csv(ref_normalization_file, sep ="\t").set_index('peptide')

    merged = pd.merge(norm1_df, norm2_df, how='inner',  left_index = True, right_index = True)
    columns = merged.columns
    merged = pd.merge(ref_normed, merged, how='inner', left_index = True, right_index = True, suffixes = ["_ref", ""])

    for i in range(len(columns)):
        sample1 = columns[i]
        sample2 = sample1+"_ref"
        ax_p = merged.plot.scatter(x=sample1,y=sample2)
        plt.show()

# Cell
import pandas as pd
import numpy as np
import alphaquant.plotting.base_functions as aqviz

def compare_to_reference(peptide_detail_file, result_df, peptide_df, protref_file, outdir):
    protein_ref = pd.read_csv(peptide_detail_file, sep="\t", usecols=["protein", "protein_pval", "protein_fc"]).drop_duplicates().rename(columns = {"protein_pval" : "pval_ref", "protein_fc": "log2fc_ref"})
    peptide_ref = pd.read_csv(peptide_detail_file, sep='\t', usecols = ["peptide", "protein", "peptide_pval","peptide_fc"]).rename(columns = {"peptide_pval" :"peptide_pval_ref", "peptide_fc" : "peptide_fc_ref"})
    aqviz.compare_peptid_protein_overlaps(protein_ref, result_df, peptide_ref, peptide_df, peptide_name = "peptide")
    compare_significant_proteins(result_df, protref_file)

    print_nonref_hits(protein_ref, result_df, peptide_ref, peptide_df, outdir)
    prots_merged = pd.merge(protein_ref, result_df, on = "protein", how='inner')
    peps_per_prot_ref = pd.DataFrame(peptide_ref.groupby(by=["protein"])['peptide'].count()).rename(columns = {"peptide":"num_peptides_ref"}).reset_index()
    prots_merged = pd.merge(prots_merged, peps_per_prot_ref, on = "protein", how='inner')

    peptides_merged = pd.merge(peptide_ref, peptide_df, on = "peptide", how='inner')

    peptides_merged["peptide_pval_diff"] = ( peptides_merged["peptide_pval"]/peptides_merged["peptide_pval_ref"]).abs()
    peptides_merged = peptides_merged.sort_values(by=['peptide_pval_diff'], ascending = False)
    display(peptides_merged.head(10))
    peptides_merged.to_csv(f"{outdir}/merged_peptides.tsv", sep = "\t", index = False)
    aqviz.scatter_df_columns(prots_merged)
    aqviz.scatter_df_columns(peptides_merged)

    prots_merged["pvaldiff"] = (np.log2(prots_merged["pval"]) - np.log2(prots_merged["pval_ref"])).abs()
    prots_merged = prots_merged.sort_values(by=['pvaldiff'], ascending = False)
    peptides_merged.to_csv(f"{outdir}/merged_proteins.tsv", sep = "\t", index = False)
    display(prots_merged.head(10))
    display(peptides_merged)


    prots_merged["numpep_diff"] = (prots_merged["num_peptides"] - prots_merged["num_peptides_ref"]).abs()
    prots_merged = prots_merged.sort_values(by=['numpep_diff'], ascending = False)
    display(prots_merged.head(10))

# Cell
from matplotlib import pyplot as plt

def compare_significant_proteins(result_df, protref_file):
    protein_ref = pd.read_csv(protref_file, sep="\t")
    sigprots_ref = protein_ref[protein_ref["fdr"]<0.05]
    sigprots = result_df[result_df["fdr"]<0.05]
    prots_ref = set(sigprots_ref["protein"].to_list())
    prots = set(sigprots["protein"].to_list())
    LOGGER.info(f"in ref only {prots_ref - prots}")
    LOGGER.info(f"in AP only {prots-prots_ref}")
    plt.show()

# Cell
def print_nonref_hits(protein_ref, protein_df, peptide_ref, peptide_df, outdir):
    prots_nonref_df =  protein_df[~(protein_df["protein"].isin(protein_ref["protein"].to_list()))]#the tilde inverts the boolean vector
    peps_nonref_df = peptide_df[~(peptide_df["peptide"].isin(peptide_ref["peptide"].to_list()))]
    prots_nonref_df.to_csv(f"{outdir}/nonref_proteins.tsv", sep = "\t", index = False)
    peps_nonref_df.to_csv(f"{outdir}/nonref_peptides.tsv", sep = "\t", index = False)
    #display(peps_nonref_df)

# Cell
import pandas as pd
import numpy as np
import uuid
import random

def test_run_pipeline():

    sample2cond_df = pd.DataFrame({'sample' : ['A1', 'A2', 'A3', 'B1', 'B2', 'B3','B4', 'B5', 'B6', 'B7', 'B8', 'B9','B10', 'B11', 'B12'],
    'condition' : ['A', 'A', 'A', 'B', 'B', 'B','B', 'B', 'B','B', 'B', 'B','B', 'B', 'B']})
    unnormed_df = generate_random_input(10000, sample2cond_df)
    res_df, pep_df = run_pipeline(unnormed_df, sample2cond_df, 2, False)
    plot_pvals(pep_df)

def generate_random_input(num_pep,sample2cond_df , simulate_nas = False, systematic_offset = 0):
    pepnames = generate_peptide_list(num_pep, [2, 3, 5, 3]) #gives uuid strings for each peptide
    protnames = generate_protein_list(pepnames)
    nrep_1 = get_num_samples_for_cond(sample2cond_df, "A")
    nrep_2 = get_num_samples_for_cond(sample2cond_df, "B")
    randarrays1 = 10+ 1.5*np.random.randn(len(pepnames),nrep_1)
    randarrays2 = 10+ 3.5*np.random.randn(len(pepnames),nrep_2)

    if simulate_nas:
        idxs_1 = np.unique(np.random.randint(0, nrep_1, size= int(len(randarrays1)/3)))
        randarrays1[idxs_1] = np.nan
        idxs_2 = np.unique(np.random.randint(0, nrep_2, size= int(len(randarrays2)/3)))
        randarrays2[idxs_2] = np.nan

    randarrays = np.concatenate((randarrays1, randarrays2), axis = 1)
    df_intens = pd.DataFrame(randarrays, columns= sample2cond_df["sample"].tolist())
    df_intens.insert(1,"protein", protnames)
    df_intens.insert(0, QUANT_ID, pepnames )
    df_intens = df_intens.set_index(QUANT_ID)
    return df_intens

def get_num_samples_for_cond(sample2cond_df, cond):
    return len(sample2cond_df[sample2cond_df["condition"]==cond])

def generate_peptide_list(num_peps, levels ):
    """levels is list of ints, each int inidcates, how many potential possibilities there are on this level"""
    pepcount = 0
    count = 0
    peptides = []
    while count < num_peps:
        list = [f'pep{pepcount}']

        for levelidx, level in enumerate(levels):
            num_events = np.random.randint(1,level)
            new_list = []
            for elem in list:
                for idx in range(num_events):
                    new_list.append(elem + f"_LVL{levelidx}_mod{idx}")
                    count+=1
            list = new_list
        peptides.extend(list)
        pepcount+=1

    return peptides



def generate_protein_list(pepnames):
    res = []
    assigned = 0
    protcount = 0
    while assigned < len(pepnames):
        protstring = f"P{protcount}"
        num_peps = random.randint(2,10)
        for i in range(num_peps):
            res.append(protstring)
        assigned+=num_peps
        protcount+=1
    res = res[:len(pepnames)]
    return res


# Utility functions to compare against other methods

def annotate_fcs_to_wideformat_table(wideformat_df, columns_intens_c1, columns_intens_c2, num_reps = None):
    wideformat_df[columns_intens_c1+columns_intens_c2] = wideformat_df[columns_intens_c1+columns_intens_c2].replace(0, np.nan)
    prots_c1 = wideformat_df[columns_intens_c1]
    prots_c2 = wideformat_df[columns_intens_c2]

    prots_c1 = prots_c1.dropna(thresh = num_reps) #if None then no nans, i.e. all replicates
    prots_c2 = prots_c2.dropna(thresh = num_reps)
    both_idx = prots_c1.index.intersection(prots_c2.index)
    wideformat_df["median_int_c1"] = prots_c1.loc[both_idx].median(axis = 1, skipna = True)
    wideformat_df["median_int_c2"] = prots_c2.loc[both_idx].median(axis = 1, skipna = True)
    wideformat_df["median_intensity"] = (wideformat_df["median_int_c1"] + wideformat_df["median_int_c2"])/2
    wideformat_df = wideformat_df.loc[both_idx]
    wideformat_df[f"log2fc"] = np.log2(wideformat_df[f"median_int_c1"]) - np.log2(wideformat_df[f"median_int_c2"])
    return wideformat_df

# Cell
def prepare_mq_table(mq_df, columns_intens_c1, columns_intens_c2):
    mq_df = mq_df[mq_df["Species"]!= np.nan]
    mq_df = mq_df[mq_df['Reverse']!= "+"]
    mq_df = mq_df[mq_df['Potential contaminant'] != "+"]
    mq_df = mq_df.rename(columns = {'Species' : "PG.Organisms", 'Protein IDs' : 'protein'})
    mq_df[columns_intens_c1+columns_intens_c2] = mq_df[columns_intens_c1+columns_intens_c2].replace(0, np.nan)
    prots_c1 = mq_df[columns_intens_c1]
    prots_c2 = mq_df[columns_intens_c2]

    prots_c1 = prots_c1.dropna(thresh = 2)
    prots_c2 = prots_c2.dropna(thresh = 2)
    both_idx = prots_c1.index.intersection(prots_c2.index)

    mq_df["median_int_c1"] = prots_c1.loc[both_idx].median(axis = 1, skipna = True)
    mq_df["median_int_c2"] = prots_c2.loc[both_idx].median(axis = 1, skipna = True)
    mq_df = mq_df.loc[both_idx]
    mq_df[f"log2fc"] = np.log2(mq_df[f"median_int_c1"]) - np.log2(mq_df[f"median_int_c2"])
    mq_df["method"] = ["MaxQuant" for x in range(len(mq_df.index))]
    return mq_df

# System-wide benchmark

def cluster_selected_proteins(protnames, quant_df, normed_c1, normed_c2, pval_threshold_basis = 0.05, fcfc_threshold = 0, take_median_ion=False):
    pep2prot = dict(zip(quant_df.index, quant_df['protein']))
    ions_to_check = normed_c1.ion2nonNanvals.keys() & normed_c2.ion2nonNanvals.keys()
    deedpair2doublediffdist = {}
    bgpair2diffDist = {}
    p2z = {}
    prot2diffions = {}
    root_node = anytree.Node('parent')
    for ion in ions_to_check:
        protein = pep2prot.get(ion)
        if protein not in protnames:
            continue
        vals1 = normed_c1.ion2nonNanvals.get(ion)
        vals2 = normed_c2.ion2nonNanvals.get(ion)
        bg1 = normed_c1.ion2background.get(ion.name)
        bg2 = normed_c2.ion2background.get(ion.name)
        diffDist = aqbg.get_subtracted_bg(bgpair2diffDist,bg1, bg2, p2z)

        diffIon = aqdiff.DifferentialIon(vals1, vals2, diffDist, ion,outlier_correction=False)


        prot_ions = prot2diffions.get(protein, list())
        prot_ions.append(diffIon)
        prot2diffions[protein] = prot_ions

    for prot in prot2diffions.keys():
        ions = prot2diffions.get(prot)
        clustered_root_node = aqclust.get_scored_clusterselected_ions(prot, ions, normed_c1, normed_c2, bgpair2diffDist, p2z, deedpair2doublediffdist, pval_threshold_basis = pval_threshold_basis, fcfc_threshold = fcfc_threshold, take_median_ion=take_median_ion)
        clustered_root_node.parent = root_node

    return root_node

import alphaquant.norm.normalization as aqnorm
def create_background_dists_from_prepared_files(samplemap_file, quant_file, cond1, cond2):


    quant_df = pd.read_csv(quant_file, sep = "\t",index_col= QUANT_ID)
    samplemap_df = aqdiffutils.load_samplemap(samplemap_file)

    df_c1, df_c2, c1_samples, c2_samples = get_c1_c2_dfs(quant_df, samplemap_df, [cond1, cond2])

    df_c1, df_c2 = aqnorm.get_normalized_dfs(df_c1, df_c2, c1_samples, c2_samples, minrep= min(len(df_c1.columns), len(df_c2.columns)), runtime_plots = False)#filter for no missing values
    p2z = {}
    normed_c1 = aqbg.ConditionBackgrounds(df_c1, p2z)
    normed_c2 = aqbg.ConditionBackgrounds(df_c2, p2z)
    return quant_df, normed_c1, normed_c2


def get_c1_c2_dfs(unnormed_df, labelmap_df, condpair, minrep = 2):
    c1_samples = labelmap_df[labelmap_df["condition"]== condpair[0]]
    c2_samples = labelmap_df[labelmap_df["condition"]== condpair[1]]
    df_c1 = unnormed_df.loc[:, c1_samples["sample"]].dropna(thresh=minrep, axis=0)
    df_c2 = unnormed_df.loc[:, c2_samples["sample"]].dropna(thresh=minrep, axis=0)

    return df_c1, df_c2, c1_samples, c2_samples


# Cell
import alphaquant.run_pipeline as aqmgr
import alphaquant.norm.normalization as aqnorm
import alphaquant.cluster.cluster_ions as aqclust
import alphaquant.diffquant.diffutils as aqdiffutils
import alphaquant.utils.utils as aqutils
import anytree
import math
import os
import alphaquant.diffquant.background_distributions as aqbg
import pandas as pd
import alphaquant.diffquant.condpair_analysis as aq_condpair


def load_real_example_ions(input_file, samplemap_file, num_ions = 20, condpair = ('S1', 'S2'), minrep = 4):
    p2z = {}
    samplemap_df = aqdiffutils.load_samplemap(samplemap_file)
    fragion_df = pd.read_csv(input_file, sep = "\t")
    _, samplemap_df = aqdiffutils.prepare_loaded_tables(fragion_df, samplemap_df)
    fragion_df = fragion_df.set_index(QUANT_ID)


    df_c1, df_c2, c1_samples, c2_samples = format_condpair_input(samplemap_df = samplemap_df, input_file=input_file,condpair = condpair, minrep= minrep)
    #df_c1_normed, df_c2_normed = aqnorm.normalize_if_specified(df_c1, df_c2, c1_samples, c2_samples, minrep=4, runtime_plots = False)
    normed_c1 = aqbg.ConditionBackgrounds(df_c1, p2z)
    normed_c2 = aqbg.ConditionBackgrounds(df_c2, p2z)
    diffions = get_subset_of_diffions(normed_c1, normed_c2, num_ions)
    return diffions, normed_c1, normed_c2



def get_grouped_diffions_for_node(type_node, diffions):
    name2diffion = {x.name : x for x in diffions}
    grouped_diffions = []
    for child in type_node.children:
        all_diffion_names_for_child = [x.name for x in child.leaves]
        diffions_for_child = [name2diffion.get(x) for x in all_diffion_names_for_child]
        grouped_diffions.append(diffions_for_child)
    return grouped_diffions


def format_condpair_input(samplemap_df, condpair, minrep, input_file):
    LOGGER.info(condpair)
    samples_c1, samples_c2 = aqdiffutils.get_samples_used_from_samplemap_df(samplemap_df, condpair[0], condpair[1])
    input_df_local = aq_condpair.get_unnormed_df_condpair(input_file = input_file, samplemap_df = samplemap_df, condpair = condpair, file_has_alphaquant_format = True)
    df_c1, df_c2 = aq_condpair.get_per_condition_dataframes(samples_c1, samples_c2, input_df_local, minrep, "both", None, None)
    return df_c1, df_c2, samples_c1, samples_c2

def get_filtered_protnodes(condpair, results_dir_unfiltered):
    condpairtree = aqutils.read_condpair_tree(condpair[0], condpair[1], results_dir_unfiltered)
    protnodes = condpairtree.children
    selected_protnodes = []
    for protnode in protnodes:
        filtered_protnode = filter_check_protnode(protnode)
        if filtered_protnode == None:
            continue
        if (filtered_protnode.fc >0.2) or (filtered_protnode.p_val < 0.05) :
            continue
        selected_protnodes.append(filtered_protnode)

    return selected_protnodes



def filter_check_protnode(protnode):

    # filter the base nodes, prepare the ms1 and fragion nodes
    for base_node in protnode.leaves:
        if base_node.cluster != 0:
            base_node.parent = None
    frgion_ms1_nodes = anytree.search.findall(protnode, filter_=lambda node:  (node.type == 'frgion') or (node.type == 'ms1_isotopes'))

    check_nodes = set()
    #annotate if fragion_ms1 has enough leafs
    for frg_ms1_node in frgion_ms1_nodes:
        if len(frg_ms1_node.leaves) <3:
            frg_ms1_node.parent = None
        else:
            check_nodes.add(frg_ms1_node)


    type2required_children = {"mod_seq_charge":2, "mod_seq":2, "seq":1, "gene":3}
    nodetypes = ["mod_seq_charge", "mod_seq", "seq", "gene"]

    for nodetype in nodetypes:
        check_nodes =  anytree.search.findall(protnode, filter_=lambda node:  node.type == nodetype) #for each level, check if there are enough children
        for check_node in check_nodes:
            num_children = len([x for x in check_node.children if (x.cluster ==0)])
            if (num_children<type2required_children.get(check_node.type)) or (check_node.fc > 0.1):
                check_node.parent = None
                if nodetype == "gene":
                    return None
            else:
                check_node.has_enough = True
    if len(check_nodes)==0:
        return None
    else:
        return list(check_nodes)[0]


import alphaquant.diffquant.diff_analysis as aqdiff

def get_subset_of_diffions(normed_c1, normed_c2, num_ions):
    ion2diffDist = {}
    p2z = {}
    diffions = []
    ions_to_check = normed_c1.ion2nonNanvals.keys() & normed_c2.ion2nonNanvals.keys()
    count_ions = 0
    for idx, ion in enumerate(ions_to_check):
        if count_ions==num_ions:
            break
        vals1 = normed_c1.ion2nonNanvals.get(ion)
        vals2 = normed_c2.ion2nonNanvals.get(ion)
        bg1 = normed_c1.ion2background.get(ion)
        bg2 = normed_c2.ion2background.get(ion)
        diffDist = aqbg.get_subtracted_bg(ion2diffDist, bg1, bg2,p2z)
        diffIon = aqdiff.DifferentialIon(vals1, vals2, diffDist, ion, outlier_correction = False)
        diffions.append(diffIon)
        count_ions+=1

    return diffions



def add_perturbations_to_proteins(protnodes):
    #go through each protein and randomly add perturbations at different levels, if a perturbation is added, propagate it to the children etc.
    for protnode in protnodes:
        for level_nodes in anytree.LevelOrderGroupIter(protnode, filter_= lambda x : 'gene' not in x.type): #iterate through all levels below protein
            for nodes_of_interest in group_level_nodes_by_parents(level_nodes):
                perturb = np.random.uniform(0, 1) < 0.3 #randomly select ~30% of the samples for perturbation
                num_perturb = math.ceil(len(nodes_of_interest)*0.2) if len(nodes_of_interest)>2 else 0
                perturb_idxs = random.sample(list(range(len(nodes_of_interest))), num_perturb)
                for sub_idx in range(len(nodes_of_interest)):
                    node_of_interest = nodes_of_interest[sub_idx]
                    applied_shift_parent = 0 if not hasattr(node_of_interest.parent, 'applied_shift') else node_of_interest.parent.applied_shift #check if the parent of the node already had a shift applied, if yes, add this shift
                    node_of_interest.applied_shift = applied_shift_parent
                    node_of_interest.applied_shift_local = 0
                    if (sub_idx in perturb_idxs) and perturb:
                        applied_shift = np.random.uniform(-2, 2)
                        node_of_interest.applied_shift += applied_shift
                        node_of_interest.applied_shift_local = applied_shift


def group_level_nodes_by_parents(nodes_of_interest):
    parent2nodes = {}
    for node in nodes_of_interest:
        parent2nodes[node.parent] = parent2nodes.get(node.parent, []) + [node]
    return list(parent2nodes.values())

def get_filtered_intensity_df(fragion_df, protnodes):

    ions_included = []
    for protnode in protnodes:
        ions_included.extend([x.name  for x in protnode.leaves if x.type == 'base'])

    #drop the unincluded ions
    fragion_df = fragion_df.loc[ions_included]

    return fragion_df


def get_perturbed_intensity_df(fragion_df, samplemap, protnodes):

    ion2shift = {}
    for protnode in protnodes:
        ion2shift.update({x.name : x.applied_shift for x in protnode.leaves if x.type =='base'})
    #drop the unincluded ions
    fragion_df = fragion_df.loc[list(ion2shift.keys())]

    #determine the factors to be added
    shifts_up = np.array([np.array([abs(ion2shift.get(x)) if ion2shift.get(x)> 0 else 0 for x in fragion_df.index])])
    shifts_down = np.array([np.array([abs(ion2shift.get(x)) if ion2shift.get(x)< 0 else 0 for x in fragion_df.index])])

    s1_samples = list(samplemap[samplemap["condition"]=="S1"]["sample"])
    s2_samples = list(samplemap[samplemap["condition"]=="S2"]["sample"])

    fragion_df[s1_samples] =fragion_df[s1_samples] +shifts_up.T
    fragion_df[s2_samples] =fragion_df[s2_samples]+shifts_down.T


    return fragion_df


def run_perturbation_test(input_file, samplemap, input_file_filtered = None, input_file_perturbed = None, run_diffanalysis_benchm_set = False, run_filtered = True,run_perturbed = True, run_perturbed_no_iontree = True, cluster_threshold_pval_perturbed = 0.01, runtime_plots = True):
    condpair_combinations = [("S1", "S2")]
    results_dir = "results"
    results_dir_filtered = "results_filtered"
    results_dir_perturbed = "results_perturbed"
    results_dir_perturbed_unclustered = "results_perturbed_unclustered"
    fragion_df = aqdiffutils.import_data(input_file)
    samplemap = aqdiffutils.load_samplemap(samplemap)
    fragion_df, samplemap = aqdiffutils.prepare_loaded_tables(fragion_df, samplemap)


    #run the diffanalysis of the basic dataset
    if run_diffanalysis_benchm_set:
        aqdiffutils.store_method_parameters({'input_file': str(input_file)}, results_dir)
        aqmgr.run_pipeline(fragion_df, samplemap, condpair_combinations=condpair_combinations, minrep = 9, runtime_plots=runtime_plots, cluster_threshold_pval=0.05, cluster_threshold_fcfc=0,results_dir=results_dir)

    #filter the analyzed results for consistent, low-FC proteins
    if (not os.path.exists(f"{results_dir}/S1_filtered_VS_S2_filtered.iontrees.json")) or (input_file_filtered == None):
        protnodes_filt = get_filtered_protnodes(condpair_combinations[0], results_dir_unfiltered=results_dir)
        fragion_df_only_filt = get_filtered_intensity_df(fragion_df, protnodes_filt)
        aqclust.export_roots_to_json(protnodes_filt,("S1_filtered", "S2_filtered"), results_dir)
        fragion_df_only_filt.reset_index().to_csv("filtered_fragions.tsv", sep = "\t", index = None)
    else:
        protnodes_filt = aqutils.read_condpair_tree("S1_filtered", "S2_filtered", results_dir).children

        fragion_df_only_filt = pd.read_csv("filtered_fragions.tsv", sep = "\t",index_col=QUANT_ID)


    #add perturbations to the filtered proteins
    if (not os.path.exists(f"{results_dir_perturbed}/S1_annot_VS_S2_annot.iontrees.json") or (input_file_perturbed == None)):
        add_perturbations_to_proteins(protnodes_filt)
        if not os.path.exists(results_dir_perturbed):
            os.makedirs(results_dir_perturbed)
        aqclust.export_roots_to_json(protnodes_filt,("S1_annot", "S2_annot"), results_dir_perturbed)
        fragion_df_perturbed = get_perturbed_intensity_df(fragion_df, samplemap, protnodes_filt)
        fragion_df_perturbed.reset_index().to_csv("perturbed_fragions.tsv", sep = "\t", index = None)
    else:
        protnodes_filt = aqutils.read_condpair_tree("S1_annot", "S2_annot", results_dir_perturbed).children
        fragion_df_perturbed = pd.read_csv(input_file_perturbed, sep = "\t",index_col=QUANT_ID)


    if run_filtered:
        aqmgr.run_pipeline(fragion_df_only_filt, samplemap, condpair_combinations=condpair_combinations, minrep = 9, normalize=True, runtime_plots=runtime_plots, use_iontree_if_possible=False, results_dir= results_dir_filtered)

    if run_perturbed_no_iontree:
        aqmgr.run_pipeline(fragion_df_perturbed, samplemap, condpair_combinations=condpair_combinations, minrep = 9,  normalize=True, runtime_plots=runtime_plots,use_iontree_if_possible=False,results_dir=results_dir_perturbed_unclustered)

    if run_perturbed:
        aqmgr.run_pipeline(fragion_df_perturbed, samplemap, condpair_combinations=condpair_combinations, minrep = 9,  normalize=True, runtime_plots=runtime_plots, cluster_threshold_pval=cluster_threshold_pval_perturbed, cluster_threshold_fcfc=0,results_dir=results_dir_perturbed)




# Cell
import alphaquant.plotting.base_functions as aqviz
import alphaquant.diffquant.diffutils as aqdiffutils
import sklearn.metrics


def compare_cluster_to_benchmarks(results_dir_unperturbed, results_dir_perturbed, results_dir_perturbed_unclustered):
    aqviz.compare_fcs_unperturbed_vs_perturbed_and_clustered(results_dir_unperturbed,results_dir_perturbed, results_dir_perturbed_unclustered)


def evaluate_per_level(level2annotated_shift, level2classified_shift):
    for level in level2annotated_shift.keys():
        y_true = level2annotated_shift.get(level)
        y_pred = level2classified_shift.get(level)
        metrics = sklearn.metrics.precision_recall_fscore_support(y_true=y_true, y_pred=y_pred)
        accuracy = sklearn.metrics.accuracy_score(y_true=y_true, y_pred= y_pred)
        LOGGER.info(f"level {level}")
        LOGGER.info(f"accuracy:{accuracy}\tprecision:{metrics[0]}\trecall{metrics[1]}\tfscore{metrics[2]}")


def count_correctly_excluded(protnodes_annotated, protnodes_clustered):
    level2annotated_shift = {}
    level2classified_shift = {}
    name2node_annot = {x.name : x for x in protnodes_annotated}
    name2node_clustered = {x.name : x for x in protnodes_clustered}
    for name in name2node_annot.keys():
        protnode_annotated = name2node_annot.get(name)
        protnode_clustered = name2node_clustered.get(name)
        for annot_nodes in anytree.LevelOrderGroupIter(protnode_annotated, filter_= lambda x : 'gene' not in x.type):
            for annot_node in annot_nodes:
                clustered_node = anytree.find(protnode_clustered, filter_= lambda x : annot_node.name == x.name)
                annot_shifted = annot_node.applied_shift_local!=0
                cluster_nonzero = clustered_node.cluster != 0
                if (not annot_shifted) and (not cluster_nonzero):
                    continue
                level2annotated_shift[annot_node.type] = level2annotated_shift.get(annot_node.type, [])
                level2classified_shift[annot_node.type] = level2classified_shift.get(clustered_node.type, [])
                level2annotated_shift[annot_node.type].append(annot_shifted)
                level2classified_shift[annot_node.type].append(cluster_nonzero)
    evaluate_per_level(level2annotated_shift, level2classified_shift)


def eval_clustered_results(results_perturbed):
    protnodes_annot = aqutils.read_condpair_tree("S1_annot", "S2_annot", results_folder=results_perturbed).children
    protnodes_perturbed = aqutils.read_condpair_tree("S1", "S2", results_folder=results_perturbed).children
    count_correctly_excluded(protnodes_annot, protnodes_perturbed)





# Prepare Benchmarking Sets



def spectronaut_filtering(table_df, undesired_peptides, desired_organism):
    table_df = table_df[[(x not in undesired_peptides) for x in table_df['PEP.StrippedSequence']]]
    if desired_organism is not None:
        table_df = table_df[table_df["PG.Organisms"] == desired_organism]

    return table_df

def diann_filtering(table_df, undesired_peptides, desired_organism):
    table_df = table_df[[(x not in undesired_peptides) for x in table_df['Stripped.Sequence']]]
    if desired_organism is not None:
        table_df = table_df[[(desired_organism in x) for x in table_df['Protein.Names']]]
    return table_df


def decide_filter_function(input_table):
    columns_table = pd.read_csv(input_table, sep = "\t", nrows=2).columns
    if "PG.Organisms" in columns_table:
        software_filter_function = spectronaut_filtering
    elif 'Protein.Names' in columns_table:
        software_filter_function = diann_filtering
    else:
        raise Exception("file for filtering does not have the needed columns!")
    return software_filter_function


# Spike-in Benchmarks
import alphaquant.diffquant.diffutils as aqdiffutils
import seaborn as sns
import alphaquant.plotting.base_functions as aqplot
import os.path
import anytree
import copy
import numpy as np


def compare_aq_to_reference(protein_nodes, expected_log2fc, condpair, software_used, name, original_input_file, samplemap,quant_level_aq, quant_level_reference, tolerance_interval, xlim_lower, xlim_upper, savedir, ml_score_cutoff, ml_exclude, percentile_to_retain, num_reps):

    fig, ax = plt.subplots(nrows = 3, ncols = 3, figsize=(15,15))
    fig.suptitle(f"{software_used}, {aqdiffutils.get_condpairname(condpair)}")
    nodes_precursors = generate_precursor_nodes_from_protein_nodes(protein_nodes, type=quant_level_aq)
    shift_to_expected_fc(nodes_precursors, expected_log2fc)

    #aqplot.plot_fc_dist_of_test_set(fcs = [x.fc for x in nodes_precursors], ax = ax[2][2])

    true_falses, ml_scores, reference_scores, fcs = aqplot.get_true_false_to_ml_scores(nodes_precursors, expected_log2fc)

    aqplot.plot_true_false_fcs_of_test_set(fcs=fcs, true_falses=true_falses, ax= ax[0][0])
    aqplot.plot_predictability_roc_curve(true_falses=true_falses, ml_scores=ml_scores, reference_scores=reference_scores, ax = ax[0][1], percentile_cutoff_indication=percentile_to_retain)
    aqplot.plot_predictability_precision_recall_curve(true_falses=true_falses, ml_scores=ml_scores, reference_scores=reference_scores, ax=ax[0][2], percentile_cutoff_indication=percentile_to_retain)


    if ml_score_cutoff is not None:
        nodes_precursors = [x for x in nodes_precursors if abs(x.ml_score)<ml_score_cutoff]
    if (ml_score_cutoff is None) and (ml_exclude):
        nodes_precursors = [x for x in nodes_precursors if not x.ml_excluded]



    original_df_reformat = get_original_input_df( c1 = condpair[0], c2 = condpair[1], input_file = original_input_file, samplemap_file = samplemap, input_type = quant_level_reference, num_reps = num_reps)
    node_df = get_node_df(nodes_precursors = nodes_precursors)


    if percentile_to_retain is not None:
        rough_tpr_cutoff = get_rough_tpr_cutoff(percentile_to_retain, true_falses)
        original_df_reformat, node_df = filter_top_qualityscore_percentiles(df_original=original_df_reformat, df_nodes=node_df, nodes_precursors=nodes_precursors, percentile=rough_tpr_cutoff, method=software_used)
        doublecheck_df_reformat = filter_score_from_original_df(original_input_file=original_input_file, input_type= quant_level_reference, c1 = condpair[0], c2 = condpair[1], samplemap_file=samplemap,percentile_to_use= rough_tpr_cutoff,minrep=num_reps)


    frac_outliers = aqdiffutils.count_fraction_outliers_from_expected_fc(original_df_reformat, tolerance_interval, expected_log2fc)
    aqplot.plot_fc_intensity_scatter(original_df_reformat, f"{software_used} ({frac_outliers:.2f})", expected_log2fc = expected_log2fc, tolerance_interval = tolerance_interval, xlim_lower=xlim_lower, xlim_upper = xlim_upper, ax = ax[1][0])
    aqplot.plot_fc_intensity_scatter(doublecheck_df_reformat, f"{software_used} doublecheck", expected_log2fc = expected_log2fc, tolerance_interval = tolerance_interval, xlim_lower=xlim_lower, xlim_upper = xlim_upper, ax = ax[1][2])
    frac_outliers_aq = aqdiffutils.count_fraction_outliers_from_expected_fc(node_df, tolerance_interval, expected_log2fc)
    aqplot.plot_fc_intensity_scatter(node_df, f"AlphaQuant ({frac_outliers_aq:.2f})", expected_log2fc = expected_log2fc, tolerance_interval = tolerance_interval, xlim_lower=xlim_lower, xlim_upper = xlim_upper, ax = ax[1][1])


    aqplot.plot_violin_plots_log2fcs([software_used, 'AlphaQuant'], [original_df_reformat, node_df], ax = ax[2][0])
    aqplot.plot_beeswarm_plot_log2fcs([software_used, 'AlphaQuant'], [original_df_reformat, node_df], ax = ax[2][1])

    aqplot.plot_outlier_fraction(node_df, reference_df = original_df_reformat, expected_log2fc=expected_log2fc, outlier_thresholds=[1.0, 0.5, 0.3], ax = ax[2][2])
    fig.tight_layout()
    plt.savefig(f"{savedir}/{name}_{software_used}.pdf")

    ax[0][0].figure.savefig(f"{savedir}/{name}_fc_dist.pdf")
    ax[0][1].figure.savefig(f"{savedir}/{name}_predictability_roc_curve.pdf")
    ax[0][2].figure.savefig(f"{savedir}/{name}_predictability_precision_recall_curve.pdf")
    ax[1][0].figure.savefig(f"{savedir}/{name}_{software_used}_fc_intensity_scatter.pdf")
    ax[1][1].figure.savefig(f"{savedir}/{name}_AlphaQuant_fc_intensity_scatter.pdf")
    ax[2][0].figure.savefig(f"{savedir}/{name}_violin_plot.pdf")
    ax[2][1].figure.savefig(f"{savedir}/{name}_beeswarm_plot.pdf")
    ax[2][1].figure.savefig(f"{savedir}/{name}_fraction_outliers.pdf")

    plt.show()




def shift_to_expected_fc(nodes_precursors, expected_log2fc):
    median_fc = np.median([x.fc for x in nodes_precursors])
    diff = expected_log2fc - median_fc
    for node in nodes_precursors:
        node.fc +=diff


def get_rough_tpr_cutoff(percentile_to_retain, true_false_vec):
    fraction_true = sum(true_false_vec)/len(true_false_vec)
    return fraction_true*percentile_to_retain



def get_top_percentile_node_df(nodes, percentile, node_filterfunction = None):

    if node_filterfunction is not None:
        nodes = [x for x in nodes if node_filterfunction(x)]
    nodes_sorted = sorted(nodes,key= lambda x : abs(x.ml_score))
    nodes_sorted = nodes_sorted[:int(len(nodes_sorted)*percentile)]
    return get_node_df(nodes_sorted)


def filter_top_qualityscore_percentiles(df_original, df_nodes, nodes_precursors, percentile, method, node_filterfunction = None):
    top_precursors_aqscore, top_precursors_default_quality_score = get_top_percentile_peptides(nodes_precursors=nodes_precursors, percentile = percentile, method = method, node_filterfunction = node_filterfunction)
    df_original = df_original[[x in top_precursors_default_quality_score for x in df_original[QUANT_ID]]]
    df_nodes = df_nodes[[x in top_precursors_aqscore for x in df_nodes[QUANT_ID]]]

    return df_original, df_nodes




def get_top_percentile_peptides(nodes_precursors, percentile, method, node_filterfunction = None):
    if node_filterfunction is not None:
        nodes_precursors = [x for x in nodes_precursors if node_filterfunction(x)]
    nodes_aqscore_sorted = sorted(nodes_precursors, key = lambda x : abs(x.ml_score))
    nodes_default_quality_score_sorted = sorted(nodes_precursors, key = lambda x : abs(x.default_quality_score), reverse=True) #the quality scores are higher is better, the ml_score is lower is better

    #get the percentiles
    nodes_default_quality_score_sorted = nodes_default_quality_score_sorted[:int(percentile*len(nodes_default_quality_score_sorted))]
    nodes_aqscore_sorted = nodes_aqscore_sorted[:int(percentile*len(nodes_aqscore_sorted))]

    #get the precursor names
    if method == "Spectronaut":
        treename2simplename = convert_tree_ionname_to_simple_ionname_sn(nodes_precursors)
    if method =="DIANN":
        treename2simplename = convert_tree_ionname_to_simple_ionname_diann(nodes_precursors)

    precursors_default_quality_score = {treename2simplename.get(x.name) for x in nodes_default_quality_score_sorted}
    precursors_aqscore = {x.name for x in nodes_aqscore_sorted}
    return precursors_aqscore, precursors_default_quality_score

def compare_aq_w_method(nodes_precursors, c1, c2, spectronaut_file, samplemap_file, expected_log2fc = None, threshold = 0.5, input_type = "spectronaut_precursor", num_reps = None, method_name = "Spectronaut", tolerance_interval = 1, xlim_lower = -1, xlim_upper = 3.5):
    specnaut_reformat = get_original_input_df( c1 = c1, c2 = c2, input_file = spectronaut_file, samplemap_file = samplemap_file, input_type = input_type, num_reps = num_reps, expected_log2fc=expected_log2fc)
    node_df = get_node_df(nodes_precursors = nodes_precursors)
    aqdiffutils.count_fraction_outliers_from_expected_fc(specnaut_reformat, threshold, expected_log2fc)
    aqplot.plot_fc_intensity_scatter(specnaut_reformat, method_name, expected_log2fc = expected_log2fc, tolerance_interval = tolerance_interval, xlim_lower=xlim_lower, xlim_upper = xlim_upper)
    aqdiffutils.count_fraction_outliers_from_expected_fc(node_df, threshold, expected_log2fc)
    aqplot.plot_fc_intensity_scatter(node_df, "AlphaQuant", expected_log2fc = expected_log2fc)

def import_input_file_in_specified_format(input_file, input_type):
    LOGGER.info(f"use input type {input_type}")
    reformat_file = f"{input_file}.{input_type}.aq_reformat.tsv"
    if os.path.isfile(reformat_file):
        specnaut_reformat = pd.read_csv(reformat_file, sep = "\t", encoding ='latin1')
    else:
        specnaut_reformat = aqdiffutils.import_data(input_file, input_type_to_use=input_type)
    return specnaut_reformat

def get_original_input_df(c1, c2, input_file, samplemap_file, num_reps, expected_log2fc  = None,input_type = "spectronaut_precursor"):
    specnaut_reformat = import_input_file_in_specified_format(input_file=input_file, input_type=input_type)
    samplemap_df = aqdiffutils.load_samplemap(samplemap_file)
    c1_samples = list(samplemap_df[samplemap_df["condition"]==c1]["sample"])
    c2_samples = list(samplemap_df[samplemap_df["condition"]==c2]["sample"])
    specnaut_reformat = annotate_fcs_to_wideformat_table(specnaut_reformat,c1_samples, c2_samples, num_reps = num_reps)
    if expected_log2fc is not None:
        specnaut_reformat = correct_fcs_to_expected(specnaut_reformat, expected_log2fc)

    return specnaut_reformat

import numpy as np
def correct_fcs_to_expected(specnaut_reformat, expected_log2fc):
    log2fcs = specnaut_reformat["log2fc"]
    median_fc = np.median(log2fcs)
    diff = expected_log2fc-median_fc
    specnaut_reformat["log2fc"] = [x+diff for x in log2fcs]
    return specnaut_reformat


def get_node_df(nodes_precursors):
    node_info_dict = {QUANT_ID: [x.name for x in nodes_precursors], 'log2fc' : [x.fc for x in nodes_precursors], "median_intensity" : [x.min_intensity for x in nodes_precursors]}
    node_df = pd.DataFrame(node_info_dict)
    return node_df





def generate_precursor_nodes_from_protein_nodes(protein_nodes, shift_fc = None, type = "mod_seq_charge"):
    all_precursors = []
    for protein in protein_nodes:
        precursors = anytree.findall(protein, filter_= lambda x : (x.type == type))
        all_precursors.extend(precursors)
    all_precursors = [copy.copy(x) for x in all_precursors]
    if shift_fc is not None:
        for precursor in all_precursors:
            precursor.fc +=shift_fc
    return all_precursors

import re
def convert_tree_ionname_to_simple_ionname_sn(nodes):
    tree2simple = {}
    for node in nodes:
        groups = re.match("(.*MOD_)(.*)(_CHARGE_)(.*)(_.*)",node.name)
        tree2simple[node.name] = f"{groups[2]}.{groups[4]}"
    return tree2simple

def convert_tree_ionname_to_simple_ionname_diann(nodes):
    tree2simple = {}
    for node in nodes:
        groups = re.match("(.*MOD_)(.*)(_CHARGE_)(.*)(_.*)",node.name)
        tree2simple[node.name] = f"{groups[2]}{groups[4]}"
    return tree2simple



# Cell

def filter_score_from_original_df(original_input_file, input_type, c1, c2, samplemap_file, percentile_to_use, minrep):
    _, config_dict, _ = aqdiffutils.get_input_type_and_config_dict(input_file=original_input_file, input_type_to_use=input_type)

    sample_id = config_dict.get("sample_ID")
    precursor_id = config_dict.get("ion_cols")[0]


    #load samples
    samplemap = aqdiffutils.load_samplemap(samplemap_file)
    samples_c1 = list(samplemap[[x ==c1 for x in samplemap["condition"]]]["sample"])
    samples_c2 = list(samplemap[[x ==c2 for x in samplemap["condition"]]]["sample"])

    #retrieve ions used by AlphaQuant
    aq_df = import_input_file_in_specified_format(input_file = original_input_file, input_type= input_type)
    aq_df = aqdiffutils.filter_df_to_minrep(aq_df, samples_c1, samples_c2, minrep)
    ions_used_aq = set(aq_df[QUANT_ID])

    samplemap = samplemap[[x == c1 or x == c2 for x in samplemap["condition"]]] #only the condition samples remain
    condition_samples = set(samplemap["sample"])
    reference_df_it = pd.read_csv(original_input_file, sep = "\t", chunksize= 100_000)
    reference_dfs = []
    for df_chunk in reference_df_it:
        df_chunk = df_chunk.drop_duplicates(subset = [sample_id, precursor_id])
        df_chunk = df_chunk[[x in ions_used_aq for x in df_chunk[precursor_id]]]
        df_chunk = df_chunk[[x in condition_samples for x in df_chunk[sample_id]]]
        reference_dfs.append(df_chunk)

    reference_df = pd.concat(reference_dfs, ignore_index=True)

    quality_id = aqdiffutils.get_quality_score_column(reference_df)

    reference_df_filtered = filter_top_percentile_reference_df(reference_df, precursor_id, quality_id, percentile_to_use)
    filename = f"{original_input_file}_{aqdiffutils.get_condpairname((c1, c2))}_scorefilt_{percentile_to_use :.2f}.tsv"
    reference_df_filtered.to_csv(filename, sep = "\t", index = None)
    reformated_df = read_reformat_filtered_df(filtered_file=filename, input_type_to_use=input_type, samplemap_file=samplemap_file, c1 = c1, c2 = c2, num_rep= minrep)

    return reformated_df


def filter_top_percentile_reference_df(reference_df, precursor_id, quality_id, percentile_to_use):
    groupedref = reference_df.groupby([precursor_id]).mean().reset_index()
    groupedref = groupedref.sort_values(by=quality_id, ascending=False)
    first_sample = list(groupedref[precursor_id][:3])

    cutoff_threshold = int(percentile_to_use * len(groupedref.index))
    best_ranked_ions = list(groupedref[precursor_id][:cutoff_threshold])

    assert (first_sample == best_ranked_ions[:3])

    filtered_df = reference_df[[x in best_ranked_ions for x in reference_df[precursor_id]]]

    return filtered_df


def read_reformat_filtered_df(filtered_file, input_type_to_use, samplemap_file, c1, c2, num_rep):
    samplemap_df = aqdiffutils.load_samplemap(samplemap_file)
    input_df = aqdiffutils.import_data(filtered_file, input_type_to_use=input_type_to_use)
    #input_df, samplemap_df = aqdiffutils.prepare_loaded_tables(input_df, samplemap_df)

    c1_samples = list(samplemap_df[samplemap_df["condition"]==c1]["sample"])
    c2_samples = list(samplemap_df[samplemap_df["condition"]==c2]["sample"])
    annotated_df = annotate_fcs_to_wideformat_table(input_df,c1_samples, c2_samples, num_reps = num_rep)
    return annotated_df


# Cell
import alphaquant.benchm.benchmarking as aqbench
import alphaquant.plotting.base_functions as aqplot
import numpy as np
import alphaquant.classify.classify_precursors as aqclass
import alphaquant.diffquant.diffutils as aqdiffutils
import alphaquant.cluster.cluster_ions as aqclust
import anytree


def benchmark_configs_and_datasets(*,results_dir, expected_log2fcs,condpairs_to_check, original_input_file, samplemap_reference,  software_used, quant_levels_reference, quant_levels_aq = ['mod_seq_charge'], replace_nans = [True], distort_every_nth_precursor = [5, np.inf],
ml_score_cutoff = None, ml_exclude = False, percentile_to_retain = 0.7, num_reps = 9, num_splits_ml_set = 5):
    """obtain """

    for idx_condpair in range(len(condpairs_to_check)):
        condpair = condpairs_to_check[idx_condpair]
        for replace_nan in replace_nans:

            for distort_modulo in distort_every_nth_precursor:
                name_analysis_level = get_benchmark_setting_name(condpair = condpair, replace_nan=replace_nan, distort_number=distort_modulo)
                protein_nodes = load_tree_assign_ml_scores(c1 = condpair[0], c2 = condpair[1], samplemap=samplemap_reference,name= name_analysis_level, results_folder = results_dir, replace_nans= replace_nan,distort_precursor_modulo = distort_modulo,
                re_run_assignment=True, num_splits_ml_set = num_splits_ml_set)
                for quant_idx in range(len(quant_levels_aq)):

                    quant_level_aq = quant_levels_aq[quant_idx]
                    quant_level_reference = quant_levels_reference[quant_idx]
                    name = name_analysis_level+quant_level_reference
                    LOGGER.info(f"TESTING: {name}")

                    compare_aq_to_reference(protein_nodes, expected_log2fcs[idx_condpair], condpair=condpair, software_used=software_used, name = name, original_input_file=original_input_file, samplemap=samplemap_reference, quant_level_aq=quant_level_aq, quant_level_reference=quant_level_reference,
                    tolerance_interval = 1, xlim_lower = -1, xlim_upper = 3.5,savedir = results_dir,ml_score_cutoff = ml_score_cutoff, ml_exclude = ml_exclude, percentile_to_retain=percentile_to_retain, num_reps = num_reps)


def load_tree_assign_ml_scores(c1, c2, samplemap,name,results_folder, re_run_assignment  = False, results_folder_diann = None, replace_nans = False, distort_precursor_modulo = np.inf, num_splits_ml_set = 5):
    """retrieve the predictability scores from a previously run differential analysis. Re-run the predictability score analysis in case they are not available, or if specified"""
    s1, s2 = aqdiffutils.get_samples_used_from_samplemap_file(samplemap, c1, c2)
    cpair_tree = aqutils.read_condpair_tree(c1, c2, results_folder=results_folder)
    cpair_tree.type = "asd"
    protnodes = anytree.findall(cpair_tree, filter_= lambda x : (x.type == "gene"),maxlevel=2)

    if hasattr(protnodes[0],'ml_score') and not re_run_assignment:
        return protnodes

    aqclass.assign_predictability_scores(protnodes,results_folder,name = name, samples_used=s1+s2, precursor_cutoff=2, fc_cutoff=0, number_splits=num_splits_ml_set, plot_predictor_performance=True, replace_nans=replace_nans, distort_precursor_modulo = distort_precursor_modulo)
    if results_folder_diann is None:
        aqclust.update_nodes_w_ml_score(protnodes)
    return protnodes

def intersect_with_diann(c1, c2, protnodes,results_folder, results_folder_diann):
    diann_intersect = aqclass.get_intersect_sn_diann_precursors(c1, c2, results_folder, results_folder_diann)
    for protein in protnodes:
        precursors = anytree.findall(protein, filter_= lambda x : (x.type == "mod_seq_charge"))
        for precursor in precursors:
            if precursor.name not in diann_intersect:
                precursor.parent = None


def get_benchmark_setting_name(condpair, replace_nan, distort_number, diann_intersect_dir = None):
    name = f"{condpair[0]}_{condpair[1]}_distort_every{distort_number}_"
    if replace_nan:
        name+="nanreplace_"
    if diann_intersect_dir:#in the case that e.g. Spectronaut results are overlayed with DIANN results
        if "no_mbr" in diann_intersect_dir:
            name+="diann_intersect_no_mbr"
        else:
            name+="diann_intersect_mbr"

    return name

# Ratio Comparisons

## Classification tests

import pandas as pd
import functools


class ResultsTable():
    def __init__(self, input_file, input_name, fdr_threshold = 0.05):
        self._input_file = input_file
        self.input_name = input_name
        self.fdr_threshold = fdr_threshold
        self.protein_column = "protein"
        self.called_column = "called"
        self.species_column = "species"
        self.cond1_intensities = "pseudoint1"
        self.cond2_intensities = "pseudoint2"
        self.formated_dataframe = self._reformat_input_file_to_default_dataframe()

    def get_proteins(self):
        return self.formated_dataframe[self.protein_column]

    def subset_to_relevant_columns(self):
        return self.formated_dataframe[[self.protein_column, self.called_column, self.cond1_intensities, self.cond2_intensities]]

    def _reformat_input_file_to_default_dataframe(self):
        return

class ResultsTableRatios(ResultsTable):
    def __init__(self, input_file, input_name):
        super().__init__(input_file, input_name)
        self.log2fc_column = 'log2fc'
        self.mean_intensity_column = 'mean_intensity'
        self._add_mean_intensity_column()


    def _reformat_input_file_to_default_dataframe(self):
        return pd.read_csv(self._input_file, sep = "\t")

    def _add_mean_intensity_column(self):
        column1 = self.formated_dataframe[self.cond1_intensities]
        column2 = self.formated_dataframe[self.cond2_intensities]
        self.formated_dataframe[self.mean_intensity_column] = np.nanmean([column1, column2], axis=0)









class ResultsTableSpectronaut(ResultsTable):
    def __init__(self, input_file, input_name, fdr_threshold = 0.05):
        super().__init__(input_file=input_file, input_name=input_name, fdr_threshold=fdr_threshold)
        self.formated_dataframe = self._reformat_input_file_to_default_dataframe()
        self.formated_dataframe = super().subset_to_relevant_columns()


    def _reformat_input_file_to_default_dataframe(self):
        results_df = self.__read_and_rename_input_file()
        results_df = self.__determine_called_proteins(results_df)
        return results_df

    def __read_and_rename_input_file(self):
        results_df = pd.read_excel(self._input_file, sheet_name=2)
        results_df = results_df.rename(mapper = {'Protein': self.protein_column}, axis=1)
        return results_df

    def __determine_called_proteins(self, results_df):
        results_df[self.called_column] = [x<self.fdr_threshold for x in results_df["adjusted.pvalue"]]
        return results_df


class ResultsTableAlphaQuant(ResultsTable):
    def __init__(self, input_file, input_name, fdr_threshold = 0.05, pre_calculated_table = None):
        super().__init__(input_file=input_file, input_name=input_name, fdr_threshold=fdr_threshold)
        self.ml_score_column = "prediction_score"
        self.consistencyscore_column = "consistency_score"
        if input_file is not None:
            results_df = self.__read_input_file()
        else:
            results_df = pre_calculated_table
        self.formated_dataframe = self.__reformat_to_default_dataframe(results_df)
        self._formated_dataframe_nofilter = self.formated_dataframe
        self.formated_dataframe = self.__subset_to_relevant_columns()

    def reduce_formatted_df_to_best_available_score_quantile(self, percentile_to_retain):
        if self.ml_score_column in self.formated_dataframe.columns:
            self.reduce_formatted_df_to_ml_score_quantile(percentile_to_retain)
        else:
            self.reduce_formatted_df_to_consistency_score_quantile(percentile_to_retain)

    def reduce_formatted_df_to_consistency_score_quantile(self, percentile_to_retain):
        sorted_df = self.__sort_dataframe_descending_by_consistency_score(self._formated_dataframe_nofilter)
        self.__subset_formated_df_to_top_rows(sorted_df, percentile_to_retain)


    def reduce_formatted_df_to_ml_score_quantile(self, percentile_to_retain):
        sorted_df = self.__sort_by_ml_score()
        self.__subset_formated_df_to_top_rows(sorted_df, percentile_to_retain)


    def __sort_by_ml_score(self):
        df = self.__set_ml_score_values_absolute()
        df = self.__sort_dataframe_ascending_by_ml_score(df)
        return df

    def __subset_formated_df_to_top_rows(self, sorted_df, percentile_to_retain):
        sorted_df = self.__return_top_rows(sorted_df, percentile_to_retain)
        self.formated_dataframe = sorted_df
        self.formated_dataframe = self.__subset_to_relevant_columns()


    @staticmethod
    def __return_top_rows(df, percentile_to_retain):
        return df.iloc[:int(percentile_to_retain*len(df.index))]

    def __sort_dataframe_descending_by_consistency_score(self, df):
        return df.sort_values(by = self.consistencyscore_column, ascending = False).reset_index()

    def __sort_dataframe_ascending_by_ml_score(self, df):
        return df.sort_values(by = self.ml_score_column, ascending = True).reset_index()

    def __set_ml_score_values_absolute(self):
        df = self._formated_dataframe_nofilter
        df[self.ml_score_column] = abs(self._formated_dataframe_nofilter[self.ml_score_column])
        return df


    def __reformat_to_default_dataframe(self, results_df):

        results_df = self.__determine_called_proteins(results_df)
        return results_df

    def __read_input_file(self):
        results_df = pd.read_csv(self._input_file, sep = "\t")
        return results_df

    def __determine_called_proteins(self, results_df):
        results_df[self.called_column] = [x<self.fdr_threshold for x in results_df["fdr"]]
        return results_df

    def __subset_to_relevant_columns(self):
        df = self.formated_dataframe[[self.protein_column, self.called_column]]
        return df


import functools
class MergedResultsTable(ResultsTable):
    def __init__(self, list_of_results_tables):
        self._list_of_results_tables = list_of_results_tables
        self._list_of_result_dataframes = self.__get_list_of_result_dataframes()
        self.protein_column = self.__get_protein_column()
        self.called_column = self.__get_called_column()
        self.species_column = self.__get_species_column()
        self.fdr_threshold = self.__get_fdr_threshold()
        self._merge_column = self.protein_column
        self.formated_dataframe = self.merge_result_tables()

    def __get_protein_column(self):
        return self._list_of_results_tables[0].protein_column

    def __get_called_column(self):
        return self._list_of_results_tables[0].called_column

    def __get_species_column(self):
        return self._list_of_results_tables[0].species_column

    def __get_fdr_threshold(self):
        return self._list_of_results_tables[0].fdr_threshold

    def __get_list_of_result_dataframes(self):
        return [x.formated_dataframe for x in self._list_of_results_tables]

    def merge_result_tables(self):
        #self.__find_and_remove_redundant_columns()
        merged_table = self.__join_prepared_tables()
        merged_table = self.__replace_nans_with_false(merged_table)
        return merged_table

    def __join_prepared_tables(self):
        df_final = functools.reduce(lambda left,right: self.__specify_merge_params(left, right), self._list_of_results_tables)
        return df_final

    def __specify_merge_params(self, left_resultstable, right_resultstable):
        return pd.merge(left_resultstable.formated_dataframe, right_resultstable.formated_dataframe, on=self._merge_column, how = 'outer', suffixes= ("_"+left_resultstable.input_name, "_"+right_resultstable.input_name))


    @staticmethod
    def __replace_nans_with_false(merged_table):
        return merged_table.fillna(value=False)



# Cell

class SpeciesAnnotator():
    def __init__(self, mapping_file, protein_column = 'PG.ProteinGroups', species_colum = 'PG.Organisms'):
        self._mapping_file = mapping_file
        self._protein_column = protein_column
        self._species_column = species_colum
        self._protein_species_mapping_df = self.__load_reduce_mapping_dataframe()

    def annotate_table_with_species(self, results_table):
        species_column = results_table.species_column
        protein_column = results_table.protein_column

        results_df = self.__add_organism_column(results_table.formated_dataframe, species_column, protein_column)
        results_df = self.__filter_non_matching_proteins(results_df, species_column)

        results_table.formated_dataframe = results_df

    def save_protein_species_map(self, outfile):
        self._protein_species_mapping_df.to_csv(outfile, sep = "\t", index = None)


    def __load_reduce_mapping_dataframe(self):
        mapping_df = pd.read_csv(self._mapping_file, sep = "\t", usecols=[self._protein_column, self._species_column], encoding='latin1').drop_duplicates()
        mapping_df = self.__filter_double_mapping_species(mapping_df)
        return mapping_df

    def __filter_double_mapping_species(self, protein2species_df):
        protein2species_df = protein2species_df[[";" not in x for x in protein2species_df[self._species_column]]] #a semicolon seperates different species entries
        return protein2species_df


    def __add_organism_column(self, results_df,species_column, protein_column):
        protein2species_dict = self.__get_protein2species_dict()
        results_df[species_column] = [protein2species_dict.get(x) for x in results_df[protein_column]]
        return results_df

    def __get_protein2species_dict(self):
        protein2species = dict(zip(self._protein_species_mapping_df[self._protein_column], self._protein_species_mapping_df[self._species_column]))
        return protein2species

    @staticmethod
    def __filter_non_matching_proteins(results_df, species_column):
        results_df = results_df[[x is not None for x in results_df[species_column]]]
        return results_df


# Cell
import seaborn as sns
import matplotlib.pyplot as plt

class ClassificationBenchmarker():
    def __init__(self, resultstable):
        self._resultstable = resultstable
        self._protein_column = resultstable.protein_column
        self._species_column = resultstable.species_column
        self.speciescount_table = self.__get_table_counting_detected_proteins_per_species()
        self.variable2falsecountthreshold = self.__calculate_acceptable_number_of_false_calls_per_variable()

    def plot_detected_proteins_per_species(self):
        ax = sns.barplot(data=self.speciescount_table, x = self._species_column, y = "value", hue="variable")
        self.__rotate_x_labels_of_barplot(ax)
        self.__annotate_plot_with_acceptable_false_id_numbers(ax)
        return ax

    def __annotate_plot_with_acceptable_false_id_numbers(self, ax):
        for variable in self.variable2falsecountthreshold:
            self.__annotate_plot_with_acceptable_false_id_for_given_variable(variable, ax)

    def __annotate_plot_with_acceptable_false_id_for_given_variable(self, variable, ax):
        threshold = self.variable2falsecountthreshold.get(variable)
        ax.axhline(threshold)


    def __calculate_acceptable_number_of_false_calls_per_variable(self):
        variables = self.__get_variable_names()
        return self.__get_variable2threshold(variables)

    def __get_variable_names(self):
        return self.speciescount_table["variable"].drop_duplicates()

    def __get_variable2threshold(self, variables):
        variable2threshold = {}
        fdr = self._resultstable.fdr_threshold
        for variable in variables:
            called_proteins = self.__get_number_called_proteins_for_variable(variable)
            variable2threshold[variable] = self.__calculate_acceptable_protein_number(called_proteins, fdr)
        return variable2threshold

    def __get_number_called_proteins_for_variable(self, variable):
        subset_variables = self.speciescount_table.set_index("variable").loc[variable]
        num_proteins = sum(subset_variables["value"])
        return num_proteins

    def __test_get_number_called_proteins_for_variable(self):
        assert self.__get_number_called_proteins_for_variable("called_AlphaQuant") == 1448


    @staticmethod
    def __calculate_acceptable_protein_number(called_proteins, fdr):
        return int(called_proteins *fdr)

    @staticmethod
    def __rotate_x_labels_of_barplot(ax):
        ax.set_xticklabels(ax.get_xticklabels(),rotation=90)

    def __get_table_counting_detected_proteins_per_species(self):
        df_melted = self._resultstable.formated_dataframe.melt(id_vars=[self._protein_column, self._species_column])
        df_grouped = df_melted.groupby([self._species_column, "variable"]).sum().reset_index()
        return df_grouped

    def run_tests(self):
        self.__test_get_number_called_proteins_for_variable()
