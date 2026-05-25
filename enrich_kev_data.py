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


def calculate_days_until_due(due_date_value):
    if pd.isna(due_date_value) or not due_date_value:
        return None

    due_date = pd.to_datetime(due_date_value, errors="coerce")

    if pd.isna(due_date):
        return None

    today = pd.Timestamp.today().normalize()
    due_date = due_date.normalize()

    return int((due_date - today).days)


def assign_priority_bucket(row):
    days_until_due = row["days_until_due"]
    ransomware_use = str(row["known_ransomware_campaign_use"]).strip().lower()

    if pd.isna(days_until_due):
        return "Review"

    if days_until_due < 0 and ransomware_use == "known":
        return "Critical"

    if days_until_due < 0:
        return "High"

    if days_until_due <= 30 and ransomware_use == "known":
        return "High"

    if days_until_due <= 30:
        return "Medium"

    return "Monitor"


def main():
    config = load_config()

    input_file = Path(config["latest_kev_summary_output_file"])
    processed_data_folder = config["processed_data_folder"]
    enriched_output_prefix = config["kev_enriched_output_prefix"]
    latest_enriched_file = Path(config["latest_kev_enriched_output_file"])
    log_file = config["log_file"]

    setup_logging(log_file)

    logging.info("Starting CISA KEV enrichment.")

    try:
        if not input_file.exists():
            raise FileNotFoundError(f"Missing KEV summary file: {input_file}")

        dataframe = pd.read_csv(input_file)

        if dataframe.empty:
            raise ValueError("KEV summary file is empty.")

        dataframe["is_known_exploited"] = True

        dataframe["days_until_due"] = dataframe["due_date"].apply(
            calculate_days_until_due
        )

        dataframe["is_overdue"] = dataframe["days_until_due"].apply(
            lambda value: False if pd.isna(value) else value < 0
        )

        dataframe["priority_bucket"] = dataframe.apply(
            assign_priority_bucket,
            axis=1
        )

        timestamped_file = build_timestamped_file_path(
            processed_data_folder,
            enriched_output_prefix,
            "csv"
        )

        timestamped_file.parent.mkdir(parents=True, exist_ok=True)
        latest_enriched_file.parent.mkdir(parents=True, exist_ok=True)

        dataframe.to_csv(timestamped_file, index=False)
        dataframe.to_csv(latest_enriched_file, index=False)

        priority_counts = dataframe["priority_bucket"].value_counts().to_dict()

        logging.info("CISA KEV enrichment completed successfully.")
        logging.info("Saved timestamped enriched KEV output to %s.", timestamped_file)
        logging.info("Saved latest enriched KEV output to %s.", latest_enriched_file)
        logging.info("Priority bucket counts: %s", priority_counts)

        print("CISA KEV enrichment complete.")
        print(f"Rows enriched: {len(dataframe)}")
        print(f"Timestamped enriched output: {timestamped_file}")
        print(f"Latest enriched output: {latest_enriched_file}")
        print(f"Priority bucket counts: {priority_counts}")

    except Exception as error:
        logging.error("CISA KEV enrichment failed: %s", error)
        print(f"CISA KEV enrichment failed: {error}")
        raise


if __name__ == "__main__":
    main()