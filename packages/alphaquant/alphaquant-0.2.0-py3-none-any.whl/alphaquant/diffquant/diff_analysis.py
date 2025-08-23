
from statistics import NormalDist
import numpy as np
import math
import statistics

class DifferentialIon():

    def __init__(self,noNanvals_from, noNanvals_to, diffDist, name, outlier_correction = True):


        self.name = name
        self.p_val = None
        self.fc = None
        self.z_val = None
        self.usable = False

        self._calc_diffreg_peptide(noNanvals_from, noNanvals_to, diffDist, name, outlier_correction)


    def _calc_diffreg_peptide(self, noNanvals_from, noNanvals_to, diffDist, name, outlier_correction):

        nrep_from = len(noNanvals_from)
        nrep_to = len(noNanvals_to)

        if ((nrep_from==0) or (nrep_to ==0)):
            return
        var_from = diffDist.var_from
        var_to = diffDist.var_to

        perEvidenceVariance = diffDist.var + (nrep_to-1) * var_from + (nrep_from-1) * var_to
        totalVariance = perEvidenceVariance*nrep_to * nrep_from
        outlier_scaling_factor = 1.0
        if outlier_correction:
            outlier_scaling_factor = calc_outlier_scaling_factor(noNanvals_from, noNanvals_to, diffDist)

        fc_sum =0
        z_sum=0
        unscaled_zs = []
        for from_intens in noNanvals_from:
            for to_intens in noNanvals_to:
                fc = from_intens - to_intens
                fc_sum+=fc
                z_unscaled = diffDist.calc_zscore_from_fc(fc)
                unscaled_zs.append(z_unscaled)
                z_sum += z_unscaled/outlier_scaling_factor

        scaled_SD =  math.sqrt(totalVariance/diffDist.var)*outlier_scaling_factor

        self.fc = fc_sum/(nrep_from * nrep_to)
        self.p_val = 2.0 * (1.0 -  NormalDist(mu=0, sigma= scaled_SD).cdf(abs(z_sum)))
        self.z_val = z_sum/scaled_SD
        self.usable = True



  #self.var_from = from_dist.var
   #     self.var_to

def calc_outlier_scaling_factor(noNanvals_from, noNanvals_to, diffDist):
    sd_from = math.sqrt(diffDist.var_from)
    sd_to = math.sqrt(diffDist.var_to)
    median_from = statistics.median(noNanvals_from)
    median_to = statistics.median(noNanvals_to)

    between_rep_SD_from = math.sqrt(sum(np.square(noNanvals_from-median_from))/len(noNanvals_from)) if len(noNanvals_from)>1 else sd_from
    between_rep_SD_to = math.sqrt(sum(np.square(noNanvals_to-median_to))/len(noNanvals_to)) if len(noNanvals_to)>1 else sd_to

    highest_SD_from = max(between_rep_SD_from, sd_from)
    highest_SD_to = max(between_rep_SD_to, sd_to)
    highest_SD_combined = math.sqrt(highest_SD_from**2 + highest_SD_to**2)

    scaling_factor = max(1.0, highest_SD_combined/diffDist.SD)
    return scaling_factor

# Cell
import math
import statistics

import numpy as np
import alphaquant.diffquant.diffutils as aqutils
class DifferentialProtein():

    def __init__(self, name, ion_diffresults, median_offset, dia_fragment_selection = False):
        self.name = name
        if dia_fragment_selection:
            ion_diffresults = select_representative_DIA_fragions(ion_diffresults)

        fc, pval, ions = evaluate_protein_expression(ion_diffresults, median_offset)

        self.pval=pval
        self.fc=fc
        self.ions = ions
        self.num_ions = len(ions)



def evaluate_protein_expression(ion_diffresults, median_offset):
    ion_diffresults = list(filter(lambda _f : _f.usable, ion_diffresults))

    if len(ion_diffresults) ==0:
        return
    fcs = list(map(lambda _dr : _dr.fc,ion_diffresults))
    median_fc = np.median(fcs)


    ion_diffresults, median_offset_fc = select_robust_if_many_ions(fcs, median_fc,ion_diffresults)


    z_sum = sum(map(lambda _dr: _dr.z_val, ion_diffresults))
    p_val = 2.0 * (1.0 - statistics.NormalDist(mu = 0, sigma = math.sqrt(len(ion_diffresults))).cdf(abs(z_sum)))
    ions = list(map(lambda _dr : _dr.name, ion_diffresults))

    prot_fc = median_offset_fc if median_offset else median_fc
    return prot_fc, p_val, ions


def select_robust_if_many_ions(fcs, median_fc,ion_diffresults):
    ninety_perc_cutoff = math.ceil(0.9*len(ion_diffresults)) #the ceil function ensures that ions are only excluded if there are more than 10 available
    ion_diffresults = sorted(ion_diffresults, key = lambda _dr : abs(_dr.fc - median_fc))
    if ninety_perc_cutoff >0:
        ion_diffresults = ion_diffresults[:ninety_perc_cutoff]
    median_offset_fc = aqutils.get_middle_elem(list(map(lambda _dr : _dr.fc,ion_diffresults)))
    return ion_diffresults, median_offset_fc

# Cell
def calc_pseudo_intensities(ions, normed_c2, log2fc):
    """Sumarizes the ion intensities in one condition and uses the fold change to calculate the intensity in the other condition.

    Args:
        ions ([type]): [description]
        normed_c2 ([type]): [description]
        log2fc ([type]): [description]
    """
    intensity_c2_summed = 0
    for ion in ions:
        intensity_est =  2**(np.median(normed_c2.ion2nonNanvals.get(ion.name)))
        intensity_c2_summed += intensity_est
    fc = 2**log2fc #fc = int_c1/int_c2
    intensity_c1_summed = fc*intensity_c2_summed#-> int_c1 = fc*int_c2
    return intensity_c1_summed, intensity_c2_summed


# Cell
import re
import numpy as np

def select_representative_DIA_fragions(diffions):
    filtered_ions = []
    precursor2ions = group_ions_by_precursor(diffions)
    for precursor in precursor2ions.keys():
        ions = precursor2ions.get(precursor)
        ions.sort(key = lambda x : x.fc)
        representative_ion = ions[int(np.round(len(ions)/2))]
        filtered_ions.append(representative_ion)
    return filtered_ions


def group_ions_by_precursor(diffions):
    pattern_specnaut = "(.*\.\d{0,1}_)(.*)"
    pattern_diann = "(.*_)(fion.*)"
    if (re.match(pattern_specnaut, diffions[0].name)):
        pattern = pattern_specnaut
    if (re.match(pattern_diann, diffions[0].name)):
        pattern = pattern_diann
    if pattern == None:
        raise Exception("fragment ion not recognized!")

    precursor2ions = {}
    for ion in diffions:
        m = re.match(pattern, ion.name)
        precursor = m.group(1)
        if precursor not in precursor2ions.keys():
            precursor2ions[precursor] = list()
        precursor2ions[precursor].append(ion)
    return precursor2ions
