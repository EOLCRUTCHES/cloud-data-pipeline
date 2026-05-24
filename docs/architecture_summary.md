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
data/run_manifest.csv