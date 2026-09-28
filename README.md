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

## Current Project Status
- **Phase 1 (Complete)**: Workspace architecture established, ground-truth business rules documented in [`docs/business_rules.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/business_rules.md), evaluation methodology defined in [`docs/evaluation_plan.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/evaluation_plan.md), and schema specifications created in [`docs/test_case_schema.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/test_case_schema.md).
- **Phase 2 (Upcoming)**: Dataset creation (curating the 60 structured test cases following `docs/test_case_schema.md`).
- **Phase 3 (Upcoming)**: Execution pipeline, LLM integration, metric calculation, failure analysis, and report generation.