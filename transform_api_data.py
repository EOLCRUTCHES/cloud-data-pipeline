import json
import logging
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

    input_file = config["raw_data_file"]
    output_file = config["summary_output_file"]
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
        dataframe.to_csv(output_file, index=False)

        logging.info("Transformation completed successfully.")
        logging.info("Saved structured output to %s.", output_file)

        print("Transformation complete.")
        print(f"Saved clean output to {output_file}")
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