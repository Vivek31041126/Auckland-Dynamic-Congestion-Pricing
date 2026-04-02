# Demo Evidence Guide

This guide lists the screenshots that should be captured as evidence for the thesis document and the GitHub README. Each item includes what to capture, the suggested file name, and a one-line caption suitable for academic reporting or repository presentation.

## 1. VS Code Project Structure

- What to capture: The repository opened in VS Code with the Explorer panel visible, showing the final organised folder structure.
- File name to save it as: `vscode_project_structure.png`
- Caption: Final organised MSc thesis repository structure in Visual Studio Code.

## 2. SUMO Outputs

- What to capture: The SUMO scenario or output view showing the simulation configuration and generated output file such as `sim/outputs/edge_data.xml`.
- File name to save it as: `sumo_outputs.png`
- Caption: SUMO simulation output used to generate edge-level traffic observations for the pricing pipeline.

## 3. Raw Dataset Sample

- What to capture: A CSV preview of the raw dataset, preferably `data_raw/SUMO/edge_1min_raw.csv` or the supporting Auckland Transport raw file.
- File name to save it as: `raw_dataset_sample.png`
- Caption: Sample of the raw input dataset prior to preprocessing and temporal aggregation.

## 4. Cleaned Dataset Sample

- What to capture: A table preview of `data_processed/travel_time/travel_time_10min.csv` showing cleaned 10-minute edge-level travel-time records.
- File name to save it as: `cleaned_dataset_sample.png`
- Caption: Cleaned 10-minute travel-time dataset prepared for forecasting and corridor construction.

## 5. Train / Validation / Test Dataset Split

- What to capture: A notebook, script output, table, or chart showing the chronological split used for modelling, including train, validation, and test partitions.
- File name to save it as: `dataset_split.png`
- Caption: Chronological train, validation, and test split used for model development and evaluation.

## 6. ARIMA / XGBoost / LSTM Results

- What to capture: The model comparison output table or metrics file showing MAE and RMSE for ARIMA, XGBoost, and LSTM.
- File name to save it as: `model_results_comparison.png`
- Caption: Forecasting performance comparison of ARIMA, XGBoost, and LSTM on corridor travel-time prediction.

## 7. Dynamic Pricing Results

- What to capture: The toll schedule output, pricing summary, or toll-over-time figure from the pricing stage.
- File name to save it as: `dynamic_pricing_results.png`
- Caption: Dynamic congestion pricing output showing time-varying toll levels derived from predicted congestion.

## 8. Demand Response Results

- What to capture: The demand response CSV, summary output, or a chart showing estimated demand reduction under the applied toll schedule.
- File name to save it as: `demand_response_results.png`
- Caption: Estimated demand response under the dynamic tolling framework using short-run elasticity assumptions.

## 9. Congestion Feedback Results

- What to capture: The feedback-adjusted travel-time table or the before-versus-after congestion feedback figure.
- File name to save it as: `congestion_feedback_results.png`
- Caption: Travel-time reduction after applying congestion feedback to the demand response output.

## 10. MQTT Terminal Publisher / Subscriber Running

- What to capture: Two terminals side by side, with the subscriber receiving messages and the publisher sending travel-time payloads.
- File name to save it as: `mqtt_publisher_subscriber_demo.png`
- Caption: MQTT publisher and subscriber processes demonstrating the IoT-style message streaming extension.

## 11. Gradio App Home Screen

- What to capture: The main landing or overview page of the Gradio dashboard with headline metrics visible.
- File name to save it as: `gradio_home_screen.png`
- Caption: Gradio dashboard home screen presenting headline thesis metrics and project overview.

## 12. Gradio App Dataset Tab

- What to capture: The dataset preview tab showing raw and processed dataset selections with sample tables.
- File name to save it as: `gradio_dataset_tab.png`
- Caption: Gradio dataset tab used to inspect raw and processed data tables interactively.

## 13. Gradio App Pricing / Demo Tab

- What to capture: The scenario explorer, pricing tab, or MQTT demo tab showing plots, outputs, or live status.
- File name to save it as: `gradio_pricing_demo_tab.png`
- Caption: Gradio pricing and demonstration interface for scenario exploration and live system monitoring.

## 14. GitHub Repository Final View

- What to capture: The GitHub repository homepage after push, showing the cleaned structure, README, and key folders.
- File name to save it as: `github_repository_final_view.png`
- Caption: Final GitHub repository view prepared for thesis submission, examiner review, and public presentation.

## Suggested Storage Location

- Save all captured images in `docs/screenshots/`.
- Reuse the same files in both the thesis document and the GitHub README where appropriate.

## Recommended Capture Tips

- Use high-resolution screenshots with readable text.
- Keep the file explorer or relevant headers visible so the context is obvious.
- Prefer consistent window sizing and naming for a more professional final presentation.
- Capture clean screens without unrelated browser tabs, notifications, or personal information.
