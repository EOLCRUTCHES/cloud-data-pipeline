# S3 Storage Plan

## Purpose

This document defines the planned S3 layout for the cloud data pipeline project.

The goal is to preserve the same separation already used locally:

- Raw data
- Processed data
- Logs
- Run manifests
- Documentation

## Planned Bucket Layout

```text
s3://cloud-data-pipeline-cc-20260526/cloud-data-pipeline/raw/
s3://cloud-data-pipeline-cc-20260526/cloud-data-pipeline/processed/
s3://cloud-data-pipeline-cc-20260526/cloud-data-pipeline/logs/
s3://cloud-data-pipeline-cc-20260526/cloud-data-pipeline/manifests/
s3://cloud-data-pipeline-cc-20260526/docs/

## Initial Upload Scope

The initial upload scope will focus on latest pipeline outputs only.

The first S3 upload script will upload:

- `data/raw/latest_api_data.json`
- `data/raw/latest_kev_data.json`
- `data/processed/latest_repo_summary.csv`
- `data/processed/latest_kev_summary.csv`
- `data/processed/latest_kev_enriched.csv`
- `data/processed/latest_executive_summary.csv`
- `data/run_manifest.csv`
- `pipeline.log`

Timestamped archive files will remain local for now.

This keeps the first cloud upload workflow simple and reduces unnecessary S3 clutter.