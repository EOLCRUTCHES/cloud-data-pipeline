from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import sys


ACTION_PLAN = Path("ai/security_evidence_exception_action_plan.csv")

REVIEW_STATUS = Path("ai/security_evidence_exception_review_status.csv")
REVIEW_PACKET_MD = Path("docs/cloud/security_evidence_exception_review_packet.md")
REPORT_FILE = Path("evidence/generated/security_evidence_exception_review_report.md")


ALLOWED_ACTION_STATUSES = {
    "NOT_STARTED",
    "IN_PROGRESS",
    "BLOCKED",
    "ACCEPTED_RISK",
    "RESOLVED",
    "DEFERRED",
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


def safe_get(row: dict[str, str], field: str) -> str:
    return (row.get(field, "") or "").strip()


def safe_cell(value: object) -> str:
    return str(value).replace("|", " ").replace("\n", " ").strip()


def parse_target_date(date_text: str):
    if not date_text:
        return None

    try:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        return "INVALID"


def days_until_target(date_text: str, today) -> str:
    parsed = parse_target_date(date_text)

    if parsed is None:
        return "not_recorded"

    if parsed == "INVALID":
        return "invalid_date"

    return str((parsed - today).days)


def review_status_for_row(row: dict[str, str], today) -> str:
    action_status = safe_get(row, "action_status").upper()
    priority = safe_get(row, "priority")
    target_date = safe_get(row, "target_date")
    action_notes = safe_get(row, "action_notes")
    resolution_evidence = safe_get(row, "resolution_evidence")

    parsed_target = parse_target_date(target_date)

    if action_status not in ALLOWED_ACTION_STATUSES:
        return "INVALID_ACTION_STATUS"

    if parsed_target == "INVALID":
        return "INVALID_TARGET_DATE"

    if action_status == "RESOLVED":
        if resolution_evidence:
            return "RESOLVED_WITH_EVIDENCE"
        return "RESOLVED_EVIDENCE_NEEDED"

    if action_status == "ACCEPTED_RISK":
        if action_notes:
            return "ACCEPTED_RISK_REVIEW"
        return "ACCEPTED_RISK_RATIONALE_NEEDED"

    if action_status == "DEFERRED":
        if action_notes or target_date:
            return "DEFERRED_REVIEW"
        return "DEFERRED_RATIONALE_NEEDED"

    if action_status == "BLOCKED":
        return "BLOCKED_MANAGEMENT_REVIEW"

    if parsed_target is not None and parsed_target < today:
        return f"OVERDUE_{action_status}"

    if action_status == "IN_PROGRESS":
        if not target_date:
            return "IN_PROGRESS_NO_TARGET_DATE"
        return "IN_PROGRESS_ON_TRACK"

    if action_status == "NOT_STARTED":
        if priority == "P1":
            return "P1_NOT_STARTED"
        if not target_date:
            return "NOT_STARTED_NO_TARGET_DATE"
        return "NOT_STARTED_SCHEDULED"

    return "ACTION_REVIEW_REQUIRED"


def recommendation_for_status(review_status: str) -> str:
    recommendations = {
        "INVALID_ACTION_STATUS": "Correct action_status to an allowed value.",
        "INVALID_TARGET_DATE": "Correct target_date to YYYY-MM-DD format or leave it blank.",
        "RESOLVED_WITH_EVIDENCE": "Review resolution evidence and retain the action record.",
        "RESOLVED_EVIDENCE_NEEDED": "Add resolution_evidence before treating the action as fully closed.",
        "ACCEPTED_RISK_REVIEW": "Confirm the risk acceptance rationale remains valid.",
        "ACCEPTED_RISK_RATIONALE_NEEDED": "Add action_notes explaining the accepted risk rationale.",
        "DEFERRED_REVIEW": "Confirm the deferral rationale and revisit timing.",
        "DEFERRED_RATIONALE_NEEDED": "Add action_notes or target_date explaining why this is deferred.",
        "BLOCKED_MANAGEMENT_REVIEW": "Escalate the blocker or decide whether to accept, defer, or reassign the action.",
        "IN_PROGRESS_NO_TARGET_DATE": "Add a target_date or review checkpoint.",
        "IN_PROGRESS_ON_TRACK": "Continue current action and review at the next checkpoint.",
        "P1_NOT_STARTED": "Start or reassign this P1 action immediately.",
        "NOT_STARTED_NO_TARGET_DATE": "Assign a target_date or explicitly defer/accept the action.",
        "NOT_STARTED_SCHEDULED": "Confirm the scheduled work remains appropriate.",
        "ACTION_REVIEW_REQUIRED": "Review the action row manually.",
    }

    if review_status.startswith("OVERDUE_"):
        return "Review overdue action, update target_date, escalate blocker, or reassign ownership."

    return recommendations.get(review_status, "Review manually.")


def management_attention_required(review_status: str) -> str:
    attention_statuses = {
        "INVALID_ACTION_STATUS",
        "INVALID_TARGET_DATE",
        "RESOLVED_EVIDENCE_NEEDED",
        "ACCEPTED_RISK_RATIONALE_NEEDED",
        "DEFERRED_RATIONALE_NEEDED",
        "BLOCKED_MANAGEMENT_REVIEW",
        "IN_PROGRESS_NO_TARGET_DATE",
        "P1_NOT_STARTED",
        "NOT_STARTED_NO_TARGET_DATE",
        "ACTION_REVIEW_REQUIRED",
    }

    if review_status.startswith("OVERDUE_"):
        return "yes"

    if review_status in attention_statuses:
        return "yes"

    return "no"


def build_review_rows() -> list[dict[str, str]]:
    generated_at = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).date()

    action_rows = read_csv(ACTION_PLAN)

    if not action_rows:
        action_rows = [
            {
                "action_id": "ACT-000",
                "stable_exception_key": "",
                "exception_id": "",
                "source_artifact": ACTION_PLAN.as_posix(),
                "source_record_id": "not_available",
                "lifecycle_stage": "Exception Action Planning",
                "exception_type": "NO_ACTION_PLAN",
                "severity": "HIGH",
                "priority": "P1",
                "exception_status": "OPEN",
                "issue": "Exception action plan is missing or empty.",
                "planned_next_step": "Run src/generate_security_evidence_exception_action_plan.py.",
                "assigned_owner": "Evidence owner",
                "target_timing": "Before management review",
                "target_date": "",
                "action_status": "NOT_STARTED",
                "action_notes": "",
                "resolution_evidence": "",
                "generated_at": generated_at,
            }
        ]

    review_rows = []

    for index, row in enumerate(action_rows, start=1):
        review_status = review_status_for_row(row, today)

        review_rows.append(
            {
                "review_id": f"REV-{index:03d}",
                "action_id": safe_get(row, "action_id"),
                "stable_exception_key": safe_get(row, "stable_exception_key"),
                "exception_id": safe_get(row, "exception_id"),
                "priority": safe_get(row, "priority"),
                "severity": safe_get(row, "severity"),
                "lifecycle_stage": safe_get(row, "lifecycle_stage"),
                "exception_type": safe_get(row, "exception_type"),
                "assigned_owner": safe_get(row, "assigned_owner"),
                "action_status": safe_get(row, "action_status").upper(),
                "target_date": safe_get(row, "target_date"),
                "days_until_target": days_until_target(safe_get(row, "target_date"), today),
                "review_status": review_status,
                "management_attention_required": management_attention_required(review_status),
                "issue": safe_get(row, "issue"),
                "planned_next_step": safe_get(row, "planned_next_step"),
                "action_notes": safe_get(row, "action_notes"),
                "resolution_evidence": safe_get(row, "resolution_evidence"),
                "review_recommendation": recommendation_for_status(review_status),
                "generated_at": generated_at,
            }
        )

    return review_rows


def count_field(rows: list[dict[str, str]], field: str) -> Counter:
    return Counter(safe_get(row, field) or "not_recorded" for row in rows)


def determine_overall_status(rows: list[dict[str, str]]) -> str:
    review_counts = count_field(rows, "review_status")
    attention_count = sum(
        1 for row in rows
        if safe_get(row, "management_attention_required") == "yes"
    )

    if review_counts.get("INVALID_ACTION_STATUS", 0) > 0:
        return "REVIEW_REQUIRED_INVALID_ACTION_STATUS"

    if review_counts.get("INVALID_TARGET_DATE", 0) > 0:
        return "REVIEW_REQUIRED_INVALID_TARGET_DATE"

    if review_counts.get("P1_NOT_STARTED", 0) > 0:
        return "MANAGEMENT_REVIEW_REQUIRED_P1_NOT_STARTED"

    overdue_count = sum(
        count for status, count in review_counts.items()
        if status.startswith("OVERDUE_")
    )

    if overdue_count > 0:
        return "MANAGEMENT_REVIEW_REQUIRED_OVERDUE_ACTIONS"

    if review_counts.get("BLOCKED_MANAGEMENT_REVIEW", 0) > 0:
        return "MANAGEMENT_REVIEW_REQUIRED_BLOCKED_ACTIONS"

    if attention_count > 0:
        return "MANAGEMENT_REVIEW_REQUIRED"

    active_count = sum(
        1 for row in rows
        if safe_get(row, "action_status") in {"NOT_STARTED", "IN_PROGRESS", "BLOCKED"}
    )

    if active_count > 0:
        return "ACTIVE_ACTIONS_TRACKED"

    return "NO_ACTIVE_ACTIONS_REQUIRING_REVIEW"


def write_markdown_packet(rows: list[dict[str, str]]) -> None:
    REVIEW_PACKET_MD.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).date().isoformat()
    overall_status = determine_overall_status(rows)
    review_counts = count_field(rows, "review_status")
    action_status_counts = count_field(rows, "action_status")
    attention_rows = [
        row for row in rows
        if safe_get(row, "management_attention_required") == "yes"
    ]

    lines = [
        "# Security Evidence Exception Review Packet",
        "",
        f"Generated: `{timestamp}`",
        f"Review Date: `{today}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This packet summarizes exception actions requiring management review, escalation, correction, evidence, or routine tracking.",
        "",
        "## Executive Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Total reviewed actions | `{len(rows)}` |",
        f"| Management attention required | `{len(attention_rows)}` |",
        f"| P1 not started | `{review_counts.get('P1_NOT_STARTED', 0)}` |",
        f"| Blocked actions | `{review_counts.get('BLOCKED_MANAGEMENT_REVIEW', 0)}` |",
        f"| Invalid action statuses | `{review_counts.get('INVALID_ACTION_STATUS', 0)}` |",
        f"| Invalid target dates | `{review_counts.get('INVALID_TARGET_DATE', 0)}` |",
        "",
        "## Action Status Counts",
        "",
        "| Action Status | Count |",
        "|---|---:|",
    ]

    for status, count in sorted(action_status_counts.items()):
        lines.append(f"| `{safe_cell(status)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Review Status Counts",
            "",
            "| Review Status | Count |",
            "|---|---:|",
        ]
    )

    for status, count in sorted(review_counts.items()):
        lines.append(f"| `{safe_cell(status)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Items Requiring Management Attention",
            "",
            "| Review | Priority | Owner | Status | Issue | Recommendation |",
            "|---|---|---|---|---|---|",
        ]
    )

    if attention_rows:
        for row in attention_rows:
            lines.append(
                f"| {safe_cell(row['review_id'])} | "
                f"**{safe_cell(row['priority'])}** | "
                f"{safe_cell(row['assigned_owner'])} | "
                f"`{safe_cell(row['review_status'])}` | "
                f"{safe_cell(row['issue'])} | "
                f"{safe_cell(row['review_recommendation'])} |"
            )
    else:
        lines.append(
            "| `none` | `P4` | Evidence owner | `NO_ATTENTION_REQUIRED` | "
            "No actions require management attention. | Continue routine monitoring. |"
        )

    lines.extend(
        [
            "",
            "## Full Review Table",
            "",
            "| Review | Action | Priority | Owner | Action Status | Review Status | Target Date | Days |",
            "|---|---|---|---|---|---|---|---:|",
        ]
    )

    for row in rows:
        lines.append(
            f"| {safe_cell(row['review_id'])} | "
            f"{safe_cell(row['action_id'])} | "
            f"**{safe_cell(row['priority'])}** | "
            f"{safe_cell(row['assigned_owner'])} | "
            f"`{safe_cell(row['action_status'])}` | "
            f"`{safe_cell(row['review_status'])}` | "
            f"{safe_cell(row['target_date'] or 'not_recorded')} | "
            f"{safe_cell(row['days_until_target'])} |"
        )

    lines.extend(
        [
            "",
            "## Governance Rule",
            "",
            "> Action plans are only useful when leadership can see what is blocked, overdue, unresolved, accepted, deferred, or ready for routine monitoring.",
            "",
            "## One-Sentence Takeaway",
            "",
            "> The exception review packet turns managed work into a leadership-ready review artifact.",
            "",
        ]
    )

    REVIEW_PACKET_MD.write_text("\n".join(lines), encoding="utf-8")


def write_report(rows: list[dict[str, str]]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    overall_status = determine_overall_status(rows)
    review_counts = count_field(rows, "review_status")
    attention_count = sum(
        1 for row in rows
        if safe_get(row, "management_attention_required") == "yes"
    )

    lines = [
        "# Security Evidence Exception Review Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report records generation of the security evidence exception review packet.",
        "",
        "## Input Artifact",
        "",
        "| Artifact | Status |",
        "|---|---|",
        f"| `{ACTION_PLAN.as_posix()}` | {artifact_status(ACTION_PLAN)} |",
        "",
        "## Generated Artifacts",
        "",
        f"- `{REVIEW_STATUS.as_posix()}`",
        f"- `{REVIEW_PACKET_MD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Review Counts",
        "",
        "| Category | Count |",
        "|---|---:|",
        f"| Reviewed actions | `{len(rows)}` |",
        f"| Management attention required | `{attention_count}` |",
    ]

    for status, count in sorted(review_counts.items()):
        lines.append(f"| `{safe_cell(status)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Control Mapping",
            "",
            "| Control Concept | Evidence Contribution |",
            "|---|---|",
            "| Management review | Summarizes exception actions needing leadership attention. |",
            "| Action tracking | Separates not started, in progress, blocked, resolved, deferred, and accepted-risk work. |",
            "| Closure discipline | Flags resolved actions that lack resolution evidence. |",
            "| Risk acceptance discipline | Flags accepted-risk actions that lack rationale. |",
            "| Schedule discipline | Flags invalid, missing, or overdue target dates. |",
            "",
            "## One-Sentence Takeaway",
            "",
            "> Exception review turns an action plan into a management-ready control artifact.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_review_rows()

    fieldnames = [
        "review_id",
        "action_id",
        "stable_exception_key",
        "exception_id",
        "priority",
        "severity",
        "lifecycle_stage",
        "exception_type",
        "assigned_owner",
        "action_status",
        "target_date",
        "days_until_target",
        "review_status",
        "management_attention_required",
        "issue",
        "planned_next_step",
        "action_notes",
        "resolution_evidence",
        "review_recommendation",
        "generated_at",
    ]

    write_csv(REVIEW_STATUS, rows, fieldnames)
    write_markdown_packet(rows)
    write_report(rows)

    overall_status = determine_overall_status(rows)
    attention_count = sum(
        1 for row in rows
        if safe_get(row, "management_attention_required") == "yes"
    )

    review_counts = count_field(rows, "review_status")

    print(f"Exception review status written to: {REVIEW_STATUS}")
    print(f"Exception review packet written to: {REVIEW_PACKET_MD}")
    print(f"Exception review report written to: {REPORT_FILE}")
    print(f"Reviewed actions: {len(rows)}")
    print(f"Management attention required: {attention_count}")
    print(f"P1 not started: {review_counts.get('P1_NOT_STARTED', 0)}")
    print(f"Blocked actions: {review_counts.get('BLOCKED_MANAGEMENT_REVIEW', 0)}")
    print(f"Overall Status: {overall_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())