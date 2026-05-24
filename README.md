# Cloud Data Pipeline

This project is a hands-on learning pipeline for cloud, data engineering, and security-oriented technical leadership.

## Day 2

Created a local Python environment, loaded sample CSV data with pandas, and pushed the project to GitHub.

## Day 3

Added an API data pull using Python requests. The script fetches public GitHub repository data and saves the response as JSON.

## Day 4

Added a transformation step that reads the raw API JSON response, extracts selected repository metadata, and saves the cleaned output as a CSV file.

This moves the project from raw data collection toward a basic ETL workflow:

- Extract: fetch public API data
- Transform: select and structure useful fields
- Load: save cleaned output as CSV

## Day 5

Added logging and basic error handling to the API fetch and transformation scripts.

The pipeline now writes operational events to `pipeline.log` and handles common failure scenarios, including:

- API request failures
- Missing input files
- JSON decoding errors
- Unexpected runtime errors

This moves the project from simple scripting toward more reliable pipeline behavior.

## Day 6

Added a pipeline runner script.

The project can now run the full workflow with one command:

```powershell
python run_pipeline.py
The runner executes the pipeline in order:

1. Fetch API data from the GitHub API
2. Save the raw API response to `api_data.json`
3. Transform selected fields into structured CSV output
4. Save the cleaned output to `repo_summary.csv`
5. Log pipeline activity to `pipeline.log`

This moves the project from separate scripts toward a repeatable data pipeline workflow.
## Day 9

Added timestamped output files.

The pipeline now saves both timestamped outputs and latest-output convenience files.

Raw API output is saved as:

- `data/raw/api_data_YYYY-MM-DD_HHMMSS.json`
- `data/raw/latest_api_data.json`

Processed CSV output is saved as:

- `data/processed/repo_summary_YYYY-MM-DD_HHMMSS.csv`
- `data/processed/latest_repo_summary.csv`

This improves basic data lineage by preserving each pipeline run instead of only overwriting the same files.

## Day 7

Added a configuration file.

The pipeline now reads key settings from `config.json`, including:

- API URL
- Raw data output file
- Summary CSV output file
- Log file name

This reduces hardcoding inside the Python scripts and makes the pipeline easier to modify without changing code.

The current workflow is:

1. `run_pipeline.py` starts the pipeline
2. `fetch_api_data.py` reads the API URL and raw output filename from `config.json`
3. `fetch_api_data.py` saves the raw API response to `api_data.json`
4. `transform_api_data.py` reads input and output filenames from `config.json`
5. `transform_api_data.py` saves structured output to `repo_summary.csv`
6. Pipeline events are written to `pipeline.log`

## Day 8

Added a data folder structure.

The pipeline now separates raw and processed data:

- Raw API responses are saved in `data/raw/`
- Cleaned CSV outputs are saved in `data/processed/`

The current configured output paths are managed through `config.json`:

- Raw data file: `data/raw/api_data.json`
- Processed summary file: `data/processed/repo_summary.csv`

This makes the project structure cleaner and closer to a real data pipeline.

## Day 9

Added timestamped output files.

The pipeline now saves both timestamped outputs and latest-output convenience files.

Raw API output is saved as:

- `data/raw/api_data_YYYY-MM-DD_HHMMSS.json`
- `data/raw/latest_api_data.json`

Processed CSV output is saved as:

- `data/processed/repo_summary_YYYY-MM-DD_HHMMSS.csv`
- `data/processed/latest_repo_summary.csv`

This improves basic data lineage by preserving each pipeline run instead of only overwriting the same files.

## Day 10

Added a run manifest.

The pipeline now appends a run record to `data/run_manifest.csv` after each execution.

The manifest tracks:

- Run timestamp
- Timestamped raw data file
- Timestamped processed output file
- Run status
- Error message, if applicable

This improves basic auditability and makes pipeline runs easier to trace.

## Day 11

Added basic data validation.

The pipeline now runs `validate_output.py` after the transformation step.

The validation checks that:

- The processed CSV exists
- The processed CSV is not empty
- Required columns are present
- The repository field is not null

This adds a basic quality gate before treating pipeline output as usable.