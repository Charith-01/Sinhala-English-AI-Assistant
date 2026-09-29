# Sinhala-English AI Assistant Evaluation Framework

## Background
Evaluating Large Language Models (LLMs) in multilingual and code-mixed conversational settings presents unique challenges, particularly for low-resource languages and localized scripts. In Sri Lanka, everyday customer service interactions frequently bridge formal English, Sinhala script, Singlish (Sinhala transcribed using the Roman alphabet), and Sinhala-English code-mixing.

## Problem Statement
Standard LLM evaluation benchmarks primarily focus on monolingual English or major global languages. When deployed as customer service assistants in Sri Lanka, generic LLMs often struggle with script switching, phonetic Singlish interpretation, localized e-commerce terminology, and contextual accuracy across mixed-language prompts. Currently, there is a lack of structured, reproducible evaluation frameworks to systematically test and quantify LLM reliability across these specific linguistic modalities.

## Main Objective
To design and build a lightweight, reproducible evaluation framework for systematically testing LLMs in a Sinhala-English business assistant context, generating quantitative performance metrics, failure pattern analyses, and structured technical reports.

## Business Use Case
- **Scenario**: Controlled customer service environment for a fictional Sri Lankan e-commerce business (**LankaCart**).
- **Ground-Truth Knowledge Base**: Defined in [`docs/business_rules.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/business_rules.md).
- **Target Role**: AI Customer Support Assistant handling inquiries regarding order tracking, payment methods, delivery timelines, return policies, and product availability.

## Scope & Language Coverage
The framework evaluates performance across four distinct language representations:
1. **English**: Standard English business inquiries (e.g., *"What is your return policy?"*)
2. **Sinhala Unicode**: Standard Sinhala script (e.g., *"මගේ ඇණවුම ලැබෙන්නේ කවදාද?"*)
3. **Singlish**: Sinhala written using the Latin/Roman alphabet (e.g., *"Mage order eka enne kawadada?"*)
4. **Sinhala-English Code-Mixed**: Prompts blending English and Sinhala words or phrases (e.g., *"Item eka return karanne kohomada?"*)

## High-Level Evaluation Dimensions
The framework focuses on key quality dimensions:
- **Language & Script Understanding**: Accuracy in comprehending Sinhala Unicode, Singlish, and code-mixed inputs.
- **Intent & Domain Accuracy**: Correct identification of user intent within the e-commerce context.
- **Response Appropriateness**: Politeness, relevance, tone, and appropriate language alignment.
- **Hallucination & Robustness**: Resistance to policy misstatements and resilience under noisy Singlish inputs.

## Planned Workflow
```
[ Ground-Truth Rules (docs/business_rules.md) ]
                       │
                       ▼
[ Test Case Dataset (50+ cases) ]
                       │
                       ▼
[ Execution Runner / LLM Interface ]
                       │
                       ▼
[ Raw Model Responses Logging ]
                       │
                       ▼
[ Evaluation & Scoring Engine ]
                       │
                       ▼
[ Metrics, Analysis Tables & Visualizations ]
```

## Planned Project Structure
```
Sinhala-English-AI-Assistant/
├── data/
│   ├── raw/
│   │   └── test_cases_template.csv # Header template for dataset curation
│   └── processed/                  # Prepared and validated test suites
├── src/                            # Core source code and evaluation utilities
│   └── __init__.py
├── scripts/                        # Utility scripts for execution and reporting
├── results/                        # Evaluation output data
│   └── figures/                    # Generated charts and visualization figures
├── tests/                          # Unit and integration tests
├── docs/                           # Project documentation & methodology
│   ├── business_rules.md           # Ground-truth business policies & evaluation IDs
│   ├── evaluation_plan.md          # Evaluation methodology, scoring rubric & test matrix
│   └── test_case_schema.md         # Field specifications for test case curation
├── .gitignore                      # Git ignore rules
└── README.md                       # Project overview documentation
```

## Setup & Configuration

### 1. Model & Environment Setup
The evaluation framework evaluates **Gemini 3.1 Flash-Lite** against the ground-truth LankaCart business policies.

To configure your local environment:
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and set your API key and Gemini model ID:
   ```env
   GEMINI_API_KEY=your_real_api_key
   GEMINI_MODEL=gemini-3.1-flash-lite
   ```
   *(Note: Set `GEMINI_MODEL` to the exact API model identifier available in your Google AI Studio environment).*

3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Running Unit Tests
Execute the unit test suite (runs offline using mocked API calls):
```bash
python -m unittest discover tests
```

### 3. Validating Test Cases
Validate raw CSV test datasets against the schema and business policy IDs:
```bash
python scripts/validate_test_cases.py
```

### 5. Running Quantitative Analysis
To calculate quantitative metrics once manual human evaluation scores are recorded:
```bash
python scripts/analyze_final_results.py
```
*(Note: Requires completed human evaluation rows in `data/processed/final_evaluation_results.csv` or `data/processed/final_evaluation_worksheet.csv`).*

## Current Project Status
- **Phase 1 (Complete)**: Workspace architecture established, ground-truth business rules documented in [`docs/business_rules.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/business_rules.md), evaluation methodology defined in [`docs/evaluation_plan.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/evaluation_plan.md), and schema specifications created in [`docs/test_case_schema.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/test_case_schema.md).
- **Phase 2 (Complete)**: Response generation pipeline implemented using `google-genai` SDK for Gemini 3.1 Flash-Lite. Sample runner and unit tests passing.
- **Phase 3 (Complete)**: Final 60-case dataset curated, validated, and response generation experiment completed. Final human evaluation worksheet generated. Quantitative analysis module `src/metrics.py`, analysis script `scripts/analyze_final_results.py`, metrics definitions `docs/metrics_definition.md`, and 64 unit tests implemented.