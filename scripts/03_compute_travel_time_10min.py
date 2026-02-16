from pathlib import Path
import pandas as pd

IN_FILE = Path("data_processed/SUMO/edge_10min.csv")
OUT_DIR = Path("data_processed/travel_time")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "travel_time_10min.csv"

df = pd.read_csv(IN_FILE)
df["time"] = pd.to_datetime(df["time"])

# Drop rows where speed or length is missing/zero
df = df.dropna(subset=["speed_mps", "length_m"])
df = df[df["speed_mps"] > 0]
df = df[df["length_m"] > 0]

# Travel time (seconds) = length / speed
df["travel_time_sec"] = df["length_m"] / df["speed_mps"]

df_out = df[["time", "edge_id", "travel_time_sec"]].copy()
df_out.to_csv(OUT_FILE, index=False)

print(f"Saved: {OUT_FILE}")
print(df_out.head())
