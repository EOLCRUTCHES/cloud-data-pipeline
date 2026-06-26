from pathlib import Path
import csv
from datetime import datetime, timezone


MATRIX_FILE = Path("security/cloud_admin_access_patterns.csv")
REPORT_FILE = Path("evidence/generated/cloud_admin_access_pattern_report.md")


PATTERNS = [
    {
        "pattern": "Direct public SSH/RDP",
        "on_prem_analogy": "Remote admin directly exposed through a firewall rule",
        "cloud_implementation": "Instances with public IPs and security group ingress for SSH/RDP",
        "primary_risk_reduced": "Low setup friction",
        "risk_introduced": "Broad attack surface and high exposure to credential attacks",
        "evidence_to_collect": "Public IP presence, security group ingress on 22/3389, route to internet gateway, CloudTrail access events",
        "maturity_read": "Usually weak except for tightly controlled temporary lab use",
        "aws_reference": "EC2 public IPs, security groups, NACLs, route tables, CloudTrail",
        "azure_equivalent": "VM public IP, NSG inbound rules, Azure Bastion alternative, Activity Logs",
        "gcp_equivalent": "Compute Engine external IPs, firewall rules, IAP alternative, Cloud Audit Logs",
        "oci_equivalent": "Compute public IPs, security lists/NSGs, Bastion service alternative, Audit logs",
    },
    {
        "pattern": "Bastion host / jump box",
        "on_prem_analogy": "Hardened jump server between remote admins and internal servers",
        "cloud_implementation": "A hardened instance in a public subnet used to reach private instances",
        "primary_risk_reduced": "Reduces direct public exposure of private workloads",
        "risk_introduced": "Creates a high-value choke point that must be patched, monitored, and tightly controlled",
        "evidence_to_collect": "Bastion security group ingress, private instance ingress from bastion only, OS patch evidence, session logs, CloudTrail events",
        "maturity_read": "Common transitional pattern; acceptable when hardened and monitored",
        "aws_reference": "EC2 bastion, public/private subnets, security groups, CloudTrail, CloudWatch logs",
        "azure_equivalent": "Azure Bastion or jump VM, VNets, NSGs, Monitor logs",
        "gcp_equivalent": "Bastion VM, VPC firewall rules, Cloud Logging, IAP alternative",
        "oci_equivalent": "OCI Bastion service or jump host, VCN, NSGs/security lists, Audit logs",
    },
    {
        "pattern": "VPN or private connectivity",
        "on_prem_analogy": "Corporate VPN into internal network before server administration",
        "cloud_implementation": "Private network path into VPC/VNet/VCN before administrative access",
        "primary_risk_reduced": "Removes administrative access from the public internet",
        "risk_introduced": "Network access may become too broad if segmentation and identity controls are weak",
        "evidence_to_collect": "VPN configuration, route tables, allowed source ranges, security group rules, authentication logs",
        "maturity_read": "Strong when paired with segmentation, MFA, and least privilege",
        "aws_reference": "Site-to-Site VPN, Client VPN, Direct Connect, route tables, security groups",
        "azure_equivalent": "VPN Gateway, ExpressRoute, VNets, NSGs",
        "gcp_equivalent": "Cloud VPN, Cloud Interconnect, VPC firewall rules",
        "oci_equivalent": "IPSec VPN, FastConnect, VCN route tables, NSGs/security lists",
    },
    {
        "pattern": "Identity-aware session management",
        "on_prem_analogy": "Privileged access broker that opens audited admin sessions without broad network exposure",
        "cloud_implementation": "Admin sessions authorized through cloud identity and agent/service control plane",
        "primary_risk_reduced": "Avoids inbound SSH/RDP exposure and centralizes session authorization/logging",
        "risk_introduced": "Depends heavily on identity policy, agent health, logging configuration, and service availability",
        "evidence_to_collect": "Managed instance status, IAM permissions, session logs, CloudTrail events, disabled inbound admin ports",
        "maturity_read": "Often stronger than classic bastion when implemented with logging and least privilege",
        "aws_reference": "AWS Systems Manager Session Manager, IAM, SSM Agent, CloudTrail, CloudWatch/S3 session logs",
        "azure_equivalent": "Azure Bastion, Entra ID, Just-in-time VM access, Defender for Cloud, Monitor logs",
        "gcp_equivalent": "Identity-Aware Proxy TCP forwarding, OS Login, IAM, Cloud Audit Logs",
        "oci_equivalent": "OCI Bastion service, IAM policies, Audit logs",
    },
    {
        "pattern": "Privileged access workflow",
        "on_prem_analogy": "PAM-approved admin access with time-bound elevation and approval trail",
        "cloud_implementation": "Just-in-time privileged access with approval, temporary credentials, and auditable session records",
        "primary_risk_reduced": "Limits standing administrative privilege",
        "risk_introduced": "Workflow complexity can create bypasses if emergency access is unmanaged",
        "evidence_to_collect": "Approval record, temporary access duration, role assumption logs, session recording, break-glass review",
        "maturity_read": "High maturity for regulated or high-risk environments",
        "aws_reference": "IAM Identity Center, STS role assumption, IAM Access Analyzer, CloudTrail",
        "azure_equivalent": "Entra Privileged Identity Management, RBAC, Activity Logs",
        "gcp_equivalent": "Privileged Access Manager, IAM Conditions, Cloud Audit Logs",
        "oci_equivalent": "IAM policies, identity domains, Audit logs, third-party PAM integration",
    },
]


def write_matrix() -> None:
    MATRIX_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "pattern",
        "on_prem_analogy",
        "cloud_implementation",
        "primary_risk_reduced",
        "risk_introduced",
        "evidence_to_collect",
        "maturity_read",
        "aws_reference",
        "azure_equivalent",
        "gcp_equivalent",
        "oci_equivalent",
    ]

    with MATRIX_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(PATTERNS)


def write_report() -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Cloud Administrative Access Pattern Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        "## Purpose",
        "",
        "This report compares common administrative access patterns across cloud environments.",
        "",
        "The goal is to translate familiar on-prem systems engineering concepts into cloud architecture, risk, and evidence terms.",
        "",
        "## Executive Summary",
        "",
        "Administrative access is not a single control. It is a pattern made from identity, network exposure, session control, logging, and evidence retention.",
        "",
        "A bastion host is one pattern, not the goal itself. The goal is controlled, monitored, least-privilege administrative access.",
        "",
        "## Pattern Comparison",
        "",
        "| Pattern | On-Prem Analogy | Risk Reduced | Risk Introduced | Maturity Read |",
        "|---|---|---|---|---|",
    ]

    for item in PATTERNS:
        lines.append(
            f"| {item['pattern']} | {item['on_prem_analogy']} | "
            f"{item['primary_risk_reduced']} | {item['risk_introduced']} | "
            f"{item['maturity_read']} |"
        )

    lines.extend(
        [
            "",
            "## Evidence Collection Focus",
            "",
            "| Pattern | Evidence to Collect |",
            "|---|---|",
        ]
    )

    for item in PATTERNS:
        lines.append(f"| {item['pattern']} | {item['evidence_to_collect']} |")

    lines.extend(
        [
            "",
            "## Multi-Cloud Translation",
            "",
            "| Pattern | AWS | Azure | GCP | OCI |",
            "|---|---|---|---|---|",
        ]
    )

    for item in PATTERNS:
        lines.append(
            f"| {item['pattern']} | {item['aws_reference']} | "
            f"{item['azure_equivalent']} | {item['gcp_equivalent']} | "
            f"{item['oci_equivalent']} |"
        )

    lines.extend(
        [
            "",
            "## Control Interpretation",
            "",
            "The control objective is not to require a bastion host.",
            "",
            "The control objective is to ensure administrative access is authorized, minimized, segmented, monitored, and reviewable.",
            "",
            "## Portfolio Relevance",
            "",
            "This artifact demonstrates cloud architecture judgment by comparing implementation patterns instead of memorizing cloud vocabulary.",
            "",
            "It supports secure automation by defining what evidence should be collected to evaluate administrative access patterns.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    write_matrix()
    write_report()

    print(f"Cloud admin access pattern matrix written to: {MATRIX_FILE}")
    print(f"Cloud admin access pattern report written to: {REPORT_FILE}")
    print("Overall Status: PASS")


if __name__ == "__main__":
    main()