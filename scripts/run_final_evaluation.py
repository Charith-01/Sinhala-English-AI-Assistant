"""Full evaluation runner script for response generation on 60 final test cases.

Executes response generation sequentially against the configured Gemini model,
supporting incremental saving, automatic resuming, rate-limit retries, and run metadata logging.
"""

import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root directory to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.llm_client import GeminiClient
from src.test_case_loader import load_test_cases


def check_preflight_validation(validation_json_path: Path, raw_csv_path: Path) -> bool:
    """Perform preflight checks on dataset validation status and row count."""
    if not validation_json_path.exists():
        print(f"[PREFLIGHT ERROR] Validation report not found at {validation_json_path}.")
        return False

    with open(validation_json_path, "r", encoding="utf-8") as f:
        val_data = json.load(f)

    if not val_data.get("validation_passed", False):
        print("[PREFLIGHT ERROR] Dataset validation_passed is FALSE. Blocked run.")
        return False

    cases = load_test_cases(raw_csv_path)
    if len(cases) != 60:
        print(f"[PREFLIGHT ERROR] Expected 60 test cases in CSV, found {len(cases)}.")
        return False

    expected_ids = [f"TC{i:03d}" for i in range(1, 61)]
    actual_ids = [tc.test_id for tc in cases]
    if actual_ids != expected_ids:
        print("[PREFLIGHT ERROR] Test IDs are not TC001 through TC060 sequentially.")
        return False

    print("[PREFLIGHT PASSED] Dataset validation report verified (60 valid test cases).")
    return True


def load_existing_responses(output_csv_path: Path) -> Tuple[Dict[str, dict], set]:
    """Read existing responses CSV to support resuming clean runs."""
    existing_rows: Dict[str, dict] = {}
    completed_ids: set = set()

    if not output_csv_path.exists():
        return existing_rows, completed_ids

    with open(output_csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tid = row["test_id"].strip()
            existing_rows[tid] = row
            if str(row.get("success", "")).strip().lower() in {"true", "1"}:
                completed_ids.add(tid)

    return existing_rows, completed_ids


def save_responses_csv(output_csv_path: Path, results: List[dict]):
    """Save/update LLM responses incrementally to CSV."""
    fieldnames = [
        "test_id",
        "category",
        "language_type",
        "difficulty",
        "user_input",
        "model_name",
        "model_response",
        "success",
        "error_message",
        "latency_seconds",
    ]

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def execute_with_retry(client: GeminiClient, test_id: str, user_input: str, max_retries: int = 3):
    """Execute response generation with bounded retry strategy for rate limits/transient errors."""
    for attempt in range(1, max_retries + 1):
        response = client.generate_response(test_id, user_input)
        if response.success:
            return response

        err_msg = response.error_message.lower()
        if ("429" in err_msg or "quota" in err_msg or "rate limit" in err_msg or "resource_exhausted" in err_msg) and attempt < max_retries:
            wait_time = attempt * 3
            print(f"   [RATE LIMIT] {test_id} (Attempt {attempt}/{max_retries}) - Retrying in {wait_time}s...")
            time.sleep(wait_time)
        else:
            return response
    return response


def run_full_experiment():
    output_dir = root_dir / "data" / "processed"
    results_dir = root_dir / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    validation_json_path = results_dir / "final_dataset_validation.json"
    raw_csv_path = root_dir / "data" / "raw" / "final_test_cases.csv"
    output_csv_path = output_dir / "final_llm_responses.csv"
    metadata_json_path = output_dir / "final_run_metadata.json"

    print("--- Starting Final Response Generation Experiment ---")

    # Step 1: Preflight validation
    if not check_preflight_validation(validation_json_path, raw_csv_path):
        print("[BLOCKED] Response generation experiment blocked due to preflight failure.")
        sys.exit(1)

    # Step 2: Initialize LLM client & print configuration
    try:
        client = GeminiClient()
    except Exception as e:
        print(f"[CONFIGURATION ERROR] {e}")
        print("Please verify GEMINI_API_KEY and GEMINI_MODEL in environment or .env file.")
        sys.exit(1)

    print(f"Evaluation model: {client.model_name}")

    # Load test cases
    test_cases = load_test_cases(raw_csv_path)

    # Load existing responses for resume support
    existing_rows, completed_ids = load_existing_responses(output_csv_path)

    resumed_run = len(completed_ids) > 0
    if resumed_run:
        print(f"Existing successful responses: {len(completed_ids)}")
        print(f"Remaining cases to process: {len(test_cases) - len(completed_ids)}")

    results_map: Dict[str, dict] = dict(existing_rows)

    start_timestamp = datetime.now(timezone.utc).isoformat()

    new_processed_count = 0

    for idx, tc in enumerate(test_cases, start=1):
        if tc.test_id in completed_ids:
            print(f"[{idx}/60] {tc.test_id} (Skipping - Already Completed)")
            continue

        print(f"[{idx}/60] {tc.test_id}...")

        # Ground-truth leakage rule enforced: only sending test_id and user_input
        llm_resp = execute_with_retry(client, tc.test_id, tc.user_input)
        new_processed_count += 1

        if not llm_resp.success:
            print(f"   [WARNING] {tc.test_id} failed: {llm_resp.error_message}")

        results_map[tc.test_id] = {
            "test_id": tc.test_id,
            "category": tc.category,
            "language_type": tc.language_type,
            "difficulty": tc.difficulty,
            "user_input": tc.user_input,
            "model_name": llm_resp.model_name,
            "model_response": llm_resp.response_text,
            "success": llm_resp.success,
            "error_message": llm_resp.error_message,
            "latency_seconds": llm_resp.latency_seconds,
        }

        # Incremental save after every single test case
        ordered_results = [results_map[t.test_id] for t in test_cases if t.test_id in results_map]
        save_responses_csv(output_csv_path, ordered_results)

    end_timestamp = datetime.now(timezone.utc).isoformat()

    # Calculate metrics
    final_ordered = [results_map[t.test_id] for t in test_cases if t.test_id in results_map]
    successful_requests = sum(1 for r in final_ordered if str(r.get("success", "")).strip().lower() in {"true", "1"})
    failed_requests = len(final_ordered) - successful_requests

    latencies = [float(r.get("latency_seconds", 0)) for r in final_ordered if str(r.get("success", "")).strip().lower() in {"true", "1"}]
    avg_latency = round(sum(latencies) / len(latencies), 4) if latencies else 0.0
    min_latency = round(min(latencies), 4) if latencies else 0.0
    max_latency = round(max(latencies), 4) if latencies else 0.0

    # Save run metadata
    metadata = {
        "experiment_name": "Sinhala-English AI Assistant 60-Case Response Generation",
        "model_name": client.model_name,
        "temperature": 0.2,
        "dataset_file": "data/raw/final_test_cases.csv",
        "total_test_cases": len(test_cases),
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "average_latency_seconds": avg_latency,
        "minimum_latency_seconds": min_latency,
        "maximum_latency_seconds": max_latency,
        "run_started_at": start_timestamp,
        "run_completed_at": end_timestamp,
        "resumed_run": resumed_run,
        "previously_completed_cases": len(completed_ids),
        "new_cases_processed": new_processed_count,
    }

    with open(metadata_json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved final responses to: {output_csv_path}")
    print(f"Saved run metadata to: {metadata_json_path}")
    print("--- Final Response Generation Experiment Finished ---")


if __name__ == "__main__":
    run_full_experiment()
