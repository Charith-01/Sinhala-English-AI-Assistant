"""Unit tests for final evaluation worksheet creation, progress tracking, and final scoring."""

import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.check_evaluation_progress import check_progress
from scripts.create_final_evaluation_worksheet import (
    build_final_worksheet,
    verify_input_alignment,
)
from scripts.score_final_evaluations import score_final_evaluations


class TestEvaluationWorksheetAndScoring(unittest.TestCase):
    def setUp(self):
        self.raw_header = "test_id,category,language_type,difficulty,user_input,expected_intent,policy_ids,expected_response_language,must_include,must_not_include,requires_clarification,requires_escalation,expected_behavior,notes\n"
        self.resp_header = "test_id,category,language_type,difficulty,user_input,model_name,model_response,success,error_message,latency_seconds\n"

        self.sample_raw_row = (
            "TC001,B. Policy-based questions,english,easy,What is the return policy?,return_policy_query,RET-01,english,14 calendar days,30 days,false,false,Explain return policy.,Notes\n"
        )
        self.sample_resp_row_success = (
            "TC001,B. Policy-based questions,english,easy,What is the return policy?,gemini-3.1-flash-lite,14 days return policy.,True,,1.2\n"
        )
        self.sample_resp_row_failure = (
            "TC001,B. Policy-based questions,english,easy,What is the return policy?,gemini-3.1-flash-lite,,False,503 Service Unavailable,0.5\n"
        )

    def test_correct_joining_by_test_id_and_alignment(self):
        """1. Raw test cases and response rows join cleanly by test_id."""
        with TemporaryDirectory() as tmpdir:
            raw_path = Path(tmpdir) / "raw.csv"
            resp_path = Path(tmpdir) / "resp.csv"
            ws_path = Path(tmpdir) / "worksheet.csv"

            # Create 60 test case rows
            raw_content = self.raw_header
            resp_content = self.resp_header
            for i in range(1, 61):
                raw_content += f"TC{i:03d},B. Policy-based questions,english,easy,Input {i},intent,RET-01,english,must,not,false,false,Behavior {i},note\n"
                resp_content += f"TC{i:03d},B. Policy-based questions,english,easy,Input {i},gemini-3.1-flash-lite,Response {i},True,,1.0\n"

            raw_path.write_text(raw_content, encoding="utf-8-sig")
            resp_path.write_text(resp_content, encoding="utf-8-sig")

            tcs, rmap = verify_input_alignment(raw_path, resp_path)
            self.assertEqual(len(tcs), 60)
            self.assertEqual(len(rmap), 60)

            build_final_worksheet(raw_path, resp_path, ws_path)
            self.assertTrue(ws_path.exists())

            with open(ws_path, "r", encoding="utf-8-sig") as f:
                reader = list(csv.DictReader(f))
                self.assertEqual(len(reader), 60)
                self.assertEqual(reader[0]["test_id"], "TC001")
                self.assertEqual(reader[0]["evaluation_status"], "pending")

    def test_technical_failure_status_creation(self):
        """2. Technical API failure rows create technical_failure evaluation_status."""
        with TemporaryDirectory() as tmpdir:
            raw_path = Path(tmpdir) / "raw.csv"
            resp_path = Path(tmpdir) / "resp.csv"
            ws_path = Path(tmpdir) / "worksheet.csv"

            raw_content = self.raw_header
            resp_content = self.resp_header
            for i in range(1, 61):
                raw_content += f"TC{i:03d},B. Policy-based questions,english,easy,Input {i},intent,RET-01,english,must,not,false,false,Behavior {i},note\n"
                success_val = "False" if i == 1 else "True"
                resp_val = "" if i == 1 else f"Response {i}"
                err_val = "503 Error" if i == 1 else ""
                resp_content += f"TC{i:03d},B. Policy-based questions,english,easy,Input {i},gemini-3.1-flash-lite,{resp_val},{success_val},{err_val},1.0\n"

            raw_path.write_text(raw_content, encoding="utf-8-sig")
            resp_path.write_text(resp_content, encoding="utf-8-sig")

            build_final_worksheet(raw_path, resp_path, ws_path)

            with open(ws_path, "r", encoding="utf-8-sig") as f:
                reader = list(csv.DictReader(f))
                self.assertEqual(reader[0]["evaluation_status"], "technical_failure")
                self.assertEqual(reader[0]["generation_error"], "503 Error")
                self.assertEqual(reader[1]["evaluation_status"], "pending")

    def test_completed_row_scoring_and_pending_non_scoring(self):
        """3. Completed rows are scored using evaluator.py, while pending/technical_failure rows are not scored."""
        with TemporaryDirectory() as tmpdir:
            ws_path = Path(tmpdir) / "worksheet.csv"
            res_path = Path(tmpdir) / "results.csv"

            fieldnames = [
                "test_id", "category", "language_type", "difficulty", "user_input",
                "expected_intent", "policy_ids", "expected_response_language",
                "must_include", "must_not_include", "requires_clarification",
                "requires_escalation", "expected_behavior", "notes", "model_name",
                "model_response", "generation_success", "generation_error",
                "latency_seconds", "policy_correctness", "intent_understanding",
                "relevance", "completeness", "language_appropriateness",
                "safety_privacy", "hallucination_control", "failure_types",
                "evaluator_notes", "evaluation_status", "overall_score",
                "score_percentage", "passed",
            ]

            row1 = {f: "" for f in fieldnames}
            row1.update({
                "test_id": "TC001", "category": "B", "language_type": "english", "difficulty": "easy",
                "user_input": "Input 1", "model_response": "Resp 1", "generation_success": "true",
                "policy_correctness": "2", "intent_understanding": "2", "relevance": "2",
                "completeness": "2", "language_appropriateness": "2", "safety_privacy": "2",
                "hallucination_control": "2", "evaluation_status": "completed",
            })

            row2 = {f: "" for f in fieldnames}
            row2.update({
                "test_id": "TC002", "category": "B", "language_type": "english", "difficulty": "easy",
                "user_input": "Input 2", "model_response": "Resp 2", "generation_success": "true",
                "evaluation_status": "pending",
            })

            row3 = {f: "" for f in fieldnames}
            row3.update({
                "test_id": "TC003", "category": "B", "language_type": "english", "difficulty": "easy",
                "user_input": "Input 3", "generation_success": "false", "generation_error": "503 Error",
                "evaluation_status": "technical_failure",
            })

            with open(ws_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows([row1, row2, row3])

            comp, pend, tech, errs, warns = score_final_evaluations(ws_path, res_path)
            self.assertEqual(comp, 1)
            self.assertEqual(pend, 1)
            self.assertEqual(tech, 1)
            self.assertEqual(len(errs), 0)

            with open(res_path, "r", encoding="utf-8-sig") as f:
                scored = list(csv.DictReader(f))
                self.assertEqual(scored[0]["overall_score"], "14")
                self.assertEqual(scored[0]["score_percentage"], "100.00")
                self.assertEqual(scored[0]["passed"], "true")
                self.assertEqual(scored[1]["overall_score"], "")
                self.assertEqual(scored[1]["passed"], "")
                self.assertEqual(scored[2]["overall_score"], "")
                self.assertEqual(scored[2]["passed"], "")

    def test_invalid_completed_score_and_failure_label_rejected(self):
        """4. Invalid completed dimension scores or invalid failure labels trigger validation errors."""
        with TemporaryDirectory() as tmpdir:
            ws_path = Path(tmpdir) / "worksheet.csv"
            res_path = Path(tmpdir) / "results.csv"

            fieldnames = [
                "test_id", "category", "language_type", "difficulty", "user_input",
                "expected_intent", "policy_ids", "expected_response_language",
                "must_include", "must_not_include", "requires_clarification",
                "requires_escalation", "expected_behavior", "notes", "model_name",
                "model_response", "generation_success", "generation_error",
                "latency_seconds", "policy_correctness", "intent_understanding",
                "relevance", "completeness", "language_appropriateness",
                "safety_privacy", "hallucination_control", "failure_types",
                "evaluator_notes", "evaluation_status", "overall_score",
                "score_percentage", "passed",
            ]

            row1 = {f: "" for f in fieldnames}
            row1.update({
                "test_id": "TC001", "category": "B", "language_type": "english", "difficulty": "easy",
                "user_input": "Input 1", "model_response": "Resp 1", "generation_success": "true",
                "policy_correctness": "3", "intent_understanding": "2", "relevance": "2",
                "completeness": "2", "language_appropriateness": "2", "safety_privacy": "2",
                "hallucination_control": "2", "evaluation_status": "completed",
            })

            row2 = {f: "" for f in fieldnames}
            row2.update({
                "test_id": "TC002", "category": "B", "language_type": "english", "difficulty": "easy",
                "user_input": "Input 2", "model_response": "Resp 2", "generation_success": "true",
                "policy_correctness": "1", "intent_understanding": "1", "relevance": "1",
                "completeness": "1", "language_appropriateness": "1", "safety_privacy": "1",
                "hallucination_control": "1", "failure_types": "invalid_label_name",
                "evaluation_status": "completed",
            })

            with open(ws_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows([row1, row2])

            comp, pend, tech, errs, warns = score_final_evaluations(ws_path, res_path)
            self.assertGreater(len(errs), 0)
            self.assertTrue(any("policy_correctness score is invalid" in e for e in errs))
            self.assertTrue(any("Unknown failure label 'invalid_label_name'" in e for e in errs))


if __name__ == "__main__":
    unittest.main()
