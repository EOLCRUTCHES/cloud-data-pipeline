from pathlib import Path
from datetime import datetime, timezone
import sys


NARRATIVE_MD = Path("docs/cloud/security_evidence_control_narrative.md")
REPORT_FILE = Path("evidence/generated/security_evidence_control_narrative_report.md")


REFERENCED_ARTIFACTS = [
    Path("security/aws_admin_port_exposure_findings.csv"),
    Path("security/aws_evidence_collector_permissions.csv"),
    Path("security/aws_admin_port_remediation_register.csv"),
    Path("ai/security_evidence_corpus_manifest.csv"),
    Path("ai/security_evidence_eval_results.csv"),
    Path("ai/security_evidence_gap_register.csv"),
    Path("ai/security_evidence_gap_closure_register.csv"),
    Path("ai/security_evidence_reviewer_decisions.csv"),
    Path("ai/security_evidence_adjudicated_gap_status.csv"),
    Path("ai/security_evidence_status_summary.csv"),
    Path("ai/security_evidence_traceability_matrix.csv"),
    Path("ai/security_evidence_traceability_exceptions.csv"),
    Path("ai/security_evidence_exception_action_plan.csv"),
    Path("ai/security_evidence_exception_review_status.csv"),
    Path("ai/security_evidence_exception_management_decisions.csv"),
    Path("ai/security_evidence_decision_followup_tracker.csv"),
    Path("ai/security_evidence_management_closeout_summary.csv"),
]


def artifact_status(path: Path) -> str:
    if path.exists() and path.stat().st_size > 0:
        return "Present"
    if path.exists() and path.stat().st_size == 0:
        return "Empty"
    return "Missing"


def safe_cell(value: object) -> str:
    return str(value).replace("|", " ").replace("\n", " ").strip()


def artifact_purpose(path: Path) -> str:
    purpose_by_name = {
        "aws_admin_port_exposure_findings.csv": "Records AWS security group findings for administrative ports.",
        "aws_evidence_collector_permissions.csv": "Shows whether the evidence collector has required AWS permissions.",
        "aws_admin_port_remediation_register.csv": "Records remediation evidence for administrative port exposure.",
        "security_evidence_corpus_manifest.csv": "Lists approved evidence records available for retrieval.",
        "security_evidence_eval_results.csv": "Tests whether the answer layer stays inside available evidence.",
        "security_evidence_gap_register.csv": "Records unsupported questions and evidence gaps.",
        "security_evidence_gap_closure_register.csv": "Maps evidence gaps to possible closure evidence.",
        "security_evidence_reviewer_decisions.csv": "Records human reviewer decisions.",
        "security_evidence_adjudicated_gap_status.csv": "Converts reviewer decisions into final gap status.",
        "security_evidence_status_summary.csv": "Summarizes the evidence system posture.",
        "security_evidence_traceability_matrix.csv": "Maps artifacts to control questions and lifecycle stages.",
        "security_evidence_traceability_exceptions.csv": "Identifies missing, pending, open, or incomplete evidence states.",
        "security_evidence_exception_action_plan.csv": "Assigns ownership and next steps for exceptions.",
        "security_evidence_exception_review_status.csv": "Summarizes items requiring management review.",
        "security_evidence_exception_management_decisions.csv": "Records management decisions.",
        "security_evidence_decision_followup_tracker.csv": "Tracks required decision follow-up.",
        "security_evidence_management_closeout_summary.csv": "Summarizes whether management follow-up reached closeout.",
    }

    return purpose_by_name.get(path.name, "Supports the security evidence workflow.")


def determine_artifact_health() -> str:
    statuses = [artifact_status(path) for path in REFERENCED_ARTIFACTS]

    if "Missing" in statuses:
        return "ARTIFACTS_MISSING"

    if "Empty" in statuses:
        return "ARTIFACTS_EMPTY"

    return "ARTIFACTS_PRESENT"


def write_narrative() -> None:
    NARRATIVE_MD.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    artifact_health = determine_artifact_health()

    lines = [
        "# Security Evidence Control Narrative",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Artifact Health: **{artifact_health}**",
        "",
        "## Executive Summary",
        "",
        "This control narrative describes a local Security AI evidence workflow that constrains answers to approved evidence, identifies evidence gaps, routes closure through human review, records management decisions, and tracks follow-up through closeout.",
        "",
        "The purpose of this system is not to let AI make unsupported security claims. The purpose is to organize evidence, force source-backed answers, expose gaps, and make review decisions auditable.",
        "",
        "## Control Objective",
        "",
        "Ensure that security evidence used for automated or AI-assisted answers is approved, traceable, reviewed, exception-managed, and closed through documented human or management action.",
        "",
        "## Control Flow",
        "",
        "```text",
        "evidence collection",
        "↓",
        "permission preflight",
        "↓",
        "evidence workflow packaging",
        "↓",
        "controlled evidence corpus",
        "↓",
        "bounded retrieval",
        "↓",
        "source-backed answer layer",
        "↓",
        "guardrail evaluation",
        "↓",
        "evidence gap register",
        "↓",
        "remediation evidence",
        "↓",
        "gap closure register",
        "↓",
        "human reviewer decisions",
        "↓",
        "adjudicated gap status",
        "↓",
        "status dashboard",
        "↓",
        "traceability matrix",
        "↓",
        "exception register",
        "↓",
        "exception action plan",
        "↓",
        "exception review packet",
        "↓",
        "management decision log",
        "↓",
        "decision follow-up tracker",
        "↓",
        "management closeout summary",
        "```",
        "",
        "## Key Governance Rules",
        "",
        "1. No approved evidence, no confident answer.",
        "2. Retrieval results are not automatically trusted; they are evidence candidates.",
        "3. Unsupported questions become evidence gaps.",
        "4. New evidence does not automatically close a gap.",
        "5. Closure requires a human reviewer decision.",
        "6. Reviewer decisions must include reviewer, date, and notes.",
        "7. Exceptions must be visible, owned, prioritized, and reviewed.",
        "8. Management decisions must be documented before follow-up can be tracked.",
        "9. Follow-up requiring action must have an owner, due date, status, and completion evidence.",
        "10. Closeout requires evidence, rationale, cancellation, or explicit no-follow-up status.",
        "",
        "## Artifact Map",
        "",
        "| Artifact | Status | Purpose |",
        "|---|---|---|",
    ]

    for artifact in REFERENCED_ARTIFACTS:
        lines.append(
            f"| `{artifact.as_posix()}` | "
            f"{safe_cell(artifact_status(artifact))} | "
            f"{safe_cell(artifact_purpose(artifact))} |"
        )

    lines.extend(
        [
            "",
            "## Control Strengths",
            "",
            "- Separates supported answers from unsupported claims.",
            "- Preserves evidence gaps instead of hiding them.",
            "- Forces human review before closure.",
            "- Records management decisions separately from technical findings.",
            "- Tracks follow-up through active, blocked, overdue, completed, cancelled, or not-applicable states.",
            "- Produces both machine-readable CSVs and human-readable Markdown artifacts.",
            "",
            "## Known Limitations",
            "",
            "- The retrieval layer is simple token scoring, not production semantic retrieval.",
            "- The evidence corpus is local and file-based.",
            "- Simulated reviewer or management decisions are not real organizational approvals.",
            "- Evidence quality still depends on the quality of the source artifacts.",
            "- This prototype demonstrates governance logic, not production-grade access control, logging, or deployment hardening.",
            "",
            "## Portfolio Positioning",
            "",
            "This project demonstrates secure automation and governed AI assistance for security evidence workflows. It shows the ability to design audit-friendly automation that collects evidence, constrains answer generation, identifies gaps, records review decisions, tracks exceptions, and follows management action through closeout.",
            "",
            "## Executive Translation",
            "",
            "The system creates a controlled path from evidence collection to answer generation, gap detection, remediation, review, exception management, decision logging, follow-up, and closeout.",
            "",
            "In plain English:",
            "",
            "> The system does not ask AI to be trustworthy by default. It builds a workflow that makes trust reviewable.",
            "",
            "## One-Sentence Takeaway",
            "",
            "> This system turns security evidence into a controlled, traceable, reviewable, and management-owned workflow.",
            "",
        ]
    )

    NARRATIVE_MD.write_text("\n".join(lines), encoding="utf-8")


def write_report() -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    artifact_health = determine_artifact_health()

    lines = [
        "# Security Evidence Control Narrative Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{artifact_health}**",
        "",
        "## Generated Artifacts",
        "",
        f"- `{NARRATIVE_MD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Referenced Artifact Health",
        "",
        "| Artifact | Status |",
        "|---|---|",
    ]

    for artifact in REFERENCED_ARTIFACTS:
        lines.append(f"| `{artifact.as_posix()}` | {artifact_status(artifact)} |")

    lines.extend(
        [
            "",
            "## One-Sentence Takeaway",
            "",
            "> The control narrative explains how the evidence workflow operates as a governed security system.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    write_narrative()
    write_report()

    print(f"Control narrative written to: {NARRATIVE_MD}")
    print(f"Control narrative report written to: {REPORT_FILE}")
    print(f"Artifact Health: {determine_artifact_health()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())