import json
import logging
from pathlib import Path
import sys

print("UPLOAD SCRIPT PYTHON:")
print(sys.executable)

import boto3
from botocore.exceptions import BotoCoreError
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError


def load_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def validate_upload_config(config):
    required_keys = [
        "s3_bucket_name",
        "s3_upload_files",
        "log_file"
    ]

    missing_keys = [
        key for key in required_keys
        if key not in config
    ]

    if missing_keys:
        raise KeyError(f"Missing required config keys: {missing_keys}")

    if not config["s3_bucket_name"]:
        raise ValueError("s3_bucket_name is empty.")

    if not isinstance(config["s3_upload_files"], list):
        raise TypeError("s3_upload_files must be a list.")

    if not config["s3_upload_files"]:
        raise ValueError("s3_upload_files is empty.")


def upload_file_to_s3(s3_client, bucket_name, local_path, s3_key):
    local_file = Path(local_path)

    if not local_file.exists():
        raise FileNotFoundError(f"Local file not found: {local_file}")

    if not local_file.is_file():
        raise ValueError(f"Local path is not a file: {local_file}")

    s3_client.upload_file(
        Filename=str(local_file),
        Bucket=bucket_name,
        Key=s3_key
    )


def main():
    config = load_config()

    log_file = config["log_file"]
    setup_logging(log_file)

    logging.info("Starting S3 upload process.")

    try:
        validate_upload_config(config)

        bucket_name = config["s3_bucket_name"]
        upload_files = config["s3_upload_files"]

        s3_client = boto3.client("s3")

        successful_uploads = 0

        for upload_item in upload_files:
            local_path = upload_item["local_path"]
            s3_key = upload_item["s3_key"]

            logging.info("Uploading %s to s3://%s/%s", local_path, bucket_name, s3_key)

            upload_file_to_s3(
                s3_client=s3_client,
                bucket_name=bucket_name,
                local_path=local_path,
                s3_key=s3_key
            )

            successful_uploads += 1

            print(f"Uploaded: {local_path} -> s3://{bucket_name}/{s3_key}")

        logging.info("S3 upload process completed successfully.")
        logging.info("Files uploaded: %s", successful_uploads)

        print("S3 upload process completed successfully.")
        print(f"Files uploaded: {successful_uploads}")

    except NoCredentialsError as error:
        logging.error("AWS credentials were not found: %s", error)
        print(f"AWS credentials were not found: {error}")
        raise

    except ClientError as error:
        logging.error("AWS client error during S3 upload: %s", error)
        print(f"AWS client error during S3 upload: {error}")
        raise

    except BotoCoreError as error:
        logging.error("Boto3 core error during S3 upload: %s", error)
        print(f"Boto3 core error during S3 upload: {error}")
        raise

    except Exception as error:
        logging.error("Unexpected error during S3 upload: %s", error)
        print(f"Unexpected error during S3 upload: {error}")
        raise


if __name__ == "__main__":
    main()