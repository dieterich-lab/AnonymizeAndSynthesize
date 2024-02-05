import os
import subprocess
from argparse import ArgumentParser
from os.path import dirname, join
from pathlib import Path

import numpy as np
import pandas as pd

from evaluation.local_utils import read_data, MEDICAL_SCORE
from preprocessing.preprocess_UCC import preprocess

DELETE_TEMP = False


def preprocess_ucc_file(df):
    """
    preprocesses the original highmed cardio data to conform with anonymization requirements
    :return:
    """

    df.fillna("NULL", inplace=True)
    for column in ['age', 'sys_bp_m', 'smoking', 'diabetes', 'copd', 'hf_duration',
                   'hf_gt_18_months', 'mra', 'beta', 'furosemide1', 'statin', 'arni',
                   'acei_arb', 'lvef_m', 'sodium_m', 'creatinine_m', 'hb_m', 'egfr_m', 'ntprobnp_m', 'hstnt_m']:
        try:
            df[column] = np.where(df[column].astype(str).str.endswith(".0"),  # if value ends with .0
                                  df[column].astype(str).str[:-2],  # column without .0
                                  df[column].astype(str))  # normal value
            # df[column] = df[column].astype(str).str.replace(".0","")
            df[column] = df[column].astype(str).str.replace("nan", "NULL")
        except:
            print(f"Preprocessing Problem for columns {column} during anonymization")
    return df


def run_anonymization(anon_input_file, anon_output_file, anon_type:MEDICAL_SCORE):
    """
    Executes a subprocess to anonymize the input file and saves the result in the output file
    :param anon_type:
    :param anon_input_file: filepath to the preprocessed highmed cardio dataset
    :param anon_output_file: filepath to where the anonymized data should be saved to
    """
    if not os.path.isabs(anon_input_file):
        anon_input_file = os.path.join(os.getcwd(), anon_input_file.lstrip("./"))
    if not os.path.isabs(anon_output_file):
        anon_output_file = os.path.join(os.getcwd(), anon_output_file.lstrip("./"))

    jar_location = join(dirname(__file__), 'ucc_anonymization.jar')

    subprocess.run(["java",
                    "-jar", f"{jar_location}",
                    f"--{anon_type.value}",
                    "-i", f"{anon_input_file}",
                    "-o", f"{anon_output_file}"])

    print("Anonymization statistics:")
    print(pd.read_csv(anon_output_file.replace(".csv", "_stats.csv"), sep=";", decimal=","))

    return pd.read_csv(anon_output_file)


def anonymize_ucc_cardio_data(df, temp_file="./temp/anon_input.csv", output_file="./temp/anon_output.csv",
                              anon_type=MEDICAL_SCORE.FULL):
    """
    Method to anonymize the use case cardio dataset using the ucc_anonymization.jar
    :param df: pandas table with the ucc data
    :param temp_file: filepath to a temporary file, that is preprocessed for the anonymization
    :param output_file: filepath to the anonymized use case cardio csv-file
    """

    output_dir = os.path.dirname(os.path.abspath(output_file))
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    temp_data = preprocess_ucc_file(df)
    temp_data.to_csv(temp_file, index=True, sep=",", na_rep='NULL')

    anonymized_data = run_anonymization(temp_file, output_file, anon_type)

    if DELETE_TEMP:
        os.remove(temp_file)
        os.remove(output_file)

    return anonymized_data