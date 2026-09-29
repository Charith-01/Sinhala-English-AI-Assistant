"""Dataset validator module for final evaluation dataset validation.

Performs thorough verification of evaluation test cases against schema definitions,
business rules, policy IDs, linguistic rules, and consistency checks.
"""

import csv
import difflib
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

VALID_LANGUAGES = {"english", "sinhala", "singlish", "code_mixed"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_CATEGORIES = {
    "A. Normal customer-support queries",
    "B. Policy-based questions",
    "C. Sinhala language understanding",
    "D. Singlish understanding",
    "E. Sinhala-English code-mixed understanding",
    "F. Typographical and grammatical errors",
    "G. Ambiguous queries",
    "H. Context / multi-turn queries",
    "I. Privacy and sensitive-information requests",
    "J. Hallucination resistance",
    "K. Human escalation cases",
    "L. Out-of-scope queries",
    "M. Adversarial / misleading requests",
}

VALID_POLICY_IDS = {
    "DEL-01", "DEL-02", "DEL-03", "DEL-04", "DEL-05", "DEL-06",
    "RET-01", "RET-02", "RET-03", "RET-04",
    "REF-01",
    "PAY-01", "PAY-02", "PAY-03",
    "ACC-01",
    "PRO-01",
    "PRI-01", "PRI-02",
    "ESC-01", "ESC-02",
    "OUT-01",
    "BEH-01", "BEH-02", "BEH-03", "BEH-04", "BEH-05", "BEH-06", "BEH-07", "BEH-08",
}

SINHALA_UNICODE_PATTERN = re.compile(r"[\u0D80-\u0DFF]")
LATIN_PATTERN = re.compile(r"[a-zA-Z]")


def has_sinhala_unicode(text: str) -> bool:
    """Check if text contains Sinhala Unicode characters."""
    return bool(SINHALA_UNICODE_PATTERN.search(text))


def has_latin_text(text: str) -> bool:
    """Check if text contains Latin alphabet characters."""
    return bool(LATIN_PATTERN.search(text))


def validate_test_count(rows: List[Dict[str, str]], errors: List[str], warnings: List[str]):
    """Verify test case count, ID formatting, and sequential ordering."""
    total_cases = len(rows)
    if total_cases != 60:
        errors.append(f"Expected exactly 60 test cases, but found {total_cases}.")

    seen_ids = set()
    for idx, row in enumerate(rows, start=1):
        test_id = row.get("test_id", "").strip()
        if not test_id:
            errors.append(f"Row {idx}: Missing test_id.")
            continue

        match = re.match(r"^TC(\d{3})$", test_id)
        if not match:
            errors.append(f"{test_id}: Invalid test_id format. Expected pattern TC001-TC060.")
        else:
            id_num = int(match.group(1))
            if id_num != idx:
                warnings.append(f"{test_id}: Non-sequential ID. Expected TC{idx:03d} at row {idx}.")

        if test_id in seen_ids:
            errors.append(f"Duplicate test_id found: {test_id}.")
        seen_ids.add(test_id)


def validate_required_fields(rows: List[Dict[str, str]], errors: List[str]):
    """Verify that all mandatory schema fields are present and non-empty."""
    required_fields = [
        "test_id",
        "category",
        "language_type",
        "difficulty",
        "user_input",
        "expected_intent",
        "expected_response_language",
        "requires_clarification",
        "requires_escalation",
        "expected_behavior",
    ]

    for idx, row in enumerate(rows, start=1):
        test_id = row.get("test_id", f"Row_{idx}").strip()
        for field in required_fields:
            val = row.get(field, None)
            if val is None or not str(val).strip():
                errors.append(f"ERROR: {test_id} - required field '{field}' is missing or empty.")


def validate_enums(
    rows: List[Dict[str, str]],
    errors: List[str],
    warnings: List[str],
) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, int]]:
    """Validate language_type, difficulty, and category enum values and collect distributions."""
    lang_dist: Dict[str, int] = {}
    diff_dist: Dict[str, int] = {}
    cat_dist: Dict[str, int] = {}

    for row in rows:
        test_id = row.get("test_id", "Unknown").strip()

        # Language Type
        lang = row.get("language_type", "").strip()
        if lang not in VALID_LANGUAGES:
            errors.append(f"ERROR: {test_id} - invalid language_type '{lang}'.")
        else:
            lang_dist[lang] = lang_dist.get(lang, 0) + 1

        # Difficulty
        diff = row.get("difficulty", "").strip()
        if diff not in VALID_DIFFICULTIES:
            errors.append(f"ERROR: {test_id} - invalid difficulty '{diff}'.")
        else:
            diff_dist[diff] = diff_dist.get(diff, 0) + 1

        # Category
        cat = row.get("category", "").strip()
        if cat not in VALID_CATEGORIES:
            errors.append(f"ERROR: {test_id} - unknown or invalid category '{cat}'.")
        else:
            cat_dist[cat] = cat_dist.get(cat, 0) + 1

    # Check for language distribution warnings
    for lang in VALID_LANGUAGES:
        count = lang_dist.get(lang, 0)
        if count == 0:
            errors.append(f"ERROR: Language type '{lang}' has 0 test cases.")
        elif count < 10:
            warnings.append(f"Language type '{lang}' is underrepresented with only {count} cases.")

    # Check for difficulty distribution warnings
    for diff in VALID_DIFFICULTIES:
        count = diff_dist.get(diff, 0)
        if count < 2:
            warnings.append(f"Difficulty level '{diff}' is underrepresented with only {count} cases.")

    return lang_dist, diff_dist, cat_dist


def validate_policy_ids(
    rows: List[Dict[str, str]],
    errors: List[str],
) -> Tuple[Dict[str, int], int, int]:
    """Verify that all referenced policy IDs exist in ground-truth business rules."""
    policy_counts: Dict[str, int] = {}
    cases_with_policies = 0
    cases_without_policies = 0

    for row in rows:
        test_id = row.get("test_id", "Unknown").strip()
        raw_policies = row.get("policy_ids", "").strip()

        if not raw_policies:
            cases_without_policies += 1
            continue

        cases_with_policies += 1
        # Check for malformed syntax like RET-01||REF-01 or Python list ["RET-01"]
        if "||" in raw_policies or "[" in raw_policies or "]" in raw_policies:
            errors.append(f"ERROR: {test_id} - malformed policy_ids syntax '{raw_policies}'.")

        policies = [p.strip() for p in raw_policies.split("|") if p.strip()]
        seen_in_row = set()

        for policy in policies:
            if policy not in VALID_POLICY_IDS:
                errors.append(f"ERROR: {test_id} - unknown policy_id '{policy}'.")
            else:
                policy_counts[policy] = policy_counts.get(policy, 0) + 1

            if policy in seen_in_row:
                errors.append(f"ERROR: {test_id} - duplicate policy_id '{policy}' in same test case.")
            seen_in_row.add(policy)

    return policy_counts, cases_with_policies, cases_without_policies


def validate_booleans(
    rows: List[Dict[str, str]],
    errors: List[str],
) -> Tuple[int, int]:
    """Validate requires_clarification and requires_escalation boolean fields."""
    clarification_count = 0
    escalation_count = 0

    valid_bool_strings = {"true", "false", "1", "0"}

    for row in rows:
        test_id = row.get("test_id", "Unknown").strip()

        for field_name in ["requires_clarification", "requires_escalation"]:
            val_str = str(row.get(field_name, "")).strip().lower()
            if val_str not in valid_bool_strings:
                errors.append(f"ERROR: {test_id} - invalid boolean for '{field_name}': '{val_str}'.")

        # Parse counts
        if str(row.get("requires_clarification", "")).strip().lower() in {"true", "1"}:
            clarification_count += 1
        if str(row.get("requires_escalation", "")).strip().lower() in {"true", "1"}:
            escalation_count += 1

    return clarification_count, escalation_count


def validate_user_inputs_and_duplicates(
    rows: List[Dict[str, str]],
    errors: List[str],
    warnings: List[str],
    sample_csv_path: Optional[Union[str, Path]] = None,
):
    """Check exact, normalized, near-duplicates, and development sample overlap."""
    seen_inputs: Dict[str, str] = {}
    seen_norm_inputs: Dict[str, str] = {}

    for row in rows:
        test_id = row.get("test_id", "Unknown").strip()
        user_input = row.get("user_input", "").strip()

        if not user_input:
            errors.append(f"ERROR: {test_id} - user_input is empty.")
            continue

        # Exact duplicate check
        if user_input in seen_inputs:
            errors.append(
                f"ERROR: {test_id} has exact duplicate user_input as {seen_inputs[user_input]}."
            )
        else:
            seen_inputs[user_input] = test_id

        # Normalized duplicate check (lowercase, collapsed whitespace)
        norm_input = re.sub(r"\s+", " ", user_input.strip().lower())
        if norm_input in seen_norm_inputs:
            prev_id = seen_norm_inputs[norm_input]
            if prev_id != test_id and user_input not in seen_inputs:
                warnings.append(
                    f"{test_id} has normalized duplicate input with {prev_id}."
                )
        else:
            seen_norm_inputs[norm_input] = test_id

    # Near-duplicate check using SequenceMatcher
    input_tuples = [(r.get("test_id", "").strip(), r.get("user_input", "").strip()) for r in rows]
    for i in range(len(input_tuples)):
        id1, text1 = input_tuples[i]
        if not text1:
            continue
        for j in range(i + 1, len(input_tuples)):
            id2, text2 = input_tuples[j]
            if not text2:
                continue
            ratio = difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
            if ratio > 0.88 and text1 != text2:
                warnings.append(
                    f"Near-duplicate user_input detected between {id1} and {id2} (similarity: {ratio:.2f})."
                )

    # Check against development sample CSV if provided
    if sample_csv_path:
        sample_path = Path(sample_csv_path)
        if sample_path.exists():
            with open(sample_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for s_row in reader:
                    s_id = s_row.get("test_id", "Sample").strip()
                    s_input = s_row.get("user_input", "").strip()
                    if s_input in seen_inputs:
                        warnings.append(
                            f"{seen_inputs[s_input]} in final dataset exactly duplicates development sample {s_id}."
                        )


def validate_language_sanity(rows: List[Dict[str, str]], warnings: List[str]):
    """Perform non-destructive linguistic sanity checks."""
    for row in rows:
        test_id = row.get("test_id", "Unknown").strip()
        lang_type = row.get("language_type", "").strip()
        user_input = row.get("user_input", "").strip()

        has_sin = has_sinhala_unicode(user_input)
        has_lat = has_latin_text(user_input)

        if lang_type == "sinhala" and not has_sin:
            warnings.append(f"{test_id}: language_type is 'sinhala' but user_input has no Sinhala Unicode.")
        elif lang_type == "english" and has_sin:
            warnings.append(f"{test_id}: language_type is 'english' but user_input contains Sinhala Unicode.")
        elif lang_type == "singlish" and has_sin:
            warnings.append(f"{test_id}: language_type is 'singlish' but user_input contains Sinhala Unicode.")
        elif lang_type == "code_mixed" and (not has_sin or not has_lat):
            warnings.append(f"{test_id}: language_type is 'code_mixed' but user_input does not contain both Sinhala Unicode and Latin text.")


def validate_list_fields_and_behavior(
    rows: List[Dict[str, str]],
    errors: List[str],
    warnings: List[str],
):
    """Validate list formatting syntax and expected behavior sanity."""
    for row in rows:
        test_id = row.get("test_id", "Unknown").strip()
        user_input = row.get("user_input", "").strip()
        expected_behavior = row.get("expected_behavior", "").strip()

        # List syntax check for must_include and must_not_include
        for field_name in ["must_include", "must_not_include"]:
            raw_val = row.get(field_name, "").strip()
            if "||" in raw_val or "[" in raw_val or "]" in raw_val:
                errors.append(f"ERROR: {test_id} - malformed {field_name} syntax '{raw_val}'.")

        # Expected behavior sanity check
        if expected_behavior == user_input and user_input != "":
            errors.append(f"ERROR: {test_id} - expected_behavior is identical to user_input.")
        elif len(expected_behavior) > 350:
            warnings.append(f"{test_id}: expected_behavior is unusually long ({len(expected_behavior)} chars).")

        # Expected response language check
        resp_lang = row.get("expected_response_language", "").strip()
        if resp_lang not in VALID_LANGUAGES:
            errors.append(f"ERROR: {test_id} - invalid expected_response_language '{resp_lang}'.")

        # Clarification consistency check
        req_clar = str(row.get("requires_clarification", "")).strip().lower() in {"true", "1"}
        if req_clar:
            eb_lower = expected_behavior.lower()
            keywords = ["ask", "clarif", "request", "missing", "inquire", "verify", "order id", "date"]
            if not any(k in eb_lower for k in keywords):
                warnings.append(f"{test_id}: requires_clarification is True but expected_behavior may not explicitly mention asking for clarification.")

        # Escalation consistency check
        req_esc = str(row.get("requires_escalation", "")).strip().lower() in {"true", "1"}
        if req_esc:
            eb_lower = expected_behavior.lower()
            keywords = ["escalat", "human", "agent", "ticket", "handoff", "representative"]
            if not any(k in eb_lower for k in keywords):
                warnings.append(f"{test_id}: requires_escalation is True but expected_behavior may not explicitly mention human escalation.")


def validate_dataset(
    csv_path: Union[str, Path],
    sample_csv_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Comprehensive validation function for evaluation dataset CSV.

    Args:
        csv_path: Path to final dataset CSV file.
        sample_csv_path: Path to development sample CSV file for duplicate comparison.

    Returns:
        Dictionary containing error_count, warning_count, distributions, and validation status.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset CSV file not found at: {path}")

    rows: List[Dict[str, str]] = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    errors: List[str] = []
    warnings: List[str] = []

    # Run modular validators
    validate_test_count(rows, errors, warnings)
    validate_required_fields(rows, errors)
    lang_dist, diff_dist, cat_dist = validate_enums(rows, errors, warnings)
    policy_counts, cases_with_pol, cases_without_pol = validate_policy_ids(rows, errors)
    clarification_count, escalation_count = validate_booleans(rows, errors)
    validate_user_inputs_and_duplicates(rows, errors, warnings, sample_csv_path)
    validate_language_sanity(rows, warnings)
    validate_list_fields_and_behavior(rows, errors, warnings)

    validation_passed = len(errors) == 0

    return {
        "total_cases": len(rows),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "language_distribution": lang_dist,
        "difficulty_distribution": diff_dist,
        "category_distribution": cat_dist,
        "clarification_count": clarification_count,
        "escalation_count": escalation_count,
        "cases_with_policy_ids": cases_with_pol,
        "cases_without_policy_ids": cases_without_pol,
        "policy_reference_counts": policy_counts,
        "validation_passed": validation_passed,
    }
