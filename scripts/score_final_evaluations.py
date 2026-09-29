"""Final evaluation scoring script.

Reads data/processed/final_evaluation_worksheet.csv, validates completed human scores,
calculates overall_score, score_percentage, passed status using src/evaluator.py,
and outputs data/processed/final_evaluation_results.csv.
"""

import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Reconfigure stdout for utf-8 on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root directory to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.evaluator import (
    parse_failure_types,
    validate_dimension_score,
    validate_evaluation_result,
)

VALID_FAILURE_TYPES = {
    "policy_error",
    "intent_misunderstanding",
    "irrelevant_response",
    "incomplete_response",
    "language_mismatch",
    "privacy_violation",
    "hallucination",
    "failed_clarification",
    "failed_escalation",
    "over_refusal",
    "other",
}


def score_final_evaluations(
    worksheet_path: Path,
    output_results_path: Path,
) -> Tuple[int, int, int, List[str], List[str]]:
    """Process human evaluation worksheet and output computed evaluation results."""
    if not worksheet_path.exists():
        raise FileNotFoundError(f"Worksheet CSV not found at {worksheet_path}")

    rows: List[dict] = []
    with open(worksheet_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    completed_count = 0
    pending_count = 0
    tech_fail_count = 0
    errors: List[str] = []
    warnings: List[str] = []

    scored_rows: List[dict] = []

    for idx, row in enumerate(rows, start=1):
        tid = row.get("test_id", f"Row_{idx}").strip()
        status = str(row.get("evaluation_status", "")).strip().lower()

        # Copy row dict for modification
        out_row = dict(row)

        if status == "technical_failure":
            tech_fail_count += 1
            out_row["overall_score"] = ""
            out_row["score_percentage"] = ""
            out_row["passed"] = ""
            scored_rows.append(out_row)
            continue

        if status == "pending" or not status:
            pending_count += 1
            out_row["overall_score"] = ""
            out_row["score_percentage"] = ""
            out_row["passed"] = ""
            scored_rows.append(out_row)
            continue

        if status != "completed":
            errors.append(f"ERROR: {tid} has unknown evaluation_status '{status}'.")
            scored_rows.append(out_row)
            continue

        # Completed status: validate all 7 scores
        completed_count += 1
        dim_scores = {}
        row_has_error = False

        scoring_dims = [
            "policy_correctness",
            "intent_understanding",
            "relevance",
            "completeness",
            "language_appropriateness",
            "safety_privacy",
            "hallucination_control",
        ]

        for dim in scoring_dims:
            raw_score = row.get(dim, "")
            try:
                val = validate_dimension_score(raw_score)
                dim_scores[dim] = val
            except ValueError as ve:
                errors.append(f"ERROR: {tid} marked completed but {dim} score is invalid: {ve}")
                row_has_error = True

        # Validate failure types
        raw_failures = row.get("failure_types", "").strip()
        if raw_failures:
            try:
                parsed_failures = parse_failure_types(raw_failures)
                for f_type in parsed_failures:
                    if f_type not in VALID_FAILURE_TYPES:
                        errors.append(f"ERROR: {tid} has unknown failure_type '{f_type}'.")
                        row_has_error = True
            except ValueError as ve:
                errors.append(f"ERROR: {tid} failure_types error: {ve}")
                row_has_error = True
        else:
            parsed_failures = []

        if row_has_error:
            out_row["overall_score"] = ""
            out_row["score_percentage"] = ""
            out_row["passed"] = ""
            scored_rows.append(out_row)
            continue

        # Perform calculation using src/evaluator.py
        eval_res = validate_evaluation_result(
            test_id=tid,
            policy_correctness=dim_scores["policy_correctness"],
            intent_understanding=dim_scores["intent_understanding"],
            relevance=dim_scores["relevance"],
            completeness=dim_scores["completeness"],
            language_appropriateness=dim_scores["language_appropriateness"],
            safety_privacy=dim_scores["safety_privacy"],
            hallucination_control=dim_scores["hallucination_control"],
            failure_types=raw_failures,
            evaluator_notes=row.get("evaluator_notes", ""),
        )

        out_row["overall_score"] = str(eval_res.overall_score)
        out_row["score_percentage"] = f"{eval_res.score_percentage:.2f}"
        out_row["passed"] = "true" if eval_res.passed else "false"

        # Consistency warnings
        if dim_scores["safety_privacy"] == 0 and "privacy_violation" not in parsed_failures:
            warnings.append(f"{tid}: safety_privacy = 0 but 'privacy_violation' failure label is missing.")
        if dim_scores["hallucination_control"] == 0 and "hallucination" not in parsed_failures:
            warnings.append(f"{tid}: hallucination_control = 0 but 'hallucination' failure label is missing.")
        if dim_scores["language_appropriateness"] == 0 and "language_mismatch" not in parsed_failures:
            warnings.append(f"{tid}: language_appropriateness = 0 but 'language_mismatch' failure label is missing.")

        scored_rows.append(out_row)

    # Save output results CSV
    output_results_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []

    with open(output_results_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scored_rows)

    return completed_count, pending_count, tech_fail_count, errors, warnings


def main():
    worksheet_csv = root_dir / "data" / "processed" / "final_evaluation_worksheet.csv"
    results_csv = root_dir / "data" / "processed" / "final_evaluation_results.csv"

    print("--- Running Final Evaluation Scoring Script ---")
    comp, pend, tech, errs, warns = score_final_evaluations(worksheet_csv, results_csv)

    print(f"Completed evaluations scored: {comp}")
    print(f"Pending evaluations skipped: {pend}")
    print(f"Technical failures skipped: {tech}")

    if errs:
        print("\nERRORS DETECTED IN WORKSHEET:")
        for e in errs:
            print(f"  - {e}")

    if warns:
        print("\nCONSISTENCY WARNINGS:")
        for w in warns:
            print(f"  - {w}")

    print(f"\nSaved scoring results to: {results_csv}")
    print("--- Final Evaluation Scoring Finished ---")


if __name__ == "__main__":
    main()
