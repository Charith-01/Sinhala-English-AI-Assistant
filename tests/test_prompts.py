"""Unit tests for prompt building logic and ground-truth leakage prevention."""

import unittest
from pathlib import Path
from src.prompts import get_system_instruction, load_business_rules


class TestPrompts(unittest.TestCase):
    def test_load_business_rules(self):
        """Verify business rules load successfully and contain expected headers."""
        rules = load_business_rules()
        self.assertIn("LankaCart", rules)
        self.assertIn("DEL-01", rules)
        self.assertIn("RET-01", rules)

    def test_system_instruction_contains_rules_and_guidelines(self):
        """Verify system instruction contains operational rules and business knowledge base."""
        instruction = get_system_instruction()
        self.assertIn("LankaCart", instruction)
        self.assertIn("OPERATIONAL GUIDELINES", instruction)
        self.assertIn("LANKACART OFFICIAL BUSINESS RULES & KNOWLEDGE BASE", instruction)
        self.assertIn("DEL-01", instruction)

    def test_no_ground_truth_leakage_in_system_instruction(self):
        """Verify ground-truth evaluation fields are NOT included in the system instruction."""
        instruction = get_system_instruction()
        prohibited_leakage_terms = [
            "expected_intent",
            "policy_ids",
            "expected_response_language",
            "must_include",
            "must_not_include",
            "requires_clarification",
            "requires_escalation",
            "expected_behavior",
            "notes",
            "expected scores",
        ]
        for term in prohibited_leakage_terms:
            self.assertNotIn(
                term,
                instruction,
                f"Ground-truth evaluation field '{term}' found in system instruction!",
            )


if __name__ == "__main__":
    unittest.main()
