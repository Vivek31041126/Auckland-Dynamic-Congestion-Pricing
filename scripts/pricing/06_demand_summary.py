from pathlib import Path
import pandas as pd

IN_FILE = Path("results/pricing/demand_response.csv")

df = pd.read_csv(IN_FILE)

avg_reduction = -df["demand_change_pct"].mean() * 100
max_reduction = -df["demand_change_pct"].min() * 100

print("Demand Response Summary")
print("-----------------------")
print(f"Average demand reduction: {avg_reduction:.2f}%")
print(f"Maximum demand reduction: {max_reduction:.2f}%")
