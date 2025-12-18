\# Research Diary – MSc Thesis

Author: Vivek Tollawala  

Project: Dynamic Congestion Pricing using AI (Auckland)



---



\## 2025-12-18

\*\*Task:\*\* Thesis workspace setup  

\*\*Actions:\*\*

\- Created folder structure

\- Defined data, models, simulation, and results directories



\*\*Notes:\*\*

\- No experiments run yet



\*\*Next Step:\*\*

\- Start Auckland Transport API data collection


## 2025-12-18
**Task:** Locked thesis scope (Step 2)

**Decisions:**
- Target variable: Average traffic speed (km/h)
- Prediction horizon: 15 minutes ahead
- Time resolution: 5-minute intervals
- Study area: SH1, SH16, and one CBD arterial corridor
- Models: ARIMA (baseline), XGBoost, LSTM
- Evaluation metrics: RMSE, MAE, inference latency
- Data split: Chronological (70% train / 15% validation / 15% test)

**Reasoning:**
- Scope chosen to balance realism, feasibility, and academic rigour


## 2025-12-18
**Task:** Started Step 3 – Data acquisition setup

**Actions:**
- Defined AT Open Data and SUMO as data sources
- Fixed 8-week data window
- Created Python environment
- Prepared AT data download script template

**Next Step:**
- Identify exact AT Open Data API endpoint for traffic speed


## 2025-12-18
**Task:** Auckland Transport traffic data acquisition

**Source:**
- Data.govt.nz – Auckland Transport traffic speed dataset

**Format:**
- CSV
- 5-minute intervals
- Variables include timestamp, road segment ID, and speed (km/h)

**Storage:**
- data_raw/AT_API/traffic_speed_raw.csv

**Notes:**
- Dataset verified and readable in Python



