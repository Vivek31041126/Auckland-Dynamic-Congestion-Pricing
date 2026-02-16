from pathlib import Path
import pandas as pd

IN_FILE = Path("data_raw/SUMO/edge_1min_raw.csv")
OUT_DIR = Path("data_processed/SUMO")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "edge_10min.csv"

df = pd.read_csv(IN_FILE)

# Convert simulation seconds to datetime-like index (relative time)
df["time"] = pd.to_datetime(df["begin_sec"], unit="s")

# Aggregate per edge per 10 minutes
agg = {
    "speed_mps": "mean",
    "density": "mean",
    "flow": "mean",
    "occupancy": "mean",
    "length_m": "first"
}

df_10 = (
    df.set_index("time")
      .groupby("edge_id")
      .resample("10min")
      .agg(agg)
      .reset_index()
)

df_10.to_csv(OUT_FILE, index=False)
print(f"Saved: {OUT_FILE}")
print(df_10.head())
