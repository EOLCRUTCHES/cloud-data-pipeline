# Governance Model

## Purpose

This project demonstrates a repeatable and auditable security-data pipeline.

The objective is not only to collect data but to preserve evidence, maintain traceability, and support management decision-making.

---

## Data Sources

### GitHub API

Purpose:

* Demonstrate API ingestion
* Demonstrate structured transformation
* Demonstrate pipeline repeatability

### CISA Known Exploited Vulnerabilities Catalog

Purpose:

* Demonstrate ingestion of authoritative security intelligence
* Demonstrate risk-oriented processing
* Demonstrate executive reporting

---

## Evidence Preservation

### Raw Data

Raw data is preserved before transformation.

Purpose:

* Reproducibility
* Forensic review
* Audit support

Location:

* Local raw data directory
* S3 raw data storage

---

### Processed Data

Processed outputs provide structured reporting.

Purpose:

* Consistency
* Reporting
* Downstream analysis

Location:

* Local processed data directory
* S3 processed data storage

---

## Risk Enrichment

Risk enrichment adds operational context.

Examples:

* Due date calculations
* Overdue determination
* Priority classification

Purpose:

* Support remediation prioritization
* Support management reporting

---

## Executive Reporting

Executive summaries provide management-facing outputs.

Purpose:

* Reduce technical complexity
* Highlight actionable information
* Support leadership decision-making

---

## Logging

Pipeline execution is logged.

Purpose:

* Operational monitoring
* Troubleshooting
* Audit support

Artifact:

* pipeline.log

---

## Run Manifest

Pipeline executions are tracked.

Purpose:

* Traceability
* Historical reporting
* Reproducibility

Artifact:

* data/run_manifest.csv

---

## Cloud Storage

Pipeline outputs are uploaded to private S3 storage.

Purpose:

* Durability
* Centralized evidence retention
* Disaster recovery

Controls:

* Private bucket
* IAM-controlled access
* Encryption enabled

---

## Future Enhancements

Potential future enhancements include:

* Automated retention policies
* Data integrity verification
* Evidence signing
* CI/CD controls
* Automated testing
* Security monitoring
