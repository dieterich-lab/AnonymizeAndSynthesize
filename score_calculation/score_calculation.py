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
from argparse import ArgumentParser

import pandas as pd
import rpy2.robjects as robj
import os
from pathlib import Path

R_SCRIPT_PATH = os.path.dirname(__file__)
DELETE_TEMP = False


def calculate_scores(dataset, temp_file="temp/without_score.csv", output_file="temp/with_score.csv"):
    temp_cwd = os.getcwd()
    temp_file = os.path.abspath(temp_file)
    output_file = os.path.abspath(output_file)

    output_dir = os.path.dirname(output_file)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    dataset.to_csv(temp_file)
    robj.r['source'](rf"{R_SCRIPT_PATH}/scores_anon.R")
    r_score = robj.globalenv['score_calculation']
    r_score(temp_file, output_file, R_SCRIPT_PATH)
    if DELETE_TEMP:
        os.remove(temp_file)
        os.remove(output_file)

    os.chdir(temp_cwd)
    return pd.read_csv(output_file)
