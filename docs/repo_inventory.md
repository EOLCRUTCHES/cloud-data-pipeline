# Repo Inventory

## Purpose

This document captures the current state of the cloud-data-pipeline repository as it transitions into a secure automation portfolio.

## Current Project Structure

.gitignore
config.json
create_executive_summary.py
data
demo_walkthrough.md
docs
enrich_kev_data.py
evidence
evidence_inventory.md
fetch_api_data.py
fetch_kev_data.py
foundation_status_report.md
foundation_status_report.py
generate_hashes.py
governance_model.md
load_data.py
pipeline.log
provenance
quantum_readiness
README.md
requirements.txt
run_pipeline.py
sample.csv
security
transform_api_data.py
transform_kev_data.py
upload_to_s3.py
validate_kev_output.py
validate_output.py
verify_hashes.py
data\integrity
data\processed
data\raw
data\run_manifest.csv
docs\architecture_diagram.md
docs\architecture_summary.md
docs\aws_setup_notes.md
docs\demo_walkthrough.md
docs\executive_summary.md
docs\interview_talking_points.md
docs\milestone_1_summary.md
docs\project_status.md
docs\repo_inventory.md
docs\s3_storage_plan.md
docs\s3_upload_design.md
docs\security_data_direction.md
evidence\evidence_index.md
provenance\provenance_model.md
quantum_readiness\crypto_inventory.csv
security\control_matrix.csv
security\risk_register.csv
data\integrity\file_hashes.csv
data\processed\executive_summary_2026-05-24_202444.csv
data\processed\executive_summary_2026-05-24_202753.csv
data\processed\executive_summary_2026-05-24_203103.csv
data\processed\executive_summary_2026-05-24_203509.csv
data\processed\executive_summary_2026-05-27_033339.csv
data\processed\executive_summary_2026-05-27_035739.csv
data\processed\executive_summary_2026-05-27_200509.csv
data\processed\executive_summary_2026-05-28_094536.csv
data\processed\executive_summary_2026-05-28_115924.csv
data\processed\executive_summary_2026-05-29_220450.csv
data\processed\executive_summary_2026-05-29_220733.csv
data\processed\executive_summary_2026-05-30_132241.csv
data\processed\executive_summary_2026-05-30_134252.csv
data\processed\executive_summary_2026-05-30_181724.csv
data\processed\executive_summary_2026-05-30_184439.csv
data\processed\executive_summary_2026-05-31_210416.csv
data\processed\executive_summary_2026-06-02_112658.csv
data\processed\kev_enriched_2026-05-24_201456.csv
data\processed\kev_enriched_2026-05-24_201716.csv
data\processed\kev_enriched_2026-05-24_202752.csv
data\processed\kev_enriched_2026-05-24_203102.csv
data\processed\kev_enriched_2026-05-24_203507.csv
data\processed\kev_enriched_2026-05-27_033338.csv
data\processed\kev_enriched_2026-05-27_035738.csv
data\processed\kev_enriched_2026-05-27_200509.csv
data\processed\kev_enriched_2026-05-28_094535.csv
data\processed\kev_enriched_2026-05-28_115923.csv
data\processed\kev_enriched_2026-05-29_220449.csv
data\processed\kev_enriched_2026-05-29_220732.csv
data\processed\kev_enriched_2026-05-30_132240.csv
data\processed\kev_enriched_2026-05-30_134251.csv
data\processed\kev_enriched_2026-05-30_181723.csv
data\processed\kev_enriched_2026-05-30_184438.csv
data\processed\kev_enriched_2026-05-31_210415.csv
data\processed\kev_enriched_2026-06-02_112658.csv
data\processed\kev_summary_2026-05-24_193939.csv
data\processed\kev_summary_2026-05-24_195016.csv
data\processed\kev_summary_2026-05-24_195749.csv
data\processed\kev_summary_2026-05-24_201714.csv
data\processed\kev_summary_2026-05-24_202749.csv
data\processed\kev_summary_2026-05-24_203100.csv
data\processed\kev_summary_2026-05-24_203503.csv
data\processed\kev_summary_2026-05-27_033335.csv
data\processed\kev_summary_2026-05-27_035736.csv
data\processed\kev_summary_2026-05-27_200506.csv
data\processed\kev_summary_2026-05-28_094534.csv
data\processed\kev_summary_2026-05-28_115922.csv
data\processed\kev_summary_2026-05-29_220447.csv
data\processed\kev_summary_2026-05-29_220731.csv
data\processed\kev_summary_2026-05-30_132238.csv
data\processed\kev_summary_2026-05-30_134248.csv
data\processed\kev_summary_2026-05-30_181720.csv
data\processed\kev_summary_2026-05-30_184436.csv
data\processed\kev_summary_2026-05-31_210414.csv
data\processed\kev_summary_2026-06-02_112656.csv
data\processed\latest_executive_summary.csv
data\processed\latest_kev_enriched.csv
data\processed\latest_kev_summary.csv
data\processed\latest_repo_summary.csv
data\processed\repo_summary.csv
data\processed\repo_summary_2026-05-15_145943.csv
data\processed\repo_summary_2026-05-22_154021.csv
data\processed\repo_summary_2026-05-22_221548.csv
data\processed\repo_summary_2026-05-24_171207.csv
data\processed\repo_summary_2026-05-24_173340.csv
data\processed\repo_summary_2026-05-24_174445.csv
data\processed\repo_summary_2026-05-24_180647.csv
data\processed\repo_summary_2026-05-24_181546.csv
data\processed\repo_summary_2026-05-24_191704.csv
data\processed\repo_summary_2026-05-24_194139.csv
data\processed\repo_summary_2026-05-24_195746.csv
data\processed\repo_summary_2026-05-24_201712.csv
data\processed\repo_summary_2026-05-24_202747.csv
data\processed\repo_summary_2026-05-24_203057.csv
data\processed\repo_summary_2026-05-24_203456.csv
data\processed\repo_summary_2026-05-27_033332.csv
data\processed\repo_summary_2026-05-27_035732.csv
data\processed\repo_summary_2026-05-27_200503.csv
data\processed\repo_summary_2026-05-28_094531.csv
data\processed\repo_summary_2026-05-28_115919.csv
data\processed\repo_summary_2026-05-29_220444.csv
data\processed\repo_summary_2026-05-29_220729.csv
data\processed\repo_summary_2026-05-30_132234.csv
data\processed\repo_summary_2026-05-30_134245.csv
data\processed\repo_summary_2026-05-30_181718.csv
data\processed\repo_summary_2026-05-30_184433.csv
data\processed\repo_summary_2026-05-31_210412.csv
data\processed\repo_summary_2026-06-02_112654.csv
data\raw\api_data.json
data\raw\api_data_2026-05-15_145941.json
data\raw\api_data_2026-05-22_154013.json
data\raw\api_data_2026-05-22_221546.json
data\raw\api_data_2026-05-24_171205.json
data\raw\api_data_2026-05-24_173339.json
data\raw\api_data_2026-05-24_174444.json
data\raw\api_data_2026-05-24_180646.json
data\raw\api_data_2026-05-24_181545.json
data\raw\api_data_2026-05-24_191703.json
data\raw\api_data_2026-05-24_194138.json
data\raw\api_data_2026-05-24_195745.json
data\raw\api_data_2026-05-24_201710.json
data\raw\api_data_2026-05-24_202746.json
data\raw\api_data_2026-05-24_203056.json
data\raw\api_data_2026-05-24_203454.json
data\raw\api_data_2026-05-27_033331.json
data\raw\api_data_2026-05-27_035729.json
data\raw\api_data_2026-05-27_200502.json
data\raw\api_data_2026-05-28_094530.json
data\raw\api_data_2026-05-28_115918.json
data\raw\api_data_2026-05-29_220437.json
data\raw\api_data_2026-05-29_220728.json
data\raw\api_data_2026-05-30_132233.json
data\raw\api_data_2026-05-30_134244.json
data\raw\api_data_2026-05-30_181713.json
data\raw\api_data_2026-05-30_184432.json
data\raw\api_data_2026-05-31_210408.json
data\raw\api_data_2026-06-02_112651.json
data\raw\kev_data_2026-05-24_191534.json
data\raw\kev_data_2026-05-24_194956.json
data\raw\kev_data_2026-05-24_195748.json
data\raw\kev_data_2026-05-24_201713.json
data\raw\kev_data_2026-05-24_202748.json
data\raw\kev_data_2026-05-24_203059.json
data\raw\kev_data_2026-05-24_203501.json
data\raw\kev_data_2026-05-27_033334.json
data\raw\kev_data_2026-05-27_035735.json
data\raw\kev_data_2026-05-27_200505.json
data\raw\kev_data_2026-05-28_094533.json
data\raw\kev_data_2026-05-28_115921.json
data\raw\kev_data_2026-05-29_220446.json
data\raw\kev_data_2026-05-29_220730.json
data\raw\kev_data_2026-05-30_132237.json
data\raw\kev_data_2026-05-30_134247.json
data\raw\kev_data_2026-05-30_181720.json
data\raw\kev_data_2026-05-30_184435.json
data\raw\kev_data_2026-05-31_210413.json
data\raw\kev_data_2026-06-02_112656.json
data\raw\latest_api_data.json
data\raw\latest_kev_data.json

## Current Scripts

| Script | Purpose | Status |
|---|---|---|
| fetch_api_data.py | Fetches API data | Existing / Review needed |
| load_data.py | Loads or processes data | Existing / Review needed |
| transform_data.py | Transforms data | Existing / Review needed |

## Current Data Files

| File | Purpose | Notes |
|---|---|---|
| data/run_manifest.csv | Tracks pipeline runs | Early audit-trail artifact |

## Current Portfolio Value

This repo already demonstrates basic automation, data ingestion, transformation, Git usage, and early run tracking.

## Gaps to Address

- Cleaner folder structure
- Stronger README
- Better run manifest
- Error handling
- Data validation
- Cloud storage integration
- Security controls
- Evidence automation
- Provenance tracking