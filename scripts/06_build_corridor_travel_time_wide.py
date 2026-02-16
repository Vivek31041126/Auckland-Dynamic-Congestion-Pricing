from pathlib import Path
import pandas as pd

IN_FILE = Path("data_processed/travel_time/travel_time_10min.csv")
OUT_FILE = Path("data_processed/travel_time/corridor_travel_time_10min.csv")

df = pd.read_csv(IN_FILE)
df["time"] = pd.to_datetime(df["time"])

# Pick edges with widest time coverage (most unique 10-min timestamps)
coverage = df.groupby("edge_id")["time"].nunique().sort_values(ascending=False)

TOP_N = 50
edges = coverage.head(TOP_N).index.tolist()

d = df[df["edge_id"].isin(edges)].copy()

time_index = pd.date_range(d["time"].min(), d["time"].max(), freq="10min")

corridor = (
    d.groupby("time")["travel_time_sec"].mean()
     .reindex(time_index)
     .interpolate("linear")
     .bfill()
     .ffill()
)

corridor_df = corridor.reset_index()
corridor_df.columns = ["time", "corridor_travel_time_sec"]
corridor_df.to_csv(OUT_FILE, index=False)

print("Saved:", OUT_FILE)
print("Shape:", corridor_df.shape)
print("Time range:", corridor_df["time"].min(), "→", corridor_df["time"].max())
print(corridor_df.head())
