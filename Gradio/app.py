from __future__ import annotations

import json
import socket
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

import gradio as gr
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from iot_db.mqtt_status import BROKER_HOST, BROKER_PORT, MQTT_TOPIC, PUBLISH_SOURCE_CSV, read_all_statuses
from pricing_utils import TollParameters, calculate_congestion_index_and_toll


CSS = """
:root {
  --page-bg: linear-gradient(180deg, #f3efe3 0%, #f8f6ef 45%, #eef6f4 100%);
  --panel-bg: rgba(255, 255, 255, 0.86);
  --panel-border: rgba(15, 59, 58, 0.12);
  --headline: #163635;
  --body: #2d4341;
  --muted: #647876;
  --teal: #146a6a;
  --teal-soft: #dff2ee;
  --amber: #d1881f;
  --amber-soft: #fff1d8;
  --coral: #c35d43;
  --shadow: 0 18px 45px rgba(22, 54, 53, 0.08);
}

body, .gradio-container {
  background: var(--page-bg) !important;
  color: var(--body);
}

.gradio-container {
  max-width: 1260px !important;
}

.hero {
  padding: 28px 30px;
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgba(209, 136, 31, 0.16), transparent 28%),
    linear-gradient(140deg, rgba(20, 106, 106, 0.96), rgba(17, 86, 98, 0.88));
  color: #fefcf8;
  box-shadow: var(--shadow);
}

.hero h1 {
  margin: 0 0 10px 0;
  font-size: 2.3rem;
  line-height: 1.05;
}

.hero p {
  margin: 0;
  font-size: 1.04rem;
  line-height: 1.6;
  max-width: 850px;
}

.section-note {
  color: var(--muted);
  font-size: 0.96rem;
  margin-top: 4px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.metric-card {
  background: var(--panel-bg);
  backdrop-filter: blur(8px);
  border: 1px solid var(--panel-border);
  border-radius: 20px;
  padding: 18px;
  box-shadow: var(--shadow);
}

.metric-label {
  color: var(--muted);
  display: block;
  font-size: 0.9rem;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-value {
  color: var(--headline);
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 6px;
}

.metric-detail {
  color: var(--body);
  font-size: 0.95rem;
}

.insight-panel {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 20px;
  padding: 18px 20px;
  box-shadow: var(--shadow);
}

.insight-panel h3 {
  margin: 0 0 10px 0;
  color: var(--headline);
}

.pill {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  margin-right: 8px;
  margin-bottom: 8px;
  font-size: 0.88rem;
  font-weight: 600;
}

.pill.teal {
  background: var(--teal-soft);
  color: var(--teal);
}

.pill.amber {
  background: var(--amber-soft);
  color: #8a5a0f;
}

.pill.coral {
  background: #f9e0da;
  color: var(--coral);
}
"""


DEFAULT_SCENARIO = {
    "freeflow_quantile": 0.05,
    "ci_free": 1.10,
    "ci_mid": 1.30,
    "ci_severe": 1.60,
    "toll_min": 1.00,
    "toll_mid": 3.00,
    "toll_cap": 6.00,
    "elasticity": -0.10,
    "base_cost": 5.00,
    "alpha": 0.80,
}


def _discover_csv_dataset_map(root_relative: str) -> dict[str, str]:
    root = PROJECT_ROOT / root_relative
    dataset_map: dict[str, str] = {}
    for path in sorted(root.rglob("*.csv")):
        label = path.relative_to(root).as_posix()
        dataset_map[label] = path.relative_to(PROJECT_ROOT).as_posix()
    return dataset_map


RAW_DATASETS = _discover_csv_dataset_map("data_raw")
CLEAN_DATASETS = _discover_csv_dataset_map("data_processed")


def _csv_path(relative_path: str) -> Path:
    path = PROJECT_ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return path


def _read_csv(relative_path: str) -> pd.DataFrame:
    df = pd.read_csv(_csv_path(relative_path))
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce", dayfirst=True)
    return df


@lru_cache(maxsize=1)
def load_project_data() -> dict[str, pd.DataFrame]:
    return {
        "model_metrics": _read_csv("results/final_pack/model_metrics.csv"),
        "pricing_metrics": _read_csv("results/final_pack/pricing_metrics.csv"),
        "pricing": _read_csv("results/pricing/pricing_schedule_arima.csv"),
        "demand": _read_csv("results/pricing/demand_response.csv"),
        "feedback": _read_csv("results/pricing/feedback_adjusted_travel_time.csv"),
        "corridor_labeled": _read_csv("data_processed/travel_time/corridor_travel_time_10min_labeled.csv"),
    }


def _format_clock(series: pd.Series) -> pd.Series:
    return series.dt.strftime("%H:%M")


def _format_currency(value: float) -> str:
    return f"NZ${value:,.2f}"


def _format_percent(value: float) -> str:
    return f"{value:.1f}%"


def _format_file_size(num_bytes: int) -> str:
    if num_bytes < 1024:
        return f"{num_bytes} B"
    if num_bytes < 1024 * 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes / (1024 * 1024):.2f} MB"


def _round_table(df: pd.DataFrame, numeric_digits: int = 3) -> pd.DataFrame:
    rounded = df.copy()
    for column in rounded.select_dtypes(include="number").columns:
        rounded[column] = rounded[column].round(numeric_digits)
    return rounded


def _make_card(label: str, value: str, detail: str) -> str:
    return f"""
    <div class="metric-card">
      <span class="metric-label">{label}</span>
      <div class="metric-value">{value}</div>
      <div class="metric-detail">{detail}</div>
    </div>
    """


@lru_cache(maxsize=64)
def _load_preview_csv(relative_path: str, preview_rows: int) -> pd.DataFrame:
    return pd.read_csv(_csv_path(relative_path), nrows=preview_rows)


@lru_cache(maxsize=64)
def _load_dataset_metadata(relative_path: str) -> dict[str, object]:
    path = _csv_path(relative_path)
    columns = pd.read_csv(path, nrows=0).columns.tolist()
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        row_count = max(sum(1 for _ in handle) - 1, 0)
    return {
        "path": relative_path,
        "rows": row_count,
        "columns": columns,
        "column_count": len(columns),
        "size": _format_file_size(path.stat().st_size),
    }


def _build_dataset_summary(title: str, relative_path: str, preview_rows: int) -> str:
    metadata = _load_dataset_metadata(relative_path)
    columns = metadata["columns"]
    visible_columns = ", ".join(f"<code>{column}</code>" for column in columns[:8])
    if len(columns) > 8:
        visible_columns += f", and {len(columns) - 8} more"

    return f"""
    <div class="insight-panel">
      <h3>{title}</h3>
      <p><strong>Path:</strong> <code>{metadata["path"]}</code></p>
      <p><strong>Shape:</strong> {metadata["rows"]:,} rows x {metadata["column_count"]} columns</p>
      <p><strong>File size:</strong> {metadata["size"]}</p>
      <p><strong>Columns:</strong> {visible_columns}</p>
      <p class="section-note">Showing the first {preview_rows} rows below.</p>
    </div>
    """


def _dataset_preview(dataset_label: str, dataset_map: dict[str, str], section_title: str, preview_rows: int) -> tuple[str, pd.DataFrame]:
    relative_path = dataset_map[dataset_label]
    summary = _build_dataset_summary(section_title, relative_path, int(preview_rows))
    preview_df = _load_preview_csv(relative_path, int(preview_rows))
    return summary, preview_df


def update_raw_dataset_preview(dataset_label: str, preview_rows: int) -> tuple[str, pd.DataFrame]:
    return _dataset_preview(dataset_label, RAW_DATASETS, "Raw Dataset", preview_rows)


def update_clean_dataset_preview(dataset_label: str, preview_rows: int) -> tuple[str, pd.DataFrame]:
    return _dataset_preview(dataset_label, CLEAN_DATASETS, "Clean Dataset", preview_rows)


def build_overview_cards() -> str:
    data = load_project_data()
    pricing_metrics = data["pricing_metrics"].iloc[0]
    model_metrics = data["model_metrics"].copy()
    best_model = model_metrics.sort_values(["RMSE_sec", "MAE_sec"]).iloc[0]

    cards = [
        _make_card(
            "Tolled Intervals",
            f"{int(pricing_metrics['tolled_intervals'])} / {int(pricing_metrics['total_intervals'])}",
            f"{_format_percent(pricing_metrics['tolled_pct'])} of 10-minute periods received a toll.",
        ),
        _make_card(
            "Average Applied Toll",
            _format_currency(pricing_metrics["avg_toll_when_applied_nzd"]),
            f"Peak: {_format_currency(pricing_metrics['avg_peak_toll_nzd'])} | Off-peak: {_format_currency(pricing_metrics['avg_offpeak_toll_nzd'])}",
        ),
        _make_card(
            "Revenue Proxy",
            _format_currency(pricing_metrics["revenue_proxy_nzd"]),
            "Proxy based on the saved pricing schedule in the repo.",
        ),
        _make_card(
            "Demand Reduction",
            _format_percent(pricing_metrics["avg_demand_reduction_pct"]),
            f"Best observed reduction: {_format_percent(pricing_metrics['max_demand_reduction_pct'])}",
        ),
        _make_card(
            "Travel-Time Relief",
            _format_percent(pricing_metrics["avg_travel_time_reduction_pct"]),
            f"Maximum observed relief: {_format_percent(pricing_metrics['max_travel_time_reduction_pct'])}",
        ),
        _make_card(
            "Best Saved Model",
            best_model["model"],
            f"RMSE {best_model['RMSE_sec']:.2f}, MAE {best_model['MAE_sec']:.2f} for the {best_model['horizon']} horizon.",
        ),
    ]
    return f'<div class="card-grid">{"".join(cards)}</div>'


def build_overview_insights() -> str:
    pricing_metrics = load_project_data()["pricing_metrics"].iloc[0]
    return f"""
    <div class="insight-panel">
      <h3>What the saved thesis run shows</h3>
      <div>
        <span class="pill teal">Dynamic tolling used in {_format_percent(pricing_metrics["tolled_pct"])} of intervals</span>
        <span class="pill amber">Average toll when active: {_format_currency(pricing_metrics["avg_toll_when_applied_nzd"])}</span>
        <span class="pill coral">Average travel-time improvement: {_format_percent(pricing_metrics["avg_travel_time_reduction_pct"])}</span>
      </div>
      <p>
        This app uses your saved corridor travel-time series, ARIMA-based toll schedule,
        demand response, and feedback-adjusted travel times. The scenario tab lets you
        stress-test the same policy logic with different toll thresholds, elasticity, and
        congestion sensitivity.
      </p>
    </div>
    """


def _format_status_timestamp(value: object) -> str:
    if value in (None, "", "NaT"):
        return "Not available"

    timestamp = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(timestamp):
        return str(value)
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")


def _probe_broker(host: str, port: int, timeout_seconds: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except OSError:
        return False


def _status_detail(status: dict[str, object]) -> str:
    message_count = int(status.get("message_count") or 0)
    updated_at = _format_status_timestamp(status.get("updated_at"))
    return f"{message_count} messages tracked | Updated: {updated_at}"


def build_mqtt_demo_snapshot() -> tuple[str, pd.DataFrame, pd.DataFrame]:
    broker_online = _probe_broker(BROKER_HOST, BROKER_PORT)
    statuses = read_all_statuses()
    publisher = statuses["publisher"]
    subscriber = statuses["subscriber"]

    summary_html = f"""
    <div class="card-grid">
      {_make_card("Broker", "Online" if broker_online else "Offline", f"{BROKER_HOST}:{BROKER_PORT}")}
      {_make_card("Topic", MQTT_TOPIC, "Shared topic for the demo publisher and subscriber.")}
      {_make_card("Publisher", str(publisher["state"]).replace("_", " ").title(), _status_detail(publisher))}
      {_make_card("Subscriber", str(subscriber["state"]).replace("_", " ").title(), _status_detail(subscriber))}
    </div>
    """

    status_rows = []
    payload_rows = []
    for component in ("publisher", "subscriber"):
        status = statuses[component]
        status_rows.append(
            {
                "component": component,
                "state": status.get("state", "unknown"),
                "messages": int(status.get("message_count") or 0),
                "updated_at": _format_status_timestamp(status.get("updated_at")),
                "last_message_time": status.get("last_message_time") or "Not available",
                "last_error": status.get("last_error") or "",
                "status_file": (PROJECT_ROOT / "iot_db" / "mqtt" / "status" / f"{component}_status.json").relative_to(PROJECT_ROOT).as_posix(),
            }
        )

        payload = status.get("last_payload")
        payload_rows.append(
            {
                "component": component,
                "broker": f"{status.get('broker_host', BROKER_HOST)}:{status.get('broker_port', BROKER_PORT)}",
                "topic": status.get("subscribed_topic") or status.get("topic") or MQTT_TOPIC,
                "source_csv": status.get("source_csv") or "Not applicable",
                "last_payload": "No payload yet" if not payload else json.dumps(payload, indent=2),
            }
        )

    return summary_html, pd.DataFrame(status_rows), pd.DataFrame(payload_rows)


def _style_time_axis(ax) -> None:
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)
        tick.set_ha("right")


def make_toll_plot(df: pd.DataFrame, title: str) -> Figure:
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(df["time"], df["toll_nzd"], color="#d1881f", linewidth=2.6)
    ax.fill_between(df["time"], df["toll_nzd"], color="#f4c87a", alpha=0.35)
    ax.set_title(title, fontsize=14, pad=12)
    ax.set_ylabel("Toll (NZD)")
    ax.set_xlabel("Time of day")
    ax.grid(alpha=0.22)
    ax.spines[["top", "right"]].set_visible(False)
    _style_time_axis(ax)
    fig.tight_layout()
    return fig


def make_feedback_plot(df: pd.DataFrame, title: str) -> Figure:
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(df["time"], df["corridor_travel_time_sec"], color="#d35f43", linewidth=2.2, label="Original")
    ax.plot(df["time"], df["adjusted_travel_time_sec"], color="#146a6a", linewidth=2.4, label="After pricing")
    ax.set_title(title, fontsize=14, pad=12)
    ax.set_ylabel("Travel time")
    ax.set_xlabel("Time of day")
    ax.grid(alpha=0.22)
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    _style_time_axis(ax)
    fig.tight_layout()
    return fig


def make_demand_plot(df: pd.DataFrame, title: str) -> Figure:
    fig, ax1 = plt.subplots(figsize=(10, 4.2))
    ax2 = ax1.twinx()

    ax1.plot(df["time"], df["toll_nzd"], color="#d1881f", linewidth=2.5, label="Toll")
    ax2.plot(df["time"], -df["demand_change_pct"] * 100, color="#146a6a", linewidth=2.2, label="Demand reduction")

    ax1.set_title(title, fontsize=14, pad=12)
    ax1.set_xlabel("Time of day")
    ax1.set_ylabel("Toll (NZD)", color="#8a5a0f")
    ax2.set_ylabel("Demand reduction (%)", color="#146a6a")
    ax1.grid(alpha=0.18)
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    _style_time_axis(ax1)

    lines = ax1.get_lines() + ax2.get_lines()
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, frameon=False, loc="upper right")

    fig.tight_layout()
    return fig


def build_saved_outputs() -> tuple[Figure, Figure, Figure, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    data = load_project_data()
    pricing_table = data["pricing"].copy()
    pricing_table["time"] = _format_clock(pricing_table["time"])
    model_table = _round_table(data["model_metrics"], numeric_digits=2)
    pricing_metrics_table = _round_table(data["pricing_metrics"], numeric_digits=2)
    return (
        make_toll_plot(data["pricing"], "Saved Dynamic Toll Schedule"),
        make_feedback_plot(data["feedback"], "Observed Travel Time vs Pricing Feedback"),
        make_demand_plot(data["demand"], "Tolling and Demand Response"),
        model_table,
        pricing_metrics_table,
        _round_table(pricing_table.head(48), numeric_digits=3),
    )


def compute_scenario(
    freeflow_quantile: float,
    ci_free: float,
    ci_mid: float,
    ci_severe: float,
    toll_min: float,
    toll_mid: float,
    toll_cap: float,
    elasticity: float,
    base_cost: float,
    alpha: float,
) -> pd.DataFrame:
    if not 0 < freeflow_quantile < 0.50:
        raise gr.Error("Free-flow quantile must be between 0 and 0.50.")
    if base_cost <= 0:
        raise gr.Error("Base generalized cost must be greater than zero.")
    if elasticity > 0:
        raise gr.Error("Elasticity should be zero or negative for a demand reduction effect.")
    if alpha < 0:
        raise gr.Error("Congestion sensitivity alpha must be zero or positive.")

    corridor = load_project_data()["corridor_labeled"].sort_values("time").reset_index(drop=True).copy()
    tt_free = corridor["corridor_travel_time_sec"].quantile(freeflow_quantile)
    corridor["TT_pred_sec"] = corridor["corridor_travel_time_sec"].shift(1)
    corridor = corridor.dropna().copy()
    try:
        pricing = calculate_congestion_index_and_toll(
            corridor["TT_pred_sec"],
            tt_free,
            TollParameters(
                ci_free=ci_free,
                ci_mid=ci_mid,
                ci_severe=ci_severe,
                toll_min=toll_min,
                toll_mid=toll_mid,
                toll_cap=toll_cap,
            ),
        )
    except ValueError as exc:
        raise gr.Error(str(exc)) from exc

    corridor[["CI", "toll_nzd"]] = pricing
    corridor["price_change_pct"] = corridor["toll_nzd"] / base_cost
    corridor["demand_change_pct"] = elasticity * corridor["price_change_pct"]
    corridor["remaining_demand_factor"] = 1 + corridor["demand_change_pct"]
    corridor["adjusted_travel_time_sec"] = (
        corridor["corridor_travel_time_sec"] * (1 - alpha * (-corridor["demand_change_pct"]))
    )
    corridor["travel_time_reduction_pct"] = (
        (corridor["corridor_travel_time_sec"] - corridor["adjusted_travel_time_sec"])
        / corridor["corridor_travel_time_sec"]
    ) * 100
    return corridor


def build_scenario_summary(scenario_df: pd.DataFrame, tt_free: float) -> str:
    tolled_intervals = int((scenario_df["toll_nzd"] > 0).sum())
    total_intervals = len(scenario_df)
    avg_toll = scenario_df.loc[scenario_df["toll_nzd"] > 0, "toll_nzd"].mean()
    avg_toll = 0.0 if pd.isna(avg_toll) else float(avg_toll)
    revenue = float(scenario_df["toll_nzd"].sum())
    avg_demand_reduction = float((-scenario_df["demand_change_pct"] * 100).mean())
    avg_travel_time_relief = float(scenario_df["travel_time_reduction_pct"].mean())
    peak_hours = scenario_df["time"].dt.hour.isin([7, 8, 9, 16, 17, 18])
    peak_avg_toll = scenario_df.loc[peak_hours, "toll_nzd"].mean()
    peak_avg_toll = 0.0 if pd.isna(peak_avg_toll) else float(peak_avg_toll)

    baseline = load_project_data()["pricing_metrics"].iloc[0]
    revenue_delta = revenue - float(baseline["revenue_proxy_nzd"])
    relief_delta = avg_travel_time_relief - float(baseline["avg_travel_time_reduction_pct"])

    cards = [
        _make_card(
            "Scenario Free-Flow Baseline",
            f"{tt_free:.3f}",
            "Computed from the selected travel-time quantile.",
        ),
        _make_card(
            "Tolled Intervals",
            f"{tolled_intervals} / {total_intervals}",
            f"{_format_percent((tolled_intervals / total_intervals) * 100)} of intervals priced.",
        ),
        _make_card(
            "Average Applied Toll",
            _format_currency(avg_toll),
            f"Peak average toll: {_format_currency(peak_avg_toll)}",
        ),
        _make_card(
            "Revenue Proxy",
            _format_currency(revenue),
            f"Difference from saved run: {revenue_delta:+.2f} NZD.",
        ),
        _make_card(
            "Demand Reduction",
            _format_percent(avg_demand_reduction),
            f"Best interval: {_format_percent((-scenario_df['demand_change_pct'] * 100).max())}",
        ),
        _make_card(
            "Travel-Time Relief",
            _format_percent(avg_travel_time_relief),
            f"Difference from saved run: {relief_delta:+.2f} percentage points.",
        ),
    ]
    return f'<div class="card-grid">{"".join(cards)}</div>'


def export_scenario_csv(scenario_df: pd.DataFrame) -> str:
    export_df = scenario_df.copy()
    export_df["time"] = export_df["time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    temp_file = tempfile.NamedTemporaryFile(
        prefix="congestion_pricing_scenario_",
        suffix=".csv",
        delete=False,
    )
    export_df.to_csv(temp_file.name, index=False)
    temp_file.close()
    return temp_file.name


def run_scenario(
    freeflow_quantile: float,
    ci_free: float,
    ci_mid: float,
    ci_severe: float,
    toll_min: float,
    toll_mid: float,
    toll_cap: float,
    elasticity: float,
    base_cost: float,
    alpha: float,
) -> tuple[str, Figure, Figure, pd.DataFrame, str]:
    scenario_df = compute_scenario(
        freeflow_quantile,
        ci_free,
        ci_mid,
        ci_severe,
        toll_min,
        toll_mid,
        toll_cap,
        elasticity,
        base_cost,
        alpha,
    )
    tt_free = load_project_data()["corridor_labeled"]["corridor_travel_time_sec"].quantile(freeflow_quantile)

    display_df = scenario_df[
        [
            "time",
            "corridor_travel_time_sec",
            "TT_pred_sec",
            "CI",
            "toll_nzd",
            "demand_change_pct",
            "adjusted_travel_time_sec",
            "travel_time_reduction_pct",
        ]
    ].copy()
    display_df["time"] = _format_clock(display_df["time"])
    display_df["demand_change_pct"] = display_df["demand_change_pct"] * 100
    display_df = _round_table(display_df.head(72), numeric_digits=3)

    summary_html = build_scenario_summary(scenario_df, tt_free)
    toll_plot = make_toll_plot(scenario_df, "Scenario Toll Schedule")
    feedback_plot = make_feedback_plot(scenario_df, "Scenario Travel Time Before and After Pricing")
    export_path = export_scenario_csv(scenario_df)
    return summary_html, toll_plot, feedback_plot, display_df, export_path


def build_app() -> gr.Blocks:
    overview_cards = build_overview_cards()
    insight_panel = build_overview_insights()
    initial_mqtt_snapshot = build_mqtt_demo_snapshot()
    saved_toll_plot, saved_feedback_plot, saved_demand_plot, model_table, pricing_metrics_table, pricing_sample = build_saved_outputs()
    initial_scenario = run_scenario(**DEFAULT_SCENARIO)
    default_raw_dataset = "SUMO/edge_1min_raw.csv" if "SUMO/edge_1min_raw.csv" in RAW_DATASETS else next(iter(RAW_DATASETS))
    default_clean_dataset = "SUMO/edge_10min.csv" if "SUMO/edge_10min.csv" in CLEAN_DATASETS else next(iter(CLEAN_DATASETS))
    initial_preview_rows = 20
    initial_raw_preview = update_raw_dataset_preview(default_raw_dataset, initial_preview_rows)
    initial_clean_preview = update_clean_dataset_preview(default_clean_dataset, initial_preview_rows)

    with gr.Blocks(css=CSS, title="Auckland Congestion Pricing Dashboard") as demo:
        gr.HTML(
            """
            <section class="hero">
              <h1>Auckland Congestion Pricing Dashboard</h1>
              <p>
                Explore the saved thesis outputs and test alternative congestion pricing policies
                from the same corridor travel-time series. The app keeps your pricing workflow
                visible: free-flow baseline, congestion index, toll schedule, demand response,
                and travel-time feedback.
              </p>
            </section>
            """
        )

        with gr.Tab("Dashboard"):
            gr.HTML(overview_cards)
            gr.HTML(insight_panel)
            gr.Markdown(
                '<div class="section-note">Saved outputs are loaded directly from `results/final_pack` and `results/pricing`.</div>'
            )
            with gr.Row():
                gr.Plot(value=saved_toll_plot, label="Saved toll schedule")
                gr.Plot(value=saved_feedback_plot, label="Saved travel-time feedback")
            gr.Plot(value=saved_demand_plot, label="Saved demand response")
            with gr.Row():
                gr.Dataframe(value=model_table, label="Model metrics", interactive=False)
                gr.Dataframe(value=pricing_metrics_table, label="Pricing metrics", interactive=False)
            gr.Dataframe(value=pricing_sample, label="Saved pricing schedule sample", interactive=False)

        with gr.Tab("Scenario Explorer"):
            gr.Markdown(
                """
                Adjust the pricing thresholds and behavioural assumptions, then recompute the policy
                using the corridor travel-time series already in this repository.
                """
            )
            with gr.Row():
                with gr.Column(scale=1):
                    freeflow_quantile = gr.Slider(0.01, 0.20, value=DEFAULT_SCENARIO["freeflow_quantile"], step=0.01, label="Free-flow quantile")
                    ci_free = gr.Slider(1.00, 1.30, value=DEFAULT_SCENARIO["ci_free"], step=0.01, label="CI free threshold")
                    ci_mid = gr.Slider(1.10, 1.50, value=DEFAULT_SCENARIO["ci_mid"], step=0.01, label="CI mid threshold")
                    ci_severe = gr.Slider(1.30, 2.00, value=DEFAULT_SCENARIO["ci_severe"], step=0.01, label="CI severe threshold")
                    toll_min = gr.Slider(0.0, 4.0, value=DEFAULT_SCENARIO["toll_min"], step=0.10, label="Minimum toll (NZD)")
                    toll_mid = gr.Slider(0.0, 6.0, value=DEFAULT_SCENARIO["toll_mid"], step=0.10, label="Mid toll (NZD)")
                    toll_cap = gr.Slider(0.0, 10.0, value=DEFAULT_SCENARIO["toll_cap"], step=0.10, label="Toll cap (NZD)")
                    elasticity = gr.Slider(-0.50, 0.0, value=DEFAULT_SCENARIO["elasticity"], step=0.01, label="Demand elasticity")
                    base_cost = gr.Slider(1.0, 20.0, value=DEFAULT_SCENARIO["base_cost"], step=0.50, label="Base generalized cost (NZD)")
                    alpha = gr.Slider(0.0, 1.5, value=DEFAULT_SCENARIO["alpha"], step=0.05, label="Congestion sensitivity alpha")
                    run_button = gr.Button("Recompute scenario", variant="primary")
                    gr.Examples(
                        examples=[
                            [0.05, 1.10, 1.30, 1.60, 1.00, 3.00, 6.00, -0.10, 5.00, 0.80],
                            [0.05, 1.12, 1.35, 1.75, 0.50, 2.00, 4.00, -0.08, 6.00, 0.65],
                            [0.03, 1.08, 1.25, 1.50, 1.50, 4.00, 8.00, -0.15, 4.00, 1.00],
                        ],
                        inputs=[freeflow_quantile, ci_free, ci_mid, ci_severe, toll_min, toll_mid, toll_cap, elasticity, base_cost, alpha],
                        label="Scenario presets",
                    )
                with gr.Column(scale=2):
                    scenario_summary = gr.HTML(value=initial_scenario[0])
                    with gr.Row():
                        scenario_toll_plot = gr.Plot(value=initial_scenario[1], label="Scenario toll schedule")
                        scenario_feedback_plot = gr.Plot(value=initial_scenario[2], label="Scenario feedback")
                    scenario_table = gr.Dataframe(value=initial_scenario[3], label="Scenario output sample", interactive=False)
                    scenario_download = gr.File(value=initial_scenario[4], label="Download full scenario CSV")

            run_button.click(
                fn=run_scenario,
                inputs=[freeflow_quantile, ci_free, ci_mid, ci_severe, toll_min, toll_mid, toll_cap, elasticity, base_cost, alpha],
                outputs=[scenario_summary, scenario_toll_plot, scenario_feedback_plot, scenario_table, scenario_download],
            )

        with gr.Tab("MQTT Demo"):
            gr.Markdown(
                f"""
                Monitor the local MQTT demo for the publisher and subscriber scripts in `iot_db`.
                The page reads status snapshots written by those scripts and also checks whether the broker is reachable at `{BROKER_HOST}:{BROKER_PORT}`.
                """
            )
            mqtt_summary = gr.HTML(value=initial_mqtt_snapshot[0])
            with gr.Row():
                mqtt_refresh = gr.Button("Refresh MQTT Status", variant="primary")
            with gr.Row():
                mqtt_status_table = gr.Dataframe(value=initial_mqtt_snapshot[1], label="Component status", interactive=False)
                mqtt_payload_table = gr.Dataframe(value=initial_mqtt_snapshot[2], label="Latest payloads", interactive=False)
            gr.Markdown(
                f"""
                Run these in separate terminals:

                ```powershell
                .\\.venv\\Scripts\\python.exe .\\iot_db\\mqtt_subscriber.py
                .\\.venv\\Scripts\\python.exe .\\iot_db\\mqtt_publisher.py
                ```

                Broker: `{BROKER_HOST}:{BROKER_PORT}`
                Topic: `{MQTT_TOPIC}`
                Source stream: `{PUBLISH_SOURCE_CSV.relative_to(PROJECT_ROOT).as_posix()}`
                """
            )
            mqtt_refresh.click(
                fn=build_mqtt_demo_snapshot,
                outputs=[mqtt_summary, mqtt_status_table, mqtt_payload_table],
            )

        with gr.Tab("Data Preview"):
            gr.Markdown(
                """
                Preview source datasets from `data_raw` alongside cleaned datasets from `data_processed`.
                This tab focuses on CSV files so you can inspect the pipeline tables directly.
                """
            )
            preview_rows = gr.Slider(5, 50, value=initial_preview_rows, step=5, label="Rows to preview")
            with gr.Row():
                with gr.Column():
                    raw_dataset = gr.Dropdown(
                        choices=list(RAW_DATASETS.keys()),
                        value=default_raw_dataset,
                        label="Raw dataset",
                    )
                    raw_summary = gr.HTML(value=initial_raw_preview[0])
                    raw_table = gr.Dataframe(value=initial_raw_preview[1], label="Raw preview", interactive=False)
                with gr.Column():
                    clean_dataset = gr.Dropdown(
                        choices=list(CLEAN_DATASETS.keys()),
                        value=default_clean_dataset,
                        label="Clean dataset",
                    )
                    clean_summary = gr.HTML(value=initial_clean_preview[0])
                    clean_table = gr.Dataframe(value=initial_clean_preview[1], label="Clean preview", interactive=False)

            raw_dataset.change(
                fn=update_raw_dataset_preview,
                inputs=[raw_dataset, preview_rows],
                outputs=[raw_summary, raw_table],
            )
            clean_dataset.change(
                fn=update_clean_dataset_preview,
                inputs=[clean_dataset, preview_rows],
                outputs=[clean_summary, clean_table],
            )
            preview_rows.change(
                fn=update_raw_dataset_preview,
                inputs=[raw_dataset, preview_rows],
                outputs=[raw_summary, raw_table],
            )
            preview_rows.change(
                fn=update_clean_dataset_preview,
                inputs=[clean_dataset, preview_rows],
                outputs=[clean_summary, clean_table],
            )

        with gr.Tab("Methods"):
            gr.Markdown(
                """
                ### Workflow mirrored from the repository

                1. Use the labeled corridor travel-time series in `data_processed/travel_time/corridor_travel_time_10min_labeled.csv`.
                2. Estimate a free-flow baseline from a chosen quantile of that series.
                3. Build a congestion index as `predicted_travel_time / free_flow_travel_time`.
                4. Convert the congestion index into a toll with low, medium, and capped pricing bands.
                5. Apply elasticity to estimate demand reduction.
                6. Translate that demand reduction into travel-time relief through the congestion feedback parameter `alpha`.

                The default slider values match the assumptions in `scripts/pricing/02_price_from_arima.py`,
                `scripts/pricing/05_demand_response.py`, and `scripts/pricing/07_congestion_feedback.py`.
                """
            )

    return demo


if __name__ == "__main__":
    build_app().launch()
