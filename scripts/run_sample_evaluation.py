"""Sample response generation runner script.

Executes 4 sample development test cases against the configured Gemini API model
and saves responses to data/processed/sample_llm_responses.csv.
"""

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root directory to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.llm_client import GeminiClient
from src.test_case_loader import load_test_cases


def run_sample_evaluation():
    sample_csv_path = root_dir / "data" / "raw" / "sample_test_cases.csv"
    output_dir = root_dir / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_csv_path = output_dir / "sample_llm_responses.csv"
    metadata_json_path = output_dir / "sample_run_metadata.json"

    print("--- Starting Sample Response Generation ---")
    test_cases = load_test_cases(sample_csv_path)
    print(f"Loaded {len(test_cases)} test cases.")

    try:
        client = GeminiClient()
    except Exception as e:
        print(f"Configuration Error: {e}")
        print("Please ensure GEMINI_API_KEY and GEMINI_MODEL are set in your .env file.")
        sys.exit(1)

    print(f"Evaluation model: {client.model_name}")

    results = []
    successful_count = 0
    failed_count = 0

    for idx, test_case in enumerate(test_cases, start=1):
        print(f"[{idx}/{len(test_cases)}] Running {test_case.test_id}...")
        llm_response = client.generate_response(test_case.test_id, test_case.user_input)

        if llm_response.success:
            successful_count += 1
        else:
            failed_count += 1
            print(f"   [WARNING] {test_case.test_id} failed: {llm_response.error_message}")

        results.append({
            "test_id": test_case.test_id,
            "language_type": test_case.language_type,
            "difficulty": test_case.difficulty,
            "user_input": test_case.user_input,
            "model_name": llm_response.model_name,
            "model_response": llm_response.response_text,
            "success": llm_response.success,
            "error_message": llm_response.error_message,
            "latency_seconds": llm_response.latency_seconds,
        })

    # Save generated responses to CSV (utf-8-sig for Excel compatibility)
    fieldnames = [
        "test_id",
        "language_type",
        "difficulty",
        "user_input",
        "model_name",
        "model_response",
        "success",
        "error_message",
        "latency_seconds",
    ]

    with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Saved generated responses to: {output_csv_path}")

    # Save run metadata
    metadata = {
        "model_name": client.model_name,
        "temperature": 0.2,
        "number_of_test_cases": len(test_cases),
        "successful_requests": successful_count,
        "failed_requests": failed_count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    with open(metadata_json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved run metadata to: {metadata_json_path}")
    print("--- Sample Response Generation Finished ---")


if __name__ == "__main__":
    run_sample_evaluation()
