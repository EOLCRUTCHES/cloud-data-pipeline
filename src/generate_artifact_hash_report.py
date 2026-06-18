from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib


HASH_CSV_FILE = Path("provenance/artifact_hashes.csv")
HASH_REPORT_FILE = Path("evidence/generated/artifact_hash_report.md")


ARTIFACTS = [
    {"group": "Sample Data", "path": "data/sample_api_response.json", "purpose": "Demo-safe raw API-style input data"},
    {"group": "Sample Data", "path": "data/sample_processed_output.csv", "purpose": "Demo-safe processed pipeline output"},
    {"group": "Automation Script", "path": "src/validate_sample_data.py", "purpose": "Validates sample data and creates validation evidence"},
    {"group": "Automation Script", "path": "src/generate_evidence_index.py", "purpose": "Generates the evidence index"},
    {"group": "Automation Script", "path": "src/generate_control_matrix.py", "purpose": "Generates the control matrix"},
    {"group": "Automation Script", "path": "src/generate_risk_register.py", "purpose": "Generates the risk register"},
    {"group": "Automation Script", "path": "src/generate_artifact_manifest.py", "purpose": "Generates the artifact manifest"},
    {"group": "Automation Script", "path": "src/run_governance_workflow.py", "purpose": "Runs the governance workflow"},
    {"group": "Evidence", "path": "evidence/generated/sample_data_validation_report.md", "purpose": "Shows sample data validation results"},
    {"group": "Evidence", "path": "evidence/generated/governance_workflow_run_report.md", "purpose": "Shows workflow execution results"},
    {"group": "Evidence", "path": "evidence/generated/artifact_manifest.md", "purpose": "Lists important project artifacts"},
    {"group": "Evidence", "path": "evidence/evidence_index.md", "purpose": "Lists generated evidence artifacts"},
    {"group": "Security Governance", "path": "security/control_matrix.csv", "purpose": "Maps controls to evidence and risks"},
    {"group": "Security Governance", "path": "security/risk_register.csv", "purpose": "Maps risks to mitigations, controls, and evidence"},
    {"group": "Documentation", "path": "docs/executive_summary.md", "purpose": "Explains the project in executive language"},
    {"group": "Documentation", "path": "docs/architecture_diagram.md", "purpose": "Shows the secure automation workflow architecture"},
]


def calculate_sha256(file_path: Path) -> str:
    """Calculate the SHA-256 hash for a file."""
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)

    return digest.hexdigest()


def build_hash_rows() -> list[dict[str, str]]:
    """Build artifact hash rows."""
    rows = []

    for artifact in ARTIFACTS:
        artifact_path = Path(artifact["path"])

        if artifact_path.exists():
            status = "Present"
            size_bytes = str(artifact_path.stat().st_size)
            sha256 = calculate_sha256(artifact_path)
        else:
            status = "Missing"
            size_bytes = "0"
            sha256 = ""

        rows.append(
            {
                "group": artifact["group"],
                "path": artifact["path"],
                "status": status,
                "size_bytes": size_bytes,
                "sha256": sha256,
                "purpose": artifact["purpose"],
            }
        )

    return rows


def write_hash_csv(rows: list[dict[str, str]]) -> None:
    """Write artifact hashes to CSV."""
    HASH_CSV_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["group", "path", "status", "size_bytes", "sha256", "purpose"]

    with HASH_CSV_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_hash_report(rows: list[dict[str, str]]) -> None:
    """Write artifact hash evidence report."""
    HASH_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    present_count = sum(1 for row in rows if row["status"] == "Present")
    missing_count = sum(1 for row in rows if row["status"] == "Missing")

    lines = [
        "# Artifact Hash Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        "## Purpose",
        "",
        "This report records SHA-256 hashes for important project artifacts.",
        "",
        "Hashes support artifact integrity, provenance, and tamper-evidence patterns.",
        "",
        "## Summary",
        "",
        f"- Present artifacts: {present_count}",
        f"- Missing artifacts: {missing_count}",
        f"- Hash CSV: `{HASH_CSV_FILE}`",
        "",
        "## Artifact Hashes",
        "",
        "| Group | Artifact | Status | Size Bytes | SHA-256 |",
        "|---|---|---|---:|---|",
    ]

    for row in rows:
        short_hash = row["sha256"][:16] + "..." if row["sha256"] else ""
        lines.append(
            f"| {row['group']} | `{row['path']}` | {row['status']} | {row['size_bytes']} | `{short_hash}` |"
        )

    lines.extend(
        [
            "",
            "## Portfolio Relevance",
            "",
            "This report demonstrates a basic trust architecture pattern: important artifacts are inventoried and fingerprinted so future changes can be detected.",
            "",
            "This is a foundation for provenance tracking, evidence integrity, and tamper-evident security automation.",
            "",
        ]
    )

    HASH_REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Generate artifact hash evidence."""
    rows = build_hash_rows()

    write_hash_csv(rows)
    write_hash_report(rows)

    print(f"Artifact hashes written to: {HASH_CSV_FILE}")
    print(f"Artifact hash report written to: {HASH_REPORT_FILE}")


if __name__ == "__main__":
    main()