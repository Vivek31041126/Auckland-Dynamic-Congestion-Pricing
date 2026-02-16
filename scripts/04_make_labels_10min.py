from pathlib import Path
import pandas as pd

IN_FILE = Path("data_processed/travel_time/travel_time_10min.csv")
OUT_FILE = Path("data_processed/travel_time/travel_time_10min_labeled_10min.csv")

df = pd.read_csv(IN_FILE)
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values(["edge_id", "time"])

df["y_travel_time_t_plus_10"] = df.groupby("edge_id")["travel_time_sec"].shift(-1)

df = df.dropna(subset=["y_travel_time_t_plus_10"])
df.to_csv(OUT_FILE, index=False)

print("Saved:", OUT_FILE)
print("shape:", df.shape)
print(df.head(3))
