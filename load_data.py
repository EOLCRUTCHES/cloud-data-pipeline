import pandas as pd


def main():
    file_path = "sample.csv"

    data = pd.read_csv(file_path)

    print("Data loaded successfully.")
    print()
    print("Preview:")
    print(data.head())
    print()
    print("Summary:")
    print(data.describe(include="all"))


if __name__ == "__main__":
    main()