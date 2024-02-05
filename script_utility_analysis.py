#!/usr/bin/env python3

import os
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from anonymization.anonymization_script import anonymize_ucc_cardio_data
from evaluation.evaluation_script import evaluate_datasets
from evaluation.local_utils import MEDICAL_SCORE, FEATURE_SETS
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

    ## data preprocessing
    print("Preprocessing started.")
    full_dataset_cleaned = preprocess(full_dataset)

    ## Filter subsample
    print("Filtering started.")
    full_dataset_cleaned = select_score_subsample(full_dataset_cleaned, medical_score)
    full_dataset_cleaned = drop_column_cleanup(full_dataset_cleaned)

    ## anonymization (might take long!)
    print("Anonymization started.")
    anonymized_dataset = anonymize_ucc_cardio_data(drop_score_columns(full_dataset_cleaned.copy()), anon_type=medical_score)

    ## synthetization (might take long!)
    print("Synthetization started.")
    synthetic_dataset = synthesize_ucc_cardio_data(full_dataset_cleaned.copy())

    ## synthetization (might take long!)
    print("Synthetization of anonymized Data started.")
    anonymized_dataset = anonymized_dataset.replace("*", np.nan)
    anonymized_dataset['alias'] = np.arange(len(anonymized_dataset))
    synthetic_anon_dataset = synthesize_ucc_cardio_data(anonymized_dataset.copy(),
                                                        columns_spec=FEATURE_SETS[medical_score]['all'])

    # synthetic_dataset is reduced to the columns in the used FEATURE_SET, missing columns are replaced by nan values
    columns = [c for c in synthetic_dataset.keys() if c not in FEATURE_SETS[medical_score]['all']]
    synthetic_anon_dataset[columns] = np.nan

    ## scoring
    print("Scoring started.")
    full_dataset_cleaned = calculate_scores(full_dataset_cleaned)

    anonymized_dataset = calculate_scores(anonymized_dataset)
    synthetic_dataset = calculate_scores(synthetic_dataset)
    synthetic_anon_dataset = calculate_scores(synthetic_anon_dataset)

    ## exporting
    filename = Path(input_path).name
    anonymized_dataset.to_csv(os.path.join(output_path, f"{filename}_anonymized.csv"))
    synthetic_dataset.to_csv(os.path.join(output_path, f"{filename}_synthetic.csv"))
    synthetic_anon_dataset.to_csv(os.path.join(output_path, f"{filename}_synth_anon.csv"))

    ## evaluation
    print("Evaluation started.")

    anonymized_dataset[["alias", "site", "treatment"]] = \
        anonymized_dataset[["alias", "site", "treatment"]].astype(object)

    evaluate_datasets(full_dataset_cleaned, synthetic_dataset, anonymized_dataset, synthetic_anon_dataset,
                      output_path, medical_score)


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
