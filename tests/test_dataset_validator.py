"""Unit tests for the dataset_validator module."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.dataset_validator import (
    validate_booleans,
    validate_dataset,
    validate_enums,
    validate_language_sanity,
    validate_list_fields_and_behavior,
    validate_policy_ids,
    validate_required_fields,
    validate_test_count,
    validate_user_inputs_and_duplicates,
)


class TestDatasetValidator(unittest.TestCase):
    def setUp(self):
        self.sample_valid_row = {
            "test_id": "TC001",
            "category": "B. Policy-based questions",
            "language_type": "english",
            "difficulty": "easy",
            "user_input": "What is the return policy?",
            "expected_intent": "return_policy_query",
            "policy_ids": "RET-01",
            "expected_response_language": "english",
            "must_include": "14 calendar days",
            "must_not_include": "30 days",
            "requires_clarification": "false",
            "requires_escalation": "false",
            "expected_behavior": "Explain the 14-day return policy.",
            "notes": "Sample test case",
        }

    def test_valid_sequential_ids_pass(self):
        """1. Valid sequential IDs pass without errors."""
        rows = [
            dict(self.sample_valid_row, test_id=f"TC{idx:03d}")
            for idx in range(1, 61)
        ]
        errors, warnings = [], []
        validate_test_count(rows, errors, warnings)
        self.assertEqual(len(errors), 0)

    def test_missing_id_detected(self):
        """2. Missing ID is detected as an error."""
        rows = [dict(self.sample_valid_row, test_id="")]
        errors, warnings = [], []
        validate_test_count(rows, errors, warnings)
        self.assertTrue(any("Missing test_id" in err for err in errors))

    def test_duplicate_id_detected(self):
        """3. Duplicate ID is detected as an error."""
        rows = [
            dict(self.sample_valid_row, test_id="TC001"),
            dict(self.sample_valid_row, test_id="TC001"),
        ]
        errors, warnings = [], []
        validate_test_count(rows, errors, warnings)
        self.assertTrue(any("Duplicate test_id" in err for err in errors))

    def test_invalid_language_type_detected(self):
        """4. Invalid language type is detected as an error."""
        rows = [dict(self.sample_valid_row, language_type="french")]
        errors, warnings = [], []
        validate_enums(rows, errors, warnings)
        self.assertTrue(any("invalid language_type" in err for err in errors))

    def test_invalid_difficulty_detected(self):
        """5. Invalid difficulty is detected as an error."""
        rows = [dict(self.sample_valid_row, difficulty="extreme")]
        errors, warnings = [], []
        validate_enums(rows, errors, warnings)
        self.assertTrue(any("invalid difficulty" in err for err in errors))

    def test_unknown_policy_id_detected(self):
        """6. Unknown policy ID is detected as an error."""
        rows = [dict(self.sample_valid_row, policy_ids="INVALID-99")]
        errors = []
        validate_policy_ids(rows, errors)
        self.assertTrue(any("unknown policy_id" in err for err in errors))

    def test_duplicate_user_input_detected(self):
        """7. Duplicate user_input is detected as an error."""
        rows = [
            dict(self.sample_valid_row, test_id="TC001", user_input="Same input text"),
            dict(self.sample_valid_row, test_id="TC002", user_input="Same input text"),
        ]
        errors, warnings = [], []
        validate_user_inputs_and_duplicates(rows, errors, warnings)
        self.assertTrue(any("exact duplicate user_input" in err for err in errors))

    def test_invalid_sinhala_language_sanity_case_produces_warning(self):
        """8. Sinhala language_type without Sinhala Unicode produces warning."""
        rows = [
            dict(
                self.sample_valid_row,
                language_type="sinhala",
                user_input="Pure English text with no Sinhala script",
            )
        ]
        warnings = []
        validate_language_sanity(rows, warnings)
        self.assertTrue(any("no Sinhala Unicode" in warn for warn in warnings))

    def test_invalid_code_mixed_sanity_case_produces_warning(self):
        """9. Code-mixed language_type without both scripts produces warning."""
        rows = [
            dict(
                self.sample_valid_row,
                language_type="code_mixed",
                user_input="Pure English text only",
            )
        ]
        warnings = []
        validate_language_sanity(rows, warnings)
        self.assertTrue(any("does not contain both Sinhala Unicode and Latin text" in warn for warn in warnings))

    def test_invalid_pipe_separated_field_detected(self):
        """10. Malformed pipe-separated syntax (e.g. Python list syntax) is detected as error."""
        rows = [dict(self.sample_valid_row, must_include='["RET-01", "REF-01"]')]
        errors, warnings = [], []
        validate_list_fields_and_behavior(rows, errors, warnings)
        self.assertTrue(any("malformed must_include syntax" in err for err in errors))

    def test_valid_clarification_escalation_values_work(self):
        """11. Valid clarification and escalation boolean strings parse correctly."""
        rows = [
            dict(self.sample_valid_row, requires_clarification="true", requires_escalation="false"),
            dict(self.sample_valid_row, requires_clarification="false", requires_escalation="true"),
        ]
        errors = []
        clar, esc = validate_booleans(rows, errors)
        self.assertEqual(len(errors), 0)
        self.assertEqual(clar, 1)
        self.assertEqual(esc, 1)

    def test_validation_passed_false_when_errors_exist(self):
        """12. validation_passed is False when error count > 0."""
        csv_header = "test_id,category,language_type,difficulty,user_input,expected_intent,policy_ids,expected_response_language,must_include,must_not_include,requires_clarification,requires_escalation,expected_behavior,notes\n"
        invalid_row = "TC001,INVALID_CAT,english,easy,input,intent,,english,,,false,false,behavior,\n"

        with TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "invalid.csv"
            csv_file.write_text(csv_header + invalid_row, encoding="utf-8-sig")

            res = validate_dataset(csv_file)
            self.assertFalse(res["validation_passed"])
            self.assertGreater(res["error_count"], 0)

    def test_warnings_alone_do_not_fail_validation(self):
        """13. Warnings alone leave validation_passed as True."""
        csv_header = "test_id,category,language_type,difficulty,user_input,expected_intent,policy_ids,expected_response_language,must_include,must_not_include,requires_clarification,requires_escalation,expected_behavior,notes\n"
        langs = ["english", "sinhala", "singlish", "code_mixed"]
        rows_str = ""
        for i in range(1, 61):
            lang = langs[(i - 1) % 4]
            if i == 1:
                # Warning trigger: sinhala language_type with English input
                rows_str += f"TC{i:03d},B. Policy-based questions,sinhala,easy,English text only question {i},intent,RET-01,sinhala,must,not,false,false,Explain return policy.,notes\n"
            elif lang == "code_mixed":
                rows_str += f"TC{i:03d},B. Policy-based questions,code_mixed,easy,Mage order eka සහ text detail {i},intent,RET-01,code_mixed,must,not,false,false,Explain return policy.,notes\n"
            elif lang == "sinhala":
                rows_str += f"TC{i:03d},B. Policy-based questions,sinhala,easy,මගේ ඇණවුම විස්තරය {i},intent,RET-01,sinhala,must,not,false,false,Explain return policy.,notes\n"
            elif lang == "singlish":
                rows_str += f"TC{i:03d},B. Policy-based questions,singlish,easy,mage order eka vistharaya {i},intent,RET-01,singlish,must,not,false,false,Explain return policy.,notes\n"
            else:
                rows_str += f"TC{i:03d},B. Policy-based questions,english,easy,Unique English query input text detail {i},intent,RET-01,english,must,not,false,false,Explain return policy.,notes\n"

        with TemporaryDirectory() as tmpdir:
            csv_file = Path(tmpdir) / "warning_only.csv"
            csv_file.write_text(csv_header + rows_str, encoding="utf-8-sig")

            res = validate_dataset(csv_file)
            self.assertTrue(res["validation_passed"])
            self.assertEqual(res["error_count"], 0)
            self.assertGreater(res["warning_count"], 0)


if __name__ == "__main__":
    unittest.main()
