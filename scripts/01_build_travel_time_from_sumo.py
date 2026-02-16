from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET

EDGE_XML = Path("sim/outputs/edge_data.xml")
NET_XML  = Path("sim/network/auckland.net.xml")

OUT_RAW_DIR = Path("data_raw/SUMO")
OUT_RAW_DIR.mkdir(parents=True, exist_ok=True)

OUT_PROC_DIR = Path("data_processed/travel_time")
OUT_PROC_DIR.mkdir(parents=True, exist_ok=True)

OUT_EDGE_1MIN = OUT_RAW_DIR / "edge_1min_raw.csv"
OUT_TT_10MIN  = OUT_PROC_DIR / "travel_time_10min.csv"

def load_edge_lengths(net_xml: Path) -> dict:
    """Read edge lengths from SUMO network file."""
    root = ET.parse(net_xml).getroot()
    lengths = {}
    for edge in root.findall("edge"):
        edge_id = edge.attrib.get("id")
        # internal edges start with ":"; ignore them
        if not edge_id or edge_id.startswith(":"):
            continue
        lane = edge.find("lane")
        if lane is None:
            continue
        length = lane.attrib.get("length")
        if length is None:
            continue
        lengths[edge_id] = float(length)
    return lengths

def parse_edge_data(edge_xml: Path) -> pd.DataFrame:
    """Parse edgeData output. Capture speed and traveltime if present."""
    root = ET.parse(edge_xml).getroot()
    rows = []
    for interval in root.findall("interval"):
        begin = float(interval.attrib["begin"])
        end = float(interval.attrib["end"])
        for edge in interval.findall("edge"):
            edge_id = edge.attrib.get("id")
            if not edge_id or edge_id.startswith(":"):
                continue
            rows.append({
                "begin_sec": begin,
                "end_sec": end,
                "edge_id": edge_id,
                "speed_mps": float(edge.attrib.get("speed", 0)),
                # traveltime may or may not exist depending on SUMO output
                "traveltime_sec": float(edge.attrib.get("traveltime", "nan")) if "traveltime" in edge.attrib else float("nan"),
            })
    return pd.DataFrame(rows)

def main():
    print("Loading edge lengths from:", NET_XML)
    lengths = load_edge_lengths(NET_XML)
    print("Loaded lengths for edges:", len(lengths))

    print("Parsing edge data from:", EDGE_XML)
    df = parse_edge_data(EDGE_XML)
    print("Parsed rows:", df.shape)

    # Save raw 1-min CSV
    df.to_csv(OUT_EDGE_1MIN, index=False)
    print("Saved:", OUT_EDGE_1MIN)

    # Attach length from net.xml
    df["length_m"] = df["edge_id"].map(lengths)

    # Compute travel time:
    # If SUMO provides traveltime, use it. Otherwise compute length/speed.
    use_tt_direct = df["traveltime_sec"].notna().any()
    if use_tt_direct:
        df["travel_time_sec"] = df["traveltime_sec"]
        print("Using traveltime_sec directly from edge_data.xml")
    else:
        # compute from length/speed
        df = df.dropna(subset=["length_m"])
        df = df[df["speed_mps"] > 0]
        df["travel_time_sec"] = df["length_m"] / df["speed_mps"]
        print("Computed travel_time_sec = length_m / speed_mps")

    # Build datetime index from sim seconds
    df["time"] = pd.to_datetime(df["begin_sec"], unit="s")

    # Aggregate to 10-minute mean travel time per edge
    df_10 = (
        df.set_index("time")
          .groupby("edge_id")
          .resample("10min")["travel_time_sec"]
          .mean()
          .reset_index()
    )

    df_10.to_csv(OUT_TT_10MIN, index=False)
    print("Saved 10-min travel time:", OUT_TT_10MIN)
    print("travel_time_10min shape:", df_10.shape)
    print(df_10.head(5))

if __name__ == "__main__":
    main()
