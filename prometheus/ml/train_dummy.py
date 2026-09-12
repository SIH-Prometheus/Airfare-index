import json
import pandas as pd
import numpy as np

from features import build_features
from anomaly import AnomalyDetector


# 1. Load dummy flight data
with open("prometheus/data/matrix_flights.json", "r") as f:
    flights = json.load(f)


# 2. Convert JSON to DataFrame
df = pd.DataFrame(flights)


# 3. Convert flight data into ML features
features = build_features(df)


# 4. Convert DataFrame to NumPy array
X = features.to_numpy()


# 5. Create anomaly detector
detector = AnomalyDetector(contamination=0.125)


# 6. Train model and predict
predictions = detector.train_and_predict(X)


# 7. Display results
print("\n===== ANOMALY DETECTION RESULTS =====\n")

for flight, prediction in zip(flights, predictions):

    if prediction == -1:
        status = "ANOMALY"
    else:
        status = "NORMAL"

    print(
        f"{flight['flight_number']:8} | "
        f"{flight['airline']:20} | "
        f"Price: ₹{flight['price']:6} | "
        f"{status}"
    )