import pandas as pd
from pathlib import Path


ROOT = Path(__file__).resolve().parent

RESULTS_FILE = (
    ROOT
    / "data"
    / "anomaly_results_3650.csv"
)

df = pd.read_csv(RESULTS_FILE)

df["scraped_at"] = pd.to_datetime(
    df["scraped_at"]
)

df["date"] = df["scraped_at"].dt.date


# ---------------------------------------
# Known injected anomaly periods
# ---------------------------------------

shock_periods = [
    ("2025-11-07", "2025-11-09"),
    ("2026-01-14", "2026-01-16"),
    ("2026-04-18", "2026-04-20"),
    ("2026-07-09", "2026-07-11"),
    ("2026-08-15", "2026-08-17"),
]


print("\n" + "=" * 70)
print("ANOMALY DETECTION EVALUATION")
print("=" * 70)


for start, end in shock_periods:

    start = pd.to_datetime(start).date()
    end = pd.to_datetime(end).date()

    period = df[
        (df["date"] >= start)
        & (df["date"] <= end)
    ]

    detected = period[
        period["alert_level"].isin(
            ["WATCH", "HIGH"]
        )
    ]

    high = period[
        period["alert_level"] == "HIGH"
    ]

    print("\nShock period:")
    print(f"{start} → {end}")

    print(
        f"Records: {len(period)}"
    )

    print(
        f"Detected: {len(detected)}"
    )

    print(
        f"HIGH: {len(high)}"
    )

    if len(period) > 0:

        detection_rate = (
            len(detected)
            / len(period)
            * 100
        )

        print(
            f"Detection rate: "
            f"{detection_rate:.2f}%"
        )


# ---------------------------------------
# Overall statistics
# ---------------------------------------

print("\n" + "=" * 70)
print("OVERALL")
print("=" * 70)

print(
    df["alert_level"]
    .value_counts()
)

print("\nAverage anomaly score by alert:")

print(
    df.groupby("alert_level")[
        "anomaly_score"
    ].mean()
)


print("\nEvaluation complete.")