# Functions ---------------------------------------------------------------

calculate_age <- function(birth_date, ref_date) {
  if(!is.na(birth_date) && !is.na(ref_date)) {
    # Set full date for partial dates
    raw_parts <- str_split(birth_date, pattern = "-")
    parts <- length(raw_parts[[1]])
    
    birth_date_full <- case_when(
      parts == 3 ~ birth_date,
      parts == 2 ~ paste0(birth_date, "-01"),
      parts == 1 ~ paste0(birth_date, "-01-01"),
    )
    
    age <- as.period(interval(as.Date(birth_date_full), ref_date), unit = "year")$year
    return (age)
  }
  return (NA)
}

calculate_age_V <- Vectorize(calculate_age)

calculate_bmi<- function(weight_m, weight_u, height_m, height_u) {
  if (weight_u == "kg" && height_u == "cm" && !is.na(weight_m) && !is.na(height_m)) {
    return (as.numeric(weight_m) / (as.numeric(height_m)/100) ^2)
  }
  return (NA)
}
calculate_bmi_V <- Vectorize(calculate_bmi)

elapsed_months <- function(start_date, ref_date) {
  if(!is.na(start_date) && !is.na(ref_date)) {
    # Set full date for partial dates
    raw_parts <- str_split(start_date, pattern = "-")
    parts <- length(raw_parts[[1]])
    
    start_date_full <- case_when(
      parts == 3 ~ start_date,
      parts == 2 ~ paste0(start_date, "-01"),
      parts == 1 ~ paste0(start_date, "-01-01"),
    )
    
    months <- interval(start_date_full, ref_date) %/% months(1)
    return (months)
  }
  return (NA)
}

elapsed_months_V <- Vectorize(elapsed_months)

format_medication <- function(df_med, df_anam) {
  #join medication with anamnesis to get the date, deduplicate, calculate difference
  df_med2 <- left_join(df_med, df_anam, by="id") %>%
    select(id, time_med, med_code, time) %>%
    unique() %>%
    mutate(difference = abs(difftime(time, time_med, units = "days")),
	  positive = 1 
    )
  
  #transform into a wide format
  df_med3 <- df_med2 %>% 
    spread(key = med_code, value = positive, fill = 0)
  
  #in case we have multiple rows per patient because of incomplete medication, keep only best timedif match
  df_med4 <- df_med3 %>%
    group_by(id) %>%
    slice_min(order_by = difference, with_ties = FALSE) %>%
    select(-difference)
  
  #make sure, that if a medication was never given, we still have the column
  #an empty column will be created,  filled with zeros in that case
  cols <- c(ACEHem = 0, ALDANT = 0, AT1RANT = 0, BETABL = 0, 
            SCHDIU = 0, STAT = 0, `VALS+SACU` = 0)
  df_med5 <- add_column(df_med4, !!!cols[setdiff(names(cols), names(df_med4))])
  
  #Rename and unite columns accordingly
  df_med6 <- df_med5 %>%
    mutate(acei_arb = pmax(ACEHem, AT1RANT)) %>%
    select(-ACEHem, -AT1RANT, -time) %>%
    rename(beta = BETABL, 
           statin = STAT, 
           mra = ALDANT, 
           furosemide1 = SCHDIU, 
           arni = `VALS+SACU`)
  
  return(df_med6)
}

format_labor <- function(df_lab, df_anam){
  df_lab2 <- left_join(df_lab, df_anam, by="id") %>%
    select(id, time.x, code, magnitude, unit, time.y) %>%
    unique() %>%
    mutate(difference = abs(difftime(time.x, time.y, units = "days")),
           magnitude = as.numeric(magnitude) 
    )
  
  #recalculate all lab values according to what loinc code was given
  df_lab3 <- df_lab2 %>% mutate(
    magnitude_processed = case_when(
      code == "2160-0" ~ as.numeric(magnitude) * 88.42, 
      TRUE ~ as.numeric(magnitude)
    ), 
    unit = case_when(
      code == "2160-0" ~ "µmol/l",
      TRUE ~ unit
    ),
    analyt = case_when(
      code == "14682-9" ~ "creatinine",
      code == "2951-2" ~ "sodium",
      code == "718-7" ~ "hb",
      code == "33762-6" ~ "ntprobnp",
      code == "62238-1" ~ "egfr",
      code == "67151-1" ~ "hstnt",
      code == "83107-3" ~ "ntprobnp",
      code == "2160-0" ~ "creatinine",
      code == "30350-3" ~ "hb"
    )
  )
  
  #extract only the minimal difference between anamnesis and lab value
  df_lab4 <- df_lab3 %>%
    group_by(id, analyt) %>%
    slice_min(order_by = difference, with_ties = FALSE) %>%
    mutate(time = time.x) %>%
    select(id, analyt, magnitude_processed, unit, time)
  
  df_lab5 <- df_lab4 %>%
    pivot_wider(id_cols = id, names_from = analyt, values_from = c("magnitude_processed", "unit", "time")) 
  
  #make sure, that even if a value does not even exist for any patient, 
  # the column is still there, but empty
  cols <- c(magnitude_processed_creatinine = NA, unit_creatinine = NA, time_creatinine = NA, 
            magnitude_processed_sodium = NA, unit_sodium = NA, time_sodium = NA,
            magnitude_processed_hb = NA, unit_hb = NA, time_hb = NA,  
            magnitude_processed_egfr = NA, unit_egfr = NA, time_egfr = NA, 
            magnitude_processed_ntprobnp = NA, unit_ntprobnp = NA, time_ntprobnp = NA,
            magnitude_processed_hstnt = NA, unit_hstnt = NA, time_hstnt = NA)
  df_lab6 <- add_column(df_lab5, !!!cols[setdiff(names(cols), names(df_lab5))]) %>%
    #afterwards, rename and reorder columns
    select(id,
           creatinine_m = magnitude_processed_creatinine, 
           creatinine_u = unit_creatinine,
           creatinine_t = time_creatinine, 
           sodium_m = magnitude_processed_sodium,
           sodium_u = unit_sodium,
           sodium_t = time_sodium,
           hb_m = magnitude_processed_hb, 
           hb_u = unit_hb,
           hb_t = time_hb,  
           egfr_m = magnitude_processed_egfr, 
           egfr_u = unit_egfr,
           egfr_t = time_egfr, 
           ntprobnp_m = magnitude_processed_ntprobnp, 
           ntprobnp_u = unit_ntprobnp,
           ntprobnp_t = time_ntprobnp,
           hstnt_m = magnitude_processed_hstnt, 
           hstnt_u = unit_hstnt,
           hstnt_t = time_hstnt)
  
  return(df_lab6)
}

format_echo <- function(df_echo, df_anam) {
  #join echo with anamnesis to get the date, deduplicate, calculate difference
  df_echo2 <- left_join(df_echo, df_anam, by="id") %>%
    select(id, time.x, lvef_m, lvef_u, time.y) %>%
    unique() %>%
    mutate(difference = abs(difftime(time.x, time.y, units = "days")),
           lvef_m = as.numeric(lvef_m) 
    )
  
  #extract only the minimal difference between anamnesis and echo
  df_echo3 <- df_echo2 %>%
    group_by(id) %>%
    slice_min(order_by = difference, with_ties = FALSE) %>%
    select(id, lvef_t = time.x, lvef_m, lvef_u)
  
  return(df_echo3)
}  


extend_aql <- function(aql, id_path = NULL, ids = NULL)
{
  if(!is.null(ids))
  {
    where_clause <- paste(id_path, "MATCHES {'", paste(ids, collapse = "','"), "'} LIMIT 100000 OFFSET 0", sep=" ")
    if (str_detect(aql, 'WHERE'))
    {
      return(paste(aql, "AND", where_clause, sep = " "))
    }
    return(paste(aql, "WHERE", where_clause, sep = " "))
  }
  return(aql)
}

execute_query <- function(url, username, password, aql, id_path = NULL, ids = NULL)
{
  r <-  POST(paste0(url, "/query/aql"), body = list(q = extend_aql(aql, id_path, ids)), encode = "json", #add verbose(), for debugging
             authenticate(username, password, type = "basic"))
  
  if (status_code(r) == 200)
  {
    df <- as.data.frame(fromJSON(content(r, "text"))$rows) 
    if (nrow(df) > 0)
    {
      colnames(df) <- fromJSON(content(r, "text"))$columns$name
      return(df)
    }
    warning(paste0("The AQL query returned an empty resultSet."))
    return(data.frame())
  }
  warning(paste0("Error while executing AQL query: HTTP status code ", status_code(r)))
  return(data.frame())   
}

execute_query_stepwise <- function(url, username, password, aql, id_path, ids, n)
{
  df <- data.frame()
  count_ids <- length(ids)

  for (i in seq(1, count_ids, n))
  {
    from <- i
    to <- ifelse(i + (n-1) < count_ids, i + (n-1), count_ids)
    df_part <- execute_query(url, username, password, aql, id_path, ids[from:to])
    df <- rbind(df, df_part)
  }
  return(df)
}
