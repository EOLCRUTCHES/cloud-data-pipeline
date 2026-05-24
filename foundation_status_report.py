import json
from pathlib import Path

import pandas as pd


def load_config():
    config_path = Path("config.json")

    if not config_path.exists():
        raise FileNotFoundError("config.json was not found in the project root.")

    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def check_path(path_value):
    path = Path(path_value)

    return {
        "path": str(path),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir()
    }


def count_files(folder_value, pattern):
    folder = Path(folder_value)

    if not folder.exists():
        return 0

    return len(list(folder.glob(pattern)))


def read_manifest_summary(manifest_file):
    manifest_path = Path(manifest_file)

    if not manifest_path.exists():
        return {
            "exists": False,
            "rows": 0,
            "latest_status": "not available"
        }

    dataframe = pd.read_csv(manifest_path)

    if dataframe.empty:
        return {
            "exists": True,
            "rows": 0,
            "latest_status": "empty"
        }

    latest_status = dataframe.iloc[-1].get("status", "unknown")

    return {
        "exists": True,
        "rows": len(dataframe),
        "latest_status": latest_status
    }


def write_status_report(report_lines, output_file):
    output_path = Path(output_file)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(report_lines))
        file.write("\n")


def main():
    config = load_config()

    raw_data_folder = config["raw_data_folder"]
    processed_data_folder = config["processed_data_folder"]
    latest_raw_data_file = config["latest_raw_data_file"]
    latest_summary_output_file = config["latest_summary_output_file"]
    log_file = config["log_file"]
    manifest_file = config.get("manifest_file", "data/run_manifest.csv")

    raw_file_count = count_files(raw_data_folder, "*.json")
    processed_file_count = count_files(processed_data_folder, "*.csv")
    manifest_summary = read_manifest_summary(manifest_file)

    checks = [
        check_path(raw_data_folder),
        check_path(processed_data_folder),
        check_path(latest_raw_data_file),
        check_path(latest_summary_output_file),
        check_path(log_file),
        check_path(manifest_file)
    ]

    report_lines = [
        "# Foundation Status Report",
        "",
        "## Pipeline File Checks",
        ""
    ]

    for item in checks:
        status = "OK" if item["exists"] else "MISSING"
        report_lines.append(f"- {status}: `{item['path']}`")

    report_lines.extend(
        [
            "",
            "## Data Output Summary",
            "",
            f"- Raw JSON files found: {raw_file_count}",
            f"- Processed CSV files found: {processed_file_count}",
            "",
            "## Run Manifest Summary",
            "",
            f"- Manifest exists: {manifest_summary['exists']}",
            f"- Manifest rows: {manifest_summary['rows']}",
            f"- Latest run status: {manifest_summary['latest_status']}",
            "",
            "## Foundation Assessment",
            ""
        ]
    )

    missing_items = [item["path"] for item in checks if not item["exists"]]

    if missing_items:
        report_lines.append("Foundation status: Needs attention.")
        report_lines.append("")
        report_lines.append("Missing items:")
        for item in missing_items:
            report_lines.append(f"- `{item}`")
    else:
        report_lines.append("Foundation status: Complete.")

    output_file = "foundation_status_report.md"
    write_status_report(report_lines, output_file)

    print("Foundation status report created.")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    main()
