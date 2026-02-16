from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

OUT_DIR = Path("results/final_pack")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- Figure 1: Toll over time ----
pricing = pd.read_csv("results/pricing/pricing_schedule_arima.csv")
pricing["time"] = pd.to_datetime(pricing["time"])

plt.figure()
plt.plot(pricing["time"], pricing["toll_nzd"])
plt.xlabel("Time")
plt.ylabel("Toll (NZD)")
plt.title("Dynamic Congestion Pricing Over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(OUT_DIR / "fig1_toll_over_time.png", dpi=300)
plt.close()

# ---- Figure 2: Travel time before vs after feedback ----
fb = pd.read_csv("results/pricing/feedback_adjusted_travel_time.csv")
fb["time"] = pd.to_datetime(fb["time"])

plt.figure()
plt.plot(fb["time"], fb["corridor_travel_time_sec"], label="Original")
plt.plot(fb["time"], fb["adjusted_travel_time_sec"], label="After Pricing Feedback")
plt.xlabel("Time")
plt.ylabel("Travel Time (sec)")
plt.title("Pricing Feedback Effect on Travel Time")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(OUT_DIR / "fig2_travel_time_feedback.png", dpi=300)
plt.close()

print("Saved figures to:", OUT_DIR)
