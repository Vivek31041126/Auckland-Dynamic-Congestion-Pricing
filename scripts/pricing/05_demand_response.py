from pathlib import Path
import pandas as pd

IN_FILE = Path("results/pricing/pricing_schedule_arima.csv")
OUT_FILE = Path("results/pricing/demand_response.csv")

ELASTICITY = -0.10      # short-run elasticity
BASE_COST = 5.00        # assumed baseline generalized cost (NZD)

df = pd.read_csv(IN_FILE)
df["time"] = pd.to_datetime(df["time"])

# Relative price change
df["price_change_pct"] = df["toll_nzd"] / BASE_COST

# Demand response
df["demand_change_pct"] = ELASTICITY * df["price_change_pct"]

# Remaining demand factor
df["remaining_demand_factor"] = 1 + df["demand_change_pct"]

df_out = df[[
    "time",
    "toll_nzd",
    "price_change_pct",
    "demand_change_pct",
    "remaining_demand_factor"
]]

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df_out.to_csv(OUT_FILE, index=False)

print("Saved:", OUT_FILE)
print(df_out.head(10))
