import json
import logging
from pathlib import Path

import pandas as pd


def load_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def main():
    config = load_config()

    input_file = Path(config["latest_kev_summary_output_file"])
    log_file = config["log_file"]

    setup_logging(log_file)

    required_columns = [
        "cve_id",
        "vendor_project",
        "product",
        "vulnerability_name",
        "date_added",
        "short_description",
        "required_action",
        "due_date",
        "known_ransomware_campaign_use",
        "notes"
    ]

    logging.info("Starting CISA KEV output validation.")

    try:
        if not input_file.exists():
            raise FileNotFoundError(f"Missing KEV processed output file: {input_file}")

        dataframe = pd.read_csv(input_file)

        if dataframe.empty:
            raise ValueError("KEV processed output file is empty.")

        missing_columns = [
            column for column in required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(f"Missing required KEV columns: {missing_columns}")

        if dataframe["cve_id"].isnull().any():
            raise ValueError("CVE ID field contains null values.")

        if dataframe["vendor_project"].isnull().any():
            raise ValueError("Vendor/project field contains null values.")

        if dataframe["date_added"].isnull().any():
            raise ValueError("Date added field contains null values.")

        duplicate_cves = dataframe["cve_id"].duplicated().sum()

        logging.info("CISA KEV validation completed successfully.")
        logging.info("KEV rows validated: %s", len(dataframe))
        logging.info("Duplicate CVE IDs found: %s", duplicate_cves)

        print("CISA KEV validation complete.")
        print(f"Validated file: {input_file}")
        print(f"Rows: {len(dataframe)}")
        print(f"Columns: {len(dataframe.columns)}")
        print(f"Duplicate CVE IDs: {duplicate_cves}")

    except Exception as error:
        logging.error("CISA KEV output validation failed: %s", error)
        print(f"CISA KEV output validation failed: {error}")
        raise


if __name__ == "__main__":
    main()