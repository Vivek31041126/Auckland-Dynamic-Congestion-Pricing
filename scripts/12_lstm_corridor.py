from pathlib import Path
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

DATA = np.load("data_processed/travel_time/corridor_lstm.npz")
X = DATA["X"]
y = DATA["y"]

# Train/test split
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Reshape for LSTM: (samples, timesteps, features)
X_train = X_train[..., np.newaxis]
X_test = X_test[..., np.newaxis]

model = Sequential([
    LSTM(32, input_shape=(X_train.shape[1], 1)),
    Dense(1)
])

model.compile(optimizer="adam", loss="mse")
model.fit(X_train, y_train, epochs=30, batch_size=16, verbose=1)

pred = model.predict(X_test).flatten()

mae = mean_absolute_error(y_test, pred)
rmse = np.sqrt(mean_squared_error(y_test, pred))

print("LSTM Corridor Results")
print(f"MAE:  {mae:.2f} sec")
print(f"RMSE: {rmse:.2f} sec")
