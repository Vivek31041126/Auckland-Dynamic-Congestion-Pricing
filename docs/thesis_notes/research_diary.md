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



## 2026-01-10
**Task:** Locked thesis scope
**Decisions (fixed):**
- Target: Travel time
- Resolution: 10 minutes
- Forecast horizon: 15 minutes ahead
- Corridors: SH1 + SH16 + CBD arterials

**Next Step:**
- Begin data acquisition and create raw data storage convention


## 2026-01-10
**Task:** Inspection of initial AT CSV dataset  
**Findings:**
- Dataset contains traffic count survey data (ADT, vehicle composition)
- No time-series speed or travel time information present
- Dataset unsuitable for forecasting models directly

**Decision:**
- Use this dataset for network characterisation and SUMO calibration
- Separate time-series travel time data will be collected for prediction tasks

**Next Step:**
- Acquire time-stamped travel time or speed data from AT Open Data


## 2026-01-10
**Task:** Assessment of available datasets
**Decision:**
- Initial CSV contained traffic count survey data only
- Time-series travel time data not yet available

**Planned Action:**
- Acquire timestamped traffic speed data from AT / NZ Open Data
- Derive travel time at 10-minute resolution for forecasting

**Justification:**
- Required for ARIMA, XGBoost, and LSTM modelling


**Issue resolved:**
- PowerShell line continuation corrected (CMD caret ^ replaced with PowerShell syntax)


**SUMO fix:**
- Configured edgeData output via additional file (edgeData.add.xml) referenced in normal.sumocfg
- Generated edge_data.xml with 60-second frequency

## 2026-01-10
**Task:** Convert SUMO 1-min edge output to 10-min travel time dataset
**Actions:**
- Parsed edge_data.xml into 1-minute CSV
- Aggregated to 10-minute features (speed, flow, density)
- Computed travel time from length and speed
- Created 15-minute-ahead labels using linear interpolation

**Outputs:**
- data_processed/travel_time/travel_time_10min_labeled_15min.csv

**Fix applied:**
- travel_time_10min was empty because edge lengths were not present in edge_data.xml
- extracted edge lengths from auckland.net.xml and recomputed travel time correctly


## 2026-01-10
**Task:** SUMO travel time dataset validated
**Outcome:**
- travel_time_10min.csv successfully generated (15851 rows)
- Ready for label generation and baseline forecasting models (ARIMA)


## 2026-01-10
**Modelling decision update:**
- Individual edges did not have sufficient temporal coverage for ARIMA
- Shifted modelling unit from edge-level to corridor-level travel time
- Corridor constructed from top 20 most active edges

**Justification:**
- Corridor-level modelling aligns with congestion pricing policy design
- Provides stable, continuous time series suitable for statistical forecasting

## 2026-01-10
**Task:** Corrected SUMO simulation duration and dataset generation
**Outcome:**
- SUMO edge output successfully generated for full 48-hour period
- travel_time_10min dataset now spans 48h (00:00 → 23:50) with 1,578,816 rows
- Dataset is now suitable for forecasting experiments and evaluation


## 2026-01-10
**Milestone achieved:** Valid ARIMA baseline

**Details:**
- Corridor-level travel time series constructed (48h, 10-min resolution)
- Final dataset size: 287 samples
- Train/Test split: 80/20
- ARIMA(1,1,1) baseline established

**Results:**
- MAE: 0.19 seconds
- RMSE: 0.25 seconds

**Significance:**
- Confirms correctness of SUMO data pipeline
- Provides statistical baseline for ML comparison


## 2026-01-10
**Task:** XGBoost corridor-level forecasting
**Results:**
- XGBoost MAE: 0.25 sec
- XGBoost RMSE: 0.33 sec

**Observation:**
- ARIMA outperformed XGBoost on corridor-level travel time
- Indicates high temporal smoothness and limited non-linear structure

**Conclusion:**
- ARIMA selected as best-performing model for corridor-level baseline

## 2026-01-10
**Task:** LSTM corridor-level forecasting
**Results:**
- LSTM MAE: 0.19 sec
- LSTM RMSE: 0.25 sec

**Comparison:**
- ARIMA and LSTM achieved equivalent performance
- XGBoost underperformed relative to both

**Conclusion:**
- Corridor-level aggregation favours statistical and recurrent models
- Model complexity must be balanced against signal characteristics

## 2026-01-29
**Task:** Start dynamic congestion pricing module
**Next:** Define pricing rule + compute toll from predicted travel time


## 2026-01-29
**Task:** Implemented dynamic congestion pricing logic

**Details:**
- Estimated free-flow travel time using 5th percentile (TT_free ≈ 1.31 sec)
- Computed congestion index (CI = TT_pred / TT_free)
- Implemented piecewise toll function with cap

**Outcome:**
- Pricing schedule generated at 10-minute resolution
- Toll activates only during congested periods

## 2026-01-29
**Task:** Dynamic pricing evaluation

**Results:**
- 69.6% of intervals tolled
- Avg toll when active: $2.66
- Revenue proxy: $529.47
- Off-peak average toll exceeded peak average

**Insight:**
- Dynamic pricing captures residual congestion beyond fixed peak definitions

## 2026-01-29
**Task:** Behavioural response modelling

**Assumption:**
- Short-run price elasticity of demand = −0.10

**Results:**
- Average demand reduction: 3.70%
- Maximum demand reduction: 12.00%

**Interpretation:**
- Pricing primarily redistributes demand rather than suppressing travel


## 2026-01-29
**Task:** Congestion pricing feedback analysis

**Results:**
- Average travel time reduction: 2.96%
- Maximum travel time reduction: 9.60%

**Conclusion:**
- Demand reduction induced by pricing leads to measurable congestion relief
- Feedback mechanism demonstrates systemic effectiveness of dynamic pricing


## 2026-03-19
**Task:** IoT communication layer implementation using MQTT
 
**Actions:**
-Installed and configured Mosquitto MQTT broker locally
-Ran MQTT broker in VS Code terminal using verbose mode
-Implemented MQTT publisher script to stream traffic travel-time data
-Implemented MQTT subscriber script to receive real-time messages
-Integrated processed dataset (travel_time_10min.csv) into publisher
-Configured topic-based communication: traffic/auckland/corridor
-Converted messages into structured JSON format
-Simulated real-time streaming using time delay (1 second interval)

**Issues resolved:**
-Fixed missing file path error for dataset loading
-Resolved column mismatch (corridor_travel_time_sec vs travel_time_sec)
-Added dynamic column detection logic in publisher script
-Verified correct data transmission between publisher and subscriber

**Outcome::**
-Successfully established real-time publish–subscribe communication
-Traffic data streamed continuously from publisher to subscriber
-Validated working IoT-style data pipeline for traffic monitoring

**Significance:::**
-Extends system from static simulation to real-time streaming architecture
-Aligns with thesis objective of IoT-based smart transport system design
-Provides foundation for database integration and performance evaluation


