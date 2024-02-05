###########################################



# HiGHmed UCC - Herzinsuffzienz Scores



##########################################

# Beim ersten Ausf?hren bitte Pakete ?ber "renv::restore()" installieren.
#
# Die Pakete (inkl. Version) werden in renv.lock definiert und beim Ausf?hren von
# "renv::restore()" automatisch lokal unter renv/library installiert.

rm(list = ls())
suppressPackageStartupMessages({
    # library(HiGHmedUCCScores)
    library(dplyr)
    library(stringr)
    library(lubridate)
    library(tidyr)
    library(tibble)
    library(httr)
    library(jsonlite)
    library(readr)
})



score_calculation <- function(input_file, output_file, cwd) {
    setwd(cwd)
    source("./scores_functions.R")
    source("./HiGHmedUCCScores/R/ucc_bcn_biohf_score_v1.R")
    source("./HiGHmedUCCScores/R/ucc_maggic_score.R")
    list_variables <- mget(load("./HiGHmedUCCScores/data/bcn_hf_score_settings.RData"))
    list2env(list_variables, .GlobalEnv)
    list_variables <- mget(load("./HiGHmedUCCScores/data/maggic_score_settings.RData"))
    list2env(list_variables, .GlobalEnv)

    resultSet <- read.csv(input_file)

    resultSet[resultSet == "*"] <- NA
    resultSet[resultSet == "NULL"] <- NA

    # Calculate Scores

    resultSet <- resultSet %>% mutate(
          gender_m = case_when(
            gender == "f" ~ 0,
            gender == "m" ~ 1),
          gender_f = case_when(
            gender == "f" ~ 1,
            gender == "m" ~ 0),
          )

     resultSet <- resultSet  %>% mutate(
       maggic_score_1 = calc_maggic_score(
         target_param = "1_year_mort",
         age = age,
         lv_ef = lvef_m,
         sys_bp = sys_bp_m,
         bmi = bmi,
         creatinine = creatinine_m,
         nyha = nyha,
         gender_m = gender_m,
         smoking = smoking,
         diabetes = diabetes,
         copd = copd,
         hf_gt_18_months = hf_gt_18_months,
         betablock = beta,
         acei_arb = acei_arb
       )
     )  %>% mutate(
       maggic_score_3 = calc_maggic_score(
         target_param = "3_year_mort",
         age = age,
         lv_ef = lvef_m,
         sys_bp = sys_bp_m,
         bmi = bmi,
         creatinine = creatinine_m,
         nyha = nyha,
         gender_m = gender_m,
         smoking = smoking,
         diabetes = diabetes,
         copd = copd,
         hf_gt_18_months = hf_gt_18_months,
         betablock = beta,
         acei_arb = acei_arb
       )
     )#  %>% mutate(
    #   maggic_score_points = calc_maggic_score(
    #     target_param = "points",
    #     age = age,
    #     lv_ef = lvef_m,
    #     sys_bp = sys_bp_m,
    #     bmi = bmi,
    #     creatinine = creatinine_m,
    #     nyha = nyha,
    #     gender_m = gender_m,
    #     smoking = smoking,
    #     diabetes = diabetes,
    #     copd = copd,
    #     hf_gt_18_months = hf_gt_18_months,
    #     betablock = beta,
    #     acei_arb = acei_arb
    #   )
    # )


    resultSet <- resultSet %>% mutate(
      biohf_v1_1 = calc_bcn_biohf_v1(
        target_param = "1_year_mort",
        selected_model="model1",
        age = age,
        gender_f = gender_f,
        nyha = nyha,
        lv_ef = lvef_m,
        sodium = sodium_m,
        egfr = egfr_m,
        hb = hb_m,
        # hstnt = hstnt_m,
        furosemide1 = furosemide1,
        statin = statin,
        acei_arb = acei_arb,
        betablock = beta,
        # ntprobnp = ntprobnp_m
      )
    ) %>% mutate(
      biohf_v1_3 = calc_bcn_biohf_v1(
        target_param = "3_year_mort",
        selected_model="model1",
        age = age,
        gender_f = gender_f,
        nyha = nyha,
        lv_ef = lvef_m,
        sodium = sodium_m,
        egfr = egfr_m,
        hb = hb_m,
        # hstnt = hstnt_m,
        furosemide1 = furosemide1,
        statin = statin,
        acei_arb = acei_arb,
        betablock = beta,
        # ntprobnp = ntprobnp_m
      )
    )


    # Export Results ----------------------------------------------------------

    out <- resultSet[, !(names(resultSet) %in% c('seq'))]
    write.csv(out, output_file)
}
