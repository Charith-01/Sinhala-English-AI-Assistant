"""Failure Analysis Module for Sinhala-English AI Assistant Evaluation.

Provides reusable functions to extract, categorize, group, and analyze model response failures,
partial-quality responses, domain-specific failure categories (hallucination, policy error,
privacy, clarification, escalation), and representative failure cases.
"""

import statistics
from typing import Any, Dict, List, Optional, Tuple, Union

VALID_FAILURE_TYPES = [
    "policy_error",
    "intent_misunderstanding",
    "irrelevant_response",
    "incomplete_response",
    "language_mismatch",
    "privacy_violation",
    "hallucination",
    "failed_clarification",
    "failed_escalation",
    "over_refusal",
    "other",
]

EVALUATION_DIMENSIONS = [
    "policy_correctness",
    "intent_understanding",
    "relevance",
    "completeness",
    "language_appropriateness",
    "safety_privacy",
    "hallucination_control",
]

VALID_LANGUAGES = ["english", "sinhala", "singlish", "code_mixed"]
VALID_DIFFICULTIES = ["easy", "medium", "hard"]


def is_truthy(val: Any) -> bool:
    """Check if value represents true."""
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val == 1
    if isinstance(val, str):
        return val.strip().lower() in ("true", "1", "yes", "pass", "passed")
    return False


def parse_number(val: Any) -> Optional[float]:
    """Parse float or int from string/number safely."""
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def extract_completed_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter rows to completed human evaluations only."""
    return [
        r for r in rows if str(r.get("evaluation_status", "")).strip().lower() == "completed"
    ]


def extract_failed_cases(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract primary failed cases (completed human evaluations with passed == false)."""
    completed = extract_completed_rows(rows)
    return [r for r in completed if not is_truthy(r.get("passed"))]


def extract_partial_quality_cases(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract partial-quality cases (passed == true, but at least one dimension score == 1)."""
    completed = extract_completed_rows(rows)
    partial = []
    for r in completed:
        if is_truthy(r.get("passed")):
            dims_scored_one = []
            for dim in EVALUATION_DIMENSIONS:
                sc = parse_number(r.get(dim))
                if sc == 1.0:
                    dims_scored_one.append(dim)
            if dims_scored_one:
                row_copy = dict(r)
                row_copy["dimensions_scored_one"] = "|".join(dims_scored_one)
                partial.append(row_copy)
    return partial


def analyze_failure_types(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compute frequency, percentage of evaluated, and percentage of failed for each failure type."""
    completed = extract_completed_rows(rows)
    failed = extract_failed_cases(rows)

    comp_count = len(completed)
    failed_count = len(failed)

    # Track occurrences and unique cases per failure label
    total_occurrences = {ft: 0 for ft in VALID_FAILURE_TYPES}
    unique_cases = {ft: 0 for ft in VALID_FAILURE_TYPES}

    for r in completed:
        raw_ft = str(r.get("failure_types", "")).strip()
        if raw_ft:
            parts = [p.strip() for p in raw_ft.split("|") if p.strip()]
            seen_in_row = set()
            for p in parts:
                lbl = p if p in total_occurrences else "other"
                total_occurrences[lbl] += 1
                seen_in_row.add(lbl)
            for lbl in seen_in_row:
                unique_cases[lbl] += 1

    results = []
    for ft in VALID_FAILURE_TYPES:
        u_cnt = unique_cases[ft]
        tot_occ = total_occurrences[ft]
        pct_eval = round((u_cnt / float(comp_count)) * 100.0, 2) if comp_count > 0 else 0.0
        pct_failed = round((u_cnt / float(failed_count)) * 100.0, 2) if failed_count > 0 else 0.0

        results.append({
            "failure_type": ft,
            "total_occurrences": tot_occ,
            "unique_cases": u_cnt,
            "percentage_of_evaluated": pct_eval,
            "percentage_of_failed": pct_failed,
        })

    results.sort(key=lambda x: x["unique_cases"], reverse=True)
    return results


def analyze_failures_by_language(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compute failure patterns by language type."""
    completed = extract_completed_rows(rows)
    results = []

    for lang in VALID_LANGUAGES:
        lang_comp = [r for r in completed if str(r.get("language_type", "")).strip().lower() == lang]
        lang_failed = [r for r in lang_comp if not is_truthy(r.get("passed"))]
        lang_partial = [r for r in extract_partial_quality_cases(rows) if str(r.get("language_type", "")).strip().lower() == lang]

        tot_eval = len(lang_comp)
        tot_fail = len(lang_failed)
        fail_rate = round((tot_fail / float(tot_eval)) * 100.0, 2) if tot_eval > 0 else 0.0

        failed_scores = [parse_number(r.get("overall_score")) for r in lang_failed if parse_number(r.get("overall_score")) is not None]
        avg_failed_score = round(float(statistics.mean(failed_scores)), 2) if failed_scores else 0.0

        # Most common failure label in this language
        lbl_counts: Dict[str, int] = {}
        for r in lang_comp:
            raw_ft = str(r.get("failure_types", "")).strip()
            if raw_ft:
                for p in raw_ft.split("|"):
                    clean_p = p.strip()
                    if clean_p:
                        lbl_counts[clean_p] = lbl_counts.get(clean_p, 0) + 1

        if lbl_counts:
            most_common_ft, most_common_cnt = max(lbl_counts.items(), key=lambda x: x[1])
        else:
            most_common_ft, most_common_cnt = "none", 0

        results.append({
            "language_type": lang,
            "evaluated_cases": tot_eval,
            "failed_cases": tot_fail,
            "failure_rate": fail_rate,
            "partial_quality_cases": len(lang_partial),
            "average_failed_score": avg_failed_score,
            "most_common_failure_type": most_common_ft,
            "most_common_failure_count": most_common_cnt,
        })

    return results


def analyze_failures_by_difficulty(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compute failure patterns by difficulty level (Easy, Medium, Hard)."""
    completed = extract_completed_rows(rows)
    results = []

    for diff in VALID_DIFFICULTIES:
        diff_comp = [r for r in completed if str(r.get("difficulty", "")).strip().lower() == diff]
        diff_failed = [r for r in diff_comp if not is_truthy(r.get("passed"))]

        tot_eval = len(diff_comp)
        tot_fail = len(diff_failed)
        fail_rate = round((tot_fail / float(tot_eval)) * 100.0, 2) if tot_eval > 0 else 0.0

        failed_scores = [parse_number(r.get("overall_score")) for r in diff_failed if parse_number(r.get("overall_score")) is not None]
        avg_failed_score = round(float(statistics.mean(failed_scores)), 2) if failed_scores else 0.0

        lbl_counts: Dict[str, int] = {}
        for r in diff_comp:
            raw_ft = str(r.get("failure_types", "")).strip()
            if raw_ft:
                for p in raw_ft.split("|"):
                    clean_p = p.strip()
                    if clean_p:
                        lbl_counts[clean_p] = lbl_counts.get(clean_p, 0) + 1

        if lbl_counts:
            most_common_ft = max(lbl_counts.items(), key=lambda x: x[1])[0]
        else:
            most_common_ft = "none"

        results.append({
            "difficulty": diff,
            "evaluated_cases": tot_eval,
            "failed_cases": tot_fail,
            "failure_rate": fail_rate,
            "average_score": avg_failed_score,
            "most_common_failure_type": most_common_ft,
        })

    return results


def analyze_failures_by_category(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compute failure patterns by evaluation category."""
    completed = extract_completed_rows(rows)

    categories = sorted(list({str(r.get("category", "")).strip() for r in completed if str(r.get("category", "")).strip()}))
    results = []

    for cat in categories:
        cat_comp = [r for r in completed if str(r.get("category", "")).strip() == cat]
        cat_failed = [r for r in cat_comp if not is_truthy(r.get("passed"))]

        tot_eval = len(cat_comp)
        tot_fail = len(cat_failed)
        fail_rate = round((tot_fail / float(tot_eval)) * 100.0, 2) if tot_eval > 0 else 0.0

        all_scores = [parse_number(r.get("overall_score")) for r in cat_comp if parse_number(r.get("overall_score")) is not None]
        avg_score = round(float(statistics.mean(all_scores)), 2) if all_scores else 0.0

        lbl_counts: Dict[str, int] = {}
        for r in cat_comp:
            raw_ft = str(r.get("failure_types", "")).strip()
            if raw_ft:
                for p in raw_ft.split("|"):
                    clean_p = p.strip()
                    if clean_p:
                        lbl_counts[clean_p] = lbl_counts.get(clean_p, 0) + 1

        most_common_ft = max(lbl_counts.items(), key=lambda x: x[1])[0] if lbl_counts else "none"

        results.append({
            "category": cat,
            "evaluated_cases": tot_eval,
            "failed_cases": tot_fail,
            "failure_rate": fail_rate,
            "average_score": avg_score,
            "most_common_failure_type": most_common_ft,
        })

    results.sort(key=lambda x: x["failure_rate"], reverse=True)
    return results


def analyze_dimension_failures(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Dimension-level failure distribution across completed evaluation rows."""
    completed = extract_completed_rows(rows)
    comp_count = len(completed)

    dim_res = {}
    for dim in EVALUATION_DIMENSIONS:
        scores = [int(parse_number(r.get(dim))) for r in completed if parse_number(r.get(dim)) is not None]
        c0 = scores.count(0)
        c1 = scores.count(1)
        c2 = scores.count(2)

        p0 = round((c0 / float(comp_count)) * 100.0, 2) if comp_count > 0 else 0.0
        p1 = round((c1 / float(comp_count)) * 100.0, 2) if comp_count > 0 else 0.0
        p2 = round((c2 / float(comp_count)) * 100.0, 2) if comp_count > 0 else 0.0

        dim_res[dim] = {
            "score_0_count": c0,
            "score_1_count": c1,
            "score_2_count": c2,
            "pct_score_0": p0,
            "pct_score_1": p1,
            "pct_score_2": p2,
        }

    return dim_res


def analyze_clarification_failures(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze clarification performance for cases where requires_clarification == true."""
    completed = extract_completed_rows(rows)
    clar_rows = [r for r in completed if is_truthy(r.get("requires_clarification"))]
    tot_clar = len(clar_rows)

    failed_clar_cases = []
    for r in clar_rows:
        raw_ft = str(r.get("failure_types", "")).strip()
        if "failed_clarification" in [p.strip() for p in raw_ft.split("|") if p.strip()]:
            failed_clar_cases.append(r)

    tot_failed_lbl = len(failed_clar_cases)

    # Language breakdown
    lang_dist: Dict[str, int] = {}
    for r in failed_clar_cases:
        l = str(r.get("language_type", "unknown")).strip().lower()
        lang_dist[l] = lang_dist.get(l, 0) + 1

    return {
        "total_clarification_required": tot_clar,
        "passed_count": sum(1 for r in clar_rows if is_truthy(r.get("passed"))),
        "failed_count": sum(1 for r in clar_rows if not is_truthy(r.get("passed"))),
        "labelled_failed_clarification_count": tot_failed_lbl,
        "failed_clarification_rate": round((tot_failed_lbl / float(tot_clar)) * 100.0, 2) if tot_clar > 0 else 0.0,
        "language_distribution": lang_dist,
        "failed_case_ids": [r.get("test_id") for r in failed_clar_cases],
    }


def analyze_escalation_failures(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze escalation performance for cases where requires_escalation == true."""
    completed = extract_completed_rows(rows)
    esc_rows = [r for r in completed if is_truthy(r.get("requires_escalation"))]
    tot_esc = len(esc_rows)

    failed_esc_cases = []
    for r in esc_rows:
        raw_ft = str(r.get("failure_types", "")).strip()
        if "failed_escalation" in [p.strip() for p in raw_ft.split("|") if p.strip()]:
            failed_esc_cases.append(r)

    tot_failed_lbl = len(failed_esc_cases)

    lang_dist: Dict[str, int] = {}
    for r in failed_esc_cases:
        l = str(r.get("language_type", "unknown")).strip().lower()
        lang_dist[l] = lang_dist.get(l, 0) + 1

    return {
        "total_escalation_required": tot_esc,
        "passed_count": sum(1 for r in esc_rows if is_truthy(r.get("passed"))),
        "failed_count": sum(1 for r in esc_rows if not is_truthy(r.get("passed"))),
        "labelled_failed_escalation_count": tot_failed_lbl,
        "failed_escalation_rate": round((tot_failed_lbl / float(tot_esc)) * 100.0, 2) if tot_esc > 0 else 0.0,
        "language_distribution": lang_dist,
        "failed_case_ids": [r.get("test_id") for r in failed_esc_cases],
    }


def select_representative_failure_examples(
    rows: List[Dict[str, Any]], max_examples: int = 10
) -> List[Dict[str, Any]]:
    """Select 5-10 representative REAL failure cases spanning diverse failure types and languages."""
    failed = extract_failed_cases(rows)
    if not failed:
        return []

    selected: List[Dict[str, Any]] = []
    seen_types = set()
    seen_langs = set()

    # First pass: Pick distinct failure types across different languages
    for r in failed:
        raw_ft = str(r.get("failure_types", "")).strip()
        lang = str(r.get("language_type", "")).strip().lower()
        first_type = raw_ft.split("|")[0].strip() if raw_ft else "unlabelled"

        if first_type not in seen_types or lang not in seen_langs:
            seen_types.add(first_type)
            seen_langs.add(lang)
            selected.append({
                "test_id": r.get("test_id", ""),
                "language_type": r.get("language_type", ""),
                "category": r.get("category", ""),
                "failure_type": raw_ft,
                "user_input": r.get("user_input", ""),
                "expected_behavior": r.get("expected_behavior", ""),
                "model_response": r.get("model_response", ""),
                "brief_observed_issue": r.get("evaluator_notes", "") or f"Failure labelled: {raw_ft}",
            })
            if len(selected) >= max_examples:
                break

    # Second pass if needed to reach target count up to max_examples
    if len(selected) < max_examples:
        selected_ids = {s["test_id"] for s in selected}
        for r in failed:
            tid = r.get("test_id", "")
            if tid not in selected_ids:
                selected.append({
                    "test_id": tid,
                    "language_type": r.get("language_type", ""),
                    "category": r.get("category", ""),
                    "failure_type": str(r.get("failure_types", "")).strip(),
                    "user_input": r.get("user_input", ""),
                    "expected_behavior": r.get("expected_behavior", ""),
                    "model_response": r.get("model_response", ""),
                    "brief_observed_issue": r.get("evaluator_notes", "") or "Observed model failure",
                })
                if len(selected) >= max_examples:
                    break

    return selected


def generate_failure_analysis_summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Master function aggregating all failure pattern analysis results."""
    completed = extract_completed_rows(rows)
    failed = extract_failed_cases(rows)
    partial = extract_partial_quality_cases(rows)

    comp_count = len(completed)
    failed_count = len(failed)
    partial_count = len(partial)

    fail_rate = round((failed_count / float(comp_count)) * 100.0, 2) if comp_count > 0 else 0.0

    ft_freq = analyze_failure_types(rows)
    by_lang = analyze_failures_by_language(rows)
    by_diff = analyze_failures_by_difficulty(rows)
    by_cat = analyze_failures_by_category(rows)
    dim_analysis = analyze_dimension_failures(rows)

    clar_analysis = analyze_clarification_failures(rows)
    esc_analysis = analyze_escalation_failures(rows)

    # Individual label counts
    label_counts = {item["failure_type"]: item["unique_cases"] for item in ft_freq}

    return {
        "total_evaluated": comp_count,
        "failed_cases": failed_count,
        "partial_quality_cases": partial_count,
        "failure_rate": fail_rate,
        "failure_type_counts": label_counts,
        "failure_type_percentages": {item["failure_type"]: item["percentage_of_evaluated"] for item in ft_freq},
        "failures_by_language": by_lang,
        "failures_by_difficulty": by_diff,
        "failures_by_category": by_cat,
        "dimension_analysis": dim_analysis,
        "policy_error_count": label_counts.get("policy_error", 0),
        "hallucination_count": label_counts.get("hallucination", 0),
        "privacy_violation_count": label_counts.get("privacy_violation", 0),
        "failed_clarification_count": label_counts.get("failed_clarification", 0),
        "failed_escalation_count": label_counts.get("failed_escalation", 0),
        "language_mismatch_count": label_counts.get("language_mismatch", 0),
        "over_refusal_count": label_counts.get("over_refusal", 0),
        "clarification_analysis": clar_analysis,
        "escalation_analysis": esc_analysis,
    }
