from pathlib import Path
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error

DATA = Path("data_processed/travel_time/travel_time_10min_labeled_10min.csv")

df = pd.read_csv(DATA)
df["time"] = pd.to_datetime(df["time"])

# Count samples per edge
counts = df["edge_id"].value_counts()

# Pick an edge with sufficient history
MIN_POINTS = 100
valid_edges = counts[counts >= MIN_POINTS]

if valid_edges.empty:
    raise ValueError("No edge has enough time points. Increase simulation duration.")

edge_id = valid_edges.index[0]
df_edge = df[df["edge_id"] == edge_id].sort_values("time").reset_index(drop=True)

print(f"Using edge: {edge_id} with {len(df_edge)} samples")

# Train/test split
split = int(len(df_edge) * 0.8)
train = df_edge.iloc[:split]
test = df_edge.iloc[split:]

y_train = train["travel_time_sec"]
y_test = test["y_travel_time_t_plus_10"]

# ARIMA baseline
model = ARIMA(y_train, order=(1,1,1))
fit = model.fit()

forecast = fit.forecast(steps=len(test))

mae = mean_absolute_error(y_test, forecast)
rmse = np.sqrt(mean_squared_error(y_test, forecast))

print(f"Train samples: {len(train)}, Test samples: {len(test)}")
print(f"ARIMA MAE:  {mae:.2f} sec")
print(f"ARIMA RMSE: {rmse:.2f} sec")



