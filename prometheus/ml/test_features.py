import json
import pandas as pd

from features import build_features


with open("../data/dummy_flights.json", "r") as f:
    flights = json.load(f)

df = pd.DataFrame(flights)

features = build_features(df)

print("\nML Features:")
print(features)
