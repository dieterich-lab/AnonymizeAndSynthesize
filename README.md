# Arx-ASyH-Comparison
Code accompanying the publication "Anonymize or Synthesize? - Privacy-Preserving Methods for Heart Failure Score Analytics", used for comparing current anonymization techniques with recent AI-driven data synthetisation algorithms, and combining the two methods to produce double-processed privacy preserving datasets.

## Requirements
- python 3.10
- R, Version >= 4.3.0
- JDK 17
- ASyH 1.0.0

## Installation
1. Create a virtual environment and install the necessary python packages according to the requirement documents
2. Under Windows: Remove the `python-magic` package and make sure `python-magic-bin` is installed
3. Activate the virtual environment and install the required R packages by using `Rscript Install_R_packages.R`. 
Make sure R_HOME environment variable is set to the R root folder.

## Usage
Go to the top directory of the cloned AnonymizeAndSynthesize copy, create a subdirectory ```data``` and add the original Dataset to anonymize/synthesize as ```data/UCC_heart_data.csv```.


### Data Generation and Utility Analysis
With the basis dataset in place and being in the top directory of the cloned copy, issue the following command:

    python3 ./script_utility_analysis.py --input_original data/UCC_heart_data.csv --output <output_directory>

replace <output_directory> with the path to which you want to have the output files written.
This will produce an anonymized, a synthetic, and a synthesized anonymized dataset for MAGGIC and BioHF separately, and will create fidelity and utility analysis data, comparing ecdf plots and violin plots of the data distributions of all datasets.


#### File System Structure of Output

    <output_directory>/BioHF/<date>_comparison_statistics_BIOHF_cat.csv
    <output_directory>/BioHF/<date>_comparison_statistics_BIOHF_cont.csv
    <output_directory>/BioHF/<date>_ecdf_orig_anon_synth-biohf_v1_1.eps
    <output_directory>/BioHF/<date>_violin_anon_orig_synth-biohf_v1_1.eps
    <output_directory>/MAGGIC/<date>_comparison_statistics_MAGGIC_cat.csv
    <output_directory>/MAGGIC/<date>_ecdf_orig_anon_synth-maggic_score_1.eps
    <output_directory>/MAGGIC/<date>_comparison_statistics_MAGGIC_cont.csv
    <output_directory>/MAGGIC/<date>_violin_anon_orig_synth-maggic_score_1.eps

### Data Generation and Re-Identification Risk Analysis

For a risk analysis, analogue to the Utility Analysis script, when in the cloned AnonymizeAndSynthesize copy's top directory, you can run

    python3 ./script_risk_analysis.py --input_original data/UCC_heart_data.csv --output <output_directory>

(again, adjust the \<output_directory\> argument).

The risk analysis data can be found under

    <output_directory>/BioHF/Risk Assessment/<date>_UCC_heart_data_control_combined.csv
    <output_directory>/BioHF/Risk Assessment/<date>_UCC_heart_data_training_combined.csv
    <output_directory>/BioHF/Risk Assessment/<date>_UCC_heart_data_control.csv
    <output_directory>/BioHF/Risk Assessment/<date>_UCC_heart_data_training.csv
    <output_directory>/BioHF/Risk Assessment/<date>_UCC_heart_data_train_anonymized.csv
    <output_directory>/BioHF/Risk Assessment/<date>_UCC_heart_data_train_synthetic.csv
    <output_directory>/MAGGIC/risk/<date>_UCC_heart_data_control_combined.csv
    <output_directory>/MAGGIC/risk/<date>_UCC_heart_data_training_combined.csv
    <output_directory>/MAGGIC/risk/<date>_UCC_heart_data_control.csv
    <output_directory>/MAGGIC/risk/<date>_UCC_heart_data_training.csv
    <output_directory>/MAGGIC/risk/<date>_UCC_heart_data_train_anonymized.csv
    <output_directory>/MAGGIC/risk/<date>_UCC_heart_data_train_synthetic.csv

## Input Dataset Layout
   The following columns are mandatory for the input data csv file to be processed for both MAGGIC and BioHF scores:
   | variable | type |
   | -------- | ---- |
   | "age" | numerical |
   | "gender" | [m \| f \| N/A ]
   | "bmi" | numerical |
   | "sys_bp_m" | numerical
   | "nyha" | [ I \| II \| III \| IV \| N/A ]|
   | "smoking" | [ 0. \| 1. \| N/A ] |
   | "diabetes" | [ 0. \| 1. \| N/A ] |
   | "copd" | [ 0. \| 1. \| N/A ] |
   | "hf_duration" | numerical |
   | "hf_gt_18_months" | [ 0. \| 1. \| N/A ] |
   | "mra" | [ 0. \| 1. \| N/A ] |
   | "beta" | [ 0. \| 1. \| N/A ] |
   | "furosemide1" | [ 0. \| 1. \| N/A ] |
   | "statin" | [ 0. \| 1. \| N/A ] |
   | "arni" | [ 0. \| 1. \| N/A ] |
   | "acei_arb" | [ 0. \| 1. \| N/A ] |
   | "lvef_m" | numerical |
   | "creatinine_m" | numerical |
   | "sodium_m" | numerical |
   | "hb_m" | numerical |
   | "egfr_m" | numerical |
   | "ntprobnp_m" | numerical |
   | "hstnt_m" | numerical |
