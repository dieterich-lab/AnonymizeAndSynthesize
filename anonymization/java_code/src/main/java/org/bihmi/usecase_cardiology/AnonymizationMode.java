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

/***
 * Enum with the different modes on which subset the anonymization should be performed
 * @author Karen Otte
 */
public enum AnonymizationMode {
    MAGGIC,
    BIO_HF,
    FULL

}
