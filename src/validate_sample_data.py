from pathlib import Path
import csv
import json


DATA_DIR = Path("data")

JSON_FILE = DATA_DIR / "sample_api_response.json"
CSV_FILE = DATA_DIR / "sample_processed_output.csv"


def validate_json_file() -> bool:
    """Validate the sample API response JSON file."""
    if not JSON_FILE.exists():
        print(f"FAIL: Missing file: {JSON_FILE}")
        return False

    try:
        data = json.loads(JSON_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"FAIL: Invalid JSON: {error}")
        return False

    required_top_level_fields = {"source", "description", "records"}

    missing_fields = required_top_level_fields - data.keys()

    if missing_fields:
        print(f"FAIL: JSON missing fields: {missing_fields}")
        return False

    if not isinstance(data["records"], list):
        print("FAIL: JSON field 'records' must be a list")
        return False

    required_record_fields = {"id", "category", "value"}

    for record in data["records"]:
        missing_record_fields = required_record_fields - record.keys()

        if missing_record_fields:
            print(f"FAIL: JSON record missing fields: {missing_record_fields}")
            return False

    print("PASS: JSON sample file is valid")
    return True


def validate_csv_file() -> bool:
    """Validate the sample processed CSV file."""
    if not CSV_FILE.exists():
        print(f"FAIL: Missing file: {CSV_FILE}")
        return False

    required_columns = {"id", "category", "value"}

    with CSV_FILE.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            print("FAIL: CSV has no header row")
            return False

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            print(f"FAIL: CSV missing columns: {missing_columns}")
            return False

        rows = list(reader)

    if not rows:
        print("FAIL: CSV has no data rows")
        return False

    print("PASS: CSV sample file is valid")
    return True


def main() -> None:
    """Run all sample data validation checks."""
    json_valid = validate_json_file()
    csv_valid = validate_csv_file()

    if json_valid and csv_valid:
        print("PASS: All sample data validation checks passed")
    else:
        print("FAIL: One or more sample data validation checks failed")


if __name__ == "__main__":
    main()