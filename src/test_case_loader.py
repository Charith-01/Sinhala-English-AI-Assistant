"""CSV test case loader and validator."""

import csv
from pathlib import Path
from typing import List, Union

from src.models import TestCase


def parse_bool(value: Union[str, bool]) -> bool:
    """Safely convert string or boolean value to python boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def parse_pipe_list(value: str) -> List[str]:
    """Parse pipe-separated string into a list of cleaned strings."""
    if not value or not isinstance(value, str):
        return []
    return [item.strip() for item in value.split("|") if item.strip()]


def load_test_cases(csv_path: Union[str, Path]) -> List[TestCase]:
    """Load evaluation test cases from a CSV file.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        List of TestCase objects.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Test case file not found at: {path}")

    test_cases: List[TestCase] = []

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_case = TestCase(
                test_id=row["test_id"].strip(),
                category=row["category"].strip(),
                language_type=row["language_type"].strip(),
                difficulty=row["difficulty"].strip(),
                user_input=row["user_input"].strip(),
                expected_intent=row["expected_intent"].strip(),
                policy_ids=parse_pipe_list(row.get("policy_ids", "")),
                expected_response_language=row.get("expected_response_language", "english").strip(),
                must_include=parse_pipe_list(row.get("must_include", "")),
                must_not_include=parse_pipe_list(row.get("must_not_include", "")),
                requires_clarification=parse_bool(row.get("requires_clarification", False)),
                requires_escalation=parse_bool(row.get("requires_escalation", False)),
                expected_behavior=row.get("expected_behavior", "").strip(),
                notes=row.get("notes", "").strip(),
            )
            test_cases.append(test_case)

    return test_cases
