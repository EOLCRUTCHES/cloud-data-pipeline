from pathlib import Path
from datetime import datetime, timezone
import csv
import subprocess
import sys


WORKFLOW_SCRIPT = Path("src/run_aws_admin_access_evidence_workflow.py")

ADMIN_PORT_FINDINGS_CSV = Path("security/aws_admin_port_exposure_findings.csv")
WORKFLOW_REPORT = Path("evidence/generated/aws_admin_access_evidence_workflow_report.md")
EVIDENCE_PACKAGE = Path("docs/cloud/aws_admin_access_evidence_package.md")

REMEDIATION_REGISTER = Path("security/aws_admin_port_remediation_register.csv")
REMEDIATION_RECORD = Path("docs/cloud/aws_admin_port_remediation_record.md")
REPORT_FILE = Path("evidence/generated/aws_admin_port_remediation_evidence_report.md")


def artifact_status(path: Path) -> str:
    if path.exists() and path.stat().st_size > 0:
        return "Present"
    if path.exists() and path.stat().st_size == 0:
        return "Empty"
    return "Missing"


def run_script(script_path: Path) -> dict[str, str]:
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


def parse_collector_run(workflow_run: dict[str, str]) -> str:
    stdout = workflow_run.get("stdout", "")

    if "Collector run: Yes" in stdout:
        return "Yes"

    if "Collector run: No" in stdout:
        return "No"

    if WORKFLOW_REPORT.exists() and WORKFLOW_REPORT.stat().st_size > 0:
        text = WORKFLOW_REPORT.read_text(encoding="utf-8", errors="replace")
        if "Collector was run: `Yes`" in text:
            return "Yes"
        if "Collector was run: `No`" in text:
            return "No"

    return "Unknown"


def read_findings(collector_run: str) -> list[dict[str, str]]:
    if collector_run != "Yes":
        return []

    if not ADMIN_PORT_FINDINGS_CSV.exists() or ADMIN_PORT_FINDINGS_CSV.stat().st_size == 0:
        return []

    with ADMIN_PORT_FINDINGS_CSV.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def summarize_findings(findings: list[dict[str, str]]) -> dict[str, int]:
    summary = {
        "total": len(findings),
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


def determine_closure_status(
    workflow_run: dict[str, str],
    collector_run: str,
    finding_summary: dict[str, int],
) -> str:
    if workflow_run["status"] != "PASS":
        return "REVIEW_REQUIRED_WORKFLOW_FAILED"

    if collector_run != "Yes":
        return "EVIDENCE_INCOMPLETE_COLLECTOR_NOT_RUN"

    if finding_summary["HIGH"] > 0:
        return "REVIEW_REQUIRED_PUBLIC_EXPOSURE_REMAINS"

    if finding_summary["MEDIUM"] > 0 or finding_summary["REVIEW"] > 0:
        return "PUBLIC_EXPOSURE_CLEARED_REVIEW_REMAINS"

    return "PUBLIC_ADMIN_EXPOSURE_CLEARED_PENDING_REVIEW"


def write_remediation_register(
    closure_status: str,
    collector_run: str,
    finding_summary: dict[str, int],
) -> None:
    REMEDIATION_REGISTER.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    row = {
        "remediation_id": "RMD-AWS-ADMIN-001",
        "control_area": "Cloud administrative access",
        "issue": "Public administrative port exposure in EC2 security group rule",
        "remediation_action": "Removed public inbound administrative access rule from EC2 security group configuration",
        "remediation_basis": "User-reported manual remediation plus post-remediation evidence workflow rerun",
        "before_evidence_source": "Earlier collector finding or console observation; retain prior artifact or Git history if full before/after proof is required",
        "after_evidence_source": EVIDENCE_PACKAGE.as_posix(),
        "collector_run": collector_run,
        "total_findings_after": str(finding_summary["total"]),
        "high_findings_after": str(finding_summary["HIGH"]),
        "medium_findings_after": str(finding_summary["MEDIUM"]),
        "review_findings_after": str(finding_summary["REVIEW"]),
        "closure_status": closure_status,
        "evidence_limitation": "This record proves current post-remediation status only if before evidence was not retained separately",
        "generated_at": timestamp,
    }

    fieldnames = list(row.keys())

    with REMEDIATION_REGISTER.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)


def write_remediation_record(
    closure_status: str,
    workflow_run: dict[str, str],
    collector_run: str,
    finding_summary: dict[str, int],
) -> None:
    REMEDIATION_RECORD.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# AWS Admin Port Remediation Record",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Closure Status: **{closure_status}**",
        "",
        "## Purpose",
        "",
        "This record documents remediation evidence for public administrative port exposure in AWS EC2 security group configuration.",
        "",
        "## Remediation Summary",
        "",
        "| Field | Value |",
        "|---|---|",
        "| Remediation ID | `RMD-AWS-ADMIN-001` |",
        "| Issue | Public administrative port exposure in EC2 security group rule |",
        "| Action | Removed public inbound administrative access rule |",
        "| Evidence workflow run | `" + workflow_run["status"] + "` |",
        "| Collector run | `" + collector_run + "` |",
        f"| Total findings after remediation | `{finding_summary['total']}` |",
        f"| High findings after remediation | `{finding_summary['HIGH']}` |",
        f"| Medium findings after remediation | `{finding_summary['MEDIUM']}` |",
        f"| Review findings after remediation | `{finding_summary['REVIEW']}` |",
        "",
        "## Evidence Chain",
        "",
        "```text",
        "Admin-port exposure identified",
        "↓",
        "Security group rule remediated",
        "↓",
        "AWS admin access evidence workflow rerun",
        "↓",
        "Current findings summarized",
        "↓",
        "Remediation closure record generated",
        "```",
        "",
        "## Related Evidence",
        "",
        "| Artifact | Status |",
        "|---|---|",
        f"| `{ADMIN_PORT_FINDINGS_CSV.as_posix()}` | {artifact_status(ADMIN_PORT_FINDINGS_CSV)} |",
        f"| `{WORKFLOW_REPORT.as_posix()}` | {artifact_status(WORKFLOW_REPORT)} |",
        f"| `{EVIDENCE_PACKAGE.as_posix()}` | {artifact_status(EVIDENCE_PACKAGE)} |",
        f"| `{REMEDIATION_REGISTER.as_posix()}` | {artifact_status(REMEDIATION_REGISTER)} |",
        "",
        "## Evidence Limitation",
        "",
        "This record is strongest when paired with retained before-evidence showing the original exposure.",
        "",
        "If the earlier finding was overwritten, this artifact should be treated as current-state remediation evidence plus a manual remediation claim, not a complete immutable before/after chain.",
        "",
        "## Reviewer Decision",
        "",
    ]

    if closure_status == "PUBLIC_ADMIN_EXPOSURE_CLEARED_PENDING_REVIEW":
        lines.extend(
            [
                "The post-remediation workflow did not detect high-severity public administrative port exposure.",
                "",
                "Recommended disposition: close the public-exposure issue after human review.",
                "",
            ]
        )
    elif closure_status == "PUBLIC_EXPOSURE_CLEARED_REVIEW_REMAINS":
        lines.extend(
            [
                "High-severity public exposure was not detected, but medium or review findings remain.",
                "",
                "Recommended disposition: close the public-exposure issue only after reviewing remaining findings.",
                "",
            ]
        )
    elif closure_status == "REVIEW_REQUIRED_PUBLIC_EXPOSURE_REMAINS":
        lines.extend(
            [
                "High-severity public administrative port exposure remains after remediation.",
                "",
                "Recommended disposition: keep the issue open and remediate remaining public exposure.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "The evidence workflow did not produce a complete post-remediation collection result.",
                "",
                "Recommended disposition: keep the issue open until the collector runs successfully.",
                "",
            ]
        )

    lines.extend(
        [
            "## One-Sentence Takeaway",
            "",
            "> A remediation is not complete until the fix is followed by evidence that the risk state changed.",
            "",
        ]
    )

    REMEDIATION_RECORD.write_text("\n".join(lines), encoding="utf-8")


def write_report(
    closure_status: str,
    workflow_run: dict[str, str],
    collector_run: str,
    finding_summary: dict[str, int],
) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# AWS Admin Port Remediation Evidence Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{closure_status}**",
        "",
        "## Purpose",
        "",
        "This report records generation of a remediation evidence package for AWS administrative port exposure.",
        "",
        "## Workflow Execution",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Workflow script | `{WORKFLOW_SCRIPT.as_posix()}` |",
        f"| Workflow status | `{workflow_run['status']}` |",
        f"| Workflow return code | `{workflow_run['return_code']}` |",
        f"| Collector run | `{collector_run}` |",
        "",
        "## Post-Remediation Finding Summary",
        "",
        "| Severity | Count |",
        "|---|---:|",
        f"| HIGH | `{finding_summary['HIGH']}` |",
        f"| MEDIUM | `{finding_summary['MEDIUM']}` |",
        f"| REVIEW | `{finding_summary['REVIEW']}` |",
        f"| OTHER | `{finding_summary['OTHER']}` |",
        f"| TOTAL | `{finding_summary['total']}` |",
        "",
        "## Generated Artifacts",
        "",
        f"- `{REMEDIATION_REGISTER.as_posix()}`",
        f"- `{REMEDIATION_RECORD.as_posix()}`",
        f"- `{REPORT_FILE.as_posix()}`",
        "",
        "## Control Mapping",
        "",
        "| Control Concept | Evidence Contribution |",
        "|---|---|",
        "| Remediation tracking | Captures the security issue, action taken, current findings, and closure status. |",
        "| Evidence-based closure | Requires a post-remediation workflow run before closure. |",
        "| Reviewer accountability | Marks closure as pending review instead of silently auto-closing. |",
        "| Evidence limitation | Distinguishes current-state proof from full before/after proof. |",
        "",
    ]

    if workflow_run["stderr"]:
        lines.extend(
            [
                "## Workflow Error Output",
                "",
                "```text",
                workflow_run["stderr"],
                "```",
                "",
            ]
        )

    lines.extend(
        [
            "## One-Sentence Takeaway",
            "",
            "> Security remediation needs closure evidence, not just a claim that the setting was fixed.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    workflow_run = run_script(WORKFLOW_SCRIPT)
    collector_run = parse_collector_run(workflow_run)
    findings = read_findings(collector_run)
    finding_summary = summarize_findings(findings)

    closure_status = determine_closure_status(
        workflow_run=workflow_run,
        collector_run=collector_run,
        finding_summary=finding_summary,
    )

    write_remediation_register(
        closure_status=closure_status,
        collector_run=collector_run,
        finding_summary=finding_summary,
    )

    write_remediation_record(
        closure_status=closure_status,
        workflow_run=workflow_run,
        collector_run=collector_run,
        finding_summary=finding_summary,
    )

    write_report(
        closure_status=closure_status,
        workflow_run=workflow_run,
        collector_run=collector_run,
        finding_summary=finding_summary,
    )

    print(f"Remediation register written to: {REMEDIATION_REGISTER}")
    print(f"Remediation record written to: {REMEDIATION_RECORD}")
    print(f"Remediation report written to: {REPORT_FILE}")
    print(f"Collector run: {collector_run}")
    print(f"High findings after remediation: {finding_summary['HIGH']}")
    print(f"Overall Status: {closure_status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())