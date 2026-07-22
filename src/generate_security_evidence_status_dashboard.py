from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import sys


CORPUS_MANIFEST = Path("ai/security_evidence_corpus_manifest.csv")
EVAL_RESULTS = Path("ai/security_evidence_eval_results.csv")
GAP_REGISTER = Path("ai/security_evidence_gap_register.csv")
CLOSURE_REGISTER = Path("ai/security_evidence_gap_closure_register.csv")
REVIEWER_DECISIONS = Path("ai/security_evidence_reviewer_decisions.csv")
ADJUDICATED_STATUS = Path("ai/security_evidence_adjudicated_gap_status.csv")
REMEDIATION_REGISTER = Path("security/aws_admin_port_remediation_register.csv")

STATUS_SUMMARY = Path("ai/security_evidence_status_summary.csv")
DASHBOARD = Path("docs/cloud/security_evidence_status_dashboard.md")
REPORT_FILE = Path("evidence/generated/security_evidence_status_dashboard_report.md")


INPUT_ARTIFACTS = [
    CORPUS_MANIFEST,
    EVAL_RESULTS,
    GAP_REGISTER,
    CLOSURE_REGISTER,
    REVIEWER_DECISIONS,
    ADJUDICATED_STATUS,
    REMEDIATION_REGISTER,
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


def count_field(rows: list[dict[str, str]], field: str) -> Counter:
    return Counter((row.get(field, "") or "not_recorded").strip() for row in rows)


def first_value(rows: list[dict[str, str]], field: str) -> str:
    if not rows:
        return "not_available"

    return (rows[0].get(field, "") or "not_recorded").strip()


def build_metrics() -> dict[str, object]:
    corpus_rows = read_csv(CORPUS_MANIFEST)
    eval_rows = read_csv(EVAL_RESULTS)
    gap_rows = read_csv(GAP_REGISTER)
    closure_rows = read_csv(CLOSURE_REGISTER)
    review_rows = read_csv(REVIEWER_DECISIONS)
    adjudicated_rows = read_csv(ADJUDICATED_STATUS)
    remediation_rows = read_csv(REMEDIATION_REGISTER)

    eval_failures = sum(
        1 for row in eval_rows
        if row.get("overall_result", "").strip() == "FAIL"
    )

    metrics = {
        "corpus_rows": corpus_rows,
        "eval_rows": eval_rows,
        "gap_rows": gap_rows,
        "closure_rows": closure_rows,
        "review_rows": review_rows,
        "adjudicated_rows": adjudicated_rows,
        "remediation_rows": remediation_rows,
        "corpus_document_count": len(corpus_rows),
        "eval_case_count": len(eval_rows),
        "eval_failure_count": eval_failures,
        "gap_status_counts": count_field(gap_rows, "gap_status"),
        "closure_status_counts": count_field(closure_rows, "closure_status"),
        "reviewer_decision_counts": count_field(review_rows, "reviewer_decision"),
        "final_gap_status_counts": count_field(adjudicated_rows, "final_gap_status"),
        "remediation_closure_status": first_value(remediation_rows, "closure_status"),
    }

    return metrics


def determine_overall_status(metrics: dict[str, object]) -> str:
    corpus_document_count = metrics["corpus_document_count"]
    eval_failure_count = metrics["eval_failure_count"]
    final_counts = metrics["final_gap_status_counts"]
    review_counts = metrics["reviewer_decision_counts"]

    if corpus_document_count == 0:
        return "NO_CORPUS"

    if eval_failure_count > 0:
        return "REVIEW_REQUIRED_EVALUATION_FAILURES"

    if final_counts.get("INVALID_REVIEWER_DECISION", 0) > 0:
        return "REVIEW_REQUIRED_INVALID_DECISIONS"

    if final_counts.get("REVIEW_DECISION_INCOMPLETE", 0) > 0:
        return "REVIEW_REQUIRED_INCOMPLETE_DECISIONS"

    if final_counts.get("PENDING_HUMAN_REVIEW", 0) > 0:
        return "PENDING_HUMAN_REVIEW"

    if final_counts.get("OPEN", 0) > 0:
        return "ACTION_REMAINS_OPEN_GAPS"

    if final_counts.get("RETRIEVAL_TUNING_REQUIRED", 0) > 0:
        return "ACTION_REMAINS_RETRIEVAL_TUNING"

    if review_counts.get("PENDING_REVIEW", 0) > 0:
        return "PENDING_HUMAN_REVIEW"

    return "EVIDENCE_SYSTEM_STABLE"


def build_next_actions(metrics: dict[str, object]) -> list[str]:
    actions = []
    final_counts = metrics["final_gap_status_counts"]
    review_counts = metrics["reviewer_decision_counts"]

    if metrics["corpus_document_count"] == 0:
        actions.append("Run the corpus builder so the evidence system has approved source material.")

    if metrics["eval_failure_count"] > 0:
        actions.append("Review failed evaluation cases and tune retrieval, answer thresholds, or test expectations.")

    if final_counts.get("REVIEW_DECISION_INCOMPLETE", 0) > 0:
        actions.append("Complete reviewer, decision_date, and reviewer_notes for non-pending reviewer decisions.")

    if final_counts.get("INVALID_REVIEWER_DECISION", 0) > 0:
        actions.append("Correct invalid reviewer_decision values in the reviewer decision CSV.")

    if final_counts.get("PENDING_HUMAN_REVIEW", 0) > 0 or review_counts.get("PENDING_REVIEW", 0) > 0:
        actions.append("Complete human review decisions for pending closure items.")

    if final_counts.get("OPEN", 0) > 0:
        actions.append("Collect missing evidence or remediate remaining risk for open gaps.")

    if final_counts.get("PARTIALLY_CLOSED", 0) > 0:
        actions.append("Track residual work for partially closed gaps.")

    if final_counts.get("RETRIEVAL_TUNING_REQUIRED", 0) > 0:
        actions.append("Tune retrieval logic, source matching, thresholds, or test classification.")

    if not actions:
        actions.append("No immediate corrective action. Continue expanding evidence coverage and evaluation cases.")

    return actions


def build_summary_rows(metrics: dict[str, object], overall_status: str) -> list[dict[str, str]]:
    rows = [
        {
            "category": "overall",
            "metric": "overall_status",
            "value": overall_status,
            "interpretation": "Top-level posture for the local security evidence system.",
        },
        {
            "category": "corpus",
            "metric": "documents_indexed",
            "value": str(metrics["corpus_document_count"]),
            "interpretation": "Number of approved evidence records available for retrieval.",
        },
        {
            "category": "evaluation",
            "metric": "evaluation_cases",
            "value": str(metrics["eval_case_count"]),
            "interpretation": "Number of answer-layer guardrail tests evaluated.",
        },
        {
            "category": "evaluation",
            "metric": "evaluation_failures",
            "value": str(metrics["eval_failure_count"]),
            "interpretation": "Failed guardrail tests requiring review.",
        },
        {
            "category": "remediation",
            "metric": "aws_admin_port_remediation_status",
            "value": str(metrics["remediation_closure_status"]),
            "interpretation": "Current recorded closure status for AWS admin-port remediation evidence.",
        },
    ]

    counter_groups = [
        ("gap_register", "gap_status", metrics["gap_status_counts"]),
        ("closure_register", "closure_status", metrics["closure_status_counts"]),
        ("reviewer_decisions", "reviewer_decision", metrics["reviewer_decision_counts"]),
        ("adjudication", "final_gap_status", metrics["final_gap_status_counts"]),
    ]

    for category, metric_name, counter in counter_groups:
        if not counter:
            rows.append(
                {
                    "category": category,
                    "metric": metric_name,
                    "value": "no_rows",
                    "interpretation": "No rows were available for this artifact.",
                }
            )
            continue

        for key, value in sorted(counter.items()):
            rows.append(
                {
                    "category": category,
                    "metric": key,
                    "value": str(value),
                    "interpretation": f"Count of {metric_name} entries with value {key}.",
                }
            )

    return rows


def safe_cell(value: object) -> str:
    return str(value).replace("|", " ").replace("\n", " ").strip()


def write_dashboard(metrics: dict[str, object], overall_status: str, next_actions: list[str]) -> None:
    DASHBOARD.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    final_counts = metrics["final_gap_status_counts"]
    review_counts = metrics["reviewer_decision_counts"]

    lines = [
        "# Security Evidence Status Dashboard",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This dashboard summarizes the current posture of the local security evidence system.",
        "",
        "It consolidates corpus coverage, answer evaluation, evidence gaps, closure review, reviewer decisions, adjudicated status, and remediation evidence.",
        "",
        "## Executive Rollup",
        "",
        "| Area | Current Value |",
        "|---|---:|",
        f"| Corpus documents indexed | `{metrics['corpus_document_count']}` |",
        f"| Evaluation cases | `{metrics['eval_case_count']}` |",
        f"| Evaluation failures | `{metrics['eval_failure_count']}` |",
        f"| Pending reviewer decisions | `{review_counts.get('PENDING_REVIEW', 0)}` |",
        f"| Final closed gaps | `{final_counts.get('CLOSED', 0)}` |",
        f"| Final open gaps | `{final_counts.get('OPEN', 0)}` |",
        f"| Pending human review | `{final_counts.get('PENDING_HUMAN_REVIEW', 0)}` |",
        f"| Retrieval tuning required | `{final_counts.get('RETRIEVAL_TUNING_REQUIRED', 0)}` |",
        f"| AWS admin-port remediation | `{safe_cell(metrics['remediation_closure_status'])}` |",
        "",
        "## Next Actions",
        "",
    ]

    for action in next_actions:
        lines.append(f"- {action}")

    lines.extend(
        [
            "",
            "## Artifact Health",
            "",
            "| Artifact | Status |",
            "|---|---|",
        ]
    )

    for artifact in INPUT_ARTIFACTS:
        lines.append(f"| `{artifact.as_posix()}` | {artifact_status(artifact)} |")

    lines.extend(
        [
            "",
            "## Final Gap Status Counts",
            "",
            "| Final Status | Count |",
            "|---|---:|",
        ]
    )

    if final_counts:
        for status, count in sorted(final_counts.items()):
            lines.append(f"| `{safe_cell(status)}` | `{count}` |")
    else:
        lines.append("| `no_rows` | `0` |")

    lines.extend(
        [
            "",
            "## Reviewer Decision Counts",
            "",
            "| Reviewer Decision | Count |",
            "|---|---:|",
        ]
    )

    if review_counts:
        for status, count in sorted(review_counts.items()):
            lines.append(f"| `{safe_cell(status)}` | `{count}` |")
    else:
        lines.append("| `no_rows` | `0` |")

    lines.extend(
        [
            "",
            "## Control Interpretation",
            "",
            "| Control Question | Current Interpretation |",
            "|---|---|",
            "| Is there an approved corpus? | Corpus count shows whether local source material exists for bounded retrieval. |",
            "| Are answer guardrails tested? | Evaluation failure count shows whether the no-source/no-confident-answer rule is holding. |",
            "| Are gaps managed? | Gap, closure, reviewer, and adjudication counts show lifecycle state. |",
            "| Is closure human-reviewed? | Pending and completed reviewer decisions show whether humans accepted closure. |",
            "| Is remediation evidenced? | Admin-port remediation status shows whether the detected issue has post-fix evidence. |",
            "",
            "## One-Sentence Takeaway",
            "",
            "> A security evidence system needs a dashboard that shows not only what it knows, but what still needs review, closure, or correction.",
            "",
        ]
    )

    DASHBOARD.write_text("\n".join(lines), encoding="utf-8")


def write_report(metrics: dict[str, object], overall_status: str, next_actions: list[str]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Security Evidence Status Dashboard Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report records generation of the security evidence status dashboard.",
        "",
        "## Generated Artifacts",
        "",
        f"- `{STATUS_SUMMARY.as_posix()}`",
        f"- `{DASHBOARD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Input Artifacts",
        "",
        "| Artifact | Status |",
        "|---|---|",
    ]

    for artifact in INPUT_ARTIFACTS:
        lines.append(f"| `{artifact.as_posix()}` | {artifact_status(artifact)} |")

    lines.extend(
        [
            "",
            "## Next Actions Count",
            "",
            f"`{len(next_actions)}`",
            "",
            "## Control Mapping",
            "",
            "| Control Concept | Evidence Contribution |",
            "|---|---|",
            "| Evidence posture visibility | Consolidates core security evidence lifecycle metrics. |",
            "| Management review | Provides a human-readable status dashboard for review. |",
            "| Machine-readable status | Writes a CSV summary for later automation or reporting. |",
            "| Safe governance | Keeps pending, open, closed, and review-required states separate. |",
            "",
            "## One-Sentence Takeaway",
            "",
            "> A governed evidence system should expose its own posture, not hide it across scattered artifacts.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    metrics = build_metrics()
    overall_status = determine_overall_status(metrics)
    next_actions = build_next_actions(metrics)
    summary_rows = build_summary_rows(metrics, overall_status)

    write_csv(
        STATUS_SUMMARY,
        summary_rows,
        ["category", "metric", "value", "interpretation"],
    )

    write_dashboard(metrics, overall_status, next_actions)
    write_report(metrics, overall_status, next_actions)

    print(f"Status summary written to: {STATUS_SUMMARY}")
    print(f"Dashboard written to: {DASHBOARD}")
    print(f"Dashboard report written to: {REPORT_FILE}")
    print(f"Corpus documents indexed: {metrics['corpus_document_count']}")
    print(f"Evaluation failures: {metrics['eval_failure_count']}")
    print(f"Overall Status: {overall_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())