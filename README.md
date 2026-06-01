# Cloud Data Pipeline

This project is a hands-on learning pipeline for cloud, data engineering, and security-oriented technical leadership.

The current pipeline pulls public repository metadata from the GitHub API, saves the raw response, transforms selected fields into structured CSV output, validates the result, logs pipeline activity, and records each run in a manifest.

## Project Goals

This project is designed to build practical experience with:

- Python scripting
- API data ingestion
- JSON handling
- CSV output
- Basic data transformation
- Logging
- Error handling
- Run history
- Data validation
- Git and GitHub workflow
- Pipeline organization

## Current Pipeline Flow

```text
GitHub API
    ↓
fetch_api_data.py
    ↓
data/raw/
    ↓
transform_api_data.py
    ↓
data/processed/
    ↓
validate_output.py
    ↓
data/run_manifest.csv
## How to Run

Activate the virtual environment:

```
venv\Scripts\activate
```

Run the full pipeline:

```
pythonrun_pipeline.py
```

## Current Outputs

Raw API responses are saved in:

```
data/raw/
```

Processed CSV outputs are saved in:

```
data/processed/
```

The latest processed output is saved as:

```
data/processed/latest_repo_summary.csv
```

Each pipeline run is recorded in:

```
data/run_manifest.csv
```

## Current Capabilities

The pipeline currently supports:

- Pulling public GitHub API data
- Saving raw JSON output
- Creating timestamped raw and processed files
- Maintaining latest-output files
- Transforming selected repository fields into CSV
- Logging pipeline events
- Handling common errors
- Validating processed output
- Recording run history

## Next Steps

Planned improvements include:

- Expanding from one repository to multiple repositories
- Adding security-relevant data sources
- Adding cloud storage
- Adding scheduled execution
- Creating dashboard-ready outputs
- Adding portfolio narrative and architecture diagrams

## Project Documentation

Additional project documentation:

- [Architecture Summary](docs/architecture_summary.md)
- [Portfolio Narrative](docs/portfolio_narrative.md)

## Day 14

Completed a foundation wrap-up review.

Added `foundation_status_report.py`, which checks the key local pipeline artifacts and generates `foundation_status_report.md`.

The report checks for:

- Raw data folder
- Processed data folder
- Latest raw API output
- Latest processed CSV output
- Pipeline log
- Run manifest

This marks the local pipeline foundation as ready for the next phase of security-data expansion.

## Day 15

Selected the Phase 2 security-data direction.

The project will expand from a generic API training pipeline into a vulnerability/risk intelligence pipeline.

The first planned security data source is the CISA Known Exploited Vulnerabilities catalog.

Phase 2 goals include:

- Ingesting CISA KEV data
- Transforming KEV data into structured CSV output
- Validating KEV output
- Adding risk-oriented enrichment
- Creating executive-summary outputs
- Preparing the project for cloud storage and dashboarding

Additional detail is documented in:

- [Security Data Direction](docs/security_data_direction.md)

## Day 16

Added CISA Known Exploited Vulnerabilities ingestion.

The project now includes `fetch_kev_data.py`, which pulls the CISA KEV JSON feed and saves both:

- A timestamped raw KEV file in `data/raw/`
- A latest KEV convenience file at `data/raw/latest_kev_data.json`

This is the first step in moving the project from a generic API training pipeline toward a security-data pipeline focused on vulnerability and risk intelligence.

## Day 17

Added CISA KEV transformation.

The project now includes `transform_kev_data.py`, which reads the latest raw CISA KEV JSON file and creates structured CSV outputs.

The KEV transform creates:

- A timestamped processed KEV CSV in `data/processed/`
- A latest KEV CSV at `data/processed/latest_kev_summary.csv`

The structured KEV output includes:

- CVE ID
- Vendor/project
- Product
- Vulnerability name
- Date added
- Short description
- Required action
- Due date
- Known ransomware campaign use
- Notes

This moves the security-data pipeline from raw ingestion toward usable vulnerability intelligence output.

## Day 18

Added CISA KEV output validation.

The project now includes `validate_kev_output.py`, which validates the structured KEV CSV output.

The validation checks that:

- The KEV processed output file exists
- The KEV processed output file is not empty
- Required KEV columns are present
- CVE ID values are populated
- Vendor/project values are populated
- Date added values are populated
- Duplicate CVE IDs are counted and reported

This adds a quality gate for the security-data portion of the pipeline.

## Day 19

Updated the pipeline runner to execute both the GitHub API flow and the CISA KEV flow.

The full pipeline now runs:

1. Fetch GitHub API data
2. Transform GitHub API data
3. Validate GitHub processed output
4. Fetch CISA KEV data
5. Transform CISA KEV data
6. Validate CISA KEV output
7. Append a combined run record to `data/run_manifest.csv`

This moves the project from separate security-data scripts toward a multi-source pipeline workflow.

## Day 20

Added risk-oriented CISA KEV enrichment.

The project now includes `enrich_kev_data.py`, which reads the structured KEV summary and adds risk-oriented fields.

The enriched KEV output includes:

- `is_known_exploited`
- `days_until_due`
- `is_overdue`
- `priority_bucket`

The priority bucket is a simple derived field intended to support early risk triage:

- `Critical`: overdue and associated with known ransomware campaign use
- `High`: overdue, or due soon with known ransomware campaign use
- `Medium`: due within 30 days
- `Monitor`: due later than 30 days
- `Review`: missing or invalid due date

This moves the project from basic security-data transformation toward risk-oriented vulnerability intelligence.

## Day 21

Added an executive summary output.

The project now includes `create_executive_summary.py`, which reads the enriched CISA KEV output and creates summary metrics.

The executive summary includes:

- Total vulnerabilities
- Overdue vulnerabilities
- Vulnerabilities due within 30 days
- Known ransomware campaign use count
- Counts by priority bucket
- Top vendors/projects by count

The latest executive summary is saved at:

- `data/processed/latest_executive_summary.csv`

Timestamped executive summary outputs are also saved in `data/processed/`.

This creates a manager-friendly output from the security-data pipeline.

## Day 22

Completed a project checkpoint and cleanup review.

The current pipeline now supports:

- GitHub API ingestion
- CISA KEV ingestion
- Raw data preservation
- Structured CSV outputs
- Data validation
- KEV risk enrichment
- Executive summary generation
- Pipeline logging
- Run manifest tracking

The current project status is documented in:

- [Project Status](docs/project_status.md)

This checkpoint stabilizes the local pipeline before moving into the cloud storage phase.

## Day 23

Started the AWS/S3 preparation phase.

Day 23 focused on preparing the cloud side safely before adding automated uploads.

Completed planning and setup items include:

- Confirmed AWS account security baseline
- Confirmed root MFA and no root access keys
- Created or identified a training S3 bucket
- Kept S3 public access blocked
- Enabled bucket versioning
- Confirmed default encryption
- Created planned S3 prefixes for raw data, processed data, logs, manifests, and documentation
- Completed a manual upload test
- Added AWS setup and S3 storage planning documentation

Related documentation:

- [AWS Setup Notes](docs/aws_setup_notes.md)
- [S3 Storage Plan](docs/s3_storage_plan.md)

## Day 24

Designed the initial S3 upload behavior.

The first S3 upload workflow will upload only the latest pipeline outputs, not every timestamped archive file.

Planned upload targets include:

- Latest raw GitHub API data
- Latest raw CISA KEV data
- Latest processed GitHub summary
- Latest processed KEV summary
- Latest enriched KEV output
- Latest executive summary
- Run manifest
- Pipeline log

The initial S3 upload design is documented in:

- [S3 Upload Design](docs/s3_upload_design.md)

README.md

## Day 26

Added standalone S3 upload capability.

The project now includes `upload_to_s3.py`, which uploads selected local pipeline outputs to the configured private S3 bucket.

The script uploads:

- Latest GitHub raw data
- Latest CISA KEV raw data
- Latest GitHub processed summary
- Latest CISA KEV summary
- Latest enriched KEV output
- Latest executive summary
- Run manifest
- Pipeline log

The S3 upload script remains separate from `run_pipeline.py` for now. This keeps cloud upload behavior isolated until it is tested and stable.

AWS credentials are not stored in the repository or in `config.json`.

## Day 27

Wired S3 upload into the full pipeline runner.

The project now runs the local data pipeline and uploads selected outputs to S3 with one command:

```powershell
python run_pipeline.py

## Day 28

Added governance and evidence documentation.

The project now documents:

- Governance model
- Evidence inventory
- Audit trail strategy
- Evidence retention rationale

This extends the project beyond data processing into governance and compliance-oriented design.

## Day 29

Added evidence integrity verification.

The project now includes SHA-256 hashing for critical pipeline evidence files.

New scripts:

- `generate_hashes.py`
- `verify_hashes.py`

New output:

- `data/integrity/file_hashes.csv`

The hash manifest records:

- Hash generation timestamp
- File path
- File size
- SHA-256 hash

This allows key evidence files to be verified later for unexpected changes or missing files.