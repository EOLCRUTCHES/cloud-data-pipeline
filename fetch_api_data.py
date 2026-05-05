import json
import requests

def main():
    url = "https://api.github.com/repos/python/cpython"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    with open("api_data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print("API data fetched successfully.")
    print(f"Repository: {data.get('full_name')}")
    print(f"Stars: {data.get('stargazers_count')}")
    print(f"Forks: {data.get('forks_count')}")
    print(f"Open issues: {data.get('open_issues_count')}")


if __name__ == "__main__":
    main()