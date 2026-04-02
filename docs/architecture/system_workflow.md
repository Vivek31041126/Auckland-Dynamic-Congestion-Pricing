# System Workflow

This repository follows a corridor-level dynamic pricing workflow:

1. SUMO assets in `sim/` define the Auckland network, routes, and scenario configuration.
2. Edge output from `sim/outputs/edge_data.xml` is converted into raw and aggregated travel-time tables by `scripts/preprocessing/`.
3. Corridor datasets are built from the most active edges and stored in `data_processed/corridor/`.
4. Forecasting experiments in `scripts/modelling/` evaluate ARIMA, XGBoost, and LSTM.
5. Pricing scripts in `scripts/pricing/` translate predicted congestion into tolls, demand response, and feedback-adjusted travel time.
6. MQTT scripts in `scripts/mqtt/` simulate a lightweight IoT streaming layer for corridor travel-time messages.
7. The Gradio interface in `app/gradio_app.py` brings together results, scenario exploration, and MQTT monitoring.
