from pathlib import Path
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

IN_FILE = Path("data_processed/travel_time/corridor_travel_time_10min_labeled.csv")
OUT_FILE = Path("results/pricing/pricing_schedule_arima.csv")

# Pricing parameters (NZD)
TOLL_MIN = 1.0
TOLL_MID = 3.0
TOLL_CAP = 6.0

CI_FREE = 1.10
CI_MID  = 1.30

df = pd.read_csv(IN_FILE)
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time").reset_index(drop=True)

series = df["corridor_travel_time_sec"]

# Free-flow baseline (5th percentile)
TT_free = series.quantile(0.05)

# Fit ARIMA on full history and forecast one-step ahead for each time (rolling style simplified)
# For thesis simplicity: use actual t value as "prediction for next interval" shift.
# This is a naive proxy; next step we will switch to true rolling forecasts.
df["TT_pred_sec"] = df["corridor_travel_time_sec"].shift(1)
df = df.dropna().copy()

df["CI"] = df["TT_pred_sec"] / TT_free

def toll(ci):
    if ci <= CI_FREE:
        return 0.0
    elif ci <= CI_MID:
        # scale from TOLL_MIN to TOLL_MID
        x = (ci - CI_FREE) / (CI_MID - CI_FREE)
        return TOLL_MIN + x * (TOLL_MID - TOLL_MIN)
    else:
        # scale from TOLL_MID to TOLL_CAP, capped
        x = min((ci - CI_MID) / (1.60 - CI_MID), 1.0)  # assumes CI=1.60 as "severe"
        return TOLL_MID + x * (TOLL_CAP - TOLL_MID)

df["toll_nzd"] = df["CI"].apply(toll)

df_out = df[["time", "TT_pred_sec", "CI", "toll_nzd"]]
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df_out.to_csv(OUT_FILE, index=False)

print("Saved pricing schedule:", OUT_FILE)
print("TT_free_sec:", TT_free)
print(df_out.head(10))
