"""Quantitative Analysis Runner Script.

Reads data/processed/final_evaluation_results.csv, validates evaluation completeness,
computes all quantitative metrics, prints a concise console summary, and exports
structured JSON, TXT, and CSV result tables to results/ and results/tables/.
"""

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Reconfigure stdout for utf-8 on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root directory to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.metrics import (
    EVALUATION_DIMENSIONS,
    VALID_LANGUAGES,
    generate_all_metrics,
    validate_final_results_completeness,
)


def export_json_summary(metrics: Dict[str, Any], output_path: Path) -> None:
    """Export metrics summary to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)


def export_txt_summary(metrics: Dict[str, Any], output_path: Path) -> None:
    """Export human-readable text summary of quantitative metrics."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    exp = metrics["experiment_counts"]
    overall = metrics["overall_performance"]
    score_st = metrics["score_statistics"]
    api = metrics["api_reliability_metrics"]
    halluc = metrics["hallucination_metrics"]
    priv = metrics["privacy_safety_metrics"]
    clar = metrics["clarification_metrics"]
    esc = metrics["escalation_metrics"]

    lines = [
        "==================================================",
        "SINHALA-ENGLISH AI ASSISTANT FINAL EVALUATION SUMMARY",
        "==================================================",
        f"Total Experiment Cases:        {exp['total_test_cases']}",
        f"Successful Generations:        {exp['successful_generation_count']}",
        f"Technical API Failures:        {exp['technical_failure_count']}",
        f"Completed Human Evaluations:   {exp['completed_evaluation_count']}",
        f"Passed Cases:                  {overall['passed_count']}",
        f"Failed Cases:                  {overall['failed_count']}",
        f"Overall Pass Rate:             {overall['overall_pass_rate']}%",
        f"Overall Fail Rate:             {overall['overall_fail_rate']}%",
        "",
        "SCORE STATISTICS (Completed Cases)",
        "--------------------------------------------------",
        f"Mean Overall Score:            {score_st['overall_score']['mean']} / 14",
        f"Median Overall Score:          {score_st['overall_score']['median']} / 14",
        f"Min / Max Overall Score:       {score_st['overall_score']['min']} / {score_st['overall_score']['max']}",
        f"Mean Score Percentage:         {score_st['score_percentage']['mean']}%",
        f"Median Score Percentage:       {score_st['score_percentage']['median']}%",
        "",
        "PERFORMANCE BY LANGUAGE TYPE",
        "--------------------------------------------------",
        "Language      | Total | Passed | Failed | Pass Rate | Avg Score | Avg %",
    ]

    for item in metrics["performance_by_language"]:
        l_name = item["language_type"].ljust(13)
        tot = str(item["total"]).rjust(5)
        p = str(item["passed"]).rjust(6)
        f_cnt = str(item["failed"]).rjust(6)
        pr = f"{item['pass_rate']}%".rjust(9)
        sc = str(item["avg_score"]).rjust(9)
        pct = f"{item['avg_percentage']}%".rjust(7)
        lines.append(f"{l_name} | {tot} | {p} | {f_cnt} | {pr} | {sc} | {pct}")

    lines.extend([
        "",
        "PERFORMANCE BY DIFFICULTY LEVEL",
        "--------------------------------------------------",
        "Difficulty    | Total | Passed | Failed | Pass Rate | Avg Score | Avg %",
    ])

    for item in metrics["performance_by_difficulty"]:
        d_name = item["difficulty"].ljust(13)
        tot = str(item["total"]).rjust(5)
        p = str(item["passed"]).rjust(6)
        f_cnt = str(item["failed"]).rjust(6)
        pr = f"{item['pass_rate']}%".rjust(9)
        sc = str(item["avg_score"]).rjust(9)
        pct = f"{item['avg_percentage']}%".rjust(7)
        lines.append(f"{d_name} | {tot} | {p} | {f_cnt} | {pr} | {sc} | {pct}")

    lines.extend([
        "",
        "EVALUATION DIMENSIONS PERFORMANCE",
        "--------------------------------------------------",
        "Dimension                | Mean (0-2) | Score % | Count 0 | Count 1 | Count 2",
    ])

    for dim, dm in metrics["dimension_metrics"].items():
        d_lbl = dim.ljust(24)
        m_sc = str(dm["mean_score"]).rjust(10)
        m_pct = f"{dm['mean_score_pct']}%".rjust(7)
        c0 = str(dm["count_0"]).rjust(7)
        c1 = str(dm["count_1"]).rjust(7)
        c2 = str(dm["count_2"]).rjust(7)
        lines.append(f"{d_lbl} | {m_sc} | {m_pct} | {c0} | {c1} | {c2}")

    lines.extend([
        "",
        "FAILURE TYPE FREQUENCY",
        "--------------------------------------------------",
        "Failure Label            | Frequency | Percentage of Evaluated",
    ])

    for item in metrics["failure_type_frequency"]:
        ft_lbl = item["failure_type"].ljust(24)
        cnt = str(item["count"]).rjust(9)
        pct = f"{item['percentage']}%".rjust(22)
        lines.append(f"{ft_lbl} | {cnt} | {pct}")

    lines.extend([
        "",
        "SPECIAL DOMAIN METRICS",
        "--------------------------------------------------",
        f"Explicit Hallucination Rate:       {halluc['explicit_hallucination_failure_rate']}%",
        f"Hallucination Control Zero Rate:    {halluc['hallucination_control_zero_rate']}%",
        f"Explicit Privacy Violation Rate:   {priv['privacy_violation_rate']}%",
        f"Safety/Privacy Score Zero Rate:    {priv['safety_privacy_zero_rate']}%",
        f"Clarification Failure Rate:        {clar['failed_clarification_rate']}% ({clar['failed_clarification_count']}/{clar['total_clarification_required']})",
        f"Escalation Failure Rate:           {esc['failed_escalation_rate']}% ({esc['failed_escalation_count']}/{esc['total_escalation_required']})",
        "",
        "TECHNICAL API RELIABILITY",
        "--------------------------------------------------",
        f"Generation Success Rate:           {api['generation_success_rate']}%",
        f"Technical API Failure Rate:        {api['technical_failure_rate']}%",
        f"Average API Latency:               {api['average_latency_seconds']} sec",
        f"Median API Latency:                {api['median_latency_seconds']} sec",
        f"Min / Max API Latency:             {api['minimum_latency_seconds']} / {api['maximum_latency_seconds']} sec",
        "==================================================",
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def export_csv_tables(metrics: Dict[str, Any], tables_dir: Path) -> None:
    """Export metric tables to individual CSV files."""
    tables_dir.mkdir(parents=True, exist_ok=True)

    # 1. Performance by Language
    with open(tables_dir / "performance_by_language.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["language_type", "total", "passed", "failed", "pass_rate", "avg_score", "avg_percentage"])
        writer.writeheader()
        writer.writerows(metrics["performance_by_language"])

    # 2. Performance by Difficulty
    with open(tables_dir / "performance_by_difficulty.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["difficulty", "total", "passed", "failed", "pass_rate", "avg_score", "avg_percentage"])
        writer.writeheader()
        writer.writerows(metrics["performance_by_difficulty"])

    # 3. Performance by Category
    with open(tables_dir / "performance_by_category.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "total", "passed", "failed", "pass_rate", "avg_score", "avg_percentage"])
        writer.writeheader()
        writer.writerows(metrics["performance_by_category"])

    # 4. Dimension Scores
    dim_table = []
    for dim, dm in metrics["dimension_metrics"].items():
        row = {"dimension": dim}
        row.update(dm)
        dim_table.append(row)

    with open(tables_dir / "dimension_scores.csv", "w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["dimension", "mean_score", "median_score", "count_0", "count_1", "count_2", "pct_0", "pct_1", "pct_2", "mean_score_pct"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dim_table)

    # 5. Dimension Scores by Language
    lang_matrix = metrics["dimension_scores_by_language"]
    lang_dim_table = []
    for lang in VALID_LANGUAGES:
        row = {"language_type": lang}
        if lang in lang_matrix:
            row.update(lang_matrix[lang])
        lang_dim_table.append(row)

    with open(tables_dir / "dimension_scores_by_language.csv", "w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["language_type"] + EVALUATION_DIMENSIONS
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(lang_dim_table)

    # 6. Failure Type Frequency
    with open(tables_dir / "failure_type_frequency.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["failure_type", "count", "percentage"])
        writer.writeheader()
        writer.writerows(metrics["failure_type_frequency"])


def main() -> None:
    print("--- Running Final Quantitative Analysis ---")

    results_file = root_dir / "data" / "processed" / "final_evaluation_results.csv"
    worksheet_file = root_dir / "data" / "processed" / "final_evaluation_worksheet.csv"

    target_file = results_file if results_file.exists() else worksheet_file

    if not target_file.exists():
        print(f"ERROR: Target evaluation file not found at {target_file}")
        sys.exit(1)

    print(f"Reading evaluation data from: {target_file}")

    rows: List[Dict[str, Any]] = []
    with open(target_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    completeness = validate_final_results_completeness(rows)

    tot = completeness["total_test_cases"]
    comp = completeness["completed_count"]
    pend = completeness["pending_count"]
    tf = completeness["technical_failure_count"]
    inv = completeness["invalid_count"]

    print("\nEVALUATION DATASET INTEGRITY CHECK")
    print("==================================")
    print(f"Total Experiment Cases:   {tot}")
    print(f"Completed Evaluations:    {comp}")
    print(f"Pending Evaluations:      {pend}")
    print(f"Technical API Failures:   {tf}")
    print(f"Invalid Rows:             {inv}")

    if completeness["invalid_rows"]:
        print("\nERRORS ENCOUNTERED IN EVALUATION ROWS:")
        for err in completeness["invalid_rows"][:10]:
            print(f"  - {err}")
        if len(completeness["invalid_rows"]) > 10:
            print(f"  ... and {len(completeness['invalid_rows']) - 10} more.")

    if pend > 0:
        print("\n" + "!" * 50)
        print("STOPPING METRICS CALCULATION")
        print("!" * 50)
        print(f"Pending human evaluations remain for {pend} test case(s).")
        print("Final quantitative metrics will NOT be calculated until all non-failed responses are evaluated.")
        print("\nNext pending test IDs:")
        for pid in completeness["pending_ids"][:15]:
            print(f"  - {pid}")
        if len(completeness["pending_ids"]) > 15:
            print(f"  ... and {len(completeness['pending_ids']) - 15} more.")
        print("\nPlease complete manual scoring in data/processed/final_evaluation_worksheet.csv,")
        print("run scripts/score_final_evaluations.py, and re-run this script.")
        print("!" * 50)
        return

    if comp == 0:
        print("\nNo completed evaluations found. Unable to calculate quantitative metrics.")
        return

    # All evaluations completed - generate metrics
    print("\nCalculating quantitative metrics...")
    metrics = generate_all_metrics(rows)

    # Export summaries and tables
    summary_json_path = root_dir / "results" / "metrics_summary.json"
    summary_txt_path = root_dir / "results" / "metrics_summary.txt"
    tables_dir = root_dir / "results" / "tables"

    export_json_summary(metrics, summary_json_path)
    export_txt_summary(metrics, summary_txt_path)
    export_csv_tables(metrics, tables_dir)

    # Console Summary Output
    overall = metrics["overall_performance"]
    score_st = metrics["score_statistics"]
    halluc = metrics["hallucination_metrics"]
    priv = metrics["privacy_safety_metrics"]

    print("\nFINAL EVALUATION ANALYSIS")
    print("=========================")
    print(f"Model: Gemini 3.1 Flash-Lite")
    print(f"Experiment cases:       {tot}")
    print(f"Completed evaluations:  {comp}")
    print(f"Technical failures:     {tf}")
    print(f"Passed:                 {overall['passed_count']}")
    print(f"Failed:                 {overall['failed_count']}")
    print(f"Overall pass rate:      {overall['overall_pass_rate']}%")
    print(f"Average score:          {score_st['overall_score']['mean']} / 14")
    print(f"Average percentage:     {score_st['score_percentage']['mean']}%")
    print("\nLanguage performance:")
    for item in metrics["performance_by_language"]:
        print(f"  - {item['language_type']}: Pass Rate = {item['pass_rate']}%, Avg Score = {item['avg_score']}/14")
    print("\nTop failure counts:")
    for item in metrics["failure_type_frequency"][:5]:
        print(f"  - {item['failure_type']}: {item['count']} ({item['percentage']}%)")
    print(f"\nHallucination rate:     {halluc['explicit_hallucination_failure_rate']}%")
    print(f"Privacy violation rate: {priv['privacy_violation_rate']}%")
    print(f"\nSaved JSON summary to: {summary_json_path}")
    print(f"Saved TXT summary to:  {summary_txt_path}")
    print(f"Saved result tables to: {tables_dir}")
    print("=========================")


if __name__ == "__main__":
    main()
