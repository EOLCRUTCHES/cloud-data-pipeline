from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import ipaddress
import json
import os
import subprocess
import sys


FINDINGS_FILE = Path("security/aws_admin_port_exposure_findings.csv")
REPORT_FILE = Path("evidence/generated/aws_admin_port_exposure_report.md")

ADMIN_PORTS = [
    {"port": 22, "service": "SSH"},
    {"port": 3389, "service": "RDP"},
    {"port": 5985, "service": "WinRM HTTP"},
    {"port": 5986, "service": "WinRM HTTPS"},
]


def stable_mask(value: str, label: str) -> str:
    """Return a stable masked identifier for portfolio-safe evidence."""
    if not value:
        return "not_present"

    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    return f"{label}_{digest}"


def run_command(command: list[str]) -> tuple[int, str, str]:
    """Run a command and return return code, stdout, stderr."""
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_aws_region() -> str:
    """Find AWS region from environment or AWS config."""
    env_region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")

    if env_region:
        return env_region

    return_code, stdout, _stderr = run_command(["aws", "configure", "get", "region"])

    if return_code == 0 and stdout:
        return stdout

    return ""


def classify_cidr(cidr_value: str) -> str:
    """Classify a CIDR without exposing sensitive non-public details."""
    if not cidr_value:
        return "unknown"

    try:
        network = ipaddress.ip_network(cidr_value, strict=False)
    except ValueError:
        return "invalid_cidr"

    if str(network) in {"0.0.0.0/0", "::/0"}:
        return "public_internet"

    if network.is_private:
        return "private_cidr"

    return "external_cidr"


def sanitize_source(source_type: str, source_value: str) -> str:
    """Sanitize source values for portfolio-safe output."""
    if not source_value:
        return "not_present"

    if source_value in {"0.0.0.0/0", "::/0"}:
        return source_value

    if source_type == "security_group_reference":
        return stable_mask(source_value, "sg_ref")

    cidr_class = classify_cidr(source_value)

    if cidr_class == "private_cidr":
        return "private_cidr_masked"

    if cidr_class == "external_cidr":
        return stable_mask(source_value, "external_cidr")

    return stable_mask(source_value, "source")


def port_matches(permission: dict, target_port: int) -> bool:
    """Determine whether a security-group permission includes a target admin port."""
    protocol = permission.get("IpProtocol")

    if protocol == "-1":
        return True

    if protocol not in {"tcp", "6"}:
        return False

    from_port = permission.get("FromPort")
    to_port = permission.get("ToPort")

    if from_port is None or to_port is None:
        return False

    return int(from_port) <= target_port <= int(to_port)


def source_records(permission: dict) -> list[dict[str, str]]:
    """Extract source records from a security-group permission."""
    records = []

    for item in permission.get("IpRanges", []):
        cidr = item.get("CidrIp", "")
        records.append(
            {
                "source_type": "ipv4_cidr",
                "source_value": cidr,
                "source_classification": classify_cidr(cidr),
                "source_display": sanitize_source("ipv4_cidr", cidr),
            }
        )

    for item in permission.get("Ipv6Ranges", []):
        cidr = item.get("CidrIpv6", "")
        records.append(
            {
                "source_type": "ipv6_cidr",
                "source_value": cidr,
                "source_classification": classify_cidr(cidr),
                "source_display": sanitize_source("ipv6_cidr", cidr),
            }
        )

    for item in permission.get("UserIdGroupPairs", []):
        group_id = item.get("GroupId", "")
        records.append(
            {
                "source_type": "security_group_reference",
                "source_value": group_id,
                "source_classification": "security_group_reference",
                "source_display": sanitize_source("security_group_reference", group_id),
            }
        )

    if not records:
        records.append(
            {
                "source_type": "unknown",
                "source_value": "",
                "source_classification": "unknown",
                "source_display": "not_present",
            }
        )

    return records


def severity_for_source(source_classification: str) -> str:
    """Assign severity based on source classification."""
    if source_classification == "public_internet":
        return "HIGH"

    if source_classification == "external_cidr":
        return "MEDIUM"

    if source_classification in {"private_cidr", "security_group_reference"}:
        return "REVIEW"

    return "REVIEW"


def collect_security_groups(region: str) -> tuple[str, list[dict]]:
    """Collect security groups using AWS CLI."""
    command = [
        "aws",
        "ec2",
        "describe-security-groups",
        "--region",
        region,
        "--output",
        "json",
    ]

    return_code, stdout, stderr = run_command(command)

    if return_code != 0:
        return stderr or "AWS CLI command failed without stderr.", []

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return f"Failed to parse AWS CLI JSON output: {exc}", []

    return "", data.get("SecurityGroups", [])


def analyze_security_groups(security_groups: list[dict], region: str) -> list[dict[str, str]]:
    """Analyze security groups for administrative port exposure."""
    findings = []

    for group in security_groups:
        group_id = group.get("GroupId", "")
        group_name = group.get("GroupName", "")
        vpc_id = group.get("VpcId", "")

        masked_group_id = stable_mask(group_id, "sg")
        masked_group_name = stable_mask(group_name, "sg_name")
        masked_vpc_id = stable_mask(vpc_id, "vpc") if vpc_id else "classic_or_not_present"

        for permission in group.get("IpPermissions", []):
            protocol = permission.get("IpProtocol", "unknown")
            from_port = permission.get("FromPort", "all")
            to_port = permission.get("ToPort", "all")

            for admin_port in ADMIN_PORTS:
                port = admin_port["port"]
                service = admin_port["service"]

                if not port_matches(permission, port):
                    continue

                for source in source_records(permission):
                    finding = {
                        "region": region,
                        "security_group_id_masked": masked_group_id,
                        "security_group_name_masked": masked_group_name,
                        "vpc_id_masked": masked_vpc_id,
                        "service": service,
                        "port": str(port),
                        "protocol": str(protocol),
                        "rule_from_port": str(from_port),
                        "rule_to_port": str(to_port),
                        "source_type": source["source_type"],
                        "source_classification": source["source_classification"],
                        "source_display": source["source_display"],
                        "severity": severity_for_source(source["source_classification"]),
                        "evidence_interpretation": (
                            f"{service} exposure detected from "
                            f"{source['source_classification']} source."
                        ),
                    }
                    findings.append(finding)

    return findings


def write_findings_csv(findings: list[dict[str, str]]) -> None:
    """Write findings CSV."""
    FINDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "region",
        "security_group_id_masked",
        "security_group_name_masked",
        "vpc_id_masked",
        "service",
        "port",
        "protocol",
        "rule_from_port",
        "rule_to_port",
        "source_type",
        "source_classification",
        "source_display",
        "severity",
        "evidence_interpretation",
    ]

    with FINDINGS_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(findings)


def overall_status(findings: list[dict[str, str]], collection_error: str) -> str:
    """Determine overall status."""
    if collection_error:
        return "REVIEW"

    if any(finding["severity"] == "HIGH" for finding in findings):
        return "REVIEW_REQUIRED"

    if findings:
        return "REVIEW"

    return "PASS"


def write_report(
    region: str,
    security_group_count: int,
    findings: list[dict[str, str]],
    collection_error: str,
) -> None:
    """Write markdown evidence report."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    status = overall_status(findings, collection_error)

    high_count = sum(1 for finding in findings if finding["severity"] == "HIGH")
    medium_count = sum(1 for finding in findings if finding["severity"] == "MEDIUM")
    review_count = sum(1 for finding in findings if finding["severity"] == "REVIEW")

    lines = [
        "# AWS Admin Port Exposure Evidence Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        f"Overall Status: **{status}**",
        "",
        "## Purpose",
        "",
        "This report collects read-only AWS security group evidence for administrative port exposure.",
        "",
        "It supports the cloud administrative access ADR by identifying whether SSH, RDP, or WinRM ports are exposed and what source category can reach them.",
        "",
        "## Collection Summary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| AWS region | `{region or 'not_resolved'}` |",
        f"| Security groups evaluated | `{security_group_count}` |",
        f"| Findings | `{len(findings)}` |",
        f"| High findings | `{high_count}` |",
        f"| Medium findings | `{medium_count}` |",
        f"| Review findings | `{review_count}` |",
        "",
    ]

    if collection_error:
        lines.extend(
            [
                "## Collection Error",
                "",
                "The collector could not retrieve AWS security group evidence.",
                "",
                "```text",
                collection_error,
                "```",
                "",
                "### Likely Cause",
                "",
                "The active AWS principal may not have `ec2:DescribeSecurityGroups`, the default region may be missing, or the AWS CLI profile may not be configured.",
                "",
            ]
        )

    if findings:
        lines.extend(
            [
                "## Findings",
                "",
                "| Severity | Service | Port | Source Classification | Security Group | Interpretation |",
                "|---|---|---:|---|---|---|",
            ]
        )

        for finding in findings:
            lines.append(
                f"| {finding['severity']} | {finding['service']} | {finding['port']} | "
                f"{finding['source_classification']} | {finding['security_group_id_masked']} | "
                f"{finding['evidence_interpretation']} |"
            )
    else:
        lines.extend(
            [
                "## Findings",
                "",
                "No administrative port exposure findings were detected from the collected security groups.",
                "",
            ]
        )

    lines.extend(
        [
            "",
            "## Evidence Interpretation",
            "",
            "- `HIGH` means an administrative port appears reachable from the public internet.",
            "- `MEDIUM` means an administrative port appears reachable from a non-private external CIDR.",
            "- `REVIEW` means an administrative port appears reachable from a private CIDR or security group reference and should be validated against the approved access pattern.",
            "",
            "## Control Mapping",
            "",
            "| Control Objective | Evidence Contribution |",
            "|---|---|",
            "| No unnecessary public admin ports | Identifies SSH/RDP/WinRM exposure by source category. |",
            "| Controlled administrative access path | Shows whether access appears direct, private, or mediated through security group references. |",
            "| Exception ownership and expiration | Findings can be reconciled against the exception register. |",
            "| Session logging and auditability | Findings identify where access path review should be paired with CloudTrail/session log review. |",
            "",
            "## Portfolio Relevance",
            "",
            "This artifact demonstrates live cloud evidence collection tied to a documented architecture decision.",
            "",
            "It moves the project from cloud vocabulary and policy language into implementation evidence.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    region = get_aws_region()

    if not region:
        collection_error = (
            "No AWS region found. Set AWS_REGION or AWS_DEFAULT_REGION, "
            "or run: aws configure set region us-east-1"
        )
        security_groups = []
    else:
        collection_error, security_groups = collect_security_groups(region)

    findings = analyze_security_groups(security_groups, region) if not collection_error else []

    write_findings_csv(findings)
    write_report(
        region=region,
        security_group_count=len(security_groups),
        findings=findings,
        collection_error=collection_error,
    )

    print(f"Findings CSV written to: {FINDINGS_FILE}")
    print(f"Evidence report written to: {REPORT_FILE}")
    print(f"Security groups evaluated: {len(security_groups)}")
    print(f"Findings: {len(findings)}")
    print(f"Overall Status: {overall_status(findings, collection_error)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())