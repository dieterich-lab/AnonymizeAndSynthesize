from enum import Enum

import os
from pathlib import Path
import pandas
import numpy
import matplotlib
import matplotlib.pyplot as pyplot
import seaborn
import re
import magic
import rpy2.robjects as robj


seaborn.set(rc={'axes.facecolor': 'lightgrey'})


class MEDICAL_SCORE(Enum):
    BIOHF = "BIOHF"
    MAGGIC = "MAGGIC"
    FULL = "FULL"


def get_attributes(risk_score: MEDICAL_SCORE):
    return FEATURE_SETS[risk_score]["all"]


FEATURE_SETS = {MEDICAL_SCORE.BIOHF:
                    {'continuous': ['age', 'lvef_m', 'sodium_m', 'hb_m', 'egfr_m', 'biohf_v1_1', 'biohf_v1_3'],
                     'categorical': ['gender', 'nyha', 'beta', 'furosemide1', 'statin', 'acei_arb'],
                     'all': ['age', 'lvef_m', 'sodium_m', 'hb_m', 'gender', 'nyha', 'beta', 'furosemide1',
                             'statin', 'acei_arb', 'egfr_m']},
                MEDICAL_SCORE.MAGGIC:
                    {'continuous': ['age', 'bmi', 'sys_bp_m', 'lvef_m', 'creatinine_m', 'maggic_score_1',
                                    'maggic_score_3'],
                     'categorical': ['gender', 'nyha', 'smoking', 'diabetes', 'copd', 'hf_gt_18_months', 'beta',
                                     'acei_arb'],
                     'all': ['age', 'bmi', 'sys_bp_m', 'lvef_m', 'creatinine_m', 'gender', 'nyha', 'smoking',
                             'diabetes', 'copd', 'hf_gt_18_months', 'beta', 'acei_arb']}}


# input csv and/or xls(x)
def read_data(datafile, **kwargs):
    filetype = magic.from_file(datafile)
    if re.compile(".*Excel.*").match(filetype):
        return pandas.read_excel(datafile, **kwargs)
    elif re.compile(".*CSV.*").match(filetype):
        return pandas.read_csv(datafile, **kwargs)
    elif re.compile(".*UTF-8.*").match(filetype):
        return pandas.read_csv(datafile, **kwargs)
    elif re.compile(".*ASCII.*").match(filetype):
        return pandas.read_csv(datafile, **kwargs)
    else:
        Warning(f'Could not read data file {datafile}!  Not in CSV or Excel format.')
        return None


def qqplot(ground_truth, y, numquant=None, ax=None, title='', ylabel='', save_to='qq-plot.png'):
    'Quantile-quantile plot for two empirical distributions.'
    pyplot.clf()
    if ax is None:
        ax = pyplot.gca()
    xx = ground_truth.dropna().to_numpy()
    yy = y.dropna().to_numpy()
    if numquant is None:
        numquant = min(len(xx), len(yy))
    x_1 = numpy.quantile(xx, numpy.linspace(0, 1, numquant))
    y_1 = numpy.quantile(yy, numpy.linspace(0, 1, numquant))
    ax.plot(numpy.sort(x_1), numpy.sort(y_1), ls='-')

    # add the red diagonal:
    pyplot.axline([0, 0], slope=1, color='r', ls='-')

    ax.set_xlabel('Ground Truth')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    pyplot.savefig(save_to)
    return ax


def ecdf_values(value_list):
    x_ecdf = numpy.sort(value_list)
    y_ecdf = numpy.arange(1, len(value_list) + 1) / len(value_list)
    return x_ecdf, y_ecdf


def ecdf_plot(orig, anon, synth, xlabel='', save_to='ecdf_plot.png'):
    x_orig, y_orig = ecdf_values(orig.dropna().to_numpy())
    x_anon, y_anon = ecdf_values(anon.dropna().to_numpy())
    x_synth, y_synth = ecdf_values(synth.dropna().to_numpy())

    pyplot.clf()
    _, ax = pyplot.subplots()

    ax.plot(x_orig, y_orig, ls='solid', label='Original')
    ax.plot(x_anon, y_anon, ls='solid', label='ARX anonymized')
    ax.plot(x_synth, y_synth, ls='solid', label='ASyH synthesized')

    ax.legend()

    pyplot.xlabel(xlabel)
    pyplot.ylabel(f'ECD({xlabel})')

    pyplot.savefig(save_to)

    return ax


def violin_plots(anon, orig, synth, plot_parm, save_to='violin_plots.png'):
    pyplot.clf()
    ax = pyplot.gca()
    datalist = [anon, orig, synth]
    ax.violinplot(datalist,
                  widths=0.85,
                  showmeans=False,
                  showmedians=False,
                  showextrema=False)
    ax.boxplot(datalist, widths=0.15, showcaps=False)
    ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator([1, 2, 3]))
    ax.set_ylabel(plot_parm)
    labels = ['Anonymized', 'Original', 'Synthesized']
    ax.set_xticklabels(labels)

    pyplot.savefig(save_to)

    return ax


R_SCRIPT_PATH = os.path.dirname(__file__)

def pca_plot_R(orig_file, synth_file, output_image, score_name):
    """Python wrapper for the R script used to produce PCA 2-d projections.
    This function expects the ORIG_FILE to contain as many data records as
    SYNTH_FILE, which contains the synthetic data to compare to.

    The R script will split continuous and categorical data according to
    FEATURE_SETS, convert any non-boolean columns to one-hot, re-centre the
    data, execute the PCA and project the data records onto the plane of the two
    largest principal components.

    This script is not integrated into any pipeline, but provided for
    completeness of methods used in the publication (cf. figs. S1 and S2,
    supplementary document).

    """
    cwd = os.getcwd()

    # creating any temporary directory
    output_file = os.path.abspath(output_image)
    output_dir = os.path.dirname(output_file)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    robj.r['source'](rf'{R_SCRIPT_PATH}/pca_projections.R')
    r_pca_projection = robj.globalenv['pca_projection']
    r_pca_projection(orig_file,
                     synth_file,
                     output_image,
                     cwd,
                     str(score_name),
                     FEATURE_SETS[score_name]['all'],
                     FEATURE_SETS[score_name]['categorical'])
