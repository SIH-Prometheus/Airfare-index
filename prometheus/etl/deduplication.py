
import json
from pathlib import Path

import polars as pl


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "cleaned_data.json"
OUTPUT_FILE = BASE_DIR / "data" / "deduplicated_data.json"


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_data():
    """
    Load cleaned flight data from cleaned_data.json.
    """

    print("Looking for input file:")
    print(INPUT_FILE)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"\nInput file not found:\n{INPUT_FILE}"
        )

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "Input data must be a JSON list of flight records."
        )

    return data


# ---------------------------------------------------------
# REMOVE DUPLICATES
# ---------------------------------------------------------

def remove_duplicates(data):
    """
    Remove exact duplicate flight observations.

    scraped_at is NOT used as a duplicate key because
    we want to preserve different fare observations over time.
    """

    if not data:
        return [], 0

    df = pl.DataFrame(data)

    original_count = df.height

    # Columns that identify the same fare observation
    duplicate_columns = [
        "airline",
        "flight_number",
        "departure_time",
        "arrival_time",
        "origin",
        "destination",
        "duration",
        "stops",
        "price",
        "currency",
        "source_platform",
        "lead_time",
    ]

    # Keep the first occurrence of each duplicate
    df = df.unique(
        subset=duplicate_columns,
        keep="first",
        maintain_order=True
    )

    final_count = df.height

    duplicates_removed = original_count - final_count

    return df.to_dicts(), duplicates_removed


# ---------------------------------------------------------
# SAVE DATA
# ---------------------------------------------------------

def save_data(data):
    """
    Save deduplicated data to deduplicated_data.json.
    """

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("\n======================================")
    print("       DATA DEDUPLICATION")
    print("======================================")

    # Load cleaned data
    data = load_data()

    print(f"\nRecords before deduplication: {len(data)}")

    # Remove duplicates
    deduplicated_data, duplicates_removed = remove_duplicates(data)

    # Save result
    save_data(deduplicated_data)

    print(f"Records after deduplication : {len(deduplicated_data)}")
    print(f"Duplicates removed          : {duplicates_removed}")

    print("\n--------------------------------------")
    print("Deduplicated data saved at:")
    print(OUTPUT_FILE)
    print("--------------------------------------")

    if duplicates_removed == 0:
        print("\nNo duplicate records found. ✅")
    else:
        print(
            f"\nSuccessfully removed "
            f"{duplicates_removed} duplicate record(s). ✅"
        )


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    main()

