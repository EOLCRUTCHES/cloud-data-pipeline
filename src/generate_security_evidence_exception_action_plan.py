from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import hashlib
import sys


EXCEPTION_REGISTER = Path("ai/security_evidence_traceability_exceptions.csv")

ACTION_PLAN = Path("ai/security_evidence_exception_action_plan.csv")
ACTION_PLAN_MD = Path("docs/cloud/security_evidence_exception_action_plan.md")
REPORT_FILE = Path("evidence/generated/security_evidence_exception_action_plan_report.md")


ALLOWED_ACTION_STATUSES = {
    "NOT_STARTED",
    "IN_PROGRESS",
    "BLOCKED",
    "ACCEPTED_RISK",
    "RESOLVED",
    "DEFERRED",
}


MANUAL_FIELDS = [
    "assigned_owner",
    "target_date",
    "action_status",
    "action_notes",
    "resolution_evidence",
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


def stable_key_for_exception(row: dict[str, str]) -> str:
    parts = [
        safe_get(row, "source_artifact"),
        safe_get(row, "source_record_id"),
        safe_get(row, "lifecycle_stage"),
        safe_get(row, "exception_type"),
        safe_get(row, "issue"),
    ]

    key_material = "||".join(parts)
    digest = hashlib.sha256(key_material.encode("utf-8")).hexdigest()[:16]

    return f"EXC-KEY-{digest}"


def recommended_priority(row: dict[str, str]) -> str:
    severity = safe_get(row, "severity")
    exception_status = safe_get(row, "exception_status")
    exception_type = safe_get(row, "exception_type")

    if exception_status != "OPEN":
        return "P4"

    if severity == "HIGH":
        return "P1"

    if severity == "MEDIUM":
        return "P2"

    if severity == "LOW":
        return "P3"

    if exception_type == "NO_OPEN_EXCEPTIONS":
        return "P4"

    return "P3"


def recommended_action_status(row: dict[str, str]) -> str:
    exception_status = safe_get(row, "exception_status")
    exception_type = safe_get(row, "exception_type")

    if exception_type == "NO_OPEN_EXCEPTIONS":
        return "RESOLVED"

    if exception_status == "CLOSED":
        return "RESOLVED"

    return "NOT_STARTED"


def recommended_target_timing(row: dict[str, str]) -> str:
    priority = recommended_priority(row)
    due_timing = safe_get(row, "due_timing")

    if due_timing:
        return due_timing

    if priority == "P1":
        return "Before next evidence-system reliance decision"

    if priority == "P2":
        return "At next evidence review checkpoint"

    if priority == "P3":
        return "During routine maintenance"

    return "No immediate action required"


def default_owner(row: dict[str, str]) -> str:
    owner = safe_get(row, "owner")
    if owner:
        return owner

    lifecycle_stage = safe_get(row, "lifecycle_stage")

    if lifecycle_stage == "Human Review":
        return "Human reviewer"

    if lifecycle_stage in {"Evaluation", "Retrieval", "Answer Layer"}:
        return "Evidence automation owner"

    return "Evidence owner"


def planned_next_step(row: dict[str, str]) -> str:
    action = safe_get(row, "recommended_action")
    if action:
        return action

    exception_type = safe_get(row, "exception_type")

    if exception_type == "NO_OPEN_EXCEPTIONS":
        return "Continue routine monitoring."

    return "Review exception and define corrective action."


def existing_manual_values() -> dict[str, dict[str, str]]:
    existing_rows = read_csv(ACTION_PLAN)
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


def normalize_action_status(value: str, default: str) -> str:
    normalized = (value or "").strip().upper()

    if normalized in ALLOWED_ACTION_STATUSES:
        return normalized

    return default


def build_action_rows() -> list[dict[str, str]]:
    generated_at = datetime.now(timezone.utc).isoformat()
    exception_rows = read_csv(EXCEPTION_REGISTER)
    existing_by_key = existing_manual_values()

    if not exception_rows:
        exception_rows = [
            {
                "exception_id": "EXC-000",
                "source_artifact": EXCEPTION_REGISTER.as_posix(),
                "source_record_id": "not_available",
                "lifecycle_stage": "Exception Management",
                "exception_type": "NO_EXCEPTION_REGISTER",
                "severity": "HIGH",
                "exception_status": "OPEN",
                "issue": "Exception register is missing or empty.",
                "recommended_action": "Run src/generate_security_evidence_traceability_exceptions.py.",
                "owner": "Evidence owner",
                "due_timing": "Before management review",
                "generated_at": generated_at,
            }
        ]

    action_rows = []

    for index, exception in enumerate(exception_rows, start=1):
        stable_key = stable_key_for_exception(exception)
        manual = existing_by_key.get(stable_key, {})

        recommended_status = recommended_action_status(exception)
        preserved_status = normalize_action_status(
            manual.get("action_status", ""),
            recommended_status,
        )

        assigned_owner = manual.get("assigned_owner", "") or default_owner(exception)
        target_date = manual.get("target_date", "")
        action_notes = manual.get("action_notes", "")
        resolution_evidence = manual.get("resolution_evidence", "")

        action_rows.append(
            {
                "action_id": f"ACT-{index:03d}",
                "stable_exception_key": stable_key,
                "exception_id": safe_get(exception, "exception_id"),
                "source_artifact": safe_get(exception, "source_artifact"),
                "source_record_id": safe_get(exception, "source_record_id"),
                "lifecycle_stage": safe_get(exception, "lifecycle_stage"),
                "exception_type": safe_get(exception, "exception_type"),
                "severity": safe_get(exception, "severity"),
                "priority": recommended_priority(exception),
                "exception_status": safe_get(exception, "exception_status"),
                "issue": safe_get(exception, "issue"),
                "planned_next_step": planned_next_step(exception),
                "assigned_owner": assigned_owner,
                "target_timing": recommended_target_timing(exception),
                "target_date": target_date,
                "action_status": preserved_status,
                "action_notes": action_notes,
                "resolution_evidence": resolution_evidence,
                "generated_at": generated_at,
            }
        )

    return action_rows


def count_field(rows: list[dict[str, str]], field: str) -> Counter:
    return Counter(safe_get(row, field) or "not_recorded" for row in rows)


def determine_overall_status(rows: list[dict[str, str]]) -> str:
    open_action_rows = [
        row for row in rows
        if safe_get(row, "action_status") not in {"RESOLVED", "ACCEPTED_RISK", "DEFERRED"}
    ]

    if not open_action_rows:
        return "NO_ACTIVE_EXCEPTION_ACTIONS"

    priority_counts = count_field(open_action_rows, "priority")
    status_counts = count_field(open_action_rows, "action_status")

    if priority_counts.get("P1", 0) > 0 and status_counts.get("NOT_STARTED", 0) > 0:
        return "P1_ACTIONS_NOT_STARTED"

    if priority_counts.get("P1", 0) > 0:
        return "P1_ACTIONS_ACTIVE"

    if status_counts.get("BLOCKED", 0) > 0:
        return "ACTION_PLAN_BLOCKED"

    if status_counts.get("NOT_STARTED", 0) > 0:
        return "ACTIONS_NOT_STARTED"

    return "ACTIONS_IN_PROGRESS"


def write_markdown_plan(rows: list[dict[str, str]]) -> None:
    ACTION_PLAN_MD.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    overall_status = determine_overall_status(rows)
    priority_counts = count_field(rows, "priority")
    action_status_counts = count_field(rows, "action_status")
    open_rows = [
        row for row in rows
        if safe_get(row, "action_status") not in {"RESOLVED", "ACCEPTED_RISK", "DEFERRED"}
    ]

    lines = [
        "# Security Evidence Exception Action Plan",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This action plan converts evidence-system exceptions into owned follow-up work.",
        "",
        "It is the bridge between finding exceptions and managing them to resolution, acceptance, deferral, or continued work.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Total action rows | `{len(rows)}` |",
        f"| Active action rows | `{len(open_rows)}` |",
        f"| P1 | `{priority_counts.get('P1', 0)}` |",
        f"| P2 | `{priority_counts.get('P2', 0)}` |",
        f"| P3 | `{priority_counts.get('P3', 0)}` |",
        f"| P4 | `{priority_counts.get('P4', 0)}` |",
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
            "## Active Actions",
            "",
            "| ID | Priority | Status | Owner | Issue | Next Step | Target |",
            "|---|---|---|---|---|---|---|",
        ]
    )

    if open_rows:
        for row in open_rows:
            lines.append(
                f"| {safe_cell(row['action_id'])} | "
                f"**{safe_cell(row['priority'])}** | "
                f"`{safe_cell(row['action_status'])}` | "
                f"{safe_cell(row['assigned_owner'])} | "
                f"{safe_cell(row['issue'])} | "
                f"{safe_cell(row['planned_next_step'])} | "
                f"{safe_cell(row['target_date'] or row['target_timing'])} |"
            )
    else:
        lines.append("| `none` | `P4` | `RESOLVED` | Evidence owner | No active exception actions. | Continue routine monitoring. | Routine review |")

    lines.extend(
        [
            "",
            "## Allowed Action Status Values",
            "",
            "- `NOT_STARTED`",
            "- `IN_PROGRESS`",
            "- `BLOCKED`",
            "- `ACCEPTED_RISK`",
            "- `RESOLVED`",
            "- `DEFERRED`",
            "",
            "## Manual Fields Preserved on Rerun",
            "",
            "- `assigned_owner`",
            "- `target_date`",
            "- `action_status`",
            "- `action_notes`",
            "- `resolution_evidence`",
            "",
            "## Governance Rule",
            "",
            "> Exceptions are not useful until they become owned action, accepted risk, deferred work, or resolved evidence.",
            "",
            "## One-Sentence Takeaway",
            "",
            "> An exception register says what is wrong; an action plan says who is doing what about it.",
            "",
        ]
    )

    ACTION_PLAN_MD.write_text("\n".join(lines), encoding="utf-8")


def write_report(rows: list[dict[str, str]]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    overall_status = determine_overall_status(rows)
    priority_counts = count_field(rows, "priority")
    action_status_counts = count_field(rows, "action_status")

    lines = [
        "# Security Evidence Exception Action Plan Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report records generation of the security evidence exception action plan.",
        "",
        "## Input Artifact",
        "",
        "| Artifact | Status |",
        "|---|---|",
        f"| `{EXCEPTION_REGISTER.as_posix()}` | {artifact_status(EXCEPTION_REGISTER)} |",
        "",
        "## Generated Artifacts",
        "",
        f"- `{ACTION_PLAN.as_posix()}`",
        f"- `{ACTION_PLAN_MD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Priority Counts",
        "",
        "| Priority | Count |",
        "|---|---:|",
    ]

    for priority, count in sorted(priority_counts.items()):
        lines.append(f"| `{safe_cell(priority)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Action Status Counts",
            "",
            "| Action Status | Count |",
            "|---|---:|",
        ]
    )

    for status, count in sorted(action_status_counts.items()):
        lines.append(f"| `{safe_cell(status)}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Control Mapping",
            "",
            "| Control Concept | Evidence Contribution |",
            "|---|---|",
            "| Ownership | Converts exceptions into owner-assigned action rows. |",
            "| Prioritization | Assigns action priority based on exception severity. |",
            "| Management review | Produces a readable plan for open exception work. |",
            "| Continuity | Preserves manual action status fields across reruns. |",
            "",
            "## One-Sentence Takeaway",
            "",
            "> Exception action planning turns review findings into managed work.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_action_rows()

    fieldnames = [
        "action_id",
        "stable_exception_key",
        "exception_id",
        "source_artifact",
        "source_record_id",
        "lifecycle_stage",
        "exception_type",
        "severity",
        "priority",
        "exception_status",
        "issue",
        "planned_next_step",
        "assigned_owner",
        "target_timing",
        "target_date",
        "action_status",
        "action_notes",
        "resolution_evidence",
        "generated_at",
    ]

    write_csv(ACTION_PLAN, rows, fieldnames)
    write_markdown_plan(rows)
    write_report(rows)

    overall_status = determine_overall_status(rows)
    priority_counts = count_field(rows, "priority")
    action_status_counts = count_field(rows, "action_status")

    print(f"Exception action plan written to: {ACTION_PLAN}")
    print(f"Exception action plan markdown written to: {ACTION_PLAN_MD}")
    print(f"Exception action plan report written to: {REPORT_FILE}")
    print(f"P1 actions: {priority_counts.get('P1', 0)}")
    print(f"NOT_STARTED actions: {action_status_counts.get('NOT_STARTED', 0)}")
    print(f"IN_PROGRESS actions: {action_status_counts.get('IN_PROGRESS', 0)}")
    print(f"Overall Status: {overall_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())