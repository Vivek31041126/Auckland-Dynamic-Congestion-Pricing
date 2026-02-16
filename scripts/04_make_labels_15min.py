from pathlib import Path
import pandas as pd

IN_FILE = Path("data_processed/travel_time/travel_time_10min.csv")
OUT_FILE = Path("data_processed/travel_time/travel_time_10min_labeled_15min.csv")

df = pd.read_csv(IN_FILE)
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values(["edge_id", "time"])

g = df.groupby("edge_id")["travel_time_sec"]

df["tt_t_plus_10"] = g.shift(-1)
df["tt_t_plus_20"] = g.shift(-2)

# Linear interpolation for 15-minute horizon
df["y_travel_time_t_plus_15"] = 0.5 * df["tt_t_plus_10"] + 0.5 * df["tt_t_plus_20"]

df = df.dropna(subset=["y_travel_time_t_plus_15"])
df = df.drop(columns=["tt_t_plus_10", "tt_t_plus_20"])

df.to_csv(OUT_FILE, index=False)
print(f"Saved: {OUT_FILE}")
print(df.head())
