import os
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from anonymization.anonymization_script import anonymize_ucc_cardio_data
from evaluation.local_utils import MEDICAL_SCORE, get_attributes, FEATURE_SETS
from evaluation.privacy_evaluation_script import anonymeter_evaluation
from preprocessing.filtering import select_score_subsample
from preprocessing.preprocess_UCC import preprocess, drop_score_columns, drop_column_cleanup
from score_calculation.score_calculation import calculate_scores
from synthetization.synthetization_script import synthesize_ucc_cardio_data


DATE_TODAY = datetime.now().strftime('%Y-%m-%d')

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def full_data_analysis(input_path, output_path, medical_score: MEDICAL_SCORE):
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    # general script overview:
    full_dataset = pd.read_csv(input_path)

    # data preprocessing
    print("Preprocessing started.")
    full_dataset_cleaned = preprocess(full_dataset)

    # Filter subsample
    print("Filtering started.")
    full_dataset_cleaned = select_score_subsample(full_dataset_cleaned, medical_score)
    full_dataset_cleaned = drop_column_cleanup(full_dataset_cleaned)

    # split datasets for holdout analysis
    train_dataset_cleaned, control_dataset_cleaned = train_test_split(full_dataset_cleaned, test_size=0.5)

    train_dataset_cleaned = drop_column_cleanup(train_dataset_cleaned)
    control_dataset_cleaned = drop_column_cleanup(control_dataset_cleaned)

    # anonymization (might take long!)
    print("Anonymization started.")
    anonymized_dataset = anonymize_ucc_cardio_data(drop_score_columns(train_dataset_cleaned.copy()),
                                                   anon_type=medical_score)

    # synthetization (might take long!)
    print("Synthetization started.")
    synthetic_dataset = synthesize_ucc_cardio_data(train_dataset_cleaned.copy())

    # synthetization (might take long!)
    print("Synthetization of anonymized Data started.")
    anonymized_dataset = anonymized_dataset.replace("*", np.nan)
    anonymized_dataset['alias'] = np.core.defchararray.add('ID_', np.arange(len(anonymized_dataset)).astype(str))
    synthetic_anon_dataset = synthesize_ucc_cardio_data(anonymized_dataset.copy(),
                                                        columns_spec=FEATURE_SETS[medical_score]['all'])

    # synthetic_dataset is reduced to the columns in the used FEATURE_SET, missing columns are replaced by nan values
    columns = [c for c in train_dataset_cleaned.keys() if c not in FEATURE_SETS[medical_score]['all']]
    synthetic_anon_dataset[columns] = np.nan

    # score calculation for orig, anon, synth

    full_dataset_cleaned = calculate_scores(full_dataset_cleaned)
    anonymized_dataset = calculate_scores(anonymized_dataset.replace("*", "nan"))
    synthetic_dataset = calculate_scores(synthetic_dataset)
    synthetic_anon_dataset = calculate_scores(synthetic_anon_dataset)

    # evaluation

    string_columns = ["alias", "site", "treatment", "egfr_u", "hb_u", "lvef_u", "sys_bp_u", "creatinine_u", "sodium_u",
                      "ntprobnp_m", "ntprobnp_u", "hstnt_u"]
    anonymized_dataset[string_columns] = anonymized_dataset[string_columns].astype(object)
    synthetic_anon_dataset[string_columns] = synthetic_anon_dataset[string_columns].astype(object)

    full_dataset_cleaned[["beta", "furosemide1", "statin", "age", "acei_arb"]] = full_dataset_cleaned[
        ["beta", "furosemide1", "statin", "age", "acei_arb"]].astype("float64")
    anonymized_dataset["age"] = anonymized_dataset["age"].astype("float64")
    synthetic_dataset["age"] = synthetic_dataset["age"].astype("float64")
    synthetic_anon_dataset["age"] = synthetic_anon_dataset["age"].astype("float64")

    score_related_columns = get_attributes(medical_score) + ["alias"]

    print("Risk Evaluation started.")
    results_syn, holdout_res_syn = anonymeter_evaluation(full_dataset_cleaned[score_related_columns],
                                                         synthetic_dataset[score_related_columns],
                                                         control_dataset_cleaned[score_related_columns])
    results_anon, holdout_res_anon = anonymeter_evaluation(full_dataset_cleaned[score_related_columns],
                                                           anonymized_dataset[score_related_columns],
                                                           control_dataset_cleaned[score_related_columns])

    results_combined, holdout_res_combined = anonymeter_evaluation(full_dataset_cleaned[score_related_columns],
                                                                   synthetic_anon_dataset[score_related_columns],
                                                                   control_dataset_cleaned[score_related_columns])

    print("Evaluation finished.")

    results_anonymeter = pd.concat([results_syn, results_anon, results_combined], axis=1)
    results_holdout = pd.concat([holdout_res_syn, holdout_res_anon, holdout_res_combined], axis=1)
    results_holdout.columns = ["Synthetic", "Anonymized", "Combined"]

    results_anonymeter.to_csv(os.path.join(output_path, f"{DATE_TODAY}_{medical_score.value}_anonymeter.csv"))
    results_holdout.to_csv(os.path.join(output_path, f"{DATE_TODAY}_{medical_score.value}_holdout.csv"))


if __name__ == "__main__":
    ORIGINAL_FILE = os.path.join(Path(__file__).parent, "data", "random_UCC_heart_data.csv")
    OUTPUT_PATH = os.path.join(Path(__file__).parent, "results")

    argparser = ArgumentParser()
    argparser.add_argument('--input_original', '-io', type=str,
                           default=ORIGINAL_FILE,
                           help='Path to the config file')
    argparser.add_argument('--output', '-o', type=str,
                           default=OUTPUT_PATH,
                           help='relative output path')
    args = argparser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)
        os.makedirs(os.path.join(args.output, "BIOHF"))
        os.makedirs(os.path.join(args.output, "MAGGIC"))

    full_data_analysis(args.input_original, os.path.join(args.output, "BIOHF"), MEDICAL_SCORE.BIOHF)
    full_data_analysis(args.input_original, os.path.join(args.output, "MAGGIC"), MEDICAL_SCORE.MAGGIC)
