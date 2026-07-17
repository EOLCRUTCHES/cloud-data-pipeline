from pathlib import Path
from datetime import datetime, timezone
import csv
import subprocess
import sys


PREFLIGHT_SCRIPT = Path("src/check_aws_evidence_collector_permissions.py")
ADMIN_PORT_SCRIPT = Path("src/collect_aws_admin_port_exposure.py")

PERMISSION_CSV = Path("security/aws_evidence_collector_permissions.csv")
ADMIN_PORT_FINDINGS_CSV = Path("security/aws_admin_port_exposure_findings.csv")

PACKAGE_FILE = Path("docs/cloud/aws_admin_access_evidence_package.md")
WORKFLOW_REPORT_FILE = Path("evidence/generated/aws_admin_access_evidence_workflow_report.md")

REFERENCE_ARTIFACTS = [
    Path("docs/cloud/adr-001-cloud-admin-access-pattern.md"),
    Path("docs/cloud/cloud_admin_access_evidence_playbook.md"),
    Path("security/cloud_admin_access_evidence_requirements.csv"),
    Path("security/cloud_admin_access_exception_register.csv"),
    Path("docs/cloud/cloud_admin_access_decision_guide.md"),
    Path("docs/cloud/cloud_admin_access_field_cards.md"),
    Path("study/cloud_admin_access_quizlet.tsv"),
    Path("study/cloud_admin_access_flashcards.csv"),
]


def artifact_status(path: Path) -> str:
    """Return a simple artifact status."""
    if path.exists() and path.stat().st_size > 0:
        return "Present"
    if path.exists() and path.stat().st_size == 0:
        return "Empty"
    return "Missing"


def run_script(script_path: Path) -> dict[str, str]:
    """Run a Python script and capture output."""
    if not script_path.exists():
        return {
            "script": script_path.as_posix(),
            "status": "MISSING",
            "return_code": "not_run",
            "stdout": "",
            "stderr": f"Script not found: {script_path}",
        }

    result = subprocess.run(
        [sys.executable, script_path.as_posix()],
        capture_output=True,
        text=True,
        check=False,
    )

    return {
        "script": script_path.as_posix(),
        "status": "PASS" if result.returncode == 0 else "REVIEW",
        "return_code": str(result.returncode),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def read_permission_results() -> list[dict[str, str]]:
    """Read permission preflight CSV if present."""
    if not PERMISSION_CSV.exists() or PERMISSION_CSV.stat().st_size == 0:
        return []

    with PERMISSION_CSV.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def ec2_describe_security_groups_authorized(permission_results: list[dict[str, str]]) -> bool:
    """Check whether ec2:DescribeSecurityGroups is authorized."""
    for row in permission_results:
        if row.get("aws_action") == "ec2:DescribeSecurityGroups":
            return row.get("status") == "AUTHORIZED"

    return False


def summarize_permissions(permission_results: list[dict[str, str]]) -> dict[str, int]:
    """Summarize permission statuses."""
    summary = {
        "AUTHORIZED": 0,
        "NOT_AUTHORIZED": 0,
        "REVIEW": 0,
        "SKIPPED": 0,
        "OTHER": 0,
    }

    for row in permission_results:
        status = row.get("status", "OTHER")
        if status in summary:
            summary[status] += 1
        else:
            summary["OTHER"] += 1

    return summary


def read_admin_port_findings() -> list[dict[str, str]]:
    """Read admin port findings CSV if present."""
    if not ADMIN_PORT_FINDINGS_CSV.exists() or ADMIN_PORT_FINDINGS_CSV.stat().st_size == 0:
        return []

    with ADMIN_PORT_FINDINGS_CSV.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def summarize_findings(findings: list[dict[str, str]]) -> dict[str, int]:
    """Summarize admin port exposure findings."""
    summary = {
        "HIGH": 0,
        "MEDIUM": 0,
        "REVIEW": 0,
        "OTHER": 0,
    }

    for finding in findings:
        severity = finding.get("severity", "OTHER")
        if severity in summary:
            summary[severity] += 1
        else:
            summary["OTHER"] += 1

    return summary


def determine_workflow_status(
    preflight_run: dict[str, str],
    collector_run: dict[str, str] | None,
    permission_summary: dict[str, int],
    finding_summary: dict[str, int],
) -> str:
    """Determine the workflow status."""
    if preflight_run["status"] != "PASS":
        return "REVIEW_REQUIRED"

    if permission_summary["NOT_AUTHORIZED"] > 0:
        return "MISSING_PERMISSIONS"

    if collector_run is None:
        return "REVIEW"

    if collector_run["status"] != "PASS":
        return "REVIEW_REQUIRED"

    if finding_summary["HIGH"] > 0:
        return "REVIEW_REQUIRED"

    if finding_summary["MEDIUM"] > 0 or finding_summary["REVIEW"] > 0:
        return "REVIEW"

    return "PASS"


def write_package(
    workflow_status: str,
    permission_results: list[dict[str, str]],
    permission_summary: dict[str, int],
    findings: list[dict[str, str]],
    finding_summary: dict[str, int],
    collector_was_run: bool,
) -> None:
    """Write the human-facing evidence package summary."""
    PACKAGE_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).date().isoformat()

    lines = [
        "# AWS Cloud Administrative Access Evidence Package",
        "",
        f"Date: `{timestamp}`",
        "",
        f"Package Status: **{workflow_status}**",
        "",
        "## Purpose",
        "",
        "This package summarizes evidence related to AWS administrative access exposure and evidence-collector readiness.",
        "",
        "It ties together the architecture decision record, evidence playbook, permission preflight, and live security-group exposure collection.",
        "",
        "## Control Objective",
        "",
        "Administrative access should be authorized, minimized, segmented, monitored, attributable, time-appropriate, and reviewable.",
        "",
        "## Workflow Summary",
        "",
        "| Item | Value |",
        "|---|---|",
        f"| Permission checks evaluated | `{len(permission_results)}` |",
        f"| Authorized checks | `{permission_summary['AUTHORIZED']}` |",
        f"| Not authorized checks | `{permission_summary['NOT_AUTHORIZED']}` |",
        f"| Review checks | `{permission_summary['REVIEW']}` |",
        f"| Skipped checks | `{permission_summary['SKIPPED']}` |",
        f"| Admin port collector run | `{'Yes' if collector_was_run else 'No'}` |",
        f"| Admin port findings | `{len(findings)}` |",
        f"| High findings | `{finding_summary['HIGH']}` |",
        f"| Medium findings | `{finding_summary['MEDIUM']}` |",
        f"| Review findings | `{finding_summary['REVIEW']}` |",
        "",
        "## Permission Results",
        "",
        "| Collector Area | AWS Action | Status | Purpose |",
        "|---|---|---|---|",
    ]

    if permission_results:
        for row in permission_results:
            lines.append(
                f"| {row.get('collector_area', '')} | "
                f"`{row.get('aws_action', '')}` | "
                f"**{row.get('status', '')}** | "
                f"{row.get('permission_purpose', '')} |"
            )
    else:
        lines.append("| No permission results found | N/A | REVIEW | Run the permission preflight. |")

    lines.extend(
        [
            "",
            "## Admin Port Exposure Findings",
            "",
            "| Severity | Service | Port | Source Classification | Interpretation |",
            "|---|---|---:|---|---|",
        ]
    )

    if findings:
        for finding in findings:
            lines.append(
                f"| {finding.get('severity', '')} | "
                f"{finding.get('service', '')} | "
                f"{finding.get('port', '')} | "
                f"{finding.get('source_classification', '')} | "
                f"{finding.get('evidence_interpretation', '')} |"
            )
    else:
        if collector_was_run:
            lines.append("| PASS | None | N/A | N/A | No admin port exposure findings were detected. |")
        else:
            lines.append("| REVIEW | Not collected | N/A | N/A | Collector was not run because required permission was missing or skipped. |")

    lines.extend(
        [
            "",
            "## Required Follow-Up Logic",
            "",
            "- If permissions are missing, update IAM only with the narrow read-only permissions needed for evidence collection.",
            "- If high findings exist, review public administrative exposure immediately.",
            "- If medium or review findings exist, validate whether the access path matches the approved pattern or exception register.",
            "- If no findings exist, retain this package as evidence that the reviewed region had no detected admin-port exposure.",
            "",
            "## Related Artifacts",
            "",
            "| Artifact | Status |",
            "|---|---|",
        ]
    )

    for path in REFERENCE_ARTIFACTS:
        lines.append(f"| `{path.as_posix()}` | {artifact_status(path)} |")

    lines.extend(
        [
            f"| `{PERMISSION_CSV.as_posix()}` | {artifact_status(PERMISSION_CSV)} |",
            f"| `{ADMIN_PORT_FINDINGS_CSV.as_posix()}` | {artifact_status(ADMIN_PORT_FINDINGS_CSV)} |",
            "",
            "## Executive Summary Language",
            "",
            "> We have a documented administrative-access standard, a permission preflight for evidence collection, and a read-only collector that tests security-group exposure for administrative ports. The evidence package shows whether the collector had permission to run and whether admin-port exposure was detected.",
            "",
        ]
    )

    PACKAGE_FILE.write_text("\n".join(lines), encoding="utf-8")


def write_workflow_report(
    workflow_status: str,
    preflight_run: dict[str, str],
    collector_run: dict[str, str] | None,
    collector_was_run: bool,
    permission_summary: dict[str, int],
    finding_summary: dict[str, int],
) -> None:
    """Write workflow execution report."""
    WORKFLOW_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# AWS Admin Access Evidence Workflow Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{workflow_status}**",
        "",
        "## Purpose",
        "",
        "This report records execution of the AWS cloud administrative access evidence workflow.",
        "",
        "The workflow runs permission preflight first, then runs the admin-port exposure collector only if the required EC2 read permission is authorized.",
        "",
        "## Workflow Steps",
        "",
        "| Step | Script | Status | Return Code |",
        "|---|---|---|---|",
        f"| Permission preflight | `{preflight_run['script']}` | {preflight_run['status']} | {preflight_run['return_code']} |",
    ]

    if collector_run is not None:
        lines.append(
            f"| Admin port exposure collector | `{collector_run['script']}` | "
            f"{collector_run['status']} | {collector_run['return_code']} |"
        )
    else:
        lines.append(
            "| Admin port exposure collector | `src/collect_aws_admin_port_exposure.py` | SKIPPED | not_run |"
        )

    lines.extend(
        [
            "",
            "## Permission Summary",
            "",
            "| Status | Count |",
            "|---|---:|",
        ]
    )

    for key, value in permission_summary.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## Finding Summary",
            "",
            "| Severity | Count |",
            "|---|---:|",
        ]
    )

    for key, value in finding_summary.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## Collector Execution Decision",
            "",
            f"- Collector was run: `{'Yes' if collector_was_run else 'No'}`",
            "",
            "## Generated Package",
            "",
            f"- `{PACKAGE_FILE.as_posix()}`",
            "",
            "## Portfolio Relevance",
            "",
            "This workflow demonstrates controlled cloud evidence collection: preflight authorization first, live read-only evidence collection second, and package-level reporting last.",
            "",
        ]
    )

    WORKFLOW_REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    preflight_run = run_script(PREFLIGHT_SCRIPT)
    permission_results = read_permission_results()
    permission_summary = summarize_permissions(permission_results)

    collector_was_run = ec2_describe_security_groups_authorized(permission_results)
    collector_run = None

    if collector_was_run:
        collector_run = run_script(ADMIN_PORT_SCRIPT)

    findings = read_admin_port_findings() if collector_was_run else []
    finding_summary = summarize_findings(findings)

    workflow_status = determine_workflow_status(
        preflight_run=preflight_run,
        collector_run=collector_run,
        permission_summary=permission_summary,
        finding_summary=finding_summary,
    )

    write_package(
        workflow_status=workflow_status,
        permission_results=permission_results,
        permission_summary=permission_summary,
        findings=findings,
        finding_summary=finding_summary,
        collector_was_run=collector_was_run,
    )

    write_workflow_report(
        workflow_status=workflow_status,
        preflight_run=preflight_run,
        collector_run=collector_run,
        collector_was_run=collector_was_run,
        permission_summary=permission_summary,
        finding_summary=finding_summary,
    )

    print(f"Evidence package written to: {PACKAGE_FILE}")
    print(f"Workflow report written to: {WORKFLOW_REPORT_FILE}")
    print(f"Collector run: {'Yes' if collector_was_run else 'No'}")
    print(f"Overall Status: {workflow_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())