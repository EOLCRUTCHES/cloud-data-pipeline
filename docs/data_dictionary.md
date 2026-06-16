# Data Dictionary

## Purpose

This document explains the sample data used in the `cloud-data-pipeline` project.

The sample files are intentionally small, demo-safe artifacts used to show expected pipeline input and output.

## Sample Files

| File | Purpose |
|---|---|
| `data/sample_api_response.json` | Demo-safe example of raw API-style input |
| `data/sample_processed_output.csv` | Demo-safe example of processed pipeline output |

## Source Data: `sample_api_response.json`

| Field | Type | Description |
|---|---|---|
| `source` | string | Identifies the demo source system |
| `description` | string | Explains the purpose of the sample API response |
| `records` | list | Collection of individual record objects |
| `records.id` | integer | Unique identifier for the record |
| `records.category` | string | Simple category value used for grouping |
| `records.value` | integer | Numeric value used for transformation or analysis |

## Processed Data: `sample_processed_output.csv`

| Field | Type | Description |
|---|---|---|
| `id` | integer | Unique identifier carried from source data |
| `category` | string | Category value carried from source data |
| `value` | integer | Numeric value carried from source data |

## Data Governance Notes

- Sample files should remain small and safe for public portfolio use.
- Raw generated API files should not accumulate in the repository.
- Repeated generated outputs should be ignored or purged unless intentionally preserved as examples.
- Future pipeline versions should document any new fields added during transformation.

## Portfolio Relevance

This data dictionary supports the portfolio by showing that the project is not just code-focused. It also considers data meaning, field definitions, sample handling, and documentation discipline.