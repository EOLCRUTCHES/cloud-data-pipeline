import json
import logging
import requests


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

    url = config["api_url"]
    output_file = config["raw_data_file"]
    log_file = config["log_file"]

    setup_logging(log_file)

    logging.info("Starting API data fetch.")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

        logging.info("API data fetched successfully.")
        logging.info("Saved raw API response to %s.", output_file)

        print("API data fetched successfully.")
        print(f"Repository: {data.get('full_name')}")
        print(f"Stars: {data.get('stargazers_count')}")
        print(f"Forks: {data.get('forks_count')}")
        print(f"Open issues: {data.get('open_issues_count')}")

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
