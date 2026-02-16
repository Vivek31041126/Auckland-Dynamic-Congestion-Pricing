"""
01_data_pull_at_traveltime.py

Purpose:
- Pull Auckland Transport travel time data (raw) and save into /data_raw/AT_API/travel_time/
- Keep raw dumps unchanged for research reproducibility

Notes:
- You must add your AT API endpoint + key (if required)
"""

from pathlib import Path
from datetime import datetime
import json
import requests

OUT_DIR = Path("data_raw/AT_API/travel_time")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def save_raw_json(payload: dict, prefix: str = "AT_travel_time"):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_file = OUT_DIR / f"{prefix}_{ts}_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Saved: {out_file}")

def main():
    # TODO: Replace with the correct AT endpoint for travel time
    url = "PASTE_AT_TRAVEL_TIME_ENDPOINT_HERE"

    # TODO: If your endpoint requires a subscription key, put it here
    headers = {
        # "Ocp-Apim-Subscription-Key": "PASTE_YOUR_KEY_HERE"
    }

    r = requests.get(url, headers=headers, timeout=60)
    r.raise_for_status()

    payload = r.json()
    save_raw_json(payload)

if __name__ == "__main__":
    main()
