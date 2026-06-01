import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


FILES_TO_HASH = [
    "data/raw/latest_api_data.json",
    "data/raw/latest_kev_data.json",
    "data/processed/latest_repo_summary.csv",
    "data/processed/latest_kev_summary.csv",
    "data/processed/latest_kev_enriched.csv",
    "data/processed/latest_executive_summary.csv",
    "data/run_manifest.csv",
    "pipeline.log"
]


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(4096)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def main():
    output_file = Path("data/integrity/file_hashes.csv")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).isoformat()

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        fieldnames = [
            "generated_at_utc",
            "file_path",
            "file_size_bytes",
            "sha256_hash"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for file_path in FILES_TO_HASH:
            path = Path(file_path)

            if not path.exists():
                print(f"Skipping missing file: {file_path}")
                continue

            file_hash = calculate_sha256(path)
            file_size = path.stat().st_size

            writer.writerow(
                {
                    "generated_at_utc": generated_at,
                    "file_path": file_path,
                    "file_size_bytes": file_size,
                    "sha256_hash": file_hash
                }
            )

            print(f"Hashed: {file_path}")

    print()
    print("Hash generation complete.")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()