# /**
#  * Use Case Cardiology HiGHmed Data Anonymisation
#  * Copyright (C) 2024 - Berlin Institute of Health
#  * <p>
#  * Licensed under the Academic Free License v3.0;
#  * you may not use this file except in compliance with the License.
#  * You may obtain a copy of the License at
#  * <p>
#  * https://license.md/licenses/academic-free-license-v3-0/
#  * <p>
#  * Unless required by applicable law or agreed to in writing, software
#  * distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.
#  */
#
#  """Preprocess UCC data by plausibility"""
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
