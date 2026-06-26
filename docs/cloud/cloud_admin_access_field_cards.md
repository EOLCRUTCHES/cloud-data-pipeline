# Cloud Administrative Access Pattern Field Cards

Generated: `2026-06-26T15:32:33.548567+00:00`

## Purpose

These field cards convert cloud administrative access patterns into portable study notes.

The goal is pattern fluency: understand what each pattern replaces, why it exists, what risk it reduces, what risk it introduces, and what evidence proves it is working.

## Study Rule

For each pattern, be able to explain it using this sentence:

> This pattern is the cloud version of _____. It reduces _____. It introduces _____. I would prove it with _____.

---

## Card 1: Direct public SSH/RDP

### On-Prem Analogy

Remote admin directly exposed through a firewall rule

### Cloud Implementation

Instances with public IPs and security group ingress for SSH/RDP

### Risk Reduced

Low setup friction

### Risk Introduced

Broad attack surface and high exposure to credential attacks

### Evidence to Collect

Public IP presence, security group ingress on 22/3389, route to internet gateway, CloudTrail access events

### Multi-Cloud Translation

| Provider | Equivalent Pattern / Service Area |
|---|---|
| AWS | EC2 public IPs, security groups, NACLs, route tables, CloudTrail |
| Azure | VM public IP, NSG inbound rules, Azure Bastion alternative, Activity Logs |
| GCP | Compute Engine external IPs, firewall rules, IAP alternative, Cloud Audit Logs |
| OCI | Compute public IPs, security lists/NSGs, Bastion service alternative, Audit logs |

### Executive Sentence

Direct public administrative access is usually a weak pattern because it exposes management ports instead of forcing access through a controlled administrative path.

### Memory Drill

> Direct public SSH/RDP: What does it replace, what risk does it reduce, what risk does it introduce, and what evidence proves it?

---

## Card 2: Bastion host / jump box

### On-Prem Analogy

Hardened jump server between remote admins and internal servers

### Cloud Implementation

A hardened instance in a public subnet used to reach private instances

### Risk Reduced

Reduces direct public exposure of private workloads

### Risk Introduced

Creates a high-value choke point that must be patched, monitored, and tightly controlled

### Evidence to Collect

Bastion security group ingress, private instance ingress from bastion only, OS patch evidence, session logs, CloudTrail events

### Multi-Cloud Translation

| Provider | Equivalent Pattern / Service Area |
|---|---|
| AWS | EC2 bastion, public/private subnets, security groups, CloudTrail, CloudWatch logs |
| Azure | Azure Bastion or jump VM, VNets, NSGs, Monitor logs |
| GCP | Bastion VM, VPC firewall rules, Cloud Logging, IAP alternative |
| OCI | OCI Bastion service or jump host, VCN, NSGs/security lists, Audit logs |

### Executive Sentence

A bastion host is not the control objective; it is one way to provide controlled, monitored access into private systems.

### Memory Drill

> Bastion host / jump box: What does it replace, what risk does it reduce, what risk does it introduce, and what evidence proves it?

---

## Card 3: VPN or private connectivity

### On-Prem Analogy

Corporate VPN into internal network before server administration

### Cloud Implementation

Private network path into VPC/VNet/VCN before administrative access

### Risk Reduced

Removes administrative access from the public internet

### Risk Introduced

Network access may become too broad if segmentation and identity controls are weak

### Evidence to Collect

VPN configuration, route tables, allowed source ranges, security group rules, authentication logs

### Multi-Cloud Translation

| Provider | Equivalent Pattern / Service Area |
|---|---|
| AWS | Site-to-Site VPN, Client VPN, Direct Connect, route tables, security groups |
| Azure | VPN Gateway, ExpressRoute, VNets, NSGs |
| GCP | Cloud VPN, Cloud Interconnect, VPC firewall rules |
| OCI | IPSec VPN, FastConnect, VCN route tables, NSGs/security lists |

### Executive Sentence

Private connectivity reduces public exposure, but it still requires segmentation, identity controls, and evidence that access is limited.

### Memory Drill

> VPN or private connectivity: What does it replace, what risk does it reduce, what risk does it introduce, and what evidence proves it?

---

## Card 4: Identity-aware session management

### On-Prem Analogy

Privileged access broker that opens audited admin sessions without broad network exposure

### Cloud Implementation

Admin sessions authorized through cloud identity and agent/service control plane

### Risk Reduced

Avoids inbound SSH/RDP exposure and centralizes session authorization/logging

### Risk Introduced

Depends heavily on identity policy, agent health, logging configuration, and service availability

### Evidence to Collect

Managed instance status, IAM permissions, session logs, CloudTrail events, disabled inbound admin ports

### Multi-Cloud Translation

| Provider | Equivalent Pattern / Service Area |
|---|---|
| AWS | AWS Systems Manager Session Manager, IAM, SSM Agent, CloudTrail, CloudWatch/S3 session logs |
| Azure | Azure Bastion, Entra ID, Just-in-time VM access, Defender for Cloud, Monitor logs |
| GCP | Identity-Aware Proxy TCP forwarding, OS Login, IAM, Cloud Audit Logs |
| OCI | OCI Bastion service, IAM policies, Audit logs |

### Executive Sentence

Identity-aware session management often improves on classic bastions by reducing inbound exposure and centralizing authorization and logging.

### Memory Drill

> Identity-aware session management: What does it replace, what risk does it reduce, what risk does it introduce, and what evidence proves it?

---

## Card 5: Privileged access workflow

### On-Prem Analogy

PAM-approved admin access with time-bound elevation and approval trail

### Cloud Implementation

Just-in-time privileged access with approval, temporary credentials, and auditable session records

### Risk Reduced

Limits standing administrative privilege

### Risk Introduced

Workflow complexity can create bypasses if emergency access is unmanaged

### Evidence to Collect

Approval record, temporary access duration, role assumption logs, session recording, break-glass review

### Multi-Cloud Translation

| Provider | Equivalent Pattern / Service Area |
|---|---|
| AWS | IAM Identity Center, STS role assumption, IAM Access Analyzer, CloudTrail |
| Azure | Entra Privileged Identity Management, RBAC, Activity Logs |
| GCP | Privileged Access Manager, IAM Conditions, Cloud Audit Logs |
| OCI | IAM policies, identity domains, Audit logs, third-party PAM integration |

### Executive Sentence

Privileged access workflows are mature when they limit standing privilege, require approval, and preserve an auditable access trail.

### Memory Drill

> Privileged access workflow: What does it replace, what risk does it reduce, what risk does it introduce, and what evidence proves it?

---

## Final Carry-Forward

Do not memorize cloud services as isolated vocabulary.

Memorize the access pattern, the risk tradeoff, and the evidence trail.
