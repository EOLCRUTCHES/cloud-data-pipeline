from pathlib import Path
from datetime import datetime, timezone
import csv
import sys


CLOSURE_REGISTER = Path("ai/security_evidence_gap_closure_register.csv")
REVIEWER_DECISIONS = Path("ai/security_evidence_reviewer_decisions.csv")
REVIEW_PACKET = Path("docs/cloud/security_evidence_human_review_packet.md")
REPORT_FILE = Path("evidence/generated/security_evidence_reviewer_decision_report.md")


DECISION_OPTIONS = [
    "PENDING_REVIEW",
    "CLOSE_GAP",
    "PARTIALLY_CLOSE_GAP",
    "KEEP_OPEN",
    "OUT_OF_SCOPE_ACCEPTED",
    "RETRIEVAL_TUNING_REQUIRED",
]


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


def existing_decision_map() -> dict[str, dict[str, str]]:
    rows = read_csv(REVIEWER_DECISIONS)
    return {row.get("closure_id", ""): row for row in rows if row.get("closure_id")}


def recommended_decision(closure_status: str) -> str:
    if closure_status == "CLOSURE_EVIDENCE_AVAILABLE_REVIEW_REQUIRED":
        return "CLOSE_GAP"

    if closure_status == "PARTIAL_CLOSURE_EVIDENCE_REVIEW_REQUIRED":
        return "PARTIALLY_CLOSE_GAP"

    if closure_status in {
        "GAP_OPEN_EVIDENCE_NEEDED",
        "GAP_REMAINS_RISK_OPEN",
        "GAP_REMAINS_EVIDENCE_INCOMPLETE",
    }:
        return "KEEP_OPEN"

    if closure_status == "RETRIEVAL_REVIEW_NEEDED":
        return "RETRIEVAL_TUNING_REQUIRED"

    if closure_status == "NOT_A_GAP_OUT_OF_SCOPE":
        return "OUT_OF_SCOPE_ACCEPTED"

    if closure_status == "NOT_A_GAP_SUPPORTED":
        return "CLOSE_GAP"

    return "PENDING_REVIEW"


def decision_rationale_hint(closure_status: str) -> str:
    if closure_status == "CLOSURE_EVIDENCE_AVAILABLE_REVIEW_REQUIRED":
        return "Closure evidence appears available; reviewer should verify before closing."

    if closure_status == "PARTIAL_CLOSURE_EVIDENCE_REVIEW_REQUIRED":
        return "Some evidence supports closure, but residual findings may remain."

    if closure_status == "GAP_OPEN_EVIDENCE_NEEDED":
        return "Gap remains open because matching evidence was not found."

    if closure_status == "GAP_REMAINS_RISK_OPEN":
        return "Gap remains open because evidence indicates risk remains."

    if closure_status == "GAP_REMAINS_EVIDENCE_INCOMPLETE":
        return "Gap remains open because evidence collection was incomplete."

    if closure_status == "RETRIEVAL_REVIEW_NEEDED":
        return "Retrieved evidence may be related but not sufficient; review retrieval quality."

    if closure_status == "NOT_A_GAP_OUT_OF_SCOPE":
        return "Question is outside approved scope unless the use case changes."

    if closure_status == "NOT_A_GAP_SUPPORTED":
        return "Question already appears source-supported."

    return "Reviewer judgment required."


def build_decision_rows(closure_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    existing = existing_decision_map()
    generated_at = datetime.now(timezone.utc).isoformat()

    if not closure_rows:
        return [
            {
                "review_id": "REV-000",
                "closure_id": "NO-CLOSURE-REGISTER",
                "candidate_id": "",
                "question": "No closure register available",
                "closure_status": "NO_CLOSURE_REGISTER",
                "closure_evidence": "",
                "recommended_decision": "PENDING_REVIEW",
                "reviewer_decision": "PENDING_REVIEW",
                "reviewer": "",
                "decision_date": "",
                "reviewer_notes": "Run src/close_security_evidence_gaps.py first.",
                "rationale_hint": "No closure register was available.",
                "generated_at": generated_at,
            }
        ]

    rows = []

    for index, closure_row in enumerate(closure_rows, start=1):
        closure_id = closure_row.get("closure_id", "")
        previous = existing.get(closure_id, {})
        closure_status = closure_row.get("closure_status", "")

        reviewer_decision = previous.get("reviewer_decision", "").strip() or "PENDING_REVIEW"
        reviewer = previous.get("reviewer", "").strip()
        decision_date = previous.get("decision_date", "").strip()
        reviewer_notes = previous.get("reviewer_notes", "").strip()

        rows.append(
            {
                "review_id": previous.get("review_id", "").strip() or f"REV-{index:03d}",
                "closure_id": closure_id,
                "candidate_id": closure_row.get("candidate_id", ""),
                "question": closure_row.get("question", ""),
                "closure_status": closure_status,
                "closure_evidence": closure_row.get("closure_evidence", ""),
                "recommended_decision": recommended_decision(closure_status),
                "reviewer_decision": reviewer_decision,
                "reviewer": reviewer,
                "decision_date": decision_date,
                "reviewer_notes": reviewer_notes,
                "rationale_hint": decision_rationale_hint(closure_status),
                "generated_at": generated_at,
            }
        )

    return rows


def summarize(rows: list[dict[str, str]]) -> dict[str, int]:
    summary = {
        "total": len(rows),
        "pending_review": 0,
        "close_gap": 0,
        "partially_close_gap": 0,
        "keep_open": 0,
        "out_of_scope_accepted": 0,
        "retrieval_tuning_required": 0,
        "invalid_decision": 0,
    }

    for row in rows:
        decision = row.get("reviewer_decision", "")

        if decision == "PENDING_REVIEW":
            summary["pending_review"] += 1
        elif decision == "CLOSE_GAP":
            summary["close_gap"] += 1
        elif decision == "PARTIALLY_CLOSE_GAP":
            summary["partially_close_gap"] += 1
        elif decision == "KEEP_OPEN":
            summary["keep_open"] += 1
        elif decision == "OUT_OF_SCOPE_ACCEPTED":
            summary["out_of_scope_accepted"] += 1
        elif decision == "RETRIEVAL_TUNING_REQUIRED":
            summary["retrieval_tuning_required"] += 1
        else:
            summary["invalid_decision"] += 1

    return summary


def determine_overall_status(summary: dict[str, int]) -> str:
    if summary["invalid_decision"] > 0:
        return "INVALID_REVIEW_DECISION"

    if summary["pending_review"] > 0:
        return "PENDING_HUMAN_REVIEW"

    if summary["keep_open"] > 0 or summary["retrieval_tuning_required"] > 0:
        return "REVIEW_COMPLETE_ACTION_REMAINS"

    return "REVIEW_COMPLETE"


def write_review_packet(rows: list[dict[str, str]]) -> None:
    REVIEW_PACKET.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    summary = summarize(rows)
    status = determine_overall_status(summary)

    lines = [
        "# Security Evidence Human Review Packet",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Review Status: **{status}**",
        "",
        "## Purpose",
        "",
        "This packet gives a human reviewer the evidence-gap closure items that need decision, acceptance, rejection, or follow-up.",
        "",
        "Automation can surface evidence, but it should not silently close governance gaps.",
        "",
        "## Allowed Reviewer Decisions",
        "",
        "| Decision | Meaning |",
        "|---|---|",
        "| `PENDING_REVIEW` | No human decision has been recorded yet. |",
        "| `CLOSE_GAP` | Reviewer accepts the closure evidence and closes the gap. |",
        "| `PARTIALLY_CLOSE_GAP` | Reviewer accepts partial closure but leaves residual work. |",
        "| `KEEP_OPEN` | Reviewer determines the evidence is insufficient or risk remains. |",
        "| `OUT_OF_SCOPE_ACCEPTED` | Reviewer accepts that the question is outside approved corpus scope. |",
        "| `RETRIEVAL_TUNING_REQUIRED` | Reviewer determines retrieval produced weak or misleading support. |",
        "",
        "## Review Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Review rows | `{summary['total']}` |",
        f"| Pending review | `{summary['pending_review']}` |",
        f"| Close gap | `{summary['close_gap']}` |",
        f"| Partially close gap | `{summary['partially_close_gap']}` |",
        f"| Keep open | `{summary['keep_open']}` |",
        f"| Retrieval tuning required | `{summary['retrieval_tuning_required']}` |",
        f"| Out of scope accepted | `{summary['out_of_scope_accepted']}` |",
        f"| Invalid decisions | `{summary['invalid_decision']}` |",
        "",
        "## Review Items",
        "",
        "| Review ID | Closure ID | Closure Status | Recommended | Reviewer Decision | Question |",
        "|---|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['review_id']} | "
            f"{row['closure_id']} | "
            f"`{row['closure_status']}` | "
            f"`{row['recommended_decision']}` | "
            f"**{row['reviewer_decision']}** | "
            f"{row['question']} |"
        )

    lines.extend(
        [
            "",
            "## How to Use",
            "",
            f"Edit `{REVIEWER_DECISIONS.as_posix()}` and update these fields:",
            "",
            "```text",
            "reviewer_decision",
            "reviewer",
            "decision_date",
            "reviewer_notes",
            "```",
            "",
            "Then rerun:",
            "",
            "```powershell",
            "python src\\generate_security_evidence_reviewer_decisions.py",
            "```",
            "",
            "## Governance Rule",
            "",
            "> A human reviewer closes the gap. Automation only prepares the decision record.",
            "",
        ]
    )

    REVIEW_PACKET.write_text("\n".join(lines), encoding="utf-8")


def write_report(rows: list[dict[str, str]]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    summary = summarize(rows)
    status = determine_overall_status(summary)

    lines = [
        "# Security Evidence Reviewer Decision Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{status}**",
        "",
        "## Purpose",
        "",
        "This report records the current human-review decision state for security evidence gap closure items.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Review rows | `{summary['total']}` |",
        f"| Pending review | `{summary['pending_review']}` |",
        f"| Closed gaps | `{summary['close_gap']}` |",
        f"| Partially closed gaps | `{summary['partially_close_gap']}` |",
        f"| Kept open | `{summary['keep_open']}` |",
        f"| Retrieval tuning required | `{summary['retrieval_tuning_required']}` |",
        f"| Out of scope accepted | `{summary['out_of_scope_accepted']}` |",
        f"| Invalid decisions | `{summary['invalid_decision']}` |",
        "",
        "## Decision Results",
        "",
        "| Review ID | Closure ID | Recommended | Reviewer Decision | Reviewer | Decision Date |",
        "|---|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['review_id']} | "
            f"{row['closure_id']} | "
            f"`{row['recommended_decision']}` | "
            f"**{row['reviewer_decision']}** | "
            f"{row['reviewer'] or 'not_recorded'} | "
            f"{row['decision_date'] or 'not_recorded'} |"
        )

    lines.extend(
        [
            "",
            "## Evidence Inputs",
            "",
            "| Artifact | Status |",
            "|---|---|",
            f"| `{CLOSURE_REGISTER.as_posix()}` | {artifact_status(CLOSURE_REGISTER)} |",
            f"| `{REVIEWER_DECISIONS.as_posix()}` | {artifact_status(REVIEWER_DECISIONS)} |",
            f"| `{REVIEW_PACKET.as_posix()}` | {artifact_status(REVIEW_PACKET)} |",
            "",
            "## Control Logic",
            "",
            "| Control Concept | Implementation |",
            "|---|---|",
            "| Human-in-the-loop governance | Reviewer decisions are required before closure is treated as complete. |",
            "| Decision traceability | Decisions preserve closure ID, question, evidence, reviewer, date, and notes. |",
            "| Safe automation | The script preserves prior reviewer decisions instead of overwriting them. |",
            "| Audit readiness | Outputs both machine-readable CSV and human-readable review packet. |",
            "",
            "## One-Sentence Takeaway",
            "",
            "> Human review converts closure evidence into an accountable governance decision.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def validate_decisions(rows: list[dict[str, str]]) -> list[str]:
    errors = []

    for row in rows:
        decision = row.get("reviewer_decision", "")

        if decision not in DECISION_OPTIONS:
            errors.append(
                f"{row.get('review_id', 'UNKNOWN')}: invalid reviewer_decision '{decision}'"
            )

    return errors


def main() -> int:
    closure_rows = read_csv(CLOSURE_REGISTER)
    decision_rows = build_decision_rows(closure_rows)
    validation_errors = validate_decisions(decision_rows)

    fieldnames = [
        "review_id",
        "closure_id",
        "candidate_id",
        "question",
        "closure_status",
        "closure_evidence",
        "recommended_decision",
        "reviewer_decision",
        "reviewer",
        "decision_date",
        "reviewer_notes",
        "rationale_hint",
        "generated_at",
    ]

    write_csv(REVIEWER_DECISIONS, decision_rows, fieldnames)
    write_review_packet(decision_rows)
    write_report(decision_rows)

    summary = summarize(decision_rows)
    status = determine_overall_status(summary)

    print(f"Reviewer decisions written to: {REVIEWER_DECISIONS}")
    print(f"Human review packet written to: {REVIEW_PACKET}")
    print(f"Reviewer decision report written to: {REPORT_FILE}")
    print(f"Review rows: {summary['total']}")
    print(f"Pending review: {summary['pending_review']}")
    print(f"Closed gaps: {summary['close_gap']}")
    print(f"Overall Status: {status}")

    if validation_errors:
        print("Validation errors:")
        for error in validation_errors:
            print(f"- {error}")

    return 0


if __name__ == "__main__":
    sys.exit(main())