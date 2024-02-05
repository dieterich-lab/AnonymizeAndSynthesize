#!/usr/bin/env python3
"""Preprocess UCC data by plausibility"""
from argparse import ArgumentParser

import pandas
import numpy


def drop_column_cleanup(dataset, unused_columns=['Unnamed: 0', 'X']):
    return dataset.drop(columns=unused_columns, errors='ignore')


def drop_unused_columns(dataset, unused_columns=['Unnamed: 0', 'ntprobnp_m', 'ntprobnp_u', 'hstnt_m', 'hstnt_u']):
    return dataset.drop(columns=unused_columns, errors='ignore')


def drop_score_columns(dataset, unused_columns=['biohf_v1_1', 'biohf_v1_3', 'maggic_score_1', 'maggic_score_3']):
    return dataset.drop(columns=unused_columns, errors='ignore')


# helper 'macro'
def cond(key, minval, maxval, do_round=False):
    def filter_cond(indict):
        outdict = indict.copy()
        if do_round and not numpy.isnan(outdict[key]):
            outdict[key] = round(outdict[key], 8)
        if outdict[key] < minval or outdict[key] > maxval:
            outdict[key] = numpy.nan
        return outdict

    return filter_cond


def cond_months_age(key, minval, maxval):
    def filter_cond(indict):
        outdict = indict.copy()
        if outdict[key] < minval * outdict['age'] or outdict[key] > maxval * outdict['age']:
            outdict[key] = numpy.nan
        return outdict

    return filter_cond


limiters = [cond('age', 18, 110, False),
            cond('bmi', 14, 60, True),
            cond('sys_bp_m', 70, 250, False),
            cond_months_age('hf_duration', 0, 12),
            cond('lvef_m', 4, 85, False),
            cond('creatinine_m', 26.526, 1326.3, False),
            cond('sodium_m', 120, 150, False),
            cond('hb_m', 5, 20, False),
            cond('egfr_m', 5, 120, False)
            ]


# for logging any chaged rows:
def check_dicts(a, b):
    if a != b:
        print(f'data outside limits: changed\n  {a}\nto\n  {b}')


# get data
def preprocess(dataset, verbose=False):
    in_data = dataset.drop('Unnamed: 0', axis=1, errors="ignore")
    cleared_data = pandas.DataFrame()

    for row in in_data.to_dict(orient='records'):
        r = row
        for lim in limiters:
            r = lim(r)
            if verbose:
                check_dicts(row, r)
        rdf = pandas.DataFrame(r, index=[0])
        cleared_data = pandas.concat([cleared_data, rdf])

    cleared_data.reset_index()
    return cleared_data
