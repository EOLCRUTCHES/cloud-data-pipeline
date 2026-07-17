Scenario Bank
1. Temporary lab VM

A developer needs SSH access to a disposable EC2 instance for a two-hour troubleshooting session. The instance contains no production data and will be destroyed today.

Decide whether direct public SSH is acceptable, and under what conditions.

2. Production database subnet

A production database server sits in a private subnet. An administrator wants to RDP directly to it from home because “it’s faster.”

Choose the access pattern and explain why direct access is a bad default.

3. Legacy lift-and-shift

A company migrated several Windows servers from an on-prem VMware environment into AWS. The admins are used to VPN + RDP. They ask for a cloud version of the same model.

Recommend a transitional pattern and a future-state pattern.

4. High-risk regulated workload

A system contains sensitive federal data. Admin access must be attributable, approved, time-limited, logged, and reviewable.

Choose the pattern stack.

5. Bastion already exists

An environment already uses a Linux bastion host in a public subnet. Private instances only allow SSH from the bastion. The bastion has broad inbound access from 0.0.0.0/0.

Keep, replace, or harden? What evidence do you need?

6. “We have a VPN, so we’re secure”

A team argues that because admins connect through VPN, no further admin-access controls are necessary.

Challenge the assumption.

7. Multi-cloud admin access

The company uses AWS, Azure, and GCP. Each team uses a different admin access method. Leadership wants a consistent control story.

What should be standardized: the tool, or the control objective?

8. No inbound admin ports

A cloud workload has no inbound SSH or RDP. Admin sessions are brokered through a cloud-native identity/session service with logs sent to central storage.

What pattern is this? What evidence proves maturity?

9. Emergency break-glass account

A production outage requires emergency admin access. The organization has a break-glass account but rarely reviews its use.

What pattern does this belong to, and what evidence is missing?

10. Auditor asks “Do you use bastion hosts?”

An auditor asks whether the environment uses bastion hosts. The team mostly uses AWS Systems Manager Session Manager instead.

How should you answer without sounding evasive?

11. Security group allows SSH from office IP

An EC2 instance allows SSH only from the corporate office IP range. The team says this is “locked down enough.”

How do you evaluate that claim?

12. Executive wants the simplest answer

A VP asks: “Why can’t we just let admins connect directly if they have MFA?”

Give the executive-level answer.

Answer Key / Model Responses
1. Temporary lab VM

Pattern: Direct public SSH/RDP may be acceptable only as a temporary lab exception.

Risk reduced: Low operational friction.

Risk introduced: Public management-port exposure.

Evidence:

source IP restriction,
time-bound rule,
owner,
purpose,
destruction/cleanup evidence,
no production data.

Executive sentence:

Direct public access can be acceptable for short-lived lab use, but only when it is time-bound, source-restricted, and cleaned up.

2. Production database subnet

Pattern: Identity-aware session management or privileged access workflow; possibly VPN/private connectivity with segmentation.

Risk reduced: Avoids exposing production admin access directly.

Risk introduced: More operational setup and dependency on identity/session controls.

Evidence:

database has no public IP,
no direct inbound RDP/SSH,
admin sessions logged,
authorized admin identity,
MFA/PAM approval if required,
route/security group evidence.

Executive sentence:

Production administration should not depend on direct remote access to the workload; it should flow through a controlled, logged, least-privilege access path.

3. Legacy lift-and-shift

Pattern: Transitional: VPN/private connectivity or hardened bastion. Future state: identity-aware session management plus privileged access workflow for high-risk systems.

Risk reduced: Maintains operational continuity while reducing public exposure.

Risk introduced: Legacy assumptions may preserve overly broad network access.

Evidence:

current access path diagram,
VPN routing,
security group/NSG rules,
admin identity records,
migration roadmap,
retirement date for weaker access methods.

Executive sentence:

Lift-and-shift can start with familiar private access patterns, but the target state should reduce standing privilege and improve session-level evidence.

4. High-risk regulated workload

Pattern: Privileged access workflow plus identity-aware session management.

Risk reduced: Limits standing privilege and creates auditable, approved, attributable sessions.

Risk introduced: More process and operational complexity.

Evidence:

approval records,
temporary role assignment,
session logs,
MFA,
break-glass records,
periodic access review,
CloudTrail/provider audit logs.

Executive sentence:

For high-risk systems, access is not just about connectivity; it must be approved, temporary, attributable, logged, and reviewable.

5. Bastion already exists

Pattern: Harden or replace depending on business constraints.

Current issue: Bastion from 0.0.0.0/0 is too exposed.

Risk reduced: Private workloads are not directly exposed.

Risk introduced: Bastion is now a high-value internet-facing target.

Evidence needed:

inbound source restrictions,
MFA or strong auth,
patch status,
session logs,
private instance ingress limited to bastion,
admin account review,
CloudTrail/CloudWatch logs,
vulnerability findings.

Executive sentence:

A bastion reduces exposure for private servers, but if the bastion itself is broadly exposed, we have simply concentrated the risk.

6. “We have a VPN, so we’re secure”

Pattern: VPN/private connectivity is useful, but incomplete.

Risk reduced: Removes direct public admin exposure.

Risk introduced: VPN can create broad internal reach if segmentation and identity controls are weak.

Evidence:

VPN user groups,
MFA,
routes,
segmentation rules,
admin destination restrictions,
logs,
access reviews.

Executive sentence:

VPN provides a private path, not automatic least privilege; we still need segmentation, identity control, and evidence of who accessed what.

7. Multi-cloud admin access

Answer: Standardize the control objective, not necessarily the exact tool.

Control objective:

Administrative access must be authorized, minimized, segmented, monitored, attributable, and reviewable.

Provider translations:

AWS: SSM Session Manager, IAM, CloudTrail
Azure: Azure Bastion, Entra ID, PIM, Monitor
GCP: IAP, OS Login, IAM, Cloud Audit Logs
OCI: OCI Bastion, IAM policies, Audit logs

Executive sentence:

The tools vary by provider, but the control objective is the same: controlled, logged, least-privilege administrative access.

8. No inbound admin ports

Pattern: Identity-aware session management.

Risk reduced: Eliminates inbound management-port exposure.

Risk introduced: Depends on identity policy, agent health, logging configuration, and service availability.

Evidence:

no inbound SSH/RDP,
managed instance/session agent status,
IAM permissions,
session logs,
CloudTrail/provider audit logs,
centralized log retention.

Executive sentence:

Identity-aware session management is often stronger than a classic bastion because it removes inbound admin exposure and improves session evidence.

9. Emergency break-glass account

Pattern: Privileged access workflow / break-glass governance.

Risk reduced: Ensures emergency access exists.

Risk introduced: Emergency access may become unmanaged standing privilege.

Missing evidence:

approval or invocation reason,
time of use,
user attribution,
session log,
post-use review,
credential rotation,
access review,
incident/ticket linkage.

Executive sentence:

Break-glass access is necessary, but every use must create evidence and trigger review.

10. Auditor asks “Do you use bastion hosts?”

Answer:

In some cases, yes, but our preferred control pattern is identity-aware session management where supported. The control objective is not the bastion itself; it is controlled, monitored, least-privilege administrative access.

Evidence:

architecture diagram,
session manager configuration,
logs,
IAM roles,
no inbound admin ports,
exception list for any bastions.

Executive sentence:

We meet the administrative-access objective through provider-native session controls rather than relying solely on traditional bastion hosts.

11. Security group allows SSH from office IP

Pattern: Direct public SSH with source restriction.

Assessment: Better than open internet, but still weaker than private or identity-aware access.

Risk reduced: Limits exposure to known source range.

Risk introduced: Office IP may be compromised, shared, spoofed through VPN path, or too broad; SSH is still exposed.

Evidence:

source CIDR,
owner,
business justification,
MFA/SSH key control,
session logs,
expiration/review date,
evidence no production data or compensating control.

Executive sentence:

Source restriction improves direct SSH, but it does not make direct public administration the preferred production pattern.

12. Executive wants simplest answer

Answer:

MFA verifies the person, but it does not eliminate the risk of exposing administrative paths directly to the internet. We still need a controlled access path that limits exposure, logs the session, and proves the access was appropriate.

Pattern preference: Identity-aware session management or privileged access workflow.

Evidence:

no public admin ports,
MFA,
session logs,
role/permission evidence,
approval trail for high-risk systems.

Executive sentence:

MFA is one layer; the access path still has to be minimized, monitored, and reviewable.