# Description

This project provides a Java-based solution for anonymizing the cardiology use case dataset. It supports various modes of
anonymization focusing on the full dataset, or the subsets relevant for calculating BioHF and MAGGIC risk scores respectively. 

# Prerequisites

* Java Development Kit (JDK) 17
* Apache Maven (for building the project)

# Add ARX 3.9.1 Library
The ARX library in Version 3.9.1 needs to be manually added to your local maven repository.
In your terminal, please run the following code:  
`mvn install:install-file -Dfile=lib/libarx-3.9.1.jar -DgroupId=org.deidentifier.arx -DartifactId=arx -Dversion=3.9.1 -Dpackaging=jar`

# Building the Project
1. Navigate to the anonymization directory.
2. Add the ARX Library to the local Maven Repository (see above).
3. Run `mvn clean install` to build the project. This will generate a JAR file in the target directory. 

# Running the Anonymization via CLI 
To run the application, use the following command:

`java -jar target/ucc_anonymization.jar --<MODE> -i <INPUT_PATH> -o <OUTPUT_PATH>`

The application supports the following **anonymization modes**:  
**BIOHF**: Anonymization mode for BIOHF datasets.  
**MAGGIC**: Anonymization mode for MAGGIC datasets.  
**FULL**: Full anonymization mode with User-Centric Control.

The **INPUT_PATH** should contain the absolute path to the dataset in CSV format using comma as separators 
and NULL for missing values.
The **OUTPUT_PATH** should be a .csv filepath to where the anonymized dataset should be saved to. 
In addition, statistical properties of the anonymization will be saved to the same location. 

# License
This project is under Apache License Version 2.0. For further information, please see **LICENSE.md**.

