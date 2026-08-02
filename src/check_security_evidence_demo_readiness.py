from pathlib import Path
from datetime import datetime, timezone
import csv
import sys


ARTIFACTS = {
    "Portfolio case study": Path(
        "docs/cloud/security_evidence_portfolio_case_study.md"
    ),
    "Demo runbook": Path(
        "docs/cloud/security_evidence_demo_runbook.md"
    ),
    "Control narrative": Path(
        "docs/cloud/security_evidence_control_narrative.md"
    ),
    "Evidence corpus manifest": Path(
        "ai/security_evidence_corpus_manifest.csv"
    ),
    "Status dashboard": Path(
        "docs/cloud/security_evidence_status_dashboard.md"
    ),
    "Gap register": Path(
        "ai/security_evidence_gap_register.csv"
    ),
    "Traceability exceptions": Path(
        "ai/security_evidence_traceability_exceptions.csv"
    ),
    "Management decisions": Path(
        "ai/security_evidence_exception_management_decisions.csv"
    ),
    "Decision follow-up tracker": Path(
        "ai/security_evidence_decision_followup_tracker.csv"
    ),
    "Management closeout summary": Path(
        "docs/cloud/security_evidence_management_closeout_summary.md"
    ),
    "Executive summary": Path(
        "docs/cloud/security_evidence_executive_summary.md"
    ),
}

EXECUTIVE_SUMMARY = ARTIFACTS["Executive summary"]
STATUS_DASHBOARD = ARTIFACTS["Status dashboard"]
CLOSEOUT_SUMMARY = ARTIFACTS["Management closeout summary"]

READINESS_CSV = Path("ai/security_evidence_demo_readiness.csv")
READINESS_MD = Path("docs/cloud/security_evidence_demo_readiness.md")
REPORT_FILE = Path(
    "evidence/generated/security_evidence_demo_readiness_report.md"
)


def artifact_status(path: Path) -> str:
    if not path.exists():
        return "Missing"

    if path.stat().st_size == 0:
        return "Empty"

    return "Present"


def extract_markdown_label(path: Path, label: str) -> str:
    if artifact_status(path) != "Present":
        return "not_available"

    prefix = f"{label}:".lower()

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()

        if stripped.lower().startswith(prefix):
            value = stripped.split(":", 1)[1]
            return value.replace("**", "").replace("`", "").strip()

    return "not_recorded"


def build_artifact_rows() -> list[dict[str, str]]:
    generated_at = datetime.now(timezone.utc).isoformat()

    return [
        {
            "generated_at": generated_at,
            "artifact_name": name,
            "artifact_path": path.as_posix(),
            "artifact_status": artifact_status(path),
        }
        for name, path in ARTIFACTS.items()
    ]


def get_system_posture() -> dict[str, str]:
    return {
        "executive_attention": extract_markdown_label(
            EXECUTIVE_SUMMARY,
            "Executive Attention Status",
        ),
        "evidence_system_status": extract_markdown_label(
            STATUS_DASHBOARD,
            "Overall Status",
        ),
        "management_closeout_status": extract_markdown_label(
            CLOSEOUT_SUMMARY,
            "Overall Status",
        ),
    }


def determine_demo_readiness(
    rows: list[dict[str, str]],
    posture: dict[str, str],
) -> str:
    artifact_statuses = {
        row["artifact_status"]
        for row in rows
    }

    if "Missing" in artifact_statuses:
        return "DEMO_BLOCKED_MISSING_ARTIFACTS"

    if "Empty" in artifact_statuses:
        return "DEMO_BLOCKED_EMPTY_ARTIFACTS"

    posture_values = list(posture.values())

    if any(
        value in {"not_available", "not_recorded", ""}
        for value in posture_values
    ):
        return "DEMO_READY_WITH_UNCONFIRMED_POSTURE"

    disclosure_terms = [
        "ATTENTION",
        "ACTIVE_ITEMS_TRACKED",
        "REVIEW_REQUIRED",
        "ACTION_REMAINS",
        "PENDING",
        "OVERDUE",
        "BLOCKED",
    ]

    if any(
        term in value.upper()
        for value in posture_values
        for term in disclosure_terms
    ):
        return "DEMO_READY_WITH_DISCLOSURES"

    return "DEMO_READY"


def write_csv(rows: list[dict[str, str]]) -> None:
    READINESS_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "generated_at",
        "artifact_name",
        "artifact_path",
        "artifact_status",
    ]

    with READINESS_CSV.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)


def readiness_explanation(readiness: str) -> str:
    explanations = {
        "DEMO_READY": (
            "Required artifacts are present and no posture disclosure "
            "was detected."
        ),
        "DEMO_READY_WITH_DISCLOSURES": (
            "Required artifacts are present, but the current system "
            "posture must be disclosed during the demonstration."
        ),
        "DEMO_READY_WITH_UNCONFIRMED_POSTURE": (
            "Required artifacts are present, but at least one posture "
            "value could not be confirmed automatically."
        ),
        "DEMO_BLOCKED_MISSING_ARTIFACTS": (
            "The demonstration is blocked because at least one "
            "required artifact is missing."
        ),
        "DEMO_BLOCKED_EMPTY_ARTIFACTS": (
            "The demonstration is blocked because at least one "
            "required artifact is empty."
        ),
    }

    return explanations[readiness]


def write_readiness_markdown(
    rows: list[dict[str, str]],
    posture: dict[str, str],
    readiness: str,
) -> None:
    READINESS_MD.parent.mkdir(parents=True, exist_ok=True)

    generated_at = rows[0]["generated_at"]

    lines = [
        "# Security Evidence Demo Readiness",
        "",
        f"Generated: `{generated_at}`",
        "",
        f"Demo Readiness: **{readiness}**",
        "",
        "## Readiness Interpretation",
        "",
        readiness_explanation(readiness),
        "",
        "## Current System Posture",
        "",
        "| Measure | Value |",
        "|---|---|",
        (
            "| Executive attention | "
            f"`{posture['executive_attention']}` |"
        ),
        (
            "| Evidence-system status | "
            f"`{posture['evidence_system_status']}` |"
        ),
        (
            "| Management closeout status | "
            f"`{posture['management_closeout_status']}` |"
        ),
        "",
        "## Artifact Preflight",
        "",
        "| Artifact | Status | Path |",
        "|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['artifact_name']} "
            f"| {row['artifact_status']} "
            f"| `{row['artifact_path']}` |"
        )

    lines.extend(
        [
            "",
            "## Manual Checks Still Required",
            "",
            "- Verify that the selected supported query still passes.",
            "- Verify that the demonstrated abstention behaves as expected.",
            "- Identify simulated decisions as simulated.",
            "- Confirm that no sensitive information is displayed.",
            "- Practice the walkthrough within the five-minute limit.",
            "",
            "## Demonstration Rule",
            "",
            "> Artifact readiness and system posture are different "
            "questions. A review-required posture does not prevent a "
            "demonstration, but it must be disclosed and explained.",
            "",
        ]
    )

    READINESS_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def write_report(
    rows: list[dict[str, str]],
    readiness: str,
) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    status_counts = {
        status: sum(
            row["artifact_status"] == status
            for row in rows
        )
        for status in ["Present", "Empty", "Missing"]
    }

    lines = [
        "# Security Evidence Demo Readiness Report",
        "",
        f"Generated: `{rows[0]['generated_at']}`",
        "",
        f"Overall Status: **{readiness}**",
        "",
        "## Artifact Counts",
        "",
        f"- Present: `{status_counts['Present']}`",
        f"- Empty: `{status_counts['Empty']}`",
        f"- Missing: `{status_counts['Missing']}`",
        "",
        "## Generated Artifacts",
        "",
        f"- `{READINESS_CSV.as_posix()}`",
        f"- `{READINESS_MD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
    ]

    REPORT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> int:
    rows = build_artifact_rows()
    posture = get_system_posture()
    readiness = determine_demo_readiness(
        rows,
        posture,
    )

    write_csv(rows)
    write_readiness_markdown(
        rows,
        posture,
        readiness,
    )
    write_report(
        rows,
        readiness,
    )

    print(f"Demo readiness CSV written to: {READINESS_CSV}")
    print(f"Demo readiness written to: {READINESS_MD}")
    print(f"Demo readiness report written to: {REPORT_FILE}")
    print(f"Demo Readiness: {readiness}")

    return 0


if __name__ == "__main__":
    sys.exit(main())