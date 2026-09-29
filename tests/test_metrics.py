"""Unit tests for the quantitative metrics module (src/metrics.py)."""

import unittest
from typing import Any, Dict, List

from src.metrics import (
    EVALUATION_DIMENSIONS,
    calculate_api_reliability_metrics,
    calculate_clarification_performance,
    calculate_dimension_metrics,
    calculate_dimension_scores_by_language,
    calculate_escalation_performance,
    calculate_failure_type_frequency,
    calculate_hallucination_metrics,
    calculate_overall_fail_rate,
    calculate_overall_pass_rate,
    calculate_percentage_statistics,
    calculate_performance_by_group,
    calculate_primary_counts,
    calculate_privacy_safety_metrics,
    calculate_score_statistics,
    generate_all_metrics,
    validate_final_results_completeness,
)


class TestMetricsModule(unittest.TestCase):
    """Test suite for metrics.py functions."""

    def setUp(self) -> None:
        """Create synthetic mock evaluation rows for testing."""
        self.mock_completed_rows: List[Dict[str, Any]] = [
            {
                "test_id": "TC001",
                "category": "A. Normal customer-support queries",
                "language_type": "english",
                "difficulty": "easy",
                "generation_success": "true",
                "evaluation_status": "completed",
                "overall_score": "14",
                "score_percentage": "100.0",
                "passed": "true",
                "policy_correctness": "2",
                "intent_understanding": "2",
                "relevance": "2",
                "completeness": "2",
                "language_appropriateness": "2",
                "safety_privacy": "2",
                "hallucination_control": "2",
                "failure_types": "",
                "requires_clarification": "false",
                "requires_escalation": "false",
                "latency_seconds": "1.5",
            },
            {
                "test_id": "TC002",
                "category": "B. Policy-based questions",
                "language_type": "sinhala",
                "difficulty": "medium",
                "generation_success": "true",
                "evaluation_status": "completed",
                "overall_score": "10",
                "score_percentage": "71.43",
                "passed": "false",
                "policy_correctness": "1",
                "intent_understanding": "2",
                "relevance": "2",
                "completeness": "1",
                "language_appropriateness": "2",
                "safety_privacy": "2",
                "hallucination_control": "0",
                "failure_types": "policy_error|hallucination",
                "requires_clarification": "true",
                "requires_escalation": "false",
                "latency_seconds": "2.0",
            },
            {
                "test_id": "TC003",
                "category": "I. Privacy and sensitive-information requests",
                "language_type": "singlish",
                "difficulty": "hard",
                "generation_success": "true",
                "evaluation_status": "completed",
                "overall_score": "5",
                "score_percentage": "35.71",
                "passed": "false",
                "policy_correctness": "0",
                "intent_understanding": "1",
                "relevance": "1",
                "completeness": "1",
                "language_appropriateness": "1",
                "safety_privacy": "0",
                "hallucination_control": "1",
                "failure_types": "policy_error|privacy_violation|failed_clarification",
                "requires_clarification": "true",
                "requires_escalation": "true",
                "latency_seconds": "2.5",
            },
            {
                "test_id": "TC004",
                "category": "K. Human escalation cases",
                "language_type": "code_mixed",
                "difficulty": "medium",
                "generation_success": "true",
                "evaluation_status": "completed",
                "overall_score": "12",
                "score_percentage": "85.71",
                "passed": "true",
                "policy_correctness": "2",
                "intent_understanding": "2",
                "relevance": "2",
                "completeness": "2",
                "language_appropriateness": "2",
                "safety_privacy": "2",
                "hallucination_control": "0",
                "failure_types": "failed_escalation",
                "requires_clarification": "false",
                "requires_escalation": "true",
                "latency_seconds": "1.8",
            },
            {
                "test_id": "TC005",
                "category": "B. Policy-based questions",
                "language_type": "english",
                "difficulty": "easy",
                "generation_success": "false",
                "evaluation_status": "technical_failure",
                "overall_score": "",
                "score_percentage": "",
                "passed": "",
                "policy_correctness": "",
                "intent_understanding": "",
                "relevance": "",
                "completeness": "",
                "language_appropriateness": "",
                "safety_privacy": "",
                "hallucination_control": "",
                "failure_types": "",
                "requires_clarification": "false",
                "requires_escalation": "false",
                "latency_seconds": "0.5",
            },
        ]

    def test_pass_rate_calculation(self) -> None:
        """1. Test correct pass-rate and fail-rate calculations."""
        pr = calculate_overall_pass_rate(2, 4)
        fr = calculate_overall_fail_rate(2, 4)
        self.assertEqual(pr, 50.0)
        self.assertEqual(fr, 50.0)

    def test_average_score_calculation(self) -> None:
        """2. Test correct average score and percentage calculations."""
        scores = [14.0, 10.0, 5.0, 12.0]
        stats = calculate_score_statistics(scores)
        self.assertEqual(stats["mean"], 10.25)
        self.assertEqual(stats["median"], 11.0)
        self.assertEqual(stats["min"], 5.0)
        self.assertEqual(stats["max"], 14.0)

        pcts = [100.0, 71.43, 35.71, 85.71]
        pct_stats = calculate_percentage_statistics(pcts)
        self.assertAlmostEqual(pct_stats["mean"], 73.21, delta=0.1)

    def test_grouped_language_metrics(self) -> None:
        """3. Test grouped performance by language type."""
        result = calculate_performance_by_group(
            self.mock_completed_rows, "language_type", ["english", "sinhala", "singlish", "code_mixed"]
        )
        self.assertEqual(len(result), 4)
        eng = next(r for r in result if r["language_type"] == "english")
        self.assertEqual(eng["total"], 1)
        self.assertEqual(eng["passed"], 1)
        self.assertEqual(eng["pass_rate"], 100.0)

    def test_grouped_difficulty_metrics(self) -> None:
        """4. Test grouped performance by difficulty."""
        result = calculate_performance_by_group(
            self.mock_completed_rows, "difficulty", ["easy", "medium", "hard"]
        )
        easy = next(r for r in result if r["difficulty"] == "easy")
        self.assertEqual(easy["total"], 1)
        self.assertEqual(easy["passed"], 1)

        hard = next(r for r in result if r["difficulty"] == "hard")
        self.assertEqual(hard["total"], 1)
        self.assertEqual(hard["passed"], 0)

    def test_failure_type_parsing(self) -> None:
        """5 & 6. Test pipe-separated failure types and multi-label counts."""
        freqs = calculate_failure_type_frequency(self.mock_completed_rows)
        # Expect 4 completed rows
        pol_err = next(f for f in freqs if f["failure_type"] == "policy_error")
        self.assertEqual(pol_err["count"], 2)
        self.assertEqual(pol_err["percentage"], 50.0)

        priv_err = next(f for f in freqs if f["failure_type"] == "privacy_violation")
        self.assertEqual(priv_err["count"], 1)
        self.assertEqual(priv_err["percentage"], 25.0)

    def test_hallucination_metrics(self) -> None:
        """7. Test hallucination failure rate and zero-score rate."""
        res = calculate_hallucination_metrics(self.mock_completed_rows)
        # Explicit hallucination label in TC002 -> 1/4 = 25%
        self.assertEqual(res["explicit_hallucination_failure_rate"], 25.0)
        # hallucination_control == 0 in TC002, TC004 -> 2/4 = 50%
        self.assertEqual(res["hallucination_control_zero_rate"], 50.0)

    def test_privacy_safety_metrics(self) -> None:
        """8. Test privacy violation rate and zero-score rate."""
        res = calculate_privacy_safety_metrics(self.mock_completed_rows)
        # Explicit privacy_violation in TC003 -> 1/4 = 25%
        self.assertEqual(res["privacy_violation_rate"], 25.0)
        # safety_privacy == 0 in TC003 -> 1/4 = 25%
        self.assertEqual(res["safety_privacy_zero_rate"], 25.0)

    def test_clarification_performance(self) -> None:
        """9. Test clarification failure rate."""
        res = calculate_clarification_performance(self.mock_completed_rows)
        # requires_clarification == true in TC002, TC003 (total = 2)
        self.assertEqual(res["total_clarification_required"], 2)
        # failed_clarification in TC003 (count = 1)
        self.assertEqual(res["failed_clarification_count"], 1)
        self.assertEqual(res["failed_clarification_rate"], 50.0)

    def test_escalation_performance(self) -> None:
        """10. Test escalation failure rate."""
        res = calculate_escalation_performance(self.mock_completed_rows)
        # requires_escalation == true in TC003, TC004 (total = 2)
        self.assertEqual(res["total_escalation_required"], 2)
        # failed_escalation in TC004 (count = 1)
        self.assertEqual(res["failed_escalation_count"], 1)
        self.assertEqual(res["failed_escalation_rate"], 50.0)

    def test_dimension_score_distributions(self) -> None:
        """11. Test dimension score distributions and invariants."""
        dim_res = calculate_dimension_metrics(self.mock_completed_rows)
        for dim in EVALUATION_DIMENSIONS:
            dm = dim_res[dim]
            # Invariant: count_0 + count_1 + count_2 == 4
            self.assertEqual(dm["count_0"] + dm["count_1"] + dm["count_2"], 4)
            self.assertGreaterEqual(dm["mean_score"], 0.0)
            self.assertLessEqual(dm["mean_score"], 2.0)

    def test_technical_failures_excluded_from_quality_denominator(self) -> None:
        """12. Test technical failures excluded from model-quality denominator."""
        counts = calculate_primary_counts(self.mock_completed_rows)
        self.assertEqual(counts["total_test_cases"], 5)
        self.assertEqual(counts["technical_failure_count"], 1)
        self.assertEqual(counts["completed_evaluation_count"], 4)
        # Model-quality pass rate uses completed_count (4) as denominator
        pr = calculate_overall_pass_rate(counts["passed_count"], counts["completed_evaluation_count"])
        self.assertEqual(pr, 50.0)

    def test_zero_evaluated_case_denominator_handled_safely(self) -> None:
        """13. Test handling zero completed evaluated cases safely."""
        empty_rows: List[Dict[str, Any]] = [
            {
                "test_id": "TC001",
                "evaluation_status": "technical_failure",
                "generation_success": "false",
            }
        ]
        pr = calculate_overall_pass_rate(0, 0)
        self.assertEqual(pr, 0.0)

        halluc = calculate_hallucination_metrics(empty_rows)
        self.assertEqual(halluc["explicit_hallucination_failure_rate"], 0.0)

    def test_grouped_counts_consistency(self) -> None:
        """14. Test consistency of grouped counts matching total completed."""
        by_lang = calculate_performance_by_group(
            self.mock_completed_rows, "language_type", ["english", "sinhala", "singlish", "code_mixed"]
        )
        total_grouped = sum(b["total"] for b in by_lang)
        self.assertEqual(total_grouped, 4)

    def test_validation_and_integrity(self) -> None:
        """Test dataset integrity validator for results completeness."""
        summary = validate_final_results_completeness(self.mock_completed_rows)
        self.assertEqual(summary["total_test_cases"], 5)
        self.assertEqual(summary["completed_count"], 4)
        self.assertEqual(summary["technical_failure_count"], 1)
        self.assertEqual(summary["pending_count"], 0)
        self.assertEqual(summary["invalid_count"], 0)


if __name__ == "__main__":
    unittest.main()
