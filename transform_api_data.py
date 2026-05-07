import json
import pandas as pd


def main():
    input_file = "api_data.json"
    output_file = "repo_summary.csv"

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

    print("Transformation complete.")
    print(f"Saved clean output to {output_file}")
    print()
    print(dataframe)


if __name__ == "__main__":
    main()