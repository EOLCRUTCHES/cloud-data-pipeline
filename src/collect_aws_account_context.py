from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import subprocess


REPORT_FILE = Path("evidence/generated/aws_account_context_report.md")


def run_command(command: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=False,
    )

    return result.returncode, result.stdout.strip(), result.stderr.strip()


def mask_account_id(account_id: str) -> str:
    """Mask an AWS account ID for safer portfolio evidence."""
    if len(account_id) < 4:
        return "Unavailable"

    return f"********{account_id[-4:]}"


def collect_aws_context() -> dict[str, str]:
    """Collect AWS CLI readiness and account context."""
    context = {
        "aws_cli_found": "No",
        "aws_cli_version": "Unavailable",
        "sts_check_status": "Not run",
        "account_id_masked": "Unavailable",
        "arn_type": "Unavailable",
        "user_id_present": "No",
        "error": "",
    }

    aws_path = shutil.which("aws")

    if aws_path is None:
        context["error"] = "AWS CLI was not found on PATH."
        return context

    context["aws_cli_found"] = "Yes"

    version_code, version_stdout, version_stderr = run_command(["aws", "--version"])

    if version_code == 0:
        context["aws_cli_version"] = version_stdout or version_stderr
    else:
        context["aws_cli_version"] = "AWS CLI found, but version check failed."
        context["error"] = version_stderr

    sts_code, sts_stdout, sts_stderr = run_command(["aws", "sts", "get-caller-identity"])

    if sts_code != 0:
        context["sts_check_status"] = "Failed"
        context["error"] = sts_stderr
        return context

    context["sts_check_status"] = "Passed"

    try:
        identity = json.loads(sts_stdout)
    except json.JSONDecodeError:
        context["sts_check_status"] = "Failed"
        context["error"] = "STS response was not valid JSON."
        return context

    account_id = identity.get("Account", "")
    arn = identity.get("Arn", "")
    user_id = identity.get("UserId", "")

    context["account_id_masked"] = mask_account_id(account_id)
    context["user_id_present"] = "Yes" if user_id else "No"

    if ":assumed-role/" in arn:
        context["arn_type"] = "Assumed role"
    elif ":user/" in arn:
        context["arn_type"] = "IAM user"
    elif ":root" in arn:
        context["arn_type"] = "Root"
    elif arn:
        context["arn_type"] = "Other"
    else:
        context["arn_type"] = "Unavailable"

    return context


def write_report(context: dict[str, str]) -> None:
    """Write AWS account context evidence report."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    overall_status = "PASS" if context["sts_check_status"] == "Passed" else "REVIEW"

    lines = [
        "# AWS Account Context Evidence Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report collects basic AWS CLI and account-context evidence without creating, modifying, or deleting cloud resources.",
        "",
        "Sensitive account details are intentionally minimized for safer portfolio use.",
        "",
        "## AWS Context Summary",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| AWS CLI found | {context['aws_cli_found']} |",
        f"| AWS CLI version | `{context['aws_cli_version']}` |",
        f"| STS caller identity check | {context['sts_check_status']} |",
        f"| Masked account ID | `{context['account_id_masked']}` |",
        f"| ARN type | {context['arn_type']} |",
        f"| User ID present | {context['user_id_present']} |",
        "",
    ]

    if context["error"]:
        lines.extend(
            [
                "## Error / Review Note",
                "",
                "```text",
                context["error"],
                "```",
                "",
            ]
        )

    lines.extend(
        [
            "## Security Notes",
            "",
            "- This script does not create AWS resources.",
            "- This script does not modify AWS resources.",
            "- This script does not delete AWS resources.",
            "- Account ID is masked in the report.",
            "- This evidence is intended to prove cloud-readiness and account-context awareness.",
            "",
            "## Portfolio Relevance",
            "",
            "This report demonstrates the first AWS evidence collection pattern in the secure automation portfolio.",
            "",
            "It connects cloud account context to local evidence generation while preserving cost control and minimizing sensitive data exposure.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"AWS account context report written to: {REPORT_FILE}")
    print(f"Overall Status: {overall_status}")


def main() -> None:
    """Collect AWS account context and write evidence report."""
    context = collect_aws_context()
    write_report(context)


if __name__ == "__main__":
    main()