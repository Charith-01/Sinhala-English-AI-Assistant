"""Evaluation completion tracking script.

Monitors progress of manual human scoring across the 60 final evaluation cases.
"""

import csv
import sys
from pathlib import Path
from typing import Dict, List

# Reconfigure stdout for utf-8 on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root directory to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))


def check_progress(worksheet_path: Path):
    if not worksheet_path.exists():
        print(f"Error: Evaluation worksheet not found at {worksheet_path}")
        sys.exit(1)

    rows: List[dict] = []
    with open(worksheet_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total_cases = len(rows)
    completed_count = 0
    pending_count = 0
    tech_fail_count = 0
    invalid_completed_count = 0

    lang_completed: Dict[str, int] = {"english": 0, "sinhala": 0, "singlish": 0, "code_mixed": 0}
    lang_total: Dict[str, int] = {"english": 0, "sinhala": 0, "singlish": 0, "code_mixed": 0}

    next_pending_ids: List[str] = []
    scoring_fields = [
        "policy_correctness",
        "intent_understanding",
        "relevance",
        "completeness",
        "language_appropriateness",
        "safety_privacy",
        "hallucination_control",
    ]

    for row in rows:
        tid = row.get("test_id", "").strip()
        status = str(row.get("evaluation_status", "")).strip().lower()
        lang = str(row.get("language_type", "")).strip().lower()

        if lang in lang_total:
            lang_total[lang] += 1

        if status == "completed":
            completed_count += 1
            if lang in lang_completed:
                lang_completed[lang] += 1

            # Validate whether all 7 scores are present and valid
            is_valid_completed = True
            for sf in scoring_fields:
                val = str(row.get(sf, "")).strip()
                if val not in {"0", "1", "2"}:
                    is_valid_completed = False
                    break
            if not is_valid_completed:
                invalid_completed_count += 1

        elif status == "technical_failure":
            tech_fail_count += 1
        else:
            # pending or blank
            pending_count += 1
            if len(next_pending_ids) < 10:
                next_pending_ids.append(tid)

    print("HUMAN EVALUATION PROGRESS SUMMARY")
    print("==================================================")
    print(f"Total Cases: {total_cases}")
    print(f"Completed: {completed_count}")
    print(f"Pending: {pending_count}")
    print(f"Technical Failures: {tech_fail_count}")
    print(f"Invalid Completed Rows: {invalid_completed_count}")
    print("\nProgress by Language Modality:")
    for l_key in ["english", "sinhala", "singlish", "code_mixed"]:
        c_num = lang_completed.get(l_key, 0)
        t_num = lang_total.get(l_key, 0)
        print(f"  - {l_key.capitalize()} completed: {c_num} / {t_num}")

    if next_pending_ids:
        print("\nNext Pending Test IDs:")
        print("  - " + ", ".join(next_pending_ids))

    print("==================================================")


def main():
    worksheet_csv = root_dir / "data" / "processed" / "final_evaluation_worksheet.csv"
    check_progress(worksheet_csv)


if __name__ == "__main__":
    main()
