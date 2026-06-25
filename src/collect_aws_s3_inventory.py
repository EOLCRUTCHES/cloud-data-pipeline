from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess


REPORT_FILE = Path("evidence/generated/aws_s3_inventory_report.md")


def run_command(command: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        shell=False,
    )

    return result.returncode, result.stdout.strip(), result.stderr.strip()


def mask_bucket_name(bucket_name: str) -> str:
    """Return a safer masked bucket identifier for portfolio evidence."""
    digest = hashlib.sha256(bucket_name.encode("utf-8")).hexdigest()

    if len(bucket_name) <= 4:
        visible_suffix = bucket_name
    else:
        visible_suffix = bucket_name[-4:]

    return f"bucket-****{visible_suffix}-{digest[:8]}"


def collect_s3_inventory() -> dict[str, object]:
    """Collect basic S3 bucket inventory evidence."""
    inventory: dict[str, object] = {
        "aws_cli_found": "No",
        "s3_check_status": "Not run",
        "bucket_count": 0,
        "buckets": [],
        "error": "",
    }

    aws_path = shutil.which("aws")

    if aws_path is None:
        inventory["error"] = "AWS CLI was not found on PATH."
        return inventory

    inventory["aws_cli_found"] = "Yes"

    code, stdout, stderr = run_command(["aws", "s3api", "list-buckets"])

    if code != 0:
        inventory["s3_check_status"] = "Failed"
        inventory["error"] = stderr
        return inventory

    try:
        response = json.loads(stdout)
    except json.JSONDecodeError:
        inventory["s3_check_status"] = "Failed"
        inventory["error"] = "AWS S3 list-buckets response was not valid JSON."
        return inventory

    buckets = response.get("Buckets", [])

    safe_buckets = []

    for bucket in buckets:
        bucket_name = bucket.get("Name", "")
        creation_date = bucket.get("CreationDate", "")

        safe_buckets.append(
            {
                "masked_name": mask_bucket_name(bucket_name),
                "creation_date": creation_date,
            }
        )

    inventory["s3_check_status"] = "Passed"
    inventory["bucket_count"] = len(safe_buckets)
    inventory["buckets"] = safe_buckets

    return inventory


def write_report(inventory: dict[str, object]) -> None:
    """Write S3 inventory evidence report."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    overall_status = "PASS" if inventory["s3_check_status"] == "Passed" else "REVIEW"

    lines = [
        "# AWS S3 Inventory Evidence Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{overall_status}**",
        "",
        "## Purpose",
        "",
        "This report collects basic AWS S3 inventory evidence without creating, modifying, or deleting cloud resources.",
        "",
        "Bucket names are masked for safer portfolio use.",
        "",
        "## Summary",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| AWS CLI found | {inventory['aws_cli_found']} |",
        f"| S3 inventory check | {inventory['s3_check_status']} |",
        f"| Bucket count | {inventory['bucket_count']} |",
        "",
        "## Bucket Inventory",
        "",
    ]

    buckets = inventory["buckets"]

    if buckets:
        lines.extend(
            [
                "| Masked Bucket Identifier | Creation Date |",
                "|---|---|",
            ]
        )

        for bucket in buckets:
            lines.append(
                f"| `{bucket['masked_name']}` | `{bucket['creation_date']}` |"
            )
    else:
        lines.append("No buckets were listed, or the S3 inventory check did not complete successfully.")

    lines.append("")

    if inventory["error"]:
        lines.extend(
            [
                "## Error / Review Note",
                "",
                "```text",
                str(inventory["error"]),
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
            "- Bucket names are masked before being written to the report.",
            "- This report is intended as a first step toward cloud storage evidence collection.",
            "",
            "## Portfolio Relevance",
            "",
            "This report demonstrates a safe AWS object-storage evidence collection pattern.",
            "",
            "Future lessons can extend this pattern to bucket encryption, public access settings, logging, and policy review.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"AWS S3 inventory report written to: {REPORT_FILE}")
    print(f"Overall Status: {overall_status}")


def main() -> None:
    """Collect AWS S3 inventory evidence and write a report."""
    inventory = collect_s3_inventory()
    write_report(inventory)


if __name__ == "__main__":
    main()