"""Response validator module for checking structural integrity of generated LLM responses CSV."""

import csv
from pathlib import Path
from typing import Any, Dict, List, Union


def validate_response_file(
    responses_csv_path: Union[str, Path],
    expected_count: int = 60,
) -> Dict[str, Any]:
    """Validate structural integrity of final_llm_responses.csv.

    Args:
        responses_csv_path: Path to final_llm_responses.csv.
        expected_count: Expected number of test cases (default 60).

    Returns:
        Dictionary containing response generation validation metrics and status.
    """
    path = Path(responses_csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Responses CSV file not found at: {path}")

    rows: List[Dict[str, str]] = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    expected_ids = {f"TC{i:03d}" for i in range(1, expected_count + 1)}
    found_ids = set()
    duplicate_ids = []
    missing_ids = []
    empty_successful = []
    failed_responses = []

    successful_count = 0
    model_names = set()
    latencies = []

    for row in rows:
        test_id = row.get("test_id", "").strip()
        if not test_id:
            continue

        if test_id in found_ids:
            duplicate_ids.append(test_id)
        found_ids.add(test_id)

        model_name = row.get("model_name", "").strip()
        if model_name:
            model_names.add(model_name)

        is_success = str(row.get("success", "")).strip().lower() in {"true", "1"}
        response_text = row.get("model_response", "")

        if is_success:
            successful_count += 1
            if not response_text or not response_text.strip():
                empty_successful.append(test_id)
        else:
            failed_responses.append(test_id)

        try:
            lat = float(row.get("latency_seconds", 0))
            if lat >= 0:
                latencies.append(lat)
        except ValueError:
            pass

    missing_ids = sorted(list(expected_ids - found_ids))
    avg_latency = round(sum(latencies) / len(latencies), 4) if latencies else 0.0

    # Response file structural validity rule
    is_valid = (
        len(rows) == expected_count
        and len(missing_ids) == 0
        and len(duplicate_ids) == 0
        and len(empty_successful) == 0
    )

    return {
        "total_expected_cases": expected_count,
        "total_output_rows": len(rows),
        "successful_responses": successful_count,
        "failed_responses": len(failed_responses),
        "failed_test_ids": failed_responses,
        "missing_test_ids": missing_ids,
        "duplicate_test_ids": duplicate_ids,
        "empty_successful_responses": empty_successful,
        "model_names_found": list(model_names),
        "average_latency_seconds": avg_latency,
        "response_file_valid": is_valid,
    }
