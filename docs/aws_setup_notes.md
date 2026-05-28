# AWS Setup Notes

## Purpose

Day 23 starts the cloud transition phase for the cloud data pipeline project.

The goal is to prepare AWS safely before adding automated uploads from Python.

## Account Security Baseline

| Item | Status |
|---|---|
| Root MFA enabled | Confirmed |
| Root access keys absent | Confirmed |
| Budget alert configured | Confirmed |
| Primary region selected | us-east-1 |

## Primary Region

The selected primary region for this training project is:

`us-east-1`

## S3 Bucket

Bucket name:

s3/buckets/cloud-data-pipeline-cc-20260526

## S3 Security Settings

The S3 bucket was created with the following intended settings:

| Setting | Value |
|---|---|
| Block Public Access | Enabled |
| Object Ownership | Bucket owner enforced |
| ACLs | Disabled |
| Bucket Versioning | Enabled |
| Default Encryption | SSE-S3 |
| Object Lock | Disabled for now |

## Manual Upload Test

A manual upload test was completed by uploading `README.md` to:

`https://us-east-1.console.aws.amazon.com/s3/buckets/cloud-data-pipeline-cc-20260526/docs/`

## Notes

No AWS access keys should be committed to the repository.

No credentials should be stored in `config.json`.

The pipeline will continue to run locally until S3 upload functionality is added in a later lab.