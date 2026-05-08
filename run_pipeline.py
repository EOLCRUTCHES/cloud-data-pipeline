import logging
import subprocess
import sys


logging.basicConfig(
filename="pipeline.log",
level=logging.INFO,
format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_step(step_name, command):
    logging.info("Starting step: %s", step_name)
    print(f"Starting step: {step_name}")

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )

        logging.info("Step completed successfully: %s", step_name)

        if result.stdout:
            logging.info("Output from %s: %s", step_name, result.stdout)
            print(result.stdout)

    except subprocess.CalledProcessError as error:
        logging.error("Step failed: %s", step_name)
        logging.error("Return code: %s", error.returncode)
        logging.error("Error output: %s", error.stderr)

        print(f"Step failed: {step_name}")
        print(error.stderr)

        sys.exit(error.returncode)


def main():
    logging.info("Pipeline run started.")
    print("Pipeline run started.")

    run_step("Fetch API data", ["python", "fetch_api_data.py"])
    run_step("Transform API data", ["python", "transform_api_data.py"])

    logging.info("Pipeline run completed successfully.")
    print("Pipeline run completed successfully.")


if __name__ == "__main__":
    main()