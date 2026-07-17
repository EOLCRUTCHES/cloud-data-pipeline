# Cloud Administrative Access Evidence Playbook

Date: `2026-07-16`

## Purpose

This playbook turns the cloud administrative access ADR into evidence requirements and exception-management practices.

The goal is to make the access decision auditable: who can administer workloads, how they connect, what risks remain, and what evidence proves the access path is controlled.

## Core Evidence Questions

For any cloud administrative access pattern, answer these questions:

1. Who is authorized to administer the workload?
2. What path do they use to reach it?
3. Are public administrative ports exposed?
4. Is access standing or temporary?
5. Are sessions logged and attributable?
6. Are exceptions owned, justified, and time-limited?
7. Can emergency access be reviewed after use?

## Evidence Requirement Summary

| Control Objective | Evidence Question | Minimum Evidence | Risk If Missing | Review Frequency |
|---|---|---|---|---|
| Authorized administrative identities | Who is allowed to administer cloud workloads? | IAM users/roles/groups, identity provider groups, privileged role assignments, access review records | Administrative access cannot be tied to approved identities. | Monthly for production; quarterly for lower-risk environments |
| No unnecessary public admin ports | Are SSH/RDP/admin ports exposed to the public internet? | Security group/NSG/firewall rules, public IP inventory, route exposure, exception records | Public administrative exposure may exist without visibility or approval. | Weekly for internet-facing environments; monthly otherwise |
| Controlled administrative access path | What path does an administrator use to reach protected workloads? | Access path diagram, bastion/session/VPN configuration, routing evidence, private workload ingress rules | The organization cannot prove the actual administrative path or whether it is controlled. | At architecture change and quarterly |
| Session logging and auditability | Can administrative sessions be reconstructed after the fact? | Provider audit logs, session logs, log retention settings, central log destination | Administrative actions may not be attributable, reviewable, or incident-investigable. | Monthly and after incidents |
| Time-bound privileged access | Is privileged access standing or temporary? | PAM/PIM activation records, temporary role assumption records, expiration timestamps, approval records | Standing privilege may persist without review or business need. | Monthly for privileged roles; after every emergency access event |
| Exception ownership and expiration | Are weaker access patterns formally owned, justified, and time-limited? | Exception register, business justification, owner, compensating controls, expiration/review date | Temporary exceptions become permanent architecture. | At least monthly until closed |
| Break-glass governance | Can emergency administrative access be used without becoming unmanaged standing privilege? | Break-glass account inventory, use records, approval/incident linkage, post-use review, credential rotation | Emergency access can bypass normal governance without detection or review. | After every use and quarterly if unused |

## Provider Evidence Translation

| Control Objective | AWS | Azure | GCP | OCI |
|---|---|---|---|---|
| Authorized administrative identities | IAM roles, IAM Identity Center assignments, CloudTrail AssumeRole or StartSession events | Entra ID groups, Azure RBAC assignments, PIM activations, Activity Logs | IAM allow policies, group membership, OS Login configuration, Cloud Audit Logs | IAM policies, identity domains, dynamic groups, Audit logs |
| No unnecessary public admin ports | EC2 public IPs, security group ingress on 22/3389, route tables, VPC flow logs if available | VM public IPs, NSG inbound rules, Azure Bastion/JIT configuration | Compute external IPs, VPC firewall rules, IAP configuration | Compute public IPs, security lists, NSGs, OCI Bastion configuration |
| Controlled administrative access path | SSM Session Manager configuration, bastion security groups, Client VPN, route tables | Azure Bastion, VPN Gateway, JIT VM access, NSGs, route tables | IAP TCP forwarding, OS Login, Cloud VPN, firewall rules | OCI Bastion, IPSec VPN, FastConnect, VCN route tables, NSGs/security lists |
| Session logging and auditability | CloudTrail, SSM session logs to CloudWatch or S3, CloudWatch retention | Activity Logs, Monitor logs, Bastion diagnostic logs, Log Analytics retention | Cloud Audit Logs, IAP logs, OS Login logs, Cloud Logging retention | OCI Audit logs, Bastion session logs where available, Logging service retention |
| Time-bound privileged access | STS AssumeRole events, IAM Identity Center assignments, Access Analyzer findings, CloudTrail | Entra PIM activations, eligible/active role records, approval history | Privileged Access Manager grants, IAM Conditions, Cloud Audit Logs | IAM policy records, identity domain assignments, third-party PAM evidence, Audit logs |
| Exception ownership and expiration | Tagged resources, exception record, security group rule age, CloudTrail change history | Tagged resources, exception record, NSG rule history, Activity Logs | Labels, exception record, firewall rule history, Cloud Audit Logs | Defined tags, exception record, security list/NSG history, Audit logs |
| Break-glass governance | CloudTrail login/API events, root/IAM credential reports, incident ticket, credential rotation record | Emergency access accounts, sign-in logs, PIM records, incident ticket, credential rotation record | Super admin/emergency IAM records, Cloud Audit Logs, incident ticket, credential rotation record | Emergency identity records, Audit logs, incident ticket, credential rotation record |

## Exception Register Rules

Use the exception register when an environment uses a weaker or transitional access pattern, such as direct public SSH/RDP, broadly exposed bastion access, or legacy VPN administration without sufficient segmentation.

Every exception must include:

- exception ID,
- workload,
- owner,
- business justification,
- access pattern,
- risk accepted,
- compensating controls,
- expiration date,
- review date,
- required evidence,
- closure evidence.

## Decision Rule

> If an access pattern cannot produce reviewable evidence, it is not mature enough for production without a documented exception.

## Executive Language

> Our administrative access standard is evidence-driven. We do not just approve access paths; we require proof that access is authorized, minimized, logged, reviewable, and time-appropriate for the workload risk.

## Related Artifacts

- `security/cloud_admin_access_evidence_requirements.csv`
- `security/cloud_admin_access_exception_register.csv`
- `docs/cloud/adr-001-cloud-admin-access-pattern.md` — Present
- `docs/cloud/cloud_admin_access_decision_guide.md` — Present
- `security/cloud_admin_access_decision_rubric.csv` — Present
- `docs/cloud/cloud_admin_access_field_cards.md` — Present
