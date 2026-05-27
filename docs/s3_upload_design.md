# S3 Upload Design

## Purpose

This document defines the initial S3 upload behavior for the cloud data pipeline project.

The goal is to upload selected local pipeline outputs to a private S3 bucket without changing the local pipeline behavior.

## Design Decision

The initial S3 upload script will upload only the latest output files, not every timestamped file.

This keeps the first cloud version simple and predictable.

Timestamped archive uploads can be added later after the basic S3 upload workflow is stable.

## Files to Upload

| Local File | S3 Prefix | Purpose |
|---|---|---|
| `data/raw/latest_api_data.json` | `cloud-data-pipeline/raw/latest_api_data.json` | Latest GitHub raw data |
| `data/raw/latest_kev_data.json` | `cloud-data-pipeline/raw/latest_kev_data.json` | Latest CISA KEV raw data |
| `data/processed/latest_repo_summary.csv` | `cloud-data-pipeline/processed/latest_repo_summary.csv` | Latest GitHub processed summary |
| `data/processed/latest_kev_summary.csv` | `cloud-data-pipeline/processed/latest_kev_summary.csv` | Latest CISA KEV structured summary |
| `data/processed/latest_kev_enriched.csv` | `cloud-data-pipeline/processed/latest_kev_enriched.csv` | Latest risk-enriched KEV output |
| `data/processed/latest_executive_summary.csv` | `cloud-data-pipeline/processed/latest_executive_summary.csv` | Latest executive summary |
| `data/run_manifest.csv` | `cloud-data-pipeline/manifests/run_manifest.csv` | Pipeline run history |
| `pipeline.log` | `cloud-data-pipeline/logs/pipeline.log` | Pipeline operational log |

## Files Not to Upload

The upload script should not upload:

- `venv/`
- `.git/`
- `.env`
- AWS credentials
- Local cache files
- Python bytecode files
- Unreviewed timestamped archives

## S3 Layout

```text
cloud-data-pipeline/
  raw/
    latest_api_data.json
    latest_kev_data.json
  processed/
    latest_repo_summary.csv
    latest_kev_summary.csv
    latest_kev_enriched.csv
    latest_executive_summary.csv
  manifests/
    run_manifest.csv
  logs/
    pipeline.log
    
## Planned Upload Script

The future upload script should be named:

`upload_to_s3.py`

The script should:

1. Load S3 settings from `config.json`
2. Check that each local source file exists
3. Upload each file to the correct S3 key
4. Log each upload
5. Print a clear success/failure message
6. Fail safely if required files are missing

## Configuration Needs

The next config update should include:

- S3 bucket name
- S3 base prefix
- Local-to-S3 file mapping

Credentials should not be stored in `config.json`.

## Security Notes

The S3 bucket should remain private.

Block Public Access should remain enabled.

AWS credentials should be managed outside the repository.

No secrets should be committed to GitHub.