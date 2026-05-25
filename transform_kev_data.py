import json
import logging
from datetime import datetime
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


def build_timestamped_file_path(folder, prefix, extension):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    file_name = f"{prefix}_{timestamp}.{extension}"
    return Path(folder) / file_name


def main():
    config = load_config()

    input_file = Path(config["latest_kev_raw_data_file"])
    processed_data_folder = config["processed_data_folder"]
    kev_summary_prefix = config["kev_summary_output_prefix"]
    latest_kev_summary_file = Path(config["latest_kev_summary_output_file"])
    log_file = config["log_file"]

    setup_logging(log_file)

    logging.info("Starting CISA KEV data transformation.")

    try:
        if not input_file.exists():
            raise FileNotFoundError(f"Missing KEV raw data file: {input_file}")

        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        vulnerabilities = data.get("vulnerabilities", [])

        if not vulnerabilities:
            raise ValueError("No vulnerabilities found in KEV raw data.")

        rows = []

        for vulnerability in vulnerabilities:
            row = {
                "cve_id": vulnerability.get("cveID"),
                "vendor_project": vulnerability.get("vendorProject"),
                "product": vulnerability.get("product"),
                "vulnerability_name": vulnerability.get("vulnerabilityName"),
                "date_added": vulnerability.get("dateAdded"),
                "short_description": vulnerability.get("shortDescription"),
                "required_action": vulnerability.get("requiredAction"),
                "due_date": vulnerability.get("dueDate"),
                "known_ransomware_campaign_use": vulnerability.get("knownRansomwareCampaignUse"),
                "notes": vulnerability.get("notes")
            }
            rows.append(row)

        dataframe = pd.DataFrame(rows)

        timestamped_file = build_timestamped_file_path(
            processed_data_folder,
            kev_summary_prefix,
            "csv"
        )

        timestamped_file.parent.mkdir(parents=True, exist_ok=True)
        latest_kev_summary_file.parent.mkdir(parents=True, exist_ok=True)

        dataframe.to_csv(timestamped_file, index=False)
        dataframe.to_csv(latest_kev_summary_file, index=False)

        logging.info("CISA KEV transformation completed successfully.")
        logging.info("Saved timestamped KEV summary to %s.", timestamped_file)
        logging.info("Saved latest KEV summary to %s.", latest_kev_summary_file)
        logging.info("KEV rows transformed: %s", len(dataframe))

        print("CISA KEV transformation complete.")
        print(f"Rows transformed: {len(dataframe)}")
        print(f"Timestamped KEV summary: {timestamped_file}")
        print(f"Latest KEV summary: {latest_kev_summary_file}")

    except FileNotFoundError as error:
        logging.error("Required KEV input file not found: %s", error)
        print(f"Required KEV input file not found: {error}")
        raise

    except json.JSONDecodeError as error:
        logging.error("Failed to decode KEV JSON input file: %s", error)
        print(f"Failed to decode KEV JSON input file: {error}")
        raise

    except Exception as error:
        logging.error("Unexpected error during KEV transformation: %s", error)
        print(f"Unexpected error during KEV transformation: {error}")
        raise


if __name__ == "__main__":
    main()