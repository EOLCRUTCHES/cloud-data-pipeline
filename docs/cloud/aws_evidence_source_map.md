# AWS Evidence Source Map

## Purpose

This document defines the AWS evidence sources that will eventually feed the secure automation governance workflow.

The goal is to connect cloud implementation work to evidence, controls, risks, and trust architecture.

## Portfolio Thesis

Secure automation requires evidence.

Automated security requires repeatable evidence collection.

This project will use AWS as the first cloud implementation environment, then compare equivalent control patterns across Azure, GCP, and OCI.

## Current Local Governance Workflow

The current local workflow produces:

1. Validation evidence
2. Evidence index
3. Control matrix
4. Risk register
5. Artifact manifest
6. Artifact hash report
7. Artifact hash verification report

## AWS Evidence Sources

| AWS Area | Evidence Source | Security Question | Future Artifact |
|---|---|---|---|
| S3 / object storage | Bucket configuration | Is storage configured securely? | S3 bucket evidence report |
| IAM | User, role, and policy configuration | Is access limited and explainable? | IAM evidence report |
| Encryption | S3 encryption and KMS configuration | Is data protected at rest? | Encryption evidence report |
| Logging | CloudTrail / CloudWatch configuration | Are actions logged and reviewable? | Logging evidence report |
| Network exposure | Public access settings | Is data unintentionally exposed? | Exposure evidence report |
| Cost control | Resource inventory | Are resources known and bounded? | Cloud resource inventory |
| Evidence integrity | Local hash report | Can evidence artifacts be fingerprinted? | Provenance records |

## First AWS Use Case

The first AWS use case should be:

> Store or describe a demo-safe evidence artifact in AWS S3, then collect configuration evidence about the storage location.

This keeps the cloud work simple while supporting the larger governance story.

## Control Pattern

The AWS control pattern will follow this chain:

```text
AWS resource
  ↓
Configuration evidence
  ↓
Evidence report
  ↓
Evidence index
  ↓
Control matrix
  ↓
Risk register
  ↓
Artifact hash report