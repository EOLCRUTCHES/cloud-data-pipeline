import csv
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def load_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def run_step(step_name, command):
    logging.info("Starting step: %s", step_name)
    print(f"Starting step: {step_name}")

    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True
    )

    logging.info("Step completed successfully: %s", step_name)

    if result.stdout:
        logging.info("Output from %s: %s", step_name, result.stdout)
        print(result.stdout)

    if result.stderr:
        logging.warning("Warnings from %s: %s", step_name, result.stderr)
        print(result.stderr)


def find_latest_file(folder, pattern):
    files = list(Path(folder).glob(pattern))

    if not files:
        return ""

    latest_file = max(files, key=lambda file_path: file_path.stat().st_mtime)
    return str(latest_file)


def append_run_manifest(
    manifest_file,
    run_timestamp,
    raw_file,
    processed_file,
    status,
    error_message,
    upload_status
):
    manifest_path = Path(manifest_file)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = manifest_path.exists()

    with open(manifest_path, "a", newline="", encoding="utf-8") as file:
        fieldnames = [
            "run_timestamp",
            "raw_file",
            "processed_file",
            "status",
            "upload_status",
            "error_message"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                "run_timestamp": run_timestamp,
                "raw_file": raw_file,
                "processed_file": processed_file,
                "status": status,
                "upload_status": upload_status,
                "error_message": error_message
            }
        )


def main():
    config = load_config()

    log_file = config["log_file"]
    raw_data_folder = config["raw_data_folder"]
    processed_data_folder = config["processed_data_folder"]
    raw_data_prefix = config["raw_data_prefix"]
    kev_raw_data_prefix = config["kev_raw_data_prefix"]
    summary_output_prefix = config["summary_output_prefix"]
    kev_summary_output_prefix = config["kev_summary_output_prefix"]
    manifest_file = config["manifest_file"]

    setup_logging(log_file)

    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    status = "success"
    upload_status = "not_attempted"
    error_message = ""

    logging.info("Multi-source cloud pipeline run started.")
    print("Multi-source cloud pipeline run started.")

    try:
        run_step("Fetch GitHub API data", [sys.executable, "fetch_api_data.py"])
        run_step("Transform GitHub API data", [sys.executable, "transform_api_data.py"])
        run_step("Validate GitHub processed output", [sys.executable, "validate_output.py"])

        run_step("Fetch CISA KEV data", [sys.executable, "fetch_kev_data.py"])
        run_step("Transform CISA KEV data", [sys.executable, "transform_kev_data.py"])
        run_step("Validate CISA KEV output", [sys.executable, "validate_kev_output.py"])
        run_step("Enrich CISA KEV data", [sys.executable, "enrich_kev_data.py"])
        run_step("Create executive summary", [sys.executable, "create_executive_summary.py"])

        run_step("Upload outputs to S3", [sys.executable, "upload_to_s3.py"])
        upload_status = "success"

    except subprocess.CalledProcessError as error:
        status = "failed"
        error_message = error.stderr or str(error)

        if error.cmd and "upload_to_s3.py" in error.cmd:
            upload_status = "failed"

        logging.error("Pipeline failed.")
        logging.error("Failed command: %s", error.cmd)
        logging.error("Return code: %s", error.returncode)
        logging.error("Error output: %s", error.stderr)

        print("Pipeline failed.")
        print(f"Failed command: {error.cmd}")
        print(error_message)

    github_raw_file = find_latest_file(
        raw_data_folder,
        f"{raw_data_prefix}_*.json"
    )

    github_processed_file = find_latest_file(
        processed_data_folder,
        f"{summary_output_prefix}_*.csv"
    )

    kev_raw_file = find_latest_file(
        raw_data_folder,
        f"{kev_raw_data_prefix}_*.json"
    )

    kev_processed_file = find_latest_file(
        processed_data_folder,
        f"{kev_summary_output_prefix}_*.csv"
    )

    combined_raw_files = f"github={github_raw_file}; kev={kev_raw_file}"
    combined_processed_files = f"github={github_processed_file}; kev={kev_processed_file}"

    append_run_manifest(
        manifest_file=manifest_file,
        run_timestamp=run_timestamp,
        raw_file=combined_raw_files,
        processed_file=combined_processed_files,
        status=status,
        error_message=error_message,
        upload_status=upload_status
    )

    if status == "success":
        logging.info("Multi-source cloud pipeline run completed successfully.")
        print("Multi-source cloud pipeline run completed successfully.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
