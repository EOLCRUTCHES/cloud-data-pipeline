from pathlib import Path
from datetime import datetime, timezone
import sys


CONTROL_NARRATIVE_MD = Path(
    "docs/cloud/security_evidence_control_narrative.md"
)
EXECUTIVE_SUMMARY_MD = Path(
    "docs/cloud/security_evidence_executive_summary.md"
)
STATUS_DASHBOARD_MD = Path(
    "docs/cloud/security_evidence_status_dashboard.md"
)
CLOSEOUT_SUMMARY_MD = Path(
    "docs/cloud/security_evidence_management_closeout_summary.md"
)

PORTFOLIO_CASE_STUDY_MD = Path(
    "docs/cloud/security_evidence_portfolio_case_study.md"
)
REPORT_FILE = Path(
    "evidence/generated/security_evidence_portfolio_case_study_report.md"
)

ARTIFACTS = [
    CONTROL_NARRATIVE_MD,
    EXECUTIVE_SUMMARY_MD,
    STATUS_DASHBOARD_MD,
    CLOSEOUT_SUMMARY_MD,
    Path("ai/security_evidence_corpus_manifest.csv"),
    Path("ai/security_evidence_executive_summary.csv"),
    Path("ai/security_evidence_traceability_matrix.csv"),
    Path("ai/security_evidence_traceability_exceptions.csv"),
    Path("ai/security_evidence_decision_followup_tracker.csv"),
    Path("ai/security_evidence_management_closeout_summary.csv"),
]

REQUIRED_INPUTS = [
    CONTROL_NARRATIVE_MD,
    EXECUTIVE_SUMMARY_MD,
]


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
            value = stripped.split(":", 1)[1].strip()

            return (
                value.replace("**", "")
                .replace("`", "")
                .strip()
            )

    return "not_recorded"


def determine_portfolio_readiness() -> str:
    required_statuses = [
        artifact_status(path)
        for path in REQUIRED_INPUTS
    ]

    if (
        "Missing" in required_statuses
        or "Empty" in required_statuses
    ):
        return "PORTFOLIO_INPUTS_INCOMPLETE"

    artifact_statuses = [
        artifact_status(path)
        for path in ARTIFACTS
    ]

    if (
        "Missing" in artifact_statuses
        or "Empty" in artifact_statuses
    ):
        return "PORTFOLIO_REVIEW_REQUIRED"

    return "PORTFOLIO_CASE_STUDY_READY"


def write_case_study() -> None:
    PORTFOLIO_CASE_STUDY_MD.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    generated_at = datetime.now(timezone.utc).isoformat()
    readiness = determine_portfolio_readiness()

    executive_posture = extract_markdown_label(
        EXECUTIVE_SUMMARY_MD,
        "Executive Posture",
    )
    executive_attention = extract_markdown_label(
        EXECUTIVE_SUMMARY_MD,
        "Executive Attention Status",
    )
    evidence_status = extract_markdown_label(
        STATUS_DASHBOARD_MD,
        "Overall Status",
    )
    closeout_status = extract_markdown_label(
        CLOSEOUT_SUMMARY_MD,
        "Overall Status",
    )

    lines = [
        "# Security Evidence Automation MVP - Portfolio Case Study",
        "",
        f"Generated: `{generated_at}`",
        "",
        f"Portfolio Readiness: **{readiness}**",
        "",
        "## Executive Pitch",
        "",
        "> I built a Python-based security evidence automation MVP "
        "that collects and validates evidence, constrains AI-assisted "
        "answers to available sources, identifies unsupported "
        "questions, routes gaps through human review, and tracks "
        "exceptions through management closeout.",
        "",
        "## Problem",
        "",
        "Security evidence is frequently scattered across technical "
        "files, control records, reports, and management decisions. "
        "AI-assisted answers can make that evidence easier to use, "
        "but they can also produce unsupported claims, obscure "
        "missing evidence, or disconnect technical findings from "
        "accountable human decisions.",
        "",
        "## Solution",
        "",
        "The MVP creates a governed path from evidence collection "
        "through answer generation, evaluation, gap handling, "
        "exception management, follow-up, and closeout.",
        "",
        "```mermaid",
        "flowchart TD",
        '    A["Collect and validate evidence"] '
        '--> B["Build controlled corpus"]',
        '    B --> C["Generate bounded answers"]',
        '    C --> D["Detect gaps and exceptions"]',
        '    D --> E["Human and management review"]',
        '    E --> F["Track follow-up and closeout"]',
        "```",
        "",
        "## Current Generated Posture",
        "",
        "| Measure | Current Value |",
        "|---|---|",
        f"| Executive posture | `{executive_posture}` |",
        f"| Executive attention | `{executive_attention}` |",
        f"| Evidence-system status | `{evidence_status}` |",
        f"| Management closeout status | `{closeout_status}` |",
        "",
        "These values report the current prototype state. A "
        "review-required result means the workflow surfaced an "
        "unresolved item; it is not automatically a software failure.",
        "",
        "## Demonstrated Capabilities",
        "",
        "- Python automation using functions, paths, CSV processing, "
        "and Markdown generation.",
        "- Security-data collection, transformation, validation, "
        "and cloud-storage patterns.",
        "- Integrity, provenance, evidence manifests, and traceability.",
        "- Evidence-bounded retrieval and source-backed answers.",
        "- Evaluation, gap registration, remediation, and adjudication.",
        "- Exception ownership, management decisions, follow-up, "
        "and closeout.",
        "- Executive reporting connecting technical conditions to "
        "management attention.",
        "",
        "## Artifact Evidence",
        "",
        "| Artifact | Status |",
        "|---|---|",
    ]

    for artifact in ARTIFACTS:
        lines.append(
            f"| `{artifact.as_posix()}` | "
            f"{artifact_status(artifact)} |"
        )

    lines.extend(
        [
            "",
            "## Control Philosophy",
            "",
            "> No approved evidence, no confident answer.",
            "",
            "The system does not assume retrieval results are "
            "trustworthy. It treats them as evidence candidates, "
            "evaluates whether answers remain supported, preserves "
            "gaps, and requires human or management action before "
            "closeout.",
            "",
            "## Business Value",
            "",
            "- Reduces manual evidence-chasing and fragmented reporting.",
            "- Makes unsupported AI-assisted claims visible.",
            "- Preserves ownership and decision history.",
            "- Gives technical reviewers and executives different "
            "views of the same workflow.",
            "- Demonstrates how security requirements can become "
            "executable, reviewable controls.",
            "",
            "## Known Limitations",
            "",
            "- The prototype is local and file-based.",
            "- Retrieval uses simplified scoring rather than "
            "production semantic search.",
            "- Reviewer and management records represent a "
            "demonstration workflow.",
            "- The project does not provide production access control, "
            "monitoring, scaling, or deployment hardening.",
            "- Evidence quality depends on the source artifacts.",
            "",
            "## Five-Minute Demonstration",
            "",
            "1. Show the executive summary and current attention status.",
            "2. Show the control narrative and evidence-boundary rule.",
            "3. Trace one question from retrieval through evaluation.",
            "4. Trace one exception through decision and closeout.",
            "5. End with the artifact map and known limitations.",
            "",
            "## Resume-Ready Statement",
            "",
            "> Designed and built a Python-based security evidence "
            "automation MVP integrating evidence ingestion, "
            "validation, provenance, bounded retrieval, answer "
            "evaluation, human adjudication, exception management, "
            "and executive reporting.",
            "",
            "## Interview Takeaway",
            "",
            "> The project does not ask AI to be trustworthy by "
            "default. It builds a workflow that makes AI-assisted "
            "security claims bounded, traceable, reviewable, and "
            "management-owned.",
            "",
        ]
    )

    PORTFOLIO_CASE_STUDY_MD.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def write_report() -> None:
    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    generated_at = datetime.now(timezone.utc).isoformat()
    readiness = determine_portfolio_readiness()

    lines = [
        "# Security Evidence Portfolio Case Study Report",
        "",
        f"Generated: `{generated_at}`",
        "",
        f"Overall Status: **{readiness}**",
        "",
        "## Generated Artifacts",
        "",
        f"- `{PORTFOLIO_CASE_STUDY_MD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Required Input Health",
        "",
        "| Artifact | Status |",
        "|---|---|",
    ]

    for artifact in REQUIRED_INPUTS:
        lines.append(
            f"| `{artifact.as_posix()}` | "
            f"{artifact_status(artifact)} |"
        )

    lines.extend(
        [
            "",
            "## One-Sentence Takeaway",
            "",
            "> The case study converts the working evidence system "
            "into a portfolio-ready explanation of its problem, "
            "solution, controls, evidence, value, and limitations.",
            "",
        ]
    )

    REPORT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> int:
    write_case_study()
    write_report()

    print(
        "Portfolio case study written to: "
        f"{PORTFOLIO_CASE_STUDY_MD}"
    )
    print(f"Portfolio report written to: {REPORT_FILE}")
    print(
        "Portfolio Readiness: "
        f"{determine_portfolio_readiness()}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())