from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import re
import sys


REVIEW_STATUS = Path("ai/security_evidence_exception_review_status.csv")

DECISIONS_CSV = Path("ai/security_evidence_exception_management_decisions.csv")
DECISION_LOG_MD = Path("docs/cloud/security_evidence_exception_management_decision_log.md")
REPORT_FILE = Path("evidence/generated/security_evidence_exception_management_decision_report.md")


ALLOWED_MANAGEMENT_DECISIONS = {
    "PENDING_DECISION",
    "START_ACTION",
    "CONTINUE_ACTION",
    "ESCALATE",
    "REASSIGN_OWNER",
    "ACCEPT_RISK",
    "DEFER_ACTION",
    "MARK_RESOLVED",
    "ADD_EVIDENCE",
    "CORRECT_RECORD",
    "NO_ACTION_REQUIRED",
}


MANUAL_FIELDS = [
    "management_decision",
    "decision_owner",
    "decision_date",
    "decision_notes",
    "followup_required",
    "followup_date",
    "followup_owner",
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


def existing_manual_values() -> dict[str, dict[str, str]]:
    existing_rows = read_csv(DECISIONS_CSV)
    existing_by_key = {}

    for row in existing_rows:
        stable_key = safe_get(row, "stable_exception_key")
        if not stable_key:
            continue

        existing_by_key[stable_key] = {
            field: safe_get(row, field)
            for field in MANUAL_FIELDS
        }

    return existing_by_key


def normalize_decision(value: str, default: str) -> str:
    normalized = (value or "").strip().upper()

    if normalized in ALLOWED_MANAGEMENT_DECISIONS:
        return normalized

    return default


def recommended_decision_for_review(row: dict[str, str]) -> str:
    review_status = safe_get(row, "review_status")
    management_attention = safe_get(row, "management_attention_required")
    action_status = safe_get(row, "action_status")

    if management_attention == "no":
        if action_status == "RESOLVED":
            return "NO_ACTION_REQUIRED"
        if action_status in {"ACCEPTED_RISK", "DEFERRED"}:
            return "NO_ACTION_REQUIRED"
        return "CONTINUE_ACTION"

    if review_status in {"INVALID_ACTION_STATUS", "INVALID_TARGET_DATE"}:
        return "CORRECT_RECORD"

    if review_status == "RESOLVED_EVIDENCE_NEEDED":
        return "ADD_EVIDENCE"

    if review_status in {
        "ACCEPTED_RISK_RATIONALE_NEEDED",
        "DEFERRED_RATIONALE_NEEDED",
    }:
        return "CORRECT_RECORD"

    if review_status == "BLOCKED_MANAGEMENT_REVIEW":
        return "ESCALATE"

    if review_status == "P1_NOT_STARTED":
        return "START_ACTION"

    if review_status == "NOT_STARTED_NO_TARGET_DATE":
        return "START_ACTION"

    if review_status == "IN_PROGRESS_NO_TARGET_DATE":
        return "CONTINUE_ACTION"

    if review_status.startswith("OVERDUE_"):
        return "ESCALATE"

    return "PENDING_DECISION"


def decision_completeness_status(row: dict[str, str]) -> str:
    decision = safe_get(row, "management_decision")
    owner = safe_get(row, "decision_owner")
    decision_date = safe_get(row, "decision_date")
    notes = safe_get(row, "decision_notes")
    followup_required = safe_get(row, "followup_required").lower()
    followup_date = safe_get(row, "followup_date")
    followup_owner = safe_get(row, "followup_owner")

    if decision not in ALLOWED_MANAGEMENT_DECISIONS:
        return "INVALID_MANAGEMENT_DECISION"

    if decision == "PENDING_DECISION":
        return "PENDING_MANAGEMENT_DECISION"

    missing = []

    if not owner:
        missing.append("decision_owner")

    if not valid_date(decision_date):
        missing.append("decision_date")

    if not notes:
        missing.append("decision_notes")

    if followup_required not in {"yes", "no"}:
        missing.append("followup_required_yes_or_no")

    if followup_required == "yes":
        if not valid_date(followup_date):
            missing.append("followup_date")
        if not followup_owner:
            missing.append("followup_owner")

    if missing:
        return "DECISION_INCOMPLETE_" + "_".join(missing)

    return "DECISION_COMPLETE"


def build_decision_rows() -> list[dict[str, str]]:
    generated_at = datetime.now(timezone.utc).isoformat()
    review_rows = read_csv(REVIEW_STATUS)
    existing_by_key = existing_manual_values()

    if not review_rows:
        review_rows = [
            {
                "review_id": "REV-000",
                "action_id": "",
                "stable_exception_key": "NO_REVIEW_STATUS",
                "exception_id": "",
                "priority": "P1",
                "severity": "HIGH",
                "lifecycle_stage": "Management Review",
                "exception_type": "NO_REVIEW_STATUS",
                "assigned_owner": "Evidence owner",
                "action_status": "NOT_STARTED",
                "target_date": "",
                "days_until_target": "not_recorded",
                "review_status": "NO_REVIEW_STATUS",
                "management_attention_required": "yes",
                "issue": "Exception review status is missing or empty.",
                "planned_next_step": "Run src/generate_security_evidence_exception_review_packet.py.",
                "action_notes": "",
                "resolution_evidence": "",
                "review_recommendation": "Generate the review packet before recording management decisions.",
                "generated_at": generated_at,
            }
        ]

    decision_rows = []

    for index, review in enumerate(review_rows, start=1):
        stable_key = safe_get(review, "stable_exception_key") or safe_get(review, "review_id")
        manual = existing_by_key.get(stable_key, {})

        recommended_decision = recommended_decision_for_review(review)
        management_decision = normalize_decision(
            manual.get("management_decision", ""),
            recommended_decision,
        )

        row = {
            "decision_id": f"MGMT-DEC-{index:03d}",
            "review_id": safe_get(review, "review_id"),
            "action_id": safe_get(review, "action_id"),
            "stable_exception_key": stable_key,
            "exception_id": safe_get(review, "exception_id"),
            "priority": safe_get(review, "priority"),
            "severity": safe_get(review, "severity"),
            "lifecycle_stage": safe_get(review, "lifecycle_stage"),
            "exception_type": safe_get(review, "exception_type"),
            "assigned_owner": safe_get(review, "assigned_owner"),
            "action_status": safe_get(review, "action_status"),
            "review_status": safe_get(review, "review_status"),
            "management_attention_required": safe_get(review, "management_attention_required"),
            "issue": safe_get(review, "issue"),
            "review_recommendation": safe_get(review, "review_recommendation"),
            "recommended_management_decision": recommended_decision,
            "management_decision": management_decision,
            "decision_owner": manual.get("decision_owner", ""),
            "decision_date": manual.get("decision_date", ""),
            "decision_notes": manual.get("decision_notes", ""),
            "followup_required": manual.get("followup_required", ""),
            "followup_date": manual.get("followup_date", ""),
            "followup_owner": manual.get("followup_owner", ""),
            "generated_at": generated_at,
        }

        row["decision_completeness_status"] = decision_completeness_status(row)
        decision_rows.append(row)

    return decision_rows


def count_field(rows: list[dict[str, str]], field: str) -> Counter:
    return Counter(safe_get(row, field) or "not_recorded" for row in rows)


def determine_overall_status(rows: list[dict[str, str]]) -> str:
    completeness_counts = count_field(rows, "decision_completeness_status")
    decision_counts = count_field(rows, "management_decision")

    if completeness_counts.get("INVALID_MANAGEMENT_DECISION", 0) > 0:
        return "REVIEW_REQUIRED_INVALID_MANAGEMENT_DECISION"

    incomplete_count = sum(
        count for status, count in completeness_counts.items()
        if status.startswith("DECISION_INCOMPLETE")
    )

    if incomplete_count > 0:
        return "REVIEW_REQUIRED_INCOMPLETE_DECISIONS"

    if completeness_counts.get("PENDING_MANAGEMENT_DECISION", 0) > 0:
        return "PENDING_MANAGEMENT_DECISIONS"

    if decision_counts.get("ESCALATE", 0) > 0:
        return "MANAGEMENT_ESCALATIONS_RECORDED"

    if decision_counts.get("REASSIGN_OWNER", 0) > 0:
        return "REASSIGNMENTS_RECORDED"

    return "MANAGEMENT_DECISIONS_COMPLETE"


def write_decision_log(rows: list[dict[str, str]]) -> None:
    DECISION_LOG_MD.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    overall_status = determine_overall_status(rows)
    decision_counts = count_field(rows, "management_decision")
    completeness_counts = count_field(rows, "decision_completeness_status")

    attention_rows = [
        row for row in rows
        if safe_get(row, "management_attention_required") == "yes"
    ]

    lines = [
        "# Security Evidence Exception Management Decision Log",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This log records management decisions made against exception review items.",
        "",
        "It preserves decision owner, date, notes, follow-up requirement, follow-up owner, and follow-up date across reruns.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Decision rows | `{len(rows)}` |",
        f"| Items requiring management attention | `{len(attention_rows)}` |",
        f"| Pending decisions | `{completeness_counts.get('PENDING_MANAGEMENT_DECISION', 0)}` |",
        f"| Complete decisions | `{completeness_counts.get('DECISION_COMPLETE', 0)}` |",
        f"| Invalid decisions | `{completeness_counts.get('INVALID_MANAGEMENT_DECISION', 0)}` |",
        "",
        "## Management Decision Counts",
        "",
        "| Decision | Count |",
        "|---|---:|",
    ]

    for decision, count in sorted(decision_counts.items()):
        lines.append(f"| `{safe_cell(decision)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Decision Completeness Counts",
            "",
            "| Completeness Status | Count |",
            "|---|---:|",
        ]
    )

    for status, count in sorted(completeness_counts.items()):
        lines.append(f"| `{safe_cell(status)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Attention Items",
            "",
            "| Decision ID | Priority | Review Status | Recommended Decision | Recorded Decision | Completeness | Issue |",
            "|---|---|---|---|---|---|---|",
        ]
    )

    if attention_rows:
        for row in attention_rows:
            lines.append(
                f"| {safe_cell(row['decision_id'])} | "
                f"**{safe_cell(row['priority'])}** | "
                f"`{safe_cell(row['review_status'])}` | "
                f"`{safe_cell(row['recommended_management_decision'])}` | "
                f"`{safe_cell(row['management_decision'])}` | "
                f"**{safe_cell(row['decision_completeness_status'])}** | "
                f"{safe_cell(row['issue'])} |"
            )
    else:
        lines.append(
            "| `none` | `P4` | `NO_ATTENTION_REQUIRED` | `NO_ACTION_REQUIRED` | "
            "`NO_ACTION_REQUIRED` | `DECISION_COMPLETE` | No management-attention items. |"
        )

    lines.extend(
        [
            "",
            "## Allowed Management Decisions",
            "",
            "- `PENDING_DECISION`",
            "- `START_ACTION`",
            "- `CONTINUE_ACTION`",
            "- `ESCALATE`",
            "- `REASSIGN_OWNER`",
            "- `ACCEPT_RISK`",
            "- `DEFER_ACTION`",
            "- `MARK_RESOLVED`",
            "- `ADD_EVIDENCE`",
            "- `CORRECT_RECORD`",
            "- `NO_ACTION_REQUIRED`",
            "",
            "## Manual Fields Preserved on Rerun",
            "",
            "- `management_decision`",
            "- `decision_owner`",
            "- `decision_date`",
            "- `decision_notes`",
            "- `followup_required`",
            "- `followup_date`",
            "- `followup_owner`",
            "",
            "## Decision Completeness Rule",
            "",
            "Any non-pending decision should include:",
            "",
            "- `decision_owner`",
            "- `decision_date` in `YYYY-MM-DD` format",
            "- `decision_notes`",
            "- `followup_required` as `yes` or `no`",
            "",
            "If `followup_required` is `yes`, also include:",
            "",
            "- `followup_date` in `YYYY-MM-DD` format",
            "- `followup_owner`",
            "",
            "## Governance Rule",
            "",
            "> Management review is not complete until decisions, rationale, owners, dates, and follow-up needs are recorded.",
            "",
            "## One-Sentence Takeaway",
            "",
            "> A review packet becomes governable when management decisions are recorded and follow-up is explicit.",
            "",
        ]
    )

    DECISION_LOG_MD.write_text("\n".join(lines), encoding="utf-8")


def write_report(rows: list[dict[str, str]]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    overall_status = determine_overall_status(rows)
    decision_counts = count_field(rows, "management_decision")
    completeness_counts = count_field(rows, "decision_completeness_status")

    lines = [
        "# Security Evidence Exception Management Decision Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report records generation of the exception management decision log.",
        "",
        "## Input Artifact",
        "",
        "| Artifact | Status |",
        "|---|---|",
        f"| `{REVIEW_STATUS.as_posix()}` | {artifact_status(REVIEW_STATUS)} |",
        "",
        "## Generated Artifacts",
        "",
        f"- `{DECISIONS_CSV.as_posix()}`",
        f"- `{DECISION_LOG_MD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Management Decision Counts",
        "",
        "| Decision | Count |",
        "|---|---:|",
    ]

    for decision, count in sorted(decision_counts.items()):
        lines.append(f"| `{safe_cell(decision)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Completeness Counts",
            "",
            "| Completeness Status | Count |",
            "|---|---:|",
        ]
    )

    for status, count in sorted(completeness_counts.items()):
        lines.append(f"| `{safe_cell(status)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Control Mapping",
            "",
            "| Control Concept | Evidence Contribution |",
            "|---|---|",
            "| Management decisioning | Records what management decided for each review item. |",
            "| Follow-up discipline | Requires explicit follow-up owner and date when follow-up is needed. |",
            "| Rationale | Requires notes for non-pending decisions. |",
            "| Auditability | Preserves manual management decision fields across reruns. |",
            "",
            "## One-Sentence Takeaway",
            "",
            "> Management decisions make exception review auditable.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_decision_rows()

    fieldnames = [
        "decision_id",
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
        "review_status",
        "management_attention_required",
        "issue",
        "review_recommendation",
        "recommended_management_decision",
        "management_decision",
        "decision_owner",
        "decision_date",
        "decision_notes",
        "followup_required",
        "followup_date",
        "followup_owner",
        "decision_completeness_status",
        "generated_at",
    ]

    write_csv(DECISIONS_CSV, rows, fieldnames)
    write_decision_log(rows)
    write_report(rows)

    overall_status = determine_overall_status(rows)
    decision_counts = count_field(rows, "management_decision")
    completeness_counts = count_field(rows, "decision_completeness_status")

    print(f"Management decisions written to: {DECISIONS_CSV}")
    print(f"Decision log written to: {DECISION_LOG_MD}")
    print(f"Decision report written to: {REPORT_FILE}")
    print(f"Pending decisions: {completeness_counts.get('PENDING_MANAGEMENT_DECISION', 0)}")
    print(f"Complete decisions: {completeness_counts.get('DECISION_COMPLETE', 0)}")
    print(f"Escalations: {decision_counts.get('ESCALATE', 0)}")
    print(f"Overall Status: {overall_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())