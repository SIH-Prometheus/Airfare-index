import joblib
import json
from pathlib import Path

import pandas as pd

from features import build_features
from anomaly import AnomalyDetector


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent

DATA_FILE = (
    ROOT
    / "data"
    / "matrix_flights_3650.json"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "anomaly_results_3650.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading dataset...")

with open(DATA_FILE, "r") as f:
    flights = json.load(f)

df = pd.DataFrame(flights)

print(f"Records loaded: {len(df)}")


# ============================================================
# FEATURE ENGINEERING
# ============================================================

print("\nBuilding route-day features...")

X, processed_df, feature_columns = build_features(df)

print(f"Feature matrix: {X.shape}")

print("\nFeatures used:")

for feature in feature_columns:
    print(" -", feature)


# ============================================================
# TRAIN ISOLATION FOREST
# ============================================================

print("\nTraining Isolation Forest...")

detector = AnomalyDetector(
    contamination=0.05
)

detector.fit(X)

predictions, scores = detector.predict(X)
MODEL_FILE = ROOT / "anomaly_model.pkl"

joblib.dump(
    detector,
    MODEL_FILE
)

print(f"\nModel saved to: {MODEL_FILE}")

processed_df["anomaly_prediction"] = predictions
processed_df["anomaly_score"] = scores


# ============================================================
# INFLATION ALERT LOGIC
# ============================================================

def determine_alert(row):

    increase = row["price_vs_7d_baseline"]
    score = row["anomaly_score"]
    z = abs(row["z_score"])

    # HIGH inflation
    if (
        increase >= 0.20
        or score >= 0.80
        or z >= 3
    ):
        return "HIGH"

    # WATCH inflation
    if (
        increase >= 0.10
        or score >= 0.60
        or z >= 2
    ):
        return "WATCH"

    # Normal price movement
    return "NORMAL"


processed_df["alert_level"] = (
    processed_df.apply(
        determine_alert,
        axis=1
    )
)


# ============================================================
# INFLATION PERCENTAGE
# ============================================================

processed_df["inflation_percent"] = (
    processed_df["price_vs_7d_baseline"] * 100
)


# ============================================================
# SAVE RESULTS
# ============================================================

processed_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("AIRFARE INFLATION ALERT SYSTEM")
print("=" * 60)

print("\nAlert distribution:")

print(
    processed_df["alert_level"]
    .value_counts()
)


# ============================================================
# TOP INFLATION ALERTS
# ============================================================

print("\n" + "=" * 60)
print("TOP 20 INFLATION ALERTS")
print("=" * 60)

columns_to_show = [
    "origin",
    "destination",
    "price",
    "baseline_7d",
    "inflation_percent",
    "price_change_1d",
    "price_change_7d",
    "z_score",
    "anomaly_score",
    "alert_level",
    "scraped_at",
]


top_alerts = (
    processed_df
    .sort_values(
        "inflation_percent",
        ascending=False
    )
    .head(20)
)


print(
    top_alerts[
        columns_to_show
    ].to_string(index=False)
)


# ============================================================
# HIGH ALERTS ONLY
# ============================================================

high_alerts = processed_df[
    processed_df["alert_level"] == "HIGH"
].copy()


print("\n" + "=" * 60)
print("HIGH INFLATION ALERTS")
print("=" * 60)

print(
    f"Total HIGH alerts: {len(high_alerts)}"
)


if len(high_alerts) > 0:

    high_alert_columns = [
        "origin",
        "destination",
        "price",
        "baseline_7d",
        "inflation_percent",
        "price_change_1d",
        "alert_level",
        "scraped_at",
    ]

    print(
        high_alerts[
            high_alert_columns
        ]
        .sort_values(
            "inflation_percent",
            ascending=False
        )
        .head(20)
        .to_string(index=False)
    )


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)

print(
    f"\nResults saved to:\n{OUTPUT_FILE}"
)

print("\nInflation thresholds:")

print(" NORMAL : < 10% increase")
print(" WATCH  : 10% - 20% increase")
print(" HIGH   : >= 20% increase")

print("\nDone.")

