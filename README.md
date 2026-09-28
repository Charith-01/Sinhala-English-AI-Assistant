# Sinhala-English AI Assistant Evaluation Framework

## Background
Evaluating Large Language Models (LLMs) in multilingual and code-mixed conversational settings presents unique challenges, particularly for low-resource languages and localized scripts. In Sri Lanka, everyday customer service interactions frequently bridge formal English, Sinhala script, Singlish (Sinhala transcribed using the Roman alphabet), and Sinhala-English code-mixing.

## Problem Statement
Standard LLM evaluation benchmarks primarily focus on monolingual English or major global languages. When deployed as customer service assistants in Sri Lanka, generic LLMs often struggle with script switching, phonetic Singlish interpretation, localized e-commerce terminology, and contextual accuracy across mixed-language prompts. Currently, there is a lack of structured, reproducible evaluation frameworks to systematically test and quantify LLM reliability across these specific linguistic modalities.

## Main Objective
To design and build a lightweight, reproducible evaluation framework for systematically testing LLMs in a Sinhala-English business assistant context, generating quantitative performance metrics, failure pattern analyses, and structured technical reports.

## Business Use Case
- **Scenario**: Controlled customer service environment for a fictional Sri Lankan e-commerce business.
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
│   ├── raw/                # Raw evaluation test cases and datasets
│   └── processed/          # Prepared and validated test suites
├── src/                    # Core source code and evaluation utilities
│   └── __init__.py
├── scripts/                # Utility scripts for execution and reporting
├── results/                # Evaluation output data
│   └── figures/            # Generated charts and visualization figures
├── tests/                  # Unit and integration tests
├── docs/                   # Documentation and final report draft
├── .gitignore              # Git ignore rules
└── README.md               # Project overview documentation
```

## Current Project Status
- **Phase 1 (Current - Project Setup)**: Workspace architecture established, directory layout created, and project guidelines documented.
- **Phase 2 (Upcoming)**: Dataset creation (curating at least 50 structured test cases covering all 4 language modalities).
- **Phase 3 (Upcoming)**: Execution pipeline, LLM integration, metric calculation, failure analysis, and report generation.