"""
Data loading and alignment utilities for two-step OPF comparison.
"""

import pandas as pd
from pathlib import Path
from typing import Tuple, Dict
from .config import COLUMN_MAPPINGS, PARQUET_FILES, FORECAST_METHODS, FORECASTS_PARQUET


def load_forecasts() -> pd.DataFrame:
    """
    Load all forecast methods from unified parquet file.
    
    Returns:
        DataFrame with columns: [scenario, bus, true, xgb, snaive, tgt, sarima, horizon_step]
    """
    df = pd.read_parquet(FORECASTS_PARQUET)
    cols = COLUMN_MAPPINGS["forecast_parquet"]
    
    # Rename to standard names
    rename_map = {
        cols["scenario"]: "scenario",
        cols["bus"]: "bus",
        cols["true"]: "true",
    }
    df = df.rename(columns=rename_map)
    
    # Validate all forecast methods are present
    missing_methods = set(FORECAST_METHODS) - set(df.columns)
    if missing_methods:
        raise ValueError(f"Missing forecast methods in parquet: {missing_methods}")
    
    return df


def load_datakit_bus(parquet_dir: Path) -> pd.DataFrame:
    """Load bus data from datakit parquet output."""
    path = parquet_dir / PARQUET_FILES["bus"]
    df = pd.read_parquet(path)
    cols = COLUMN_MAPPINGS["datakit_bus"]
    return df.rename(columns={v: k for k, v in cols.items()})


def load_datakit_gen(parquet_dir: Path) -> pd.DataFrame:
    """Load generator data from datakit parquet output."""
    path = parquet_dir / PARQUET_FILES["gen"]
    df = pd.read_parquet(path)
    cols = COLUMN_MAPPINGS["datakit_gen"]
    return df.rename(columns={v: k for k, v in cols.items()})


def prepare_load_forecast_comparison(
    forecasts_df: pd.DataFrame, method: str
) -> pd.DataFrame:
    """
    Prepare load forecast data for a single method.
    
    Args:
        forecasts_df: Full forecasts dataframe with all methods.
        method: Forecast method name (e.g., 'xgb').
    
    Returns:
        DataFrame with columns: [scenario, bus, pred, true] for Pd only.
        Note: forecasts.parquet contains active load (Pd) only, not reactive (Qd).
    """
    if method not in FORECAST_METHODS:
        raise ValueError(f"Unknown method '{method}'. Available: {FORECAST_METHODS}")
    
    return forecasts_df[["scenario", "bus", method, "true"]].rename(
        columns={method: "pred", "true": "true"}
    )


def align_opf_results(
    pred_bus: pd.DataFrame,
    true_bus: pd.DataFrame,
    pred_gen: pd.DataFrame,
    true_gen: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Align predicted and ground-truth OPF results.
    
    Returns:
        (bus_merged, gen_merged): Aligned dataframes with _pred and _true suffixes.
    """
    # Align bus data
    bus_merged = pred_bus.merge(
        true_bus,
        on=["scenario", "bus"],
        how="inner",
        suffixes=("_pred", "_true"),
    )
    
    # Align generator data
    gen_merged = pred_gen.merge(
        true_gen,
        on=["scenario", "gen_idx"],
        how="inner",
        suffixes=("_pred", "_true"),
    )
    
    # Validate scenario coverage
    pred_scenarios = set(pred_bus["scenario"].unique())
    true_scenarios = set(true_bus["scenario"].unique())
    
    if pred_scenarios != true_scenarios:
        missing = true_scenarios - pred_scenarios
        raise ValueError(
            f"Scenario mismatch in OPF results. Missing: {sorted(missing)[:5]}"
        )
    
    return bus_merged, gen_merged