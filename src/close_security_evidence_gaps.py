from pathlib import Path
from datetime import datetime, timezone
import csv
import sys


GAP_REGISTER = Path("ai/security_evidence_gap_register.csv")
REMEDIATION_REGISTER = Path("security/aws_admin_port_remediation_register.csv")
REMEDIATION_RECORD = Path("docs/cloud/aws_admin_port_remediation_record.md")

CLOSURE_REGISTER = Path("ai/security_evidence_gap_closure_register.csv")
CLOSURE_PLAYBOOK = Path("docs/cloud/security_evidence_gap_closure_playbook.md")
REPORT_FILE = Path("evidence/generated/security_evidence_gap_closure_report.md")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []

    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def artifact_status(path: Path) -> str:
    if path.exists() and path.stat().st_size > 0:
        return "Present"
    if path.exists() and path.stat().st_size == 0:
        return "Empty"
    return "Missing"


def remediation_closure_signal(remediation_rows: list[dict[str, str]]) -> dict[str, str]:
    if not remediation_rows:
        return {
            "signal": "NO_REMEDIATION_EVIDENCE",
            "closure_evidence": "",
            "interpretation": "No remediation register was available.",
        }

    row = remediation_rows[0]
    closure_status = row.get("closure_status", "")

    if closure_status == "PUBLIC_ADMIN_EXPOSURE_CLEARED_PENDING_REVIEW":
        return {
            "signal": "CLOSURE_EVIDENCE_AVAILABLE_REVIEW_REQUIRED",
            "closure_evidence": f"{REMEDIATION_REGISTER.as_posix()} | {REMEDIATION_RECORD.as_posix()}",
            "interpretation": "Post-remediation evidence indicates public admin exposure was cleared, pending human review.",
        }

    if closure_status == "PUBLIC_EXPOSURE_CLEARED_REVIEW_REMAINS":
        return {
            "signal": "PARTIAL_CLOSURE_EVIDENCE_REVIEW_REQUIRED",
            "closure_evidence": f"{REMEDIATION_REGISTER.as_posix()} | {REMEDIATION_RECORD.as_posix()}",
            "interpretation": "High public exposure appears cleared, but medium or review findings remain.",
        }

    if closure_status == "REVIEW_REQUIRED_PUBLIC_EXPOSURE_REMAINS":
        return {
            "signal": "GAP_REMAINS_RISK_OPEN",
            "closure_evidence": f"{REMEDIATION_REGISTER.as_posix()} | {REMEDIATION_RECORD.as_posix()}",
            "interpretation": "Post-remediation evidence still shows high-severity public admin exposure.",
        }

    if closure_status == "EVIDENCE_INCOMPLETE_COLLECTOR_NOT_RUN":
        return {
            "signal": "GAP_REMAINS_EVIDENCE_INCOMPLETE",
            "closure_evidence": f"{REMEDIATION_REGISTER.as_posix()} | {REMEDIATION_RECORD.as_posix()}",
            "interpretation": "The collector did not run, so remediation closure evidence is incomplete.",
        }

    return {
        "signal": "REMEDIATION_REVIEW_REQUIRED",
        "closure_evidence": f"{REMEDIATION_REGISTER.as_posix()} | {REMEDIATION_RECORD.as_posix()}",
        "interpretation": f"Remediation register exists with closure status: {closure_status or 'not_present'}",
    }


def is_admin_port_remediation_gap(row: dict[str, str]) -> bool:
    question = row.get("question", "").lower()
    needed = row.get("needed_evidence_if_gap", "").lower()
    combined = f"{question} {needed}"

    indicators = [
        "admin-port",
        "admin port",
        "ec2 public",
        "public admin",
        "remediated",
        "remediation",
        "security group",
    ]

    return any(indicator in combined for indicator in indicators)


def classify_gap_closure(
    gap_row: dict[str, str],
    remediation_signal: dict[str, str],
) -> dict[str, str]:
    gap_status = gap_row.get("gap_status", "UNKNOWN")

    if gap_status == "SUPPORTED":
        return {
            "closure_status": "NOT_A_GAP_SUPPORTED",
            "closure_evidence": gap_row.get("source_ids", ""),
            "closure_interpretation": "The candidate was already supported by source-backed evidence.",
            "recommended_reviewer_action": "No closure action required.",
        }

    if gap_status == "OUT_OF_SCOPE_CONFIRMED":
        return {
            "closure_status": "NOT_A_GAP_OUT_OF_SCOPE",
            "closure_evidence": "",
            "closure_interpretation": "The candidate was correctly treated as outside the approved corpus scope.",
            "recommended_reviewer_action": "No closure action required unless this becomes an approved use case.",
        }

    if is_admin_port_remediation_gap(gap_row):
        signal = remediation_signal["signal"]

        if signal in {
            "CLOSURE_EVIDENCE_AVAILABLE_REVIEW_REQUIRED",
            "PARTIAL_CLOSURE_EVIDENCE_REVIEW_REQUIRED",
            "GAP_REMAINS_RISK_OPEN",
            "GAP_REMAINS_EVIDENCE_INCOMPLETE",
            "REMEDIATION_REVIEW_REQUIRED",
        }:
            return {
                "closure_status": signal,
                "closure_evidence": remediation_signal["closure_evidence"],
                "closure_interpretation": remediation_signal["interpretation"],
                "recommended_reviewer_action": "Review the remediation record and decide whether the gap can be closed, partially closed, or must remain open.",
            }

    if gap_status in {"EVIDENCE_GAP", "GAP_CONFIRMED"}:
        return {
            "closure_status": "GAP_OPEN_EVIDENCE_NEEDED",
            "closure_evidence": "",
            "closure_interpretation": "The gap remains open because no matching closure evidence was found.",
            "recommended_reviewer_action": "Collect the missing evidence, rebuild the corpus, rerun the gap register, and rerun closure.",
        }

    if gap_status in {"BOUNDARY_REVIEW", "POSSIBLE_FALSE_POSITIVE_REVIEW"}:
        return {
            "closure_status": "RETRIEVAL_REVIEW_NEEDED",
            "closure_evidence": gap_row.get("source_ids", ""),
            "closure_interpretation": "The answer layer returned related sources, but retrieval quality or evidence sufficiency needs review.",
            "recommended_reviewer_action": "Review whether the sources truly answer the question or whether retrieval thresholds need tightening.",
        }

    return {
        "closure_status": "REVIEW",
        "closure_evidence": "",
        "closure_interpretation": f"Unhandled gap status: {gap_status}",
        "recommended_reviewer_action": "Review manually.",
    }


def build_closure_rows(
    gap_rows: list[dict[str, str]],
    remediation_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    remediation_signal = remediation_closure_signal(remediation_rows)
    generated_at = datetime.now(timezone.utc).isoformat()

    closure_rows = []

    if not gap_rows:
        closure_rows.append(
            {
                "closure_id": "GAP-CLOSE-000",
                "candidate_id": "NO-GAP-REGISTER",
                "question": "No gap register available",
                "original_gap_status": "NO_GAP_REGISTER",
                "closure_status": "REVIEW",
                "closure_evidence": "",
                "closure_interpretation": "No gap register was available to reconcile.",
                "recommended_reviewer_action": "Run src/generate_security_evidence_gap_register.py first.",
                "generated_at": generated_at,
            }
        )
        return closure_rows

    for index, gap_row in enumerate(gap_rows, start=1):
        closure = classify_gap_closure(
            gap_row=gap_row,
            remediation_signal=remediation_signal,
        )

        closure_rows.append(
            {
                "closure_id": f"GAP-CLOSE-{index:03d}",
                "candidate_id": gap_row.get("candidate_id", ""),
                "question": gap_row.get("question", ""),
                "original_gap_status": gap_row.get("gap_status", ""),
                "closure_status": closure["closure_status"],
                "closure_evidence": closure["closure_evidence"],
                "closure_interpretation": closure["closure_interpretation"],
                "recommended_reviewer_action": closure["recommended_reviewer_action"],
                "generated_at": generated_at,
            }
        )

    return closure_rows


def write_closure_register(rows: list[dict[str, str]]) -> None:
    CLOSURE_REGISTER.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "closure_id",
        "candidate_id",
        "question",
        "original_gap_status",
        "closure_status",
        "closure_evidence",
        "closure_interpretation",
        "recommended_reviewer_action",
        "generated_at",
    ]

    with CLOSURE_REGISTER.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, str]]) -> dict[str, int]:
    summary = {
        "total": len(rows),
        "closure_evidence_available": 0,
        "partial_closure_review": 0,
        "open_gaps": 0,
        "retrieval_reviews": 0,
        "not_gaps": 0,
        "other_review": 0,
    }

    for row in rows:
        status = row["closure_status"]

        if status == "CLOSURE_EVIDENCE_AVAILABLE_REVIEW_REQUIRED":
            summary["closure_evidence_available"] += 1
        elif status == "PARTIAL_CLOSURE_EVIDENCE_REVIEW_REQUIRED":
            summary["partial_closure_review"] += 1
        elif status in {
            "GAP_OPEN_EVIDENCE_NEEDED",
            "GAP_REMAINS_RISK_OPEN",
            "GAP_REMAINS_EVIDENCE_INCOMPLETE",
            "NO_REMEDIATION_EVIDENCE",
        }:
            summary["open_gaps"] += 1
        elif status == "RETRIEVAL_REVIEW_NEEDED":
            summary["retrieval_reviews"] += 1
        elif status in {"NOT_A_GAP_SUPPORTED", "NOT_A_GAP_OUT_OF_SCOPE"}:
            summary["not_gaps"] += 1
        else:
            summary["other_review"] += 1

    return summary


def determine_overall_status(summary: dict[str, int]) -> str:
    if summary["open_gaps"] > 0:
        return "OPEN_GAPS_REMAIN"

    if summary["closure_evidence_available"] > 0 or summary["partial_closure_review"] > 0:
        return "CLOSURE_REVIEW_REQUIRED"

    if summary["retrieval_reviews"] > 0 or summary["other_review"] > 0:
        return "REVIEW_REQUIRED"

    return "PASS"


def write_playbook() -> None:
    CLOSURE_PLAYBOOK.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Security Evidence Gap Closure Playbook",
        "",
        "## Purpose",
        "",
        "This playbook defines how evidence gaps move from open status to closure review.",
        "",
        "## Gap Lifecycle",
        "",
        "```text",
        "Question asked",
        "↓",
        "Corpus searched",
        "↓",
        "No sufficient source found",
        "↓",
        "Evidence gap registered",
        "↓",
        "New evidence collected or generated",
        "↓",
        "Corpus rebuilt",
        "↓",
        "Gap register rerun",
        "↓",
        "Closure register generated",
        "↓",
        "Human reviewer closes, partially closes, or keeps gap open",
        "```",
        "",
        "## Closure Rules",
        "",
        "| Status | Meaning |",
        "|---|---|",
        "| `CLOSURE_EVIDENCE_AVAILABLE_REVIEW_REQUIRED` | Evidence exists that may close the gap, but reviewer approval is required. |",
        "| `PARTIAL_CLOSURE_EVIDENCE_REVIEW_REQUIRED` | Evidence addresses part of the gap, but residual findings remain. |",
        "| `GAP_OPEN_EVIDENCE_NEEDED` | No matching closure evidence exists yet. |",
        "| `GAP_REMAINS_RISK_OPEN` | Evidence shows the risk still exists. |",
        "| `GAP_REMAINS_EVIDENCE_INCOMPLETE` | The evidence workflow did not run completely. |",
        "| `RETRIEVAL_REVIEW_NEEDED` | The answer layer found related sources, but relevance or sufficiency needs review. |",
        "",
        "## Governance Rule",
        "",
        "> New evidence does not automatically close a gap. It creates a closure-review event.",
        "",
    ]

    CLOSURE_PLAYBOOK.write_text("\n".join(lines), encoding="utf-8")


def write_report(rows: list[dict[str, str]]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    summary = summarize(rows)
    overall_status = determine_overall_status(summary)

    lines = [
        "# Security Evidence Gap Closure Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report reconciles evidence gap register entries against available closure evidence.",
        "",
        "It does not automatically close gaps. It identifies which gaps have closure evidence available for human review.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Closure rows evaluated | `{summary['total']}` |",
        f"| Closure evidence available | `{summary['closure_evidence_available']}` |",
        f"| Partial closure reviews | `{summary['partial_closure_review']}` |",
        f"| Open gaps | `{summary['open_gaps']}` |",
        f"| Retrieval reviews | `{summary['retrieval_reviews']}` |",
        f"| Not gaps | `{summary['not_gaps']}` |",
        f"| Other review | `{summary['other_review']}` |",
        "",
        "## Closure Register Results",
        "",
        "| Closure ID | Candidate | Original Gap Status | Closure Status | Reviewer Action |",
        "|---|---|---|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['closure_id']} | "
            f"{row['candidate_id']} | "
            f"`{row['original_gap_status']}` | "
            f"**{row['closure_status']}** | "
            f"{row['recommended_reviewer_action']} |"
        )

    lines.extend(
        [
            "",
            "## Evidence Inputs",
            "",
            "| Artifact | Status |",
            "|---|---|",
            f"| `{GAP_REGISTER.as_posix()}` | {artifact_status(GAP_REGISTER)} |",
            f"| `{REMEDIATION_REGISTER.as_posix()}` | {artifact_status(REMEDIATION_REGISTER)} |",
            f"| `{REMEDIATION_RECORD.as_posix()}` | {artifact_status(REMEDIATION_RECORD)} |",
            f"| `{CLOSURE_REGISTER.as_posix()}` | {artifact_status(CLOSURE_REGISTER)} |",
            f"| `{CLOSURE_PLAYBOOK.as_posix()}` | {artifact_status(CLOSURE_PLAYBOOK)} |",
            "",
            "## Control Logic",
            "",
            "| Control Concept | Implementation |",
            "|---|---|",
            "| Evidence gap lifecycle | Gap entries are reconciled against new closure evidence. |",
            "| Human review | Closure evidence is marked review-required instead of auto-closing. |",
            "| Traceability | Closure rows preserve candidate ID, question, original status, evidence, and reviewer action. |",
            "| Safe failure | Open gaps remain open when evidence is missing, incomplete, or shows risk remains. |",
            "",
            "## One-Sentence Takeaway",
            "",
            "> Evidence gaps close through reviewable closure evidence, not optimism.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    gap_rows = read_csv(GAP_REGISTER)
    remediation_rows = read_csv(REMEDIATION_REGISTER)

    closure_rows = build_closure_rows(
        gap_rows=gap_rows,
        remediation_rows=remediation_rows,
    )

    write_closure_register(closure_rows)
    write_playbook()
    write_report(closure_rows)

    summary = summarize(closure_rows)
    overall_status = determine_overall_status(summary)

    print(f"Closure register written to: {CLOSURE_REGISTER}")
    print(f"Closure playbook written to: {CLOSURE_PLAYBOOK}")
    print(f"Closure report written to: {REPORT_FILE}")
    print(f"Closure evidence available: {summary['closure_evidence_available']}")
    print(f"Open gaps: {summary['open_gaps']}")
    print(f"Retrieval reviews: {summary['retrieval_reviews']}")
    print(f"Overall Status: {overall_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())