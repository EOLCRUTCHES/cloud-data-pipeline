from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import sys


STATUS_DASHBOARD_MD = Path("docs/cloud/security_evidence_status_dashboard.md")
CLOSEOUT_MD = Path("docs/cloud/security_evidence_management_closeout_summary.md")
CONTROL_NARRATIVE_MD = Path("docs/cloud/security_evidence_control_narrative.md")

CORPUS_MANIFEST = Path("ai/security_evidence_corpus_manifest.csv")
TRACEABILITY_EXCEPTIONS = Path("ai/security_evidence_traceability_exceptions.csv")
ACTION_PLAN = Path("ai/security_evidence_exception_action_plan.csv")
MANAGEMENT_DECISIONS = Path("ai/security_evidence_exception_management_decisions.csv")
FOLLOWUP_TRACKER = Path("ai/security_evidence_decision_followup_tracker.csv")
CLOSEOUT_SUMMARY = Path("ai/security_evidence_management_closeout_summary.csv")

EXECUTIVE_CSV = Path("ai/security_evidence_executive_summary.csv")
EXECUTIVE_MD = Path("docs/cloud/security_evidence_executive_summary.md")
REPORT_FILE = Path("evidence/generated/security_evidence_executive_summary_report.md")


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


def safe_cell(value: object) -> str:
    return str(value).replace("|", " ").replace("\n", " ").strip()


def artifact_status(path: Path) -> str:
    if path.exists() and path.stat().st_size > 0:
        return "Present"
    if path.exists() and path.stat().st_size == 0:
        return "Empty"
    return "Missing"


def extract_markdown_label(path: Path, label: str) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return "not_available"

    prefix = f"{label}:".lower()

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()

        if stripped.lower().startswith(prefix):
            value = stripped.split(":", 1)[1].strip()
            value = value.replace("**", "").replace("`", "").strip()
            return value or "not_recorded"

    return "not_recorded"


def count_field(rows: list[dict[str, str]], field: str) -> Counter:
    return Counter(safe_get(row, field) or "not_recorded" for row in rows)


def count_incomplete_management_decisions(rows: list[dict[str, str]]) -> int:
    if not rows:
        return 0

    if "decision_completeness_status" in rows[0]:
        return sum(
            1
            for row in rows
            if safe_get(row, "decision_completeness_status") != "DECISION_COMPLETE"
        )

    incomplete_count = 0

    for row in rows:
        decision = safe_get(row, "management_decision")

        if not decision or decision == "PENDING_DECISION":
            incomplete_count += 1
            continue

        required_fields = [
            "decision_owner",
            "decision_date",
            "decision_notes",
            "followup_required",
        ]

        if any(not safe_get(row, field) for field in required_fields):
            incomplete_count += 1

    return incomplete_count


def summarize_closeout(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = count_field(rows, "closeout_category")

    return {
        "closed_with_evidence": counts.get("CLOSED_WITH_EVIDENCE", 0),
        "closed_no_followup_required": counts.get("CLOSED_NO_FOLLOWUP_REQUIRED", 0),
        "closed_cancelled": counts.get("CLOSED_CANCELLED_WITH_RATIONALE", 0),
        "open_active": counts.get("OPEN_ACTIVE", 0),
        "open_blocked": counts.get("OPEN_BLOCKED", 0),
        "open_overdue": counts.get("OPEN_OVERDUE", 0),
        "review_required": counts.get("REVIEW_REQUIRED", 0),
    }


def determine_executive_attention(summary: dict[str, str]) -> str:
    artifact_health = summary["artifact_health"]
    evidence_system_status = summary["evidence_system_status"]
    closeout_status = summary["closeout_status"]

    if artifact_health in {"ARTIFACTS_MISSING", "ARTIFACTS_EMPTY"}:
        return "EXECUTIVE_ATTENTION_ARTIFACT_HEALTH"

    if int(summary["incomplete_management_decisions"]) > 0:
        return "EXECUTIVE_ATTENTION_INCOMPLETE_DECISIONS"

    if int(summary["closeout_review_required"]) > 0:
        return "EXECUTIVE_ATTENTION_CLOSEOUT_REVIEW"

    if int(summary["closeout_open_overdue"]) > 0:
        return "EXECUTIVE_ATTENTION_OVERDUE_FOLLOWUP"

    if int(summary["closeout_open_blocked"]) > 0:
        return "EXECUTIVE_ATTENTION_BLOCKED_FOLLOWUP"

    review_terms = [
        "REVIEW_REQUIRED",
        "MANAGEMENT_REVIEW_REQUIRED",
        "ACTION_REMAINS",
        "PENDING_HUMAN_REVIEW",
    ]

    if any(term in evidence_system_status for term in review_terms):
        return "EXECUTIVE_ATTENTION_SYSTEM_STATUS"

    if any(term in closeout_status for term in review_terms):
        return "EXECUTIVE_ATTENTION_CLOSEOUT_STATUS"

    if int(summary["closeout_open_active"]) > 0:
        return "EXECUTIVE_ACTIVE_ITEMS_TRACKED"

    return "EXECUTIVE_SUMMARY_STABLE"


def build_summary_row() -> dict[str, str]:
    corpus_rows = read_csv(CORPUS_MANIFEST)
    exception_rows = read_csv(TRACEABILITY_EXCEPTIONS)
    action_rows = read_csv(ACTION_PLAN)
    decision_rows = read_csv(MANAGEMENT_DECISIONS)
    followup_rows = read_csv(FOLLOWUP_TRACKER)
    closeout_rows = read_csv(CLOSEOUT_SUMMARY)

    closeout_counts = summarize_closeout(closeout_rows)

    artifact_health = extract_markdown_label(CONTROL_NARRATIVE_MD, "Artifact Health")
    evidence_system_status = extract_markdown_label(STATUS_DASHBOARD_MD, "Overall Status")
    closeout_status = extract_markdown_label(CLOSEOUT_MD, "Overall Status")

    row = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "executive_attention_status": "",
        "artifact_health": artifact_health,
        "evidence_system_status": evidence_system_status,
        "closeout_status": closeout_status,
        "corpus_records": str(len(corpus_rows)),
        "traceability_exception_rows": str(len(exception_rows)),
        "action_plan_rows": str(len(action_rows)),
        "management_decision_rows": str(len(decision_rows)),
        "incomplete_management_decisions": str(count_incomplete_management_decisions(decision_rows)),
        "followup_tracker_rows": str(len(followup_rows)),
        "closeout_rows": str(len(closeout_rows)),
        "closeout_closed_with_evidence": str(closeout_counts["closed_with_evidence"]),
        "closeout_closed_no_followup_required": str(closeout_counts["closed_no_followup_required"]),
        "closeout_closed_cancelled": str(closeout_counts["closed_cancelled"]),
        "closeout_open_active": str(closeout_counts["open_active"]),
        "closeout_open_blocked": str(closeout_counts["open_blocked"]),
        "closeout_open_overdue": str(closeout_counts["open_overdue"]),
        "closeout_review_required": str(closeout_counts["review_required"]),
    }

    row["executive_attention_status"] = determine_executive_attention(row)

    return row


def write_executive_markdown(summary: dict[str, str]) -> None:
    EXECUTIVE_MD.parent.mkdir(parents=True, exist_ok=True)

    attention = summary["executive_attention_status"]

    if attention == "EXECUTIVE_SUMMARY_STABLE":
        posture = "Green"
        posture_meaning = "The evidence workflow appears stable based on the executive summary inputs."
    elif attention == "EXECUTIVE_ACTIVE_ITEMS_TRACKED":
        posture = "Yellow"
        posture_meaning = "There is active follow-up work, but it is visible and tracked."
    else:
        posture = "Red / Review Required"
        posture_meaning = "One or more records, decisions, artifacts, or closeout items need attention."

    lines = [
        "# Security Evidence Executive Summary",
        "",
        f"Generated: `{summary['generated_at']}`",
        "",
        f"Executive Posture: **{posture}**",
        "",
        f"Executive Attention Status: **{attention}**",
        "",
        f"{posture_meaning}",
        "",
        "## Status Snapshot",
        "",
        "| Area | Status |",
        "|---|---|",
        f"| Artifact health | `{safe_cell(summary['artifact_health'])}` |",
        f"| Evidence system status | `{safe_cell(summary['evidence_system_status'])}` |",
        f"| Management closeout status | `{safe_cell(summary['closeout_status'])}` |",
        "",
        "## Key Counts",
        "",
        "| Measure | Count |",
        "|---|---:|",
        f"| Evidence corpus records | `{summary['corpus_records']}` |",
        f"| Traceability exception rows | `{summary['traceability_exception_rows']}` |",
        f"| Exception action plan rows | `{summary['action_plan_rows']}` |",
        f"| Management decision rows | `{summary['management_decision_rows']}` |",
        f"| Incomplete management decisions | `{summary['incomplete_management_decisions']}` |",
        f"| Follow-up tracker rows | `{summary['followup_tracker_rows']}` |",
        f"| Closeout rows | `{summary['closeout_rows']}` |",
        "",
        "## Closeout Posture",
        "",
        "| Closeout Category | Count |",
        "|---|---:|",
        f"| Closed with evidence | `{summary['closeout_closed_with_evidence']}` |",
        f"| Closed - no follow-up required | `{summary['closeout_closed_no_followup_required']}` |",
        f"| Closed - cancelled with rationale | `{summary['closeout_closed_cancelled']}` |",
        f"| Open active | `{summary['closeout_open_active']}` |",
        f"| Open blocked | `{summary['closeout_open_blocked']}` |",
        f"| Open overdue | `{summary['closeout_open_overdue']}` |",
        f"| Review required | `{summary['closeout_review_required']}` |",
        "",
        "## Executive Readout",
        "",
    ]

    if attention == "EXECUTIVE_SUMMARY_STABLE":
        lines.append("The evidence workflow has no executive-level attention items based on the current summary inputs.")
    elif attention == "EXECUTIVE_ACTIVE_ITEMS_TRACKED":
        lines.append("The evidence workflow has active follow-up items, but they are visible and tracked through the closeout workflow.")
    elif attention == "EXECUTIVE_ATTENTION_INCOMPLETE_DECISIONS":
        lines.append("Management decision records are incomplete. Complete the decision owner, date, notes, and follow-up requirement fields before treating follow-up as reliable.")
    elif attention == "EXECUTIVE_ATTENTION_CLOSEOUT_REVIEW":
        lines.append("Closeout records require review. Inspect the closeout summary and correct the underlying management decision or follow-up source records.")
    elif attention == "EXECUTIVE_ATTENTION_OVERDUE_FOLLOWUP":
        lines.append("At least one follow-up item is overdue. Management should reset the date, escalate the owner, or close the item with evidence.")
    elif attention == "EXECUTIVE_ATTENTION_BLOCKED_FOLLOWUP":
        lines.append("At least one follow-up item is blocked. Management review is needed to remove the blocker or accept the risk.")
    elif attention == "EXECUTIVE_ATTENTION_ARTIFACT_HEALTH":
        lines.append("One or more referenced artifacts are missing or empty. Regenerate the artifact chain before relying on the executive summary.")
    else:
        lines.append("The evidence system status indicates review is required. Inspect the status dashboard and closeout summary first.")

    lines.extend(
        [
            "",
            "## Read These First",
            "",
            "1. `docs/cloud/security_evidence_executive_summary.md`",
            "2. `docs/cloud/security_evidence_status_dashboard.md`",
            "3. `docs/cloud/security_evidence_management_closeout_summary.md`",
            "4. `docs/cloud/security_evidence_control_narrative.md`",
            "",
            "## Governance Rule",
            "",
            "> Executives do not need every artifact first. They need posture, attention items, ownership, and the path to evidence.",
            "",
            "## One-Sentence Takeaway",
            "",
            "> The executive summary turns the evidence system from a working prototype into a readable management posture.",
            "",
        ]
    )

    EXECUTIVE_MD.write_text("\n".join(lines), encoding="utf-8")


def write_report(summary: dict[str, str]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Security Evidence Executive Summary Report",
        "",
        f"Generated: `{summary['generated_at']}`",
        "",
        f"Overall Status: **{summary['executive_attention_status']}**",
        "",
        "## Generated Artifacts",
        "",
        f"- `{EXECUTIVE_CSV.as_posix()}`",
        f"- `{EXECUTIVE_MD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Input Artifact Health",
        "",
        "| Artifact | Status |",
        "|---|---|",
    ]

    for artifact in [
        STATUS_DASHBOARD_MD,
        CLOSEOUT_MD,
        CONTROL_NARRATIVE_MD,
        CORPUS_MANIFEST,
        TRACEABILITY_EXCEPTIONS,
        ACTION_PLAN,
        MANAGEMENT_DECISIONS,
        FOLLOWUP_TRACKER,
        CLOSEOUT_SUMMARY,
    ]:
        lines.append(f"| `{artifact.as_posix()}` | {artifact_status(artifact)} |")

    lines.extend(
        [
            "",
            "## One-Sentence Takeaway",
            "",
            "> The executive summary compresses the evidence workflow into posture, counts, and attention items.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    summary = build_summary_row()

    fieldnames = list(summary.keys())

    write_csv(EXECUTIVE_CSV, [summary], fieldnames)
    write_executive_markdown(summary)
    write_report(summary)

    print(f"Executive summary CSV written to: {EXECUTIVE_CSV}")
    print(f"Executive summary written to: {EXECUTIVE_MD}")
    print(f"Executive summary report written to: {REPORT_FILE}")
    print(f"Executive Attention Status: {summary['executive_attention_status']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())