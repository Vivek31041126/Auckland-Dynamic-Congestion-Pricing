from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TollParameters:
    ci_free: float = 1.10
    ci_mid: float = 1.30
    ci_severe: float = 1.60
    toll_min: float = 1.00
    toll_mid: float = 3.00
    toll_cap: float = 6.00


def validate_toll_parameters(params: TollParameters) -> None:
    if params.ci_free >= params.ci_mid:
        raise ValueError("CI mid threshold must be larger than CI free threshold.")
    if params.ci_mid >= params.ci_severe:
        raise ValueError("CI severe threshold must be larger than CI mid threshold.")
    if params.toll_min > params.toll_mid or params.toll_mid > params.toll_cap:
        raise ValueError("Toll values must follow min <= mid <= cap.")


def calculate_congestion_index(
    predicted_travel_time_sec: pd.Series,
    free_flow_travel_time_sec: float,
) -> pd.Series:
    if free_flow_travel_time_sec <= 0:
        raise ValueError("Free-flow travel time must be greater than zero.")
    return predicted_travel_time_sec.astype(float) / float(free_flow_travel_time_sec)


def calculate_toll(congestion_index: pd.Series, params: TollParameters) -> pd.Series:
    validate_toll_parameters(params)

    ci = congestion_index.astype(float)
    toll = pd.Series(0.0, index=ci.index, dtype=float)

    mid_mask = (ci > params.ci_free) & (ci <= params.ci_mid)
    if mid_mask.any():
        mid_share = (ci.loc[mid_mask] - params.ci_free) / (params.ci_mid - params.ci_free)
        toll.loc[mid_mask] = params.toll_min + mid_share * (params.toll_mid - params.toll_min)

    severe_mask = ci > params.ci_mid
    if severe_mask.any():
        severe_share = ((ci.loc[severe_mask] - params.ci_mid) / (params.ci_severe - params.ci_mid)).clip(upper=1.0)
        toll.loc[severe_mask] = params.toll_mid + severe_share * (params.toll_cap - params.toll_mid)

    return toll


def calculate_congestion_index_and_toll(
    predicted_travel_time_sec: pd.Series,
    free_flow_travel_time_sec: float,
    params: TollParameters,
) -> pd.DataFrame:
    congestion_index = calculate_congestion_index(predicted_travel_time_sec, free_flow_travel_time_sec)
    toll = calculate_toll(congestion_index, params)
    return pd.DataFrame({"CI": congestion_index, "toll_nzd": toll}, index=predicted_travel_time_sec.index)
