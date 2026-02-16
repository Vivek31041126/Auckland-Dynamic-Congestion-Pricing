from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET

XML_FILE = Path("sim/outputs/edge_data.xml")
OUT_DIR = Path("data_raw/SUMO")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "edge_1min_raw.csv"

rows = []

root = ET.parse(XML_FILE).getroot()

for interval in root.findall("interval"):
    t_begin = float(interval.attrib["begin"])  # seconds
    t_end = float(interval.attrib["end"])      # seconds

    for edge in interval.findall("edge"):
        # Not all attributes exist in every SUMO output, so use .get()
        rows.append({
            "begin_sec": t_begin,
            "end_sec": t_end,
            "edge_id": edge.attrib.get("id"),
            "speed_mps": float(edge.attrib.get("speed", 0)),
            "density": float(edge.attrib.get("density", 0)) if edge.attrib.get("density") is not None else None,
            "flow": float(edge.attrib.get("flow", 0)) if edge.attrib.get("flow") is not None else None,
            "occupancy": float(edge.attrib.get("occupancy", 0)) if edge.attrib.get("occupancy") is not None else None,
            "length_m": float(edge.attrib.get("length", 0)) if edge.attrib.get("length") is not None else None
        })

df = pd.DataFrame(rows)
df.to_csv(OUT_FILE, index=False)
print(f"Saved: {OUT_FILE}")
print(df.head())
