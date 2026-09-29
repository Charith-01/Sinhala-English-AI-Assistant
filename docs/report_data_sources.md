# Report Data Sources Mapping

This document maps each section of the Final Technical Report ([`docs/final_technical_report.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/final_technical_report.md)) to its primary source files and implementation modules.

---

| Report Section | Primary Source File(s) | Source Module / Script |
| :--- | :--- | :--- |
| **Executive Summary** | `results/metrics_summary.json`<br>`data/processed/final_run_metadata.json` | `scripts/analyze_final_results.py` |
| **Introduction & Business Scenario** | `docs/business_rules.md`<br>`docs/evaluation_plan.md` | Ground-Truth Documentation |
| **Project Objectives** | `docs/evaluation_plan.md` | Evaluation Design |
| **Model Under Evaluation** | `docs/experiment_setup.md`<br>`data/processed/final_run_metadata.json` | `src/llm_client.py` |
| **Business Knowledge Base** | `docs/business_rules.md` | Ground-Truth Knowledge Base |
| **Evaluation Dataset & Sample Cases** | `docs/dataset_summary.md`<br>`data/raw/final_test_cases.csv` | `src/dataset_validator.py` |
| **Evaluation Methodology & Rubric** | `docs/scoring_guide.md`<br>`docs/evaluation_plan.md` | `src/evaluator.py` |
| **Human-Grounded Evaluation** | `docs/final_evaluation_instructions.md`<br>`data/processed/final_evaluation_worksheet.csv` | `scripts/create_final_evaluation_worksheet.py` |
| **Experimental Pipeline** | `docs/experiment_setup.md` | Project Architecture |
| **Overall Quantitative Results** | `results/metrics_summary.json`<br>`results/tables/final_summary_table.csv` | `src/metrics.py` |
| **Language Performance** | `results/tables/performance_by_language.csv`<br>`results/figures/pass_rate_by_language.png` | `src/metrics.py`<br>`src/visualization.py` |
| **Difficulty Performance** | `results/tables/performance_by_difficulty.csv`<br>`results/figures/pass_rate_by_difficulty.png` | `src/metrics.py`<br>`src/visualization.py` |
| **Category Performance** | `results/tables/performance_by_category.csv`<br>`results/figures/pass_rate_by_category.png` | `src/metrics.py`<br>`src/visualization.py` |
| **Evaluation Dimensions** | `results/tables/dimension_scores.csv`<br>`results/figures/average_dimension_scores.png` | `src/metrics.py`<br>`src/visualization.py` |
| **Failure Pattern Analysis** | `results/failure_analysis_summary.json`<br>`docs/failure_analysis.md` | `src/failure_analysis.py` |
| **Representative Failure Examples** | `results/tables/representative_failure_examples.csv` | `src/failure_analysis.py` |
| **Hallucination & Privacy Findings** | `results/metrics_summary.json`<br>`results/failure_analysis_summary.json` | `src/metrics.py`<br>`src/failure_analysis.py` |
| **Clarification & Escalation Analysis** | `results/failure_analysis_summary.json` | `src/failure_analysis.py` |
| **Technical Implementation & Commands** | Project codebase (`src/`, `scripts/`, `tests/`) | Project Repository |
