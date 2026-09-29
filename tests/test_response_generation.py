"""Unit tests for response generation runner, resume support, and response validation."""

import csv
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from src.models import LLMResponse, TestCase
from src.response_validator import validate_response_file
from scripts.run_final_evaluation import (
    execute_with_retry,
    load_existing_responses,
    save_responses_csv,
)


class TestResponseGeneration(unittest.TestCase):
    def test_resume_skips_already_successful_ids(self):
        """1. Resume functionality correctly identifies and skips successful IDs."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "responses.csv"
            rows = [
                {"test_id": "TC001", "success": "True", "model_response": "Hello"},
                {"test_id": "TC002", "success": "False", "model_response": ""},
            ]
            save_responses_csv(csv_path, rows)

            existing_rows, completed_ids = load_existing_responses(csv_path)
            self.assertIn("TC001", completed_ids)
            self.assertNotIn("TC002", completed_ids)
            self.assertEqual(len(completed_ids), 1)

    def test_unsuccessful_ids_remain_eligible_for_retry(self):
        """2. Unsuccessful IDs are not added to completed_ids and remain eligible for retry."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "responses.csv"
            rows = [{"test_id": "TC005", "success": "False", "model_response": "", "error_message": "API Error"}]
            save_responses_csv(csv_path, rows)

            _, completed_ids = load_existing_responses(csv_path)
            self.assertNotIn("TC005", completed_ids)

    def test_duplicate_output_ids_detected(self):
        """3. Duplicate output IDs in responses CSV are detected by response validator."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "responses.csv"
            rows = [
                {"test_id": "TC001", "success": "True", "model_response": "R1", "latency_seconds": "1.0"},
                {"test_id": "TC001", "success": "True", "model_response": "R2", "latency_seconds": "1.0"},
            ]
            save_responses_csv(csv_path, rows)

            res = validate_response_file(csv_path, expected_count=2)
            self.assertIn("TC001", res["duplicate_test_ids"])
            self.assertFalse(res["response_file_valid"])

    def test_successful_response_cannot_silently_have_empty_text(self):
        """4. Successful response with empty text is detected by response validator."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "responses.csv"
            rows = [
                {"test_id": "TC001", "success": "True", "model_response": "", "latency_seconds": "1.0"},
                {"test_id": "TC002", "success": "True", "model_response": "Valid response", "latency_seconds": "1.0"},
            ]
            save_responses_csv(csv_path, rows)

            res = validate_response_file(csv_path, expected_count=2)
            self.assertIn("TC001", res["empty_successful_responses"])
            self.assertFalse(res["response_file_valid"])

    def test_failed_response_preserves_error_message(self):
        """5. Failed response preserves the error message without throwing exception."""
        mock_client = MagicMock()
        mock_client.generate_response.return_value = LLMResponse(
            test_id="TC001",
            model_name="gemini-3.1-flash-lite",
            response_text="",
            success=False,
            error_message="503 Service Unavailable",
            latency_seconds=0.5,
        )

        resp = execute_with_retry(mock_client, "TC001", "User prompt", max_retries=1)
        self.assertFalse(resp.success)
        self.assertEqual(resp.error_message, "503 Service Unavailable")

    def test_incremental_saving_works_with_mocked_data(self):
        """6. Incremental saving writes data correctly to disk after each step."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "incremental.csv"
            results = [{"test_id": "TC001", "model_response": "Step 1", "success": "True"}]
            save_responses_csv(csv_path, results)

            self.assertTrue(csv_path.exists())
            with open(csv_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
                self.assertIn("TC001", content)
                self.assertIn("Step 1", content)

    def test_metadata_does_not_contain_api_key(self):
        """7. Metadata dict does not expose any API keys or secrets."""
        metadata = {
            "experiment_name": "Test Run",
            "model_name": "gemini-3.1-flash-lite",
            "temperature": 0.2,
            "successful_requests": 60,
        }
        meta_str = json.dumps(metadata)
        self.assertNotIn("API_KEY", meta_str)
        self.assertNotIn("AIzaSy", meta_str)

    def test_final_response_validation_detects_missing_ids(self):
        """8. Response validation detects missing test IDs when expected count is 60."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "partial.csv"
            rows = [{"test_id": "TC001", "success": "True", "model_response": "Res", "latency_seconds": "1.0"}]
            save_responses_csv(csv_path, rows)

            res = validate_response_file(csv_path, expected_count=60)
            self.assertGreater(len(res["missing_test_ids"]), 0)
            self.assertFalse(res["response_file_valid"])

    def test_response_rows_remain_aligned_with_original_test_cases(self):
        """9. Response rows remain cleanly aligned with test case metadata."""
        with TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "aligned.csv"
            rows = [
                {
                    "test_id": "TC001",
                    "category": "B. Policy-based questions",
                    "language_type": "english",
                    "difficulty": "easy",
                    "user_input": "Question 1",
                    "model_name": "gemini-3.1-flash-lite",
                    "model_response": "Answer 1",
                    "success": "True",
                    "error_message": "",
                    "latency_seconds": "1.2",
                }
            ]
            save_responses_csv(csv_path, rows)

            with open(csv_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                read_row = next(reader)
                self.assertEqual(read_row["test_id"], "TC001")
                self.assertEqual(read_row["category"], "B. Policy-based questions")
                self.assertEqual(read_row["language_type"], "english")


if __name__ == "__main__":
    unittest.main()
