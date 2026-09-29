"""Script to generate a human evaluation worksheet by pairing test cases with generated LLM responses.

Outputs data/processed/sample_evaluation_worksheet.csv with blank scoring fields for human evaluation.
"""

import csv
import sys
from pathlib import Path

# Add project root directory to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.test_case_loader import load_test_cases


def create_evaluation_worksheet(
    raw_csv_path: Path,
    responses_csv_path: Path,
    output_worksheet_path: Path,
):
    """Pair raw test cases with model responses to produce a human evaluation worksheet CSV."""
    if not raw_csv_path.exists():
        print(f"Error: Raw test cases file not found at {raw_csv_path}")
        sys.exit(1)

    if not responses_csv_path.exists():
        print(f"Error: LLM responses file not found at {responses_csv_path}")
        print("Please run scripts/run_sample_evaluation.py first to generate model responses.")
        sys.exit(1)

    # Load test cases into a dictionary by test_id
    test_cases_list = load_test_cases(raw_csv_path)
    test_cases_map = {tc.test_id: tc for tc in test_cases_list}

    # Load LLM responses into a dictionary by test_id
    responses_map = {}
    with open(responses_csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            responses_map[row["test_id"].strip()] = row

    worksheet_rows = []

    for test_id, tc in test_cases_map.items():
        resp = responses_map.get(test_id, {})

        model_name = resp.get("model_name", "")
        model_response = resp.get("model_response", "")

        row = {
            "test_id": tc.test_id,
            "category": tc.category,
            "language_type": tc.language_type,
            "difficulty": tc.difficulty,
            "user_input": tc.user_input,
            "expected_intent": tc.expected_intent,
            "policy_ids": "|".join(tc.policy_ids) if tc.policy_ids else "",
            "expected_response_language": tc.expected_response_language,
            "must_include": "|".join(tc.must_include) if tc.must_include else "",
            "must_not_include": "|".join(tc.must_not_include) if tc.must_not_include else "",
            "requires_clarification": "true" if tc.requires_clarification else "false",
            "requires_escalation": "true" if tc.requires_escalation else "false",
            "expected_behavior": tc.expected_behavior,
            "model_name": model_name,
            "model_response": model_response,
            # Blank human scoring columns
            "policy_correctness": "",
            "intent_understanding": "",
            "relevance": "",
            "completeness": "",
            "language_appropriateness": "",
            "safety_privacy": "",
            "hallucination_control": "",
            "failure_types": "",
            "evaluator_notes": "",
            "overall_score": "",
            "score_percentage": "",
            "passed": "",
        }
        worksheet_rows.append(row)

    fieldnames = [
        "test_id",
        "category",
        "language_type",
        "difficulty",
        "user_input",
        "expected_intent",
        "policy_ids",
        "expected_response_language",
        "must_include",
        "must_not_include",
        "requires_clarification",
        "requires_escalation",
        "expected_behavior",
        "model_name",
        "model_response",
        "policy_correctness",
        "intent_understanding",
        "relevance",
        "completeness",
        "language_appropriateness",
        "safety_privacy",
        "hallucination_control",
        "failure_types",
        "evaluator_notes",
        "overall_score",
        "score_percentage",
        "passed",
    ]

    output_worksheet_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_worksheet_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(worksheet_rows)

    print(f"Evaluation worksheet generated successfully: {output_worksheet_path}")
    print(f"Total test cases in worksheet: {len(worksheet_rows)}")


def main():
    raw_csv = root_dir / "data" / "raw" / "sample_test_cases.csv"
    responses_csv = root_dir / "data" / "processed" / "sample_llm_responses.csv"
    worksheet_csv = root_dir / "data" / "processed" / "sample_evaluation_worksheet.csv"

    create_evaluation_worksheet(raw_csv, responses_csv, worksheet_csv)


if __name__ == "__main__":
    main()
