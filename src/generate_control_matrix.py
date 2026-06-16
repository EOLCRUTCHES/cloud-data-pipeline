from pathlib import Path
import csv


CONTROL_MATRIX_FILE = Path("security/control_matrix.csv")


CONTROL_ROWS = [
    {
        "control_id": "DC-001",
        "control_name": "Sample data validation",
        "control_objective": "Confirm sample input and output files exist and contain expected fields before they are used as trusted pipeline artifacts.",
        "evidence_file": "evidence/generated/sample_data_validation_report.md",
        "automation_script": "src/validate_sample_data.py",
        "risk_addressed": "Pipeline may process missing, malformed, or unexpected data.",
        "status": "Implemented",
    },
    {
        "control_id": "DC-002",
        "control_name": "Evidence indexing",
        "control_objective": "Maintain an index of generated evidence artifacts so validation outputs are findable and reusable.",
        "evidence_file": "evidence/evidence_index.md",
        "automation_script": "src/generate_evidence_index.py",
        "risk_addressed": "Generated evidence may become difficult to locate, reducing auditability and portfolio clarity.",
        "status": "Implemented",
    },
]


def write_control_matrix() -> None:
    """Write the control matrix CSV."""
    CONTROL_MATRIX_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "control_id",
        "control_name",
        "control_objective",
        "evidence_file",
        "automation_script",
        "risk_addressed",
        "status",
    ]

    with CONTROL_MATRIX_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(CONTROL_ROWS)

    print(f"Control matrix written to: {CONTROL_MATRIX_FILE}")


if __name__ == "__main__":
    write_control_matrix()