import pandas as pd

df = pd.read_csv("../../data_raw/AT_API/traffic_speed_raw.csv")
print(df.columns.tolist())

# -----------------------------
# CONFIG
# -----------------------------
RAW_FILE = "../../data_raw/AT_API/traffic_speed_raw.csv"
OUTPUT_FILE = "../traffic_speed_cleaned.csv"

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(RAW_FILE)

print("Initial shape:", df.shape)
print("Columns:", df.columns)

# -----------------------------
# STANDARDISE COLUMN NAMES
# -----------------------------
df.columns = [c.lower().strip() for c in df.columns]

# -----------------------------
# IDENTIFY KEY COLUMNS
# (adjust names if needed)
# -----------------------------
# -----------------------------
# IDENTIFY KEY COLUMNS (ROBUST)
# -----------------------------
possible_time_cols = ["time", "date", "timestamp"]
possible_speed_cols = ["speed", "velocity", "avg", "value"]

time_col = None
speed_col = None

for c in df.columns:
    if any(k in c for k in possible_time_cols):
        time_col = c
    if any(k in c for k in possible_speed_cols):
        speed_col = c

if time_col is None:
    raise ValueError("❌ No time column found. Check dataset columns.")

if speed_col is None:
    raise ValueError("❌ No speed column found. Check dataset columns.")

print("✔ Detected time column:", time_col)
print("✔ Detected speed column:", speed_col)

# -----------------------------
# PARSE TIMESTAMP
# -----------------------------
df[time_col] = pd.to_datetime(df[time_col], errors="coerce")

# -----------------------------
# DROP INVALID ROWS
# -----------------------------
df = df.dropna(subset=[time_col, speed_col])

# -----------------------------
# REMOVE IMPOSSIBLE SPEEDS
# -----------------------------
df = df[(df[speed_col] >= 0) & (df[speed_col] <= 130)]

# -----------------------------
# SORT BY TIME
# -----------------------------
df = df.sort_values(time_col)

print("After cleaning shape:", df.shape)

# -----------------------------
# SAVE CLEAN DATA
# -----------------------------
df.to_csv(OUTPUT_FILE, index=False)
print("Saved cleaned data to:", OUTPUT_FILE)
