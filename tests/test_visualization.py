"""Unit tests for the visualization module (src/visualization.py) and chart generator script (scripts/generate_charts.py)."""

import json
import tempfile
import unittest
from pathlib import Path
import pandas as pd

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
from scripts.generate_charts import (
    generate_difficulty_comparison_table,
    generate_dimension_comparison_table,
    generate_final_summary_table,
    generate_language_comparison_table,
)


class TestVisualizationModule(unittest.TestCase):
    """Test suite for visualization module functions."""

    def setUp(self) -> None:
        """Create sample DataFrames for testing visualizers."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)

        self.df_lang = pd.DataFrame([
            {"language_type": "english", "total": 15, "passed": 12, "failed": 3, "pass_rate": 80.0, "avg_score": 11.5, "avg_percentage": 82.14},
            {"language_type": "sinhala", "total": 15, "passed": 10, "failed": 5, "pass_rate": 66.67, "avg_score": 10.2, "avg_percentage": 72.86},
            {"language_type": "singlish", "total": 15, "passed": 9, "failed": 6, "pass_rate": 60.0, "avg_score": 9.5, "avg_percentage": 67.86},
            {"language_type": "code_mixed", "total": 15, "passed": 11, "failed": 4, "pass_rate": 73.33, "avg_score": 10.8, "avg_percentage": 77.14},
        ])

        self.df_diff = pd.DataFrame([
            {"difficulty": "easy", "total": 14, "passed": 12, "failed": 2, "pass_rate": 85.71, "avg_score": 12.1, "avg_percentage": 86.43},
            {"difficulty": "medium", "total": 24, "passed": 18, "failed": 6, "pass_rate": 75.0, "avg_score": 11.0, "avg_percentage": 78.57},
            {"difficulty": "hard", "total": 22, "passed": 12, "failed": 10, "pass_rate": 54.55, "avg_score": 8.9, "avg_percentage": 63.57},
        ])

        self.df_dim = pd.DataFrame([
            {"dimension": "policy_correctness", "mean_score": 1.6, "mean_score_pct": 80.0, "count_0": 5, "count_1": 10, "count_2": 45},
            {"dimension": "intent_understanding", "mean_score": 1.8, "mean_score_pct": 90.0, "count_0": 2, "count_1": 8, "count_2": 50},
            {"dimension": "relevance", "mean_score": 1.7, "mean_score_pct": 85.0, "count_0": 3, "count_1": 12, "count_2": 45},
            {"dimension": "completeness", "mean_score": 1.4, "mean_score_pct": 70.0, "count_0": 8, "count_1": 18, "count_2": 34},
            {"dimension": "language_appropriateness", "mean_score": 1.9, "mean_score_pct": 95.0, "count_0": 1, "count_1": 4, "count_2": 55},
            {"dimension": "safety_privacy", "mean_score": 1.95, "mean_score_pct": 97.5, "count_0": 0, "count_1": 3, "count_2": 57},
            {"dimension": "hallucination_control", "mean_score": 1.5, "mean_score_pct": 75.0, "count_0": 6, "count_1": 14, "count_2": 40},
        ])

        self.df_fail = pd.DataFrame([
            {"failure_type": "policy_error", "count": 12, "percentage": 20.0},
            {"failure_type": "incomplete_response", "count": 10, "percentage": 16.67},
            {"failure_type": "hallucination", "count": 6, "percentage": 10.0},
        ])

        self.df_cat = pd.DataFrame([
            {"category": "A. Normal customer-support queries", "pass_rate": 90.0},
            {"category": "B. Policy-based questions", "pass_rate": 75.0},
        ])

        self.df_lang_dim = pd.DataFrame([
            {"language_type": "english", "policy_correctness": 1.8, "intent_understanding": 1.9, "relevance": 1.9, "completeness": 1.7, "language_appropriateness": 2.0, "safety_privacy": 2.0, "hallucination_control": 1.7},
            {"language_type": "sinhala", "policy_correctness": 1.5, "intent_understanding": 1.7, "relevance": 1.6, "completeness": 1.3, "language_appropriateness": 1.8, "safety_privacy": 1.9, "hallucination_control": 1.4},
        ])

        self.df_latency = pd.DataFrame([
            {"language_type": "english", "latency_seconds": 2.5},
            {"language_type": "sinhala", "latency_seconds": 3.1},
        ])

    def tearDown(self) -> None:
        """Clean up temporary directory."""
        self.tmp_dir.cleanup()

    def test_plot_pass_rate_by_language(self) -> None:
        """1 & 2. Test chart creation and non-empty output file."""
        out_p = self.tmp_path / "test_pass_lang.png"
        res = plot_pass_rate_by_language(self.df_lang, out_p)
        self.assertTrue(res.exists())
        self.assertGreater(res.stat().st_size, 1000)

    def test_plot_average_score_by_language(self) -> None:
        """Test average score chart creation."""
        out_p = self.tmp_path / "test_avg_score_lang.png"
        res = plot_average_score_by_language(self.df_lang, out_p)
        self.assertTrue(res.exists())
        self.assertGreater(res.stat().st_size, 1000)

    def test_plot_pass_rate_by_difficulty(self) -> None:
        """Test pass rate by difficulty chart creation."""
        out_p = self.tmp_path / "test_pass_diff.png"
        res = plot_pass_rate_by_difficulty(self.df_diff, out_p)
        self.assertTrue(res.exists())
        self.assertGreater(res.stat().st_size, 1000)

    def test_plot_average_dimension_scores(self) -> None:
        """Test average dimension score chart creation."""
        out_p = self.tmp_path / "test_avg_dim.png"
        res = plot_average_dimension_scores(self.df_dim, out_p)
        self.assertTrue(res.exists())
        self.assertGreater(res.stat().st_size, 1000)

    def test_plot_failure_type_frequency(self) -> None:
        """Test failure frequency chart creation."""
        out_p = self.tmp_path / "test_fail_freq.png"
        res = plot_failure_type_frequency(self.df_fail, out_p)
        self.assertTrue(res.exists())
        self.assertGreater(res.stat().st_size, 1000)

    def test_plot_pass_rate_by_category(self) -> None:
        """Test pass rate by category chart creation."""
        out_p = self.tmp_path / "test_pass_cat.png"
        res = plot_pass_rate_by_category(self.df_cat, out_p)
        self.assertTrue(res.exists())
        self.assertGreater(res.stat().st_size, 1000)

    def test_plot_dimension_scores_by_language(self) -> None:
        """Test grouped dimension scores chart creation."""
        out_p = self.tmp_path / "test_dim_lang.png"
        res = plot_dimension_scores_by_language(self.df_lang_dim, out_p)
        self.assertTrue(res.exists())
        self.assertGreater(res.stat().st_size, 1000)

    def test_plot_latency_by_language(self) -> None:
        """Test latency by language chart creation."""
        out_p = self.tmp_path / "test_latency_lang.png"
        res = plot_latency_by_language(self.df_latency, out_p)
        self.assertTrue(res.exists())
        self.assertGreater(res.stat().st_size, 1000)

    def test_empty_dataframe_raises_value_error(self) -> None:
        """4. Test that empty DataFrame input raises ValueError."""
        empty_df = pd.DataFrame()
        with self.assertRaises(ValueError):
            plot_pass_rate_by_language(empty_df, self.tmp_path / "empty.png")

    def test_missing_column_raises_value_error(self) -> None:
        """6. Test required column validation."""
        bad_df = pd.DataFrame([{"invalid_col": 123}])
        with self.assertRaises(ValueError):
            plot_pass_rate_by_language(bad_df, self.tmp_path / "bad.png")

    def test_final_summary_table_generation(self) -> None:
        """7. Test final summary table generation contains required fields."""
        summary_data = {
            "experiment_counts": {"total_test_cases": 60, "completed_evaluation_count": 58},
            "overall_performance": {"passed_count": 48, "failed_count": 10, "overall_pass_rate": 82.76},
            "score_statistics": {"overall_score": {"mean": 11.8}, "score_percentage": {"mean": 84.29}},
            "hallucination_metrics": {"explicit_hallucination_failure_rate": 5.17},
            "privacy_safety_metrics": {"privacy_violation_rate": 0.0},
            "api_reliability_metrics": {"generation_success_rate": 96.67, "average_latency_seconds": 3.25},
        }

        json_p = self.tmp_path / "metrics_summary.json"
        with open(json_p, "w", encoding="utf-8") as f:
            json.dump(summary_data, f)

        out_csv = self.tmp_path / "final_summary_table.csv"
        generate_final_summary_table(json_p, out_csv)

        self.assertTrue(out_csv.exists())
        df_out = pd.read_csv(out_csv)
        self.assertEqual(len(df_out), 1)
        self.assertEqual(df_out.iloc[0]["Total Test Cases"], 60)
        self.assertEqual(df_out.iloc[0]["Completed Evaluations"], 58)
        self.assertEqual(df_out.iloc[0]["Overall Pass Rate"], 82.76)

    def test_language_comparison_table_ordering(self) -> None:
        """8. Test language comparison table ordering (English, Sinhala, Singlish, Code-mixed)."""
        lang_csv = self.tmp_path / "performance_by_language.csv"
        self.df_lang.to_csv(lang_csv, index=False)

        out_csv = self.tmp_path / "language_comparison_table.csv"
        generate_language_comparison_table(lang_csv, out_csv)

        self.assertTrue(out_csv.exists())
        df_out = pd.read_csv(out_csv)
        langs = list(df_out["Language Type"])
        self.assertEqual(langs, ["English", "Sinhala", "Singlish", "Code-Mixed"])

    def test_difficulty_comparison_table_ordering(self) -> None:
        """9. Test difficulty comparison table ordering (Easy, Medium, Hard)."""
        diff_csv = self.tmp_path / "performance_by_difficulty.csv"
        self.df_diff.to_csv(diff_csv, index=False)

        out_csv = self.tmp_path / "difficulty_comparison_table.csv"
        generate_difficulty_comparison_table(diff_csv, out_csv)

        self.assertTrue(out_csv.exists())
        df_out = pd.read_csv(out_csv)
        diffs = list(df_out["Difficulty"])
        self.assertEqual(diffs, ["Easy", "Medium", "Hard"])


if __name__ == "__main__":
    unittest.main()
