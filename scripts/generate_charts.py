"""Chart and Summary Table Generator Script.

Loads quantitative result tables from results/tables/ and results/metrics_summary.json,
generates polished standalone visualization charts into results/figures/,
and outputs final formatted summary CSV tables into results/tables/.
"""

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

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

from src.visualization import (
    plot_average_dimension_scores,
    plot_average_score_by_language,
    plot_dimension_scores_by_language,
    plot_failure_type_frequency,
    plot_latency_by_language,
    plot_pass_rate_by_category,
    plot_pass_rate_by_difficulty,
    plot_pass_rate_by_language,
)


def generate_final_summary_table(
    metrics_summary_path: Path, output_path: Path
) -> Optional[Path]:
    """Generate results/tables/final_summary_table.csv from metrics_summary.json."""
    if not metrics_summary_path.exists():
        print(f"Warning: {metrics_summary_path} not found. Skipping final_summary_table.csv")
        return None

    with open(metrics_summary_path, "r", encoding="utf-8") as f:
        m = json.load(f)

    exp = m.get("experiment_counts", {})
    overall = m.get("overall_performance", {})
    score_st = m.get("score_statistics", {})
    halluc = m.get("hallucination_metrics", {})
    priv = m.get("privacy_safety_metrics", {})
    api = m.get("api_reliability_metrics", {})

    summary_row = {
        "Model": "Gemini 3.1 Flash-Lite",
        "Total Test Cases": exp.get("total_test_cases", 0),
        "Completed Evaluations": exp.get("completed_evaluation_count", 0),
        "Passed": overall.get("passed_count", 0),
        "Failed": overall.get("failed_count", 0),
        "Overall Pass Rate": overall.get("overall_pass_rate", 0.0),
        "Average Score": score_st.get("overall_score", {}).get("mean", 0.0),
        "Average Score Percentage": score_st.get("score_percentage", {}).get("mean", 0.0),
        "Hallucination Failure Rate": halluc.get("explicit_hallucination_failure_rate", 0.0),
        "Privacy Violation Rate": priv.get("privacy_violation_rate", 0.0),
        "Generation Success Rate": api.get("generation_success_rate", 0.0),
        "Average Latency Seconds": api.get("average_latency_seconds", 0.0),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([summary_row])
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def generate_language_comparison_table(
    lang_csv_path: Path, output_path: Path
) -> Optional[Path]:
    """Generate results/tables/language_comparison_table.csv."""
    if not lang_csv_path.exists():
        print(f"Warning: {lang_csv_path} not found. Skipping language_comparison_table.csv")
        return None

    df = pd.read_csv(lang_csv_path)
    desired_order = ["english", "sinhala", "singlish", "code_mixed"]
    df["lang_lower"] = df["language_type"].str.lower()
    df["sort_key"] = df["lang_lower"].apply(
        lambda x: desired_order.index(x) if x in desired_order else 99
    )
    df_sorted = df.sort_values("sort_key").drop(columns=["lang_lower", "sort_key"])

    # Rename headers for publication formatting
    renames = {
        "language_type": "Language Type",
        "total": "Evaluated Cases",
        "passed": "Passed",
        "failed": "Failed",
        "pass_rate": "Pass Rate (%)",
        "avg_score": "Average Score",
        "avg_percentage": "Average Score Percentage (%)",
    }
    df_renamed = df_sorted.rename(columns=renames)
    df_renamed["Language Type"] = df_renamed["Language Type"].apply(
        lambda x: str(x).replace("_", "-").title() if str(x).lower() == "code_mixed" else str(x).title()
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_renamed.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def generate_difficulty_comparison_table(
    diff_csv_path: Path, output_path: Path
) -> Optional[Path]:
    """Generate results/tables/difficulty_comparison_table.csv."""
    if not diff_csv_path.exists():
        print(f"Warning: {diff_csv_path} not found. Skipping difficulty_comparison_table.csv")
        return None

    df = pd.read_csv(diff_csv_path)
    desired_order = ["easy", "medium", "hard"]
    df["diff_lower"] = df["difficulty"].str.lower()
    df["sort_key"] = df["diff_lower"].apply(
        lambda x: desired_order.index(x) if x in desired_order else 99
    )
    df_sorted = df.sort_values("sort_key").drop(columns=["diff_lower", "sort_key"])

    renames = {
        "difficulty": "Difficulty",
        "total": "Evaluated Cases",
        "passed": "Passed",
        "failed": "Failed",
        "pass_rate": "Pass Rate (%)",
        "avg_score": "Average Score",
        "avg_percentage": "Average Score Percentage (%)",
    }
    df_renamed = df_sorted.rename(columns=renames)
    df_renamed["Difficulty"] = df_renamed["Difficulty"].astype(str).str.title()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_renamed.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def generate_dimension_comparison_table(
    dim_csv_path: Path, output_path: Path
) -> Optional[Path]:
    """Generate results/tables/dimension_comparison_table.csv."""
    if not dim_csv_path.exists():
        print(f"Warning: {dim_csv_path} not found. Skipping dimension_comparison_table.csv")
        return None

    df = pd.read_csv(dim_csv_path)

    renames = {
        "dimension": "Dimension",
        "mean_score": "Mean Score",
        "mean_score_pct": "Mean Percentage (%)",
        "count_0": "Score 0 Count",
        "count_1": "Score 1 Count",
        "count_2": "Score 2 Count",
    }
    cols_to_keep = ["Dimension", "Mean Score", "Mean Percentage (%)", "Score 0 Count", "Score 1 Count", "Score 2 Count"]
    
    df_renamed = df.rename(columns=renames)
    available_cols = [c for c in cols_to_keep if c in df_renamed.columns]
    df_final = df_renamed[available_cols].copy()
    df_final["Dimension"] = df_final["Dimension"].apply(lambda x: str(x).replace("_", " ").title())

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def main() -> None:
    print("--- Running Visualizations and Chart Generation ---")

    tables_dir = root_dir / "results" / "tables"
    figures_dir = root_dir / "results" / "figures"
    metrics_json_path = root_dir / "results" / "metrics_summary.json"

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate Formatted Summary Tables
    print("\nGenerating formatted summary CSV tables...")
    t_summary = generate_final_summary_table(metrics_json_path, tables_dir / "final_summary_table.csv")
    t_lang = generate_language_comparison_table(tables_dir / "performance_by_language.csv", tables_dir / "language_comparison_table.csv")
    t_diff = generate_difficulty_comparison_table(tables_dir / "performance_by_difficulty.csv", tables_dir / "difficulty_comparison_table.csv")
    t_dim = generate_dimension_comparison_table(tables_dir / "dimension_scores.csv", tables_dir / "dimension_comparison_table.csv")

    # 2. Generate Chart Visualizations
    generated_figures: List[Path] = []
    skipped_figures: List[str] = []

    # Chart 1: Pass Rate by Language
    p_lang_csv = tables_dir / "performance_by_language.csv"
    if p_lang_csv.exists() and p_lang_csv.stat().st_size > 10:
        df_lang = pd.read_csv(p_lang_csv)
        if not df_lang.empty:
            p1 = plot_pass_rate_by_language(df_lang, figures_dir / "pass_rate_by_language.png")
            generated_figures.append(p1)
            p2 = plot_average_score_by_language(df_lang, figures_dir / "average_score_by_language.png")
            generated_figures.append(p2)
        else:
            skipped_figures.extend(["pass_rate_by_language.png", "average_score_by_language.png"])
    else:
        skipped_figures.extend(["pass_rate_by_language.png", "average_score_by_language.png"])

    # Chart 3: Pass Rate by Difficulty
    p_diff_csv = tables_dir / "performance_by_difficulty.csv"
    if p_diff_csv.exists() and p_diff_csv.stat().st_size > 10:
        df_diff = pd.read_csv(p_diff_csv)
        if not df_diff.empty:
            p3 = plot_pass_rate_by_difficulty(df_diff, figures_dir / "pass_rate_by_difficulty.png")
            generated_figures.append(p3)
        else:
            skipped_figures.append("pass_rate_by_difficulty.png")
    else:
        skipped_figures.append("pass_rate_by_difficulty.png")

    # Chart 4: Average Dimension Scores
    p_dim_csv = tables_dir / "dimension_scores.csv"
    if p_dim_csv.exists() and p_dim_csv.stat().st_size > 10:
        df_dim = pd.read_csv(p_dim_csv)
        if not df_dim.empty:
            p4 = plot_average_dimension_scores(df_dim, figures_dir / "average_dimension_scores.png")
            generated_figures.append(p4)
        else:
            skipped_figures.append("average_dimension_scores.png")
    else:
        skipped_figures.append("average_dimension_scores.png")

    # Chart 5: Failure Type Frequency
    p_fail_csv = tables_dir / "failure_type_frequency.csv"
    if p_fail_csv.exists() and p_fail_csv.stat().st_size > 10:
        df_fail = pd.read_csv(p_fail_csv)
        if not df_fail.empty:
            p5 = plot_failure_type_frequency(df_fail, figures_dir / "failure_type_frequency.png")
            generated_figures.append(p5)
        else:
            skipped_figures.append("failure_type_frequency.png")
    else:
        skipped_figures.append("failure_type_frequency.png")

    # Chart 6: Pass Rate by Category
    p_cat_csv = tables_dir / "performance_by_category.csv"
    if p_cat_csv.exists() and p_cat_csv.stat().st_size > 10:
        df_cat = pd.read_csv(p_cat_csv)
        if not df_cat.empty:
            p6 = plot_pass_rate_by_category(df_cat, figures_dir / "pass_rate_by_category.png")
            generated_figures.append(p6)
        else:
            skipped_figures.append("pass_rate_by_category.png")
    else:
        skipped_figures.append("pass_rate_by_category.png")

    # Chart 7: Dimension Scores by Language
    p_lang_dim_csv = tables_dir / "dimension_scores_by_language.csv"
    if p_lang_dim_csv.exists() and p_lang_dim_csv.stat().st_size > 10:
        df_lang_dim = pd.read_csv(p_lang_dim_csv)
        if not df_lang_dim.empty:
            p7 = plot_dimension_scores_by_language(df_lang_dim, figures_dir / "dimension_scores_by_language.png")
            generated_figures.append(p7)
        else:
            skipped_figures.append("dimension_scores_by_language.png")
    else:
        skipped_figures.append("dimension_scores_by_language.png")

    # Chart 8: Optional Generation Latency by Language
    raw_responses_csv = root_dir / "data" / "processed" / "final_llm_responses.csv"
    if raw_responses_csv.exists():
        df_resp = pd.read_csv(raw_responses_csv)
        if not df_resp.empty and "latency_seconds" in df_resp.columns and "language_type" in df_resp.columns:
            p8 = plot_latency_by_language(df_resp, figures_dir / "latency_by_language.png")
            generated_figures.append(p8)

    # 3. Print Generation Summary
    print("\nVISUALIZATION GENERATION SUMMARY")
    print("================================")
    print(f"Generated Figures ({len(generated_figures)}):")
    for fig_p in generated_figures:
        sz = fig_p.stat().st_size if fig_p.exists() else 0
        print(f"  - {fig_p.name} ({sz} bytes)")

    if skipped_figures:
        print(f"\nSkipped Figures ({len(skipped_figures)}) [Awaiting completed quantitative result tables]:")
        for sk in skipped_figures:
            print(f"  - {sk} (Source table in results/tables/ not generated yet)")

    print(f"\nFigures Directory: {figures_dir}")
    print(f"Tables Directory:  {tables_dir}")
    print("================================")


if __name__ == "__main__":
    main()
