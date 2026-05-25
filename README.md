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

