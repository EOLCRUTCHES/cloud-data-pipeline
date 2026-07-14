# Cloud Administrative Access Pattern Decision Guide

Generated: `2026-07-14T19:25:54.729123+00:00`

## Purpose

This guide turns cloud administrative access patterns into architecture decision logic.

The goal is to choose and defend an access pattern based on risk, evidence, operational burden, and governance maturity.

## Core Control Objective

The objective is not to deploy a specific named service.

The objective is to ensure administrative access is authorized, minimized, segmented, monitored, time-appropriate, and reviewable.

## Decision Rule

Choose the weakest pattern only when the risk is low, the exposure is temporary, and the evidence is clear.

Choose stronger patterns when the workload is production, regulated, privileged, externally exposed, or operationally critical.

## Fast Decision Tree

1. Does the workload need public inbound SSH/RDP?
   - If yes, challenge the assumption.
   - If no, prefer private or identity-aware access.

2. Can administrative access be brokered through identity instead of network exposure?
   - If yes, prefer identity-aware session management.
   - If no, use private connectivity or a hardened bastion as a transitional pattern.

3. Is the system production, regulated, privileged, or high impact?
   - If yes, add privileged access workflow controls.
   - If no, still require logging, owner, and cleanup evidence.

4. Can the access decision be reviewed later?
   - If no, the pattern is not mature enough.
   - If yes, retain the evidence trail.

## Pattern Rubric

Scoring note: lower is better for risk and burden; higher is better for logging and governance strength.

| Pattern | Exposure Risk | Standing Privilege Risk | Logging Strength | Operational Burden | Governance Strength | Default Decision |
|---|---:|---:|---:|---:|---:|---|
| Direct public SSH/RDP | 5 | 4 | 2 | 1 | 1 | Avoid for production; allow only for temporary lab use with time-bound, source-restricted access. |
| Bastion host / jump box | 3 | 3 | 3 | 3 | 3 | Accept as a transitional pattern when hardened, patched, monitored, and limited to private workload access. |
| VPN or private connectivity | 2 | 3 | 3 | 4 | 3 | Use when private network access is required, but pair it with segmentation, MFA, and narrow admin paths. |
| Identity-aware session management | 1 | 2 | 5 | 2 | 5 | Prefer for modern cloud administration when the service supports logging, identity policy, and private workload access. |
| Privileged access workflow | 1 | 1 | 5 | 4 | 5 | Use for high-risk, regulated, privileged, or production environments where approval and time-bound access matter. |

## Scenario Recommendations

| Scenario | Recommended Pattern | Why | Minimum Evidence |
|---|---|---|---|
| Temporary lab or disposable sandbox | Direct public SSH/RDP may be acceptable only as a time-bound exception; identity-aware session management is still better if available. | The business risk is low, but internet-exposed management ports should still be source-restricted and temporary. | Security group/source restriction, expiration date, owner, purpose, and cleanup confirmation. |
| Private production workload | Identity-aware session management, VPN/private connectivity with segmentation, or hardened bastion as a transitional pattern. | Production administration should not depend on broad public management exposure. | No public inbound admin ports on private workloads, authorized admin identities, session logs, and route/security group evidence. |
| Regulated or high-risk system | Privileged access workflow plus identity-aware session management where possible. | The control objective is not only access; it is approved, time-bound, attributable, monitored, and reviewable access. | Approval trail, temporary privilege assignment, session recording/logging, break-glass review, and periodic access review. |
| Legacy lift-and-shift migration | VPN/private connectivity or bastion may be acceptable as a transition, with a roadmap toward identity-aware sessions and PAM. | Legacy administration often arrives with network assumptions that should be reduced over time. | Current access path, compensating controls, target-state pattern, migration owner, and retirement date for weaker access methods. |
| Multi-cloud enterprise | Normalize the control objective across providers and collect provider-native evidence for the same access pattern. | The services differ, but the governance question is the same: who accessed what, how, under what authority, and where is the evidence? | Provider-native logs, identity records, access path diagrams, session records, and cross-cloud control mapping. |

## Pattern Defense Notes

### Direct public SSH/RDP

**Executive read:** Fast to set up, weak to defend.

**On-prem analogy:** Remote admin directly exposed through a firewall rule

**Cloud implementation:** Instances with public IPs and security group ingress for SSH/RDP

**Risk reduced:** Low setup friction

**Risk introduced:** Broad attack surface and high exposure to credential attacks

**Evidence to collect:** Public IP presence, security group ingress on 22/3389, route to internet gateway, CloudTrail access events

**Multi-cloud translation:** AWS: EC2 public IPs, security groups, NACLs, route tables, CloudTrail | Azure: VM public IP, NSG inbound rules, Azure Bastion alternative, Activity Logs | GCP: Compute Engine external IPs, firewall rules, IAP alternative, Cloud Audit Logs | OCI: Compute public IPs, security lists/NSGs, Bastion service alternative, Audit logs

### Bastion host / jump box

**Executive read:** Useful choke point, but now the choke point is high-value infrastructure.

**On-prem analogy:** Hardened jump server between remote admins and internal servers

**Cloud implementation:** A hardened instance in a public subnet used to reach private instances

**Risk reduced:** Reduces direct public exposure of private workloads

**Risk introduced:** Creates a high-value choke point that must be patched, monitored, and tightly controlled

**Evidence to collect:** Bastion security group ingress, private instance ingress from bastion only, OS patch evidence, session logs, CloudTrail events

**Multi-cloud translation:** AWS: EC2 bastion, public/private subnets, security groups, CloudTrail, CloudWatch logs | Azure: Azure Bastion or jump VM, VNets, NSGs, Monitor logs | GCP: Bastion VM, VPC firewall rules, Cloud Logging, IAP alternative | OCI: OCI Bastion service or jump host, VCN, NSGs/security lists, Audit logs

### VPN or private connectivity

**Executive read:** Private path is better than public exposure, but private network access is not the same as least privilege.

**On-prem analogy:** Corporate VPN into internal network before server administration

**Cloud implementation:** Private network path into VPC/VNet/VCN before administrative access

**Risk reduced:** Removes administrative access from the public internet

**Risk introduced:** Network access may become too broad if segmentation and identity controls are weak

**Evidence to collect:** VPN configuration, route tables, allowed source ranges, security group rules, authentication logs

**Multi-cloud translation:** AWS: Site-to-Site VPN, Client VPN, Direct Connect, route tables, security groups | Azure: VPN Gateway, ExpressRoute, VNets, NSGs | GCP: Cloud VPN, Cloud Interconnect, VPC firewall rules | OCI: IPSec VPN, FastConnect, VCN route tables, NSGs/security lists

### Identity-aware session management

**Executive read:** Usually the best default because it reduces inbound exposure and improves evidence quality.

**On-prem analogy:** Privileged access broker that opens audited admin sessions without broad network exposure

**Cloud implementation:** Admin sessions authorized through cloud identity and agent/service control plane

**Risk reduced:** Avoids inbound SSH/RDP exposure and centralizes session authorization/logging

**Risk introduced:** Depends heavily on identity policy, agent health, logging configuration, and service availability

**Evidence to collect:** Managed instance status, IAM permissions, session logs, CloudTrail events, disabled inbound admin ports

**Multi-cloud translation:** AWS: AWS Systems Manager Session Manager, IAM, SSM Agent, CloudTrail, CloudWatch/S3 session logs | Azure: Azure Bastion, Entra ID, Just-in-time VM access, Defender for Cloud, Monitor logs | GCP: Identity-Aware Proxy TCP forwarding, OS Login, IAM, Cloud Audit Logs | OCI: OCI Bastion service, IAM policies, Audit logs

### Privileged access workflow

**Executive read:** Highest governance value when privilege must be temporary, approved, and reviewable.

**On-prem analogy:** PAM-approved admin access with time-bound elevation and approval trail

**Cloud implementation:** Just-in-time privileged access with approval, temporary credentials, and auditable session records

**Risk reduced:** Limits standing administrative privilege

**Risk introduced:** Workflow complexity can create bypasses if emergency access is unmanaged

**Evidence to collect:** Approval record, temporary access duration, role assumption logs, session recording, break-glass review

**Multi-cloud translation:** AWS: IAM Identity Center, STS role assumption, IAM Access Analyzer, CloudTrail | Azure: Entra Privileged Identity Management, RBAC, Activity Logs | GCP: Privileged Access Manager, IAM Conditions, Cloud Audit Logs | OCI: IAM policies, identity domains, Audit logs, third-party PAM integration

## Executive Summary Language

Use this language when explaining the decision:

> We are not selecting an access pattern because it is fashionable or provider-native. We are selecting it because it changes the risk profile in a defensible way and gives us evidence we can review later.

## Final Carry-Forward

A strong cloud access decision names the pattern, the risk tradeoff, the evidence trail, and the provider-native implementation.
