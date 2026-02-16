from pathlib import Path
import pandas as pd
import numpy as np

IN_FILE = Path("data_processed/travel_time/corridor_travel_time_10min_labeled.csv")
OUT_FILE = Path("data_processed/travel_time/corridor_lstm.npz")

SEQ_LEN = 6  # past 60 minutes (6 × 10-min)

df = pd.read_csv(IN_FILE)
series = df["corridor_travel_time_sec"].values
target = df["y_t_plus_10"].values

X, y = [], []
for i in range(len(series) - SEQ_LEN):
    X.append(series[i:i+SEQ_LEN])
    y.append(target[i+SEQ_LEN])

X = np.array(X)
y = np.array(y)

np.savez(OUT_FILE, X=X, y=y)
print("Saved LSTM sequences:", OUT_FILE)
print("X shape:", X.shape, "y shape:", y.shape)
