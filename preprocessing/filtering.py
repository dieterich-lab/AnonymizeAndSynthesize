#!/usr/bin/env python3
"""Preprocess UCC data by plausibility"""
from argparse import ArgumentParser

import pandas as pd

from evaluation.local_utils import MEDICAL_SCORE, FEATURE_SETS


def select_score_subsample(full_dataset_cleaned: pd.DataFrame,
                           medical_score: MEDICAL_SCORE) -> pd.DataFrame:
    match medical_score:
        case MEDICAL_SCORE.BIOHF:
            return filter_for_biohf(full_dataset_cleaned)
        case MEDICAL_SCORE.MAGGIC:
            return filter_for_maggic(full_dataset_cleaned)
    return None


def filter_for_biohf(dataset: pd.DataFrame):
    required_columns = FEATURE_SETS[MEDICAL_SCORE.BIOHF]["all"]
    return dataset.dropna(subset=required_columns)


def filter_for_maggic(dataset: pd.DataFrame):
    required_columns = FEATURE_SETS[MEDICAL_SCORE.MAGGIC]["all"]
    return dataset.dropna(subset=required_columns)
