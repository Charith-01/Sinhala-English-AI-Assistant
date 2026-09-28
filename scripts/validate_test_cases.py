"""Utility script to validate test case CSV files against project schema and business rules."""

import sys
from pathlib import Path

# Add project root directory to path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.test_case_loader import load_test_cases


def validate_file(file_path: Path) -> bool:
    """Validate a single test case CSV file."""
    print(f"Validating: {file_path}")
    try:
        cases = load_test_cases(file_path)
        print(f"Successfully loaded {len(cases)} test cases from {file_path.name}")
        return True
    except Exception as e:
        print(f"Validation failed for {file_path.name}: {e}")
        return False


def main():
    raw_dir = root_dir / "data" / "raw"

    csv_files = list(raw_dir.glob("*.csv"))
    if not csv_files:
        print("No CSV files found in data/raw/")
        sys.exit(1)

    all_passed = True
    for csv_file in csv_files:
        if csv_file.name == "test_cases_template.csv":
            continue
        if not validate_file(csv_file):
            all_passed = False

    if all_passed:
        print("All test case files validated successfully!")
        sys.exit(0)
    else:
        print("Some test case files failed validation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
