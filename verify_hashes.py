import csv
import hashlib
from pathlib import Path


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
    hash_file = Path("data/integrity/file_hashes.csv")

    if not hash_file.exists():
        raise FileNotFoundError(f"Hash manifest not found: {hash_file}")

    total_checked = 0
    total_passed = 0
    total_failed = 0
    total_missing = 0

    with open(hash_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required_columns = [
            "file_path",
            "sha256_hash"
        ]

        missing_columns = [
            column for column in required_columns
            if column not in reader.fieldnames
        ]

        if missing_columns:
            raise ValueError(f"Hash manifest missing columns: {missing_columns}")

        for row in reader:
            total_checked += 1

            file_path = row["file_path"]
            expected_hash = row["sha256_hash"]

            path = Path(file_path)

            if not path.exists():
                total_missing += 1
                print(f"MISSING: {file_path}")
                continue

            actual_hash = calculate_sha256(path)

            if actual_hash == expected_hash:
                total_passed += 1
                print(f"PASS: {file_path}")
            else:
                total_failed += 1
                print(f"FAIL: {file_path}")

    print()
    print("Integrity verification summary:")
    print(f"Checked: {total_checked}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Missing: {total_missing}")

    if total_failed > 0 or total_missing > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()