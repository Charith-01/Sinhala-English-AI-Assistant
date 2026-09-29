"""Quantitative Analysis Module for Sinhala-English AI Assistant Evaluation.

Provides reusable functions to compute overall, grouped, dimension-level, failure taxonomy,
domain-specific (hallucination, privacy, clarification, escalation), and technical API reliability metrics.
"""

import csv
import json
import statistics
from pathlib import Path
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
    """Helper to check if a value string/bool represents true."""
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val == 1
    if isinstance(val, str):
        return val.strip().lower() in ("true", "1", "yes", "pass", "passed")
    return False


def parse_number(val: Any) -> Optional[float]:
    """Helper to parse float or int from string/number safely."""
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def validate_final_results_completeness(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate completeness and integrity of evaluation result rows.

    Returns dict with summary counts, lists of test IDs, and any validation errors.
    """
    total_count = len(rows)
    seen_ids = set()
    duplicate_ids = []
    completed_ids = []
    pending_ids = []
    tech_fail_ids = []
    invalid_rows = []

    for idx, row in enumerate(rows, start=1):
        tid = str(row.get("test_id", f"Row_{idx}")).strip()
        if not tid:
            invalid_rows.append(f"Row {idx}: missing test_id")
            continue

        if tid in seen_ids:
            duplicate_ids.append(tid)
        seen_ids.add(tid)

        status = str(row.get("evaluation_status", "")).strip().lower()

        if status == "technical_failure":
            tech_fail_ids.append(tid)
        elif status == "pending" or not status:
            pending_ids.append(tid)
        elif status == "completed":
            # Verify all 7 dimension scores are present and in {0, 1, 2}
            row_valid = True
            for dim in EVALUATION_DIMENSIONS:
                score_num = parse_number(row.get(dim))
                if score_num is None or score_num not in (0.0, 1.0, 2.0):
                    invalid_rows.append(
                        f"{tid}: invalid or missing dimension score for '{dim}' ({row.get(dim)})"
                    )
                    row_valid = False
            
            # Check overall score, score percentage, passed
            overall = parse_number(row.get("overall_score"))
            score_pct = parse_number(row.get("score_percentage"))
            passed_val = row.get("passed")

            if overall is None or overall < 0 or overall > 14:
                invalid_rows.append(f"{tid}: invalid overall_score ({row.get('overall_score')})")
                row_valid = False
            if score_pct is None or score_pct < 0.0 or score_pct > 100.0:
                invalid_rows.append(f"{tid}: invalid score_percentage ({row.get('score_percentage')})")
                row_valid = False
            if passed_val is None or str(passed_val).strip() == "":
                invalid_rows.append(f"{tid}: missing passed status")
                row_valid = False

            if row_valid:
                completed_ids.append(tid)
        else:
            invalid_rows.append(f"{tid}: unknown evaluation_status '{status}'")

    return {
        "total_test_cases": total_count,
        "completed_count": len(completed_ids),
        "pending_count": len(pending_ids),
        "technical_failure_count": len(tech_fail_ids),
        "invalid_count": len(invalid_rows),
        "duplicate_ids": duplicate_ids,
        "completed_ids": completed_ids,
        "pending_ids": pending_ids,
        "tech_fail_ids": tech_fail_ids,
        "invalid_rows": invalid_rows,
    }


def calculate_primary_counts(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    """Compute primary experiment counts."""
    total_test_cases = len(rows)
    successful_gen = 0
    tech_failures = 0
    completed_eval = 0
    passed_count = 0
    failed_count = 0

    for row in rows:
        gen_success = is_truthy(row.get("generation_success"))
        status = str(row.get("evaluation_status", "")).strip().lower()

        if status == "technical_failure" or not gen_success:
            tech_failures += 1
        else:
            successful_gen += 1

        if status == "completed":
            completed_eval += 1
            if is_truthy(row.get("passed")):
                passed_count += 1
            else:
                failed_count += 1

    return {
        "total_test_cases": total_test_cases,
        "successful_generation_count": successful_gen,
        "technical_failure_count": tech_failures,
        "completed_evaluation_count": completed_eval,
        "passed_count": passed_count,
        "failed_count": failed_count,
    }


def calculate_overall_pass_rate(passed_count: int, completed_count: int) -> float:
    """Calculate overall pass rate percentage using completed_count as denominator."""
    if completed_count <= 0:
        return 0.0
    return round((passed_count / float(completed_count)) * 100.0, 2)


def calculate_overall_fail_rate(failed_count: int, completed_count: int) -> float:
    """Calculate overall fail rate percentage using completed_count as denominator."""
    if completed_count <= 0:
        return 0.0
    return round((failed_count / float(completed_count)) * 100.0, 2)


def calculate_score_statistics(scores: List[float]) -> Dict[str, float]:
    """Calculate mean, median, min, max of overall scores."""
    if not scores:
        return {"mean": 0.0, "median": 0.0, "min": 0.0, "max": 0.0}
    return {
        "mean": round(float(statistics.mean(scores)), 2),
        "median": round(float(statistics.median(scores)), 2),
        "min": round(float(min(scores)), 2),
        "max": round(float(max(scores)), 2),
    }


def calculate_percentage_statistics(percentages: List[float]) -> Dict[str, float]:
    """Calculate mean and median of score percentages."""
    if not percentages:
        return {"mean": 0.0, "median": 0.0}
    return {
        "mean": round(float(statistics.mean(percentages)), 2),
        "median": round(float(statistics.median(percentages)), 2),
    }


def calculate_performance_by_group(
    rows: List[Dict[str, Any]], group_key: str, valid_groups: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Calculate grouped performance metrics for completed evaluation rows."""
    completed_rows = [
        r for r in rows if str(r.get("evaluation_status", "")).strip().lower() == "completed"
    ]

    grouped_data: Dict[str, List[Dict[str, Any]]] = {}

    if valid_groups:
        for g in valid_groups:
            grouped_data[g] = []

    for r in completed_rows:
        val = str(r.get(group_key, "unknown")).strip()
        if val not in grouped_data:
            grouped_data[val] = []
        grouped_data[val].append(r)

    results = []
    for g_name, g_rows in grouped_data.items():
        total_eval = len(g_rows)
        passed = sum(1 for r in g_rows if is_truthy(r.get("passed")))
        failed = total_eval - passed
        pass_rate = round((passed / float(total_eval)) * 100.0, 2) if total_eval > 0 else 0.0

        scores = [parse_number(r.get("overall_score")) for r in g_rows if parse_number(r.get("overall_score")) is not None]
        pcts = [parse_number(r.get("score_percentage")) for r in g_rows if parse_number(r.get("score_percentage")) is not None]

        avg_score = round(float(statistics.mean(scores)), 2) if scores else 0.0
        avg_pct = round(float(statistics.mean(pcts)), 2) if pcts else 0.0

        results.append({
            group_key: g_name,
            "total": total_eval,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "avg_score": avg_score,
            "avg_percentage": avg_pct,
        })

    # Consistency check: total evaluated cases across groups must equal len(completed_rows)
    total_grouped = sum(res["total"] for res in results)
    if total_grouped != len(completed_rows):
        raise ValueError(
            f"Grouped total mismatch for {group_key}: sum is {total_grouped}, expected {len(completed_rows)}"
        )

    return results


def calculate_dimension_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Calculate metric distribution across the 7 scoring dimensions for completed rows."""
    completed_rows = [
        r for r in rows if str(r.get("evaluation_status", "")).strip().lower() == "completed"
    ]
    completed_count = len(completed_rows)

    dim_metrics = {}

    for dim in EVALUATION_DIMENSIONS:
        scores = [
            int(parse_number(r.get(dim)))
            for r in completed_rows
            if parse_number(r.get(dim)) is not None
        ]

        if not scores:
            dim_metrics[dim] = {
                "mean_score": 0.0,
                "median_score": 0.0,
                "count_0": 0,
                "count_1": 0,
                "count_2": 0,
                "pct_0": 0.0,
                "pct_1": 0.0,
                "pct_2": 0.0,
                "mean_score_pct": 0.0,
            }
            continue

        c0 = scores.count(0)
        c1 = scores.count(1)
        c2 = scores.count(2)

        # Consistency check: c0 + c1 + c2 must equal completed_count
        if c0 + c1 + c2 != completed_count:
            raise ValueError(
                f"Dimension score count mismatch for {dim}: sum is {c0+c1+c2}, expected {completed_count}"
            )

        mean_val = float(statistics.mean(scores))
        median_val = float(statistics.median(scores))

        p0 = round((c0 / float(completed_count)) * 100.0, 2) if completed_count > 0 else 0.0
        p1 = round((c1 / float(completed_count)) * 100.0, 2) if completed_count > 0 else 0.0
        p2 = round((c2 / float(completed_count)) * 100.0, 2) if completed_count > 0 else 0.0
        mean_score_pct = round((mean_val / 2.0) * 100.0, 2)

        dim_metrics[dim] = {
            "mean_score": round(mean_val, 2),
            "median_score": round(median_val, 2),
            "count_0": c0,
            "count_1": c1,
            "count_2": c2,
            "pct_0": p0,
            "pct_1": p1,
            "pct_2": p2,
            "mean_score_pct": mean_score_pct,
        }

    return dim_metrics


def calculate_dimension_scores_by_language(
    rows: List[Dict[str, Any]]
) -> Dict[str, Dict[str, float]]:
    """Compute average score for each dimension grouped by language type."""
    completed_rows = [
        r for r in rows if str(r.get("evaluation_status", "")).strip().lower() == "completed"
    ]

    lang_dim_matrix: Dict[str, Dict[str, float]] = {}

    for lang in VALID_LANGUAGES:
        lang_rows = [r for r in completed_rows if str(r.get("language_type", "")).strip().lower() == lang]
        lang_dim_matrix[lang] = {}
        for dim in EVALUATION_DIMENSIONS:
            scores = [
                parse_number(r.get(dim))
                for r in lang_rows
                if parse_number(r.get(dim)) is not None
            ]
            if scores:
                avg_score = round(float(statistics.mean(scores)), 2)
            else:
                avg_score = 0.0
            lang_dim_matrix[lang][dim] = avg_score

    return lang_dim_matrix


def calculate_failure_type_frequency(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compute frequency and percentage of each failure type in completed rows."""
    completed_rows = [
        r for r in rows if str(r.get("evaluation_status", "")).strip().lower() == "completed"
    ]
    completed_count = len(completed_rows)

    counts = {ft: 0 for ft in VALID_FAILURE_TYPES}

    for r in completed_rows:
        raw_ft = str(r.get("failure_types", "")).strip()
        if raw_ft:
            parts = [p.strip() for p in raw_ft.split("|") if p.strip()]
            for p in parts:
                if p in counts:
                    counts[p] += 1
                else:
                    counts["other"] = counts.get("other", 0) + 1

    results = []
    for ft in VALID_FAILURE_TYPES:
        c = counts[ft]
        pct = round((c / float(completed_count)) * 100.0, 2) if completed_count > 0 else 0.0
        results.append({
            "failure_type": ft,
            "count": c,
            "percentage": pct,
        })

    # Sort descending by count
    results.sort(key=lambda x: x["count"], reverse=True)
    return results


def calculate_hallucination_metrics(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate explicit hallucination rate and hallucination_control zero rate."""
    completed_rows = [
        r for r in rows if str(r.get("evaluation_status", "")).strip().lower() == "completed"
    ]
    completed_count = len(completed_rows)

    if completed_count == 0:
        return {
            "explicit_hallucination_failure_rate": 0.0,
            "hallucination_control_zero_rate": 0.0,
        }

    explicit_count = 0
    zero_score_count = 0

    for r in completed_rows:
        raw_ft = str(r.get("failure_types", "")).strip()
        if "hallucination" in [p.strip() for p in raw_ft.split("|") if p.strip()]:
            explicit_count += 1
        
        hc_score = parse_number(r.get("hallucination_control"))
        if hc_score == 0.0:
            zero_score_count += 1

    return {
        "explicit_hallucination_failure_rate": round((explicit_count / float(completed_count)) * 100.0, 2),
        "hallucination_control_zero_rate": round((zero_score_count / float(completed_count)) * 100.0, 2),
    }


def calculate_privacy_safety_metrics(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate explicit privacy violation rate and safety_privacy zero rate."""
    completed_rows = [
        r for r in rows if str(r.get("evaluation_status", "")).strip().lower() == "completed"
    ]
    completed_count = len(completed_rows)

    if completed_count == 0:
        return {
            "privacy_violation_rate": 0.0,
            "safety_privacy_zero_rate": 0.0,
        }

    explicit_count = 0
    zero_score_count = 0

    for r in completed_rows:
        raw_ft = str(r.get("failure_types", "")).strip()
        if "privacy_violation" in [p.strip() for p in raw_ft.split("|") if p.strip()]:
            explicit_count += 1
        
        sp_score = parse_number(r.get("safety_privacy"))
        if sp_score == 0.0:
            zero_score_count += 1

    return {
        "privacy_violation_rate": round((explicit_count / float(completed_count)) * 100.0, 2),
        "safety_privacy_zero_rate": round((zero_score_count / float(completed_count)) * 100.0, 2),
    }


def calculate_clarification_performance(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute clarification performance for completed rows where requires_clarification is True."""
    completed_rows = [
        r for r in rows if str(r.get("evaluation_status", "")).strip().lower() == "completed"
    ]
    clarification_rows = [r for r in completed_rows if is_truthy(r.get("requires_clarification"))]
    total_clarification = len(clarification_rows)

    failed_count = 0
    for r in clarification_rows:
        raw_ft = str(r.get("failure_types", "")).strip()
        if "failed_clarification" in [p.strip() for p in raw_ft.split("|") if p.strip()]:
            failed_count += 1

    rate = round((failed_count / float(total_clarification)) * 100.0, 2) if total_clarification > 0 else 0.0

    return {
        "total_clarification_required": total_clarification,
        "failed_clarification_count": failed_count,
        "failed_clarification_rate": rate,
    }


def calculate_escalation_performance(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute escalation performance for completed rows where requires_escalation is True."""
    completed_rows = [
        r for r in rows if str(r.get("evaluation_status", "")).strip().lower() == "completed"
    ]
    escalation_rows = [r for r in completed_rows if is_truthy(r.get("requires_escalation"))]
    total_escalation = len(escalation_rows)

    failed_count = 0
    for r in escalation_rows:
        raw_ft = str(r.get("failure_types", "")).strip()
        if "failed_escalation" in [p.strip() for p in raw_ft.split("|") if p.strip()]:
            failed_count += 1

    rate = round((failed_count / float(total_escalation)) * 100.0, 2) if total_escalation > 0 else 0.0

    return {
        "total_escalation_required": total_escalation,
        "failed_escalation_count": failed_count,
        "failed_escalation_rate": rate,
    }


def calculate_api_reliability_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute API generation reliability metrics and latency statistics across all rows."""
    total_cases = len(rows)
    success_count = 0
    tech_fail_count = 0
    latencies: List[float] = []

    for r in rows:
        status = str(r.get("evaluation_status", "")).strip().lower()
        gen_success = is_truthy(r.get("generation_success"))

        if status == "technical_failure" or not gen_success:
            tech_fail_count += 1
        else:
            success_count += 1

        lat = parse_number(r.get("latency_seconds"))
        if lat is not None:
            latencies.append(lat)

    success_rate = round((success_count / float(total_cases)) * 100.0, 2) if total_cases > 0 else 0.0
    tech_fail_rate = round((tech_fail_count / float(total_cases)) * 100.0, 2) if total_cases > 0 else 0.0

    if latencies:
        avg_lat = round(float(statistics.mean(latencies)), 4)
        med_lat = round(float(statistics.median(latencies)), 4)
        min_lat = round(float(min(latencies)), 4)
        max_lat = round(float(max(latencies)), 4)
    else:
        avg_lat = med_lat = min_lat = max_lat = 0.0

    return {
        "total_test_cases": total_cases,
        "successful_generation_count": success_count,
        "technical_failure_count": tech_fail_count,
        "generation_success_rate": success_rate,
        "technical_failure_rate": tech_fail_rate,
        "average_latency_seconds": avg_lat,
        "median_latency_seconds": med_lat,
        "minimum_latency_seconds": min_lat,
        "maximum_latency_seconds": max_lat,
    }


def generate_all_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Master function to aggregate all quantitative metrics."""
    counts = calculate_primary_counts(rows)
    comp_count = counts["completed_evaluation_count"]

    completed_rows = [
        r for r in rows if str(r.get("evaluation_status", "")).strip().lower() == "completed"
    ]

    scores = [parse_number(r.get("overall_score")) for r in completed_rows if parse_number(r.get("overall_score")) is not None]
    pcts = [parse_number(r.get("score_percentage")) for r in completed_rows if parse_number(r.get("score_percentage")) is not None]

    score_stats = calculate_score_statistics(scores)
    pct_stats = calculate_percentage_statistics(pcts)

    pass_rate = calculate_overall_pass_rate(counts["passed_count"], comp_count)
    fail_rate = calculate_overall_fail_rate(counts["failed_count"], comp_count)

    by_lang = calculate_performance_by_group(rows, "language_type", VALID_LANGUAGES)
    by_diff = calculate_performance_by_group(rows, "difficulty", VALID_DIFFICULTIES)
    by_cat = calculate_performance_by_group(rows, "category")

    dim_metrics = calculate_dimension_metrics(rows)
    lang_dim_matrix = calculate_dimension_scores_by_language(rows)
    failure_freq = calculate_failure_type_frequency(rows)

    hallucination_m = calculate_hallucination_metrics(rows)
    privacy_m = calculate_privacy_safety_metrics(rows)
    clarification_m = calculate_clarification_performance(rows)
    escalation_m = calculate_escalation_performance(rows)
    api_m = calculate_api_reliability_metrics(rows)

    return {
        "experiment_counts": counts,
        "overall_performance": {
            "overall_pass_rate": pass_rate,
            "overall_fail_rate": fail_rate,
            "passed_count": counts["passed_count"],
            "failed_count": counts["failed_count"],
            "completed_evaluation_count": comp_count,
        },
        "score_statistics": {
            "overall_score": score_stats,
            "score_percentage": pct_stats,
        },
        "performance_by_language": by_lang,
        "performance_by_difficulty": by_diff,
        "performance_by_category": by_cat,
        "dimension_metrics": dim_metrics,
        "dimension_scores_by_language": lang_dim_matrix,
        "failure_type_frequency": failure_freq,
        "hallucination_metrics": hallucination_m,
        "privacy_safety_metrics": privacy_m,
        "clarification_metrics": clarification_m,
        "escalation_metrics": escalation_m,
        "api_reliability_metrics": api_m,
    }
