# ASyH scripts

These are the scripts with which the synthetic dataset was produced. To successfully
execute them the following preconditions must be met, e.g. in a dedicated Python venv:

* The requirements in requirements.txt or requirements-windows.txt from the parent
  directory must be installed. On systems where a libmagic is easily available, 
  most likely everything but Windows, the first one will do:

        pip install -r requirements.txt

* The ASyH software is installed (git@github.com:dieterich-lab/ASyH.git), e.g.:

        cd ..
        git clone git@github.com:dieterich-lab/ASyH.git
        cd ASyH
        pip install .
        cd ../ARX-ASyH-Comparison

* In the working directory the raw data are available in "UCC_heart_data.csv".
* In the working directory a copy of "metadata.json" from this directory is present.

The scripts are:

* 1-preprocess_UCC.py  
A script to take out values outside the plausible data range for the variables `age`, `bmi`, `sys_bp_m`, `hf_duration`, `lvef_m`, `creatinine_m`, `sodium_m`, `hb_m`, and `egfr_m`, according to Table 3 of [1].

* 2-train+sample+report.py  
Train the four ASyH models (SDV synthesizers) and sample a synthetic dataset with the best scoring synthesizer.  Produce a report MarkDown document with plots of the similarity score details.  This MarkDown document can be translated to a PDF document.  There will also be a CSV file with the numerical similarity score details.

* 3-run-GCM-distribution-variation.py
After it turned out that the GaussianCopula was the best scoring synthesizer, we found that the GaussianCopulaSynthesizer can be tuned by using different distributions to fit the single variable distributions, picking the best fitting distributions for each variable.  This script takes each available fitting distribution, fits each variable with them and scores by similarity with the original variable distribution.  We then manually pick the best scoring fitting distribution for each variable and specify these in the next script as argument 'numerical_distributions':

* 4-run-GCM-specific-numerical-distributions.py  
This produced the result presented.

[1] Sommer KK, Amr A, Bavendiek U, Beierle F, Brunecker P, Dathe H, Eils J, Ertl M, Fette G, Gietzelt M, Heidecker B, Hellenkamp K, Heuschmann P, Hoos JDE, Kesztyüs T, Kerwagen F, Kindermann A, Krefting D, Landmesser U, Marschollek M, Meder B, Merzweiler A, Prasser F, Pryss R, Richter J, Schneider P, Störk S, Dieterich C. Structured, Harmonized, and Interoperable Integration of Clinical Routine Data to Compute Heart Failure Risk Scores. Life (Basel). 2022 May 18;12(5):749. doi: 10.3390/life12050749. PMID: 35629415; PMCID: PMC9147139.
