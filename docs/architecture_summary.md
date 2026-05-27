# Architecture Summary

## Overview

This project implements a basic local data pipeline that ingests public API data, stores the raw response, transforms selected fields into structured output, validates the output, logs execution activity, and records pipeline run history.

## Pipeline Flow

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

## Components

| Component | Purpose |
| --- | --- |
| `config.json` | Centralizes pipeline settings |
| `fetch_api_data.py` | Pulls raw API data |
| `transform_api_data.py` | Converts raw JSON to structured CSV |
| `validate_output.py` | Performs basic quality checks |
| `run_pipeline.py` | Orchestrates the pipeline steps |
| `pipeline.log` | Captures operational events |
| `data/run_manifest.csv` | Records run history |

## Design Principles

This project demonstrates several foundational pipeline design principles:

- Separation of code and configuration
- Separation of raw and processed data
- Repeatable execution
- Timestamped outputs
- Operational logging
- Basic error handling
- Basic validation
- Run history and traceability

## Current Limitations

The current pipeline is intentionally simple. It runs locally, uses one public API endpoint, and writes local files.

Current limitations include:

- No cloud storage
- No scheduler
- No authentication
- No database
- No dashboard
- Limited validation rules
- Single API source

## Future Enhancements

Potential next steps include:

- Add multiple API sources
- Use security data sources such as NVD or CISA KEV
- Store outputs in cloud object storage
- Add database loading
- Add scheduled execution
- Create dashboard-ready outputs
- Add tests
- Add CI/CD