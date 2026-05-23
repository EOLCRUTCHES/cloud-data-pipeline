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
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def run_step(step_name, command):
    logging.info("Starting step: %s", step_name)
    print(f"Starting step: {step_name}")

    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )

    logging.info("Step completed successfully: %s", step_name)

    if result.stdout:
        logging.info("Output from %s: %s", step_name, result.stdout)
        print(result.stdout)


def find_latest_file(folder, pattern):
    files = list(Path(folder).glob(pattern))

    if not files:
        return ""

    latest_file = max(files, key=lambda file_path: file_path.stat().st_mtime)
    return str(latest_file)


def append_run_manifest(manifest_file, run_timestamp, raw_file, processed_file, status, error_message):
    manifest_path = Path(manifest_file)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = manifest_path.exists()

    with open(manifest_path, "a", newline="", encoding="utf-8") as file:
        fieldnames = [
            "run_timestamp",
            "raw_file",
            "processed_file",
            "status",
            "error_message",
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
                "error_message": error_message,
            }
        )


def main():
    config = load_config()

    log_file = config["log_file"]
    raw_data_folder = config["raw_data_folder"]
    processed_data_folder = config["processed_data_folder"]
    raw_data_prefix = config["raw_data_prefix"]
    summary_output_prefix = config["summary_output_prefix"]
    manifest_file = config["manifest_file"]

    setup_logging(log_file)

    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    status = "success"
    error_message = ""

    logging.info("Pipeline run started.")
    print("Pipeline run started.")

    try:
        run_step("Fetch API data", ["python", "fetch_api_data.py"])
        run_step("Transform API data", ["python", "transform_api_data.py"])
    except subprocess.CalledProcessError as error:
        status = "failed"
        error_message = error.stderr or str(error)

        logging.error("Pipeline failed.")
        logging.error("Return code: %s", error.returncode)
        logging.error("Error output: %s", error.stderr)

        print("Pipeline failed.")
        print(error.stderr)

    raw_file = find_latest_file(
        raw_data_folder,
        f"{raw_data_prefix}_*.json",
    )

    processed_file = find_latest_file(
        processed_data_folder,
        f"{summary_output_prefix}_*.csv",
    )

    append_run_manifest(
        manifest_file,
        run_timestamp,
        raw_file,
        processed_file,
        status,
        error_message,
    )

    if status == "success":
        logging.info("Pipeline run completed successfully.")
        print("Pipeline run completed successfully.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()