import json
import logging
from datetime import datetime
from pathlib import Path

import requests


def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def build_timestamped_file_path(folder,prefix,extension):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    file_name = f"{prefix}_{timestamp}.{extension}"
    return Path(folder) / file_name


def save_json_file(data,file_path):
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def main():
    config = load_config()

    url = config["api_url"]
    raw_data_folder = config["raw_data_folder"]
    raw_data_prefix = config["raw_data_prefix"]
    latest_raw_data_file = Path(config["latest_raw_data_file"])
    log_file = config["log_file"]

    setup_logging(log_file)

    logging.info("Starting API data fetch.")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        timestamped_file = build_timestamped_file_path(
            raw_data_folder, raw_data_prefix, "json"
        )

        save_json_file(data, timestamped_file)
        save_json_file(data, latest_raw_data_file)

        logging.info("API data fetched successfully.")
        logging.info("Saved timestamped raw API response to %s.", timestamped_file)
        logging.info("Saved latest raw API response to %s.", latest_raw_data_file)

        print("API data fetched successfully.")
        print(f"Repository: {data.get('full_name')}")
        print(f"Stars: {data.get('stargazers_count')}")
        print(f"Forks: {data.get('forks_count')}")
        print(f"Open issues: {data.get('open_issues_count')}")
        print(f"Timestamped raw file: {timestamped_file}")
        print(f"Latest raw file: {latest_raw_data_file}")

    except requests.exceptions.RequestException as error:
        logging.error("API request failed: %s", error)
        print(f"API request failed: {error}")

    except json.JSONDecodeError as error:
        logging.error("Failed to decode JSON response: %s", error)
        print(f"Failed to decode JSON response: {error}")

    except Exception as error:
        logging.error("Unexpected error during API fetch: %s", error)
        print(f"Unexpected error during API fetch: {error}")


if __name__ == "__main__":
    main()