import pandas as pd

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame()

    # Flight price
    features["price"] = df["price"]

    # T+1 → 1, T+7 → 7, etc.
    features["lead_time_days"] = (
        df["lead_time"]
        .str.replace("T+", "", regex=False)
        .astype(int)
    )

    # "02h 30m" → 150 minutes
    duration = df["duration"].str.extract(
    r"(\d+)\s*(?:h|hr)\s*(\d+)\s*(?:m|min)"
)

    features["duration_minutes"] = (
    duration[0].astype(int) * 60
    + duration[1].astype(int)
)

    # Non-stop → 0
    # Anything with a stop → 1 for now
    features["stops_count"] = (
    df["stops"]
    .str.extract(r"(\d+)")
    .fillna(0)
    .astype(int)
)

    # "05:35" → 5
    features["departure_hour"] = (
        df["departure_time"]
        .str.split(":")
        .str[0]
        .astype(int)
    )

    # "08:05" → 8
    features["arrival_hour"] = (
        df["arrival_time"]
        .str.split(":")
        .str[0]
        .astype(int)
    )

    return features