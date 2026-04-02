# Repository Cleanup Report

## Summary

The repository was reorganized into a cleaner academic layout centred on `app/`, `data_raw/`, `data_processed/`, `scripts/`, `sim/`, `results/`, `docs/`, `thesis/`, and `archive/`.

## Files Kept in Main Structure

- Gradio dashboard moved to `app/gradio_app.py`
- Active preprocessing, modelling, pricing, MQTT, and utility scripts grouped under `scripts/`
- Raw and processed thesis datasets kept under `data_raw/` and `data_processed/`
- SUMO network, scenario, and output files kept under `sim/`
- Final metrics, tables, and figures kept under `results/`
- Research notes and screenshots kept under `docs/`
- Final thesis manuscript, PDF, and presentation kept under `thesis/final_document/`

## Files Archived

- Legacy scripts moved to `archive/old_scripts/`
- Duplicate route and figure files moved to `archive/duplicate_files/`
- Runtime logs, MQTT status snapshots, and the Mosquitto installer moved to `archive/unused_outputs/`
- Older presentation deck moved to `archive/duplicate_files/AI_Dynamic_Congestion_Pricing_Presentation_Final.pptx`

## Files Renamed

- `Gradio/app.py` -> `app/gradio_app.py`
- `pricing_utils.py` -> `scripts/utils/pricing_utils.py`
- `data_raw/AT_API/traffic_counts/AT_traffic_counts_raw.csv.csv` -> `data_raw/AT_API/traffic_counts/auckland_traffic_counts_raw.csv`
- `data_processed/SUMO/edge_10min.csv` -> `data_processed/travel_time/sumo_edge_10min.csv`
- `results/pricing/pricing_schedule_arima.csv` -> `results/tables/dynamic_toll_schedule.csv`
- `thesis/My_Thesis.docx` -> `thesis/final_document/Auckland_Dynamic_Congestion_Pricing_Thesis.docx`
- `thesis/Sample.pdf` -> `thesis/final_document/Auckland_Dynamic_Congestion_Pricing_Thesis.pdf`
- `thesis/Auckland_Congestion_Pricing_Final_Presentation.pptx` -> `thesis/final_document/Auckland_Dynamic_Congestion_Pricing_Presentation.pptx`

## Exception Noted

- `thesis/Written_Document_Thesis.docx` could not be moved during cleanup because it was locked by another process. It remains in `thesis/` and can be moved later once the file is closed.
