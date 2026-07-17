from pathlib import Path
from datetime import datetime, timezone
import csv


EVIDENCE_REQUIREMENTS_FILE = Path("security/cloud_admin_access_evidence_requirements.csv")
EXCEPTION_REGISTER_FILE = Path("security/cloud_admin_access_exception_register.csv")
PLAYBOOK_FILE = Path("docs/cloud/cloud_admin_access_evidence_playbook.md")
REPORT_FILE = Path("evidence/generated/cloud_admin_access_evidence_kit_report.md")

REFERENCE_ARTIFACTS = [
    Path("docs/cloud/adr-001-cloud-admin-access-pattern.md"),
    Path("docs/cloud/cloud_admin_access_decision_guide.md"),
    Path("security/cloud_admin_access_decision_rubric.csv"),
    Path("docs/cloud/cloud_admin_access_field_cards.md"),
]


EVIDENCE_REQUIREMENTS = [
    {
        "control_objective": "Authorized administrative identities",
        "evidence_question": "Who is allowed to administer cloud workloads?",
        "minimum_evidence": "IAM users/roles/groups, identity provider groups, privileged role assignments, access review records",
        "aws_evidence": "IAM roles, IAM Identity Center assignments, CloudTrail AssumeRole or StartSession events",
        "azure_evidence": "Entra ID groups, Azure RBAC assignments, PIM activations, Activity Logs",
        "gcp_evidence": "IAM allow policies, group membership, OS Login configuration, Cloud Audit Logs",
        "oci_evidence": "IAM policies, identity domains, dynamic groups, Audit logs",
        "risk_if_missing": "Administrative access cannot be tied to approved identities.",
        "review_frequency": "Monthly for production; quarterly for lower-risk environments",
    },
    {
        "control_objective": "No unnecessary public admin ports",
        "evidence_question": "Are SSH/RDP/admin ports exposed to the public internet?",
        "minimum_evidence": "Security group/NSG/firewall rules, public IP inventory, route exposure, exception records",
        "aws_evidence": "EC2 public IPs, security group ingress on 22/3389, route tables, VPC flow logs if available",
        "azure_evidence": "VM public IPs, NSG inbound rules, Azure Bastion/JIT configuration",
        "gcp_evidence": "Compute external IPs, VPC firewall rules, IAP configuration",
        "oci_evidence": "Compute public IPs, security lists, NSGs, OCI Bastion configuration",
        "risk_if_missing": "Public administrative exposure may exist without visibility or approval.",
        "review_frequency": "Weekly for internet-facing environments; monthly otherwise",
    },
    {
        "control_objective": "Controlled administrative access path",
        "evidence_question": "What path does an administrator use to reach protected workloads?",
        "minimum_evidence": "Access path diagram, bastion/session/VPN configuration, routing evidence, private workload ingress rules",
        "aws_evidence": "SSM Session Manager configuration, bastion security groups, Client VPN, route tables",
        "azure_evidence": "Azure Bastion, VPN Gateway, JIT VM access, NSGs, route tables",
        "gcp_evidence": "IAP TCP forwarding, OS Login, Cloud VPN, firewall rules",
        "oci_evidence": "OCI Bastion, IPSec VPN, FastConnect, VCN route tables, NSGs/security lists",
        "risk_if_missing": "The organization cannot prove the actual administrative path or whether it is controlled.",
        "review_frequency": "At architecture change and quarterly",
    },
    {
        "control_objective": "Session logging and auditability",
        "evidence_question": "Can administrative sessions be reconstructed after the fact?",
        "minimum_evidence": "Provider audit logs, session logs, log retention settings, central log destination",
        "aws_evidence": "CloudTrail, SSM session logs to CloudWatch or S3, CloudWatch retention",
        "azure_evidence": "Activity Logs, Monitor logs, Bastion diagnostic logs, Log Analytics retention",
        "gcp_evidence": "Cloud Audit Logs, IAP logs, OS Login logs, Cloud Logging retention",
        "oci_evidence": "OCI Audit logs, Bastion session logs where available, Logging service retention",
        "risk_if_missing": "Administrative actions may not be attributable, reviewable, or incident-investigable.",
        "review_frequency": "Monthly and after incidents",
    },
    {
        "control_objective": "Time-bound privileged access",
        "evidence_question": "Is privileged access standing or temporary?",
        "minimum_evidence": "PAM/PIM activation records, temporary role assumption records, expiration timestamps, approval records",
        "aws_evidence": "STS AssumeRole events, IAM Identity Center assignments, Access Analyzer findings, CloudTrail",
        "azure_evidence": "Entra PIM activations, eligible/active role records, approval history",
        "gcp_evidence": "Privileged Access Manager grants, IAM Conditions, Cloud Audit Logs",
        "oci_evidence": "IAM policy records, identity domain assignments, third-party PAM evidence, Audit logs",
        "risk_if_missing": "Standing privilege may persist without review or business need.",
        "review_frequency": "Monthly for privileged roles; after every emergency access event",
    },
    {
        "control_objective": "Exception ownership and expiration",
        "evidence_question": "Are weaker access patterns formally owned, justified, and time-limited?",
        "minimum_evidence": "Exception register, business justification, owner, compensating controls, expiration/review date",
        "aws_evidence": "Tagged resources, exception record, security group rule age, CloudTrail change history",
        "azure_evidence": "Tagged resources, exception record, NSG rule history, Activity Logs",
        "gcp_evidence": "Labels, exception record, firewall rule history, Cloud Audit Logs",
        "oci_evidence": "Defined tags, exception record, security list/NSG history, Audit logs",
        "risk_if_missing": "Temporary exceptions become permanent architecture.",
        "review_frequency": "At least monthly until closed",
    },
    {
        "control_objective": "Break-glass governance",
        "evidence_question": "Can emergency administrative access be used without becoming unmanaged standing privilege?",
        "minimum_evidence": "Break-glass account inventory, use records, approval/incident linkage, post-use review, credential rotation",
        "aws_evidence": "CloudTrail login/API events, root/IAM credential reports, incident ticket, credential rotation record",
        "azure_evidence": "Emergency access accounts, sign-in logs, PIM records, incident ticket, credential rotation record",
        "gcp_evidence": "Super admin/emergency IAM records, Cloud Audit Logs, incident ticket, credential rotation record",
        "oci_evidence": "Emergency identity records, Audit logs, incident ticket, credential rotation record",
        "risk_if_missing": "Emergency access can bypass normal governance without detection or review.",
        "review_frequency": "After every use and quarterly if unused",
    },
]


EXCEPTION_ROWS = [
    {
        "exception_id": "CAE-EX-001",
        "status": "Example",
        "workload": "Temporary lab instance",
        "access_pattern": "Direct public SSH/RDP",
        "business_justification": "Short-lived troubleshooting or training lab with no production data",
        "risk_accepted": "Temporary public administrative exposure",
        "compensating_controls": "Source IP restriction; time-bound rule; named owner; cleanup evidence",
        "owner": "Lab owner",
        "opened_date": "YYYY-MM-DD",
        "expiration_date": "YYYY-MM-DD",
        "review_date": "YYYY-MM-DD",
        "required_evidence": "Security group rule, owner, purpose, expiration, destruction or rule-removal evidence",
        "closure_evidence": "Pending",
    },
    {
        "exception_id": "CAE-EX-002",
        "status": "Example",
        "workload": "Legacy migration workload",
        "access_pattern": "Bastion host / jump box",
        "business_justification": "Legacy administration pattern retained during migration",
        "risk_accepted": "Bastion becomes high-value access choke point",
        "compensating_controls": "Restricted ingress; patching; MFA/key control; session logging; target-state migration plan",
        "owner": "Migration owner",
        "opened_date": "YYYY-MM-DD",
        "expiration_date": "YYYY-MM-DD",
        "review_date": "YYYY-MM-DD",
        "required_evidence": "Bastion rules, private workload rules, patch evidence, session logs, migration plan",
        "closure_evidence": "Pending",
    },
]


def artifact_status(path):
    if path.exists() and path.stat().st_size > 0:
        return "Present"
    if path.exists() and path.stat().st_size == 0:
        return "Empty"
    return "Missing"


def write_evidence_requirements():
    EVIDENCE_REQUIREMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(EVIDENCE_REQUIREMENTS[0].keys())

    with EVIDENCE_REQUIREMENTS_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(EVIDENCE_REQUIREMENTS)


def write_exception_register():
    EXCEPTION_REGISTER_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(EXCEPTION_ROWS[0].keys())

    with EXCEPTION_REGISTER_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(EXCEPTION_ROWS)


def write_playbook():
    PLAYBOOK_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).date().isoformat()

    lines = [
        "# Cloud Administrative Access Evidence Playbook",
        "",
        f"Date: `{timestamp}`",
        "",
        "## Purpose",
        "",
        "This playbook turns the cloud administrative access ADR into evidence requirements and exception-management practices.",
        "",
        "The goal is to make the access decision auditable: who can administer workloads, how they connect, what risks remain, and what evidence proves the access path is controlled.",
        "",
        "## Core Evidence Questions",
        "",
        "For any cloud administrative access pattern, answer these questions:",
        "",
        "1. Who is authorized to administer the workload?",
        "2. What path do they use to reach it?",
        "3. Are public administrative ports exposed?",
        "4. Is access standing or temporary?",
        "5. Are sessions logged and attributable?",
        "6. Are exceptions owned, justified, and time-limited?",
        "7. Can emergency access be reviewed after use?",
        "",
        "## Evidence Requirement Summary",
        "",
        "| Control Objective | Evidence Question | Minimum Evidence | Risk If Missing | Review Frequency |",
        "|---|---|---|---|---|",
    ]

    for item in EVIDENCE_REQUIREMENTS:
        lines.append(
            f"| {item['control_objective']} | {item['evidence_question']} | "
            f"{item['minimum_evidence']} | {item['risk_if_missing']} | "
            f"{item['review_frequency']} |"
        )

    lines.extend(
        [
            "",
            "## Provider Evidence Translation",
            "",
            "| Control Objective | AWS | Azure | GCP | OCI |",
            "|---|---|---|---|---|",
        ]
    )

    for item in EVIDENCE_REQUIREMENTS:
        lines.append(
            f"| {item['control_objective']} | {item['aws_evidence']} | "
            f"{item['azure_evidence']} | {item['gcp_evidence']} | {item['oci_evidence']} |"
        )

    lines.extend(
        [
            "",
            "## Exception Register Rules",
            "",
            "Use the exception register when an environment uses a weaker or transitional access pattern, such as direct public SSH/RDP, broadly exposed bastion access, or legacy VPN administration without sufficient segmentation.",
            "",
            "Every exception must include:",
            "",
            "- exception ID,",
            "- workload,",
            "- owner,",
            "- business justification,",
            "- access pattern,",
            "- risk accepted,",
            "- compensating controls,",
            "- expiration date,",
            "- review date,",
            "- required evidence,",
            "- closure evidence.",
            "",
            "## Decision Rule",
            "",
            "> If an access pattern cannot produce reviewable evidence, it is not mature enough for production without a documented exception.",
            "",
            "## Executive Language",
            "",
            "> Our administrative access standard is evidence-driven. We do not just approve access paths; we require proof that access is authorized, minimized, logged, reviewable, and time-appropriate for the workload risk.",
            "",
            "## Related Artifacts",
            "",
            f"- `{EVIDENCE_REQUIREMENTS_FILE.as_posix()}`",
            f"- `{EXCEPTION_REGISTER_FILE.as_posix()}`",
        ]
    )

    for artifact in REFERENCE_ARTIFACTS:
        lines.append(f"- `{artifact.as_posix()}` — {artifact_status(artifact)}")

    lines.append("")

    PLAYBOOK_FILE.write_text("\n".join(lines), encoding="utf-8")


def write_report():
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    present_count = sum(1 for artifact in REFERENCE_ARTIFACTS if artifact_status(artifact) == "Present")

    lines = [
        "# Cloud Admin Access Evidence Kit Generation Report",
        "",
        f"Generated: `{timestamp}`",
        "",
        "Overall Status: **PASS**",
        "",
        "## Generated Artifacts",
        "",
        f"- `{EVIDENCE_REQUIREMENTS_FILE.as_posix()}`",
        f"- `{EXCEPTION_REGISTER_FILE.as_posix()}`",
        f"- `{PLAYBOOK_FILE.as_posix()}`",
        "",
        "## Summary",
        "",
        f"- Evidence requirements generated: `{len(EVIDENCE_REQUIREMENTS)}`",
        f"- Example exception rows generated: `{len(EXCEPTION_ROWS)}`",
        f"- Reference artifacts present: `{present_count}` of `{len(REFERENCE_ARTIFACTS)}`",
        "",
        "## Reference Artifact Status",
        "",
        "| Artifact | Status |",
        "|---|---|",
    ]

    for artifact in REFERENCE_ARTIFACTS:
        lines.append(f"| `{artifact.as_posix()}` | {artifact_status(artifact)} |")

    lines.extend(
        [
            "",
            "## Portfolio Relevance",
            "",
            "This artifact converts architecture decision-making into an audit-ready evidence and exception-management model.",
            "",
            "It demonstrates how cloud access decisions can be governed through evidence requirements, review frequency, exception ownership, and provider-specific proof points.",
            "",
        ]
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main():
    write_evidence_requirements()
    write_exception_register()
    write_playbook()
    write_report()

    print(f"Evidence requirements written to: {EVIDENCE_REQUIREMENTS_FILE}")
    print(f"Exception register written to: {EXCEPTION_REGISTER_FILE}")
    print(f"Evidence playbook written to: {PLAYBOOK_FILE}")
    print(f"Evidence report written to: {REPORT_FILE}")
    print("Overall Status: PASS")


if __name__ == "__main__":
    main()