

from alphaquant.config.variables import *
import alphabase.quantification.quant_reader.config_dict_loader as abconfigdictloader
import alphaquant.resources.database_loader as aq_resource_dbloader

import alphaquant.config.config as aqconfig
import logging
aqconfig.setup_logging()
LOGGER = logging.getLogger(__name__)
import alphaquant.config.variables as aq_variables
#helper classes

headers_dicts = {'Spectronaut' : {"label_column" : "R.Label", "fg_id_column" : "FG.Id", 'sequence' : "PEP.StrippedSequence", 'proteins' : "PG.UniProtIds", 'precursor_mz' : "FG.PrecMz", "precursor_charge" : "FG.Charge",
                                  "precursor_quantity": "FG.Quantity", "excluded_from_quantification": "F.ExcludedFromQuantification"},
'DIANN' : {"label_column" : "Run", "fg_id_column" : "Precursor.Id", 'sequence' : "Stripped.Sequence",'proteins' :"Protein.Ids", 'precursor_mz' : "Precursor.Mz", "precursor_charge" : "Precursor.Charge"}}

# Cell

import pandas as pd
import dask.dataframe as dd



def assign_dataset_chunkwise(input_file, results_dir, samplemap_df , modification_type = "[Phospho (STY)]", id_thresh = 0.6, excl_thresh =0.2 ,swissprot_file = None,
sequence_file=None, input_type = "Spectronaut", organism = "human"):
    """
    Go through the dataset chunkwise for PTM site mapping.

    The crucial step here is that the dataset needs to be sorted by protein (realized via set_index)
    such that the chunks are independent (different proteins are independent).

    Note: This function performs basic deduplication during preprocessing. The main sophisticated
    deduplication (by peak area for ambiguous PTM localizations) happens later in the pipeline
    after PTM mapping is complete.

    Args:
        input_file (str): Path to input file
        results_dir (str): Directory for results
        samplemap_df (pd.DataFrame): Sample mapping dataframe
        modification_type (str): Type of modification to analyze
        id_thresh (float): Identification threshold for PTM sites
        excl_thresh (float): Exclusion threshold for PTM sites
        swissprot_file (str): Path to SwissProt file (optional)
        sequence_file (str): Path to sequence file (optional)
        input_type (str): Type of input data ("Spectronaut" or "DIANN")
        organism (str): Organism name
    """
    clean_up_previous_processings(results_dir)

    if input_type == 'Spectronaut':
        relevant_cols = get_relevant_cols_spectronaut(modification_type)
        input_df = dd.read_csv(input_file, sep = "\t", dtype='str', blocksize = 100*1024*1024, usecols = relevant_cols)
        input_df = input_df.set_index('PG.ProteinGroups')

    if input_type == 'DIANN':
        relevant_cols = get_relevant_cols_diann(modification_type)
        input_df = dd.read_csv(input_file, sep = "\t", dtype='str', blocksize = 100*1024*1024, usecols = relevant_cols)
        input_df = input_df.set_index('ProteinGroup')

    input_df = input_df.drop_duplicates()
    sorted_reduced_input = f"{input_file}.sorted_reduced.xz"
    if os.path.exists(sorted_reduced_input):
        os.remove(sorted_reduced_input)
    input_df.to_csv(sorted_reduced_input, single_file = True, sep = "\t", compression = 'xz')

    input_df_it = pd.read_csv(sorted_reduced_input, sep = "\t", chunksize = 1000_000, encoding ='latin1')
    for input_df in input_df_it:

        assign_dataset(input_df, id_thresh = id_thresh, excl_thresh =excl_thresh, results_folder = results_dir, samplemap_df = samplemap_df, swissprot_file = swissprot_file, sequence_file=sequence_file, modification_type = modification_type, input_type = input_type,
        organism = organism)




def assign_dataset_inmemory(input_file, results_dir, samplemap_df, modification_type = "[Phospho (STY)]", id_thresh = 0.7, excl_thresh =0.1 ,swissprot_file = None,
sequence_file=None, input_type = "Spectronaut", organism = "human"):
    if input_type == "Spectronaut":
        input_df = read_df_spectronaut_reduce_cols(input_file, modification_type)
    if input_type == "DIANN":
        input_df = read_df_diann_reduce_cols(input_file)

    assign_dataset(input_df, id_thresh = id_thresh, excl_thresh =excl_thresh, results_folder = results_dir, samplemap_df = samplemap_df, swissprot_file = swissprot_file, sequence_file=sequence_file, modification_type = modification_type, input_type = input_type,
        organism = organism)

# Cell


import os
def assign_dataset(input_df, samplemap_df, id_thresh = 0.6, excl_thresh =0.2, results_folder = None, swissprot_file = None,
sequence_file=None, modification_type = "[Phospho (STY)]", input_type = "Spectronaut", organism = "human", header = True):

    """wrapper function reformats Spectronaut inputs tables and iterates through the whole dataset.
    Needed columns:
    "EG.PTMProbabilities {modification_type}"
    "EG.PTMPositions {modification_type}"
    "PEP.StrippedSequence"
    "FG.PrecMz"
    "FG.Charge"

    """""
    print("id_thresh", id_thresh, "excl_thresh", excl_thresh)
    if(id_thresh < 0.5):
        LOGGER.info("id threshold was set below 0.5, which can lead to ambigous ID sites. Setting to 0.51")
        id_thresh = 0.51
    swissprot_file = aq_resource_dbloader.get_swissprot_path(organism)
    sequence_file = aq_resource_dbloader.get_uniprot_path(organism)
    #input_df = pd.read_csv(ptmprob_file, sep = sep).drop_duplicates()
    headers_dict = headers_dicts.get(input_type)
    label_column = headers_dict.get("label_column")
    fg_id_column = headers_dict.get("fg_id_column")
   # sample2cond = dict(zip(samplemap_df["sample"], samplemap_df["condition"]))
    sample2cond = {x : "cond" for x in samplemap_df["sample"]} #we now compare over all conditions.
    len_before = len(input_df.index)
    input_df = filter_input_table(input_type, modification_type, input_df)
    LOGGER.info(f"filtered PTM peptides from {len_before} to {len(input_df.index)}")
    swissprot_ids = set(pd.read_csv(swissprot_file, sep = "\t", usecols = ["Entry"])["Entry"])
    sequence_df = pd.read_csv(sequence_file, sep = "\t", usecols = ["Entry", "Sequence", "Gene Names"])
    sequence_map = dict(zip(sequence_df["Entry"], sequence_df["Sequence"]))
    sequence_df = sequence_df.dropna()

    refgene_map = dict(zip(sequence_df["Entry"], [x.split(" ")[0] for x in sequence_df["Gene Names"]]))

    input_df.loc[:,"REFPROT"] = get_idmap_column(input_df[headers_dict.get("proteins")].astype(str),swissprot_ids)
    input_df.loc[:,"IonID"] = input_df[label_column] + input_df[fg_id_column]
    input_df = input_df.set_index("REFPROT")
    input_df.sort_index(inplace=True)
    #input_df.to_csv(f"{ptmprob_file}.sorted", sep = "\t")
    site_ids = []
    fg_ids = []
    run_ids = []
    prot_ids = []
    gene_ids = []
    ptmlocs = []
    locprobs = []
    siteprobs = []
    stripped_seqs = []
    prec_mz = []
    fg_charge = []
    ptm_id = []
    ion_id = []
    precursor_quantities = []



    num_proteins = len(input_df.index.unique())
    num_mapped = 0
    for idx, prot in enumerate(input_df.index.unique()):#input_df["REFPROT"].unique():

        if idx %100 == 0:
            LOGGER.info(f"processing {idx} of {num_proteins} ({(idx/num_proteins):.2f}) proteins for ptmsite mapping")

        #filtvec = [prot in x for x in input_df["REFPROT"]]

        protein_df = input_df.loc[[prot]].copy()#input_df[filtvec].copy()
        protein_df = protein_df.reset_index()

        sequence = sequence_map.get(prot)
        if sequence == None:
            continue
        num_mapped+=1
        gene = refgene_map.get(prot)

        modpeps_per_sample = [ModifiedPeptide(input_type,protein_df.loc[x],sequence, modification_type) for x in protein_df.index]
        merged_siteprobs = get_site_prob_overview(modpeps_per_sample, prot, gene)
        siteprobs.extend(merged_siteprobs)
        modpeps, condid2ionids = merge_samecond_modpeps(modpeps_per_sample, sample2cond, id_thresh, excl_thresh) #all ions coming from the same condition are merged
        ionid2ptmid = assign_ptm_locations(modpeps, condid2ionids,id_thresh)##after clustering, conditions are mapped back to the original run

        ptm_ids_prot = [ionid2ptmid.get(x) for x in protein_df["IonID"]]

        ptmlocs.extend([x for x in protein_df[get_ptmpos_header(input_type, modification_type)]])
        locprobs.extend([x for x in protein_df[get_ptmprob_header(input_type, modification_type)]])
        site_ids.extend(ptm_ids_prot)
        fg_ids.extend(protein_df[fg_id_column].tolist())
        ion_id.extend([f"{fg}_{site_num}" for fg, site_num in zip(protein_df[fg_id_column].tolist(), ptm_ids_prot)])
        run_ids.extend(protein_df[label_column].tolist())
        prot_ids.extend([prot for x in range(len(ptm_ids_prot))])
        gene_ids.extend([gene for x in range(len(ptm_ids_prot))])
        stripped_seqs.extend(protein_df[headers_dict.get("sequence")])
        prec_mz.extend(protein_df[headers_dict.get("precursor_mz")])
        fg_charge.extend(protein_df[headers_dict.get("precursor_charge")])
        precursor_quantities.extend(protein_df[headers_dict.get("precursor_quantity")])
        ptm_id.extend([f"{gene}_{prot}_{ionid2ptmid.get(x)}" for x in protein_df["IonID"]])

    LOGGER.info(f"{num_mapped} of {num_proteins} could be mapped")
    if num_mapped/num_proteins < 0.7:
        LOGGER.warning(f"Fewer proteins than expected could be mapped to sequence. Ensure that the organism is specified correctly.")

    conditions = [sample2cond.get(x) for x in run_ids]

    mapped_df = pd.DataFrame({label_column : run_ids, "conditions" : conditions, fg_id_column : fg_ids, "REFPROT" : prot_ids, "gene" : gene_ids,"site" : site_ids, "ptmlocs":ptmlocs ,
    "locprob" : locprobs, "PEP.StrippedSequence" : stripped_seqs, "FG.PrecMz" : prec_mz, "FG.Charge": fg_charge, "FG.Quantity": precursor_quantities, "FG.Id.ptm" : ion_id, "ptm_id" : ptm_id})


    siteprob_df = pd.DataFrame(siteprobs)
    siteprob_df = siteprob_df.astype({"site" : "int"})
    siteprob_df.set_index(["REFPROT", "site"], inplace=True)
    siteprob_df = siteprob_df.sort_index().reset_index()

    if results_folder != None:
        os.makedirs(results_folder, exist_ok=True)
        LOGGER.info(f"Writing ptm_ids.tsv and siteprobs.tsv to {results_folder}")
        mapped_df.to_csv(os.path.join(results_folder, "ptm_ids.tsv"), sep = "\t", index = None)
        siteprob_df.to_csv(os.path.join(results_folder, "siteprobs.tsv"), sep = "\t", index = None)

    return mapped_df, siteprob_df


def assign_ptm_locations(modpeps,condid2ionids, id_thresh):
    """go through ions of a given protein, cluster if necessary and map each ion to a ptm_site ID"""
    id2groupid = {}

    if len(modpeps) == 1:
        grouped_ions = [modpeps]
    else:
        grouped_ions = cluster_ions(modpeps)

    for iongroup in grouped_ions:
        idxs_most_likely, idxs_confident = get_most_likely_sites(iongroup, id_thresh)
        positions_ids = get_AA_positions(iongroup, idxs_most_likely, idxs_confident)
        positions_ids_w_aa = add_AA_ids_to_positions(positions_ids, iongroup)

        #positions = np.sort(positions)
        all_ions = sum([condid2ionids.get(x.id) for x in iongroup], [])#the condition-level merged ions are mapped back to the existin ion-level IDs
        id2groupid.update({x:positions_ids_w_aa for x in all_ions})
    return id2groupid

def get_most_likely_sites(iongroup, id_thresh):
    summed_probs = np.sum([x.probabilities for x in iongroup], axis = 0)
    max_probs = np.max([x.probabilities for x in iongroup], axis = 0)
    num_sites = iongroup[0].num_sites

    idxs_most_likely = np.argpartition(summed_probs, -num_sites)[-num_sites:] #get the indices of the most likely sites
    idxs_most_likely = np.sort(idxs_most_likely)
    idxs_confident = set(np.where(max_probs>=id_thresh)[0]) #check which sites are above the confidence threshold
    return idxs_most_likely, idxs_confident


def get_AA_positions(iongroup, idxs_most_likely, idxs_confident):
    positions = list(iongroup[0].positions)
    positions_final = []
    for idx in idxs_most_likely:
        if idx in idxs_confident:
            positions_final.append(positions[idx])
        else:
            positions_final.append(np.nan)#set those sites that are not confident enough to np.nan
    return positions_final


def add_AA_ids_to_positions(position_ids, iongroup):
    position_ids_w_aa = []
    pepseq = iongroup[0].seq
    start_idx = iongroup[0].start_idx
    position_ids_normed = [x-start_idx-1 for x in position_ids]

    for idx in range(len(position_ids_normed)):
        position_id = position_ids[idx]
        position_id_normed = position_ids_normed[idx]
        if np.isnan(position_id):
            position_ids_w_aa.append(np.nan)
        else:
            aa_id = pepseq[position_id_normed]
            position_id_w_aa = f"{aa_id}{position_id}"
            position_ids_w_aa.append(position_id_w_aa)

    return position_ids_w_aa


# Cell
import numpy as np
class ModifiedPeptide():
    """
    helper class for convenient access of modified peptide variables
    """
    def __init__(self, input_type, df_line, protein_sequence, modification_type):
        if input_type == "Spectronaut":
            self.init_spectronaut(df_line, protein_sequence,modification_type)
        if input_type == "DIANN":
            self.init_diann(df_line, protein_sequence, modification_type)

    def init_spectronaut(self, df_line, protein_sequence, modification_type ):
        self.id = df_line["IonID"]
        self.ionname = df_line["FG.Id"]
        self.sample = df_line["R.Label"]
        self.seq = df_line["PEP.StrippedSequence"]
        self.prot = df_line["PG.UniProtIds"]
        self.start_idx = protein_sequence.find(self.seq)
        positions_parsed = np.array(df_line[f"EG.PTMPositions {modification_type}"].split(";")).astype("int")
        probabilities_parsed =  np.array(df_line[f"EG.PTMProbabilities {modification_type}"].split(";")).astype("float")
        self.positions = scale_site_idxs_to_protein(protein_sequence, self.seq, positions_parsed)
        self.num_sites = get_num_sites(probabilities_parsed)
        self.probabilities = probabilities_parsed
        self.encoded_probs = None#encode_probabilities(probabilities_parsed, id_thresh, excl_thresh)

    def init_diann(self, df_line, protein_sequence, modification_type):
        self.id = df_line["IonID"]
        self.ionname = df_line["Precursor.Id"]
        self.sample = df_line["Run"]
        self.seq = df_line["Stripped.Sequence"]
        self.prot = df_line["Protein.Ids"]
        self.start_idx = protein_sequence.find(self.seq)
        modified_sequence = df_line["Modified.Sequence"]
        positions_parsed = retrieve_relative_positions_diann(modification_type, modified_sequence)#digly mod: "(UniMod:121)"
        probabilities_parsed =  retrieve_probabilities_diann(df_line["PTM.Site.Confidence"])
        self.positions = scale_site_idxs_to_protein(protein_sequence, self.seq, positions_parsed)
        self.num_sites = get_num_sites(probabilities_parsed)
        self.probabilities = probabilities_parsed
        self.encoded_probs = None


# Helper Functions

## Group ions and reduce redundancies



import copy
def merge_samecond_modpeps(ions, sample2cond, id_thresh, excl_thresh):
    """
    identical ions from the same condition are merged and their site localization probabilities are averaged
    """
    res = []
    condid2ionids = {}

    condion2modpeps = {}
    for ion in ions:
        condid = f"{sample2cond.get(ion.sample)}{ion.ionname}"
        condion2modpeps[condid] = condion2modpeps.get(condid, []) + [ion]
        condid2ionids[condid] = condid2ionids.get(condid, []) + [ion.id]

    for condid,modpeps in condion2modpeps.items():
        modpep_selected = copy.deepcopy(modpeps[0])
        allprobs = [x.probabilities for x in modpeps]
        meanprobs = np.mean(allprobs, axis = 0)
        modpep_selected.id = condid
        modpep_selected.probabilities = meanprobs
        modpep_selected.encoded_probs = encode_probabilities(meanprobs, id_thresh, excl_thresh)
        res.append(modpep_selected)
    return res, condid2ionids

# Cell
def scale_site_idxs_to_protein(protseq, pepseq, localization_array):
    """align peptide sequence along protein, express idxs relative to start"""
    start_idx = protseq.find(pepseq)
    localization_array = localization_array + start_idx
    return localization_array

# Cell
def get_num_sites(probabilities_parsed):
    return round(sum(probabilities_parsed))


# Cell
def group_by_nummods_posv(ions):
    """ions with identical position vector and number of modifications are grouped together"""
    nmod2ions = {}
    for ion in ions:
        nmodposv = f"{ion.num_sites}_{ion.positions}"
        nmod2ions[nmodposv] = nmod2ions.get(nmodposv, []) + [ion]
    return list(nmod2ions.values())

# Cell
def condense_ions(ions):
    """
    group ions together, which have identical sequence and encoded probabilities. This way you only need to
    compare these in the distance matrix
    """
    key2equivions = {}
    for ion in ions:
        key = f"{ion.seq}_{ion.encoded_probs}"
        key2equivions[key] = key2equivions.get(key, []) + [ion]
    ion2equiv_ions = {gr_ions[0] : gr_ions for gr_ions in key2equivions.values()}
    representative_ions = list(ion2equiv_ions.keys())
    return representative_ions, ion2equiv_ions

# Cell
def encode_probabilities(probabilties_parsed, id_thresh, excl_thresh):
    prob_copy = probabilties_parsed.copy()
    prob_copy[prob_copy>id_thresh] = 5
    prob_copy[prob_copy < excl_thresh] = 3
    prob_copy[(prob_copy!=3) & (prob_copy!=5)] = 0

    return prob_copy.astype('int')


# Cell
import re
import numpy as np
def retrieve_relative_positions_diann(modification,modified_sequence):
    return np.array([m.start() for m in re.finditer(modification, modified_sequence)])

def retrieve_probabilities_diann(localisation_probability):
    if not np.isscalar(localisation_probability):
        raise ValueError(f"The case of localisation probability {localisation_probability} in type {type(localisation_probability)} is not yet implemented for DIANN type input!")
    return np.array([localisation_probability])

## Compare and cluster ions

def cluster_ions(ions):
    res = []
    nmod_posv_grouped = group_by_nummods_posv(ions)
    for candidates in nmod_posv_grouped:
        if len(candidates)==1: #check if only one ion, then no pairwise comparison needed
            res.extend([candidates])
            continue

        representative_ions, ion2equiv_ions = condense_ions(candidates)
        if len(representative_ions)==1:#check if only one condensed ion, then also no pairwise comparison needed
            equiv_ions = ion2equiv_ions.get(representative_ions[0])
            res.extend([equiv_ions])
            continue

        ionclustered = cluster_ions_pairwise(representative_ions) #if multiple ions to compare, do pairwise comparisons
        for cluster in ionclustered:
            clust_copy = cluster.copy()
            for ion in clust_copy:
                equiv_ions = ion2equiv_ions.get(ion)
                if len(equiv_ions)>1:
                    cluster.extend(equiv_ions)
        res.extend(ionclustered)

    return res

# Cell

import scipy.cluster.hierarchy as hierarchy

def cluster_ions_pairwise(ions):
    """form complete linkage clusters (every ion is a neighbor to every ion in the cluster) for a given set of ions. Distance matrix define in 'compare ion similarities'"""
    ions.sort(key = lambda x : len(x.seq),reverse = True)
    condensed_distance_matrix = compare_ion_similarities(ions)
    after_clust = hierarchy.complete(condensed_distance_matrix)
    clustered = hierarchy.fcluster(after_clust, 0.1, criterion='distance')
    clust2ions = {}
    for i in range(len(clustered)):
       clustions = clust2ions.get(clustered[i],list())
       clustions.append(ions[i])
       clust2ions[clustered[i]] = clustions

    return list(clust2ions.values())

# Cell

def compare_ion_similarities(ions):
    """returns a condensed distance matrix for a given set of ions. Distances are calculated based on the encoded site localization probabilities, as described below"""
    seqs = np.array([x.seq for x in ions])
    encoded = np.array([x.encoded_probs for x in ions])
    distances = get_condensed_matrix(seqs, encoded)

    return distances


# Cell
def get_condensed_matrix(seqs, encoded):
    """checks pairwise occpancy vectors based on the following encoding: 3 == clearly not occupied, 5 == clearly occupied.
    If a sum=vec1+vec2 contains 3+5=8, this means it is dissimilar and is assigned distance = 1, distance =0 otherwise
    """
    res = np.zeros(int(len(seqs) * (len(seqs)-1)/2))
    count = 0
    for i in range(len(seqs)):
        for j in range(i+1, len(seqs)):
            seq1 = seqs[i]
            seq2 = seqs[j]
            if seq2 in seq1:
                encode1 = encoded[i]
                encode2 = encoded[j]
                summed = encode1 + encode2
                if 8 in summed:
                    res[count] = 1
            count+=1
    return res

## Read and reformat input files
import pandas as pd

def read_df_spectronaut_reduce_cols(input_file, modification_type):
    relevant_cols = get_relevant_cols_spectronaut(modification_type)
    input_df = read_df_reduce_cols(input_file, relevant_cols)
    return input_df

def read_df_diann_reduce_cols(input_file):
    relevant_cols = get_relevant_cols_diann()
    input_df = read_df_reduce_cols(input_file, relevant_cols)
    return input_df

def read_df_reduce_cols(input_file, relevant_cols):
    input_df_it = pd.read_csv(input_file, sep = "\t", usecols = relevant_cols, encoding ='latin1', chunksize=1000000)
    input_df_list = []
    for input_df_subset in input_df_it:
        input_df_subset = input_df_subset.drop_duplicates()
        input_df_list.append(input_df_subset)
    input_df = pd.concat(input_df_list)
    return input_df

def get_relevant_cols_spectronaut(modification_type):
    relevant_cols = list(headers_dicts.get('Spectronaut').values())
    relevant_cols = relevant_cols  + [f"EG.PTMPositions {modification_type}", f"EG.PTMProbabilities {modification_type}"]
    return relevant_cols

def get_relevant_cols_diann():
    relevant_cols = list(headers_dicts.get('DIANN').values())
    relevant_cols = relevant_cols  + ["Modified.Sequence", "PTM.Site.Confidence"]
    return relevant_cols

# Cell
def get_idmap_column(protgroups, swissprots):
    """go through protein groups and map to swissprot ID if possible"""
    res = []
    for protgroup in protgroups:
        mapped = False
        proteins = list(protgroup.split(";"))
        for protein in proteins:
            if protein in swissprots:
                res.append(protein)
                mapped = True
                break
        if not mapped:
            res.append(proteins[0])
    return res

# Cell
import pandas as pd
def get_site_prob_overview(modpeps, refprot, refgene):
    """reformats the modified peptide objects for a given protein. The returned series objects contain the mean probabilities for a given site and experimental sample"""
    site2sample2probs = {}
    for modpep in modpeps:
        for idx in range(len(modpep.positions)):
            site = modpep.positions[idx]
            prob = modpep.probabilities[idx]
            sample = modpep.sample
            site2sample2probs[site] = site2sample2probs.get(site, {}) #.update({sample:[]})
            site2sample2probs.get(site)[sample] = site2sample2probs.get(site).get(sample, []) + [prob]

    series_collected = []
    for site in site2sample2probs.keys():
        sample2probs = site2sample2probs.get(site)
        header = list(sample2probs.keys())
        probs = [np.mean(sample2probs.get(x)) for x in header]
        # site_series = pd.Series(probs, index=header)
        # site_series = site_series.append(pd.Series([int(site)], index=["site"]))
        # site_series = site_series.append(pd.Series(refprot, index= ["REFPROT"]))
        # site_series = site_series.append(pd.Series(refgene, index= ["gene"]))

        site_series_idxs = header + ["site"] + ["REFPROT"] + ["gene"]
        site_series_values = probs + [int(site)] + [refprot] + [refgene]
        site_series = pd.Series(site_series_values, index = site_series_idxs)
        series_collected.append(site_series)

    return series_collected

# Cell
def add_ptmsite_infos_spectronaut(input_df, ptm_ids_df):
    intersect_columns = input_df.columns.intersection(ptm_ids_df.columns)
    if(len(intersect_columns)==2):
        LOGGER.info(f"assigning ptms based on columns {intersect_columns}")
        input_df = input_df.merge(ptm_ids_df, on=list(intersect_columns), how= 'left')
    else:
        raise Exception(f"Number of intersecting columns {intersect_columns} not as expected")
    input_df = add_ptm_precursor_names_spectronaut(input_df)
    input_df = input_df[~input_df["conditions"].isna()]
    return input_df

# Cell
def add_ptm_precursor_names_spectronaut(ptm_annotated_input):
    delimiter = pd.Series(["_" for x in range(len(ptm_annotated_input.index))])
    ptm_annotated_input[QUANT_ID] = ptm_annotated_input["PEP.StrippedSequence"] + delimiter + ptm_annotated_input["FG.PrecMz"].astype('str') + delimiter + ptm_annotated_input["FG.Charge"].astype('str') + delimiter + ptm_annotated_input["REFPROT"] + delimiter +ptm_annotated_input["site"].astype('str')
    ptm_annotated_input.gene.fillna('', inplace=True)
    ptm_annotated_input["site_id"] = ptm_annotated_input["gene"].astype('str')+delimiter+ptm_annotated_input["REFPROT"].astype('str') + delimiter +ptm_annotated_input["site"].astype('str')
    return ptm_annotated_input

# Cell
def filter_input_table(input_type, modification_type,input_df):
    if input_type == "Spectronaut":
        return input_df[~input_df[f"EG.PTMProbabilities {modification_type}"].isna()]
    if input_type == "DIANN":
        return input_df[[(modification_type in x) for x in input_df["Modified.Sequence"]]]

# Cell


# Cell

def get_ptmpos_header(input_type, modification_type):
    if input_type == 'Spectronaut':
        return f"EG.PTMPositions {modification_type}"
    if input_type == 'DIANN':
        return "Modified.Sequence"

# Cell

def get_ptmprob_header(input_type, modification_type):
    if input_type == 'Spectronaut':
        return f"EG.PTMProbabilities {modification_type}"
    if input_type == 'DIANN':
        return "PTM.Site.Confidence"

# Cell
import pathlib
import os


# Workflow
## Assign all ions for a given protein

import pandas as pd
import numpy as np


## Iterate through dataset

# Cell

def clean_up_previous_processings(results_folder):
    file_ptm_ids = os.path.join(results_folder, "ptm_ids.tsv")
    file_siteprobs = os.path.join(results_folder, "siteprobs.tsv")

    if os.path.exists(file_ptm_ids):
        os.remove(file_ptm_ids)
    if os.path.exists(file_siteprobs):
        os.remove(file_siteprobs)



## Create ptm mapped input tables

import numpy as np
import alphaquant.diffquant.diffutils as aqutils
import os

def merge_ptmsite_mappings_write_table(spectronaut_file, mapped_df, modification_type, input_type_to_use = "spectronaut_ptm_fragion", chunksize = 100_000):
    """
    Merge PTM site mappings with the original spectronaut file and write the result.

    For Spectronaut data, applies sophisticated deduplication by keeping the row with
    maximum F.PeakArea per group defined by key columns. This resolves ambiguous PTM
    site localizations by selecting the most reliable measurement.

    Args:
        spectronaut_file (str): Path to the original spectronaut file
        mapped_df (pd.DataFrame): DataFrame with PTM site mappings
        modification_type (str): Type of modification (e.g., "[Phospho (STY)]")
        input_type_to_use (str): Input type configuration to use
        chunksize (int): Size of chunks for processing large files

    Returns:
        str: Path to the created PTM-mapped file
    """
    config_dict = abconfigdictloader.import_config_dict()
    config_dict_ptm = config_dict.get(input_type_to_use)
    relevant_columns = abconfigdictloader.get_relevant_columns_config_dict(config_dict_ptm)#the columns that will be relevant in the ptm table
    relevant_columns_spectronaut = list(set(relevant_columns).intersection(set(pd.read_csv(spectronaut_file, sep = "\t", nrows=2).columns)))# the relevant columsn in the spectronaut table ()
    relevant_columns_spectronaut = relevant_columns_spectronaut+["EG.ModifiedSequence"] + ["FG.Quantity"]
    ptmmapped_table_filename = get_ptmmapped_filename(spectronaut_file)
    lines_read = 0

    labelid2ptmid, labelid2site = get_ptmid_mappings(mapped_df) #get precursor+experiment to site mappings
    specnaut_df_it = pd.read_csv(spectronaut_file, sep = "\t", chunksize=chunksize, usecols=relevant_columns_spectronaut)

    LOGGER.info(f"adding ptm info to spectronaut file")

    if os.path.exists(ptmmapped_table_filename):
        os.remove(ptmmapped_table_filename)

    # Determine if we should apply deduplication (only for Spectronaut)
    is_spectronaut = "spectronaut" in input_type_to_use.lower()

    if is_spectronaut:
        # Collect all chunks for batch deduplication
        LOGGER.info("Collecting chunks for PTM deduplication (Spectronaut data)")
        all_chunks = []

        for specnaut_df in specnaut_df_it:
            specnaut_df_annot = add_ptmsite_info_to_subtable(specnaut_df, labelid2ptmid, labelid2site, modification_type, relevant_columns)
            all_chunks.append(specnaut_df_annot)
            lines_read += chunksize
            LOGGER.info(f"{lines_read} lines read")

        # Combine all chunks and apply sophisticated deduplication
        LOGGER.info("Combining chunks for PTM deduplication...")
        combined_df = pd.concat(all_chunks, ignore_index=True)

        # Apply sophisticated deduplication for Spectronaut
        deduplicated_df = deduplicate_spectronaut_ptm_by_peak_area(combined_df)

        # Write deduplicated result
        LOGGER.info(f"Writing deduplicated PTM table with {len(deduplicated_df)} rows to {ptmmapped_table_filename}")
        deduplicated_df.to_csv(ptmmapped_table_filename, sep='\t', index=False)

    else:
        # Write chunks directly for non-Spectronaut data (DIANN, etc.)
        LOGGER.info("Processing non-Spectronaut data - no deduplication applied")
        header = True

        for specnaut_df in specnaut_df_it:
            specnaut_df_annot = add_ptmsite_info_to_subtable(specnaut_df, labelid2ptmid, labelid2site, modification_type, relevant_columns)
            aqutils.write_chunk_to_file(specnaut_df_annot, ptmmapped_table_filename, header)
            header = False
            lines_read += chunksize
            LOGGER.info(f"{lines_read} lines read")

    return ptmmapped_table_filename

def deduplicate_spectronaut_ptm_by_peak_area(df):
    """
    Deduplicate Spectronaut PTM data by keeping the row with maximum peak area per group.

    This addresses ambiguous PTM site localizations where the same fragment ion
    can be assigned to different phosphorylation sites. We keep the measurement
    with the highest signal intensity (F.PeakArea) as the most reliable.

    Args:
        df (pd.DataFrame): PTM-mapped Spectronaut dataframe

    Returns:
        pd.DataFrame: Deduplicated dataframe
    """
    if len(df) == 0:
        return df

    # Key columns that define duplicate groups for Spectronaut data
    key_columns = [
        'PEP.StrippedSequence',   # Peptide sequence
        'FG.Charge',              # Precursor charge
        'F.FrgIon',               # Fragment ion type
        'F.FrgLossType',          # Fragment loss type
        'F.Charge',               # Fragment charge
        'ptm_mapped_modseq',      # PTM-mapped modified sequence
        'R.Label'                 # Sample/run label
    ]
    intensity_column = 'F.PeakArea'

    # Convert intensity column to numeric and remove NaN values
    df = df.copy()
    df[intensity_column] = pd.to_numeric(df[intensity_column], errors='coerce')
    df = df.dropna(subset=[intensity_column])

    if len(df) == 0:
        return df

    # Group by key columns and keep row with maximum peak area per group
    max_intensity_indices = df.groupby(key_columns)[intensity_column].idxmax()
    deduplicated_df = df.loc[max_intensity_indices].reset_index(drop=True)

    rows_removed = len(df) - len(deduplicated_df)
    if rows_removed > 0:
        LOGGER.info(f"PTM deduplication: Removed {rows_removed} duplicate rows, kept {len(deduplicated_df)} rows")

    return deduplicated_df

def get_ptmmapped_filename(spectronaut_file):
    spectronaut_file_abspath = os.path.abspath(spectronaut_file)
    foldername = os.path.dirname(spectronaut_file_abspath)
    filename = os.path.basename(spectronaut_file_abspath)
    filename_reduced = filename.replace(".tsv", "")
    return f"{foldername}/{filename_reduced}.ptmsite_mapped.tsv" #this file is not written to the progress folder



def add_ptmsite_info_to_subtable(spectronaut_df, labelid2ptmid, labelid2site, modification_type, relevant_columns):

    spectronaut_df["labelid"] = spectronaut_df["R.Label"].astype('str').to_numpy() + spectronaut_df["FG.Id"].astype('str').to_numpy() #derive the id to map from Spectronaut
    spectronaut_df = spectronaut_df[[x in labelid2ptmid.keys() for x in spectronaut_df["labelid"]]].copy() #drop peptides that have no ptm

    spectronaut_df["ptm_id"] = np.array([labelid2ptmid.get(x) for x in spectronaut_df["labelid"]]) #add the ptm_id row to the spectronaut table
    modseq_typereplaced = np.array([str(x.replace(modification_type, "")) for x in spectronaut_df["EG.ModifiedSequence"]]) #EG.ModifiedSequence already determines a localization of the modification type. Replace all localizations and add the new localizations below
    sites = np.array([str(labelid2site.get(x)) for x in spectronaut_df["labelid"]])
    spectronaut_df["ptm_mapped_modseq"] = np.char.add(modseq_typereplaced, sites)

    return spectronaut_df


def get_ptmid_mappings(mapped_df):
    labelid = mapped_df["R.Label"].astype('str').to_numpy() + mapped_df["FG.Id"].astype('str').to_numpy()
    ptm_ids = mapped_df["ptm_id"].to_numpy()
    site = mapped_df["site"].to_numpy()
    labelid2ptmid = dict(zip(labelid, ptm_ids))
    labelid2site = dict(zip(labelid, site))
    return labelid2ptmid, labelid2site




# Detect Changes in site occupancy

import pandas as pd
import numpy as np


def initialize_ptmsite_df(ptmsite_file, samplemap_file):
    """returns ptmsite_df, samplemap_df from files"""
    samplemap_df, _ = initialize_sample2cond(samplemap_file)
    ptmsite_df = pd.read_csv(ptmsite_file, sep = "\t")
    return ptmsite_df, samplemap_df

def detect_site_occupancy_change(cond1, cond2, ptmsite_df ,samplemap_df, min_valid_values = 2, threshold_prob = 0.05):
    """
    uses a PTMsite df with headers "REFPROT", "gene","site", and headers for sample1, sample2, etc and determines
    whether a site appears/dissappears between conditions based on some probability threshold
    """

    ptmsite_df["site_id"] = ptmsite_df["REFPROT"] + ptmsite_df["site"].astype("str")
    ptmsite_df = ptmsite_df.set_index("site_id")
    cond1_samples = list(set(samplemap_df[(samplemap_df["condition"]==cond1)]["sample"]).intersection(set(ptmsite_df.columns)))
    cond2_samples = list(set(samplemap_df[(samplemap_df["condition"]==cond2)]["sample"]).intersection(set(ptmsite_df.columns)))

    ptmsite_df = ptmsite_df[cond1_samples + cond2_samples + ["REFPROT", "gene", "site"]]
    filtvec = [(sum(~np.isnan(x))>0) for _, x in ptmsite_df[cond1_samples + cond2_samples].iterrows()]
    ptmsite_df = ptmsite_df[filtvec]
    ptmsite_df = ptmsite_df.sort_index()

    regulated_sites = []
    count = 0
    for ptmsite in ptmsite_df.index.unique():

        site_df = ptmsite_df.loc[[ptmsite]]
        if count%1000 ==0:
            num_checks = len(ptmsite_df.index.unique())
            LOGGER.info(f"{count} of {num_checks} {count/num_checks :.2f}")
        count+=1

        cond1_vals = site_df[cond1_samples].to_numpy()
        cond2_vals = site_df[cond2_samples].to_numpy()

        cond1_vals = cond1_vals[~np.isnan(cond1_vals)]
        cond2_vals = cond2_vals[~np.isnan(cond2_vals)]

        numrep_c1 = len(cond1_vals)
        numrep_c2 = len(cond2_vals)

        if(numrep_c1<min_valid_values) | (numrep_c2 < min_valid_values):
            continue

        cond1_prob = np.mean(cond1_vals)
        cond2_prob = np.mean(cond2_vals)

        unlikely_c1 = cond1_prob<threshold_prob
        unlikely_c2 = cond2_prob<threshold_prob
        likely_c1 = cond1_prob>1-threshold_prob
        likely_c2 = cond2_prob>1-threshold_prob
        direction = 0

        if(unlikely_c1&likely_c2):
            direction = -1
        if(unlikely_c2&likely_c1):
            direction = 1

        if direction!=0:
            LOGGER.info("occpancy change detected")
            refprot = site_df["REFPROT"].values[0]
            gene = site_df["gene"].values[0]
            site = site_df["site"].values[0]
            regulated_sites.append([refprot, gene, site, direction, cond1_prob, cond2_prob, numrep_c1, numrep_c2])


    df_occupancy_change = pd.DataFrame(regulated_sites, columns=["REFPROT", "gene", "site", "direction", "c1_meanprob", "c2_meanprob", "c1_nrep", "c2_nrep"])
    return df_occupancy_change





