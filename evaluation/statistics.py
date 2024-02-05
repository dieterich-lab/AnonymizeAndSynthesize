import numpy as np
from scipy import stats
import pandas as pd
import math


def calc_stats_for_all(data, featureset=None):
    if not featureset:
        featureset = data.columns
    stats_ALL = pd.DataFrame()
    for varName in featureset:
        try:
            stats_ALL[varName] = calc_stats(data, varName)
        except:
            pass
    return pretty_summary_for(stats_ALL, featureset)


def pretty_summary_for(groupStats, parameters):
    returnValue = pd.Series()
    for parameter in parameters:
        returnValue[parameter] = '{:.2f} ({:.2f})'.format(groupStats[parameter].Mean, groupStats[parameter].SD)
    return returnValue


def pretty_comparison_summary_for(groupStats, parameters, mean_index, sd_index):
    returnValue = pd.Series()
    for parameter in parameters:
        if groupStats[parameter].dtype == "object":
            returnValue[parameter] = f"{groupStats[parameter][mean_index]} ({groupStats[parameter][sd_index]})"
        else:
            returnValue[parameter] = '{:.2f} ({:.2f})'.format(groupStats[parameter][mean_index],
                                                              groupStats[parameter][sd_index])
    return returnValue

def calc_stats(dataset, featurename):
    variable = dataset[featurename].dropna()
    n_pd = len(variable)
    mean_pd = variable.mean()
    std_pd = variable.std()
    w, p_val = stats.shapiro(variable)
    header = ['N', 'Mean', 'SD', 'Shapiro Wilk W', 'Shapiro p-Value']
    data = [n_pd, mean_pd, std_pd, w, p_val]
    return pd.Series(data, index=header)


def compare_datasets(dataset_1, dataset_2, featureset_cont, featureset_cat, prefix, ignore_error=False):
    stats_comparisons_ALL = pd.DataFrame()
    for varName in featureset_cont:
        try:
            stats_comparisons_ALL[varName] = calc_comparison_statistics(dataset_1, dataset_2, varName, prefix)
        except Exception as e:
            stats_comparisons_ALL[varName] = 'NaN'
            if ignore_error:
                pass
            else:
                print(e)
                print(f"Error in compare Datasets for numerical Parametername {varName}")

    stats_comparisons_cat = {}
    for varName in featureset_cat:
        try:
            stats_comparisons_cat[varName] = calc_comparison_statistics_cat(dataset_1, dataset_2, varName, prefix)
        except Exception as e:
            stats_comparisons_cat[varName] = pd.DataFrame()
            if ignore_error:
                pass
            else:
                print(e)
                print(f"Error in compare Datasets for categorical Parametername {varName}")
    stats_comparisons_cat = pd.concat(stats_comparisons_cat)

    pretty_result_cont = summary_continuous_stats(stats_comparisons_ALL, prefix, featureset_cont)
    pretty_result_cat = summary_categorical_stats(stats_comparisons_cat, prefix)
    return pretty_result_cont, pretty_result_cat

def summary_continuous_stats(data_comparison, groups, parameterset_cont):
    group1 = groups[0]
    group2 = groups[1]
    table_content = {}
    table_content[f'{group1}_values'] = pretty_comparison_summary_for(data_comparison, parameterset_cont,
                                                                      f'{group1}_Mean', f'{group1}_SD')
    table_content[f'{group2}_values'] = pretty_comparison_summary_for(data_comparison, parameterset_cont,
                                                                      f'{group2}_Mean', f'{group2}_SD')
    # table_content[f'{group1}_vs_{group2}_pvalues'] = data_comparison[parameterset].loc['p-value mann whitney u'].map('{:,.3f}'.format)
    # table_content[f'{group1}_vs_{group2}_uvalues'] = data_comparison[parameterset].loc['U mann whitney u'].map('{:,.3f}'.format)
    table_content[f'{group1}_vs_{group2}_pvalues'] = data_comparison[parameterset_cont].loc['p-value kolmogorov smirnov'].map('{:,.3f}'.format)
    table_content[f'{group1}_vs_{group2}_tvalues'] = data_comparison[parameterset_cont].loc['d kolmogorov smirnov'].map('{:,.3f}'.format)
    # table_content[f'{group1}_vs_{group2}_pvalues'] = data_comparison[parameterset].loc['p-value indep. t test'].map('{:,.3f}'.format)
    # table_content[f'{group1}_vs_{group2}_tvalues'] = data_comparison[parameterset].loc['t indep. t test'].map('{:,.3f}'.format)
    table_content[f'{group1}_vs_{group2}_cohensd'] = data_comparison[parameterset_cont].loc['Cohens D'].map('{:,.3f}'.format)
    #table_content[f'{group1}_vs_{group2}_hedgesg'] = data_comparison[parameterset_cont].loc['Hedges G'].map('{:,.3f}'.format)
    n_group1 = data_comparison.iloc[:, 0][f'{group1}_N']
    n_group2 = data_comparison.iloc[:, 0][f'{group2}_N']
    columnames = [f"{group1}, N={n_group1}",
                  f"{group2}, N={n_group2}",
                  f"{group1} vs. {group2} p-value (KS Test)",
                  f"{group1} vs. {group2} d value (KS Test)",
                  f"{group1} vs. {group2} Cohens D",
                  #f"{group1} vs. {group2} Hedges G"
                  ]
    table = pd.DataFrame(data=table_content)
    table.columns = columnames
    return table

def summary_categorical_stats(data_comparison, groups):
    group1 = groups[0]
    group2 = groups[1]

    table_content = {}

    data_comparison.index = data_comparison.index.map(lambda x: '{}  {}'.format(x[0], x[1]))
    parameterset_cont = data_comparison.index
    data_comparison = data_comparison.transpose()

    table_content[f'{group1}_values'] = pretty_comparison_summary_for(data_comparison, parameterset_cont,
                                                                      f'{group1} Frequency', f'{group1} Proportion')
    table_content[f'{group2}_values'] = pretty_comparison_summary_for(data_comparison, parameterset_cont,
                                                                      f'{group2} Frequency', f'{group2} Proportion')
    table_content[f'{group1}_vs_{group2}_pvalues'] = data_comparison[parameterset_cont].loc['Chi2 p-value'].map('{:,.3f}'.format)
    table_content[f'{group1}_vs_{group2}_values'] = data_comparison[parameterset_cont].loc['Chi2'].map('{:,.3f}'.format)
    table_content[f'{group1}_vs_{group2}cramersv'] = data_comparison[parameterset_cont].loc['Cramers_V'].map('{:,.3f}'.format)
    #table_content[f'{group1}_vs_{group2}_fisherpvalues'] = data_comparison[parameterset_cont].loc['Fisher_p-value'].map('{:,.3f}'.format)

    n_group1 = data_comparison.iloc[:, 0][f'{group1} Frequency'].sum()
    n_group2 = data_comparison.iloc[:, 0][f'{group2} Frequency'].sum()
    columnames = [f"{group1} Freq. (ratio), N={n_group1}",
                  f"{group2} Freq. (ratio), N={n_group2}",
                  f"{group1} vs. {group2} p-value (X^2 Test)",
                  f"{group1} vs. {group2} X^2 value (X^2 Test)",
                  f"{group1} vs. {group2} Cramers V",
                  #f"{group1} vs. {group2} Fisher p-value"
                  ]
    table = pd.DataFrame(data=table_content)
    table.columns = columnames
    return table


def calc_comparison_statistics(dataset_1, dataset_2, featurename, prefix=['DS_1_', 'DS_2_']):
    variable_1 = dataset_1[featurename].dropna().astype(float)
    variable_2 = dataset_2[featurename].dropna().astype(float)

    stats_1 = calc_stats(dataset_1, featurename)
    stats_2 = calc_stats(dataset_2, featurename)
    mean_diff = stats_1['Mean'] - stats_2['Mean']
    cohens_d = (mean_diff) / (math.sqrt((stats_1['SD'] ** 2 + stats_2['SD'] ** 2) / 2))
    pooled_sd = math.sqrt(
        (((stats_1['N'] - 1) * (stats_1['SD'] ** 2)) + ((stats_2['N'] - 1) * (stats_2['SD'] ** 2))) / (
                stats_1['N'] + stats_2['N'] - 2))
    hedges_g = mean_diff / pooled_sd

    stats_levene, p_levene = stats.levene(variable_1, variable_2)
    t_ttest, p_ttest = stats.ttest_ind(variable_1, variable_2)

    xt_1, _ = stats.boxcox(variable_1)
    xt_2, _ = stats.boxcox(variable_1)
    t_ttest2, p_ttest2 = stats.ttest_ind(xt_1, xt_2)
    t_mwu, p_mwu = stats.mannwhitneyu(variable_1, variable_2,
                                      alternative='two-sided')
    stat_ks, p_ks = stats.kstest(variable_1, variable_2)

    if (len(prefix) == 2):
        stats_1.index = prefix[0] + '_' + stats_1.index
        stats_2.index = prefix[1] + '_' + stats_2.index

    return pd.concat([stats_1, stats_2, pd.Series(
        [mean_diff, cohens_d, hedges_g, p_levene, t_ttest, p_ttest, t_ttest2, p_ttest2, t_mwu, p_mwu, stat_ks, p_ks],
        index=['Mean Diff', 'Cohens D', 'Hedges G', 'Levene p', 't indep. t test', 'p-value indep. t test',
               't normalized t test', 'p-value normalized. t test', 'U mann whitney u', 'p-value mann whitney u',
               'd kolmogorov smirnov', 'p-value kolmogorov smirnov'])])

def calc_comparison_statistics_cat(dataset_1, dataset_2, featurename, prefix=['DS_1_', 'DS_2_']):
    # Frequency and proportion of each category in dataset 1
    freq_1 = dataset_1[featurename].value_counts()
    prop_1 = dataset_1[featurename].value_counts(normalize=True)

    # Frequency and proportion of each category in dataset 2
    freq_2 = dataset_2[featurename].value_counts()
    prop_2 = dataset_2[featurename].value_counts(normalize=True)

    # Number of unique categories in each dataset
    num_categories_1 = dataset_1[featurename].nunique()
    num_categories_2 = dataset_2[featurename].nunique()

    # Chi-square test
    # Creating a contingency table
    contingency_table = pd.crosstab(dataset_1[featurename], dataset_2[featurename])
    freq_2_chi2 = freq_2[freq_1.index]  # uses only original categories and drops generalized ones for statistical analyses
    freq_2_normed = (freq_1.sum()/freq_2_chi2.sum()) * freq_2_chi2
    chi2, p = stats.chisquare(f_obs=freq_1, f_exp=freq_2_normed)

    stats_df = pd.concat([freq_1, prop_1, freq_2, prop_2], axis=1)
    stats_df.columns = [f"{prefix[0]} Frequency",
                        f"{prefix[0]} Proportion",
                        f"{prefix[1]} Frequency",
                        f"{prefix[1]} Proportion"]
    stats_df["Chi2"] = chi2
    stats_df["Chi2 p-value"] = p

    # Cramér's V
    phi2 = chi2 / sum(contingency_table.sum())
    n = contingency_table.sum().sum()
    minDim = min(contingency_table.shape) - 1
    cramers_v = np.sqrt(phi2 / minDim)

    # Fisher's Exact Test (for 2x2 tables)
    if contingency_table.shape == (2, 2):
        _, fisher_p = stats.fisher_exact(contingency_table)
    else:
        fisher_p = None

    # Append results to the DataFrame
    stats_df["Cramers_V"] = cramers_v
    stats_df["Fisher_p-value"] = fisher_p

    return stats_df
