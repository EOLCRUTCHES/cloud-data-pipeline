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


def count_due_soon(dataframe, days):
    if "days_until_due" not in dataframe.columns:
        return 0

    due_values = pd.to_numeric(dataframe["days_until_due"], errors="coerce")

    return int(((due_values >= 0) & (due_values <= days)).sum())


def create_summary_rows(dataframe):
    total_vulnerabilities = len(dataframe)

    priority_counts = dataframe["priority_bucket"].value_counts().to_dict()

    overdue_count = int(dataframe["is_overdue"].fillna(False).sum())
    due_soon_30_count = count_due_soon(dataframe, 30)

    ransomware_known_count = int(
        dataframe["known_ransomware_campaign_use"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("known")
        .sum()
    )

    top_vendor_counts = (
        dataframe["vendor_project"]
        .fillna("Unknown")
        .value_counts()
        .head(10)
        .to_dict()
    )

    rows = [
        {
            "metric": "total_vulnerabilities",
            "value": total_vulnerabilities,
            "category": "overall"
        },
        {
            "metric": "overdue_vulnerabilities",
            "value": overdue_count,
            "category": "timeliness"
        },
        {
            "metric": "due_within_30_days",
            "value": due_soon_30_count,
            "category": "timeliness"
        },
        {
            "metric": "known_ransomware_campaign_use",
            "value": ransomware_known_count,
            "category": "threat_context"
        }
    ]

    for priority, count in priority_counts.items():
        rows.append(
            {
                "metric": f"priority_{priority.lower()}",
                "value": int(count),
                "category": "priority_bucket"
            }
        )

    for vendor, count in top_vendor_counts.items():
        rows.append(
            {
                "metric": f"top_vendor_{vendor}",
                "value": int(count),
                "category": "vendor_project"
            }
        )

    return rows


def main():
    config = load_config()

    input_file = Path(config["latest_kev_enriched_output_file"])
    processed_data_folder = config["processed_data_folder"]
    executive_summary_prefix = config["executive_summary_output_prefix"]
    latest_executive_summary_file = Path(config["latest_executive_summary_output_file"])
    log_file = config["log_file"]

    setup_logging(log_file)

    logging.info("Starting executive summary generation.")

    try:
        if not input_file.exists():
            raise FileNotFoundError(f"Missing enriched KEV file: {input_file}")

        dataframe = pd.read_csv(input_file)

        if dataframe.empty:
            raise ValueError("Enriched KEV file is empty.")

        required_columns = [
            "vendor_project",
            "known_ransomware_campaign_use",
            "is_overdue",
            "days_until_due",
            "priority_bucket"
        ]

        missing_columns = [
            column for column in required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        summary_rows = create_summary_rows(dataframe)
        summary_dataframe = pd.DataFrame(summary_rows)

        timestamped_file = build_timestamped_file_path(
            processed_data_folder,
            executive_summary_prefix,
            "csv"
        )

        timestamped_file.parent.mkdir(parents=True, exist_ok=True)
        latest_executive_summary_file.parent.mkdir(parents=True, exist_ok=True)

        summary_dataframe.to_csv(timestamped_file, index=False)
        summary_dataframe.to_csv(latest_executive_summary_file, index=False)

        logging.info("Executive summary generated successfully.")
        logging.info("Saved timestamped executive summary to %s.", timestamped_file)
        logging.info("Saved latest executive summary to %s.", latest_executive_summary_file)

        print("Executive summary generated.")
        print(f"Summary rows: {len(summary_dataframe)}")
        print(f"Timestamped executive summary: {timestamped_file}")
        print(f"Latest executive summary: {latest_executive_summary_file}")

    except Exception as error:
        logging.error("Executive summary generation failed: %s", error)
        print(f"Executive summary generation failed: {error}")
        raise


if __name__ == "__main__":
    main()