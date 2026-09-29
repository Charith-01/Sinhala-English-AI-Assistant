"""Scoring script for validating and computing results from human evaluation worksheets.

Reads data/processed/sample_evaluation_worksheet.csv and outputs completed scores to
data/processed/sample_evaluation_results.csv.
"""

import csv
import sys
from pathlib import Path

# Add project root directory to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.evaluator import (
    validate_evaluation_result,
    VALID_FAILURE_TYPES,
)



def score_evaluations(worksheet_csv: Path, output_results_csv: Path):
    """Read human evaluation worksheet, validate inputs, compute totals, and save results."""
    if not worksheet_csv.exists():
        print(f"Error: Evaluation worksheet file not found at {worksheet_csv}")
        print("Please run scripts/create_evaluation_worksheet.py first.")
        sys.exit(1)

    scored_rows = []
    incomplete_count = 0
    scored_count = 0

    dimension_fields = [
        "policy_correctness",
        "intent_understanding",
        "relevance",
        "completeness",
        "language_appropriateness",
        "safety_privacy",
        "hallucination_control",
    ]

    with open(worksheet_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_id = row["test_id"].strip()

            # Check if any required dimension score is blank
            missing_scores = [d for d in dimension_fields if not row.get(d, "").strip()]

            if missing_scores:
                incomplete_count += 1
                print(f"[INFO] {test_id}: Incomplete human evaluation scores (missing: {', '.join(missing_scores)}). Skipping scoring calculation.")
                # Preserve row as un-scored
                scored_rows.append(row)
                continue

            try:
                eval_res = validate_and_build_result(
                    test_id=test_id,
                    policy_correctness=row["policy_correctness"],
                    intent_understanding=row["intent_understanding"],
                    relevance=row["relevance"],
                    completeness=row["completeness"],
                    language_appropriateness=row["language_appropriateness"],
                    safety_privacy=row["safety_privacy"],
                    hallucination_control=row["hallucination_control"],
                    failure_types=row.get("failure_types", ""),
                    evaluator_notes=row.get("evaluator_notes", ""),
                )

                # Score Consistency Warnings
                if eval_res.safety_privacy == 0 and "privacy_violation" not in eval_res.failure_types:
                    print(f"[WARNING] {test_id}: safety_privacy score is 0 but 'privacy_violation' is not listed in failure_types!")

                if eval_res.hallucination_control == 0 and "hallucination" not in eval_res.failure_types:
                    print(f"[WARNING] {test_id}: hallucination_control score is 0 but 'hallucination' is not listed in failure_types!")

                if eval_res.language_appropriateness == 0 and "language_mismatch" not in eval_res.failure_types:
                    print(f"[WARNING] {test_id}: language_appropriateness score is 0 but 'language_mismatch' is not listed in failure_types!")

                if eval_res.policy_correctness == 0 and "policy_error" not in eval_res.failure_types:
                    print(f"[WARNING] {test_id}: policy_correctness score is 0 but 'policy_error' is not listed in failure_types!")

                # Update row with computed values
                row["policy_correctness"] = str(eval_res.policy_correctness)
                row["intent_understanding"] = str(eval_res.intent_understanding)
                row["relevance"] = str(eval_res.relevance)
                row["completeness"] = str(eval_res.completeness)
                row["language_appropriateness"] = str(eval_res.language_appropriateness)
                row["safety_privacy"] = str(eval_res.safety_privacy)
                row["hallucination_control"] = str(eval_res.hallucination_control)
                row["failure_types"] = "|".join(eval_res.failure_types)
                row["evaluator_notes"] = eval_res.evaluator_notes
                row["overall_score"] = str(eval_res.overall_score)
                row["score_percentage"] = f"{eval_res.score_percentage:.2f}"
                row["passed"] = "true" if eval_res.passed else "false"

                scored_count += 1

            except ValueError as ve:
                print(f"[ERROR] {test_id}: Validation error - {ve}")
                sys.exit(1)

            scored_rows.append(row)

    # Save to output results CSV
    fieldnames = list(scored_rows[0].keys()) if scored_rows else []
    output_results_csv.parent.mkdir(parents=True, exist_ok=True)

    with open(output_results_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scored_rows)

    print(f"Scoring complete! Results saved to: {output_results_csv}")
    print(f"Fully evaluated test cases: {scored_count}")
    print(f"Incomplete / pending test cases: {incomplete_count}")


def main():
    worksheet_csv = root_dir / "data" / "processed" / "sample_evaluation_worksheet.csv"
    results_csv = root_dir / "data" / "processed" / "sample_evaluation_results.csv"

    score_evaluations(worksheet_csv, results_csv)


if __name__ == "__main__":
    main()
