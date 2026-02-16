from pathlib import Path
import pandas as pd

IN_FILE = Path("data_processed/travel_time/corridor_travel_time_10min.csv")
OUT_FILE = Path("results/pricing/freeflow_baseline.txt")

df = pd.read_csv(IN_FILE)
tt = df["corridor_travel_time_sec"]

tt_free = tt.quantile(0.05)  # 5th percentile free-flow
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUT_FILE.write_text(f"TT_free_sec={tt_free}\n", encoding="utf-8")

print("Saved free-flow baseline:", OUT_FILE)
print("TT_free_sec:", tt_free)
