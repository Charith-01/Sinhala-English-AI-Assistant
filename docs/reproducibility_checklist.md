# Reproducibility Checklist

This document verifies the technical reproducibility of the Sinhala-English AI Assistant Evaluation Framework.

---

## Reproducibility Verification Items

- [x] **Python Dependencies Documented**: All required project packages (`pandas`, `python-dotenv`, `google-genai`, `matplotlib`) are specified in [`requirements.txt`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/requirements.txt).
- [x] **API Keys & Secrets Excluded**: Local secrets file `.env` is ignored by Git in `.gitignore`. Real credentials are never committed.
- [x] **Environment Configuration**: Environment variables (`GEMINI_API_KEY`, `GEMINI_MODEL`) are cleanly managed via `python-dotenv` with a template in [`.env.example`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/.env.example).
- [x] **Deterministic Experiment Settings**: Gemini 3.1 Flash-Lite generation uses a controlled temperature (`temperature=0.2`) with system instructions loaded from ground-truth business rules.
- [x] **Ground-Truth Isolation**: Expected answer metadata is strictly omitted from LLM prompts to prevent data leakage.
- [x] **Final Dataset Curated**: Dataset contains exactly 60 test cases (`TC001`–`TC060`) across 4 language representations (English, Sinhala, Singlish, Code-mixed) and 3 difficulty levels.
- [x] **Dataset Validation Passes**: `python scripts/validate_final_dataset.py` passes with 0 schema or policy ID errors.
- [x] **Offline Unit Test Suite**: `python -m unittest discover tests` passes 100% of offline unit tests without making external network calls.
- [x] **Preserved Model Responses**: Raw model output text, latency timings, and API success flags are saved in [`data/processed/final_llm_responses.csv`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/data/processed/final_llm_responses.csv).
- [x] **Transparent Human Scoring Criteria**: 7-dimension scoring guidelines and threshold logic are documented in [`docs/scoring_guide.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/scoring_guide.md) and [`docs/evaluation_plan.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/evaluation_plan.md).
- [x] **Quantitative Metrics Formulas**: Mathematical definitions, denominators ($N_{\text{completed}}$), and grouped metric calculations are documented in [`docs/metrics_definition.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/metrics_definition.md).
- [x] **Failure Taxonomy Method**: Categorization of failed cases and partial-quality cases is documented in [`docs/failure_analysis.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/failure_analysis.md).
- [x] **Standalone Visualizations**: 300 DPI Matplotlib PNG charts are generated directly from saved result data tables into `results/figures/`.
- [x] **Cross-Checked Technical Report**: All numerical metrics in [`docs/final_technical_report.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/final_technical_report.md) are programmatically mapped and cross-checked against project result files in [`docs/report_data_sources.md`](file:///d:/Internship%20Tasks/Task%20-%202026.09.22/Sinhala-English-AI-Assistant/docs/report_data_sources.md).

---

## Pipeline Execution Sequence

To execute and verify the complete project pipeline:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run unit tests
python -m unittest discover tests

# 3. Validate dataset schema
python scripts/validate_final_dataset.py

# 4. Generate model responses (requires GEMINI_API_KEY in .env)
python scripts/run_final_evaluation.py

# 5. Create evaluation worksheet
python scripts/create_final_evaluation_worksheet.py

# 6. Score human evaluations
python scripts/score_final_evaluations.py

# 7. Compute quantitative metrics
python scripts/analyze_final_results.py

# 8. Render visualization charts and result tables
python scripts/generate_charts.py

# 9. Perform failure pattern analysis
python scripts/analyze_failures.py

# 10. Generate final technical report & data mapping
python scripts/generate_final_report.py
```
