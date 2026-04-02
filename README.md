# Designing a Data-Driven Congestion Pricing System for Auckland Using AI

## MSc Thesis Repository

This repository contains the research code, simulation assets, datasets, results, and demonstration interfaces developed for a thesis on dynamic congestion pricing in Auckland. The study integrates traffic simulation, short-horizon travel-time forecasting, dynamic toll design, behavioural response modelling, congestion feedback analysis, an MQTT-based IoT extension, and an interactive Gradio dashboard.

## Thesis Summary

Urban congestion in Auckland imposes substantial travel-time, economic, and environmental costs. This thesis investigates whether an AI-assisted dynamic congestion pricing workflow can be developed from simulated corridor conditions, forecast near-term congestion with statistical and machine-learning models, translate those forecasts into dynamic tolls, and estimate the resulting demand and travel-time impacts. The project uses SUMO-generated traffic data, corridor-level travel-time aggregation, forecasting models including ARIMA, XGBoost, and LSTM, and a prototype decision-support interface for demonstration and analysis.

## Research Objective

The primary objective of this research is to design and evaluate an end-to-end dynamic congestion pricing framework for Auckland that:

- simulates network conditions in SUMO,
- extracts and aggregates operational travel-time data,
- forecasts short-term corridor congestion,
- converts predicted congestion into time-varying tolls,
- estimates demand reduction and congestion relief,
- demonstrates a lightweight IoT streaming extension through MQTT, and
- presents the complete workflow in a Gradio-based interactive dashboard.

## End-to-End Methodology Pipeline

```text
SUMO simulation
→ raw data extraction
→ 10-minute aggregation
→ ARIMA / XGBoost / LSTM forecasting
→ dynamic congestion pricing
→ demand response modelling
→ congestion feedback analysis
→ MQTT / IoT extension
→ Gradio demo
```

### Pipeline Description

1. **SUMO simulation**  
   Auckland network and route files are used to generate traffic conditions and edge-level outputs.

2. **Raw data extraction**  
   SUMO `edgeData` outputs are parsed into raw CSV format for reproducible downstream analysis.

3. **10-minute aggregation**  
   Edge-level traffic information is aggregated to 10-minute intervals and converted into travel-time series.

4. **Forecasting**  
   Corridor travel time is modelled using ARIMA, XGBoost, and LSTM approaches.

5. **Dynamic congestion pricing**  
   Predicted travel time is transformed into a congestion index and a corresponding time-varying toll.

6. **Demand response modelling**  
   Short-run elasticity is used to estimate demand reduction under different toll levels.

7. **Congestion feedback analysis**  
   Demand reduction is translated into adjusted travel-time outcomes through a congestion feedback factor.

8. **MQTT / IoT extension**  
   Travel-time messages are published and subscribed through a local MQTT broker to demonstrate a simple streaming architecture.

9. **Gradio demo**  
   An interactive dashboard presents datasets, metrics, pricing scenarios, and MQTT monitoring.

## Folder Structure

```text
.
├── README.md
├── requirements.txt
├── .gitignore
├── .gitattributes
├── app/                    # Clean dashboard entry point
├── Gradio/                 # Original dashboard code preserved for compatibility
├── data_raw/
│   ├── AT_API/
│   └── SUMO/
├── data_processed/
│   ├── corridor/
│   ├── splits/
│   └── travel_time/
├── scripts/
│   ├── preprocessing/      # Organised wrappers
│   ├── modelling/          # Organised wrappers
│   ├── pricing/            # Original pricing scripts + organised wrappers
│   ├── mqtt/               # Organised MQTT wrappers
│   ├── final/              # Original export scripts
│   └── utils/
├── iot_db/                 # Original MQTT scripts preserved for compatibility
├── sim/
│   ├── network/
│   ├── outputs/
│   ├── routes/
│   └── scenarios/
├── results/
│   ├── figures/
│   ├── final_pack/
│   ├── metrics/
│   ├── pricing/
│   └── tables/
├── docs/
│   ├── architecture/
│   ├── screenshots/
│   ├── thesis_notes/
│   └── repository_cleanup_report.md
├── thesis/
│   ├── chapters/
│   └── final_document/
├── archive/
│   ├── duplicate_files/
│   ├── old_scripts/
│   └── unused_outputs/
└── pricing_utils.py        # Original shared utility preserved for compatibility
```

## Datasets

### Raw Dataset

- `data_raw/SUMO/edge_1min_raw.csv`  
  Raw 1-minute edge-level traffic output derived from SUMO simulation.

- `data_raw/AT_API/traffic_counts/auckland_traffic_counts_raw.csv`  
  Auckland Transport traffic-count dataset retained as supporting contextual data.

### Cleaned Dataset

- `data_processed/travel_time/travel_time_10min.csv`  
  Cleaned 10-minute edge-level travel-time dataset.

- `data_processed/travel_time/travel_time_10min_labeled_10min.csv`  
  Edge-level supervised dataset for 10-minute-ahead prediction.

- `data_processed/travel_time/travel_time_10min_labeled_15min.csv`  
  Edge-level supervised dataset for 15-minute-ahead prediction.

### Corridor Dataset

- `data_processed/travel_time/corridor_travel_time_10min.csv`  
  Corridor-level 10-minute travel-time series.

- `data_processed/travel_time/corridor_travel_time_10min_labeled.csv`  
  Corridor-level labelled forecasting dataset.

- `data_processed/travel_time/corridor_xgb_features.csv`  
  Feature-engineered dataset for XGBoost modelling.

- `data_processed/travel_time/corridor_lstm.npz`  
  Sequence dataset for LSTM training.

### Train / Validation / Test Datasets

- `data_processed/splits/` is the designated location for exported train, validation, and test split files.
- In the current thesis workflow, chronological splits are primarily implemented directly within the modelling scripts.
- This preserves reproducibility while allowing split artefacts to be exported separately when needed for reporting or future experiments.

## Models

### ARIMA

ARIMA is used as the statistical baseline for corridor-level travel-time forecasting. It provides an interpretable benchmark for short-horizon temporal prediction.

### XGBoost

XGBoost is used as a supervised machine-learning model on lagged corridor features and simple time-based predictors. It tests whether tree-based learning can capture non-linear travel-time patterns more effectively than the statistical baseline.

### LSTM

LSTM is used as a sequence model for corridor-level travel-time forecasting. It is designed to capture temporal dependencies across rolling 10-minute input windows.

## Key Results

### Forecasting Performance

| Model | MAE (sec) | RMSE (sec) |
|-------|-----------:|------------:|
| ARIMA | 0.19 | 0.25 |
| XGBoost | 0.25 | 0.33 |
| LSTM | 0.19 | 0.25 |

### Dynamic Pricing and Feedback Outcomes

| Metric | Value |
|--------|------:|
| Tolled intervals | 69.6% |
| Average toll | NZD 2.66 |
| Revenue proxy | NZD 529.47 |
| Average demand reduction | 3.70% |
| Maximum demand reduction | 12.00% |
| Average travel-time reduction | 2.96% |
| Maximum travel-time reduction | 9.60% |

These results indicate that ARIMA and LSTM achieved the strongest forecasting accuracy on the corridor series, while the dynamic pricing module produced measurable demand reduction and modest travel-time relief under the assumed elasticity and congestion feedback settings.

## Demo

### Gradio App

The Gradio interface provides:

- project overview and headline metrics,
- model and pricing results,
- scenario exploration for toll parameter changes,
- data preview for raw and processed datasets, and
- MQTT demo status monitoring.

Recommended launch entry point:

```powershell
.\.venv\Scripts\python.exe .\app\gradio_app.py
```

Legacy compatibility entry point retained:

```powershell
.\.venv\Scripts\python.exe .\Gradio\app.py
```

### MQTT Publisher / Subscriber Demo

The MQTT extension demonstrates a lightweight IoT-style streaming workflow in which travel-time values are published and consumed locally.

Recommended launch commands:

```powershell
.\.venv\Scripts\python.exe .\scripts\mqtt\mqtt_subscriber.py
.\.venv\Scripts\python.exe .\scripts\mqtt\mqtt_publisher.py
```

Legacy compatibility commands retained:

```powershell
.\.venv\Scripts\python.exe .\iot_db\mqtt_subscriber.py
.\.venv\Scripts\python.exe .\iot_db\mqtt_publisher.py
```

## Screenshots

Representative dashboard screenshots are shown below. These can be replaced with updated captures as the interface evolves.

![Main Dashboard](docs/screenshots/Auckland_Congestion_Pricing_Dashboard.png)

![Scenario Explorer](docs/screenshots/Scenario_Explorer_Dashboard.png)

![MQTT Demo](docs/screenshots/Mqtt_Demo_Dashboard.png)

## Setup Instructions

### Prerequisites

- Python 3.x
- Git LFS for large CSV, XML, NPZ, and PNG assets
- SUMO, if simulation outputs need to be regenerated
- A local MQTT broker such as Mosquitto for the IoT demo

### Environment Setup

```powershell
git clone <repository-url>
cd MSc_Thesis_Auckland_Congestion
git lfs install
git lfs pull
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run Instructions

### 1. Launch the Gradio Dashboard

```powershell
.\.venv\Scripts\python.exe .\app\gradio_app.py
```

The dashboard should be available at:

```text
http://127.0.0.1:7860/
```

### 2. Run the MQTT Demo

Start a local MQTT broker on `localhost:1883`, then run:

```powershell
.\.venv\Scripts\python.exe .\scripts\mqtt\mqtt_subscriber.py
.\.venv\Scripts\python.exe .\scripts\mqtt\mqtt_publisher.py
```

### 3. Re-run the Research Pipeline

If you wish to regenerate datasets and results, the original thesis scripts remain available under the legacy `scripts/` layout, while grouped wrapper commands are also available under:

- `scripts/preprocessing/`
- `scripts/modelling/`
- `scripts/pricing/`

## Future Work

- replace simplified one-step proxy pricing inputs with full rolling forecasts,
- export dedicated train, validation, and test split artefacts for reproducible benchmark comparison,
- incorporate richer real-world Auckland time-series inputs beyond supporting traffic-count context,
- evaluate additional predictive models and uncertainty-aware pricing strategies,
- extend the MQTT layer to a distributed deployment setting, and
- test policy sensitivity under alternative elasticity and congestion-feedback assumptions.

## Author and Supervisor

**Author:** Vivek Tollawala  
**Supervisor:** Dr. Prakash Karn
