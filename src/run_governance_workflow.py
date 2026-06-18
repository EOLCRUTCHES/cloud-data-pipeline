from pathlib import Path
from datetime import datetime, timezone
import subprocess
import sys


EVIDENCE_DIR = Path("evidence/generated")
WORKFLOW_REPORT = EVIDENCE_DIR / "governance_workflow_run_report.md"


WORKFLOW_STEPS = [
    {
        "name": "Validate sample data and generate evidence report",
        "script": "src/validate_sample_data.py",
    },
    {
        "name": "Generate control matrix",
        "script": "src/generate_control_matrix.py",
    },
    {
        "name": "Generate risk register",
        "script": "src/generate_risk_register.py",
    },
    {
        "name": "Generate artifact manifest",
        "script": "src/generate_artifact_manifest.py",
    },
    {
        "name": "Generate artifact hash report",
        "script": "src/generate_artifact_hash_report.py",
    },
    {
        "name": "Generate evidence index",
        "script": "src/generate_evidence_index.py",
    },
]


def run_step(step: dict[str, str]) -> dict[str, str]:
    """Run one workflow step and return the result."""
    script_path = Path(step["script"])

    print("")
    print(f"START: {step['name']}")

    if not script_path.exists():
        message = f"Missing script: {script_path}"
        print(f"FAIL: {message}")

        return {
            "name": step["name"],
            "script": step["script"],
            "status": "FAIL",
            "stdout": "",
            "stderr": message,
        }

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    if stdout:
        print(stdout)

    if stderr:
        print(stderr)

    status = "PASS" if result.returncode == 0 else "FAIL"

    print(f"{status}: {step['name']}")

    return {
        "name": step["name"],
        "script": step["script"],
        "status": status,
        "stdout": stdout,
        "stderr": stderr,
    }


def write_workflow_report(results: list[dict[str, str]], overall_status: str) -> None:
    """Write workflow execution evidence to a markdown report."""
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Governance Workflow Run Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Workflow Steps",
        "",
        "| Step | Script | Status |",
        "|---|---|---|",
    ]

    for result in results:
        lines.append(
            f"| {result['name']} | `{result['script']}` | {result['status']} |"
        )

    lines.extend(
        [
            "",
            "## Step Output",
            "",
        ]
    )

    for result in results:
        lines.extend(
            [
                f"### {result['name']}",
                "",
                f"Status: **{result['status']}**",
                "",
                "Output:",
                "",
                "```text",
                result["stdout"] if result["stdout"] else "No standard output.",
                "```",
                "",
            ]
        )

        if result["stderr"]:
            lines.extend(
                [
                    "Errors:",
                    "",
                    "```text",
                    result["stderr"],
                    "```",
                    "",
                ]
            )

    lines.extend(
        [
            "## Portfolio Relevance",
            "",
            "This report demonstrates that the governance automation workflow creates evidence of execution, not just individual output files.",
            "",
            "This supports auditability, repeatability, and future security evidence automation.",
            "",
        ]
    )

    WORKFLOW_REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("")
    print(f"Workflow report written to: {WORKFLOW_REPORT}")


def main() -> None:
    """Run the governance automation workflow and write execution evidence."""
    print("Governance workflow started")

    results = []

    for step in WORKFLOW_STEPS:
        result = run_step(step)
        results.append(result)

        if result["status"] == "FAIL":
            break

    overall_status = "PASS"

    for result in results:
        if result["status"] == "FAIL":
            overall_status = "FAIL"

    write_workflow_report(results, overall_status)

    print("")

    if overall_status == "PASS":
        print("PASS: Governance workflow completed successfully")
    else:
        print("FAIL: Governance workflow did not complete successfully")
        sys.exit(1)


if __name__ == "__main__":
    main()