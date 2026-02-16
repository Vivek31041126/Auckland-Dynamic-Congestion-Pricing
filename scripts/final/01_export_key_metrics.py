from pathlib import Path
import pandas as pd

OUT_DIR = Path("results/final_pack")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- Model metrics (fill with your confirmed final numbers) ----
model_metrics = pd.DataFrame([
    {"model": "ARIMA",  "horizon": "10-min", "MAE_sec": 0.19, "RMSE_sec": 0.25},
    {"model": "XGBoost","horizon": "10-min", "MAE_sec": 0.25, "RMSE_sec": 0.33},
    {"model": "LSTM",   "horizon": "10-min", "MAE_sec": 0.19, "RMSE_sec": 0.25},
])

# ---- Pricing summary (fill with your confirmed final numbers) ----
pricing_metrics = pd.DataFrame([{
    "total_intervals": 286,
    "tolled_intervals": 199,
    "tolled_pct": 69.6,
    "avg_toll_when_applied_nzd": 2.66,
    "revenue_proxy_nzd": 529.47,
    "avg_peak_toll_nzd": 1.54,
    "avg_offpeak_toll_nzd": 1.95,
    "avg_demand_reduction_pct": 3.70,
    "max_demand_reduction_pct": 12.00,
    "avg_travel_time_reduction_pct": 2.96,
    "max_travel_time_reduction_pct": 9.60
}])

model_metrics.to_csv(OUT_DIR / "model_metrics.csv", index=False)
pricing_metrics.to_csv(OUT_DIR / "pricing_metrics.csv", index=False)

print("Saved:", OUT_DIR / "model_metrics.csv")
print("Saved:", OUT_DIR / "pricing_metrics.csv")
print("\nMODEL METRICS:\n", model_metrics)
print("\nPRICING METRICS:\n", pricing_metrics)
