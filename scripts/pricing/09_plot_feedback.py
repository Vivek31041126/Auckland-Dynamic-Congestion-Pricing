import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/pricing/feedback_adjusted_travel_time.csv")
df["time"] = pd.to_datetime(df["time"])

plt.figure()
plt.plot(df["time"], df["corridor_travel_time_sec"], label="Original")
plt.plot(df["time"], df["adjusted_travel_time_sec"], label="After Pricing Feedback")
plt.xlabel("Time")
plt.ylabel("Travel Time (sec)")
plt.title("Congestion Pricing Feedback Effect on Travel Time")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
