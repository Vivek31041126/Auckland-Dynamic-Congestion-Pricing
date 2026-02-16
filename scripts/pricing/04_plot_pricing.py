import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

IN_FILE = Path("results/pricing/pricing_schedule_arima.csv")

df = pd.read_csv(IN_FILE)
df["time"] = pd.to_datetime(df["time"])

plt.figure()
plt.plot(df["time"], df["toll_nzd"])
plt.xlabel("Time")
plt.ylabel("Toll (NZD)")
plt.title("Dynamic Congestion Pricing over Time")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
