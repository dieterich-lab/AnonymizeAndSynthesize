/**
 * Use Case Cardiology HiGHmed Data Anonymisation
 * Copyright (C) 2024 - Berlin Institute of Health
 * <p>
 * Licensed under the Academic Free License v3.0;
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * https://license.md/licenses/academic-free-license-v3-0/
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
import org.deidentifier.arx.DataHandleOutput;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * Utility class, code was adapted from: <a href="https://github.com/BIH-MI/leoss-puf">LEOSS Repository</a>
 *
 * @author Fabian Prasser
 */
public class Util {

    /**
     * Extract data
     * @param handle
     * @return
     */
    public static Data getData(DataHandle handle) {

        // Prepare
        Iterator<String[]> iter = handle.iterator();
        List<String[]> rows = new ArrayList<>();
        rows.add(iter.next());
        int rowNumber = 0;
        
        // Convert
        while (iter.hasNext()) {
            String[] row = iter.next();
            if (!(handle instanceof DataHandleOutput) || !handle.isOutlier(rowNumber)) {
                rows.add(row);
            }
            rowNumber++;
        }
        
        // Done
        return Data.create(rows);
    }
    
}

