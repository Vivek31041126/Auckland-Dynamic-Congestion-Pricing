from pathlib import Path
import pandas as pd

RAW_FILE = Path(""C:\Users\VIVEK\Documents\MSc_Thesis_Auckland_Congestion\data_raw\AT_API\traffic_counts\AT_traffic_counts_raw.csv.csv"")
OUT_DIR = Path("data_processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "speed_10min_clean.csv"

def main():
    df = pd.read_csv(RAW_FILE)

    # TODO: UPDATE THESE COLUMN NAMES to match your CSV
    # Common examples: timestamp, time, datetime, segment_id, link_id, speed, avg_speed
    time_col = "timestamp"
    segment_col = "segment_id"
    speed_col = "speed"

    # Convert time column to datetime
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.dropna(subset=[time_col])

    # Keep only needed columns
    df = df[[time_col, segment_col, speed_col]].copy()

    # Convert speed to numeric
    df[speed_col] = pd.to_numeric(df[speed_col], errors="coerce")
    df = df.dropna(subset=[speed_col])

    # Set index for resampling
    df = df.set_index(time_col)

    # Aggregate to 10-min intervals (mean speed per segment)
    df_10 = (
        df.groupby(segment_col)
          .resample("10min")[speed_col]
          .mean()
          .reset_index()
          .rename(columns={speed_col: "speed_mean"})
    )

    df_10.to_csv(OUT_FILE, index=False)
    print(f"Saved cleaned 10-min data: {OUT_FILE}")
    print(df_10.head(10))

if __name__ == "__main__":
    main()
