"""Unit tests for CSV test case loader."""

import unittest
from pathlib import Path
from src.test_case_loader import load_test_cases, parse_bool, parse_pipe_list
from src.models import TestCase


class TestLoader(unittest.TestCase):
    def test_parse_bool(self):
        self.assertTrue(parse_bool("true"))
        self.assertTrue(parse_bool("True"))
        self.assertTrue(parse_bool("TRUE"))
        self.assertFalse(parse_bool("false"))
        self.assertFalse(parse_bool("False"))
        self.assertFalse(parse_bool(""))

    def test_parse_pipe_list(self):
        self.assertEqual(parse_pipe_list("DEL-01|DEL-02"), ["DEL-01", "DEL-02"])
        self.assertEqual(parse_pipe_list("  RET-01 | REF-01  "), ["RET-01", "REF-01"])
        self.assertEqual(parse_pipe_list(""), [])

    def test_load_sample_test_cases(self):
        sample_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "sample_test_cases.csv"
        cases = load_test_cases(sample_path)
        self.assertEqual(len(cases), 4)

        tc1 = cases[0]
        self.assertIsInstance(tc1, TestCase)
        self.assertEqual(tc1.test_id, "TC001")
        self.assertEqual(tc1.language_type, "english")

        tc2 = cases[1]
        self.assertEqual(tc2.test_id, "TC002")
        self.assertEqual(tc2.language_type, "sinhala")
        self.assertTrue(tc2.requires_clarification)

    def test_missing_file_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            load_test_cases("non_existent_file.csv")


if __name__ == "__main__":
    unittest.main()
