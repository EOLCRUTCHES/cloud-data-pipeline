from pathlib import Path
import subprocess
import sys


WORKFLOW_STEPS = [
    {
        "name": "Validate sample data and generate evidence report",
        "script": "src/validate_sample_data.py",
    },
    {
        "name": "Generate evidence index",
        "script": "src/generate_evidence_index.py",
    },
    {
        "name": "Generate control matrix",
        "script": "src/generate_control_matrix.py",
    },
    {
        "name": "Generate risk register",
        "script": "src/generate_risk_register.py",
    },
]


def run_step(step: dict[str, str]) -> bool:
    """Run one workflow step."""
    script_path = Path(step["script"])

    print("")
    print(f"START: {step['name']}")

    if not script_path.exists():
        print(f"FAIL: Missing script: {script_path}")
        return False

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout.strip())

    if result.stderr:
        print(result.stderr.strip())

    if result.returncode != 0:
        print(f"FAIL: {step['name']}")
        return False

    print(f"PASS: {step['name']}")
    return True


def main() -> None:
    """Run the governance automation workflow."""
    print("Governance workflow started")

    all_passed = True

    for step in WORKFLOW_STEPS:
        step_passed = run_step(step)

        if not step_passed:
            all_passed = False
            break

    print("")

    if all_passed:
        print("PASS: Governance workflow completed successfully")
    else:
        print("FAIL: Governance workflow did not complete successfully")
        sys.exit(1)


if __name__ == "__main__":
    main()