from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import sys


FOLLOWUP_TRACKER = Path("ai/security_evidence_decision_followup_tracker.csv")

CLOSEOUT_CSV = Path("ai/security_evidence_management_closeout_summary.csv")
CLOSEOUT_MD = Path("docs/cloud/security_evidence_management_closeout_summary.md")
REPORT_FILE = Path("evidence/generated/security_evidence_management_closeout_report.md")


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


def safe_get(row: dict[str, str], field: str) -> str:
    return (row.get(field, "") or "").strip()


def first_present(row: dict[str, str], fields: list[str]) -> str:
    for field in fields:
        value = safe_get(row, field)
        if value:
            return value
    return ""


def safe_cell(value: object) -> str:
    return str(value).replace("|", " ").replace("\n", " ").strip()


def artifact_status(path: Path) -> str:
    if path.exists() and path.stat().st_size > 0:
        return "Present"
    if path.exists() and path.stat().st_size == 0:
        return "Empty"
    return "Missing"


def count_field(rows: list[dict[str, str]], field: str) -> Counter:
    return Counter(safe_get(row, field) or "not_recorded" for row in rows)


def closeout_category(row: dict[str, str]) -> str:
    tracker_status = safe_get(row, "tracker_status")
    followup_status = safe_get(row, "followup_status")

    if tracker_status == "FOLLOWUP_COMPLETED":
        return "CLOSED_WITH_EVIDENCE"

    if tracker_status == "NO_FOLLOWUP_REQUIRED":
        return "CLOSED_NO_FOLLOWUP_REQUIRED"

    if tracker_status == "FOLLOWUP_CANCELLED":
        return "CLOSED_CANCELLED_WITH_RATIONALE"

    if tracker_status.startswith("FOLLOWUP_OVERDUE_"):
        return "OPEN_OVERDUE"

    if tracker_status == "FOLLOWUP_BLOCKED":
        return "OPEN_BLOCKED"

    if tracker_status in {"FOLLOWUP_IN_PROGRESS", "FOLLOWUP_NOT_STARTED"}:
        return "OPEN_ACTIVE"

    review_required_statuses = {
        "COMPLETED_EVIDENCE_NEEDED",
        "COMPLETED_DATE_NEEDED",
        "DECISION_RECORD_INCOMPLETE",
        "FOLLOWUP_REQUIREMENT_INVALID",
        "INVALID_FOLLOWUP_STATUS",
        "NO_FOLLOWUP_REQUIRED_STATUS_REVIEW",
        "FOLLOWUP_OWNER_MISSING",
        "FOLLOWUP_DATE_MISSING",
        "INVALID_FOLLOWUP_DATE",
        "INVALID_COMPLETION_DATE",
        "CANCELLED_RATIONALE_NEEDED",
    }

    if tracker_status in review_required_statuses:
        return "REVIEW_REQUIRED"

    if followup_status == "NOT_APPLICABLE":
        return "CLOSED_NO_FOLLOWUP_REQUIRED"

    return "REVIEW_REQUIRED"


def recommended_closeout_action(row: dict[str, str]) -> str:
    category = closeout_category(row)
    tracker_status = safe_get(row, "tracker_status")

    if category == "CLOSED_WITH_EVIDENCE":
        return "Archive as closed with completion evidence."

    if category == "CLOSED_NO_FOLLOWUP_REQUIRED":
        return "Archive as closed; no follow-up required."

    if category == "CLOSED_CANCELLED_WITH_RATIONALE":
        return "Archive as cancelled with rationale."

    if category == "OPEN_ACTIVE":
        return "Continue tracking through the follow-up workflow."

    if category == "OPEN_BLOCKED":
        return "Escalate blocked follow-up to management review."

    if category == "OPEN_OVERDUE":
        return "Escalate overdue follow-up and reset owner/date or close with evidence."

    if tracker_status == "DECISION_RECORD_INCOMPLETE":
        return "Complete the management decision record in ai/security_evidence_exception_management_decisions.csv."

    if tracker_status == "COMPLETED_EVIDENCE_NEEDED":
        return "Add completion_evidence to the follow-up tracker source record."

    if tracker_status == "COMPLETED_DATE_NEEDED":
        return "Add completion_date in YYYY-MM-DD format."

    if tracker_status == "CANCELLED_RATIONALE_NEEDED":
        return "Add cancellation rationale in followup_notes."

    return "Review the tracker status and correct the source management or follow-up record."


def build_closeout_rows() -> list[dict[str, str]]:
    generated_at = datetime.now(timezone.utc).isoformat()
    rows = read_csv(FOLLOWUP_TRACKER)

    if not rows:
        return [
            {
                "closeout_id": "CLOSE-000",
                "followup_id": "",
                "decision_id": "",
                "priority": "P1",
                "owner": "Evidence owner",
                "issue": "Follow-up tracker missing or empty.",
                "tracker_status": "NO_FOLLOWUP_TRACKER",
                "followup_status": "",
                "closeout_category": "REVIEW_REQUIRED",
                "completion_evidence": "",
                "recommended_next_step": "Run src/generate_security_evidence_decision_followup_tracker.py.",
                "generated_at": generated_at,
            }
        ]

    closeout_rows = []

    for index, row in enumerate(rows, start=1):
        owner = first_present(
            row,
            [
                "followup_owner",
                "decision_owner",
                "assigned_owner",
                "owner",
            ],
        )

        issue = first_present(
            row,
            [
                "issue",
                "exception_description",
                "management_review_issue",
                "action_description",
                "decision_notes",
            ],
        )

        priority = first_present(row, ["priority", "management_priority", "severity"])

        closeout_rows.append(
            {
                "closeout_id": f"CLOSE-{index:03d}",
                "followup_id": safe_get(row, "followup_id"),
                "decision_id": safe_get(row, "decision_id"),
                "priority": priority or "P3",
                "owner": owner or "Evidence owner",
                "issue": issue or "No issue description recorded.",
                "tracker_status": safe_get(row, "tracker_status") or "TRACKER_STATUS_MISSING",
                "followup_status": safe_get(row, "followup_status"),
                "closeout_category": closeout_category(row),
                "completion_evidence": safe_get(row, "completion_evidence"),
                "recommended_next_step": recommended_closeout_action(row),
                "generated_at": generated_at,
            }
        )

    return closeout_rows


def determine_overall_status(rows: list[dict[str, str]]) -> str:
    counts = count_field(rows, "closeout_category")

    if counts.get("REVIEW_REQUIRED", 0) > 0:
        return "CLOSEOUT_REVIEW_REQUIRED"

    if counts.get("OPEN_OVERDUE", 0) > 0:
        return "CLOSEOUT_OVERDUE_ITEMS"

    if counts.get("OPEN_BLOCKED", 0) > 0:
        return "CLOSEOUT_BLOCKED_ITEMS"

    if counts.get("OPEN_ACTIVE", 0) > 0:
        return "CLOSEOUT_ACTIVE_ITEMS"

    return "CLOSEOUT_COMPLETE"


def write_markdown(rows: list[dict[str, str]]) -> None:
    CLOSEOUT_MD.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    overall_status = determine_overall_status(rows)
    category_counts = count_field(rows, "closeout_category")

    open_rows = [
        row
        for row in rows
        if safe_get(row, "closeout_category")
        in {
            "OPEN_ACTIVE",
            "OPEN_BLOCKED",
            "OPEN_OVERDUE",
            "REVIEW_REQUIRED",
        }
    ]

    lines = [
        "# Security Evidence Management Closeout Summary",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This closeout summary shows whether management decision follow-up is complete, active, blocked, overdue, cancelled, not applicable, or still review-required.",
        "",
        "## Closeout Category Counts",
        "",
        "| Category | Count |",
        "|---|---:|",
    ]

    for category, count in sorted(category_counts.items()):
        lines.append(f"| `{safe_cell(category)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Items Still Needing Attention",
            "",
            "| Closeout | Priority | Owner | Category | Issue | Next Step |",
            "|---|---|---|---|---|---|",
        ]
    )

    if open_rows:
        for row in open_rows:
            lines.append(
                f"| {safe_cell(row['closeout_id'])} | "
                f"**{safe_cell(row['priority'])}** | "
                f"{safe_cell(row['owner'])} | "
                f"`{safe_cell(row['closeout_category'])}` | "
                f"{safe_cell(row['issue'])} | "
                f"{safe_cell(row['recommended_next_step'])} |"
            )
    else:
        lines.append(
            "| `none` | `P4` | Evidence owner | `CLOSEOUT_COMPLETE` | "
            "No open closeout items. | Continue routine monitoring. |"
        )

    lines.extend(
        [
            "",
            "## Governance Rule",
            "",
            "> Management review is not complete until follow-up is either closed with evidence, cancelled with rationale, marked not applicable, or kept visible as active work.",
            "",
            "## One-Sentence Takeaway",
            "",
            "> Closeout turns follow-up tracking into a final management status view.",
            "",
        ]
    )

    CLOSEOUT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_report(rows: list[dict[str, str]]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    overall_status = determine_overall_status(rows)
    category_counts = count_field(rows, "closeout_category")

    lines = [
        "# Security Evidence Management Closeout Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Input Artifact",
        "",
        "| Artifact | Status |",
        "|---|---|",
        f"| `{FOLLOWUP_TRACKER.as_posix()}` | {artifact_status(FOLLOWUP_TRACKER)} |",
        "",
        "## Generated Artifacts",
        "",
        f"- `{CLOSEOUT_CSV.as_posix()}`",
        f"- `{CLOSEOUT_MD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Counts",
        "",
        "| Category | Count |",
        "|---|---:|",
    ]

    for category, count in sorted(category_counts.items()):
        lines.append(f"| `{safe_cell(category)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## One-Sentence Takeaway",
            "",
            "> Closeout evidence shows whether management follow-up actually reached a defensible ending state.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_closeout_rows()

    fieldnames = [
        "closeout_id",
        "followup_id",
        "decision_id",
        "priority",
        "owner",
        "issue",
        "tracker_status",
        "followup_status",
        "closeout_category",
        "completion_evidence",
        "recommended_next_step",
        "generated_at",
    ]

    write_csv(CLOSEOUT_CSV, rows, fieldnames)
    write_markdown(rows)
    write_report(rows)

    counts = count_field(rows, "closeout_category")
    overall_status = determine_overall_status(rows)

    print(f"Closeout CSV written to: {CLOSEOUT_CSV}")
    print(f"Closeout summary written to: {CLOSEOUT_MD}")
    print(f"Closeout report written to: {REPORT_FILE}")
    print(f"Closed with evidence: {counts.get('CLOSED_WITH_EVIDENCE', 0)}")
    print(f"Closed no follow-up required: {counts.get('CLOSED_NO_FOLLOWUP_REQUIRED', 0)}")
    print(f"Open active: {counts.get('OPEN_ACTIVE', 0)}")
    print(f"Open overdue: {counts.get('OPEN_OVERDUE', 0)}")
    print(f"Open blocked: {counts.get('OPEN_BLOCKED', 0)}")
    print(f"Review required: {counts.get('REVIEW_REQUIRED', 0)}")
    print(f"Overall Status: {overall_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())