import os
import pathlib
from ..config.variables import QUANT_ID
import importlib.metadata


if "__file__" in globals():#only run in the translated python file, as __file__ is not defined with ipython
    INTABLE_CONFIG = os.path.join(pathlib.Path(__file__).parent.absolute(), "configs", "intable_config.yaml") #the yaml config is located one directory below the python library files

import alphaquant.config.config as aqconfig
import logging
aqconfig.setup_logging()
LOGGER = logging.getLogger(__name__)

# Cell

def get_samples_used_from_samplemap_file(samplemap_file, cond1, cond2):
    samplemap_df = load_samplemap(samplemap_file)
    return get_samples_used_from_samplemap_df(samplemap_df, cond1, cond2)

import pandas as pd

def load_samplemap(samplemap_file):
    file_ext = os.path.splitext(samplemap_file)[-1]
    if file_ext=='.csv':
        sep=','
    if (file_ext=='.tsv') | (file_ext=='.txt'):
        sep='\t'

    if 'sep' not in locals():
        LOGGER.info(f"neither of the file extensions (.tsv, .csv, .txt) detected for file {samplemap_file}! Trying with tab separation. In the case that it fails, please add the appropriate extension to your file name.")
        sep = "\t"

    return pd.read_csv(samplemap_file, sep = sep, encoding ='latin1', dtype='str')

# Cell
def prepare_loaded_tables(data_df, samplemap_df):
    """
    Integrates information from the peptide/ion data and the samplemap, selects the relevant columns and log2 transforms intensities.
    """
    samplemap_df = samplemap_df[samplemap_df["condition"]!=""] #remove rows that have no condition entry
    filtvec_not_in_data = [(x in data_df.columns) for x in samplemap_df["sample"]] #remove samples that are not in the dataframe
    samplemap_df = samplemap_df[filtvec_not_in_data]
    headers = ['protein'] + samplemap_df["sample"].to_list()
    data_df = data_df.set_index(QUANT_ID)
    for sample in samplemap_df["sample"]:
        data_df[sample] = np.log2(data_df[sample].replace(0, np.nan))
    return data_df[headers], samplemap_df



def get_samples_used_from_samplemap_df(samplemap_df, cond1, cond2):
    samples_c1 = samplemap_df[[cond1 == x for x in samplemap_df["condition"]]]["sample"] #subset the df to the condition
    samples_c2 = samplemap_df[[cond2 == x for x in samplemap_df["condition"]]]["sample"]
    return list(samples_c1), list(samples_c2)

def get_all_samples_from_samplemap_df(samplemap_df):
    return list(samplemap_df["sample"])

# Cell
import pandas as pd

def get_samplenames_from_input_df(data):
    """extracts the names of the samples of the AQ input dataframe"""
    names = list(data.columns)
    names.remove('protein')
    names.remove(QUANT_ID)
    return names

# Cell
import numpy as np
def filter_df_to_min_valid_values(quant_df_wideformat, samples_c1, samples_c2, min_valid_values):
    """filters dataframe in alphaquant format such that each column has a minimum number of replicates
    """
    quant_df_wideformat = quant_df_wideformat.replace(0, np.nan)
    df_c1_min_valid_values = quant_df_wideformat[samples_c1].dropna(thresh = min_valid_values, axis = 0)
    df_c2_min_valid_values = quant_df_wideformat[samples_c2].dropna(thresh = min_valid_values, axis = 0)
    idxs_both = df_c1_min_valid_values.index.intersection(df_c2_min_valid_values.index)
    quant_df_reduced = quant_df_wideformat.iloc[idxs_both].reset_index()
    return quant_df_reduced


# Cell
def get_condpairname(condpair):
    return f"{condpair[0]}_VS_{condpair[1]}"

# Cell

def get_quality_score_column(acquisition_info_df):
    if "FG.ShapeQualityScore" in acquisition_info_df.columns:
        param = "FG.ShapeQualityScore"
    elif "Quantity.Quality" in acquisition_info_df.columns:
        param = "Quantity.Quality"
    return param

# Cell
import os

def make_dir_w_existcheck(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

# Cell
import os
def get_results_plot_dir_condpair(results_dir, condpair):
    results_dir_plots = f"{results_dir}/{condpair}_plots"
    make_dir_w_existcheck(results_dir_plots)
    return results_dir_plots

# Cell
def get_middle_elem(sorted_list):
    nvals = len(sorted_list)
    if nvals==1:
        return sorted_list[0]
    middle_idx = nvals//2
    if nvals%2==1:
        return sorted_list[middle_idx]
    return 0.5* (sorted_list[middle_idx] + sorted_list[middle_idx-1])

# Cell
import numpy as np
def get_nonna_array(array_w_nas):
    res = []
    isnan_arr = np.isnan(array_w_nas)

    for idx in range(len(array_w_nas)):
        sub_res = []
        sub_array = array_w_nas[idx]
        na_array = isnan_arr[idx]
        for idx2 in range(len(sub_array)):
            if not na_array[idx2]:
               sub_res.append(sub_array[idx2])
        res.append(np.array(sub_res))
    return np.array(res)

# Cell
import numpy as np
def get_non_nas_from_pd_df(df):
    return {
        pep_name: sub_vals[~np.isnan(sub_vals)] for pep_name, sub_vals in
        zip( df.index.values, df.values)
    }

# Cell
import numpy as np
def get_ionints_from_pd_df(df):
    return {
        pep_name: sub_vals for pep_name, sub_vals in
        zip( df.index.values, df.values)
    }

# Cell
def invert_dictionary(my_map):
    inv_map = {}
    for k, v in my_map.items():
        inv_map[v] = inv_map.get(v, []) + [k]
    return inv_map

from collections import defaultdict
def invert_tuple_list_w_nonunique_values(tuple_list):
    inverted_dict = defaultdict(list)
    for key, value in tuple_list:
        inverted_dict[value].append(key)
    return inverted_dict


# Cell
import statistics

def get_z_from_p_empirical(p_emp,p2z):
    p_rounded = np.format_float_scientific(p_emp, 1)
    if p_rounded in p2z:
        return p2z.get(p_rounded)
    z = statistics.NormalDist().inv_cdf(float(p_rounded))
    p2z[p_rounded] = z
    return z

# Cell


# Cell
def count_fraction_outliers_from_expected_fc(result_df, threshold, expected_log2fc):
    num_outliers = sum([abs(x-expected_log2fc)> threshold for x in result_df["log2fc"]])
    fraction_outliers = num_outliers/len(result_df["log2fc"])
    LOGGER.info(f"{round(fraction_outliers, 2)} outliers")
    return fraction_outliers

# Cell



# Cell
import os
import shutil
def create_or_replace_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

# Cell
def write_chunk_to_file(chunk, filepath ,write_header):
    """write chunk of pandas dataframe to a file"""
    chunk.to_csv(filepath, header=write_header, mode='a', sep = "\t", index = None)


# Cell
import yaml
import os.path
import pathlib
import re

def remove_old_method_parameters_file_if_exists(results_dir):
    params_file = f"{results_dir}/aq_parameters.yaml"
    if os.path.exists(params_file):
        os.remove(params_file)


def load_method_parameters(results_dir):
    params_file = f"{results_dir}/aq_parameters.yaml"
    return load_config(params_file)

def load_config(config_yaml):
    stream = open(config_yaml, 'r')
    config_all = yaml.safe_load(stream)
    return config_all

def store_method_parameters(local_vars_dict, results_dir):
    method_params = get_methods_dict_from_local_vars(local_vars_dict)
    method_params["alphaquant_version"] = importlib.metadata.version("alphaquant")
    #add_ml_input_file_location(method_params)
    params_file = f"{results_dir}/aq_parameters.yaml"
    if os.path.exists(params_file):
        previous_params = load_method_parameters(results_dir)
        previous_params = {x:y for x, y in previous_params.items() if x not in method_params.keys()}
        method_params.update(previous_params)
    if not os.path.exists(f"{results_dir}/"):
        os.makedirs(f"{results_dir}/")
    save_dict_as_yaml(method_params, params_file)

def save_dict_as_yaml(dict, file):
    with open(file, 'w') as outfile:
        yaml.dump(dict, outfile, default_flow_style=False)


def get_methods_dict_from_local_vars(local_vars):
    method_params = {}
    allowed_types = (bool, int, float, str, type(None))

    for x, value in local_vars.items():
        if not isinstance(value, allowed_types):
            continue

        if (("_df" not in x) and ('condpair' not in x) and ('sys'!=x) and ('runconfig' != x)):
            if ("input_file" in x) or ("results_dir" in x):
                method_params[x] = os.path.abspath(value)
            else:
                method_params[x] = value

    return method_params

def add_ml_input_file_location(method_params):
    input_file = method_params.get("input_file")
    if ".aq_reformat" in input_file:
        ml_input_file = get_path_to_unformatted_file(input_file)
    else:
        ml_input_file = input_file
    method_params["ml_input_file"] = ml_input_file

def get_path_to_unformatted_file(input_file_name):
    prefixes = input_file_name.split(".")[:-3]
    cleaned_filename = ".".join(prefixes)
    return cleaned_filename




# Cell

# Cell
import os
def check_for_processed_runs_in_results_folder(results_folder):
    contained_condpairs = []
    folder_files = os.listdir(results_folder)
    result_files = list(filter(lambda x: "results.tsv" in x ,folder_files))
    for result_file in result_files:
        res_name = result_file.replace(".results.tsv", "")
        if ((f"{res_name}.normed.tsv" in folder_files) and (f"{res_name}.results.ions.tsv" in folder_files)):
            contained_condpairs.append(res_name)
    return contained_condpairs

# Cell
import pandas as pd
import os
import pathlib

import alphabase.quantification.quant_reader.config_dict_loader as abconfigdictloader
import alphabase.quantification.quant_reader.longformat_reader as ablongformatreader
import alphabase.quantification.quant_reader.wideformat_reader as abwideformatreader



def import_data(input_file, input_type_to_use = None, samples_subset = None, results_dir = None, file_has_alphaquant_format = False):
    """
    Function to import peptide level data. Depending on available columns in the provided file,
    the function identifies the type of input used (e.g. Spectronaut, MaxQuant, DIA-NN), reformats if necessary
    and returns a generic wide-format dataframe
    :param file input_file: quantified peptide/ion -level data
    :param file results_folder: the folder where the alphaquant outputs are stored
    """

    samples_subset = add_ion_protein_headers_if_applicable(samples_subset)
    if "aq_reformat" in input_file or file_has_alphaquant_format:
        file_to_read = input_file
    else:
        file_to_read = reformat_and_save_input_file(input_file=input_file, input_type_to_use=input_type_to_use, use_alphaquant_format = True)

    input_reshaped = pd.read_csv(file_to_read, sep = "\t", encoding = 'latin1', usecols=samples_subset)
    input_reshaped = input_reshaped.drop_duplicates(subset='quant_id')
    input_reshaped = input_reshaped.astype({'protein': 'str', QUANT_ID: 'str'})

    return input_reshaped

def add_ion_protein_headers_if_applicable(samples_subset):
    if samples_subset is not None:
        return samples_subset + [QUANT_ID, "protein"]
    else:
        return None

def reformat_and_save_input_file(input_file, input_type_to_use = None, use_alphaquant_format = False):

    input_type, config_dict_for_type, sep = abconfigdictloader.get_input_type_and_config_dict(input_file, input_type_to_use)
    LOGGER.info(f"using input type {input_type}")
    format = config_dict_for_type.get('format')
    outfile_name = f"{input_file}.{input_type}.aq_reformat.tsv"

    if format == "longtable":
        ablongformatreader.reformat_and_write_longtable_according_to_config(input_file, outfile_name,config_dict_for_type, sep = sep, use_alphaquant_format=use_alphaquant_format)
    elif format == "widetable":
        abwideformatreader.reformat_and_write_wideformat_table(input_file, outfile_name, config_dict_for_type)
    else:
        raise Exception('Format not recognized!')
    return outfile_name


# Cell

def merge_acquisition_df_parameter_df(acquisition_df, node_features_df, groupby_merge_type = 'mean'):
    """acquisition df contains details on the acquisition, parameter df are the parameters derived from the tree
    """
    merged_df = node_features_df.merge(acquisition_df, how = 'left', on = QUANT_ID)

    if groupby_merge_type == 'mean':
        merged_df = merged_df.groupby(QUANT_ID).mean().reset_index()
    if groupby_merge_type == 'min':
        merged_df = merged_df.groupby(QUANT_ID).min().reset_index()
    if groupby_merge_type == 'max':
        merged_df = merged_df.groupby(QUANT_ID).max().reset_index()
    merged_df = merged_df.dropna(axis=1, how='all')
    return merged_df
