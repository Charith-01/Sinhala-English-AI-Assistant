"""Script to generate the final human evaluation worksheet for TC001-TC060.

Pairs ground-truth test case definitions from data/raw/final_test_cases.csv
with generated LLM responses in data/processed/final_llm_responses.csv.
"""

import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root directory to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.test_case_loader import load_test_cases


def verify_input_alignment(raw_csv_path: Path, responses_csv_path: Path) -> Tuple[List, Dict]:
    """Verify input files and check alignment between ground-truth cases and model responses."""
    if not raw_csv_path.exists():
        raise FileNotFoundError(f"Raw test cases file not found at: {raw_csv_path}")

    if not responses_csv_path.exists():
        raise FileNotFoundError(f"LLM responses file not found at: {responses_csv_path}")

    test_cases_list = load_test_cases(raw_csv_path)
    if len(test_cases_list) != 60:
        raise ValueError(f"Expected 60 raw test cases, found {len(test_cases_list)}.")

    responses_map = {}
    with open(responses_csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tid = row["test_id"].strip()
            if tid in responses_map:
                raise ValueError(f"Duplicate test_id '{tid}' in responses CSV.")
            responses_map[tid] = row

    if len(responses_map) != 60:
        raise ValueError(f"Expected 60 response rows, found {len(responses_map)}.")

    # Check alignment
    for tc in test_cases_list:
        if tc.test_id not in responses_map:
            raise ValueError(f"Missing response row for test_id '{tc.test_id}'.")

        resp_row = responses_map[tc.test_id]
        if resp_row["user_input"].strip() != tc.user_input.strip():
            raise ValueError(f"user_input mismatch between raw and response CSV for {tc.test_id}.")
        if resp_row["language_type"].strip() != tc.language_type.strip():
            raise ValueError(f"language_type mismatch between raw and response CSV for {tc.test_id}.")
        if resp_row["difficulty"].strip() != tc.difficulty.strip():
            raise ValueError(f"difficulty mismatch between raw and response CSV for {tc.test_id}.")

    print("Input alignment verification passed: All 60 test cases match cleanly with response records.")
    return test_cases_list, responses_map


def build_final_worksheet(
    raw_csv_path: Path,
    responses_csv_path: Path,
    output_worksheet_path: Path,
):
    """Generate the final evaluation worksheet CSV pairing ground truth and model responses."""
    test_cases_list, responses_map = verify_input_alignment(raw_csv_path, responses_csv_path)

    worksheet_rows = []
    pending_count = 0
    tech_fail_count = 0

    for tc in test_cases_list:
        resp = responses_map[tc.test_id]

        gen_success = str(resp.get("success", "")).strip().lower() in {"true", "1"}
        gen_error = resp.get("error_message", "").strip()
        model_resp = resp.get("model_response", "")

        if gen_success:
            status = "pending"
            pending_count += 1
        else:
            status = "technical_failure"
            tech_fail_count += 1

        row = {
            # Test Identification
            "test_id": tc.test_id,
            "category": tc.category,
            "language_type": tc.language_type,
            "difficulty": tc.difficulty,
            # Customer Input
            "user_input": tc.user_input,
            # Ground Truth
            "expected_intent": tc.expected_intent,
            "policy_ids": "|".join(tc.policy_ids) if tc.policy_ids else "",
            "expected_response_language": tc.expected_response_language,
            "must_include": "|".join(tc.must_include) if tc.must_include else "",
            "must_not_include": "|".join(tc.must_not_include) if tc.must_not_include else "",
            "requires_clarification": "true" if tc.requires_clarification else "false",
            "requires_escalation": "true" if tc.requires_escalation else "false",
            "expected_behavior": tc.expected_behavior,
            "notes": tc.notes,
            # Model Output
            "model_name": resp.get("model_name", ""),
            "model_response": model_resp,
            "generation_success": "true" if gen_success else "false",
            "generation_error": gen_error,
            "latency_seconds": resp.get("latency_seconds", "0.0"),
            # Human Evaluation (blank)
            "policy_correctness": "",
            "intent_understanding": "",
            "relevance": "",
            "completeness": "",
            "language_appropriateness": "",
            "safety_privacy": "",
            "hallucination_control": "",
            "failure_types": "",
            "evaluator_notes": "",
            "evaluation_status": status,
            # Calculated Fields (blank)
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
        "notes",
        "model_name",
        "model_response",
        "generation_success",
        "generation_error",
        "latency_seconds",
        "policy_correctness",
        "intent_understanding",
        "relevance",
        "completeness",
        "language_appropriateness",
        "safety_privacy",
        "hallucination_control",
        "failure_types",
        "evaluator_notes",
        "evaluation_status",
        "overall_score",
        "score_percentage",
        "passed",
    ]

    output_worksheet_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_worksheet_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(worksheet_rows)

    print(f"Final evaluation worksheet generated successfully: {output_worksheet_path}")
    print(f"Total worksheet rows: {len(worksheet_rows)}")
    print(f"Pending human evaluation rows: {pending_count}")
    print(f"Technical failure rows: {tech_fail_count}")


def main():
    raw_csv = root_dir / "data" / "raw" / "final_test_cases.csv"
    responses_csv = root_dir / "data" / "processed" / "final_llm_responses.csv"
    worksheet_csv = root_dir / "data" / "processed" / "final_evaluation_worksheet.csv"

    build_final_worksheet(raw_csv, responses_csv, worksheet_csv)


if __name__ == "__main__":
    main()
