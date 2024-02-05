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

import org.apache.commons.cli.*;
import org.deidentifier.arx.Data;
import org.deidentifier.arx.DataHandle;

import java.io.File;
import java.io.IOException;

/**
 * Main entry point, code was adapted from: <a href="https://github.com/BIH-MI/leoss-puf">LEOSS Repository</a>
 * @author Fabian Prasser
 * @author Karen Otte
 */
public class Main {

    /** Mode*/
    private static final Option MODE_MAGGIC = Option.builder().longOpt("MAGGIC")
            .desc("Risk assessment mode. If chosen, the following options must be present as well: riskAssessmentConfig, dataConfig, anonymizationConfig, name")
            .hasArg(false)
            .required(false)
            .build();
    /** Mode*/
    private static final Option MODE_BIOHF = Option.builder().longOpt("BIOHF")
            .desc("Risk assessment series mode: If chosen, the following options must be present as well: seriesConfig")
            .hasArg(false)
            .required(false)
            .build();
    /** Mode*/
    private static final Option MODE_FULL_UCC = Option.builder().longOpt("FULL")
            .desc("Target selection mode: If chosen, the following options must be present as well: dataConfig")
            .hasArg(false)
            .required(false)
            .build();

    /** Parameter */
    private static final Option PARAMETER_INPUT_PATH = Option.builder("i").longOpt("input")
            .desc("Path to risk assessment configuration")
            .hasArg(true)
            .required(true)
            .build();

    /** Parameter */
    private static final Option PARAMETER_OUTPUT_PATH = Option.builder("o").longOpt("output")
            .desc("Path to risk assessment configuration")
            .hasArg(true)
            .required(true)
            .build();

    /**
     * Main entry point
     * @param args Should include anonymization mode, input and output paths
     * @throws IOException
     */
    public static void main(String[] args) throws IOException {

        // Prepare options
        Options options = new Options();
        options.addOption(MODE_BIOHF);
        options.addOption(MODE_MAGGIC);
        options.addOption(MODE_FULL_UCC);

        // Check args
        if (args == null || args.length == 0) {
            help(options, "No parameters provided");
            return;
        }

        // Prepare parsing
        CommandLineParser parser = new DefaultParser();
        CommandLine cmd;

        // Parse
        try {
            cmd = parser.parse(options, args, true);
        } catch (Exception e) {
            help(options, e.getMessage());
            return;
        }

        // set anonymization mode
        AnonymizationMode mode = null;
        if (cmd.hasOption(MODE_BIOHF)) {
            mode = AnonymizationMode.BIO_HF;
        }
        if (cmd.hasOption(MODE_MAGGIC)) {
            mode = AnonymizationMode.MAGGIC;
        }
        if (cmd.hasOption(MODE_FULL_UCC)) {
            mode = AnonymizationMode.FULL;
        }
        if (mode == null){
            help(options, "No known option provided");
            return;
        }

        // Parse again with specific options
        options = new Options();
        options.addOption(PARAMETER_INPUT_PATH);
        options.addOption(PARAMETER_OUTPUT_PATH);
        switch (mode){
            case MAGGIC -> options.addOption(MODE_MAGGIC);
            case BIO_HF -> options.addOption(MODE_BIOHF);
            case FULL -> options.addOption(MODE_FULL_UCC);
        }

        try {
            cmd = parser.parse(options, args, false);
        } catch (Exception e) {
            help(options, e.getMessage());
            return;
        }

        // define Input and output file paths
        String input = cmd.getOptionValue(PARAMETER_INPUT_PATH);
        String output = cmd.getOptionValue(PARAMETER_OUTPUT_PATH);
        String output_stats = cmd.getOptionValue(PARAMETER_OUTPUT_PATH);
        output_stats = output_stats.replace(".csv", "_stats.csv");

        // Parse Data
        Data data = IO.loadData(new File(input));

        // Anonymize
        DataHandle data_anon = Anon.anonymizeUseCaseCardio(data, mode);

        // Write
        File output_file = new File(output);
        File output_stats_file = new File(output_stats);
        IO.writeOutput(Util.getData(data_anon), output_file);
        IO.writeStatsOutput(data.getHandle(), data_anon, output_stats_file);

    }

    /**
     * Print help
     * @param options
     * @param message
     */
    private static void help(Options options, String message) {
        HelpFormatter formatter = new HelpFormatter();
        formatter.printHelp("java -jar [file].jar", message, options, "");
    }
}
