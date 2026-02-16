from pathlib import Path
import pandas as pd

IN_FILE = Path("data_processed/travel_time/corridor_travel_time_10min.csv")
OUT_FILE = Path("data_processed/travel_time/corridor_travel_time_10min_labeled.csv")

df = pd.read_csv(IN_FILE)
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time")

df["y_t_plus_10"] = df["corridor_travel_time_sec"].shift(-1)

df = df.dropna()
df.to_csv(OUT_FILE, index=False)

print("Saved labeled corridor data:", OUT_FILE)
print("Shape:", df.shape)
print(df.head())
