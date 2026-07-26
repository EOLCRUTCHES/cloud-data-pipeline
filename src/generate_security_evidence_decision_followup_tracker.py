from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import re
import sys


DECISIONS_CSV = Path("ai/security_evidence_exception_management_decisions.csv")

FOLLOWUP_TRACKER = Path("ai/security_evidence_decision_followup_tracker.csv")
FOLLOWUP_MD = Path("docs/cloud/security_evidence_decision_followup_tracker.md")
REPORT_FILE = Path("evidence/generated/security_evidence_decision_followup_report.md")


ALLOWED_FOLLOWUP_STATUSES = {
    "NOT_APPLICABLE",
    "NOT_STARTED",
    "IN_PROGRESS",
    "BLOCKED",
    "COMPLETED",
    "CANCELLED",
}


MANUAL_FIELDS = [
    "followup_status",
    "followup_notes",
    "completion_date",
    "completion_evidence",
]


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


def valid_date(date_text: str) -> bool:
    if not date_text:
        return False

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_text):
        return False

    try:
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return False

    return True


def parse_date(date_text: str):
    if not date_text:
        return None

    if not valid_date(date_text):
        return "INVALID"

    return datetime.strptime(date_text, "%Y-%m-%d").date()


def days_until(date_text: str, today) -> str:
    parsed = parse_date(date_text)

    if parsed is None:
        return "not_recorded"

    if parsed == "INVALID":
        return "invalid_date"

    return str((parsed - today).days)


def existing_manual_values() -> dict[str, dict[str, str]]:
    existing_rows = read_csv(FOLLOWUP_TRACKER)
    existing_by_key = {}

    for row in existing_rows:
        stable_key = safe_get(row, "stable_exception_key")
        decision_id = safe_get(row, "decision_id")

        key = stable_key or decision_id

        if not key:
            continue

        existing_by_key[key] = {
            field: safe_get(row, field)
            for field in MANUAL_FIELDS
        }

    return existing_by_key


def default_followup_status(row: dict[str, str]) -> str:
    followup_required = safe_get(row, "followup_required").lower()
    completeness = safe_get(row, "decision_completeness_status")

    if completeness != "DECISION_COMPLETE":
        return "NOT_STARTED"

    if followup_required == "no":
        return "NOT_APPLICABLE"

    if followup_required == "yes":
        return "NOT_STARTED"

    return "NOT_STARTED"


def normalize_followup_status(value: str, default: str) -> str:
    normalized = (value or "").strip().upper()

    if normalized in ALLOWED_FOLLOWUP_STATUSES:
        return normalized

    return default


def tracker_status_for_row(row: dict[str, str], today) -> str:
    decision_completeness = safe_get(row, "decision_completeness_status")
    followup_required = safe_get(row, "followup_required").lower()
    followup_date = safe_get(row, "followup_date")
    followup_owner = safe_get(row, "followup_owner")
    followup_status = safe_get(row, "followup_status").upper()
    completion_date = safe_get(row, "completion_date")
    completion_evidence = safe_get(row, "completion_evidence")

    if decision_completeness != "DECISION_COMPLETE":
        return "DECISION_RECORD_INCOMPLETE"

    if followup_required not in {"yes", "no"}:
        return "FOLLOWUP_REQUIREMENT_INVALID"

    if followup_status not in ALLOWED_FOLLOWUP_STATUSES:
        return "INVALID_FOLLOWUP_STATUS"

    if followup_required == "no":
        if followup_status == "NOT_APPLICABLE":
            return "NO_FOLLOWUP_REQUIRED"
        return "NO_FOLLOWUP_REQUIRED_STATUS_REVIEW"

    if not followup_owner:
        return "FOLLOWUP_OWNER_MISSING"

    parsed_followup_date = parse_date(followup_date)

    if parsed_followup_date is None:
        return "FOLLOWUP_DATE_MISSING"

    if parsed_followup_date == "INVALID":
        return "INVALID_FOLLOWUP_DATE"

    if followup_status == "COMPLETED":
        if completion_date and not valid_date(completion_date):
            return "INVALID_COMPLETION_DATE"

        if not completion_date:
            return "COMPLETED_DATE_NEEDED"

        if not completion_evidence:
            return "COMPLETED_EVIDENCE_NEEDED"

        return "FOLLOWUP_COMPLETED"

    if followup_status == "CANCELLED":
        if not safe_get(row, "followup_notes"):
            return "CANCELLED_RATIONALE_NEEDED"
        return "FOLLOWUP_CANCELLED"

    if followup_status == "BLOCKED":
        return "FOLLOWUP_BLOCKED"

    if parsed_followup_date < today:
        return f"FOLLOWUP_OVERDUE_{followup_status}"

    if followup_status == "IN_PROGRESS":
        return "FOLLOWUP_IN_PROGRESS"

    if followup_status == "NOT_STARTED":
        return "FOLLOWUP_NOT_STARTED"

    return "FOLLOWUP_REVIEW_REQUIRED"


def recommendation_for_tracker_status(status: str) -> str:
    recommendations = {
        "DECISION_RECORD_INCOMPLETE": "Complete the management decision record before relying on follow-up tracking.",
        "FOLLOWUP_REQUIREMENT_INVALID": "Set followup_required to yes or no in the management decision log.",
        "INVALID_FOLLOWUP_STATUS": "Correct followup_status to an allowed value.",
        "NO_FOLLOWUP_REQUIRED": "No follow-up action required; retain decision record.",
        "NO_FOLLOWUP_REQUIRED_STATUS_REVIEW": "Use NOT_APPLICABLE when followup_required is no.",
        "FOLLOWUP_OWNER_MISSING": "Add followup_owner in the management decision log.",
        "FOLLOWUP_DATE_MISSING": "Add followup_date in YYYY-MM-DD format.",
        "INVALID_FOLLOWUP_DATE": "Correct followup_date to YYYY-MM-DD format.",
        "INVALID_COMPLETION_DATE": "Correct completion_date to YYYY-MM-DD format.",
        "COMPLETED_DATE_NEEDED": "Add completion_date before treating follow-up as complete.",
        "COMPLETED_EVIDENCE_NEEDED": "Add completion_evidence before treating follow-up as fully supported.",
        "FOLLOWUP_COMPLETED": "Retain completion evidence and continue routine review.",
        "CANCELLED_RATIONALE_NEEDED": "Add followup_notes explaining why the follow-up was cancelled.",
        "FOLLOWUP_CANCELLED": "Retain cancellation rationale and review if risk changes.",
        "FOLLOWUP_BLOCKED": "Escalate blocker, reassign owner, defer, or accept risk.",
        "FOLLOWUP_IN_PROGRESS": "Continue action and review at the next checkpoint.",
        "FOLLOWUP_NOT_STARTED": "Start follow-up or reassign ownership before the due date.",
        "FOLLOWUP_REVIEW_REQUIRED": "Review the follow-up row manually.",
    }

    if status.startswith("FOLLOWUP_OVERDUE_"):
        return "Review overdue follow-up, update status, escalate blocker, or reassign ownership."

    return recommendations.get(status, "Review manually.")


def management_attention_required(status: str) -> str:
    no_attention_statuses = {
        "NO_FOLLOWUP_REQUIRED",
        "FOLLOWUP_COMPLETED",
        "FOLLOWUP_CANCELLED",
        "FOLLOWUP_IN_PROGRESS",
        "FOLLOWUP_NOT_STARTED",
    }

    if status in no_attention_statuses:
        return "no"

    return "yes"


def build_followup_rows() -> list[dict[str, str]]:
    generated_at = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).date()

    decision_rows = read_csv(DECISIONS_CSV)
    existing_by_key = existing_manual_values()

    if not decision_rows:
        decision_rows = [
            {
                "decision_id": "MGMT-DEC-000",
                "review_id": "",
                "action_id": "",
                "stable_exception_key": "NO_MANAGEMENT_DECISIONS",
                "exception_id": "",
                "priority": "P1",
                "severity": "HIGH",
                "lifecycle_stage": "Management Decision",
                "exception_type": "NO_MANAGEMENT_DECISIONS",
                "assigned_owner": "Evidence owner",
                "action_status": "NOT_STARTED",
                "review_status": "NO_MANAGEMENT_DECISIONS",
                "management_attention_required": "yes",
                "issue": "Management decision log is missing or empty.",
                "review_recommendation": "Run src/generate_security_evidence_exception_management_decisions.py.",
                "recommended_management_decision": "PENDING_DECISION",
                "management_decision": "PENDING_DECISION",
                "decision_owner": "",
                "decision_date": "",
                "decision_notes": "",
                "followup_required": "yes",
                "followup_date": "",
                "followup_owner": "Evidence owner",
                "decision_completeness_status": "PENDING_MANAGEMENT_DECISION",
                "generated_at": generated_at,
            }
        ]

    followup_rows = []

    for index, decision in enumerate(decision_rows, start=1):
        stable_key = safe_get(decision, "stable_exception_key") or safe_get(decision, "decision_id")
        manual = existing_by_key.get(stable_key, {})

        default_status = default_followup_status(decision)

        followup_status = normalize_followup_status(
            manual.get("followup_status", ""),
            default_status,
        )

        row = {
            "followup_id": f"FUP-{index:03d}",
            "decision_id": safe_get(decision, "decision_id"),
            "review_id": safe_get(decision, "review_id"),
            "action_id": safe_get(decision, "action_id"),
            "stable_exception_key": stable_key,
            "exception_id": safe_get(decision, "exception_id"),
            "priority": safe_get(decision, "priority"),
            "severity": safe_get(decision, "severity"),
            "lifecycle_stage": safe_get(decision, "lifecycle_stage"),
            "exception_type": safe_get(decision, "exception_type"),
            "issue": safe_get(decision, "issue"),
            "management_decision": safe_get(decision, "management_decision"),
            "decision_owner": safe_get(decision, "decision_owner"),
            "decision_date": safe_get(decision, "decision_date"),
            "decision_completeness_status": safe_get(decision, "decision_completeness_status"),
            "followup_required": safe_get(decision, "followup_required"),
            "followup_owner": safe_get(decision, "followup_owner"),
            "followup_date": safe_get(decision, "followup_date"),
            "days_until_followup": days_until(safe_get(decision, "followup_date"), today),
            "followup_status": followup_status,
            "followup_notes": manual.get("followup_notes", ""),
            "completion_date": manual.get("completion_date", ""),
            "completion_evidence": manual.get("completion_evidence", ""),
            "generated_at": generated_at,
        }

        tracker_status = tracker_status_for_row(row, today)

        row["tracker_status"] = tracker_status
        row["management_attention_required"] = management_attention_required(tracker_status)
        row["recommended_next_step"] = recommendation_for_tracker_status(tracker_status)

        followup_rows.append(row)

    return followup_rows


def count_field(rows: list[dict[str, str]], field: str) -> Counter:
    return Counter(safe_get(row, field) or "not_recorded" for row in rows)


def determine_overall_status(rows: list[dict[str, str]]) -> str:
    tracker_counts = count_field(rows, "tracker_status")
    attention_count = sum(
        1 for row in rows
        if safe_get(row, "management_attention_required") == "yes"
    )

    overdue_count = sum(
        count for status, count in tracker_counts.items()
        if status.startswith("FOLLOWUP_OVERDUE_")
    )

    if tracker_counts.get("DECISION_RECORD_INCOMPLETE", 0) > 0:
        return "REVIEW_REQUIRED_INCOMPLETE_DECISIONS"

    if overdue_count > 0:
        return "REVIEW_REQUIRED_OVERDUE_FOLLOWUPS"

    if tracker_counts.get("FOLLOWUP_BLOCKED", 0) > 0:
        return "REVIEW_REQUIRED_BLOCKED_FOLLOWUPS"

    if tracker_counts.get("COMPLETED_EVIDENCE_NEEDED", 0) > 0:
        return "REVIEW_REQUIRED_COMPLETION_EVIDENCE"

    if attention_count > 0:
        return "FOLLOWUP_REVIEW_REQUIRED"

    active_count = (
        tracker_counts.get("FOLLOWUP_IN_PROGRESS", 0)
        + tracker_counts.get("FOLLOWUP_NOT_STARTED", 0)
    )

    if active_count > 0:
        return "FOLLOWUPS_ACTIVE"

    return "FOLLOWUPS_STABLE"


def safe_status_count(counter: Counter, prefix: str) -> int:
    return sum(count for status, count in counter.items() if status.startswith(prefix))


def write_followup_markdown(rows: list[dict[str, str]]) -> None:
    FOLLOWUP_MD.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).date().isoformat()
    overall_status = determine_overall_status(rows)
    tracker_counts = count_field(rows, "tracker_status")
    status_counts = count_field(rows, "followup_status")

    attention_rows = [
        row for row in rows
        if safe_get(row, "management_attention_required") == "yes"
    ]

    active_rows = [
        row for row in rows
        if safe_get(row, "tracker_status") in {"FOLLOWUP_IN_PROGRESS", "FOLLOWUP_NOT_STARTED"}
    ]

    lines = [
        "# Security Evidence Decision Follow-Up Tracker",
        "",
        f"Generated: `{timestamp}`",
        f"Review Date: `{today}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This tracker monitors follow-up required by management decisions.",
        "",
        "It shows whether follow-up is not started, in progress, blocked, overdue, completed, cancelled, or not applicable.",
        "",
        "## Executive Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Follow-up rows | `{len(rows)}` |",
        f"| Management attention required | `{len(attention_rows)}` |",
        f"| Active follow-ups | `{len(active_rows)}` |",
        f"| Overdue follow-ups | `{safe_status_count(tracker_counts, 'FOLLOWUP_OVERDUE_')}` |",
        f"| Blocked follow-ups | `{tracker_counts.get('FOLLOWUP_BLOCKED', 0)}` |",
        f"| Completed follow-ups | `{tracker_counts.get('FOLLOWUP_COMPLETED', 0)}` |",
        f"| No follow-up required | `{tracker_counts.get('NO_FOLLOWUP_REQUIRED', 0)}` |",
        "",
        "## Follow-Up Status Counts",
        "",
        "| Follow-Up Status | Count |",
        "|---|---:|",
    ]

    for status, count in sorted(status_counts.items()):
        lines.append(f"| `{safe_cell(status)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Tracker Status Counts",
            "",
            "| Tracker Status | Count |",
            "|---|---:|",
        ]
    )

    for status, count in sorted(tracker_counts.items()):
        lines.append(f"| `{safe_cell(status)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Items Requiring Management Attention",
            "",
            "| Follow-Up | Priority | Owner | Due | Status | Issue | Recommended Next Step |",
            "|---|---|---|---|---|---|---|",
        ]
    )

    if attention_rows:
        for row in attention_rows:
            lines.append(
                f"| {safe_cell(row['followup_id'])} | "
                f"**{safe_cell(row['priority'])}** | "
                f"{safe_cell(row['followup_owner'])} | "
                f"{safe_cell(row['followup_date'] or 'not_recorded')} | "
                f"`{safe_cell(row['tracker_status'])}` | "
                f"{safe_cell(row['issue'])} | "
                f"{safe_cell(row['recommended_next_step'])} |"
            )
    else:
        lines.append(
            "| `none` | `P4` | Evidence owner | not_recorded | `NO_ATTENTION_REQUIRED` | "
            "No follow-up items require management attention. | Continue routine monitoring. |"
        )

    lines.extend(
        [
            "",
            "## Full Follow-Up Table",
            "",
            "| Follow-Up | Decision | Priority | Owner | Due | Days | Follow-Up Status | Tracker Status |",
            "|---|---|---|---|---|---:|---|---|",
        ]
    )

    for row in rows:
        lines.append(
            f"| {safe_cell(row['followup_id'])} | "
            f"{safe_cell(row['decision_id'])} | "
            f"**{safe_cell(row['priority'])}** | "
            f"{safe_cell(row['followup_owner'])} | "
            f"{safe_cell(row['followup_date'] or 'not_recorded')} | "
            f"{safe_cell(row['days_until_followup'])} | "
            f"`{safe_cell(row['followup_status'])}` | "
            f"`{safe_cell(row['tracker_status'])}` |"
        )

    lines.extend(
        [
            "",
            "## Allowed Follow-Up Status Values",
            "",
            "- `NOT_APPLICABLE`",
            "- `NOT_STARTED`",
            "- `IN_PROGRESS`",
            "- `BLOCKED`",
            "- `COMPLETED`",
            "- `CANCELLED`",
            "",
            "## Manual Fields Preserved on Rerun",
            "",
            "- `followup_status`",
            "- `followup_notes`",
            "- `completion_date`",
            "- `completion_evidence`",
            "",
            "## Completion Rule",
            "",
            "A completed follow-up should include:",
            "",
            "- `followup_status = COMPLETED`",
            "- `completion_date` in `YYYY-MM-DD` format",
            "- `completion_evidence` pointing to the artifact, record, note, or decision that proves completion",
            "",
            "## Governance Rule",
            "",
            "> Management decisions are not finished until required follow-up is tracked, completed, cancelled with rationale, or explicitly not applicable.",
            "",
            "## One-Sentence Takeaway",
            "",
            "> Decision follow-up tracking prevents management review from becoming meeting theater.",
            "",
        ]
    )

    FOLLOWUP_MD.write_text("\n".join(lines), encoding="utf-8")


def write_report(rows: list[dict[str, str]]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    overall_status = determine_overall_status(rows)
    tracker_counts = count_field(rows, "tracker_status")

    attention_count = sum(
        1 for row in rows
        if safe_get(row, "management_attention_required") == "yes"
    )

    lines = [
        "# Security Evidence Decision Follow-Up Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report records generation of the management decision follow-up tracker.",
        "",
        "## Input Artifact",
        "",
        "| Artifact | Status |",
        "|---|---|",
        f"| `{DECISIONS_CSV.as_posix()}` | {artifact_status(DECISIONS_CSV)} |",
        "",
        "## Generated Artifacts",
        "",
        f"- `{FOLLOWUP_TRACKER.as_posix()}`",
        f"- `{FOLLOWUP_MD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Follow-Up Counts",
        "",
        "| Category | Count |",
        "|---|---:|",
        f"| Follow-up rows | `{len(rows)}` |",
        f"| Management attention required | `{attention_count}` |",
        f"| Overdue follow-ups | `{safe_status_count(tracker_counts, 'FOLLOWUP_OVERDUE_')}` |",
        f"| Blocked follow-ups | `{tracker_counts.get('FOLLOWUP_BLOCKED', 0)}` |",
        f"| Completed follow-ups | `{tracker_counts.get('FOLLOWUP_COMPLETED', 0)}` |",
        f"| No follow-up required | `{tracker_counts.get('NO_FOLLOWUP_REQUIRED', 0)}` |",
        "",
        "## Control Mapping",
        "",
        "| Control Concept | Evidence Contribution |",
        "|---|---|",
        "| Follow-up discipline | Tracks whether management decisions were carried forward. |",
        "| Ownership | Preserves follow-up owner and due date from the decision log. |",
        "| Closure evidence | Flags completed follow-ups without completion evidence. |",
        "| Escalation | Flags blocked and overdue follow-ups for management attention. |",
        "| Continuity | Preserves manual follow-up status fields across reruns. |",
        "",
        "## One-Sentence Takeaway",
        "",
        "> Decision follow-up tracking turns management decisions into accountable execution evidence.",
        "",
    ]

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_followup_rows()

    fieldnames = [
        "followup_id",
        "decision_id",
        "review_id",
        "action_id",
        "stable_exception_key",
        "exception_id",
        "priority",
        "severity",
        "lifecycle_stage",
        "exception_type",
        "issue",
        "management_decision",
        "decision_owner",
        "decision_date",
        "decision_completeness_status",
        "followup_required",
        "followup_owner",
        "followup_date",
        "days_until_followup",
        "followup_status",
        "tracker_status",
        "management_attention_required",
        "recommended_next_step",
        "followup_notes",
        "completion_date",
        "completion_evidence",
        "generated_at",
    ]

    write_csv(FOLLOWUP_TRACKER, rows, fieldnames)
    write_followup_markdown(rows)
    write_report(rows)

    overall_status = determine_overall_status(rows)
    tracker_counts = count_field(rows, "tracker_status")

    attention_count = sum(
        1 for row in rows
        if safe_get(row, "management_attention_required") == "yes"
    )

    print(f"Decision follow-up tracker written to: {FOLLOWUP_TRACKER}")
    print(f"Decision follow-up markdown written to: {FOLLOWUP_MD}")
    print(f"Decision follow-up report written to: {REPORT_FILE}")
    print(f"Management attention required: {attention_count}")
    print(f"Overdue follow-ups: {safe_status_count(tracker_counts, 'FOLLOWUP_OVERDUE_')}")
    print(f"Blocked follow-ups: {tracker_counts.get('FOLLOWUP_BLOCKED', 0)}")
    print(f"Completed follow-ups: {tracker_counts.get('FOLLOWUP_COMPLETED', 0)}")
    print(f"Overall Status: {overall_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())