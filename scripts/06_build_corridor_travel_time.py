from pathlib import Path
import pandas as pd

IN_FILE = Path("data_processed/travel_time/travel_time_10min.csv")
OUT_FILE = Path("data_processed/travel_time/corridor_travel_time_10min.csv")

df = pd.read_csv(IN_FILE)
df["time"] = pd.to_datetime(df["time"])

# STEP 1: select top-N most active edges
edge_counts = df["edge_id"].value_counts()
TOP_N = 20
top_edges = edge_counts.head(TOP_N).index.tolist()

df = df[df["edge_id"].isin(top_edges)]

# STEP 2: create continuous 10-min timeline
time_index = pd.date_range(
    start=df["time"].min(),
    end=df["time"].max(),
    freq="10min"
)

# STEP 3: aggregate travel time per 10-min
corridor = (
    df.groupby("time")["travel_time_sec"]
      .mean()
      .reindex(time_index)
)

# STEP 4: handle missing bins (critical)
corridor = corridor.interpolate(method="linear")
corridor = corridor.fillna(method="bfill").fillna(method="ffill")

corridor_df = corridor.reset_index()
corridor_df.columns = ["time", "corridor_travel_time_sec"]

corridor_df.to_csv(OUT_FILE, index=False)

print("Saved:", OUT_FILE)
print("Shape:", corridor_df.shape)
print(corridor_df.head())
