from pathlib import Path
from datetime import datetime, timezone
import csv
import re
import subprocess
import sys


ANSWER_SCRIPT = Path("src/answer_security_evidence_question.py")
ANSWER_FILE = Path("ai/security_evidence_answer.md")
ANSWER_SOURCES_CSV = Path("ai/security_evidence_answer_sources.csv")

GAP_CANDIDATES_CSV = Path("ai/security_evidence_gap_candidates.csv")
GAP_REGISTER_CSV = Path("ai/security_evidence_gap_register.csv")
REPORT_FILE = Path("evidence/generated/security_evidence_gap_report.md")


DEFAULT_GAP_CANDIDATES = [
    {
        "candidate_id": "GAP-CAND-001",
        "question": "What evidence supports the AWS cloud administrative access standard?",
        "expected_disposition": "should_be_answerable",
        "business_reason": "The local corpus should contain the ADR, access playbook, permission preflight, and workflow package.",
        "needed_evidence_if_gap": "Cloud admin access ADR, evidence playbook, permission preflight report, and workflow evidence package.",
    },
    {
        "candidate_id": "GAP-CAND-002",
        "question": "What evidence shows admin port exposure was reviewed?",
        "expected_disposition": "should_be_answerable",
        "business_reason": "The local corpus should include the admin-port exposure collector and related workflow package.",
        "needed_evidence_if_gap": "Admin-port exposure report, security group findings CSV, and workflow report.",
    },
    {
        "candidate_id": "GAP-CAND-003",
        "question": "What evidence proves the EC2 public admin-port rule was remediated?",
        "expected_disposition": "should_be_gap",
        "business_reason": "The project may show current exposure status, but a remediation proof should require before/after evidence or a documented remediation record.",
        "needed_evidence_if_gap": "Before finding, remediation action record, after-scan result, timestamp, owner, and exception/risk closure note.",
    },
    {
        "candidate_id": "GAP-CAND-004",
        "question": "What is the best firewall vendor for my company?",
        "expected_disposition": "out_of_scope",
        "business_reason": "Vendor selection is not part of the approved local evidence corpus.",
        "needed_evidence_if_gap": "Approved vendor requirements, evaluation criteria, product shortlist, cost constraints, and security architecture context.",
    },
    {
        "candidate_id": "GAP-CAND-005",
        "question": "What is the current USD to EUR exchange rate?",
        "expected_disposition": "out_of_scope",
        "business_reason": "Current exchange rates are external time-sensitive facts and should not be answered from the local security evidence corpus.",
        "needed_evidence_if_gap": "External trusted financial data source, retrieval timestamp, and explicit approval to use that source.",
    },
]


def write_default_candidates_if_missing() -> None:
    """Create default gap candidate cases if missing."""
    GAP_CANDIDATES_CSV.parent.mkdir(parents=True, exist_ok=True)

    if GAP_CANDIDATES_CSV.exists() and GAP_CANDIDATES_CSV.stat().st_size > 0:
        return

    fieldnames = [
        "candidate_id",
        "question",
        "expected_disposition",
        "business_reason",
        "needed_evidence_if_gap",
    ]

    with GAP_CANDIDATES_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(DEFAULT_GAP_CANDIDATES)


def load_gap_candidates() -> list[dict[str, str]]:
    """Load gap candidate questions."""
    write_default_candidates_if_missing()

    with GAP_CANDIDATES_CSV.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def run_answer_script(question: str) -> dict[str, str]:
    """Run answer script for one question."""
    if not ANSWER_SCRIPT.exists():
        return {
            "return_code": "not_run",
            "stdout": "",
            "stderr": f"Missing answer script: {ANSWER_SCRIPT}",
        }

    result = subprocess.run(
        [
            sys.executable,
            ANSWER_SCRIPT.as_posix(),
            question,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    return {
        "return_code": str(result.returncode),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def parse_answer_status() -> str:
    """Parse answer status from generated answer file."""
    if not ANSWER_FILE.exists() or ANSWER_FILE.stat().st_size == 0:
        return "ANSWER_FILE_MISSING"

    text = ANSWER_FILE.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"Answer Status:\s+\*\*(.*?)\*\*", text)

    if match:
        return match.group(1).strip()

    return "ANSWER_STATUS_NOT_FOUND"


def load_answer_sources() -> list[dict[str, str]]:
    """Load answer source records."""
    if not ANSWER_SOURCES_CSV.exists() or ANSWER_SOURCES_CSV.stat().st_size == 0:
        return []

    with ANSWER_SOURCES_CSV.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def classify_gap_status(expected_disposition: str, answer_status: str, source_count: int) -> tuple[str, str]:
    """Classify whether the result is supported, a gap, out-of-scope, or a false-positive risk."""
    source_backed = answer_status == "SOURCE_BACKED_REVIEW_REQUIRED" and source_count > 0
    insufficient = answer_status in {"INSUFFICIENT_EVIDENCE", "NO_CORPUS"} or source_count == 0

    if expected_disposition == "should_be_answerable":
        if source_backed:
            return "SUPPORTED", "Expected answerable question returned source-backed evidence."
        return "EVIDENCE_GAP", "Expected answerable question did not return sufficient corpus evidence."

    if expected_disposition == "should_be_gap":
        if insufficient:
            return "GAP_CONFIRMED", "Question correctly exposed a missing evidence requirement."
        return "POSSIBLE_FALSE_POSITIVE_REVIEW", "Question returned sources, but expected disposition says stronger evidence may be required."

    if expected_disposition == "out_of_scope":
        if insufficient:
            return "OUT_OF_SCOPE_CONFIRMED", "Question correctly avoided a confident answer outside the approved corpus."
        return "BOUNDARY_REVIEW", "Question returned sources even though the question is expected to be out-of-scope."

    return "REVIEW", "Unknown expected disposition."


def source_ids_from_sources(sources: list[dict[str, str]]) -> str:
    """Return compact source ID list."""
    ids = []

    for source in sources:
        document_id = source.get("document_id", "").strip()
        if document_id and document_id not in ids:
            ids.append(document_id)

    return ", ".join(ids)


def evaluate_candidate(candidate: dict[str, str]) -> dict[str, str]:
    """Evaluate one candidate question and create a gap-register row."""
    run_result = run_answer_script(candidate["question"])
    answer_status = parse_answer_status()
    sources = load_answer_sources()
    source_count = len(sources)

    gap_status, interpretation = classify_gap_status(
        expected_disposition=candidate["expected_disposition"],
        answer_status=answer_status,
        source_count=source_count,
    )

    if gap_status in {"EVIDENCE_GAP", "GAP_CONFIRMED"}:
        recommended_action = "Collect or create the missing evidence, then rebuild the corpus and rerun retrieval."
    elif gap_status in {"POSSIBLE_FALSE_POSITIVE_REVIEW", "BOUNDARY_REVIEW"}:
        recommended_action = "Review retrieval quality and tighten answer-layer thresholds or source classification."
    elif gap_status == "SUPPORTED":
        recommended_action = "No gap action required; retain source-backed result for review."
    elif gap_status == "OUT_OF_SCOPE_CONFIRMED":
        recommended_action = "No corpus action required unless this question becomes an approved use case."
    else:
        recommended_action = "Review manually."

    return {
        "candidate_id": candidate["candidate_id"],
        "question": candidate["question"],
        "expected_disposition": candidate["expected_disposition"],
        "answer_status": answer_status,
        "source_count": str(source_count),
        "source_ids": source_ids_from_sources(sources),
        "gap_status": gap_status,
        "business_reason": candidate["business_reason"],
        "needed_evidence_if_gap": candidate["needed_evidence_if_gap"],
        "interpretation": interpretation,
        "recommended_action": recommended_action,
        "return_code": run_result["return_code"],
        "stderr": run_result["stderr"],
    }


def write_gap_register(rows: list[dict[str, str]]) -> None:
    """Write gap register CSV."""
    GAP_REGISTER_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "candidate_id",
        "question",
        "expected_disposition",
        "answer_status",
        "source_count",
        "source_ids",
        "gap_status",
        "business_reason",
        "needed_evidence_if_gap",
        "interpretation",
        "recommended_action",
        "return_code",
        "stderr",
    ]

    with GAP_REGISTER_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, str]]) -> dict[str, int]:
    """Summarize gap register results."""
    summary = {
        "total": len(rows),
        "supported": 0,
        "evidence_gap": 0,
        "gap_confirmed": 0,
        "out_of_scope_confirmed": 0,
        "boundary_review": 0,
        "possible_false_positive_review": 0,
        "review": 0,
    }

    for row in rows:
        status = row["gap_status"]

        if status == "SUPPORTED":
            summary["supported"] += 1
        elif status == "EVIDENCE_GAP":
            summary["evidence_gap"] += 1
        elif status == "GAP_CONFIRMED":
            summary["gap_confirmed"] += 1
        elif status == "OUT_OF_SCOPE_CONFIRMED":
            summary["out_of_scope_confirmed"] += 1
        elif status == "BOUNDARY_REVIEW":
            summary["boundary_review"] += 1
        elif status == "POSSIBLE_FALSE_POSITIVE_REVIEW":
            summary["possible_false_positive_review"] += 1
        else:
            summary["review"] += 1

    return summary


def determine_overall_status(summary: dict[str, int]) -> str:
    """Determine report-level status."""
    if summary["total"] == 0:
        return "REVIEW"

    if summary["evidence_gap"] > 0:
        return "EVIDENCE_GAPS_FOUND"

    if summary["boundary_review"] > 0 or summary["possible_false_positive_review"] > 0:
        return "REVIEW_REQUIRED"

    return "PASS"


def write_report(rows: list[dict[str, str]]) -> None:
    """Write markdown gap report."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    summary = summarize(rows)
    overall_status = determine_overall_status(summary)

    lines = [
        "# Security Evidence Gap Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report identifies whether the source-backed answer layer can answer approved questions, refuses out-of-scope questions, and surfaces missing evidence as gaps.",
        "",
        "The control principle is: no source, no confident answer; no answer, no silent stop.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Candidates evaluated | `{summary['total']}` |",
        f"| Supported | `{summary['supported']}` |",
        f"| Evidence gaps | `{summary['evidence_gap']}` |",
        f"| Confirmed expected gaps | `{summary['gap_confirmed']}` |",
        f"| Out-of-scope confirmed | `{summary['out_of_scope_confirmed']}` |",
        f"| Boundary reviews | `{summary['boundary_review']}` |",
        f"| Possible false-positive reviews | `{summary['possible_false_positive_review']}` |",
        f"| Other review | `{summary['review']}` |",
        "",
        "## Gap Register Results",
        "",
        "| Candidate | Expected | Answer Status | Sources | Gap Status | Recommended Action |",
        "|---|---|---|---:|---|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['candidate_id']} | "
            f"`{row['expected_disposition']}` | "
            f"`{row['answer_status']}` | "
            f"{row['source_count']} | "
            f"**{row['gap_status']}** | "
            f"{row['recommended_action']} |"
        )

    actionable_rows = [
        row for row in rows
        if row["gap_status"] in {
            "EVIDENCE_GAP",
            "GAP_CONFIRMED",
            "BOUNDARY_REVIEW",
            "POSSIBLE_FALSE_POSITIVE_REVIEW",
        }
    ]

    if actionable_rows:
        lines.extend(
            [
                "",
                "## Actionable Items",
                "",
                "| Candidate | Question | Needed Evidence or Review |",
                "|---|---|---|",
            ]
        )

        for row in actionable_rows:
            lines.append(
                f"| {row['candidate_id']} | {row['question']} | {row['needed_evidence_if_gap']} |"
            )

    lines.extend(
        [
            "",
            "## Control Logic",
            "",
            "| Control Concept | Implementation |",
            "|---|---|",
            "| Evidence gap handling | Unsupported approved questions become gap-register items. |",
            "| Boundary enforcement | Out-of-scope questions should not produce confident source-backed answers. |",
            "| False-positive review | If weakly related sources are returned for an expected gap, the result is marked for review. |",
            "| Repeatability | Candidate questions and gap results are stored as CSV artifacts. |",
            "",
            "## Generated Artifacts",
            "",
            f"- `{GAP_CANDIDATES_CSV.as_posix()}`",
            f"- `{GAP_REGISTER_CSV.as_posix()}`",
            f"- `{REPORT_FILE.as_posix()}`",
            "",
            "## One-Sentence Takeaway",
            "",
            "> A governed security assistant should convert missing evidence into an evidence gap, not a hallucinated answer.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    candidates = load_gap_candidates()
    rows = [evaluate_candidate(candidate) for candidate in candidates]

    write_gap_register(rows)
    write_report(rows)

    summary = summarize(rows)
    overall_status = determine_overall_status(summary)

    print(f"Gap candidates written to: {GAP_CANDIDATES_CSV}")
    print(f"Gap register written to: {GAP_REGISTER_CSV}")
    print(f"Gap report written to: {REPORT_FILE}")
    print(f"Candidates evaluated: {summary['total']}")
    print(f"Evidence gaps: {summary['evidence_gap']}")
    print(f"Boundary reviews: {summary['boundary_review']}")
    print(f"Possible false-positive reviews: {summary['possible_false_positive_review']}")
    print(f"Overall Status: {overall_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())