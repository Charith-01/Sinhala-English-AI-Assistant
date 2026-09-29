"""Runner script to validate structural integrity of final_llm_responses.csv and output summary reports."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Reconfigure sys.stdout to utf-8 on Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root directory to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.response_validator import validate_response_file


def generate_readable_summary_text(summary: dict) -> str:
    """Generate human-readable summary text report."""
    status_str = "VALID" if summary["response_file_valid"] else "INVALID"

    lines = [
        "FINAL LLM RESPONSE GENERATION SUMMARY",
        "==================================================",
        f"Timestamp: {datetime.now(timezone.utc).isoformat()}",
        f"Response File Status: {status_str}",
        f"Model Names: {', '.join(summary['model_names_found'])}",
        f"Total Expected Cases: {summary['total_expected_cases']}",
        f"Total Output Rows: {summary['total_output_rows']}",
        f"Successful Requests: {summary['successful_responses']}",
        f"Failed Requests: {summary['failed_responses']}",
        f"Average Latency: {summary['average_latency_seconds']} seconds",
        f"Missing Test IDs: {len(summary['missing_test_ids'])}",
        f"Duplicate Test IDs: {len(summary['duplicate_test_ids'])}",
        f"Empty Successful Responses: {len(summary['empty_successful_responses'])}",
    ]

    if summary["failed_test_ids"]:
        lines.append(f"Failed Test IDs: {', '.join(summary['failed_test_ids'])}")

    lines.extend([
        "==================================================",
        f"FINAL STATUS: {status_str}",
    ])

    return "\n".join(lines)


def main():
    responses_csv = root_dir / "data" / "processed" / "final_llm_responses.csv"
    results_dir = root_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    json_report_path = results_dir / "final_response_generation_summary.json"
    txt_report_path = results_dir / "final_response_generation_summary.txt"

    if not responses_csv.exists():
        print(f"Error: Responses file not found at {responses_csv}")
        sys.exit(1)

    summary = validate_response_file(responses_csv)

    txt_text = generate_readable_summary_text(summary)
    print("\n" + txt_text + "\n")

    txt_report_path.write_text(txt_text, encoding="utf-8")
    print(f"Saved text summary to: {txt_report_path}")

    json_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_expected_cases": summary["total_expected_cases"],
        "total_output_rows": summary["total_output_rows"],
        "successful_responses": summary["successful_responses"],
        "failed_responses": summary["failed_responses"],
        "failed_test_ids": summary["failed_test_ids"],
        "missing_test_ids": summary["missing_test_ids"],
        "duplicate_test_ids": summary["duplicate_test_ids"],
        "empty_successful_responses": summary["empty_successful_responses"],
        "model_names_found": summary["model_names_found"],
        "average_latency_seconds": summary["average_latency_seconds"],
        "response_file_valid": summary["response_file_valid"],
    }

    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
    print(f"Saved JSON summary to: {json_report_path}")


if __name__ == "__main__":
    main()
