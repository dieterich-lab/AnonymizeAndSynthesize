import numpy as np
import pandas as pd
from sklearn.compose import make_column_transformer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder, QuantileTransformer


# Method originally from https://github.com/mostly-ai/paper-fidelity-accuracy
# specifically from https://colab.research.google.com/github/mostly-ai/paper-fidelity-accuracy/blob/main/2023-05/evaluate.ipynb#scrollTo=yYeyS8P7f9U0

def mostly_privacy_metrics(training, holdout, synthetic):
    n_training = training.shape[0]
    n_holdout = holdout.shape[0]
    n_synthetic = synthetic.shape[0]
    print(f"number of records in train, holdout and synthetic: {n_training=}, {n_holdout=}, {n_synthetic=}")

    # numerical columns are transformed to normal distribution and categoricals are hot_encoded
    numeric_cols = training.select_dtypes(include=np.number).columns
    other_cols = training.select_dtypes(exclude=np.number).columns

    # check datasets for nan values in numeric columsn and replace by nanmean of columns
    if any(any(row) for row in np.isnan(training[numeric_cols].values)):
        print("WARNING! Training data contains nan values in numerical columns.")
        training[numeric_cols] = training[numeric_cols].fillna(training[numeric_cols].mean())
        print("For holdout distance analyses, nan values are replaced by column mean.")

    if any(any(row) for row in np.isnan(holdout[numeric_cols].values)):
        print("WARNING! Holdout data contains nan values in numerical columns.")
        holdout[numeric_cols] = holdout[numeric_cols].fillna(holdout[numeric_cols].mean())
        print("For holdout distance analyses, nan values are replaced by column mean.")

    if any(any(row) for row in np.isnan(synthetic[numeric_cols].values)):
        print("WARNING! Synthetic data contains nan values in numerical columns.")
        synthetic[numeric_cols] = synthetic[numeric_cols].fillna(synthetic[numeric_cols].mean())
        print("For holdout distance analyses, nan values are replaced by column mean.")

    transformer = make_column_transformer(
        (OneHotEncoder(handle_unknown="ignore"), other_cols),
        (QuantileTransformer(output_distribution='normal'), numeric_cols),
        remainder="passthrough",
    )

    transformer.fit(pd.concat([training, holdout, synthetic], axis=0))
    training_hot = transformer.transform(training)
    holdout_hot = transformer.transform(holdout)
    synthetic_hot = transformer.transform(synthetic)
    synthetic_hot = np.nan_to_num(synthetic_hot, copy=False)
    synthetic_hot.data[np.isnan(synthetic_hot.data)] = 0

    print('calculate distances to training data')
    index = NearestNeighbors(n_neighbors=1, algorithm="brute", metric="l2", n_jobs=-1)

    index.fit(training_hot)
    dcrs_training, idxs_training = index.kneighbors(synthetic_hot)  # TODO (KO): problems with nan values in this section

    print('calculate distances to holdout data')
    index = NearestNeighbors(n_neighbors=1, algorithm="brute", metric="l2", n_jobs=-1)
    index.fit(holdout_hot)
    dcrs_holdout, idxs_holdout = index.kneighbors(synthetic_hot)

    # normalize
    dcrs_training = np.square(dcrs_training)[:, 0] / 2
    dcrs_holdout = np.square(dcrs_holdout)[:, 0] / 2

    # results
    share = np.mean(dcrs_training < dcrs_holdout) + (n_training / (n_training + n_holdout)) * np.mean(
        dcrs_training == dcrs_holdout)
    ratio = np.maximum(dcrs_training, 1e-20) / np.maximum(dcrs_holdout, 1e-20)
    out = pd.DataFrame({
        'n_training': [n_training],
        'n_holdout': [n_holdout],
        'n_synthetic': [n_synthetic],
        'n_closer': np.sum([dcrs_training < dcrs_holdout]),
        'n_further': np.sum([dcrs_training > dcrs_holdout]),
        'n_equal': np.sum([dcrs_training == dcrs_holdout]),
        'Share': [share],
        'Avg DCR to Training': [np.mean(dcrs_training)],
        'Avg DCR to Holdout': [np.mean(dcrs_holdout)],
        'Median DCR Ratio': np.median(ratio),
    })
    return out

