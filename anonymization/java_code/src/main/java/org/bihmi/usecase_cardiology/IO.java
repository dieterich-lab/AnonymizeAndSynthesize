/**
 * Use Case Cardiology HiGHmed Data Anonymisation
 * Copyright (C) 2023 - Berlin Institute of Health
 * <p>
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * http://www.apache.org/licenses/LICENSE-2.0
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.bihmi.usecase_cardiology;

import org.deidentifier.arx.Data;
import org.deidentifier.arx.DataHandle;
import org.deidentifier.arx.DataSource;
import org.deidentifier.arx.DataType;
import org.deidentifier.arx.io.CSVDataOutput;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Set;

/**
 * Data loading, code was adapted from: <a href="https://github.com/BIH-MI/leoss-puf">LEOSS Repository</a>
 * @author Fabian Prasser
 * @author Karen Otte
 */
public class IO {

    private static final String lineSeparator = System.lineSeparator();

    /** Final field */
    public static final String FIELD_INDEX                                = "";
    /** Final field */
    public static final String FIELD_ALIAS                                = "alias";
    /** Final field */
    public static final String FIELD_SITE                             = "site";
    /** Final field */
    public static final String FIELD_AGE                    = "age";
    /** Final field */
    public static final String FIELD_GENDER                     = "gender";
    /** Final field */
    public static final String FIELD_TREATMENT                = "treatment";
    /** Final field */
    public static final String FIELD_BMI                  = "bmi";
    /** Final field */
    public static final String FIELD_SYS_BLOODPREASURE_MEASURE                     = "sys_bp_m";
    /** Final field */
    public static final String FIELD_SYS_BLOODPREASURE_UNIT                     = "sys_bp_u";
    /** Final field */
    public static final String FIELD_NYHA                     = "nyha";
    /** Final field */
    public static final String FIELD_SMOKING                     = "smoking";
    /** Final field */
    public static final String FIELD_DIABETES                  = "diabetes";
    /** Final field */
    public static final String FIELD_COPD    = "copd";
    /** Final field */
    public static final String FIELD_HEARTFAILURE_DURATION      = "hf_duration";
    /** Final field */
    public static final String FIELD_HEARTFAILURE_LONGER_18MONTH        = "hf_gt_18_months";
    /** Final field */
    public static final String FIELD_MRA = "mra";
    /** Final field */
    public static final String FIELD_BETA   = "beta";
    /** Final field */
    public static final String FIELD_FUROSEMIDE1     = "furosemide1";
    /** Final field */
    public static final String FIELD_STATIN            = "statin";
    /** Final field */
    public static final String FIELD_ARNI            = "arni";
    /** Final field */
    public static final String FIELD_ACEI_ARB            = "acei_arb";
    /** Final field */
    public static final String FIELD_LVEF_MEASURE            = "lvef_m";
    /** Final field */
    public static final String FIELD_LVEF_UNIT            = "lvef_u";
    /** Final field */
    public static final String FIELD_CREATININE_MEASURE            = "creatinine_m";
    /** Final field */
    public static final String FIELD_CREATININE_UNIT            = "creatinine_u";
    /** Final field */
    public static final String FIELD_SODIUM_MEASURE            = "sodium_m";
    /** Final field */
    public static final String FIELD_SODIUM_UNIT            = "sodium_u";
    /** Final field */
    public static final String FIELD_HB_MEASURE            = "hb_m";
    /** Final field */
    public static final String FIELD_HB_UNIT            = "hb_u";
    /** Final field */
    public static final String FIELD_EGFR_MEASURE            = "egfr_m";
    /** Final field */
    public static final String FIELD_EGFR_UNIT            = "egfr_u";
    /** Final field */
    public static final String FIELD_NTPROBNP_MEASURE            = "ntprobnp_m";
    /** Final field */
    public static final String FIELD_NTPROBNP_UNIT            = "ntprobnp_u";
    /** Final field */
    public static final String FIELD_HSTNT_MEASURE            = "hstnt_m";
    /** Final field */
    public static final String FIELD_HSTNT_UNIT            = "hstnt_u";

    /**
     * File loading
     * @param inputFile File Handle for the input data
     * @return loaded data file as Data Object
     * @throws IOException Will be raised in case the File could not be found or imported
     */
    public static Data loadData(File inputFile) throws IOException {
        
        // Import process
        DataSource sourceSpecification = DataSource.createCSVSource(inputFile, StandardCharsets.UTF_8, ',', true);
        
        // Clean columns
        sourceSpecification.addColumn(0,FIELD_INDEX, DataType.INTEGER);
        sourceSpecification.addColumn(1,FIELD_ALIAS, DataType.STRING);
        sourceSpecification.addColumn(2,FIELD_SITE, DataType.STRING);
        sourceSpecification.addColumn(3,FIELD_AGE, DataType.INTEGER);
        sourceSpecification.addColumn(4,FIELD_GENDER, DataType.STRING);
        sourceSpecification.addColumn(5,FIELD_TREATMENT, DataType.STRING);
        sourceSpecification.addColumn(6,FIELD_BMI, DataType.DECIMAL);
        sourceSpecification.addColumn(7,FIELD_SYS_BLOODPREASURE_MEASURE, DataType.INTEGER);
        sourceSpecification.addColumn(8,FIELD_SYS_BLOODPREASURE_UNIT, DataType.STRING);
        sourceSpecification.addColumn(9,FIELD_NYHA, DataType.STRING);
        sourceSpecification.addColumn(10,FIELD_SMOKING, DataType.INTEGER);
        sourceSpecification.addColumn(11,FIELD_DIABETES, DataType.INTEGER);
        sourceSpecification.addColumn(12,FIELD_COPD, DataType.INTEGER);
        sourceSpecification.addColumn(13,FIELD_HEARTFAILURE_DURATION, DataType.INTEGER);
        sourceSpecification.addColumn(14,FIELD_HEARTFAILURE_LONGER_18MONTH, DataType.INTEGER);
        sourceSpecification.addColumn(15,FIELD_MRA, DataType.INTEGER);
        sourceSpecification.addColumn(16,FIELD_BETA, DataType.INTEGER);
        sourceSpecification.addColumn(17,FIELD_FUROSEMIDE1, DataType.INTEGER);
        sourceSpecification.addColumn(18,FIELD_STATIN, DataType.INTEGER);
        sourceSpecification.addColumn(19,FIELD_ARNI, DataType.INTEGER);
        sourceSpecification.addColumn(20,FIELD_ACEI_ARB, DataType.INTEGER);
        sourceSpecification.addColumn(21,FIELD_LVEF_MEASURE, DataType.DECIMAL);
        sourceSpecification.addColumn(22,FIELD_LVEF_UNIT, DataType.STRING);
        sourceSpecification.addColumn(23,FIELD_CREATININE_MEASURE, DataType.DECIMAL);
        sourceSpecification.addColumn(24,FIELD_CREATININE_UNIT, DataType.STRING);
        sourceSpecification.addColumn(25,FIELD_SODIUM_MEASURE, DataType.DECIMAL);
        sourceSpecification.addColumn(26,FIELD_SODIUM_UNIT, DataType.STRING);
        sourceSpecification.addColumn(27,FIELD_HB_MEASURE, DataType.DECIMAL);
        sourceSpecification.addColumn(28,FIELD_HB_UNIT, DataType.STRING);
        sourceSpecification.addColumn(29,FIELD_EGFR_MEASURE, DataType.DECIMAL);
        sourceSpecification.addColumn(30,FIELD_EGFR_UNIT, DataType.STRING);
        sourceSpecification.addColumn(31,FIELD_NTPROBNP_MEASURE, DataType.INTEGER);
        sourceSpecification.addColumn(32,FIELD_NTPROBNP_UNIT, DataType.STRING);
        sourceSpecification.addColumn(33,FIELD_HSTNT_MEASURE, DataType.DECIMAL);
        sourceSpecification.addColumn(34,FIELD_HSTNT_UNIT, DataType.STRING);

        return Data.create(sourceSpecification);
    }

    /**
     * Writes the data, shuffles rows
     * @param original
     * @param result
     * @param output
     * @throws IOException
     */
    public static void writeStatsOutput(DataHandle original, DataHandle result, File output) throws IOException {

        BufferedWriter writer = new BufferedWriter(new FileWriter(output.getAbsoluteFile()));

        writer.write("attribute name; original granularity; original missings; original non-uniform entropy; " +
                "result granularity; result missings; result non-uniform entropy");
        writer.write(lineSeparator);

        Set<String> qids = original.getDefinition().getQuasiIdentifyingAttributes();
        for (String qid : qids) {
            double granularity_ori = original.getStatistics().getQualityStatistics().getGranularity().getValue(qid);
            double missings_ori = original.getStatistics().getQualityStatistics().getMissings().getValue(qid);
            double nonUniformEntropy_ori = original.getStatistics().getQualityStatistics().getNonUniformEntropy().getValue(qid);

            double granularity_res = result.getStatistics().getQualityStatistics().getGranularity().getValue(qid);
            double missings_res = result.getStatistics().getQualityStatistics().getMissings().getValue(qid);
            double nonUniformEntropy_res = result.getStatistics().getQualityStatistics().getNonUniformEntropy().getValue(qid);

            writer.write(String.format("%s; %f; %f; %f; %f; %f; %f",
                    qid,
                    granularity_ori,
                    missings_ori,
                    nonUniformEntropy_ori,
                    granularity_res,
                    missings_res,
                    nonUniformEntropy_res));
            writer.write(lineSeparator);

        }
        writer.close();
    }
    
    /**
     * Writes the data, shuffles rows
     * @param result 
     * @param output
     * @throws IOException 
     */
    public static void writeOutput(Data result, File output) throws IOException {
        CSVDataOutput writer = new CSVDataOutput(output, ',');
        writer.write(result.getHandle().iterator());
    }

}
