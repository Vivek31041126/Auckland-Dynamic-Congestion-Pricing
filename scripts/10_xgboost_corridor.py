from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

DATA = Path("data_processed/travel_time/corridor_xgb_features.csv")

df = pd.read_csv(DATA)

X = df[["lag_1", "lag_2", "lag_3", "hour", "minute"]]
y = df["y_t_plus_10"]

# Train/test split
split = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

model = XGBRegressor(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

model.fit(X_train, y_train)

pred = model.predict(X_test)

mae = mean_absolute_error(y_test, pred)
rmse = np.sqrt(mean_squared_error(y_test, pred))

print("XGBoost Corridor Results")
print(f"MAE:  {mae:.2f} sec")
print(f"RMSE: {rmse:.2f} sec")
