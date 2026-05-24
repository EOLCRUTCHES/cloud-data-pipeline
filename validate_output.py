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

    input_file = Path(config["latest_summary_output_file"])
    log_file = config["log_file"]

    setup_logging(log_file)

    required_columns = [
        "repository",
        "description",
        "language",
        "stars",
        "forks",
        "open_issues",
        "watchers",
        "created_at",
        "updated_at",
        "pushed_at",
        "default_branch",
        "visibility"
    ]

    logging.info("Starting output validation.")

    try:
        if not input_file.exists():
            raise FileNotFoundError(f"Missing processed output file: {input_file}")

        dataframe = pd.read_csv(input_file)

        if dataframe.empty:
            raise ValueError("Processed output file is empty.")

        missing_columns = [
            column for column in required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        if dataframe["repository"].isnull().any():
            raise ValueError("Repository field contains null values.")

        logging.info("Output validation completed successfully.")

        print("Validation complete.")
        print(f"Validated file: {input_file}")
        print(f"Rows: {len(dataframe)}")
        print(f"Columns: {len(dataframe.columns)}")

    except Exception as error:
        logging.error("Output validation failed: %s", error)
        print(f"Output validation failed: {error}")
        raise


if __name__ == "__main__":
    main()