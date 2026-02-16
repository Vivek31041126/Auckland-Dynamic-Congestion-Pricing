import pandas as pd

df = pd.read_csv("results/pricing/feedback_adjusted_travel_time.csv")

reduction = (
    (df["corridor_travel_time_sec"] - df["adjusted_travel_time_sec"])
    / df["corridor_travel_time_sec"]
) * 100

print("Congestion Relief Summary")
print("-------------------------")
print(f"Average travel time reduction: {reduction.mean():.2f}%")
print(f"Maximum travel time reduction: {reduction.max():.2f}%")
