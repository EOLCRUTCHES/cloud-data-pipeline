from pathlib import Path
from datetime import datetime, timezone


MANIFEST_FILE = Path("evidence/generated/artifact_manifest.md")


ARTIFACTS = [
    {
        "group": "Sample Data",
        "path": "data/sample_api_response.json",
        "purpose": "Demo-safe raw API-style input data",
    },
    {
        "group": "Sample Data",
        "path": "data/sample_processed_output.csv",
        "purpose": "Demo-safe processed pipeline output",
    },
    {
        "group": "Automation Script",
        "path": "src/validate_sample_data.py",
        "purpose": "Validates sample data and creates validation evidence",
    },
    {
        "group": "Automation Script",
        "path": "src/generate_evidence_index.py",
        "purpose": "Generates the evidence index",
    },
    {
        "group": "Automation Script",
        "path": "src/generate_control_matrix.py",
        "purpose": "Generates the control matrix",
    },
    {
        "group": "Automation Script",
        "path": "src/generate_risk_register.py",
        "purpose": "Generates the risk register",
    },
    {
        "group": "Automation Script",
        "path": "src/run_governance_workflow.py",
        "purpose": "Runs the governance workflow",
    },
    {
        "group": "Evidence",
        "path": "evidence/generated/sample_data_validation_report.md",
        "purpose": "Shows sample data validation results",
    },
    {
        "group": "Evidence",
        "path": "evidence/generated/governance_workflow_run_report.md",
        "purpose": "Shows workflow execution results",
    },
    {
        "group": "Evidence",
        "path": "evidence/evidence_index.md",
        "purpose": "Lists generated evidence artifacts",
    },
    {
        "group": "Security Governance",
        "path": "security/control_matrix.csv",
        "purpose": "Maps controls to evidence and risks",
    },
    {
        "group": "Security Governance",
        "path": "security/risk_register.csv",
        "purpose": "Maps risks to mitigations, controls, and evidence",
    },
    {
        "group": "Documentation",
        "path": "docs/executive_summary.md",
        "purpose": "Explains the project in executive language",
    },
    {
        "group": "Documentation",
        "path": "docs/architecture_diagram.md",
        "purpose": "Shows the secure automation workflow architecture",
    },
]


def get_file_status(file_path: Path) -> tuple[str, str]:
    """Return file existence and size."""
    if not file_path.exists():
        return "Missing", "0"

    return "Present", str(file_path.stat().st_size)


def build_manifest() -> str:
    """Build the artifact manifest markdown."""
    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Artifact Manifest",
        "",
        f"Generated: `{timestamp}`",
        "",
        "## Purpose",
        "",
        "This manifest lists important project artifacts and confirms whether they exist.",
        "",
        "It supports portfolio review, audit readiness, evidence organization, and future provenance tracking.",
        "",
        "## Artifact Inventory",
        "",
        "| Group | Artifact | Status | Size Bytes | Purpose |",
        "|---|---|---|---:|---|",
    ]

    for artifact in ARTIFACTS:
        artifact_path = Path(artifact["path"])
        status, size = get_file_status(artifact_path)

        lines.append(
            f"| {artifact['group']} | `{artifact['path']}` | {status} | {size} | {artifact['purpose']} |"
        )

    lines.extend(
        [
            "",
            "## Portfolio Relevance",
            "",
            "This manifest demonstrates that the project can inventory its own important artifacts.",
            "",
            "That pattern will later support evidence packaging, artifact integrity checks, provenance records, and trust architecture.",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    """Generate the artifact manifest."""
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest()

    MANIFEST_FILE.write_text(manifest, encoding="utf-8")

    print(f"Artifact manifest written to: {MANIFEST_FILE}")


if __name__ == "__main__":
    main()