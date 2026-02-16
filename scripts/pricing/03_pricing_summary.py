from pathlib import Path
import pandas as pd

IN_FILE = Path("results/pricing/pricing_schedule_arima.csv")
OUT_FILE = Path("results/pricing/pricing_summary.txt")

df = pd.read_csv(IN_FILE)
df["time"] = pd.to_datetime(df["time"])

# Peak definition (simple & defensible)
df["hour"] = df["time"].dt.hour
df["is_peak"] = df["hour"].isin([7,8,9,16,17,18])

# Key metrics
total_intervals = len(df)
toll_intervals = (df["toll_nzd"] > 0).sum()
pct_tolled = toll_intervals / total_intervals * 100

avg_toll = df.loc[df["toll_nzd"] > 0, "toll_nzd"].mean()

# Revenue proxy (assume 1 vehicle per interval for normalization)
total_revenue = df["toll_nzd"].sum()

# Peak vs off-peak
peak_avg = df.loc[df["is_peak"], "toll_nzd"].mean()
offpeak_avg = df.loc[~df["is_peak"], "toll_nzd"].mean()

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUT_FILE.write_text(
    f"""
Dynamic Congestion Pricing Summary
---------------------------------
Total intervals: {total_intervals}
Tolled intervals: {toll_intervals} ({pct_tolled:.1f}%)

Average toll (when applied): ${avg_toll:.2f}
Total revenue proxy: ${total_revenue:.2f}

Average peak toll: ${peak_avg:.2f}
Average off-peak toll: ${offpeak_avg:.2f}
""".strip()
)

print(OUT_FILE.read_text())
