# Artifact Manifest

Generated: `2026-06-18T15:58:00.392099+00:00`

## Purpose

This manifest lists important project artifacts and confirms whether they exist.

It supports portfolio review, audit readiness, evidence organization, and future provenance tracking.

## Artifact Inventory

| Group | Artifact | Status | Size Bytes | Purpose |
|---|---|---|---:|---|
| Sample Data | `data/sample_api_response.json` | Present | 362 | Demo-safe raw API-style input data |
| Sample Data | `data/sample_processed_output.csv` | Present | 58 | Demo-safe processed pipeline output |
| Automation Script | `src/validate_sample_data.py` | Present | 4469 | Validates sample data and creates validation evidence |
| Automation Script | `src/generate_evidence_index.py` | Present | 2169 | Generates the evidence index |
| Automation Script | `src/generate_control_matrix.py` | Present | 1850 | Generates the control matrix |
| Automation Script | `src/generate_risk_register.py` | Present | 2636 | Generates the risk register |
| Automation Script | `src/run_governance_workflow.py` | Present | 4926 | Runs the governance workflow |
| Evidence | `evidence/generated/sample_data_validation_report.md` | Present | 508 | Shows sample data validation results |
| Evidence | `evidence/generated/governance_workflow_run_report.md` | Present | 1671 | Shows workflow execution results |
| Evidence | `evidence/evidence_index.md` | Present | 959 | Lists generated evidence artifacts |
| Security Governance | `security/control_matrix.csv` | Present | 700 | Maps controls to evidence and risks |
| Security Governance | `security/risk_register.csv` | Present | 1073 | Maps risks to mitigations, controls, and evidence |
| Documentation | `docs/executive_summary.md` | Present | 2902 | Explains the project in executive language |
| Documentation | `docs/architecture_diagram.md` | Present | 2668 | Shows the secure automation workflow architecture |

## Portfolio Relevance

This manifest demonstrates that the project can inventory its own important artifacts.

That pattern will later support evidence packaging, artifact integrity checks, provenance records, and trust architecture.
