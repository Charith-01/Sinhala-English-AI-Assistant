"""Runner script to perform full dataset validation and generate report artifacts.

Outputs:
- Console report summary
- results/final_dataset_validation.json
- results/final_dataset_validation.txt
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure stdout uses utf-8 encoding on Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root directory to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.dataset_validator import validate_dataset


def generate_readable_text_report(results: dict) -> str:
    """Generate a clean human-readable text report from validation results."""
    status_str = "PASSED" if results["validation_passed"] else "FAILED"
    if results["validation_passed"] and results["warning_count"] > 0:
        status_str = "PASSED WITH WARNINGS"

    lines = [
        "FINAL DATASET VALIDATION REPORT",
        "==================================================",
        f"Timestamp: {datetime.now(timezone.utc).isoformat()}",
        f"Validation Status: {status_str}",
        f"Total Test Cases: {results['total_cases']}",
        f"Errors: {results['error_count']}",
        f"Warnings: {results['warning_count']}",
        "",
        "Linguistic Modality Distribution:",
    ]

    for lang, count in results.get("language_distribution", {}).items():
        lines.append(f"  - {lang}: {count}")

    lines.extend([
        "",
        "Difficulty Level Distribution:",
    ])
    for diff, count in results.get("difficulty_distribution", {}).items():
        lines.append(f"  - {diff}: {count}")

    lines.extend([
        "",
        "Category Distribution:",
    ])
    for cat, count in results.get("category_distribution", {}).items():
        lines.append(f"  - {cat}: {count}")

    lines.extend([
        "",
        "Behavioral Counts:",
        f"  - Requires Clarification: {results['clarification_count']}",
        f"  - Requires Escalation: {results['escalation_count']}",
        f"  - Cases referencing Policy IDs: {results['cases_with_policy_ids']}",
        f"  - Cases without Policy IDs: {results['cases_without_policy_ids']}",
        "",
        "Top Referenced Policy IDs:",
    ])

    sorted_policies = sorted(
        results.get("policy_reference_counts", {}).items(),
        key=lambda x: x[1],
        reverse=True,
    )
    for pol_id, count in sorted_policies[:10]:
        lines.append(f"  - {pol_id}: {count} references")

    if results["errors"]:
        lines.extend(["", "ERRORS FOUND:"])
        for err in results["errors"]:
            lines.append(f"  - [ERROR] {err}")

    if results["warnings"]:
        lines.extend(["", "WARNINGS LOGGED:"])
        for warn in results["warnings"]:
            lines.append(f"  - [WARNING] {warn}")

    lines.extend([
        "",
        "==================================================",
        f"FINAL STATUS: {status_str}",
    ])

    return "\n".join(lines)


def main():
    raw_csv = root_dir / "data" / "raw" / "final_test_cases.csv"
    sample_csv = root_dir / "data" / "raw" / "sample_test_cases.csv"
    results_dir = root_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    json_report_path = results_dir / "final_dataset_validation.json"
    txt_report_path = results_dir / "final_dataset_validation.txt"

    print(f"Running validation on: {raw_csv}")
    results = validate_dataset(raw_csv, sample_csv if sample_csv.exists() else None)

    # Format text report
    text_report = generate_readable_text_report(results)
    print("\n" + text_report + "\n")

    # Write text report
    txt_report_path.write_text(text_report, encoding="utf-8")
    print(f"Saved human-readable report to: {txt_report_path}")

    # Write JSON report
    json_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_cases": results["total_cases"],
        "error_count": results["error_count"],
        "warning_count": results["warning_count"],
        "validation_passed": results["validation_passed"],
        "errors": results["errors"],
        "warnings": results["warnings"],
        "language_distribution": results["language_distribution"],
        "difficulty_distribution": results["difficulty_distribution"],
        "category_distribution": results["category_distribution"],
        "clarification_count": results["clarification_count"],
        "escalation_count": results["escalation_count"],
        "cases_with_policy_ids": results["cases_with_policy_ids"],
        "cases_without_policy_ids": results["cases_without_policy_ids"],
        "policy_reference_counts": results["policy_reference_counts"],
    }

    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
    print(f"Saved JSON report to: {json_report_path}")

    if not results["validation_passed"]:
        print("\n[FAIL] Validation failed with errors! Please fix dataset errors before proceeding.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Validation completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
