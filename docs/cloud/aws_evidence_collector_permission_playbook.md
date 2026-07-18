# AWS Evidence Collector Permission Playbook

Date: `2026-07-18`

## Purpose

This playbook defines the read-only permissions needed by the AWS evidence collectors in this project.

It exists so evidence collection failures can be interpreted as authorization findings instead of generic script failures.

## Active Identity Context

| Field | Value |
|---|---|
| Identity status | `AUTHENTICATED` |
| Account | `account_dee1259834` |
| ARN | `arn_f200e52a7a` |
| User ID | `user_ef0bd59078` |
| Region | `us-east-1` |

## Permission Check Results

| Check | Collector Area | AWS Action | Status | Interpretation |
|---|---|---|---|---|
| AWS-STS-001 | Account context evidence | `sts:GetCallerIdentity` | **AUTHORIZED** | Command completed successfully. |
| AWS-S3-001 | S3 inventory evidence | `s3:ListAllMyBuckets` | **AUTHORIZED** | Command completed successfully. |
| AWS-EC2-001 | Admin port exposure evidence | `ec2:DescribeSecurityGroups` | **AUTHORIZED** | DryRunOperation returned, which indicates the principal has permission. |

## Minimal Policy Snippets

Use these only when the active lab principal needs the specific read-only evidence collection capability.

No missing permissions were detected by this preflight.

## Governance Note

The goal is not to give the lab principal broad administrative authority.

The goal is to grant narrow read-only permissions that allow the project to collect evidence safely.

## Decision Rule

> If a collector requires a permission, document the action, purpose, resource scope, and evidence value before granting it.
