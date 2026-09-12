
import json
import re
from pathlib import Path

import polars as pl


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "deduplicated_data.json"
OUTPUT_FILE = BASE_DIR / "data" / "normalised_data.json"


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_data():
    """
    Load deduplicated flight data.
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
# TEXT NORMALISATION
# ---------------------------------------------------------

def normalise_text_columns(df):
    """
    Remove extra spaces from text fields.
    """

    text_columns = [
        "airline",
        "flight_number",
        "origin",
        "destination",
        "duration",
        "stops",
        "currency",
        "source_platform",
        "lead_time",
    ]

    for column in text_columns:
        if column in df.columns:
            df = df.with_columns(
                pl.col(column)
                .cast(pl.String)
                .str.strip_chars()
                .str.replace_all(r"\s+", " ")
                .alias(column)
            )

    return df


# ---------------------------------------------------------
# AIRPORT CODE NORMALISATION
# ---------------------------------------------------------

def normalise_airport_codes(df):
    """
    Convert airport codes to uppercase.

    Example:
        del -> DEL
        bom -> BOM
    """

    for column in ["origin", "destination"]:
        if column in df.columns:
            df = df.with_columns(
                pl.col(column)
                .str.to_uppercase()
                .alias(column)
            )

    return df


# ---------------------------------------------------------
# FLIGHT NUMBER NORMALISATION
# ---------------------------------------------------------

def normalise_flight_numbers(df):
    """
    Make flight numbers uppercase and remove spaces.

    Example:
        ix 1056 -> IX1056
        ix-1056 -> IX-1056
    """

    if "flight_number" in df.columns:
        df = df.with_columns(
            pl.col("flight_number")
            .str.to_uppercase()
            .str.replace_all(r"\s+", "")
            .alias("flight_number")
        )

    return df


# ---------------------------------------------------------
# TIME NORMALISATION
# ---------------------------------------------------------

def normalise_time_column(df, column):
    """
    Convert different time formats into HH:MM:SS.

    Example:
        05:35 -> 05:35:00
        5:35  -> 05:35:00
    """

    if column not in df.columns:
        return df

    df = df.with_columns(
        pl.col(column)
        .cast(pl.String)
        .str.strip_chars()
        .str.extract(r"(\d{1,2}:\d{2})", 1)
        .alias(column)
    )

    df = df.with_columns(
        pl.col(column)
        .str.strptime(
            pl.Time,
            format="%H:%M",
            strict=False
        )
        .dt.strftime("%H:%M:%S")
        .alias(column)
    )

    return df


def normalise_times(df):
    """
    Normalise departure and arrival times.
    """

    df = normalise_time_column(df, "departure_time")
    df = normalise_time_column(df, "arrival_time")

    return df


# ---------------------------------------------------------
# DURATION NORMALISATION
# ---------------------------------------------------------

def normalise_duration(df):
    """
    Convert duration into a consistent HHh MMm format.

    Example:
        02h 30m -> 02h 30m
        2h 30m  -> 02h 30m
    """

    if "duration" not in df.columns:
        return df

    def format_duration(value):
        if value is None:
            return None

        value = str(value).strip().lower()

        hours_match = re.search(r"(\d+)\s*h", value)
        minutes_match = re.search(r"(\d+)\s*m", value)

        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0

        return f"{hours:02d}h {minutes:02d}m"

    df = df.with_columns(
        pl.col("duration")
        .map_elements(
            format_duration,
            return_dtype=pl.String
        )
        .alias("duration")
    )

    return df


# ---------------------------------------------------------
# STOPS NORMALISATION
# ---------------------------------------------------------

def normalise_stops(df):
    """
    Convert different stop descriptions into one standard format.

    Examples:
        Non-stop
        Non Stop
        nonstop
        1 Stop
        2 Stops
    """

    if "stops" not in df.columns:
        return df

    df = df.with_columns(
        pl.col("stops")
        .cast(pl.String)
        .str.strip_chars()
        .str.to_lowercase()
        .str.replace_all(r"\s+", " ")
        .alias("stops")
    )

    df = df.with_columns(
        pl.when(
            pl.col("stops").is_in(
                ["non-stop", "non stop", "nonstop", "direct", "0 stop"]
            )
        )
        .then(pl.lit("non-stop"))

        .when(
            pl.col("stops").is_in(["1 stop", "1-stop", "1 stops"])
        )
        .then(pl.lit("1 stop"))

        .when(
            pl.col("stops").is_in(["2 stops", "2 stop", "2-stops"])
        )
        .then(pl.lit("2 stops"))

        .when(
            pl.col("stops").is_in(["3 stops", "3 stop", "3-stops"])
        )
        .then(pl.lit("3 stops"))

        .when(
            pl.col("stops").is_in(["4 stops", "4 stop", "4-stops"])
        )
        .then(pl.lit("4 stops"))

        .otherwise(pl.col("stops"))

        .alias("stops")
    )

    return df


# ---------------------------------------------------------
# PRICE NORMALISATION
# ---------------------------------------------------------

def normalise_price(df):
    """
    Convert price into a numeric float.

    Examples:
        ₹6,529 -> 6529.0
        6,529  -> 6529.0
        6529   -> 6529.0
    """

    if "price" not in df.columns:
        return df

    df = df.with_columns(
        pl.col("price")
        .cast(pl.String)
        .str.replace_all(r"[^0-9.]", "")
        .cast(pl.Float64, strict=False)
        .alias("price")
    )

    return df


# ---------------------------------------------------------
# CURRENCY NORMALISATION
# ---------------------------------------------------------

def normalise_currency(df):
    """
    Convert currency representations into INR.
    """

    if "currency" not in df.columns:
        return df

    df = df.with_columns(
        pl.col("currency")
        .cast(pl.String)
        .str.strip_chars()
        .str.to_uppercase()
        .alias("currency")
    )

    df = df.with_columns(
        pl.when(
            pl.col("currency").is_in(
                ["₹", "RS", "RS.", "RUPEE", "RUPEES", "INR"]
            )
        )
        .then(pl.lit("INR"))
        .otherwise(pl.col("currency"))
        .alias("currency")
    )

    return df


# ---------------------------------------------------------
# LEAD TIME NORMALISATION
# ---------------------------------------------------------

def normalise_lead_time(df):
    """
    Convert lead time into T+N format.

    Examples:
        t+1 -> T+1
        T + 3 -> T+3
        5 -> T+5
    """

    if "lead_time" not in df.columns:
        return df

    df = df.with_columns(
        pl.col("lead_time")
        .cast(pl.String)
        .str.strip_chars()
        .str.to_uppercase()
        .str.replace_all(r"\s+", "")
        .alias("lead_time")
    )

    df = df.with_columns(
        pl.col("lead_time")
        .str.replace(
            r"^T\+?(\d+)$",
            "T+$1"
        )
        .alias("lead_time")
    )

    return df


# ---------------------------------------------------------
# SCRAPED TIME NORMALISATION
# ---------------------------------------------------------

def normalise_scraped_at(df):
    """
    Convert scraped_at into a standard ISO datetime string.
    """

    if "scraped_at" not in df.columns:
        return df

    df = df.with_columns(
        pl.col("scraped_at")
        .cast(pl.String)
        .str.strip_chars()
        .str.to_datetime(
            strict=False,
            time_zone="UTC"
        )
        .dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        .alias("scraped_at")
    )

    return df


# ---------------------------------------------------------
# COMPLETE NORMALISATION
# ---------------------------------------------------------

def normalise_data(data):
    """
    Apply all normalisation operations.
    """

    if not data:
        return []

    df = pl.DataFrame(data)

    print("\nNormalising data...")

    df = normalise_text_columns(df)

    print("✓ Text fields normalised")

    df = normalise_airport_codes(df)

    print("✓ Airport codes normalised")

    df = normalise_flight_numbers(df)

    print("✓ Flight numbers normalised")

    df = normalise_times(df)

    print("✓ Departure and arrival times normalised")

    df = normalise_duration(df)

    print("✓ Duration normalised")

    df = normalise_stops(df)

    print("✓ Stops normalised")

    df = normalise_price(df)

    print("✓ Price normalised")

    df = normalise_currency(df)

    print("✓ Currency normalised")

    df = normalise_lead_time(df)

    print("✓ Lead time normalised")

    df = normalise_scraped_at(df)

    print("✓ Scraped timestamp normalised")

    return df.to_dicts()


# ---------------------------------------------------------
# SAVE DATA
# ---------------------------------------------------------

def save_data(data):
    """
    Save normalised data.
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
    print("       DATA NORMALISATION")
    print("======================================")

    # Load deduplicated data
    data = load_data()

    print(f"\nRecords received: {len(data)}")

    # Normalise
    normalised_data = normalise_data(data)

    # Save
    save_data(normalised_data)

    print("\n======================================")
    print("       NORMALISATION SUMMARY")
    print("======================================")

    print(f"Records processed: {len(normalised_data)}")

    print("\nNormalised data saved at:")
    print(OUTPUT_FILE)

    print("\nFirst record after normalisation:")

    if normalised_data:
        print(
            json.dumps(
                normalised_data[0],
                indent=4,
                ensure_ascii=False
            )
        )

    print("\n======================================")


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
