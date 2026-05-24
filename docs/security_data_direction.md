# Security Data Direction

## Phase 2 Direction

The next phase of this project will expand the local data pipeline from a generic API training workflow into a security-data pipeline focused on vulnerability and risk intelligence.

The recommended direction is:

> Build a vulnerability/risk intelligence pipeline using public security data sources.

## Why This Direction

This direction fits the broader career goal because it connects cloud, data engineering, cybersecurity, GRC, risk management, and executive reporting.

The current foundation already demonstrates:

- API ingestion
- Raw data preservation
- Structured output
- Logging
- Error handling
- Validation
- Run history
- Documentation
- GitHub workflow

The next phase will apply those same patterns to security-relevant data.

## Initial Security Data Source

The first recommended security data source is the CISA Known Exploited Vulnerabilities catalog.

This catalog is useful because it focuses on vulnerabilities known to have been exploited in the wild. That makes it more directly relevant to prioritization than a generic vulnerability list.

## Planned Security Data Sources

Potential data sources for this project include:

| Source | Purpose |
|---|---|
| CISA Known Exploited Vulnerabilities catalog | Known exploited vulnerability prioritization |
| NVD CVE data | Broader vulnerability metadata |
| EPSS data | Exploit prediction scoring |
| Sample asset inventory | Simulated enterprise exposure context |
| Sample risk register | GRC/risk reporting context |

## Target Future Pipeline

The intended future pipeline is:

```text
Security data source
    ↓
Fetch raw security data
    ↓
Save raw data
    ↓
Transform selected fields
    ↓
Validate output
    ↓
Enrich with risk context
    ↓
Generate executive summary
    ↓
Record run history
    ↓
Optionally upload to cloud storage
