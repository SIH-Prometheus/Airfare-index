import pandas as pd
import numpy as np


def build_features(df: pd.DataFrame):

    df = df.copy()

    # -----------------------------
    # Parse date
    # -----------------------------

    df["scraped_at"] = pd.to_datetime(df["scraped_at"])

    df["date"] = df["scraped_at"].dt.date

    df["route"] = (
        df["origin"].astype(str)
        + "-"
        + df["destination"].astype(str)
    )

    # -----------------------------
    # Basic flight features
    # -----------------------------

    df["lead_time_days"] = (
        df["lead_time"]
        .str.extract(r"(\d+)")
        .astype(int)
    )

    duration = df["duration"].str.extract(
        r"(\d+)\s*(?:h|hr)\s*(\d+)\s*(?:m|min)"
    )

    df["duration_minutes"] = (
        duration[0].astype(int) * 60
        + duration[1].astype(int)
    )

    df["stops_count"] = df["stops"].apply(
        lambda x: 0 if x == "Non-stop" else 1
    )

    df["departure_hour"] = (
        df["departure_time"]
        .str.extract(r"(\d+)")
        .astype(int)
    )

    df["arrival_hour"] = (
        df["arrival_time"]
        .str.extract(r"(\d+)")
        .astype(int)
    )

    df["day_of_week"] = df["scraped_at"].dt.dayofweek
    df["month"] = df["scraped_at"].dt.month

    # -----------------------------
    # Sort chronologically
    # -----------------------------

    df = df.sort_values(
        ["route", "date"]
    ).reset_index(drop=True)

    # -----------------------------
    # Route-level historical data
    # -----------------------------

    grouped = df.groupby("route")["price"]

    # Previous day's price
    df["previous_price"] = grouped.shift(1)

    # 7-day historical mean
    # shift(1) prevents today's price
    # from entering today's baseline
    df["baseline_7d"] = (
        grouped
        .transform(
            lambda x:
            x.shift(1)
             .rolling(7, min_periods=3)
             .mean()
        )
    )

    # 7-day historical standard deviation
    df["std_7d"] = (
        grouped
        .transform(
            lambda x:
            x.shift(1)
             .rolling(7, min_periods=3)
             .std()
        )
    )

    # 30-day historical mean
    df["baseline_30d"] = (
        grouped
        .transform(
            lambda x:
            x.shift(1)
             .rolling(30, min_periods=7)
             .mean()
        )
    )

    # -----------------------------
    # Price changes
    # -----------------------------

    df["price_change_1d"] = (
        df["price"]
        / df["previous_price"]
        - 1
    )

    df["price_7d_ago"] = grouped.shift(7)

    df["price_change_7d"] = (
        df["price"]
        / df["price_7d_ago"]
        - 1
    )

    # -----------------------------
    # Z-score
    # -----------------------------

    df["z_score"] = (
        df["price"] - df["baseline_7d"]
    ) / df["std_7d"]

    # -----------------------------
    # Percentage deviation
    # -----------------------------

    df["price_vs_7d_baseline"] = (
        df["price"]
        / df["baseline_7d"]
        - 1
    )

    # -----------------------------
    # Clean numerical values
    # -----------------------------

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # We don't want missing historical
    # values to become artificial anomalies.
    df["baseline_7d"] = df["baseline_7d"].fillna(
        df["price"]
    )

    df["std_7d"] = df["std_7d"].fillna(0)

    df["baseline_30d"] = df["baseline_30d"].fillna(
        df["price"]
    )

    df["price_change_1d"] = (
        df["price_change_1d"]
        .fillna(0)
    )

    df["price_change_7d"] = (
        df["price_change_7d"]
        .fillna(0)
    )

    df["z_score"] = (
        df["z_score"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    df["price_vs_7d_baseline"] = (
        df["price_vs_7d_baseline"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    # -----------------------------
    # Features specifically for
    # airfare anomaly detection
    # -----------------------------

    feature_columns = [
        "price",
        "baseline_7d",
        "std_7d",
        "price_change_1d",
        "price_change_7d",
        "z_score",
        "price_vs_7d_baseline",
        "day_of_week",
        "month",
    ]

    X = df[feature_columns].copy()

    return X, df, feature_columns