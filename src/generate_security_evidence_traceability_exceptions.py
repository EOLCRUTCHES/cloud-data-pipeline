from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import re
import sys


TRACEABILITY_MATRIX = Path("ai/security_evidence_traceability_matrix.csv")
STATUS_SUMMARY = Path("ai/security_evidence_status_summary.csv")
ADJUDICATED_STATUS = Path("ai/security_evidence_adjudicated_gap_status.csv")
EVAL_RESULTS = Path("ai/security_evidence_eval_results.csv")
REVIEWER_DECISIONS = Path("ai/security_evidence_reviewer_decisions.csv")

EXCEPTION_REGISTER = Path("ai/security_evidence_traceability_exceptions.csv")
EXCEPTION_MD = Path("docs/cloud/security_evidence_traceability_exception_register.md")
REPORT_FILE = Path("evidence/generated/security_evidence_traceability_exception_report.md")


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


def safe_get(row: dict[str, str], field: str) -> str:
    return (row.get(field, "") or "").strip()


def safe_cell(value: object) -> str:
    return str(value).replace("|", " ").replace("\n", " ").strip()


def valid_decision_date(date_text: str) -> bool:
    if not date_text:
        return False

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_text):
        return False

    try:
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return False

    return True


def make_exception(
    exception_id: str,
    source_artifact: str,
    source_record_id: str,
    lifecycle_stage: str,
    exception_type: str,
    severity: str,
    exception_status: str,
    issue: str,
    recommended_action: str,
    owner: str,
    due_timing: str,
    generated_at: str,
) -> dict[str, str]:
    return {
        "exception_id": exception_id,
        "source_artifact": source_artifact,
        "source_record_id": source_record_id,
        "lifecycle_stage": lifecycle_stage,
        "exception_type": exception_type,
        "severity": severity,
        "exception_status": exception_status,
        "issue": issue,
        "recommended_action": recommended_action,
        "owner": owner,
        "due_timing": due_timing,
        "generated_at": generated_at,
    }


def traceability_exceptions(rows: list[dict[str, str]], generated_at: str) -> list[dict[str, str]]:
    exceptions = []

    for row in rows:
        trace_status = safe_get(row, "trace_status")
        artifact_status_value = safe_get(row, "artifact_status")
        trace_id = safe_get(row, "trace_id")
        artifact_path = safe_get(row, "artifact_path")
        lifecycle_stage = safe_get(row, "lifecycle_stage")
        control_question = safe_get(row, "control_question")

        if trace_status == "TRACE_REVIEW_MISSING_ARTIFACT" or artifact_status_value == "Missing":
            exceptions.append(
                make_exception(
                    exception_id="",
                    source_artifact=artifact_path,
                    source_record_id=trace_id,
                    lifecycle_stage=lifecycle_stage,
                    exception_type="MISSING_ARTIFACT",
                    severity="HIGH",
                    exception_status="OPEN",
                    issue=f"Expected artifact is missing for control question: {control_question}",
                    recommended_action="Regenerate the missing artifact or remove it from expected traceability if no longer required.",
                    owner="Evidence owner",
                    due_timing="Before audit or management review",
                    generated_at=generated_at,
                )
            )

        elif trace_status == "TRACE_REVIEW_EMPTY_ARTIFACT" or artifact_status_value == "Empty":
            exceptions.append(
                make_exception(
                    exception_id="",
                    source_artifact=artifact_path,
                    source_record_id=trace_id,
                    lifecycle_stage=lifecycle_stage,
                    exception_type="EMPTY_ARTIFACT",
                    severity="HIGH",
                    exception_status="OPEN",
                    issue=f"Expected artifact exists but is empty for control question: {control_question}",
                    recommended_action="Rerun the generating script and verify the artifact has content.",
                    owner="Evidence owner",
                    due_timing="Before audit or management review",
                    generated_at=generated_at,
                )
            )

    return exceptions


def evaluation_exceptions(rows: list[dict[str, str]], generated_at: str) -> list[dict[str, str]]:
    exceptions = []

    for row in rows:
        result = safe_get(row, "overall_result")
        case_id = safe_get(row, "case_id") or safe_get(row, "eval_id") or "not_recorded"
        question = safe_get(row, "question")

        if result == "FAIL":
            exceptions.append(
                make_exception(
                    exception_id="",
                    source_artifact=EVAL_RESULTS.as_posix(),
                    source_record_id=case_id,
                    lifecycle_stage="Evaluation",
                    exception_type="EVALUATION_FAILURE",
                    severity="HIGH",
                    exception_status="OPEN",
                    issue=f"Answer-layer evaluation failed for question: {question}",
                    recommended_action="Review retrieval results, answer status, expected result, and evaluation hint logic.",
                    owner="Evidence automation owner",
                    due_timing="Before relying on answer-layer output",
                    generated_at=generated_at,
                )
            )

    return exceptions


def reviewer_decision_exceptions(rows: list[dict[str, str]], generated_at: str) -> list[dict[str, str]]:
    exceptions = []

    for row in rows:
        decision = safe_get(row, "reviewer_decision")
        review_id = safe_get(row, "review_id") or "not_recorded"
        question = safe_get(row, "question")
        reviewer = safe_get(row, "reviewer")
        decision_date = safe_get(row, "decision_date")
        notes = safe_get(row, "reviewer_notes")

        if decision == "PENDING_REVIEW":
            exceptions.append(
                make_exception(
                    exception_id="",
                    source_artifact=REVIEWER_DECISIONS.as_posix(),
                    source_record_id=review_id,
                    lifecycle_stage="Human Review",
                    exception_type="PENDING_REVIEW",
                    severity="MEDIUM",
                    exception_status="OPEN",
                    issue=f"Reviewer decision is still pending for question: {question}",
                    recommended_action="Record reviewer_decision, reviewer, decision_date, and reviewer_notes when review is complete.",
                    owner="Human reviewer",
                    due_timing="At next review checkpoint",
                    generated_at=generated_at,
                )
            )

        elif decision and decision != "PENDING_REVIEW":
            missing_parts = []

            if not reviewer:
                missing_parts.append("reviewer")
            if not valid_decision_date(decision_date):
                missing_parts.append("decision_date")
            if not notes:
                missing_parts.append("reviewer_notes")

            if missing_parts:
                exceptions.append(
                    make_exception(
                        exception_id="",
                        source_artifact=REVIEWER_DECISIONS.as_posix(),
                        source_record_id=review_id,
                        lifecycle_stage="Human Review",
                        exception_type="INCOMPLETE_REVIEW_DECISION",
                        severity="HIGH",
                        exception_status="OPEN",
                        issue=f"Reviewer decision {decision} is missing required fields: {', '.join(missing_parts)}",
                        recommended_action="Complete reviewer, decision_date in YYYY-MM-DD format, and reviewer_notes.",
                        owner="Human reviewer",
                        due_timing="Before adjudication can be trusted",
                        generated_at=generated_at,
                    )
                )

    return exceptions


def adjudication_exceptions(rows: list[dict[str, str]], generated_at: str) -> list[dict[str, str]]:
    exceptions = []

    severity_by_status = {
        "OPEN": "HIGH",
        "PARTIALLY_CLOSED": "MEDIUM",
        "PENDING_HUMAN_REVIEW": "MEDIUM",
        "RETRIEVAL_TUNING_REQUIRED": "HIGH",
        "REVIEW_DECISION_INCOMPLETE": "HIGH",
        "INVALID_REVIEWER_DECISION": "HIGH",
        "REVIEW_REQUIRED": "HIGH",
    }

    action_by_status = {
        "OPEN": "Collect missing evidence or remediate the remaining risk.",
        "PARTIALLY_CLOSED": "Track residual work and define the remaining closure evidence required.",
        "PENDING_HUMAN_REVIEW": "Complete the human review decision.",
        "RETRIEVAL_TUNING_REQUIRED": "Tune retrieval logic, matching thresholds, or test case classification.",
        "REVIEW_DECISION_INCOMPLETE": "Complete reviewer, decision_date, and reviewer_notes.",
        "INVALID_REVIEWER_DECISION": "Correct reviewer_decision to an allowed value.",
        "REVIEW_REQUIRED": "Review why adjudication did not produce a final stable status.",
    }

    for row in rows:
        final_status = safe_get(row, "final_gap_status")
        adjudication_id = safe_get(row, "adjudication_id") or "not_recorded"
        question = safe_get(row, "question")

        if final_status in severity_by_status:
            exceptions.append(
                make_exception(
                    exception_id="",
                    source_artifact=ADJUDICATED_STATUS.as_posix(),
                    source_record_id=adjudication_id,
                    lifecycle_stage="Adjudication",
                    exception_type=final_status,
                    severity=severity_by_status[final_status],
                    exception_status="OPEN",
                    issue=f"Adjudicated gap status requires attention: {final_status}. Question: {question}",
                    recommended_action=action_by_status[final_status],
                    owner="Evidence owner",
                    due_timing="At next evidence review checkpoint",
                    generated_at=generated_at,
                )
            )

    return exceptions


def status_summary_exceptions(rows: list[dict[str, str]], generated_at: str) -> list[dict[str, str]]:
    exceptions = []

    overall_status = ""

    for row in rows:
        if safe_get(row, "metric") == "overall_status":
            overall_status = safe_get(row, "value")
            break

    if overall_status and overall_status != "EVIDENCE_SYSTEM_STABLE":
        exceptions.append(
            make_exception(
                exception_id="",
                source_artifact=STATUS_SUMMARY.as_posix(),
                source_record_id="overall_status",
                lifecycle_stage="Status Dashboard",
                exception_type="NON_STABLE_OVERALL_STATUS",
                severity="MEDIUM",
                exception_status="OPEN",
                issue=f"Dashboard overall status is {overall_status}.",
                recommended_action="Review detailed exceptions and clear open, pending, invalid, incomplete, or failed items.",
                owner="Evidence owner",
                due_timing="At next management review",
                generated_at=generated_at,
            )
        )

    return exceptions


def assign_exception_ids(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    for index, row in enumerate(rows, start=1):
        row["exception_id"] = f"EXC-{index:03d}"

    return rows


def build_exception_rows() -> list[dict[str, str]]:
    generated_at = datetime.now(timezone.utc).isoformat()

    traceability_rows = read_csv(TRACEABILITY_MATRIX)
    status_rows = read_csv(STATUS_SUMMARY)
    adjudicated_rows = read_csv(ADJUDICATED_STATUS)
    eval_rows = read_csv(EVAL_RESULTS)
    review_rows = read_csv(REVIEWER_DECISIONS)

    exceptions = []
    exceptions.extend(traceability_exceptions(traceability_rows, generated_at))
    exceptions.extend(evaluation_exceptions(eval_rows, generated_at))
    exceptions.extend(reviewer_decision_exceptions(review_rows, generated_at))
    exceptions.extend(adjudication_exceptions(adjudicated_rows, generated_at))
    exceptions.extend(status_summary_exceptions(status_rows, generated_at))

    if not exceptions:
        exceptions.append(
            make_exception(
                exception_id="",
                source_artifact="multiple",
                source_record_id="none",
                lifecycle_stage="Overall",
                exception_type="NO_OPEN_EXCEPTIONS",
                severity="INFO",
                exception_status="CLOSED",
                issue="No open traceability, evaluation, review, adjudication, or dashboard exceptions were detected.",
                recommended_action="Continue routine monitoring and expand evidence coverage as new use cases are added.",
                owner="Evidence owner",
                due_timing="Routine review",
                generated_at=generated_at,
            )
        )

    return assign_exception_ids(exceptions)


def count_field(rows: list[dict[str, str]], field: str) -> Counter:
    return Counter(safe_get(row, field) or "not_recorded" for row in rows)


def determine_overall_status(rows: list[dict[str, str]]) -> str:
    open_rows = [
        row for row in rows
        if safe_get(row, "exception_status") == "OPEN"
    ]

    if not open_rows:
        return "NO_OPEN_EXCEPTIONS"

    severity_counts = count_field(open_rows, "severity")

    if severity_counts.get("HIGH", 0) > 0:
        return "EXCEPTIONS_OPEN_HIGH"

    if severity_counts.get("MEDIUM", 0) > 0:
        return "EXCEPTIONS_OPEN_MEDIUM"

    return "EXCEPTIONS_OPEN_LOW"


def write_markdown_register(rows: list[dict[str, str]]) -> None:
    EXCEPTION_MD.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    overall_status = determine_overall_status(rows)
    severity_counts = count_field(rows, "severity")
    type_counts = count_field(rows, "exception_type")
    open_count = sum(1 for row in rows if safe_get(row, "exception_status") == "OPEN")

    lines = [
        "# Security Evidence Traceability Exception Register",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This register identifies evidence-system items that need review before the system is treated as audit-ready.",
        "",
        "It converts traceability, evaluation, reviewer decision, adjudication, and dashboard signals into actionable exceptions.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Total exceptions | `{len(rows)}` |",
        f"| Open exceptions | `{open_count}` |",
        f"| High severity | `{severity_counts.get('HIGH', 0)}` |",
        f"| Medium severity | `{severity_counts.get('MEDIUM', 0)}` |",
        f"| Low severity | `{severity_counts.get('LOW', 0)}` |",
        f"| Info | `{severity_counts.get('INFO', 0)}` |",
        "",
        "## Exception Type Counts",
        "",
        "| Exception Type | Count |",
        "|---|---:|",
    ]

    for exception_type, count in sorted(type_counts.items()):
        lines.append(f"| `{safe_cell(exception_type)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Open Exceptions",
            "",
            "| ID | Severity | Stage | Type | Issue | Recommended Action |",
            "|---|---|---|---|---|---|",
        ]
    )

    open_rows = [row for row in rows if safe_get(row, "exception_status") == "OPEN"]

    if open_rows:
        for row in open_rows:
            lines.append(
                f"| {safe_cell(row['exception_id'])} | "
                f"**{safe_cell(row['severity'])}** | "
                f"{safe_cell(row['lifecycle_stage'])} | "
                f"`{safe_cell(row['exception_type'])}` | "
                f"{safe_cell(row['issue'])} | "
                f"{safe_cell(row['recommended_action'])} |"
            )
    else:
        lines.append("| `none` | `INFO` | Overall | `NO_OPEN_EXCEPTIONS` | No open exceptions detected. | Continue routine monitoring. |")

    lines.extend(
        [
            "",
            "## Source Artifacts Checked",
            "",
            "| Artifact | Status |",
            "|---|---|",
            f"| `{TRACEABILITY_MATRIX.as_posix()}` | {artifact_status(TRACEABILITY_MATRIX)} |",
            f"| `{STATUS_SUMMARY.as_posix()}` | {artifact_status(STATUS_SUMMARY)} |",
            f"| `{ADJUDICATED_STATUS.as_posix()}` | {artifact_status(ADJUDICATED_STATUS)} |",
            f"| `{EVAL_RESULTS.as_posix()}` | {artifact_status(EVAL_RESULTS)} |",
            f"| `{REVIEWER_DECISIONS.as_posix()}` | {artifact_status(REVIEWER_DECISIONS)} |",
            "",
            "## Governance Rule",
            "",
            "> A dashboard shows posture; an exception register shows what must be fixed, accepted, or reviewed.",
            "",
            "## One-Sentence Takeaway",
            "",
            "> Exception management turns evidence-system problems into visible, owned follow-up work.",
            "",
        ]
    )

    EXCEPTION_MD.write_text("\n".join(lines), encoding="utf-8")


def write_report(rows: list[dict[str, str]]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    overall_status = determine_overall_status(rows)
    severity_counts = count_field(rows, "severity")
    open_count = sum(1 for row in rows if safe_get(row, "exception_status") == "OPEN")

    lines = [
        "# Security Evidence Traceability Exception Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report records generation of the security evidence traceability exception register.",
        "",
        "## Generated Artifacts",
        "",
        f"- `{EXCEPTION_REGISTER.as_posix()}`",
        f"- `{EXCEPTION_MD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Exception Counts",
        "",
        "| Category | Count |",
        "|---|---:|",
        f"| Total rows | `{len(rows)}` |",
        f"| Open rows | `{open_count}` |",
        f"| High severity | `{severity_counts.get('HIGH', 0)}` |",
        f"| Medium severity | `{severity_counts.get('MEDIUM', 0)}` |",
        f"| Low severity | `{severity_counts.get('LOW', 0)}` |",
        f"| Info | `{severity_counts.get('INFO', 0)}` |",
        "",
        "## Control Mapping",
        "",
        "| Control Concept | Evidence Contribution |",
        "|---|---|",
        "| Exception management | Converts review-required signals into actionable rows. |",
        "| Audit readiness | Identifies missing, empty, failed, pending, open, or incomplete evidence states. |",
        "| Ownership | Assigns owner categories and due timing to each exception. |",
        "| Management review | Produces a human-readable register and machine-readable CSV. |",
        "",
        "## One-Sentence Takeaway",
        "",
        "> Evidence systems become manageable when exceptions are visible, categorized, owned, and reviewed.",
        "",
    ]

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_exception_rows()

    fieldnames = [
        "exception_id",
        "source_artifact",
        "source_record_id",
        "lifecycle_stage",
        "exception_type",
        "severity",
        "exception_status",
        "issue",
        "recommended_action",
        "owner",
        "due_timing",
        "generated_at",
    ]

    write_csv(EXCEPTION_REGISTER, rows, fieldnames)
    write_markdown_register(rows)
    write_report(rows)

    overall_status = determine_overall_status(rows)
    severity_counts = count_field(rows, "severity")
    open_count = sum(1 for row in rows if safe_get(row, "exception_status") == "OPEN")

    print(f"Exception register written to: {EXCEPTION_REGISTER}")
    print(f"Exception markdown written to: {EXCEPTION_MD}")
    print(f"Exception report written to: {REPORT_FILE}")
    print(f"Open exceptions: {open_count}")
    print(f"High severity: {severity_counts.get('HIGH', 0)}")
    print(f"Medium severity: {severity_counts.get('MEDIUM', 0)}")
    print(f"Overall Status: {overall_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())