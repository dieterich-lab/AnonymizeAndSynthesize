from argparse import ArgumentParser
from datetime import datetime

from evaluation.local_utils import read_data, MEDICAL_SCORE, FEATURE_SETS
from evaluation.plots import violin_plots, ecdf_plot
from evaluation.statistics import compare_datasets
import pandas as pd

pd.set_option('display.max_columns',None)
pd.set_option('max_colwidth',None)
pd.set_option('max_seq_items',None)

DATE_TODAY = datetime.now().strftime('%Y-%m-%d')

def evaluate_datasets(dataset_original: pd.DataFrame,
                      dataset_synth: pd.DataFrame,
                      dataset_anon: pd.DataFrame,
                      dataset_combined: pd.DataFrame,
                      output_path: str,
                      medical_score:MEDICAL_SCORE):

    dataset_original["anonymized"] = "Original"
    dataset_anon["anonymized"] = "Anonymized"
    dataset_synth["anonymized"] = "Synthetic"
    dataset_combined["anonymized"] = "Combined"
    data = pd.concat([dataset_original, dataset_anon, dataset_synth], axis=0)
    data.reset_index(inplace=True)

    ### question 1 + 2: statistical comparisons dataset and medical scores
    comparison_original_synth, comparison_original_synth_cat = compare_datasets(dataset_original, dataset_synth,
                                                                                FEATURE_SETS[medical_score]["continuous"],
                                                                                FEATURE_SETS[medical_score]["categorical"],
                                                                                ["original", "synthetic"], ignore_error=True)


    comparison_original_anon, comparison_original_anon_cat = compare_datasets(dataset_original, dataset_anon,
                                                                              FEATURE_SETS[medical_score]["continuous"],
                                                                              FEATURE_SETS[medical_score]["categorical"],
                                                                              ["original", "anonymized"], ignore_error=True)


    comparison_original_combined, comparison_original_combined_cat = compare_datasets(dataset_original, dataset_combined,
                                                                              FEATURE_SETS[medical_score]["continuous"],
                                                                              FEATURE_SETS[medical_score]["categorical"],
                                                                              ["original", "combined"], ignore_error=True)

    stats_cont = pd.concat([comparison_original_synth, comparison_original_anon, comparison_original_combined], axis=1)
    stats_cat = pd.concat([comparison_original_synth_cat, comparison_original_anon_cat, comparison_original_combined_cat], axis=1)


    stats_cont.to_csv(f"{output_path}/{DATE_TODAY}_comparison_statistics_{medical_score.name}_cont.csv")
    stats_cat.to_csv(f"{output_path}/{DATE_TODAY}_comparison_statistics_{medical_score.name}_cat.csv")

    ### 3. question: visual comparisons medical scores
    IMAGE_SUFFIX = "eps"
    SCORES = {'maggic_score_1': 'MAGGIC score 1 year mortality',
               'biohf_v1_1': 'Barcelona Heart Failure score 1 year mortality'}

    for score in SCORES:
        if not medical_score.value.lower() in score:
            continue

        orig_values = dataset_original[score].dropna().astype(float).values
        anon_values = dataset_anon[score].dropna().astype(float).values
        synth_values = dataset_synth[score].dropna().astype(float).values
        combined_values = dataset_combined[score].dropna().astype(float).values

        ecdf_plot(orig_values, anon_values, synth_values, combined_values,
                        xlabel=SCORES[score],
                        save_to=f'{output_path}/{DATE_TODAY}_ecdf_orig_anon_synth-{score}.{IMAGE_SUFFIX}')

        # violin plots
        violin_plots(orig_values, anon_values, synth_values, combined_values,
                           score,
                           save_to=f'{output_path}/{DATE_TODAY}_violin_anon_orig_synth-{score}.{IMAGE_SUFFIX}')

