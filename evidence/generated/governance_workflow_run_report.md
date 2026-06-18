# Governance Workflow Run Report

Generated: `2026-06-18T15:58:00.701640+00:00`

Overall Status: **PASS**

## Workflow Steps

| Step | Script | Status |
|---|---|---|
| Validate sample data and generate evidence report | `src/validate_sample_data.py` | PASS |
| Generate control matrix | `src/generate_control_matrix.py` | PASS |
| Generate risk register | `src/generate_risk_register.py` | PASS |
| Generate artifact manifest | `src/generate_artifact_manifest.py` | PASS |
| Generate artifact hash report | `src/generate_artifact_hash_report.py` | PASS |
| Generate evidence index | `src/generate_evidence_index.py` | PASS |

## Step Output

### Validate sample data and generate evidence report

Status: **PASS**

Output:

```text
PASS: JSON sample file is valid
PASS: CSV sample file is valid
PASS: All sample data validation checks passed
Evidence report written to: evidence\generated\sample_data_validation_report.md
```

### Generate control matrix

Status: **PASS**

Output:

```text
Control matrix written to: security\control_matrix.csv
```

### Generate risk register

Status: **PASS**

Output:

```text
Risk register written to: security\risk_register.csv
```

### Generate artifact manifest

Status: **PASS**

Output:

```text
Artifact manifest written to: evidence\generated\artifact_manifest.md
```

### Generate artifact hash report

Status: **PASS**

Output:

```text
Artifact hashes written to: provenance\artifact_hashes.csv
Artifact hash report written to: evidence\generated\artifact_hash_report.md
```

### Generate evidence index

Status: **PASS**

Output:

```text
Evidence index written to: evidence\evidence_index.md
```

## Portfolio Relevance

This report demonstrates that the governance automation workflow creates evidence of execution, not just individual output files.

This supports auditability, repeatability, and future security evidence automation.
