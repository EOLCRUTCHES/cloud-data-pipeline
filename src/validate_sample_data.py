from pathlib import Path
from datetime import datetime, timezone
import csv
import json


DATA_DIR = Path("data")
EVIDENCE_DIR = Path("evidence/generated")

JSON_FILE = DATA_DIR / "sample_api_response.json"
CSV_FILE = DATA_DIR / "sample_processed_output.csv"
EVIDENCE_FILE = EVIDENCE_DIR / "sample_data_validation_report.md"


def add_result(results: list[str], status: str, message: str) -> None:
    """Add a validation result to the results list and print it."""
    line = f"{status}: {message}"
    print(line)
    results.append(line)


def validate_json_file(results: list[str]) -> bool:
    """Validate the sample API response JSON file."""
    if not JSON_FILE.exists():
        add_result(results, "FAIL", f"Missing file: {JSON_FILE}")
        return False

    try:
        data = json.loads(JSON_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        add_result(results, "FAIL", f"Invalid JSON: {error}")
        return False

    required_top_level_fields = {"source", "description", "records"}
    missing_fields = required_top_level_fields - data.keys()

    if missing_fields:
        add_result(results, "FAIL", f"JSON missing fields: {missing_fields}")
        return False

    if not isinstance(data["records"], list):
        add_result(results, "FAIL", "JSON field 'records' must be a list")
        return False

    required_record_fields = {"id", "category", "value"}

    for record in data["records"]:
        missing_record_fields = required_record_fields - record.keys()

        if missing_record_fields:
            add_result(results, "FAIL", f"JSON record missing fields: {missing_record_fields}")
            return False

    add_result(results, "PASS", "JSON sample file is valid")
    return True


def validate_csv_file(results: list[str]) -> bool:
    """Validate the sample processed CSV file."""
    if not CSV_FILE.exists():
        add_result(results, "FAIL", f"Missing file: {CSV_FILE}")
        return False

    required_columns = {"id", "category", "value"}

    with CSV_FILE.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            add_result(results, "FAIL", "CSV has no header row")
            return False

        missing_columns = required_columns - set(reader.fieldnames)

        if missing_columns:
            add_result(results, "FAIL", f"CSV missing columns: {missing_columns}")
            return False

        rows = list(reader)

    if not rows:
        add_result(results, "FAIL", "CSV has no data rows")
        return False

    add_result(results, "PASS", "CSV sample file is valid")
    return True


def write_evidence_report(results: list[str], overall_status: str) -> None:
    """Write validation results to a markdown evidence report."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    report = [
        "# Sample Data Validation Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Validation Results",
        "",
    ]

    for result in results:
        report.append(f"- {result}")

    report.extend(
        [
            "",
            "## Files Validated",
            "",
            f"- `{JSON_FILE}`",
            f"- `{CSV_FILE}`",
            "",
            "## Portfolio Relevance",
            "",
            "This report demonstrates that sample data files are validated before being treated as trustworthy pipeline inputs or outputs.",
            "",
        ]
    )

    EVIDENCE_FILE.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    """Run all sample data validation checks and generate evidence."""
    results = []

    json_valid = validate_json_file(results)
    csv_valid = validate_csv_file(results)

    if json_valid and csv_valid:
        overall_status = "PASS"
        add_result(results, "PASS", "All sample data validation checks passed")
    else:
        overall_status = "FAIL"
        add_result(results, "FAIL", "One or more sample data validation checks failed")

    write_evidence_report(results, overall_status)

    print(f"Evidence report written to: {EVIDENCE_FILE}")


if __name__ == "__main__":
    main()