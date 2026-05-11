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
