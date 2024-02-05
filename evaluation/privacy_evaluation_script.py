# please run pip install git+https://github.com/alan-turing-institute/privacy-sdg-toolbox first
import os
from argparse import ArgumentParser

import pandas as pd
from anonymeter.evaluators import LinkabilityEvaluator, InferenceEvaluator, SinglingOutEvaluator

from evaluation.local_utils import read_data
from evaluation.privacy_metrics import mostly_privacy_metrics


def run_anonymeter_linkability(data_origin, data_processed, data_control, aux_columns):

    n_attacks = len(data_processed.index)

    evaluator = LinkabilityEvaluator(ori=data_origin,
                                     syn=data_processed,
                                     control=data_control,
                                     n_attacks=400,
                                     aux_cols=aux_columns,
                                     n_neighbors=10)

    evaluator.evaluate(n_jobs=-2)

    risk = evaluator.risk(confidence_level=0.95)
    results = evaluator.results()
    results_df = pd.DataFrame()
    results_df["attack_rate success_rate"] = pd.Series(results.attack_rate.value)
    results_df["attack_rate error"] = pd.Series(results.attack_rate.error)
    results_df["baseline_rate success_rate"] = pd.Series(results.baseline_rate.value)
    results_df["baseline_rate error"] = pd.Series(results.baseline_rate.error)
    results_df["control_rate success_rate"] = pd.Series(results.control_rate.value)
    results_df["control_rate error"] = pd.Series(results.control_rate.error)
    results_df["n_attacks"] = pd.Series(results.n_attacks)
    results_df["n_baseline"] = pd.Series(results.n_baseline)
    results_df["n_control"] = pd.Series(results.n_control)
    results_df["n_success"] = pd.Series(results.n_success)
    results_df["priv_risk"] = pd.Series(risk.value)
    results_df["priv_risk_ci"] = pd.Series(risk.ci)
    results_df["can_be_used"] = results_df["baseline_rate success_rate"] < results_df["attack_rate success_rate"]
    return results_df.transpose()

def run_anonymeter_attribute_inference(data_origin, data_processed, data_control):
    columns = list(set(data_origin.columns).intersection(data_processed.columns))
    results = []
    risks = []

    n_attacks = len(data_processed.index)

    for secret in columns:
        aux_cols = [col for col in columns if col != secret]

        evaluator = InferenceEvaluator(ori=data_origin,
                                       syn=data_processed,
                                       control=data_control,
                                       aux_cols=aux_cols,
                                       secret=secret,
                                       n_attacks=400)
        evaluator.evaluate(n_jobs=-2)
        results.append((secret, evaluator.results()))
        risks.append((secret, evaluator.risk()))

    pattern = '|'.join(["SuccessRate(value=","error=", ")"])

    results_df = pd.DataFrame({k: __to_series(v, "inference") for k, v in dict(results).items()}).add_prefix("inference_")
    results_df = results_df.transpose()
    results_df[["attack_rate success_rate", "attack_rate error"]] = pd.DataFrame(results_df['attack_rate'].tolist(), index=results_df.index)
    results_df[["baseline_rate success_rate", "baseline_rate error"]] = pd.DataFrame(results_df['baseline_rate'].tolist(), index=results_df.index)
    results_df[["control_rate success_rate", "control_rate error"]] = pd.DataFrame(results_df['control_rate'].tolist(), index=results_df.index)
    results_df.drop(["attack_rate", "baseline_rate", "control_rate"], inplace=True, axis=1)

    risks_df = pd.DataFrame({k: v for k, v in dict(risks).items()}).add_prefix(
        "inference_")
    risks_df.index = ["priv_risk","priv_risk_ci"]
    risks_df = risks_df.transpose()
    results_df[["priv_risk","priv_risk_ci"]] = risks_df[["priv_risk","priv_risk_ci"]]

    results_df["can_be_used"] = results_df["baseline_rate success_rate"] < results_df["attack_rate success_rate"]

    return results_df.transpose()

def run_anonymeter_singlingout(data_origin, data_processed, data_control, mode="univariate"):

    n_attacks = len(data_processed.index)

    evaluator = SinglingOutEvaluator(ori=data_origin,
                                     syn=data_processed,
                                     control=data_control,
                                     n_attacks=400)
    evaluator.evaluate(mode=mode)

    risk = evaluator.risk(confidence_level=0.95)

    results = evaluator.results()
    results_df = pd.DataFrame()
    results_df["attack_rate success_rate"] = pd.Series(results.attack_rate.value)
    results_df["attack_rate error"] = pd.Series(results.attack_rate.error)
    results_df["baseline_rate success_rate"] = pd.Series(results.baseline_rate.value)
    results_df["baseline_rate error"] = pd.Series(results.baseline_rate.error)
    results_df["control_rate success_rate"] = pd.Series(results.control_rate.value)
    results_df["control_rate error"] = pd.Series(results.control_rate.error)
    results_df["n_attacks"] = pd.Series(results.n_attacks)
    results_df["n_baseline"] = pd.Series(results.n_baseline)
    results_df["n_control"] = pd.Series(results.n_control)
    results_df["n_success"] = pd.Series(results.n_success)
    results_df["priv_risk"] = pd.Series(risk.value)
    results_df["priv_risk_ci"] = pd.Series(risk.ci)
    results_df["can_be_used"] = results_df["baseline_rate success_rate"] < results_df["attack_rate success_rate"]
    return results_df.transpose()

def __to_series(class_object, name = 0):
    series = pd.Series(class_object.__dict__, name=name)
    return series


def __format_results(res_Link, res_Inf, res_SO_uni, res_SO_multi, priv_mostly):
    results = res_Inf
    results.insert(0, "inference average", results.transpose().mean(skipna=True).transpose())
    results.insert(0, "linkage", res_Link[0])

    results.insert(1, "singling out_univariate", res_SO_uni[0])
    results.insert(2, "singling out_multivariate", res_SO_multi[0])

    holdout_res = priv_mostly.loc[0]
    return results.transpose(), holdout_res



def anonymeter_evaluation(data_origin, data_processed, data_control):

    available_columns = ['lvef_m', 'creatinine_m', 'sodium_m', 'hb_m', 'egfr_m']
    unavailable_columns = ['age', 'bmi', 'diabetes', 'copd', 'gender']

    shared_columns = list(set.intersection(*[set(x) for x in [data_origin.columns, data_processed.columns,
                                                              data_control.columns]]))

    available_columns = [x for x in available_columns if x in shared_columns]
    unavailable_columns = [x for x in unavailable_columns if x in shared_columns]

    aux_columns = [
        available_columns,  # available/leaked columns (laboratory results
        unavailable_columns # private/interesting columns (demographic data)
    ]

    res_Link = run_anonymeter_linkability(data_origin, data_processed, data_control, aux_columns)
    res_Inf = run_anonymeter_attribute_inference(data_origin, data_processed, data_control)
    res_SO_uni = run_anonymeter_singlingout(data_origin, data_processed, data_control, "univariate")
    res_SO_multi = run_anonymeter_singlingout(data_origin, data_processed, data_control, "multivariate")

    train_mask = data_origin["alias"].isin(data_control["alias"])
    data_train = data_origin.loc[~train_mask]
    priv_mostly = mostly_privacy_metrics(data_train, data_control, data_processed)
    return __format_results(res_Link, res_Inf, res_SO_uni, res_SO_multi, priv_mostly)

