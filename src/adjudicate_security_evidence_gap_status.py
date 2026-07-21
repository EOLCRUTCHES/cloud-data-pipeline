from pathlib import Path
from datetime import datetime, timezone
import csv
import re
import sys


REVIEWER_DECISIONS = Path("ai/security_evidence_reviewer_decisions.csv")

ADJUDICATED_STATUS = Path("ai/security_evidence_adjudicated_gap_status.csv")
ADJUDICATION_SUMMARY = Path("docs/cloud/security_evidence_adjudication_summary.md")
REPORT_FILE = Path("evidence/generated/security_evidence_adjudication_report.md")


ALLOWED_DECISIONS = {
    "PENDING_REVIEW",
    "CLOSE_GAP",
    "PARTIALLY_CLOSE_GAP",
    "KEEP_OPEN",
    "OUT_OF_SCOPE_ACCEPTED",
    "RETRIEVAL_TUNING_REQUIRED",
}


FINAL_STATUS_BY_DECISION = {
    "PENDING_REVIEW": "PENDING_HUMAN_REVIEW",
    "CLOSE_GAP": "CLOSED",
    "PARTIALLY_CLOSE_GAP": "PARTIALLY_CLOSED",
    "KEEP_OPEN": "OPEN",
    "OUT_OF_SCOPE_ACCEPTED": "OUT_OF_SCOPE_ACCEPTED",
    "RETRIEVAL_TUNING_REQUIRED": "RETRIEVAL_TUNING_REQUIRED",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []

    with path.open("r", encoding="utf-8", newline="") as file:
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


def decision_is_complete(row: dict[str, str]) -> bool:
    decision = row.get("reviewer_decision", "").strip()

    if decision == "PENDING_REVIEW":
        return True

    reviewer = row.get("reviewer", "").strip()
    decision_date = row.get("decision_date", "").strip()
    reviewer_notes = row.get("reviewer_notes", "").strip()

    return bool(reviewer) and valid_decision_date(decision_date) and bool(reviewer_notes)


def final_status_for_row(row: dict[str, str]) -> str:
    decision = row.get("reviewer_decision", "").strip()

    if decision not in ALLOWED_DECISIONS:
        return "INVALID_REVIEWER_DECISION"

    if not decision_is_complete(row):
        return "REVIEW_DECISION_INCOMPLETE"

    return FINAL_STATUS_BY_DECISION[decision]


def action_required_for_status(final_status: str) -> str:
    actions = {
        "PENDING_HUMAN_REVIEW": "Reviewer decision required.",
        "CLOSED": "No further gap action required; retain closure evidence and decision record.",
        "PARTIALLY_CLOSED": "Track residual work and create follow-up evidence request if needed.",
        "OPEN": "Collect missing evidence or remediate remaining risk.",
        "OUT_OF_SCOPE_ACCEPTED": "No evidence action required unless this question becomes an approved use case.",
        "RETRIEVAL_TUNING_REQUIRED": "Review retrieval logic, thresholds, source matching, or test case classification.",
        "INVALID_REVIEWER_DECISION": "Correct reviewer_decision to an allowed value.",
        "REVIEW_DECISION_INCOMPLETE": "Complete reviewer, decision_date, and reviewer_notes.",
    }

    return actions.get(final_status, "Review manually.")


def build_adjudicated_rows(review_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    generated_at = datetime.now(timezone.utc).isoformat()

    if not review_rows:
        return [
            {
                "adjudication_id": "ADJ-000",
                "review_id": "",
                "closure_id": "",
                "candidate_id": "",
                "question": "No reviewer decision log available",
                "closure_status": "NO_REVIEWER_DECISIONS",
                "recommended_decision": "",
                "reviewer_decision": "",
                "final_gap_status": "REVIEW_REQUIRED",
                "closure_evidence": "",
                "reviewer": "",
                "decision_date": "",
                "reviewer_notes": "Run src/generate_security_evidence_reviewer_decisions.py first.",
                "action_required": "Generate reviewer decision log.",
                "generated_at": generated_at,
            }
        ]

    adjudicated_rows = []

    for index, row in enumerate(review_rows, start=1):
        final_status = final_status_for_row(row)

        adjudicated_rows.append(
            {
                "adjudication_id": f"ADJ-{index:03d}",
                "review_id": row.get("review_id", ""),
                "closure_id": row.get("closure_id", ""),
                "candidate_id": row.get("candidate_id", ""),
                "question": row.get("question", ""),
                "closure_status": row.get("closure_status", ""),
                "recommended_decision": row.get("recommended_decision", ""),
                "reviewer_decision": row.get("reviewer_decision", ""),
                "final_gap_status": final_status,
                "closure_evidence": row.get("closure_evidence", ""),
                "reviewer": row.get("reviewer", ""),
                "decision_date": row.get("decision_date", ""),
                "reviewer_notes": row.get("reviewer_notes", ""),
                "action_required": action_required_for_status(final_status),
                "generated_at": generated_at,
            }
        )

    return adjudicated_rows


def summarize(rows: list[dict[str, str]]) -> dict[str, int]:
    summary = {
        "total": len(rows),
        "closed": 0,
        "partially_closed": 0,
        "open": 0,
        "pending_review": 0,
        "out_of_scope_accepted": 0,
        "retrieval_tuning_required": 0,
        "incomplete_decisions": 0,
        "invalid_decisions": 0,
        "other_review": 0,
    }

    for row in rows:
        status = row.get("final_gap_status", "")

        if status == "CLOSED":
            summary["closed"] += 1
        elif status == "PARTIALLY_CLOSED":
            summary["partially_closed"] += 1
        elif status == "OPEN":
            summary["open"] += 1
        elif status == "PENDING_HUMAN_REVIEW":
            summary["pending_review"] += 1
        elif status == "OUT_OF_SCOPE_ACCEPTED":
            summary["out_of_scope_accepted"] += 1
        elif status == "RETRIEVAL_TUNING_REQUIRED":
            summary["retrieval_tuning_required"] += 1
        elif status == "REVIEW_DECISION_INCOMPLETE":
            summary["incomplete_decisions"] += 1
        elif status == "INVALID_REVIEWER_DECISION":
            summary["invalid_decisions"] += 1
        else:
            summary["other_review"] += 1

    return summary


def determine_overall_status(summary: dict[str, int]) -> str:
    if summary["invalid_decisions"] > 0:
        return "INVALID_DECISIONS"

    if summary["incomplete_decisions"] > 0:
        return "INCOMPLETE_REVIEW_DECISIONS"

    if summary["pending_review"] > 0:
        return "PENDING_HUMAN_REVIEW"

    if summary["open"] > 0 or summary["retrieval_tuning_required"] > 0:
        return "ACTION_REMAINS"

    if summary["partially_closed"] > 0:
        return "PARTIAL_CLOSURE_RECORDED"

    return "ADJUDICATION_COMPLETE"


def safe_cell(value: str) -> str:
    return str(value).replace("|", " ").replace("\n", " ").strip()


def write_summary(rows: list[dict[str, str]]) -> None:
    ADJUDICATION_SUMMARY.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    summary = summarize(rows)
    overall_status = determine_overall_status(summary)

    lines = [
        "# Security Evidence Adjudication Summary",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Adjudication Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This summary shows the final adjudicated status of evidence gaps after human review decisions are applied.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Adjudicated rows | `{summary['total']}` |",
        f"| Closed | `{summary['closed']}` |",
        f"| Partially closed | `{summary['partially_closed']}` |",
        f"| Open | `{summary['open']}` |",
        f"| Pending human review | `{summary['pending_review']}` |",
        f"| Out of scope accepted | `{summary['out_of_scope_accepted']}` |",
        f"| Retrieval tuning required | `{summary['retrieval_tuning_required']}` |",
        f"| Incomplete decisions | `{summary['incomplete_decisions']}` |",
        f"| Invalid decisions | `{summary['invalid_decisions']}` |",
        "",
        "## Adjudicated Results",
        "",
        "| ID | Review | Final Status | Reviewer Decision | Action Required |",
        "|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {safe_cell(row['adjudication_id'])} | "
            f"{safe_cell(row['review_id'])} | "
            f"**{safe_cell(row['final_gap_status'])}** | "
            f"`{safe_cell(row['reviewer_decision'])}` | "
            f"{safe_cell(row['action_required'])} |"
        )

    lines.extend(
        [
            "",
            "## Governance Rule",
            "",
            "> Reviewer decisions must be visible, complete, and tied to closure evidence before a gap is considered closed.",
            "",
            "## Decision Completeness Rule",
            "",
            "Any non-pending reviewer decision should include:",
            "",
            "- `reviewer`",
            "- `decision_date` in `YYYY-MM-DD` format",
            "- `reviewer_notes`",
            "",
        ]
    )

    ADJUDICATION_SUMMARY.write_text("\n".join(lines), encoding="utf-8")


def write_report(rows: list[dict[str, str]]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    summary = summarize(rows)
    overall_status = determine_overall_status(summary)

    lines = [
        "# Security Evidence Adjudication Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report records adjudication of security evidence gaps based on human reviewer decisions.",
        "",
        "## Evidence Input",
        "",
        "| Artifact | Status |",
        "|---|---|",
        f"| `{REVIEWER_DECISIONS.as_posix()}` | {artifact_status(REVIEWER_DECISIONS)} |",
        "",
        "## Generated Artifacts",
        "",
        f"- `{ADJUDICATED_STATUS.as_posix()}`",
        f"- `{ADJUDICATION_SUMMARY.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Status Counts",
        "",
        "| Final Status Category | Count |",
        "|---|---:|",
        f"| Closed | `{summary['closed']}` |",
        f"| Partially closed | `{summary['partially_closed']}` |",
        f"| Open | `{summary['open']}` |",
        f"| Pending human review | `{summary['pending_review']}` |",
        f"| Out of scope accepted | `{summary['out_of_scope_accepted']}` |",
        f"| Retrieval tuning required | `{summary['retrieval_tuning_required']}` |",
        f"| Incomplete decisions | `{summary['incomplete_decisions']}` |",
        f"| Invalid decisions | `{summary['invalid_decisions']}` |",
        "",
        "## Control Logic",
        "",
        "| Control Concept | Implementation |",
        "|---|---|",
        "| Human accountability | Final status is derived from reviewer decisions, not automation alone. |",
        "| Decision completeness | Non-pending decisions require reviewer, date, and notes. |",
        "| Closure discipline | Closed, open, partial, pending, and out-of-scope statuses are separated. |",
        "| Audit readiness | Machine-readable and human-readable adjudication artifacts are generated. |",
        "",
        "## One-Sentence Takeaway",
        "",
        "> Adjudication converts human review decisions into final, auditable evidence-gap status.",
        "",
    ]

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    review_rows = read_csv(REVIEWER_DECISIONS)
    adjudicated_rows = build_adjudicated_rows(review_rows)

    fieldnames = [
        "adjudication_id",
        "review_id",
        "closure_id",
        "candidate_id",
        "question",
        "closure_status",
        "recommended_decision",
        "reviewer_decision",
        "final_gap_status",
        "closure_evidence",
        "reviewer",
        "decision_date",
        "reviewer_notes",
        "action_required",
        "generated_at",
    ]

    write_csv(ADJUDICATED_STATUS, adjudicated_rows, fieldnames)
    write_summary(adjudicated_rows)
    write_report(adjudicated_rows)

    summary = summarize(adjudicated_rows)
    overall_status = determine_overall_status(summary)

    print(f"Adjudicated status written to: {ADJUDICATED_STATUS}")
    print(f"Adjudication summary written to: {ADJUDICATION_SUMMARY}")
    print(f"Adjudication report written to: {REPORT_FILE}")
    print(f"Closed: {summary['closed']}")
    print(f"Open: {summary['open']}")
    print(f"Pending human review: {summary['pending_review']}")
    print(f"Overall Status: {overall_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())