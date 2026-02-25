"""
Data loading and alignment utilities for two-step OPF comparison.
"""

import pandas as pd
from pathlib import Path
from typing import Tuple
import config
from config import PARQUET_FILES, FORECAST_METHODS, FORECASTS_PARQUET


def load_forecasts() -> pd.DataFrame:
    """
    Load all forecast methods from unified parquet file.
    Expected columns: load_scenario_idx, bus_id, true, xgb, snaive, tgt, sarima.
    """
    return pd.read_parquet(FORECASTS_PARQUET)


def load_datakit_bus(parquet_dir: Path) -> pd.DataFrame:
    """Load bus data from datakit parquet output.
    Expected columns: load_scenario_idx, bus, Pd, Qd, Pg, Qg, Vm, Va, PQ, PV, REF.
    """
    return pd.read_parquet(parquet_dir / PARQUET_FILES["bus"])


def load_datakit_gen(parquet_dir: Path) -> pd.DataFrame:
    """Load generator data from datakit parquet output.
    Expected columns: load_scenario_idx, idx, bus, p_mw, q_mvar, cp0_eur, cp1_eur_per_mw, cp2_eur_per_mw2.
    """
    return pd.read_parquet(parquet_dir / PARQUET_FILES["gen"])


def prepare_load_forecast_comparison(
    forecasts_df: pd.DataFrame, method: str
) -> pd.DataFrame:
    """
    Prepare load forecast data for a single method.
    
    Args:
        forecasts_df: Full forecasts dataframe with all methods.
        method: Forecast method name (e.g., 'xgb').
    
    Returns:
        DataFrame with forecast comparison columns
    """
    if method not in FORECAST_METHODS:
        raise ValueError(f"Unknown method '{method}'. Available: {FORECAST_METHODS}")
    
    # Select columns and rename to standard names for comparison
    return forecasts_df[["load_scenario_idx", "bus_id", method, "true"]].rename(
        columns={"load_scenario_idx": "scenario", "bus_id": "bus", method: "pred"}
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
    # Align bus data on (load_scenario_idx, bus)
    bus_merged = pred_bus.merge(
        true_bus,
        on=["load_scenario_idx", "bus"],
        how="inner",
        suffixes=("_pred", "_true"),
    )
    
    # Align generator data on (load_scenario_idx, idx)
    gen_merged = pred_gen.merge(
        true_gen,
        on=["load_scenario_idx", "idx"],
        how="inner",
        suffixes=("_pred", "_true"),
    )
    
    # Validate scenario coverage
    pred_scenarios = set(pred_bus["load_scenario_idx"].unique())
    true_scenarios = set(true_bus["load_scenario_idx"].unique())
    
    if pred_scenarios != true_scenarios:
        missing = true_scenarios - pred_scenarios
        raise ValueError(
            f"Scenario mismatch in OPF results. Missing: {sorted(missing)[:5]}"
        )
    
    return bus_merged, gen_merged