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

import org.deidentifier.arx.*;
import org.deidentifier.arx.AttributeType.Hierarchy;
import org.deidentifier.arx.AttributeType.Hierarchy.DefaultHierarchy;
import org.deidentifier.arx.aggregates.HierarchyBuilderIntervalBased;
import org.deidentifier.arx.aggregates.HierarchyBuilderIntervalBased.Range;
import org.deidentifier.arx.criteria.KAnonymity;
import org.deidentifier.arx.exceptions.RollbackRequiredException;
import org.deidentifier.arx.metric.Metric;

import java.io.IOException;
import java.util.Arrays;

/**
 * Implements all anonymization processes, code was adapted from: <a href="https://github.com/BIH-MI/leoss-puf">LEOSS Repository</a>
 *
 * @author Fabian Prasser
 * @author Karen Otte
 */
public class Anon {

    /**
     * Transformation rule
     */
    private static Hierarchy RULE_AGE;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_GENDER;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_BMI;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_SYS_BP_M;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_NYHA;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_SMOKING;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_DIABETES;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_COPD;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_HF_GT_18;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_BETA;

    /**
     * Transformation rule
     */
    private static Hierarchy RULE_FUROSEMIDE1;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_STATIN;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_ACEI_ARB;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_LVEF_M;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_CREATININE_M;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_SODIUM_M;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_HB_M;
    /**
     * Transformation rule
     */
    private static Hierarchy RULE_EGFR_M;

    private static void createHierarchies(Data data) {

        RULE_AGE = getAgeHierarchy(data);
        RULE_GENDER = getGenderHierarchy();
        RULE_BMI = getBMIHierarchy(data);
        RULE_SYS_BP_M = getSysBpMHierarchy(data);
        RULE_NYHA = getNyhaHierarchy();
        RULE_SMOKING = getSmokingHierarchy();
        RULE_DIABETES = getDiabetesHierarchy();
        RULE_COPD = getCopdHierarchy();
        RULE_HF_GT_18 = getHfGt18Hierarchy();
        RULE_BETA = getBetaHierarchy();
        RULE_FUROSEMIDE1 = getFurosemide1Hierarchy();
        RULE_STATIN = getStatinHierarchy();
        RULE_ACEI_ARB = getAceiArbHierarchy();
        RULE_LVEF_M = getLvefMHierarchy(data);
        RULE_CREATININE_M = getCreatinineMHierarchy(data);
        RULE_SODIUM_M = getSodiumMHierarchy(data);
        RULE_HB_M = getHbMHierarchy(data);
        RULE_EGFR_M = getEgrfMHierarchy(data);

    }

    /**
     * Anonymization for Use Case Cardiology HiGHmed Cardio Dataset
     *
     * @param data
     * @return
     * @throws IOException
     */
    public static DataHandle anonymizeUseCaseCardio(Data data, AnonymizationMode mode) throws IOException {

        createHierarchies(data);

        // Define all as identifying attributes
        for (int i = 0; i < data.getHandle().getNumColumns(); i++) {
            data.getDefinition().setAttributeType(data.getHandle().getAttributeName(i), AttributeType.IDENTIFYING_ATTRIBUTE);
        }

        // Define quasi-identifiers
        switch (mode) {
            case MAGGIC -> data = define_quasiidentifiers_maggic(data);
            case BIO_HF -> data = define_quasiidentifiers_biohf(data);
            case FULL -> data = define_quasiidentifiers_full(data);
            default -> data = define_quasiidentifiers_full(data);
        }

        // Prepare config
        ARXConfiguration config = ARXConfiguration.create();

        // Configure transformation model
        config.setSuppressionLimit(1d);
        config.addPrivacyModel(new KAnonymity(2));
        config.setQualityModel(Metric.createLossMetric(0, Metric.AggregateFunction.GEOMETRIC_MEAN));
        config.setAlgorithm(ARXConfiguration.AnonymizationAlgorithm.BEST_EFFORT_BOTTOM_UP);
        config.setHeuristicSearchStepLimit(50000);

        // Anonymize
        ARXAnonymizer anonymizer = new ARXAnonymizer();
        ARXResult result = anonymizer.anonymize(data, config);

        DataHandle output = result.getOutput();
        double oMin = 1d / 1000d;
        try {

            result.optimizeIterativeFast(output, oMin);
        } catch (RollbackRequiredException e) {
            e.printStackTrace();
        }

        System.out.println(Arrays.toString(result.getGlobalOptimum().getTransformation()));

        // Done
        return output;
    }

    private static Data define_quasiidentifiers_maggic(Data data) {
        // Define quasi-identifiers
        data.getDefinition().setAttributeType(IO.FIELD_AGE, RULE_AGE);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_AGE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_GENDER, RULE_GENDER);
        data.getDefinition().setAttributeType(IO.FIELD_BMI, RULE_BMI);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_BMI, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_SYS_BLOODPREASURE_MEASURE, RULE_SYS_BP_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_SYS_BLOODPREASURE_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_NYHA, RULE_NYHA);
        data.getDefinition().setAttributeType(IO.FIELD_SMOKING, RULE_SMOKING);
        data.getDefinition().setAttributeType(IO.FIELD_DIABETES, RULE_DIABETES);
        data.getDefinition().setAttributeType(IO.FIELD_COPD, RULE_COPD);
        data.getDefinition().setAttributeType(IO.FIELD_HEARTFAILURE_LONGER_18MONTH, RULE_HF_GT_18);
        data.getDefinition().setAttributeType(IO.FIELD_BETA, RULE_BETA);
        data.getDefinition().setAttributeType(IO.FIELD_ACEI_ARB, RULE_ACEI_ARB);
        data.getDefinition().setAttributeType(IO.FIELD_LVEF_MEASURE, RULE_LVEF_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_LVEF_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_CREATININE_MEASURE, RULE_CREATININE_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_CREATININE_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        return data;
    }

    private static Data define_quasiidentifiers_biohf(Data data) {
        // Define quasi-identifiers
        data.getDefinition().setAttributeType(IO.FIELD_AGE, RULE_AGE);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_AGE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_GENDER, RULE_GENDER);
        data.getDefinition().setAttributeType(IO.FIELD_NYHA, RULE_NYHA);
        data.getDefinition().setAttributeType(IO.FIELD_BETA, RULE_BETA);
        data.getDefinition().setAttributeType(IO.FIELD_FUROSEMIDE1, RULE_FUROSEMIDE1);
        data.getDefinition().setAttributeType(IO.FIELD_STATIN, RULE_STATIN);
        data.getDefinition().setAttributeType(IO.FIELD_ACEI_ARB, RULE_ACEI_ARB);
        data.getDefinition().setAttributeType(IO.FIELD_LVEF_MEASURE, RULE_LVEF_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_LVEF_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_SODIUM_MEASURE, RULE_SODIUM_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_SODIUM_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_HB_MEASURE, RULE_HB_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_HB_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_EGFR_MEASURE, RULE_EGFR_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_EGFR_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        return data;
    }

    private static Data define_quasiidentifiers_full(Data data) {
        // Define quasi-identifiers
        data.getDefinition().setAttributeType(IO.FIELD_AGE, RULE_AGE);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_AGE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_GENDER, RULE_GENDER);
        data.getDefinition().setAttributeType(IO.FIELD_BMI, RULE_BMI);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_BMI, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_SYS_BLOODPREASURE_MEASURE, RULE_SYS_BP_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_SYS_BLOODPREASURE_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_NYHA, RULE_NYHA);
        data.getDefinition().setAttributeType(IO.FIELD_SMOKING, RULE_SMOKING);
        data.getDefinition().setAttributeType(IO.FIELD_DIABETES, RULE_DIABETES);
        data.getDefinition().setAttributeType(IO.FIELD_COPD, RULE_COPD);
        data.getDefinition().setAttributeType(IO.FIELD_HEARTFAILURE_LONGER_18MONTH, RULE_HF_GT_18);
        data.getDefinition().setAttributeType(IO.FIELD_BETA, RULE_BETA);
        data.getDefinition().setAttributeType(IO.FIELD_FUROSEMIDE1, RULE_FUROSEMIDE1);
        data.getDefinition().setAttributeType(IO.FIELD_STATIN, RULE_STATIN);
        data.getDefinition().setAttributeType(IO.FIELD_ACEI_ARB, RULE_ACEI_ARB);
        data.getDefinition().setAttributeType(IO.FIELD_LVEF_MEASURE, RULE_LVEF_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_LVEF_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_CREATININE_MEASURE, RULE_CREATININE_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_CREATININE_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_SODIUM_MEASURE, RULE_SODIUM_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_SODIUM_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_HB_MEASURE, RULE_HB_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_HB_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        data.getDefinition().setAttributeType(IO.FIELD_EGFR_MEASURE, RULE_EGFR_M);
        data.getDefinition().setMicroAggregationFunction(IO.FIELD_EGFR_MEASURE, AttributeType.MicroAggregationFunction.createGeometricMean(), true);
        return data;
    }

    /**
     * Binary Hierarchy
     *
     * @return
     */
    private static Hierarchy getBinaryHierarchy() {
        DefaultHierarchy hierarchy = Hierarchy.create();
        hierarchy.add("0", "*");
        hierarchy.add("1", "*");
        hierarchy.add("NULL", "*");
        return hierarchy;
    }

    /**
     * Age hierarchy
     *
     * @return
     */
    private static Hierarchy getAgeHierarchy(Data data) {

        HierarchyBuilderIntervalBased<Double> hierarchyBuilder = HierarchyBuilderIntervalBased.create(
                DataType.DECIMAL,
                new Range<Double>(15d, 15d, 15d),
                new Range<Double>(100d, 100d, 100d));

        // Define base intervals
        hierarchyBuilder.setAggregateFunction(DataType.DECIMAL.createAggregate().createArithmeticMeanFunction());
        hierarchyBuilder.addInterval(15d, 20d);
        // Define grouping
        hierarchyBuilder.getLevel(0).addGroup(2);
        hierarchyBuilder.getLevel(1).addGroup(2);
        hierarchyBuilder.getLevel(2).addGroup(2);

        hierarchyBuilder.prepare(data.getHandle().getDistinctValues(data.getHandle().getColumnIndexOf(IO.FIELD_AGE)));
        return hierarchyBuilder.build();

    }

    /**
     * Gender hierarchy
     *
     * @return
     */
    private static Hierarchy getGenderHierarchy() {
        DefaultHierarchy hierarchy = Hierarchy.create();
        hierarchy.add("NULL");
        hierarchy.add("f");
        hierarchy.add("m");
        return hierarchy;
    }

    /**
     * BMI hierarchy
     *
     * @return
     */
    private static Hierarchy getBMIHierarchy(Data data) {

        HierarchyBuilderIntervalBased<Double> hierarchyBuilder = HierarchyBuilderIntervalBased.create(
                DataType.DECIMAL,
                new Range<Double>(0d, 0d, 0d),
                new Range<Double>(80d, 80d, Double.MAX_VALUE));

        // Define base intervals
        hierarchyBuilder.setAggregateFunction(DataType.DECIMAL.createAggregate().createArithmeticMeanFunction());
        hierarchyBuilder.addInterval(0d, 14d);
        hierarchyBuilder.addInterval(14d, 16d);
        hierarchyBuilder.addInterval(16d, 18d);
        // Define grouping
        hierarchyBuilder.getLevel(0).addGroup(2);
        hierarchyBuilder.getLevel(1).addGroup(2);
        hierarchyBuilder.getLevel(2).addGroup(2);
        hierarchyBuilder.getLevel(3).addGroup(2);
        hierarchyBuilder.getLevel(4).addGroup(2);

        hierarchyBuilder.prepare(data.getHandle().getDistinctValues(data.getHandle().getColumnIndexOf(IO.FIELD_BMI)));
        Hierarchy hierarchy = hierarchyBuilder.build();

        return hierarchy;

    }

    /**
     * Systolic Blood Preasure hierarchy
     *
     * @return Systolic Blood Preasure hierarchy
     */
    private static Hierarchy getSysBpMHierarchy(Data data) {

        HierarchyBuilderIntervalBased<Long> hierarchyBuilder = HierarchyBuilderIntervalBased.create(
                DataType.INTEGER,
                new Range<Long>(0l, 0l, 0l),
                new Range<Long>(240l, 240l, 240l));

        // Define base intervals
        hierarchyBuilder.setAggregateFunction(DataType.INTEGER.createAggregate().createIntervalFunction(true, false));
        hierarchyBuilder.addInterval(0l, 10l);
        // Define grouping
        hierarchyBuilder.getLevel(0).addGroup(2);
        hierarchyBuilder.getLevel(1).addGroup(2);
        hierarchyBuilder.getLevel(2).addGroup(2);
        hierarchyBuilder.getLevel(3).addGroup(2);
        hierarchyBuilder.getLevel(4).addGroup(2);

        hierarchyBuilder.prepare(data.getHandle().getDistinctValues(data.getHandle().getColumnIndexOf(IO.FIELD_SYS_BLOODPREASURE_MEASURE)));
        return hierarchyBuilder.build();
    }

    /**
     * NYHA hierarchy
     *
     * @return
     */
    private static Hierarchy getNyhaHierarchy() {
        DefaultHierarchy hierarchy = Hierarchy.create();
        hierarchy.add("I", "{I,II}");
        hierarchy.add("II", "{I,II}");
        hierarchy.add("III", "{III,IV}");
        hierarchy.add("IV", "{III,IV}");
        hierarchy.add("NULL", "{NULL}");
        return hierarchy;
    }

    /**
     * Smoking hierarchy
     *
     * @return
     */
    private static Hierarchy getSmokingHierarchy() {
        return getBinaryHierarchy();
    }

    /**
     * Diabetes hierarchy
     *
     * @return
     */
    private static Hierarchy getDiabetesHierarchy() {
        return getBinaryHierarchy();
    }

    /**
     * COPD hierarchy
     *
     * @return
     */
    private static Hierarchy getCopdHierarchy() {
        return getBinaryHierarchy();
    }

    /**
     * Beta hierarchy
     *
     * @return
     */
    private static Hierarchy getBetaHierarchy() {
        return getBinaryHierarchy();
    }

    /**
     * Furosemide1 hierarchy
     *
     * @return
     */
    private static Hierarchy getFurosemide1Hierarchy() {
        return getBinaryHierarchy();
    }

    /**
     * HF greater 18 month hierarchy
     *
     * @return
     */
    private static Hierarchy getHfGt18Hierarchy() {
        return getBinaryHierarchy();
    }

    /**
     * Statin hierarchy
     *
     * @return
     */
    private static Hierarchy getStatinHierarchy() {
        return getBinaryHierarchy();
    }

    /**
     * Acei arb hierarchy
     *
     * @return
     */
    private static Hierarchy getAceiArbHierarchy() {
        return getBinaryHierarchy();
    }

    /**
     * Lvef Measure hierarchy
     *
     * @return
     */
    private static Hierarchy getLvefMHierarchy(Data data) {

        HierarchyBuilderIntervalBased<Double> hierarchyBuilder = HierarchyBuilderIntervalBased.create(
                DataType.DECIMAL,
                new Range<Double>(5d, 5d, 5d),
                new Range<Double>(85d, 85d, 85d));

        // Define base intervals
        hierarchyBuilder.setAggregateFunction(DataType.DECIMAL.createAggregate().createIntervalFunction(true, false));
        hierarchyBuilder.addInterval(0d, 5d);

        // Define grouping
        hierarchyBuilder.getLevel(0).addGroup(2);
        hierarchyBuilder.getLevel(1).addGroup(2);
        hierarchyBuilder.getLevel(2).addGroup(2);
        hierarchyBuilder.getLevel(3).addGroup(2);
        hierarchyBuilder.getLevel(4).addGroup(2);

        hierarchyBuilder.prepare(data.getHandle().getDistinctValues(data.getHandle().getColumnIndexOf(IO.FIELD_LVEF_MEASURE)));
        return hierarchyBuilder.build();
    }


    /**
     * Creatinine Measure hierarchy
     *
     * @return
     */
    private static Hierarchy getCreatinineMHierarchy(Data data) {
        HierarchyBuilderIntervalBased<Double> hierarchyBuilder = HierarchyBuilderIntervalBased.create(
                DataType.DECIMAL,
                new Range<Double>(0d, 0d, 0d),
                new Range<Double>(1200d, 1200d, 1200d));

        // Define base intervals
        hierarchyBuilder.setAggregateFunction(DataType.DECIMAL.createAggregate().createIntervalFunction(true, false));
        hierarchyBuilder.addInterval(0d, 100d);
        // Define grouping
        hierarchyBuilder.getLevel(0).addGroup(2);
        hierarchyBuilder.getLevel(1).addGroup(2);
        hierarchyBuilder.getLevel(2).addGroup(2);

        hierarchyBuilder.prepare(data.getHandle().getDistinctValues(data.getHandle().getColumnIndexOf(IO.FIELD_CREATININE_MEASURE)));
        return hierarchyBuilder.build();
    }

    /**
     * Sodium hierarchy
     *
     * @return
     */
    private static Hierarchy getSodiumMHierarchy(Data data) {

        HierarchyBuilderIntervalBased<Double> hierarchyBuilder = HierarchyBuilderIntervalBased.create(
                DataType.DECIMAL,
                new Range<Double>(110d, 110d, 110d),
                new Range<Double>(160d, 160d, 160d));

        // Define base intervals
        hierarchyBuilder.setAggregateFunction(DataType.DECIMAL.createAggregate().createIntervalFunction(true, false));
        hierarchyBuilder.addInterval(0d, 10d);

        // Define grouping
        hierarchyBuilder.getLevel(0).addGroup(2);
        hierarchyBuilder.getLevel(1).addGroup(2);
        hierarchyBuilder.getLevel(2).addGroup(2);
        hierarchyBuilder.getLevel(3).addGroup(2);

        hierarchyBuilder.prepare(data.getHandle().getDistinctValues(data.getHandle().getColumnIndexOf(IO.FIELD_SODIUM_MEASURE)));
        return hierarchyBuilder.build();
    }

    /**
     * HB hierarchy
     *
     * @return
     */
    private static Hierarchy getHbMHierarchy(Data data) {

        HierarchyBuilderIntervalBased<Double> hierarchyBuilder = HierarchyBuilderIntervalBased.create(
                DataType.DECIMAL,
                new Range<Double>(5d, 5d, 5d),
                new Range<Double>(1022d, 1022d, 1022d));

        // Define base intervals
        hierarchyBuilder.setAggregateFunction(DataType.DECIMAL.createAggregate().createIntervalFunction(true, false));
        hierarchyBuilder.addInterval(0d, 1d);

        // Define grouping
        hierarchyBuilder.getLevel(0).addGroup(5);
        hierarchyBuilder.getLevel(1).addGroup(2);
        hierarchyBuilder.getLevel(2).addGroup(2);

        hierarchyBuilder.prepare(data.getHandle().getDistinctValues(data.getHandle().getColumnIndexOf(IO.FIELD_HB_MEASURE)));
        return hierarchyBuilder.build();

    }

    /**
     * EGRF hierarchy
     *
     * @return
     */
    private static Hierarchy getEgrfMHierarchy(Data data) {

        HierarchyBuilderIntervalBased<Double> hierarchyBuilder = HierarchyBuilderIntervalBased.create(
                DataType.DECIMAL,
                new Range<Double>(5d, 5d, 5d),
                new Range<Double>(170d, 170d, 170d));

        // Define base intervals
        hierarchyBuilder.setAggregateFunction(DataType.DECIMAL.createAggregate().createArithmeticMeanFunction());
        hierarchyBuilder.addInterval(0d, 1d);

        // Define grouping
        hierarchyBuilder.getLevel(0).addGroup(2);
        hierarchyBuilder.getLevel(1).addGroup(2);
        hierarchyBuilder.getLevel(2).addGroup(2);
        hierarchyBuilder.getLevel(3).addGroup(2);

        hierarchyBuilder.prepare(data.getHandle().getDistinctValues(data.getHandle().getColumnIndexOf(IO.FIELD_EGFR_MEASURE)));
        return hierarchyBuilder.build();
    }
}