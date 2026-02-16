from pathlib import Path
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error

DATA = Path("data_processed/travel_time/corridor_travel_time_10min_labeled.csv")

df = pd.read_csv(DATA)
df["time"] = pd.to_datetime(df["time"])

print("Loaded shape:", df.shape)

# Train/test split
split = int(len(df) * 0.8)
train = df.iloc[:split]
test = df.iloc[split:]

y_train = train["corridor_travel_time_sec"]
y_test = test["y_t_plus_10"]

model = ARIMA(y_train, order=(1,1,1))
fit = model.fit()

forecast = fit.forecast(steps=len(test))

mae = mean_absolute_error(y_test, forecast)
rmse = np.sqrt(mean_squared_error(y_test, forecast))

print(f"Train samples: {len(train)}, Test samples: {len(test)}")
print(f"ARIMA Corridor MAE:  {mae:.2f} sec")
print(f"ARIMA Corridor RMSE: {rmse:.2f} sec")
