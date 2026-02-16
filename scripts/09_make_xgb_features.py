from pathlib import Path
import pandas as pd

IN_FILE = Path("data_processed/travel_time/corridor_travel_time_10min_labeled.csv")
OUT_FILE = Path("data_processed/travel_time/corridor_xgb_features.csv")

df = pd.read_csv(IN_FILE)
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time")

# Lag features
df["lag_1"] = df["corridor_travel_time_sec"].shift(1)
df["lag_2"] = df["corridor_travel_time_sec"].shift(2)
df["lag_3"] = df["corridor_travel_time_sec"].shift(3)

# Time features
df["hour"] = df["time"].dt.hour
df["minute"] = df["time"].dt.minute

df = df.dropna()
df.to_csv(OUT_FILE, index=False)

print("Saved:", OUT_FILE)
print("Shape:", df.shape)
print(df.head())
