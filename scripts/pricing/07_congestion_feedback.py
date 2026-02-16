from pathlib import Path
import pandas as pd

IN_FILE = Path("results/pricing/demand_response.csv")
OUT_FILE = Path("results/pricing/feedback_adjusted_travel_time.csv")

ALPHA = 0.8  # congestion sensitivity

df = pd.read_csv(IN_FILE)
df["time"] = pd.to_datetime(df["time"])

# Re-load original corridor travel time
tt = pd.read_csv("data_processed/travel_time/corridor_travel_time_10min.csv")
tt["time"] = pd.to_datetime(tt["time"])

df = df.merge(tt, on="time", how="left")

# Apply feedback
df["adjusted_travel_time_sec"] = (
    df["corridor_travel_time_sec"]
    * (1 - ALPHA * (-df["demand_change_pct"]))
)

df_out = df[[
    "time",
    "corridor_travel_time_sec",
    "adjusted_travel_time_sec",
    "demand_change_pct"
]]

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df_out.to_csv(OUT_FILE, index=False)

print("Saved:", OUT_FILE)
print(df_out.head(10))
