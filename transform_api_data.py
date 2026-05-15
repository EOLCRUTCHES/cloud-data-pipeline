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
                format="%(asctime)s - %(levelname)s - %(message)s",
        )


def build_timestamped_file_path(folder, prefix, extension):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        file_name = f"{prefix}_{timestamp}.{extension}"
        return Path(folder) / file_name


def main():
        config = load_config()

        input_file = Path(config["latest_raw_data_file"])
        processed_data_folder = config["processed_data_folder"]
        summary_output_prefix = config["summary_output_prefix"]
        latest_summary_output_file = Path(config["latest_summary_output_file"])
        log_file = config["log_file"]

        setup_logging(log_file)

        logging.info("Starting API data transformation.")

        try:
                with open(input_file, "r", encoding="utf-8") as file:
                        data = json.load(file)

                repo_summary = {
                        "repository": data.get("full_name"),
                        "description": data.get("description"),
                        "language": data.get("language"),
                        "stars": data.get("stargazers_count"),
                        "forks": data.get("forks_count"),
                        "open_issues": data.get("open_issues_count"),
                        "watchers": data.get("watchers_count"),
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at"),
                        "pushed_at": data.get("pushed_at"),
                        "default_branch": data.get("default_branch"),
                        "visibility": data.get("visibility"),
                }

                dataframe = pd.DataFrame([repo_summary])

                timestamped_file = build_timestamped_file_path(
                        processed_data_folder, summary_output_prefix, "csv"
                )

                timestamped_file.parent.mkdir(parents=True, exist_ok=True)
                latest_summary_output_file.parent.mkdir(parents=True, exist_ok=True)

                dataframe.to_csv(timestamped_file, index=False)
                dataframe.to_csv(latest_summary_output_file, index=False)

                logging.info("Transformation completed successfully.")
                logging.info("Saved timestamped structured output to %s.", timestamped_file)
                logging.info("Saved latest structured output to %s.", latest_summary_output_file)

                print("Transformation complete.")
                print(f"Saved timestamped output to {timestamped_file}")
                print(f"Saved latest output to {latest_summary_output_file}")
                print()
                print(dataframe)

        except FileNotFoundError as error:
                logging.error("Required input file not found: %s", error)
                print(f"Required input file not found: {error}")

        except json.JSONDecodeError as error:
                logging.error("Failed to decode JSON input file: %s", error)
                print(f"Failed to decode JSON input file: {error}")

        except Exception as error:
                logging.error("Unexpected error during transformation: %s", error)
                print(f"Unexpected error during transformation: {error}")


if __name__ == "__main__":
    main()