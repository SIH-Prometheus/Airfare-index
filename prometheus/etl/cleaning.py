import json
import re
from pathlib import Path

import polars as pl

pl.Config.set_ascii_tables(True)


# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent

INPUT_FILE = BASE_DIR / "data" / "raw_data.json"
OUTPUT_FILE = BASE_DIR / "data" / "cleaned_data.json"


# ============================================================
# LOAD RAW DATA
# ============================================================

def load_raw_data():
    input_path = INPUT_FILE
    if not input_path.exists():
        candidates = [
            REPO_ROOT / "data" / "raw_data.json",
            REPO_ROOT / "data" / "sample" / "DEL_BOM_sample.json",
            BASE_DIR / "data" / "sample" / "DEL_BOM_sample.json",
        ]
        for cand in candidates:
            if cand.exists():
                input_path = cand
                break
        else:
            raise FileNotFoundError(
                f"Raw data file not found:\n{INPUT_FILE}"
            )

    with open(input_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "Raw data must be a JSON list."
        )

    return data


# ============================================================
# REMOVE EMPTY RECORDS
# ============================================================

def remove_empty_records(data):

    cleaned_data = []

    for record in data:

        if not isinstance(record, dict):
            continue

        # Keep record if at least one value contains data
        if any(
            value is not None
            and str(value).strip() != ""
            for value in record.values()
        ):
            cleaned_data.append(record)

    return cleaned_data


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(value):

    if value is None:
        return None

    value = str(value).strip()

    # Replace multiple spaces with one space
    value = re.sub(r"\s+", " ", value)

    return value


# ============================================================
# CLEAN TEXT COLUMNS
# ============================================================

def clean_text_columns(df):

    text_columns = [
        "airline",
        "flight_number",
        "origin",
        "destination",
        "duration",
        "stops",
        "currency",
        "source_platform",
        "lead_time"
    ]

    existing_columns = [
        column
        for column in text_columns
        if column in df.columns
    ]

    if not existing_columns:
        return df

    return df.with_columns(
        [
            pl.col(column)
            .cast(pl.String)
            .map_elements(
                clean_text,
                return_dtype=pl.String
            )
            .alias(column)
            for column in existing_columns
        ]
    )


# ============================================================
# CLEAN AIRPORT CODES
# ============================================================

def clean_airport_codes(df):

    expressions = []

    if "origin" in df.columns:

        expressions.append(
            pl.col("origin")
            .str.to_uppercase()
            .alias("origin")
        )

    if "destination" in df.columns:

        expressions.append(
            pl.col("destination")
            .str.to_uppercase()
            .alias("destination")
        )

    if expressions:

        df = df.with_columns(expressions)

    return df


# ============================================================
# CLEAN FLIGHT NUMBER
# ============================================================

def clean_flight_numbers(df):

    if "flight_number" not in df.columns:
        return df

    return df.with_columns(

        pl.col("flight_number")
        .str.to_uppercase()
        .str.replace_all(r"\s+", "")
        .str.replace(r"ECONOMY$", "")
        .alias("flight_number")

    )


# ============================================================
# CLEAN TIME
# ============================================================

def clean_time_column(df, column_name):

    if column_name not in df.columns:
        return df

    return df.with_columns(

        pl.col(column_name)
        .cast(pl.String)
        .str.strip_chars()
        .str.extract(
            r"(\d{1,2}:\d{2})",
            group_index=1
        )
        .alias(column_name)

    )


# ============================================================
# CLEAN DURATION
# ============================================================

def clean_duration(df):

    if "duration" not in df.columns:
        return df

    return df.with_columns(

        pl.col("duration")
        .cast(pl.String)
        .str.strip_chars()
        .str.to_lowercase()
        .str.replace_all(r"\s+", " ")
        .alias("duration")

    )


# ============================================================
# CLEAN PRICE
# ============================================================

def clean_price(df):

    if "price" not in df.columns:
        return df

    return df.with_columns(

        pl.col("price")
        .cast(pl.String)
        .str.replace_all(r"[^\d.]", "")
        .cast(
            pl.Float64,
            strict=False
        )
        .alias("price")

    )


# ============================================================
# CLEAN STOPS
# ============================================================

def clean_stops(df):

    if "stops" not in df.columns:
        return df

    def normalize_stops(value):

        if value is None:
            return None

        value = str(value).strip().lower()

        mapping = {

            # Non-stop
            "0": "non-stop",
            "0 stop": "non-stop",
            "0 stops": "non-stop",
            "nonstop": "non-stop",
            "non-stop": "non-stop",
            "direct": "non-stop",

            # One stop
            "1": "1 stop",
            "1 stop": "1 stop",
            "1 stops": "1 stop",
            "1-stop": "1 stop",
            "1-stops": "1 stop",

            # Two stops
            "2": "2 stops",
            "2 stop": "2 stops",
            "2 stops": "2 stops",
            "2-stop": "2 stops",
            "2-stops": "2 stops",

            # Three stops
            "3": "3 stops",
            "3 stop": "3 stops",
            "3 stops": "3 stops",
            "3-stop": "3 stops",
            "3-stops": "3 stops",

            # Four stops
            "4": "4 stops",
            "4 stop": "4 stops",
            "4 stops": "4 stops",
            "4-stop": "4 stops",
            "4-stops": "4 stops"
        }

        return mapping.get(value, value)

    return df.with_columns(

        pl.col("stops")
        .map_elements(
            normalize_stops,
            return_dtype=pl.String
        )
        .alias("stops")

    )


# ============================================================
# CLEAN CURRENCY
# ============================================================

def clean_currency(df):

    if "currency" not in df.columns:
        return df

    return df.with_columns(

        pl.col("currency")
        .cast(pl.String)
        .str.strip_chars()
        .str.to_uppercase()
        .replace({
            "₹": "INR",
            "RS": "INR",
            "RS.": "INR",
            "RUPEE": "INR",
            "RUPEES": "INR"
        })
        .alias("currency")

    )


# ============================================================
# CLEAN SOURCE PLATFORM
# ============================================================

def clean_source_platform(df):

    if "source_platform" not in df.columns:
        return df

    return df.with_columns(

        pl.col("source_platform")
        .cast(pl.String)
        .str.strip_chars()
        .alias("source_platform")

    )


# ============================================================
# CLEAN LEAD TIME
# ============================================================

def clean_lead_time(df):

    if "lead_time" not in df.columns:
        return df

    return df.with_columns(

        pl.col("lead_time")
        .cast(pl.String)
        .str.strip_chars()
        .str.to_uppercase()
        .alias("lead_time")

    )


# ============================================================
# CLEAN SCRAPED TIME
# ============================================================

def clean_scraped_at(df):

    if "scraped_at" not in df.columns:
        return df

    return df.with_columns(

        pl.col("scraped_at")
        .cast(pl.String)
        .str.strip_chars()
        .alias("scraped_at")

    )


# ============================================================
# COMPLETE CLEANING PROCESS
# ============================================================

def clean_data(data):

    print("Removing empty records...")

    data = remove_empty_records(data)

    print(
        f"Records after removing empty records: {len(data)}"
    )

    if not data:
        return pl.DataFrame()

    # Convert list of dictionaries → Polars DataFrame
    df = pl.DataFrame(data)

    print("Cleaning text fields...")
    df = clean_text_columns(df)

    print("Cleaning airport codes...")
    df = clean_airport_codes(df)

    print("Cleaning flight numbers...")
    df = clean_flight_numbers(df)

    print("Cleaning departure time...")
    df = clean_time_column(
        df,
        "departure_time"
    )

    print("Cleaning arrival time...")
    df = clean_time_column(
        df,
        "arrival_time"
    )

    print("Cleaning duration...")
    df = clean_duration(df)

    print("Cleaning price...")
    df = clean_price(df)

    print("Cleaning stops...")
    df = clean_stops(df)

    print("Cleaning currency...")
    df = clean_currency(df)

    print("Cleaning source platform...")
    df = clean_source_platform(df)

    print("Cleaning lead time...")
    df = clean_lead_time(df)

    print("Cleaning scraped timestamp...")
    df = clean_scraped_at(df)

    return df


# ============================================================
# SAVE CLEANED DATA
# ============================================================

def save_cleaned_data(df):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.write_json(OUTPUT_FILE)

    print(
        f"\nCleaned data saved successfully at:"
        f"\n{OUTPUT_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("Starting data cleaning process...\n")

    data = load_raw_data()

    print(
        f"Raw records received: {len(data)}"
    )

    cleaned_df = clean_data(data)

    print(
        f"\nRecords after cleaning: "
        f"{cleaned_df.height}"
    )

    print("\nCleaned Data Preview:")
    print(cleaned_df)

    save_cleaned_data(cleaned_df)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()