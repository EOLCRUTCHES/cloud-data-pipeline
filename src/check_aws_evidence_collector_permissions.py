from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import os
import subprocess
import sys


PERMISSIONS_FILE = Path("security/aws_evidence_collector_permissions.csv")
PLAYBOOK_FILE = Path("docs/cloud/aws_evidence_collector_permission_playbook.md")
REPORT_FILE = Path("evidence/generated/aws_evidence_collector_permission_preflight_report.md")


def run_command(command: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def stable_mask(value: str, label: str) -> str:
    if not value:
        return "not_present"
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    return f"{label}_{digest}"


def get_region() -> str:
    env_region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")

    if env_region:
        return env_region

    return_code, stdout, _stderr = run_command(["aws", "configure", "get", "region"])

    if return_code == 0 and stdout:
        return stdout

    return ""


def get_identity_context() -> dict[str, str]:
    return_code, stdout, stderr = run_command(
        ["aws", "sts", "get-caller-identity", "--output", "json"]
    )

    if return_code != 0:
        return {
            "identity_status": "NOT_AUTHENTICATED",
            "account_masked": "not_available",
            "arn_masked": "not_available",
            "user_id_masked": "not_available",
            "identity_error": stderr or "STS get-caller-identity failed.",
        }

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "identity_status": "REVIEW",
            "account_masked": "not_available",
            "arn_masked": "not_available",
            "user_id_masked": "not_available",
            "identity_error": "STS output could not be parsed as JSON.",
        }

    return {
        "identity_status": "AUTHENTICATED",
        "account_masked": stable_mask(data.get("Account", ""), "account"),
        "arn_masked": stable_mask(data.get("Arn", ""), "arn"),
        "user_id_masked": stable_mask(data.get("UserId", ""), "user"),
        "identity_error": "",
    }


def classify_command_result(
    return_code: int,
    stdout: str,
    stderr: str,
    success_mode: str,
) -> tuple[str, str]:
    combined = f"{stdout}\n{stderr}".lower()

    if success_mode == "normal_success" and return_code == 0:
        return "AUTHORIZED", "Command completed successfully."

    if success_mode == "ec2_dry_run":
        if "dryrunoperation" in combined:
            return "AUTHORIZED", "DryRunOperation returned, which indicates the principal has permission."
        if "unauthorizedoperation" in combined or "not authorized" in combined:
            return "NOT_AUTHORIZED", "AWS returned UnauthorizedOperation for the dry-run request."

    if "accessdenied" in combined or "access denied" in combined:
        return "NOT_AUTHORIZED", "AWS returned AccessDenied."

    if "not authorized" in combined or "unauthorized" in combined:
        return "NOT_AUTHORIZED", "AWS returned an authorization failure."

    if "could not be found" in combined or "invalidclienttokenid" in combined:
        return "REVIEW", "AWS credentials or identity context may be invalid."

    if return_code != 0:
        return "REVIEW", stderr or stdout or "Command failed without detailed output."

    return "REVIEW", "Command result did not match an expected success or authorization-failure pattern."


def build_checks(region: str) -> list[dict[str, str]]:
    checks = [
        {
            "check_id": "AWS-STS-001",
            "collector_area": "Account context evidence",
            "aws_action": "sts:GetCallerIdentity",
            "permission_purpose": "Identify the active AWS principal without exposing account details.",
            "command_display": "aws sts get-caller-identity --output json",
            "command": ["aws", "sts", "get-caller-identity", "--output", "json"],
            "success_mode": "normal_success",
            "policy_resource": "*",
            "recommended_policy_sid": "AllowGetCallerIdentity",
        },
        {
            "check_id": "AWS-S3-001",
            "collector_area": "S3 inventory evidence",
            "aws_action": "s3:ListAllMyBuckets",
            "permission_purpose": "List account-owned S3 buckets for inventory evidence.",
            "command_display": "aws s3api list-buckets --output json",
            "command": ["aws", "s3api", "list-buckets", "--output", "json"],
            "success_mode": "normal_success",
            "policy_resource": "*",
            "recommended_policy_sid": "AllowListAllS3Buckets",
        },
    ]

    if region:
        checks.append(
            {
                "check_id": "AWS-EC2-001",
                "collector_area": "Admin port exposure evidence",
                "aws_action": "ec2:DescribeSecurityGroups",
                "permission_purpose": "Read security group rules to identify administrative port exposure.",
                "command_display": f"aws ec2 describe-security-groups --region {region} --dry-run --output json",
                "command": [
                    "aws",
                    "ec2",
                    "describe-security-groups",
                    "--region",
                    region,
                    "--dry-run",
                    "--output",
                    "json",
                ],
                "success_mode": "ec2_dry_run",
                "policy_resource": "*",
                "recommended_policy_sid": "AllowDescribeSecurityGroups",
            }
        )
    else:
        checks.append(
            {
                "check_id": "AWS-EC2-001",
                "collector_area": "Admin port exposure evidence",
                "aws_action": "ec2:DescribeSecurityGroups",
                "permission_purpose": "Read security group rules to identify administrative port exposure.",
                "command_display": "Skipped because no AWS region is configured.",
                "command": [],
                "success_mode": "skipped",
                "policy_resource": "*",
                "recommended_policy_sid": "AllowDescribeSecurityGroups",
            }
        )

    return checks


def evaluate_checks(region: str) -> list[dict[str, str]]:
    results = []

    for check in build_checks(region):
        if check["success_mode"] == "skipped":
            status = "SKIPPED"
            interpretation = "No AWS region was configured, so this regional EC2 check was skipped."
        else:
            return_code, stdout, stderr = run_command(check["command"])
            status, interpretation = classify_command_result(
                return_code=return_code,
                stdout=stdout,
                stderr=stderr,
                success_mode=check["success_mode"],
            )

        results.append(
            {
                "check_id": check["check_id"],
                "collector_area": check["collector_area"],
                "aws_action": check["aws_action"],
                "status": status,
                "permission_purpose": check["permission_purpose"],
                "command_display": check["command_display"],
                "policy_resource": check["policy_resource"],
                "recommended_policy_sid": check["recommended_policy_sid"],
                "interpretation": interpretation,
            }
        )

    return results


def write_permissions_csv(results: list[dict[str, str]]) -> None:
    PERMISSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "check_id",
        "collector_area",
        "aws_action",
        "status",
        "permission_purpose",
        "command_display",
        "policy_resource",
        "recommended_policy_sid",
        "interpretation",
    ]

    with PERMISSIONS_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def overall_status(identity: dict[str, str], results: list[dict[str, str]]) -> str:
    if identity["identity_status"] != "AUTHENTICATED":
        return "REVIEW_REQUIRED"

    if any(result["status"] == "NOT_AUTHORIZED" for result in results):
        return "MISSING_PERMISSIONS"

    if any(result["status"] in {"REVIEW", "SKIPPED"} for result in results):
        return "REVIEW"

    return "PASS"


def write_playbook(region: str, identity: dict[str, str], results: list[dict[str, str]]) -> None:
    PLAYBOOK_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).date().isoformat()

    lines = [
        "# AWS Evidence Collector Permission Playbook",
        "",
        f"Date: `{timestamp}`",
        "",
        "## Purpose",
        "",
        "This playbook defines the read-only permissions needed by the AWS evidence collectors in this project.",
        "",
        "It exists so evidence collection failures can be interpreted as authorization findings instead of generic script failures.",
        "",
        "## Active Identity Context",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Identity status | `{identity['identity_status']}` |",
        f"| Account | `{identity['account_masked']}` |",
        f"| ARN | `{identity['arn_masked']}` |",
        f"| User ID | `{identity['user_id_masked']}` |",
        f"| Region | `{region or 'not_configured'}` |",
        "",
        "## Permission Check Results",
        "",
        "| Check | Collector Area | AWS Action | Status | Interpretation |",
        "|---|---|---|---|---|",
    ]

    for result in results:
        lines.append(
            f"| {result['check_id']} | {result['collector_area']} | "
            f"`{result['aws_action']}` | **{result['status']}** | {result['interpretation']} |"
        )

    missing_actions = [
        result for result in results if result["status"] == "NOT_AUTHORIZED"
    ]

    lines.extend(
        [
            "",
            "## Minimal Policy Snippets",
            "",
            "Use these only when the active lab principal needs the specific read-only evidence collection capability.",
            "",
        ]
    )

    if missing_actions:
        for result in missing_actions:
            lines.extend(
                [
                    f"### {result['recommended_policy_sid']}",
                    "",
                    "```json",
                    "{",
                    '  "Version": "2012-10-17",',
                    '  "Statement": [',
                    "    {",
                    f'      "Sid": "{result["recommended_policy_sid"]}",',
                    '      "Effect": "Allow",',
                    f'      "Action": "{result["aws_action"]}",',
                    f'      "Resource": "{result["policy_resource"]}"',
                    "    }",
                    "  ]",
                    "}",
                    "```",
                    "",
                ]
            )
    else:
        lines.append("No missing permissions were detected by this preflight.")
        lines.append("")

    lines.extend(
        [
            "## Governance Note",
            "",
            "The goal is not to give the lab principal broad administrative authority.",
            "",
            "The goal is to grant narrow read-only permissions that allow the project to collect evidence safely.",
            "",
            "## Decision Rule",
            "",
            "> If a collector requires a permission, document the action, purpose, resource scope, and evidence value before granting it.",
            "",
        ]
    )

    PLAYBOOK_FILE.write_text("\n".join(lines), encoding="utf-8")


def write_report(region: str, identity: dict[str, str], results: list[dict[str, str]]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    status = overall_status(identity, results)

    authorized_count = sum(1 for result in results if result["status"] == "AUTHORIZED")
    not_authorized_count = sum(1 for result in results if result["status"] == "NOT_AUTHORIZED")
    review_count = sum(1 for result in results if result["status"] == "REVIEW")
    skipped_count = sum(1 for result in results if result["status"] == "SKIPPED")

    lines = [
        "# AWS Evidence Collector Permission Preflight Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{status}**",
        "",
        "## Purpose",
        "",
        "This report checks whether the active AWS principal can run the read-only commands required by the project's AWS evidence collectors.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Identity status | `{identity['identity_status']}` |",
        f"| Region | `{region or 'not_configured'}` |",
        f"| Authorized checks | `{authorized_count}` |",
        f"| Not authorized checks | `{not_authorized_count}` |",
        f"| Review checks | `{review_count}` |",
        f"| Skipped checks | `{skipped_count}` |",
        "",
    ]

    if identity["identity_error"]:
        lines.extend(
            [
                "## Identity Error",
                "",
                "```text",
                identity["identity_error"],
                "```",
                "",
            ]
        )

    lines.extend(
        [
            "## Permission Results",
            "",
            "| Check | AWS Action | Status | Purpose |",
            "|---|---|---|---|",
        ]
    )

    for result in results:
        lines.append(
            f"| {result['check_id']} | `{result['aws_action']}` | "
            f"**{result['status']}** | {result['permission_purpose']} |"
        )

    lines.extend(
        [
            "",
            "## Control Mapping",
            "",
            "| Control Concept | Evidence Contribution |",
            "|---|---|",
            "| Least privilege | Identifies exactly which read-only actions are required for evidence collection. |",
            "| Evidence collection scope | Shows which collectors can run under the active principal. |",
            "| Authorization transparency | Turns denied AWS actions into documented findings. |",
            "| Audit readiness | Produces a record of required permissions, purpose, and status. |",
            "",
            "## Portfolio Relevance",
            "",
            "This artifact demonstrates safe cloud evidence automation by checking read-only collector permissions before running deeper evidence collection.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    region = get_region()
    identity = get_identity_context()
    results = evaluate_checks(region)

    write_permissions_csv(results)
    write_playbook(region, identity, results)
    write_report(region, identity, results)

    status = overall_status(identity, results)

    print(f"Permission CSV written to: {PERMISSIONS_FILE}")
    print(f"Permission playbook written to: {PLAYBOOK_FILE}")
    print(f"Evidence report written to: {REPORT_FILE}")
    print(f"Overall Status: {status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())