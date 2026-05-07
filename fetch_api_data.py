import json
import logging
import requests


logging.basicConfig(
filename="pipeline.log",
level=logging.INFO,
format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    url = "https://api.github.com/repos/python/cpython"
    output_file = "api_data.json"

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