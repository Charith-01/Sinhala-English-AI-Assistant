"""Failure Analysis Runner Script.

Loads final evaluation results, runs qualitative & quantitative failure pattern analysis,
exports detailed failure tables to results/tables/, writes results/failure_analysis_summary.json,
generates the comprehensive factual report docs/failure_analysis.md, and prints a console summary.
"""

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

# Reconfigure stdout for utf-8 on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root directory to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.failure_analysis import (
    analyze_failures_by_category,
    analyze_failures_by_difficulty,
    analyze_failures_by_language,
    extract_completed_rows,
    extract_failed_cases,
    extract_partial_quality_cases,
    generate_failure_analysis_summary,
    select_representative_failure_examples,
)


def export_failure_csv_tables(
    rows: List[Dict[str, Any]], tables_dir: Path
) -> Dict[str, Path]:
    """Export detailed failure CSV tables."""
    tables_dir.mkdir(parents=True, exist_ok=True)
    paths = {}

    failed_cases = extract_failed_cases(rows)
    partial_cases = extract_partial_quality_cases(rows)
    by_lang = analyze_failures_by_language(rows)
    by_diff = analyze_failures_by_difficulty(rows)
    by_cat = analyze_failures_by_category(rows)
    rep_examples = select_representative_failure_examples(rows, max_examples=10)

    # 1. failed_cases_detail.csv
    p1 = tables_dir / "failed_cases_detail.csv"
    fields_1 = [
        "test_id",
        "language_type",
        "difficulty",
        "category",
        "user_input",
        "expected_behavior",
        "model_response",
        "overall_score",
        "score_percentage",
        "failure_types",
        "evaluator_notes",
    ]
    with open(p1, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields_1, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(failed_cases)
    paths["failed_cases_detail"] = p1

    # 2. partial_quality_cases.csv
    p2 = tables_dir / "partial_quality_cases.csv"
    fields_2 = [
        "test_id",
        "language_type",
        "difficulty",
        "category",
        "overall_score",
        "score_percentage",
        "dimensions_scored_one",
        "failure_types",
        "evaluator_notes",
    ]
    with open(p2, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields_2, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(partial_cases)
    paths["partial_quality_cases"] = p2

    # 3. failure_patterns_by_language.csv
    p3 = tables_dir / "failure_patterns_by_language.csv"
    with open(p3, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "language_type",
                "evaluated_cases",
                "failed_cases",
                "failure_rate",
                "partial_quality_cases",
                "most_common_failure_type",
                "most_common_failure_count",
            ],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(by_lang)
    paths["failure_patterns_by_language"] = p3

    # 4. failure_patterns_by_difficulty.csv
    p4 = tables_dir / "failure_patterns_by_difficulty.csv"
    with open(p4, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "difficulty",
                "evaluated_cases",
                "failed_cases",
                "failure_rate",
                "average_score",
                "most_common_failure_type",
            ],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(by_diff)
    paths["failure_patterns_by_difficulty"] = p4

    # 5. failure_patterns_by_category.csv
    p5 = tables_dir / "failure_patterns_by_category.csv"
    with open(p5, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "category",
                "evaluated_cases",
                "failed_cases",
                "failure_rate",
                "average_score",
                "most_common_failure_type",
            ],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(by_cat)
    paths["failure_patterns_by_category"] = p5

    # 6. representative_failure_examples.csv
    p6 = tables_dir / "representative_failure_examples.csv"
    fields_6 = [
        "test_id",
        "language_type",
        "category",
        "failure_type",
        "user_input",
        "expected_behavior",
        "model_response",
        "brief_observed_issue",
    ]
    with open(p6, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields_6, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rep_examples)
    paths["representative_failure_examples"] = p6

    return paths


def generate_failure_analysis_markdown(
    summary: Dict[str, Any], rep_examples: List[Dict[str, Any]], output_path: Path
) -> Path:
    """Generate docs/failure_analysis.md factual report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Failure-Pattern Analysis Report",
        "",
        "## 1. Overview",
        f"- **Model Evaluated**: Gemini 3.1 Flash-Lite (`gemini-3.1-flash-lite`)",
        f"- **Total Evaluated Cases**: {summary['total_evaluated']}",
        f"- **Primary Failed Cases**: {summary['failed_cases']} ({summary['failure_rate']}%)",
        f"- **Partial-Quality Cases**: {summary['partial_quality_cases']}",
        "",
        "## 2. Failure Type Distribution",
        "Frequency and percentage breakdown of human-labelled failure types across all completed evaluations:",
        "",
        "| Failure Label | Unique Case Count | Percentage of Evaluated (%) |",
        "| :--- | :---: | :---: |",
    ]

    for ft, cnt in summary["failure_type_counts"].items():
        pct = summary["failure_type_percentages"].get(ft, 0.0)
        lines.append(f"| `{ft}` | {cnt} | {pct}% |")

    lines.extend([
        "",
        "## 3. Language-Related Failure Patterns",
        "Observed performance and failure counts grouped by language modality:",
        "",
        "| Language Type | Evaluated Cases | Failed Cases | Failure Rate (%) | Partial-Quality Cases | Most Common Failure Label |",
        "| :--- | :---: | :---: | :---: | :---: | :--- |",
    ])

    for item in summary["failures_by_language"]:
        l_name = item["language_type"].capitalize()
        lines.append(
            f"| {l_name} | {item['evaluated_cases']} | {item['failed_cases']} | {item['failure_rate']}% | {item['partial_quality_cases']} | `{item['most_common_failure_type']}` |"
        )

    lines.extend([
        "",
        "## 4. Difficulty-Related Failure Patterns",
        "Observed failure rates across prompt difficulty levels:",
        "",
        "| Difficulty | Evaluated Cases | Failed Cases | Failure Rate (%) | Avg Failed Score | Most Common Failure Label |",
        "| :--- | :---: | :---: | :---: | :---: | :--- |",
    ])

    for item in summary["failures_by_difficulty"]:
        d_name = item["difficulty"].capitalize()
        lines.append(
            f"| {d_name} | {item['evaluated_cases']} | {item['failed_cases']} | {item['failure_rate']}% | {item['average_score']} / 14 | `{item['most_common_failure_type']}` |"
        )

    lines.extend([
        "",
        "## 5. Category-Level Failure Patterns",
        "Breakdown of failure occurrences by business inquiry category:",
        "",
        "| Category | Evaluated Cases | Failed Cases | Failure Rate (%) | Avg Score | Most Common Failure Label |",
        "| :--- | :---: | :---: | :---: | :---: | :--- |",
    ])

    for item in summary["failures_by_category"]:
        lines.append(
            f"| {item['category']} | {item['evaluated_cases']} | {item['failed_cases']} | {item['failure_rate']}% | {item['average_score']} / 14 | `{item['most_common_failure_type']}` |"
        )

    lines.extend([
        "",
        "## 6. Policy Errors",
        f"- **Recorded Policy Error Count**: {summary['policy_error_count']}",
        "Observed policy errors represent instances where the model provided incorrect return windows, wrong delivery timelines or fees, unverified cancellation guidelines, or unsupported payment methods contrary to `docs/business_rules.md`.",
        "",
        "## 7. Hallucination Patterns",
        f"- **Recorded Explicit Hallucination Count**: {summary['hallucination_count']}",
        "Hallucination occurrences involve cases where the model fabricated unannounced company policies, invented unsupported discount rules, or claimed non-existent system capabilities.",
        "",
        "## 8. Privacy and Safety Compliance",
        f"- **Recorded Privacy Violation Count**: {summary['privacy_violation_count']}",
    ])

    if summary["privacy_violation_count"] == 0:
        lines.append("No privacy violations were recorded in the evaluated dataset.")
    else:
        lines.append(f"Recorded {summary['privacy_violation_count']} instance(s) involving sensitive credential handling or data privacy issues.")

    lines.extend([
        "",
        "## 9. Clarification and Escalation Performance",
        f"- **Clarification Required Cases**: {summary['clarification_analysis']['total_clarification_required']}",
        f"- **Failed Clarification Count**: {summary['failed_clarification_count']} (Rate: {summary['clarification_analysis']['failed_clarification_rate']}%)",
        f"- **Escalation Required Cases**: {summary['escalation_analysis']['total_escalation_required']}",
        f"- **Failed Escalation Count**: {summary['failed_escalation_count']} (Rate: {summary['escalation_analysis']['failed_escalation_rate']}%)",
        "",
        "## 10. Language Appropriateness & Mismatch",
        f"- **Recorded Language Mismatch Count**: {summary['language_mismatch_count']}",
        f"- **Recorded Over-Refusal Count**: {summary['over_refusal_count']}",
        "Observed language mismatch issues involve responses generated in a language other than the expected response language or unnatural phrasing in code-mixed prompts.",
        "",
        "## 11. Incomplete Responses",
        f"- **Incomplete Response Count**: {summary['failure_type_counts'].get('incomplete_response', 0)}",
        "Incomplete responses occur when the model answers one part of a multi-condition query while ignoring additional essential conditions.",
        "",
        "## 12. Representative Failure Examples",
        "A selection of representative failure cases observed in the real evaluation dataset:",
        "",
        "| Test ID | Language | Category | Failure Label | Brief Observed Issue |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])

    for ex in rep_examples:
        lines.append(
            f"| `{ex['test_id']}` | {ex['language_type']} | {ex['category']} | `{ex['failure_type']}` | {ex['brief_observed_issue']} |"
        )

    lines.extend([
        "",
        "## 13. Summary of Observed Failure Patterns",
        "- All findings in this report are grounded strictly in empirical evaluation records.",
        "- Grouped performance and failure label frequencies reflect observed data distributions without speculative unverified training data claims.",
        "",
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return output_path


def main() -> None:
    print("--- Running Failure Pattern Analysis ---")

    results_file = root_dir / "data" / "processed" / "final_evaluation_results.csv"
    worksheet_file = root_dir / "data" / "processed" / "final_evaluation_worksheet.csv"
    target_file = results_file if results_file.exists() else worksheet_file

    if not target_file.exists():
        print(f"ERROR: Evaluation results file not found at {target_file}")
        sys.exit(1)

    print(f"Reading evaluation data from: {target_file}")
    rows: List[Dict[str, Any]] = []
    with open(target_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    completed = extract_completed_rows(rows)

    if not completed:
        print("\n" + "!" * 50)
        print("STOPPING FAILURE ANALYSIS")
        print("!" * 50)
        print("No completed human evaluations found in evaluation results file.")
        print("Failure analysis requires human-scored evaluations.")
        print("Please complete manual evaluation in data/processed/final_evaluation_worksheet.csv,")
        print("run scripts/score_final_evaluations.py, and re-run this script.")
        print("!" * 50)
        return

    # Generate summary & tables
    summary = generate_failure_analysis_summary(rows)
    tables_dir = root_dir / "results" / "tables"
    summary_json_path = root_dir / "results" / "failure_analysis_summary.json"
    doc_path = root_dir / "docs" / "failure_analysis.md"

    # Export JSON
    summary_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Export CSV tables
    export_failure_csv_tables(rows, tables_dir)

    # Export Markdown doc
    rep_examples = select_representative_failure_examples(rows, max_examples=10)
    generate_failure_analysis_markdown(summary, rep_examples, doc_path)

    # Print Console Summary
    print("\nFAILURE ANALYSIS SUMMARY")
    print("========================")
    print(f"Total Evaluated Cases:   {summary['total_evaluated']}")
    print(f"Primary Failed Cases:    {summary['failed_cases']} ({summary['failure_rate']}%)")
    print(f"Partial-Quality Cases:   {summary['partial_quality_cases']}")
    print("\nMost Frequent Failure Types:")
    for ft, cnt in list(summary['failure_type_counts'].items())[:5]:
        pct = summary['failure_type_percentages'].get(ft, 0.0)
        print(f"  - {ft}: {cnt} cases ({pct}%)")

    print("\nFailures by Language:")
    for item in summary['failures_by_language']:
        print(f"  - {item['language_type']}: {item['failed_cases']} failed / {item['evaluated_cases']} total (Rate: {item['failure_rate']}%)")

    print(f"\nSaved summary JSON to:      {summary_json_path}")
    print(f"Saved failure tables to:   {tables_dir}")
    print(f"Saved Markdown report to:  {doc_path}")
    print("========================")


if __name__ == "__main__":
    main()
