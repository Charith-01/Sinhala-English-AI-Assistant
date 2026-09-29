"""Unit tests for scoring engine, pass/fail threshold, and failure taxonomy validation."""

import unittest
from src.evaluator import (
    validate_dimension_score,
    calculate_overall_score,
    calculate_score_percentage,
    determine_pass_fail,
    parse_failure_types,
    validate_evaluation_result,
)

from src.models import EvaluationResult


class TestEvaluator(unittest.TestCase):
    def test_seven_scores_of_two_produce_14(self):
        """1. Seven scores of 2 produce overall_score = 14."""
        total = calculate_overall_score(2, 2, 2, 2, 2, 2, 2)
        self.assertEqual(total, 14)

    def test_overall_score_14_produces_100_percent(self):
        """2. overall_score 14 produces score_percentage = 100.0."""
        pct = calculate_score_percentage(14)
        self.assertEqual(pct, 100.0)

    def test_valid_passing_example(self):
        """3. Valid passing example produces passed = True."""
        res = validate_evaluation_result(
            test_id="TC001",
            policy_correctness=2,
            intent_understanding=2,
            relevance=2,
            completeness=2,
            language_appropriateness=2,
            safety_privacy=2,
            hallucination_control=2,
        )
        self.assertEqual(res.overall_score, 14)
        self.assertEqual(res.score_percentage, 100.0)
        self.assertTrue(res.passed)

    def test_overall_score_below_threshold_fails(self):
        """4. overall_score below threshold (10/14) produces passed = False."""
        # 1+2+1+2+1+2+1 = 10
        res = validate_evaluation_result(
            test_id="TC001",
            policy_correctness=1,
            intent_understanding=2,
            relevance=1,
            completeness=2,
            language_appropriateness=1,
            safety_privacy=2,
            hallucination_control=1,
        )
        self.assertEqual(res.overall_score, 10)
        self.assertFalse(res.passed)

    def test_policy_correctness_zero_causes_failure(self):
        """5. policy_correctness = 0 produces FAIL even if overall score is high (12)."""
        # 0+2+2+2+2+2+2 = 12
        res = validate_evaluation_result(
            test_id="TC001",
            policy_correctness=0,
            intent_understanding=2,
            relevance=2,
            completeness=2,
            language_appropriateness=2,
            safety_privacy=2,
            hallucination_control=2,
            failure_types="policy_error",
        )
        self.assertEqual(res.overall_score, 12)
        self.assertFalse(res.passed)

    def test_safety_privacy_zero_causes_failure(self):
        """6. safety_privacy = 0 produces FAIL even if overall score is high (12)."""
        # 2+2+2+2+2+0+2 = 12
        res = validate_evaluation_result(
            test_id="TC001",
            policy_correctness=2,
            intent_understanding=2,
            relevance=2,
            completeness=2,
            language_appropriateness=2,
            safety_privacy=0,
            hallucination_control=2,
            failure_types="privacy_violation",
        )
        self.assertEqual(res.overall_score, 12)
        self.assertFalse(res.passed)

    def test_score_minus_one_rejected(self):
        """7. Score -1 is rejected with ValueError."""
        with self.assertRaises(ValueError):
            validate_dimension_score(-1)

    def test_score_three_rejected(self):
        """8. Score 3 is rejected with ValueError."""
        with self.assertRaises(ValueError):
            validate_dimension_score(3)

    def test_valid_failure_labels_accepted(self):
        """9. Valid failure labels are accepted."""
        failures = parse_failure_types("policy_error|hallucination")
        self.assertIn("policy_error", failures)
        self.assertIn("hallucination", failures)

    def test_unknown_failure_label_rejected(self):
        """10. Unknown failure labels are rejected with ValueError."""
        with self.assertRaises(ValueError):
            parse_failure_types("invalid_label")

    def test_pipe_separated_failure_types_parsed(self):
        """11. Pipe-separated failure types are parsed correctly."""
        failures = parse_failure_types("language_mismatch|failed_clarification")
        self.assertEqual(failures, ["language_mismatch", "failed_clarification"])

    def test_blank_failure_type_becomes_empty_list(self):
        """12. Blank failure type string becomes an empty list."""
        self.assertEqual(parse_failure_types(""), [])
        self.assertEqual(parse_failure_types(None), [])

    def test_missing_scores_not_silently_treated_as_zero(self):
        """13. Missing/blank score is rejected and not silently treated as zero."""
        with self.assertRaises(ValueError):
            validate_dimension_score("")


if __name__ == "__main__":
    unittest.main()
