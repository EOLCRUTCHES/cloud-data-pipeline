# ADR-001: Cloud Administrative Access Pattern Standard

Date: `2026-07-14`

Status: **Proposed**

## Context

Cloud administrative access can be implemented through several patterns, including direct public SSH/RDP, bastion hosts, VPN or private connectivity, identity-aware session management, and privileged access workflows.

These patterns are not interchangeable. Each changes the risk profile, operational burden, logging quality, and evidence available for review.

The control objective is not to require a specific named service such as a bastion host. The control objective is to ensure administrative access is authorized, minimized, segmented, monitored, attributable, time-appropriate, and reviewable.

## Decision

For modern cloud workloads, the preferred default administrative access pattern is **identity-aware session management** where supported.

For high-risk, regulated, production, or privileged environments, identity-aware session management should be paired with a **privileged access workflow** that supports approval, time-bound access, attribution, logging, and review.

Bastion hosts and VPN/private connectivity may be acceptable as transitional or compensating patterns when business, legacy, or technical constraints prevent immediate adoption of identity-aware session management.

Direct public SSH/RDP should be avoided for production workloads and allowed only as a tightly controlled, time-bound exception for low-risk lab or troubleshooting scenarios.

## Decision Rules

### Prefer Identity-Aware Session Management When

- the provider supports brokered administrative sessions,
- workloads do not require inbound public management ports,
- session activity can be centrally logged,
- identity policy can control who can start sessions,
- the environment needs stronger evidence than network access alone provides.

### Require Privileged Access Workflow When

- the system is production, regulated, sensitive, or mission-critical,
- access must be approved before use,
- privilege should be temporary rather than standing,
- access must be attributable to an individual,
- evidence must support audit, review, or authorization.

### Allow Bastion or VPN as Transitional Patterns When

- legacy administration methods must be supported temporarily,
- private workloads are protected from direct public access,
- the access path is segmented and monitored,
- the pattern has an owner and review date,
- there is a roadmap toward stronger identity-aware or privileged access controls.

### Allow Direct Public SSH/RDP Only When

- the workload is low risk, temporary, and non-production,
- source access is tightly restricted,
- the exception is time-bound,
- the owner and purpose are documented,
- cleanup evidence is retained.

## Rationale

Identity-aware session management generally reduces exposure by avoiding inbound administrative ports and shifting access control toward identity, policy, managed sessions, and centralized logging.

Privileged access workflows reduce standing privilege and create a stronger evidence trail for high-risk administrative actions.

Bastion hosts reduce direct exposure of private workloads, but they also become high-value targets that require patching, hardening, logging, and tight authorization.

VPN or private connectivity removes administrative access from the public internet, but it does not automatically prove least privilege. Segmentation, identity controls, and logging remain necessary.

Direct public administrative access is fast to configure but weak to defend because it exposes management paths directly to network attack and credential abuse.

## Minimum Evidence Expectations

Any approved administrative access pattern should produce evidence for:

- authorized administrative identities,
- access path and network exposure,
- inbound management-port status,
- session logging or provider audit logs,
- MFA or equivalent identity control,
- privilege assignment and scope,
- approval trail for high-risk access,
- exception owner and expiration date,
- break-glass use and post-use review,
- periodic access review.

## Consequences

### Positive Consequences

- reduces unnecessary public administrative exposure,
- improves evidence quality for audit and authorization,
- creates a consistent decision model across providers,
- supports least privilege and session accountability,
- makes cloud administration easier to explain to executives and auditors.

### Negative Consequences

- may require additional setup and operational discipline,
- may require agent health, identity policy, and logging dependencies,
- may require exception handling for legacy workloads,
- may increase friction for administrators accustomed to direct access.

## Exception Handling

Exceptions must document:

- business justification,
- workload owner,
- access method,
- risk accepted,
- compensating controls,
- expiration or review date,
- required evidence.

## Review Triggers

This decision should be reviewed when:

- a workload moves from lab to production,
- direct public admin access is requested,
- a new cloud provider is introduced,
- a regulated workload is onboarded,
- a bastion host is exposed broadly,
- privileged access processes change,
- logging or audit requirements change.

## Executive Statement

> We are not selecting an access pattern because it is fashionable or provider-native. We are selecting it because it changes the risk profile in a defensible way and gives us evidence we can review later.

## Related Artifacts

- `security/cloud_admin_access_patterns.csv` — Present
- `security/cloud_admin_access_decision_rubric.csv` — Present
- `docs/cloud/cloud_admin_access_field_cards.md` — Present
- `docs/cloud/cloud_admin_access_decision_guide.md` — Present
- `study/cloud_admin_access_quizlet.tsv` — Present
- `study/cloud_admin_access_flashcards.csv` — Present
