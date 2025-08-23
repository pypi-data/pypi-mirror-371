import alphaquant.diffquant.background_distributions as aqbg
from numba import njit
import numpy as np


def calc_doublediff_score(ions1, ions2, normed_c1, normed_c2, ion2diffDist, p2z, deedpair2doublediffdist):#~13% of overall runtime
    """Gives a p-value for the null hypothesis: No change between the foldchanges of the ions1 in comparison to the ions2

    Args:
        ions1 (list[String]): list of ions1 to be compared to ions1
        ions2 (list[String]): list of ions2  to be compared to ions1
        normed_c1 (ConditionBackground): Condition background ions1
        normed_c2 (ConditionBackground): Condition background ions2
        ion2diffDist (dict[String : EmpiricalBackground]): map from each ion to its assigned empirical background distribution
        p2z (dict[double:double]): map from p-value to z-value (lookup to improve runtime)
        deedpair2doublediffdist (dict[(EmpiricalBackground, EmpiricalBackground) : EmpiricalBackground]): map from each pair of empirical backgrounds to the subtracted empirical background representing the double differential noise

    Returns:
        double: p-value as specified above
    """
    z_total = 0
    fcfc_total = 0
    count_pairs = 0
    firstterm_variance = 0
    all_ionpairs = []
    ion2pairs = {}
    ionpair2idx_ols = {}

    nrep_c1 = len(normed_c1.ion2allvals.get(ions1[0]))
    nrep_c2 = len(normed_c2.ion2allvals.get(ions2[0]))


    for ion1 in ions1:
        ion1_c1_ints = normed_c1.ion2allvals.get(ion1)
        ion1_c2_ints = normed_c2.ion2allvals.get(ion1)
        for ion2 in ions2:
            ion2_c1_ints = normed_c1.ion2allvals.get(ion2)
            ion2_c2_ints = normed_c2.ion2allvals.get(ion2)

            #account for missing values: ion1 and ion2 values are only compared within the same sample -> filter for intensities that occur in the same sample for both ions
            overlapping_c1_idx = get_indexes_present_in_both_ions(nrep=nrep_c1, ion1_ints=ion1_c1_ints, ion2_ints=ion2_c1_ints)#[x for x in range(nrep_c1) if (~np.isnan(ion1_c1_ints[x])) & (~np.isnan(ion2_c1_ints[x]))]
            nrep_ol_c1 = len(overlapping_c1_idx)
            if nrep_ol_c1 ==0:
                continue

            overlapping_c2_idx = get_indexes_present_in_both_ions(nrep=nrep_c2, ion1_ints=ion1_c2_ints, ion2_ints=ion2_c2_ints)#[x for x in range(nrep_c2) if (~np.isnan(ion1_c2_ints[x])) & (~np.isnan(ion2_c2_ints[x]))]
            nrep_ol_c2 = len(overlapping_c2_idx)
            if nrep_ol_c2 ==0:
                continue

            #collection information for later variance calculation
            ionpair = (ion1, ion2)
            all_ionpairs.append(ionpair)
            ion2pairs[ion1] = ion2pairs.get(ion1, []) + [ionpair]
            ion2pairs[ion2] = ion2pairs.get(ion2, []) + [ionpair]
            ionpair2idx_ols[ionpair] = [overlapping_c1_idx, overlapping_c2_idx]

            #define all empirical error distributions (eed) and differential empirical error distributions (deed) and obtain the variance
            eed_ion1_c1 = normed_c1.ion2background.get(ion1)
            eed_ion1_c2 = normed_c2.ion2background.get(ion1)

            eed_ion2_c1 = normed_c1.ion2background.get(ion2)
            eed_ion2_c2 = normed_c2.ion2background.get(ion2)

            deed_ion1 = aqbg.get_subtracted_bg(ion2diffDist,eed_ion1_c1, eed_ion1_c2, p2z)
            deed_ion2 = aqbg.get_subtracted_bg(ion2diffDist,eed_ion2_c1, eed_ion2_c2, p2z)

            #calculate the ionpair total variance as shown in Berchtold et al. EmpiReS

            ionpair_variance = (nrep_ol_c1 * nrep_ol_c2 *(deed_ion1.var + deed_ion2.var) + nrep_ol_c1 *nrep_ol_c2 *(nrep_ol_c2-1) * (eed_ion1_c1.var + eed_ion2_c1.var) +
             nrep_ol_c1 *nrep_ol_c2 *(nrep_ol_c1-1) * (eed_ion1_c2.var + eed_ion2_c2.var))/(deed_ion1.var + deed_ion2.var)

            firstterm_variance += ionpair_variance

            #calculate z-value and fcfc for the ion pair
            ddeed_ion1_ion2 = aqbg.get_doublediff_bg(deed_ion1, deed_ion2, deedpair2doublediffdist,p2z)

            z_pair, fcfc_pair = calc_per_peppair_z_and_fcfc(overlapping_c1_idx = np.array(overlapping_c1_idx), overlapping_c2_idx = np.array(overlapping_c2_idx), ion1_c1_ints=  ion1_c1_ints, ion1_c2_ints=ion1_c2_ints,
            ion2_c1_ints = ion2_c1_ints, ion2_c2_ints = ion2_c2_ints, fc_conversion_factor=ddeed_ion1_ion2.fc_conversion_factor,
            fc_resolution_factor=ddeed_ion1_ion2.fc_resolution_factor, min_fc= ddeed_ion1_ion2.min_fc, cumulative = ddeed_ion1_ion2.cumulative, max_z= ddeed_ion1_ion2.max_z, zscores= ddeed_ion1_ion2.zscores)
            z_total+=z_pair
            fcfc_total+=fcfc_pair
            count_pairs+=1

    if count_pairs==0: # in this case, it was not possible to find any sample overlaps -> no comparison "possible"
        return 0.0, 1.0 # classify as "similar" in this case, as we cannot reject the null hypothesis
    secondterm_variance = calculate_pairpair_overlap_factor(all_ionpairs, ion2pairs, ionpair2idx_ols, normed_c1, normed_c2, ion2diffDist, p2z)
    fcfc = fcfc_total/count_pairs
    pval = calculate_scaled_pval(z_total, firstterm_variance, secondterm_variance)

    return fcfc, pval

@njit
def calc_per_peppair_z_and_fcfc(*,overlapping_c1_idx, overlapping_c2_idx, ion1_c1_ints, ion1_c2_ints, ion2_c1_ints, ion2_c2_ints, fc_conversion_factor, fc_resolution_factor, min_fc, cumulative, max_z, zscores):
    fcfc_res = 0
    count_fcfcs = 0
    z_summed = 0


    for idx1 in overlapping_c1_idx:
        for idx2 in overlapping_c2_idx:
            fc_ion1 = ion1_c1_ints[idx1] - ion1_c2_ints[idx2]
            fc_ion2 = ion2_c1_ints[idx1] - ion2_c2_ints[idx2]
            fcfc_idxpair = fc_ion1 - fc_ion2
            z_idxpair = aqbg._calc_zscore_from_fc(fc = fcfc_idxpair,fc_conversion_factor=fc_conversion_factor, fc_resolution_factor=fc_resolution_factor, min_fc=min_fc, cumulative=cumulative, max_z=max_z, zscores=zscores)
            fcfc_res += fcfc_idxpair
            z_summed += z_idxpair
            count_fcfcs+=1
    if count_fcfcs==0:
        raise Exception("no idx overlap even though filtering has happened!")

    return z_summed, fcfc_res/count_fcfcs





def calculate_pairpair_overlap_factor(all_ionpairs, ion2pairs, ionpair2idx_ols, normed_c1, normed_c2, ion2diffdist, p2z):

    secondterm_variance = 0

    for ionpair in all_ionpairs:
        for ion in ionpair:
            compare_pairs = ion2pairs.get(ion)
            compare_pairs.remove(ionpair)

            for comp_ionpair in compare_pairs:

                comp_ion = comp_ionpair[0]

                idxs_ionpair = ionpair2idx_ols.get(ionpair)
                idxs_comp_ionpair = ionpair2idx_ols.get(comp_ionpair)

                n_sameidx_first = len(set(idxs_ionpair[0]).intersection(set(idxs_comp_ionpair[0])))
                n_sameidx_second = len(set(idxs_ionpair[1]).intersection(set(idxs_comp_ionpair[1])))


                eed_ion_c1 = normed_c1.ion2background.get(ion)
                eed_ion_c2 = normed_c2.ion2background.get(ion)

                eed_comp_ion_c1 = normed_c1.ion2background.get(comp_ion)
                eed_comp_ion_c2 = normed_c2.ion2background.get(comp_ion)

                deed1 = aqbg.get_subtracted_bg(ion2diffdist, eed_ion_c1, eed_ion_c2, p2z)
                deed2 = aqbg.get_subtracted_bg(ion2diffdist, eed_comp_ion_c1, eed_comp_ion_c2, p2z)



                correlation_normfact = deed1.SD * deed2.SD

                var_overlap = len(idxs_ionpair[1])*len(idxs_comp_ionpair[1]) * n_sameidx_first * eed_ion_c1.var + len(idxs_ionpair[0])*len(idxs_comp_ionpair[0]) * n_sameidx_second * eed_ion_c2.var
                secondterm_variance += var_overlap/correlation_normfact

    return secondterm_variance


from statistics import NormalDist

def calculate_scaled_pval(z_sum, firstterm_variance, secondterm_variance):
    scaled_SD = np.sqrt((firstterm_variance+secondterm_variance))
    p_val = 2.0 * (1.0 -  NormalDist(mu=0, sigma= scaled_SD).cdf(abs(z_sum)))
    return p_val




@njit
def get_indexes_present_in_both_ions(*,nrep, ion1_ints, ion2_ints):
    res = []
    for x in range(nrep):
        if (~np.isnan(ion1_ints[x])) and (~np.isnan(ion2_ints[x])):
            res.append(x)
    return res

