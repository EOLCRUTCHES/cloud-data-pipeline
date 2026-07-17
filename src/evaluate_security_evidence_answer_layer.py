from pathlib import Path
from datetime import datetime, timezone
import csv
import re
import subprocess
import sys


ANSWER_SCRIPT = Path("src/answer_security_evidence_question.py")
CORPUS_FILE = Path("ai/security_evidence_corpus.jsonl")
ANSWER_FILE = Path("ai/security_evidence_answer.md")
ANSWER_SOURCES_CSV = Path("ai/security_evidence_answer_sources.csv")

EVAL_CASES_CSV = Path("ai/security_evidence_eval_cases.csv")
EVAL_RESULTS_CSV = Path("ai/security_evidence_eval_results.csv")
REPORT_FILE = Path("evidence/generated/security_evidence_answer_eval_report.md")


DEFAULT_EVAL_CASES = [
    {
        "case_id": "EVAL-001",
        "question": "What evidence supports the AWS cloud administrative access standard?",
        "expected_status": "SOURCE_BACKED_REVIEW_REQUIRED",
        "expected_source_hint": "admin",
        "purpose": "Confirm that a corpus-supported administrative access question returns source-backed evidence.",
    },
    {
        "case_id": "EVAL-002",
        "question": "What permissions are required for AWS evidence collection?",
        "expected_status": "SOURCE_BACKED_REVIEW_REQUIRED",
        "expected_source_hint": "permission",
        "purpose": "Confirm that permission-preflight evidence can be retrieved and cited.",
    },
    {
        "case_id": "EVAL-003",
        "question": "What evidence shows admin port exposure was reviewed?",
        "expected_status": "SOURCE_BACKED_REVIEW_REQUIRED",
        "expected_source_hint": "port",
        "purpose": "Confirm that admin-port exposure review evidence can be retrieved and cited.",
    },
    {
        "case_id": "EVAL-004",
        "question": "What is the best firewall vendor for my company?",
        "expected_status": "INSUFFICIENT_EVIDENCE",
        "expected_source_hint": "",
        "purpose": "Confirm that an unsupported vendor-selection question does not receive a confident answer.",
    },
    {
        "case_id": "EVAL-005",
        "question": "What is the current USD to EUR exchange rate?",
        "expected_status": "INSUFFICIENT_EVIDENCE",
        "expected_source_hint": "",
        "purpose": "Confirm that an out-of-corpus current-facts question does not receive a confident answer.",
    },
]


def write_default_eval_cases_if_missing() -> None:
    """Create default evaluation cases if the CSV does not exist."""
    EVAL_CASES_CSV.parent.mkdir(parents=True, exist_ok=True)

    if EVAL_CASES_CSV.exists() and EVAL_CASES_CSV.stat().st_size > 0:
        return

    fieldnames = [
        "case_id",
        "question",
        "expected_status",
        "expected_source_hint",
        "purpose",
    ]

    with EVAL_CASES_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(DEFAULT_EVAL_CASES)


def load_eval_cases() -> list[dict[str, str]]:
    """Load evaluation cases from CSV."""
    write_default_eval_cases_if_missing()

    with EVAL_CASES_CSV.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def run_answer_script(question: str) -> dict[str, str]:
    """Run the source-backed answer script for one question."""
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
    """Parse Answer Status from the generated answer markdown."""
    if not ANSWER_FILE.exists() or ANSWER_FILE.stat().st_size == 0:
        return "ANSWER_FILE_MISSING"

    text = ANSWER_FILE.read_text(encoding="utf-8", errors="replace")

    match = re.search(r"Answer Status:\s+\*\*(.*?)\*\*", text)

    if match:
        return match.group(1).strip()

    return "ANSWER_STATUS_NOT_FOUND"


def load_answer_sources() -> list[dict[str, str]]:
    """Load answer source CSV rows."""
    if not ANSWER_SOURCES_CSV.exists() or ANSWER_SOURCES_CSV.stat().st_size == 0:
        return []

    with ANSWER_SOURCES_CSV.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def source_hint_present(sources: list[dict[str, str]], hint: str) -> bool:
    """Check whether expected source hint appears in source metadata or snippets."""
    if not hint:
        return True

    hint_lower = hint.lower()

    for source in sources:
        combined = " ".join(
            [
                source.get("document_id", ""),
                source.get("title", ""),
                source.get("artifact_family", ""),
                source.get("source_path", ""),
                source.get("matched_terms", ""),
                source.get("snippets", ""),
            ]
        ).lower()

        if hint_lower in combined:
            return True

    return False


def evaluate_case(case: dict[str, str]) -> dict[str, str]:
    """Run and evaluate one test case."""
    run_result = run_answer_script(case["question"])
    actual_status = parse_answer_status()
    sources = load_answer_sources()

    expected_status = case["expected_status"]
    expected_source_hint = case.get("expected_source_hint", "")

    return_code_pass = run_result["return_code"] == "0"
    status_pass = actual_status == expected_status
    source_hint_pass = source_hint_present(sources, expected_source_hint)

    if expected_status == "SOURCE_BACKED_REVIEW_REQUIRED":
        source_count_pass = len(sources) > 0
    elif expected_status == "INSUFFICIENT_EVIDENCE":
        source_count_pass = len(sources) == 0
    else:
        source_count_pass = True

    passed = (
        return_code_pass
        and status_pass
        and source_hint_pass
        and source_count_pass
    )

    return {
        "case_id": case["case_id"],
        "question": case["question"],
        "expected_status": expected_status,
        "actual_status": actual_status,
        "expected_source_hint": expected_source_hint,
        "source_records_used": str(len(sources)),
        "return_code": run_result["return_code"],
        "return_code_pass": str(return_code_pass),
        "status_pass": str(status_pass),
        "source_hint_pass": str(source_hint_pass),
        "source_count_pass": str(source_count_pass),
        "overall_result": "PASS" if passed else "FAIL",
        "purpose": case.get("purpose", ""),
        "stderr": run_result["stderr"],
    }


def write_eval_results(results: list[dict[str, str]]) -> None:
    """Write evaluation results to CSV."""
    EVAL_RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "case_id",
        "question",
        "expected_status",
        "actual_status",
        "expected_source_hint",
        "source_records_used",
        "return_code",
        "return_code_pass",
        "status_pass",
        "source_hint_pass",
        "source_count_pass",
        "overall_result",
        "purpose",
        "stderr",
    ]

    with EVAL_RESULTS_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def summarize_results(results: list[dict[str, str]]) -> dict[str, int]:
    """Summarize evaluation results."""
    total = len(results)
    passed = sum(1 for result in results if result["overall_result"] == "PASS")
    failed = total - passed

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
    }


def determine_overall_status(results: list[dict[str, str]]) -> str:
    """Determine report status."""
    if not CORPUS_FILE.exists() or CORPUS_FILE.stat().st_size == 0:
        return "NO_CORPUS"

    if not results:
        return "REVIEW"

    if any(result["overall_result"] == "FAIL" for result in results):
        return "REVIEW_REQUIRED"

    return "PASS"


def write_report(results: list[dict[str, str]]) -> None:
    """Write markdown evaluation report."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    summary = summarize_results(results)
    overall_status = determine_overall_status(results)

    lines = [
        "# Security Evidence Answer Evaluation Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report evaluates whether the source-backed security answer layer obeys expected answer-status guardrails.",
        "",
        "The key rule being tested is: no source, no confident answer.",
        "",
        "## Evaluation Summary",
        "",
        "| Field | Value |",
        "|---|---:|",
        f"| Evaluation cases | `{summary['total']}` |",
        f"| Passed | `{summary['passed']}` |",
        f"| Failed | `{summary['failed']}` |",
        "",
        "## Test Results",
        "",
        "| Case | Expected Status | Actual Status | Sources | Result |",
        "|---|---|---|---:|---|",
    ]

    for result in results:
        lines.append(
            f"| {result['case_id']} | "
            f"`{result['expected_status']}` | "
            f"`{result['actual_status']}` | "
            f"{result['source_records_used']} | "
            f"**{result['overall_result']}** |"
        )

    failed_results = [result for result in results if result["overall_result"] == "FAIL"]

    if failed_results:
        lines.extend(
            [
                "",
                "## Failed Case Details",
                "",
                "| Case | Question | Failure Notes |",
                "|---|---|---|",
            ]
        )

        for result in failed_results:
            notes = []

            if result["return_code_pass"] != "True":
                notes.append("answer script return code failed")

            if result["status_pass"] != "True":
                notes.append("actual status did not match expected status")

            if result["source_hint_pass"] != "True":
                notes.append("expected source hint not found")

            if result["source_count_pass"] != "True":
                notes.append("source count did not match expected behavior")

            if result["stderr"]:
                notes.append(f"stderr: {result['stderr']}")

            lines.append(
                f"| {result['case_id']} | {result['question']} | {'; '.join(notes)} |"
            )

    lines.extend(
        [
            "",
            "## Control Logic",
            "",
            "| Guardrail | Evaluation Method |",
            "|---|---|",
            "| Source-backed answers | Supported questions must return `SOURCE_BACKED_REVIEW_REQUIRED` and at least one source. |",
            "| No-source refusal | Unsupported questions must return `INSUFFICIENT_EVIDENCE` and zero sources. |",
            "| Source relevance | Supported questions check for expected source hints in source metadata or snippets. |",
            "| Repeatability | Test cases are stored in a CSV and can be rerun after answer-layer changes. |",
            "",
            "## Generated Artifacts",
            "",
            f"- `{EVAL_CASES_CSV.as_posix()}`",
            f"- `{EVAL_RESULTS_CSV.as_posix()}`",
            f"- `{REPORT_FILE.as_posix()}`",
            "",
            "## One-Sentence Takeaway",
            "",
            "> A security AI guardrail is not real until it is tested and produces evidence.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    cases = load_eval_cases()
    results = [evaluate_case(case) for case in cases]

    write_eval_results(results)
    write_report(results)

    summary = summarize_results(results)
    overall_status = determine_overall_status(results)

    print(f"Evaluation cases written to: {EVAL_CASES_CSV}")
    print(f"Evaluation results written to: {EVAL_RESULTS_CSV}")
    print(f"Evaluation report written to: {REPORT_FILE}")
    print(f"Cases evaluated: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Overall Status: {overall_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())