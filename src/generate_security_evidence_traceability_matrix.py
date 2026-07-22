from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import re
import sys


TRACEABILITY_MATRIX = Path("ai/security_evidence_traceability_matrix.csv")
TRACEABILITY_MD = Path("docs/cloud/security_evidence_traceability_matrix.md")
REPORT_FILE = Path("evidence/generated/security_evidence_traceability_report.md")


TRACEABILITY_ITEMS = [
    {
        "lifecycle_stage": "Permission Preflight",
        "control_question": "Was the collector authorized to inspect the required AWS evidence?",
        "artifact_path": "security/aws_evidence_collector_permissions.csv",
        "artifact_type": "csv",
        "machine_readable": "yes",
        "evidence_contribution": "Records AWS permission checks before evidence collection.",
    },
    {
        "lifecycle_stage": "Evidence Collection",
        "control_question": "What AWS administrative port exposure was observed?",
        "artifact_path": "security/aws_admin_port_exposure_findings.csv",
        "artifact_type": "csv",
        "machine_readable": "yes",
        "evidence_contribution": "Records discovered SSH, RDP, and WinRM exposure findings.",
    },
    {
        "lifecycle_stage": "Evidence Workflow",
        "control_question": "Was collection packaged into a reviewable evidence workflow?",
        "artifact_path": "docs/cloud/aws_admin_access_evidence_package.md",
        "artifact_type": "markdown",
        "machine_readable": "no",
        "evidence_contribution": "Explains the admin-access evidence workflow and review package.",
    },
    {
        "lifecycle_stage": "Evidence Workflow",
        "control_question": "What was the latest workflow execution result?",
        "artifact_path": "evidence/generated/aws_admin_access_evidence_workflow_report.md",
        "artifact_type": "markdown",
        "machine_readable": "no",
        "evidence_contribution": "Records the generated workflow execution report.",
    },
    {
        "lifecycle_stage": "Corpus",
        "control_question": "Which approved evidence artifacts are available for retrieval?",
        "artifact_path": "ai/security_evidence_corpus_manifest.csv",
        "artifact_type": "csv",
        "machine_readable": "yes",
        "evidence_contribution": "Lists indexed corpus records and their source artifacts.",
    },
    {
        "lifecycle_stage": "Corpus",
        "control_question": "What is the approved local evidence corpus content?",
        "artifact_path": "ai/security_evidence_corpus.jsonl",
        "artifact_type": "jsonl",
        "machine_readable": "yes",
        "evidence_contribution": "Stores approved evidence records for bounded retrieval.",
    },
    {
        "lifecycle_stage": "Retrieval",
        "control_question": "Which evidence was retrieved for security questions?",
        "artifact_path": "ai/security_evidence_query_results.csv",
        "artifact_type": "csv",
        "machine_readable": "yes",
        "evidence_contribution": "Records query results, matched terms, scores, and source paths.",
    },
    {
        "lifecycle_stage": "Answer Layer",
        "control_question": "Did the answer layer cite approved local evidence?",
        "artifact_path": "ai/security_evidence_answer_sources.csv",
        "artifact_type": "csv",
        "machine_readable": "yes",
        "evidence_contribution": "Lists source records used by the source-backed answer layer.",
    },
    {
        "lifecycle_stage": "Answer Layer",
        "control_question": "What source-backed answer was generated?",
        "artifact_path": "ai/security_evidence_answer.md",
        "artifact_type": "markdown",
        "machine_readable": "no",
        "evidence_contribution": "Provides the human-readable answer and its source constraints.",
    },
    {
        "lifecycle_stage": "Evaluation",
        "control_question": "Are answer guardrails passing?",
        "artifact_path": "ai/security_evidence_eval_results.csv",
        "artifact_type": "csv",
        "machine_readable": "yes",
        "evidence_contribution": "Records guardrail evaluation results for supported and unsupported questions.",
    },
    {
        "lifecycle_stage": "Gap Management",
        "control_question": "Which unsupported questions became managed evidence gaps?",
        "artifact_path": "ai/security_evidence_gap_register.csv",
        "artifact_type": "csv",
        "machine_readable": "yes",
        "evidence_contribution": "Records evidence gaps, supported questions, and out-of-scope items.",
    },
    {
        "lifecycle_stage": "Remediation Evidence",
        "control_question": "What evidence supports admin-port remediation?",
        "artifact_path": "security/aws_admin_port_remediation_register.csv",
        "artifact_type": "csv",
        "machine_readable": "yes",
        "evidence_contribution": "Records remediation closure status for AWS admin-port exposure.",
    },
    {
        "lifecycle_stage": "Remediation Evidence",
        "control_question": "What human-readable remediation record exists?",
        "artifact_path": "docs/cloud/aws_admin_port_remediation_record.md",
        "artifact_type": "markdown",
        "machine_readable": "no",
        "evidence_contribution": "Explains the remediation evidence and limitations.",
    },
    {
        "lifecycle_stage": "Gap Closure",
        "control_question": "Which gaps have closure evidence available?",
        "artifact_path": "ai/security_evidence_gap_closure_register.csv",
        "artifact_type": "csv",
        "machine_readable": "yes",
        "evidence_contribution": "Maps evidence gaps to closure evidence and recommended closure treatment.",
    },
    {
        "lifecycle_stage": "Human Review",
        "control_question": "Who reviewed closure and what did they decide?",
        "artifact_path": "ai/security_evidence_reviewer_decisions.csv",
        "artifact_type": "csv",
        "machine_readable": "yes",
        "evidence_contribution": "Records reviewer decisions, reviewer identity, date, and notes.",
    },
    {
        "lifecycle_stage": "Adjudication",
        "control_question": "What is the final adjudicated status of each gap?",
        "artifact_path": "ai/security_evidence_adjudicated_gap_status.csv",
        "artifact_type": "csv",
        "machine_readable": "yes",
        "evidence_contribution": "Converts reviewer decisions into final gap status.",
    },
    {
        "lifecycle_stage": "Adjudication",
        "control_question": "What is the human-readable adjudication summary?",
        "artifact_path": "docs/cloud/security_evidence_adjudication_summary.md",
        "artifact_type": "markdown",
        "machine_readable": "no",
        "evidence_contribution": "Summarizes adjudicated gap status for review.",
    },
    {
        "lifecycle_stage": "Status Dashboard",
        "control_question": "What is the current health of the evidence system?",
        "artifact_path": "ai/security_evidence_status_summary.csv",
        "artifact_type": "csv",
        "machine_readable": "yes",
        "evidence_contribution": "Provides machine-readable posture metrics.",
    },
    {
        "lifecycle_stage": "Status Dashboard",
        "control_question": "What dashboard can an executive or auditor read?",
        "artifact_path": "docs/cloud/security_evidence_status_dashboard.md",
        "artifact_type": "markdown",
        "machine_readable": "no",
        "evidence_contribution": "Provides human-readable posture, next actions, and artifact health.",
    },
    {
        "lifecycle_stage": "Evidence Index",
        "control_question": "Where is the consolidated evidence index?",
        "artifact_path": "evidence/evidence_index.md",
        "artifact_type": "markdown",
        "machine_readable": "no",
        "evidence_contribution": "Provides a central index of generated evidence artifacts.",
    },
]


CSV_SIGNAL_FIELDS = {
    "aws_evidence_collector_permissions.csv": "status",
    "aws_admin_port_exposure_findings.csv": "severity",
    "security_evidence_query_results.csv": "query_id",
    "security_evidence_answer_sources.csv": "document_id",
    "security_evidence_eval_results.csv": "overall_result",
    "security_evidence_gap_register.csv": "gap_status",
    "aws_admin_port_remediation_register.csv": "closure_status",
    "security_evidence_gap_closure_register.csv": "closure_status",
    "security_evidence_reviewer_decisions.csv": "reviewer_decision",
    "security_evidence_adjudicated_gap_status.csv": "final_gap_status",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def artifact_status(path: Path) -> str:
    if path.exists() and path.stat().st_size > 0:
        return "Present"
    if path.exists() and path.stat().st_size == 0:
        return "Empty"
    return "Missing"


def counter_summary(counter: Counter) -> str:
    if not counter:
        return "no_rows"

    return "; ".join(f"{key}={value}" for key, value in sorted(counter.items()))


def count_field(rows: list[dict[str, str]], field: str) -> Counter:
    return Counter((row.get(field, "") or "not_recorded").strip() for row in rows)


def csv_signal(path: Path) -> str:
    rows = read_csv(path)

    if not rows:
        return "no_rows"

    if path.name == "security_evidence_corpus_manifest.csv":
        return f"records={len(rows)}"

    if path.name == "security_evidence_status_summary.csv":
        for row in rows:
            if row.get("metric", "").strip() == "overall_status":
                return f"overall_status={row.get('value', '').strip() or 'not_recorded'}"
        return f"rows={len(rows)}; overall_status=not_recorded"

    field = CSV_SIGNAL_FIELDS.get(path.name)

    if field:
        return counter_summary(count_field(rows, field))

    return f"rows={len(rows)}"


def jsonl_signal(path: Path) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return "no_rows"

    with path.open("r", encoding="utf-8") as file:
        line_count = sum(1 for line in file if line.strip())

    return f"records={line_count}"


def markdown_signal(path: Path) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return "no_signal"

    text = path.read_text(encoding="utf-8", errors="replace")

    patterns = [
        r"Overall Status:\s*\*\*([^*]+)\*\*",
        r"Adjudication Status:\s*\*\*([^*]+)\*\*",
        r"Package Status:\s*\*\*([^*]+)\*\*",
        r"Status:\s*\*\*([^*]+)\*\*",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return f"status={match.group(1).strip()}"

    heading_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    if heading_match:
        return f"title={heading_match.group(1).strip()}"

    return "no_status_found"


def current_signal(path: Path) -> str:
    status = artifact_status(path)

    if status != "Present":
        return status.lower()

    if path.suffix.lower() == ".csv":
        return csv_signal(path)

    if path.suffix.lower() == ".jsonl":
        return jsonl_signal(path)

    if path.suffix.lower() == ".md":
        return markdown_signal(path)

    return "present"


def build_traceability_rows() -> list[dict[str, str]]:
    generated_at = datetime.now(timezone.utc).isoformat()
    rows = []

    for index, item in enumerate(TRACEABILITY_ITEMS, start=1):
        path = Path(item["artifact_path"])
        status = artifact_status(path)

        if status == "Present":
            trace_status = "TRACEABLE"
        elif status == "Empty":
            trace_status = "TRACE_REVIEW_EMPTY_ARTIFACT"
        else:
            trace_status = "TRACE_REVIEW_MISSING_ARTIFACT"

        rows.append(
            {
                "trace_id": f"TRACE-{index:03d}",
                "lifecycle_stage": item["lifecycle_stage"],
                "control_question": item["control_question"],
                "artifact_path": item["artifact_path"],
                "artifact_type": item["artifact_type"],
                "artifact_status": status,
                "trace_status": trace_status,
                "machine_readable": item["machine_readable"],
                "current_signal": current_signal(path),
                "evidence_contribution": item["evidence_contribution"],
                "generated_at": generated_at,
            }
        )

    return rows


def summarize(rows: list[dict[str, str]]) -> dict[str, int]:
    return {
        "total": len(rows),
        "traceable": sum(1 for row in rows if row["trace_status"] == "TRACEABLE"),
        "missing": sum(1 for row in rows if row["artifact_status"] == "Missing"),
        "empty": sum(1 for row in rows if row["artifact_status"] == "Empty"),
        "machine_readable": sum(1 for row in rows if row["machine_readable"] == "yes"),
        "human_readable": sum(1 for row in rows if row["machine_readable"] == "no"),
    }


def determine_overall_status(summary: dict[str, int]) -> str:
    if summary["missing"] > 0:
        return "TRACEABILITY_REVIEW_REQUIRED_MISSING_ARTIFACTS"

    if summary["empty"] > 0:
        return "TRACEABILITY_REVIEW_REQUIRED_EMPTY_ARTIFACTS"

    return "TRACEABILITY_COMPLETE"


def safe_cell(value: object) -> str:
    return str(value).replace("|", " ").replace("\n", " ").strip()


def write_markdown_matrix(rows: list[dict[str, str]]) -> None:
    TRACEABILITY_MD.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    summary = summarize(rows)
    overall_status = determine_overall_status(summary)

    lines = [
        "# Security Evidence Traceability Matrix",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This matrix maps security evidence artifacts to the control questions they support.",
        "",
        "It prevents the evidence system from becoming a set of disconnected scripts and reports.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Traceability rows | `{summary['total']}` |",
        f"| Traceable artifacts | `{summary['traceable']}` |",
        f"| Missing artifacts | `{summary['missing']}` |",
        f"| Empty artifacts | `{summary['empty']}` |",
        f"| Machine-readable artifacts | `{summary['machine_readable']}` |",
        f"| Human-readable artifacts | `{summary['human_readable']}` |",
        "",
        "## Matrix",
        "",
        "| ID | Stage | Control Question | Artifact | Status | Signal |",
        "|---|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {safe_cell(row['trace_id'])} | "
            f"{safe_cell(row['lifecycle_stage'])} | "
            f"{safe_cell(row['control_question'])} | "
            f"`{safe_cell(row['artifact_path'])}` | "
            f"**{safe_cell(row['trace_status'])}** | "
            f"{safe_cell(row['current_signal'])} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `TRACEABLE` means the artifact exists and can be tied to a control question.",
            "- `TRACE_REVIEW_EMPTY_ARTIFACT` means the artifact exists but has no content.",
            "- `TRACE_REVIEW_MISSING_ARTIFACT` means the expected artifact was not found.",
            "",
            "## Governance Rule",
            "",
            "> Every important evidence artifact should answer a named control question.",
            "",
            "## One-Sentence Takeaway",
            "",
            "> Traceability turns a pile of evidence files into a defensible control story.",
            "",
        ]
    )

    TRACEABILITY_MD.write_text("\n".join(lines), encoding="utf-8")


def write_report(rows: list[dict[str, str]]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    summary = summarize(rows)
    overall_status = determine_overall_status(summary)

    lines = [
        "# Security Evidence Traceability Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report records generation of the security evidence traceability matrix.",
        "",
        "## Generated Artifacts",
        "",
        f"- `{TRACEABILITY_MATRIX.as_posix()}`",
        f"- `{TRACEABILITY_MD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Traceability Counts",
        "",
        "| Category | Count |",
        "|---|---:|",
        f"| Total rows | `{summary['total']}` |",
        f"| Traceable | `{summary['traceable']}` |",
        f"| Missing | `{summary['missing']}` |",
        f"| Empty | `{summary['empty']}` |",
        "",
        "## Control Mapping",
        "",
        "| Control Concept | Evidence Contribution |",
        "|---|---|",
        "| Traceability | Maps artifacts to specific control questions. |",
        "| Auditability | Shows which evidence exists, is missing, or is empty. |",
        "| Explainability | Describes why each artifact matters. |",
        "| Governance readiness | Separates machine-readable evidence from human-readable review artifacts. |",
        "",
        "## One-Sentence Takeaway",
        "",
        "> Traceability proves why each artifact exists and what governance question it supports.",
        "",
    ]

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_traceability_rows()

    fieldnames = [
        "trace_id",
        "lifecycle_stage",
        "control_question",
        "artifact_path",
        "artifact_type",
        "artifact_status",
        "trace_status",
        "machine_readable",
        "current_signal",
        "evidence_contribution",
        "generated_at",
    ]

    write_csv(TRACEABILITY_MATRIX, rows, fieldnames)
    write_markdown_matrix(rows)
    write_report(rows)

    summary = summarize(rows)
    overall_status = determine_overall_status(summary)

    print(f"Traceability matrix written to: {TRACEABILITY_MATRIX}")
    print(f"Traceability markdown written to: {TRACEABILITY_MD}")
    print(f"Traceability report written to: {REPORT_FILE}")
    print(f"Traceable artifacts: {summary['traceable']}")
    print(f"Missing artifacts: {summary['missing']}")
    print(f"Empty artifacts: {summary['empty']}")
    print(f"Overall Status: {overall_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())