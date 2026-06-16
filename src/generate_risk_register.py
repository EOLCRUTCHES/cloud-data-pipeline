from pathlib import Path
import csv


RISK_REGISTER_FILE = Path("security/risk_register.csv")


RISK_ROWS = [
    {
        "risk_id": "RISK-001",
        "risk_name": "Invalid sample data processed",
        "risk_statement": "The pipeline may process missing, malformed, or unexpected sample data if validation checks are not performed before use.",
        "impact": "Medium",
        "likelihood": "Medium",
        "risk_level": "Medium",
        "related_control": "DC-001",
        "mitigation": "Validate sample input and output files before treating them as trustworthy pipeline artifacts.",
        "evidence_file": "evidence/generated/sample_data_validation_report.md",
        "status": "Mitigated",
    },
    {
        "risk_id": "RISK-002",
        "risk_name": "Generated evidence becomes hard to locate",
        "risk_statement": "Generated evidence may become difficult to find if validation and control artifacts are not indexed.",
        "impact": "Low",
        "likelihood": "Medium",
        "risk_level": "Low",
        "related_control": "DC-002",
        "mitigation": "Generate and maintain an evidence index that lists available evidence artifacts.",
        "evidence_file": "evidence/evidence_index.md",
        "status": "Mitigated",
    },
    {
        "risk_id": "RISK-003",
        "risk_name": "Repository accumulates generated clutter",
        "risk_statement": "The repository may become difficult to review if raw API pulls, temporary outputs, and repeated generated files are committed unnecessarily.",
        "impact": "Low",
        "likelihood": "High",
        "risk_level": "Medium",
        "related_control": "Repository hygiene",
        "mitigation": "Use .gitignore rules and retain only representative sample artifacts.",
        "evidence_file": ".gitignore",
        "status": "Mitigated",
    },
]


def write_risk_register() -> None:
    """Write the risk register CSV."""
    RISK_REGISTER_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "risk_id",
        "risk_name",
        "risk_statement",
        "impact",
        "likelihood",
        "risk_level",
        "related_control",
        "mitigation",
        "evidence_file",
        "status",
    ]

    with RISK_REGISTER_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(RISK_ROWS)

    print(f"Risk register written to: {RISK_REGISTER_FILE}")


if __name__ == "__main__":
    write_risk_register()