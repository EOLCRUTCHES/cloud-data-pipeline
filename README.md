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
text
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

powershell
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

## Milestone 1 Complete

Days 1–30 focused on building a cloud-enabled security evidence pipeline.

Major accomplishments:

- API ingestion
- Data transformation
- Validation
- Executive reporting
- AWS S3 integration
- Governance documentation
- Evidence integrity verification

See:

- docs/demo_walkthrough.md
- docs/interview_talking_points.md
- docs/milestone_1_summary.md

## Portfolio Direction

This project began as a data/cloud pipeline learning project and is now being extended into a secure automation portfolio.

The long-term objective is to demonstrate the ability to build, secure, assess, and explain automated cloud-enabled systems.

### Portfolio Thesis

I possess the technical and business acumen to help organizations secure automation and automate security.

### Planned Capability Layers

1. Data/Cloud Pipeline
   - Ingest data
   - Transform data
   - Track pipeline runs
   - Store outputs

2. Cloud Security
   - Identity and access management
   - Secure storage
   - Encryption
   - Logging and monitoring
   - Secrets management

3. Security Automation
   - Automated validation
   - Automated evidence collection
   - Control mapping
   - Risk register generation

4. Security AI
   - Evidence-aware assistant
   - Controlled retrieval
   - Risk explanation
   - Audit-support summaries

5. Provenance and Trust
   - Artifact hashing
   - Chain-of-custody tracking
   - Tamper-evident evidence records

6. Crypto-Agility and Post-Quantum Readiness
   - Cryptographic inventory
   - Key dependency tracking
   - Future migration considerations

   ## Day 30 - Portfolio Pivot

Today marks the transition from a basic data/cloud learning project into a secure automation portfolio.

The project will continue building on the existing pipeline rather than starting a separate repository. The goal is to demonstrate a complete technical and governance story: build automation, secure it, automate evidence, and make trust verifiable.

## Day 32 - Generated Files Policy

Today I clarified which artifacts belong in the repository and which should be treated as disposable generated output.

The repo should preserve source code, representative samples, and portfolio-ready documentation while excluding repeated raw API pulls, temporary outputs, logs, and generated clutter.

### Working Rule

Keep samples. Ignore clutter. Regenerate outputs when needed.

## Day 33 - Sample Data Artifacts

Today I added small, demo-safe sample data files to represent pipeline input and output.

### Sample Files

- `data/sample_api_response.json`
- `data/sample_processed_output.csv`

These files are intentionally small and stable so they can remain in the repository as portfolio examples.

Generated raw files and repeated daily outputs should remain disposable and ignored when appropriate.

## Day 34 - Data Dictionary

Today I added a data dictionary to explain the sample input and output files used by the pipeline.

This improves the repo by making the sample data understandable to reviewers and introduces basic data governance discipline.

### Artifact Added

- `docs/data_dictionary.md`

## Day 35 - Sample Data Validation

Today I added a Python validation script to confirm that the sample input and output files exist and contain the expected fields.

### Artifact Added

- `src/validate_sample_data.py`

### Validation Checks

- Confirms `data/sample_api_response.json` exists
- Confirms JSON is valid
- Confirms required JSON fields are present
- Confirms `data/sample_processed_output.csv` exists
- Confirms required CSV columns are present
- Confirms CSV contains data rows

### Portfolio Relevance

This introduces basic data quality control and creates the foundation for later security evidence validation, control checking, and AI input validation.

## Day 36 - Validation Evidence Report

Today I upgraded the sample data validation script so it writes a markdown evidence report instead of only printing results to the console.

### Artifact Updated

- `src/validate_sample_data.py`

### Artifact Added

- `evidence/generated/sample_data_validation_report.md`

### Portfolio Relevance

This introduces a key secure automation pattern: validation results should become reusable evidence.

The project is now beginning to show how automated checks can support auditability, data governance, and future security evidence workflows.

## Day 37 - Evidence Index

Today I added a Python script that scans generated evidence files and creates an evidence index.

### Artifact Added

- `src/generate_evidence_index.py`

### Artifact Updated

- `evidence/evidence_index.md`

### Portfolio Relevance

This creates an audit-support pattern: generated evidence should be organized, findable, and reusable.

The project now has the beginning of an evidence package rather than isolated validation outputs.

## Day 38 - Control Matrix v1

Today I created the first version of the project control matrix.

### Artifact Added

- `src/generate_control_matrix.py`

### Artifact Updated

- `security/control_matrix.csv`

### Controls Added

- `DC-001` - Sample data validation
- `DC-002` - Evidence indexing

### Portfolio Relevance

This connects technical automation to control objectives, evidence artifacts, and risks addressed.

The project now demonstrates the beginning of a GRC automation pattern: scripts produce evidence, evidence supports controls, and controls reduce specific risks.

## Day 39 - Risk Register v1

Today I created the first version of the project risk register.

### Artifact Added

- `src/generate_risk_register.py`

### Artifact Updated

- `security/risk_register.csv`

### Risks Added

- `RISK-001` - Invalid sample data processed
- `RISK-002` - Generated evidence becomes hard to locate
- `RISK-003` - Repository accumulates generated clutter

### Portfolio Relevance

This connects the technical automation work to governance and risk management.

The project now demonstrates a basic GRC pattern:

Risk → Control → Evidence → Status

## Day 40 - Executive Summary v1

Today I created the first version of the project executive summary.

### Artifact Updated

- `docs/executive_summary.md`

### Portfolio Relevance

This translates the technical work into business, security, and governance language.

The project now has an executive-facing explanation of how the automation, evidence, controls, and risks fit together.

## Day 41 - Architecture Diagram v1

Today I created the first architecture diagram for the secure automation portfolio.

### Artifact Updated

- `docs/architecture_diagram.md`

### Portfolio Relevance

This diagram shows how sample data, validation, evidence, control mapping, risk tracking, and executive explanation connect into a single secure automation workflow.

The project now has a visual system explanation instead of only individual scripts and documents.

## Day 42 - Governance Workflow Runner

Today I created a workflow runner that executes the current secure automation chain with one command.

### Artifact Added

- `src/run_governance_workflow.py`

### Workflow Steps

1. Validate sample data and generate evidence.
2. Generate the evidence index.
3. Generate the control matrix.
4. Generate the risk register.

### Portfolio Relevance

This turns separate scripts into an orchestrated governance automation workflow.

The project now demonstrates a repeatable pattern for generating validation evidence, indexing evidence, mapping controls, and updating risk visibility.

## Day 43 - Workflow Evidence Report

Today I upgraded the governance workflow runner so it writes a workflow execution report.

### Artifact Updated

- `src/run_governance_workflow.py`

### Runtime Evidence Generated

- `evidence/generated/governance_workflow_run_report.md`

### Portfolio Relevance

This adds an auditability pattern to the workflow itself.

The project now demonstrates that automation can execute controls, generate evidence, and produce a report showing whether the workflow completed successfully.

## Day 44 - Artifact Manifest v1
Today I added a generated artifact manifest.

### Artifact Added
- `src/generate_artifact_manifest.py`

### Runtime Evidence Generated
- `evidence/generated/artifact_manifest.md`

### Portfolio Relevance
This creates a project inventory pattern.

The project can now list important data, scripts, evidence, security governance files, and documentation artifacts, along with their existence and file size.

This supports future evidence packaging, artifact integrity checks, provenance tracking, and trust architecture.

## Day 45 - Add Artifact Manifest to Workflow
Today I updated the governance workflow runner so it automatically generates the artifact manifest.

### Artifact Updated
- `src/run_governance_workflow.py`

### Workflow Updated
The workflow now runs:
1. Sample data validation
2. Control matrix generation
3. Risk register generation
4. Artifact manifest generation
5. Evidence index generation

### Portfolio Relevance
This improves the project’s automation maturity by making artifact inventory part of the repeatable governance workflow.

The project can now generate evidence, controls, risks, artifact inventory, and evidence visibility from one command.

## Day 46 - Artifact Hashes v1

Today I added a script that generates SHA-256 hashes for important project artifacts.

### Artifact Added

- `src/generate_artifact_hash_report.py`

### Runtime Evidence Generated

- `evidence/generated/artifact_hash_report.md`
- `provenance/artifact_hashes.csv`

### Portfolio Relevance

This introduces artifact integrity and provenance concepts into the secure automation portfolio.

The project can now generate fingerprints for important files, supporting future tamper-evidence, evidence integrity, and trust architecture patterns.

## Day 47 - Add Artifact Hashing to Workflow
updated the governance workflow so artifact hash generation runs automatically.

### Artifact Updated
- `src/run_governance_workflow.py`

### Workflow Updated
The workflow now runs:
1. Sample data validation
2. Control matrix generation
3. Risk register generation
4. Artifact manifest generation
5. Artifact hash report generation
6. Evidence index generation

### Portfolio Relevance
This improves the secure automation workflow by making artifact integrity evidence part of the standard process.
The project now generates validation evidence, governance artifacts, artifact inventory, artifact hashes, and evidence visibility from one command.

## Day 48 - Verify Artifact Hashes v1
Today I added a script that verifies current artifact hashes against the saved hash baseline.

### Artifact Added
- `src/verify_artifact_hashes.py`

### Runtime Evidence Generated
- `evidence/generated/artifact_hash_verification_report.md`

### Portfolio Relevance
This introduces artifact integrity verification into the secure automation portfolio.
The project can now detect changed or missing artifacts by comparing current SHA-256 hashes against a saved baseline.
This supports tamper-evident evidence, provenance tracking, and trust architecture.

## Day 49 - AWS Evidence Source Map v1
Today I added an AWS evidence source map to reconnect the secure automation workflow to cloud implementation.

### Artifact Added
- `docs/cloud/aws_evidence_source_map.md`

### Portfolio Relevance
This reconnects the local governance workflow to AWS cloud security evidence.
The project is now positioned to collect AWS configuration evidence, map it to controls and risks, and later compare equivalent control patterns across Azure, GCP, and OCI.

## Day 50 - AWS Account Context Evidence v1

Today I added a script that collects basic AWS CLI and account-context evidence without creating, modifying, or deleting cloud resources.

### Artifact Added
- `src/collect_aws_account_context.py`

### Runtime Evidence Generated
- `evidence/generated/aws_account_context_report.md`

### Portfolio Relevance
This reconnects the secure automation portfolio to AWS by collecting safe cloud-readiness evidence.
The project now demonstrates an AWS evidence collection pattern that supports cloud security governance, account-context awareness, cost control, and future multi-cloud control mapping.

## Day 51 - AWS S3 Inventory Evidence v1

Today I added a script that collects basic AWS S3 inventory evidence without creating, modifying, or deleting cloud resources.

### Artifact Added
- `src/collect_aws_s3_inventory.py`

### Runtime Evidence Generated
- `evidence/generated/aws_s3_inventory_report.md`

### Portfolio Relevance
This introduces AWS object-storage evidence collection into the secure automation portfolio.

The project now demonstrates a safe read-only pattern for collecting cloud storage context, masking sensitive bucket identifiers, and generating local evidence for future control and risk mapping.

## Day 52 - AWS Authorization Evidence v1
Today I added a script that interprets AWS authorization results from the S3 inventory evidence report.

### Artifact Added
- `src/generate_aws_authorization_evidence.py`

### Runtime Evidence Generated
- `evidence/generated/aws_authorization_evidence_report.md`

### Portfolio Relevance
This turns an AWS permission denial into useful cloud security evidence.
The project now demonstrates that cloud automation should capture authorization boundaries, explain evidence collection limits, and connect permission behavior to least privilege, governance, and risk.

## Day 53 - Cloud Admin Access Patterns
Today I added a cloud administrative access pattern matrix.

### Artifacts Added
- `src/generate_cloud_access_pattern_matrix.py`
- `security/cloud_admin_access_patterns.csv`
- `evidence/generated/cloud_admin_access_pattern_report.md`

### Key Lesson
A bastion host is not the control objective. It is one implementation pattern.
The real control objective is to ensure administrative access is authorized, minimized, segmented, monitored, and reviewable.

### Portfolio Relevance
This strengthens the project by translating on-prem systems engineering intuition into cloud architecture evidence.
The project now compares direct public access, bastion hosts, VPN/private connectivity, identity-aware session management, and privileged access workflows across AWS, Azure, GCP, and OCI.

## Day 54 - Cloud Pattern Field Cards v1

Today I converted the cloud administrative access pattern matrix into portable study cards.

### Artifacts Added

- `src/generate_cloud_pattern_field_cards.py`
- `docs/cloud/cloud_admin_access_field_cards.md`
- `evidence/generated/cloud_pattern_field_card_report.md`

### Key Lesson

Cloud architecture fluency comes from understanding patterns, not memorizing vendor vocabulary.

### Study Pattern

For each cloud access pattern, I should be able to explain:

- what it replaces on-prem,
- how it works in cloud,
- what risk it reduces,
- what risk it introduces,
- what evidence proves it is working,
- how the pattern translates across AWS, Azure, GCP, and OCI.

### Portfolio Relevance

This artifact turns cloud architecture concepts into reusable field cards for executive, security architecture, CCSP, and multi-cloud readiness.

## Day 55 - Cloud Access Pattern Decision Guide v1

## Day 56 - Cloud Admin Access ADR

Today I generated an architecture decision record for cloud administrative access patterns.

### Artifacts Added

- `src/generate_cloud_admin_access_adr.py`
- `docs/cloud/adr-001-cloud-admin-access-pattern.md`
- `evidence/generated/adr_001_cloud_admin_access_report.md`

### Key Lesson

A senior cloud/security decision is not just a preferred tool. It is a documented decision with context, rationale, exceptions, consequences, and evidence expectations.

### Portfolio Relevance

This artifact turns cloud access pattern study material into a defensible architecture decision record suitable for executive, audit, security architecture, and governance discussions.

Today I added a decision guide for cloud administrative access patterns.

### Artifacts Added

- `src/generate_cloud_access_decision_guide.py`
- `security/cloud_admin_access_decision_rubric.csv`
- `docs/cloud/cloud_admin_access_decision_guide.md`
- `evidence/generated/cloud_admin_access_decision_guide_report.md`

### Key Lesson

Knowing cloud patterns is not enough. I need to be able to choose, defend, and evidence the right pattern for the workload.

### Decision Focus

The guide compares administrative access patterns using:

- exposure risk,
- standing privilege risk,
- logging strength,
- operational burden,
- governance strength,
- scenario fit,
- minimum evidence requirements.

### Portfolio Relevance

This artifact moves the project from cloud vocabulary to cloud architecture judgment.

It demonstrates the ability to evaluate direct public access, bastion hosts, VPN/private connectivity, identity-aware session management, and privileged access workflows based on risk and evidence.

## Day 57 - Cloud Admin Access Evidence Kit

Today I generated an evidence kit for the cloud administrative access standard.

### Artifacts Added

- `src/generate_cloud_admin_access_evidence_kit.py`
- `security/cloud_admin_access_evidence_requirements.csv`
- `security/cloud_admin_access_exception_register.csv`
- `docs/cloud/cloud_admin_access_evidence_playbook.md`
- `evidence/generated/cloud_admin_access_evidence_kit_report.md`

### Key Lesson

Architecture decisions become governable when they define the evidence required to prove implementation, review exceptions, and monitor risk.

### Portfolio Relevance

This artifact converts the cloud administrative access ADR into an audit-ready evidence model covering identity, network exposure, access paths, session logging, privileged access, exceptions, and break-glass governance.

## Day 58 - AWS Admin Port Exposure Evidence Collector

Today I added a read-only AWS evidence collector for administrative port exposure.

### Artifacts Added

- `src/collect_aws_admin_port_exposure.py`
- `security/aws_admin_port_exposure_findings.csv`
- `evidence/generated/aws_admin_port_exposure_report.md`

### Key Lesson

Cloud access standards become real when they can be tested against live configuration evidence.

### What the Collector Checks

The collector reviews AWS security groups for administrative port exposure, including:

- SSH / 22
- RDP / 3389
- WinRM HTTP / 5985
- WinRM HTTPS / 5986

### Portfolio Relevance

This artifact connects the cloud administrative access ADR to implementation evidence.

It demonstrates read-only cloud evidence collection, exposure classification, sanitized reporting, and control mapping.

## Day 59 - AWS Evidence Collector Permission Preflight

Today I added a preflight check for AWS evidence collector permissions.

### Artifacts Added

- `src/check_aws_evidence_collector_permissions.py`
- `security/aws_evidence_collector_permissions.csv`
- `docs/cloud/aws_evidence_collector_permission_playbook.md`
- `evidence/generated/aws_evidence_collector_permission_preflight_report.md`

### Key Lesson

Cloud evidence collectors should verify required read-only permissions before running deeper collection logic.

### Portfolio Relevance

This artifact turns AWS authorization failures into documented evidence collection findings.

It shows which collector permissions are present, which are missing, and why each permission is needed.

## Day 60 - AWS Admin Access Evidence Workflow

Today I added a workflow runner for AWS cloud administrative access evidence.

### Artifacts Added

- `src/run_aws_admin_access_evidence_workflow.py`
- `docs/cloud/aws_admin_access_evidence_package.md`
- `evidence/generated/aws_admin_access_evidence_workflow_report.md`

### Key Lesson

Cloud evidence collection should run as a controlled workflow: permission preflight first, live evidence collection second, and package-level reporting last.

### Portfolio Relevance

This artifact turns the cloud administrative access work into a repeatable evidence package.

It demonstrates authorization-aware evidence collection, live configuration review, exception visibility, and executive/audit-ready reporting.

## Day 61 - Security Evidence Corpus v1

Today I created the first structured security evidence corpus for the project.

### Artifacts Added

- `src/build_security_evidence_corpus.py`
- `ai/security_evidence_corpus.jsonl`
- `ai/security_evidence_corpus_manifest.csv`
- `evidence/generated/security_evidence_corpus_report.md`

### Key Lesson

An evidence-aware AI system should not begin with unstructured files. It should begin with a bounded corpus that preserves source paths, document IDs, hashes, summaries, and traceability.

### Portfolio Relevance

This artifact starts the Security AI MVP phase.

It prepares the project for future evidence-aware retrieval, citation, summarization, and governance workflows by organizing existing cloud/security artifacts into an auditable source corpus.

## Day 62 - Security Evidence Retrieval v1

Today I added a bounded retrieval layer for the local security evidence corpus.

### Artifacts Added

- `src/query_security_evidence_corpus.py`
- `ai/security_evidence_query_results.csv`
- `evidence/generated/security_evidence_query_report.md`

### Key Lesson

Security AI should retrieve from a controlled evidence corpus before attempting to answer questions.

### Portfolio Relevance

This artifact creates the first evidence search layer for the Security AI MVP.

It searches only indexed project evidence, ranks matching records, and preserves source traceability through document IDs and source paths.