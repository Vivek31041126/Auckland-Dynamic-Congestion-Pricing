import json
import time
from pathlib import Path

import pandas as pd
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)

# Change this path if needed
csv_path = Path("data_processed/travel_time/travel_time_10min.csv")
df = pd.read_csv(csv_path)

print("Columns found:", df.columns.tolist())

# Pick the correct travel-time column
if "corridor_travel_time_sec" in df.columns:
    tt_col = "corridor_travel_time_sec"
elif "travel_time_sec" in df.columns:
    tt_col = "travel_time_sec"
else:
    raise ValueError(f"No travel time column found in {csv_path}. Columns: {df.columns.tolist()}")

# If edge-level data exists, optionally filter one edge to simulate a single stream
if "edge_id" in df.columns:
    first_edge = df["edge_id"].dropna().iloc[0]
    df = df[df["edge_id"] == first_edge].copy()
    print("Using edge_id:", first_edge)

for _, row in df.iterrows():
    message = {
        "time": str(row["time"]),
        "travel_time": float(row[tt_col])
    }

    client.publish("traffic/auckland/corridor", json.dumps(message))
    print("Published:", message)

    time.sleep(1)