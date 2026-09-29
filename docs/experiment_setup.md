# Response Generation Experiment Setup & Methodology

This document records the exact configuration, operational parameters, and execution methodology for the response generation experiment evaluated under the **Sinhala-English AI Assistant Evaluation Framework**.

---

## 1. Experiment Overview

* **Evaluated Model**: `gemini-3.1-flash-lite` (Gemini 3.1 Flash-Lite)
* **API SDK**: Official Google GenAI SDK (`google-genai`)
* **Target Dataset Size**: **60 test cases** (`TC001` through `TC060`)
* **Linguistic Scope**: 4 modalities (15 English, 15 Sinhala Unicode, 15 Singlish, 15 Code-Mixed)
* **System Knowledge Base**: Ground-truth LankaCart business policies (`docs/business_rules.md`)

---

## 2. Model & Generation Parameters

| Parameter | Value | Rationale |
| :--- | :--- | :--- |
| **Model Identifier** | `gemini-3.1-flash-lite` | Target model under evaluation for speed, cost, and Sri Lankan multilingual capabilities. |
| **Temperature** | `0.2` | Controlled low temperature to promote deterministic policy retrieval and minimize random output variation. |
| **Execution Mode** | Sequential | Single-threaded sequential processing (TC001 to TC060) to ensure exact reproducibility and prevent rate limits. |
| **System Instruction** | Full `docs/business_rules.md` | Provides operational rules and the complete 22 LankaCart ground-truth policies. |

---

## 3. Strict Ground-Truth Isolation

To maintain rigorous experimental integrity, zero evaluation ground-truth data was disclosed to the LLM during response generation.

**Data Sent to Gemini**:
1. Official LankaCart system instruction and business policy text (`docs/business_rules.md`).
2. Exact customer `user_input` prompt string.

**Data Strictly Excluded from Gemini**:
* `expected_intent`
* `policy_ids`
* `expected_response_language`
* `must_include`
* `must_not_include`
* `requires_clarification`
* `requires_escalation`
* `expected_behavior`
* Evaluation rubrics & scoring formulas

---

## 4. Pipeline Features & Robustness Controls

1. **Incremental Persistence**: Generated responses are written to `data/processed/final_llm_responses.csv` after every single test case completes, protecting against unexpected interruptions or rate limits.
2. **Resume Capability**: Before sending requests, the runner inspects existing output files and automatically skips test IDs that already recorded `success = True`.
3. **Bounded Rate-Limit Retry**: Transient 429 / quota errors trigger a 3-attempt exponential backoff retry before logging a clean failure without interrupting the remaining batch.
4. **Latency Measurement**: Wall-clock response latency is measured via high-precision `time.perf_counter()` and recorded in seconds per request.
5. **Observation Integrity**: Successfully generated model responses are preserved as true experimental observations without manual editing, quality filtering, or unprompted re-generation.

---

## 5. Next Steps

Upon completion of response generation, raw LLM outputs stored in `data/processed/final_llm_responses.csv` will be paired with ground-truth test case criteria to form the human evaluation worksheet (`data/processed/final_evaluation_worksheet.csv`) for 0–2 dimensional scoring.
