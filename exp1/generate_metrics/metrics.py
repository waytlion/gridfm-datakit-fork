"""
Metric computation functions matching GraphKit's ForecastOPFTask.
"""

import pandas as pd
import numpy as np
from typing import Dict


def compute_mae(df: pd.DataFrame, features: list) -> Dict[str, float]:
    """
    Compute MAE for specified features.
    
    Args:
        df: DataFrame with {feature}_pred and {feature}_true columns.
        features: List of feature names (e.g., ['pd', 'qd']).
    
    Returns:
        Dict mapping feature names to MAE values.
    """
    return {
        feat: np.abs(df[f"{feat}_pred"] - df[f"{feat}_true"]).mean()
        for feat in features
    }


def compute_rmse_by_bus_type(
    bus_df: pd.DataFrame, features: list
) -> pd.DataFrame:
    """
    Compute RMSE for specified features, split by bus type (PQ/PV/REF).
    
    Args:
        bus_df: Aligned bus dataframe with PQ/PV/REF flags and pred/true columns.
        features: List of feature names (using parquet names, e.g., ['Vm', 'Va', 'Pg', 'Qg']).
    
    Returns:
        DataFrame with columns [bus_type, feature, rmse].
    """
    results = []
    
    # Bus type flags in parquet: PQ, PV, REF
    for bus_type in ["PQ", "PV", "REF"]:
        # Filter to buses of this type (flag == 1 or True)
        mask = bus_df[f"{bus_type}_true"].astype(bool)
        subset = bus_df[mask]
        
        if len(subset) == 0:
            continue  # No buses of this type
        
        for feat in features:
            squared_error = (subset[f"{feat}_pred"] - subset[f"{feat}_true"]) ** 2
            rmse = np.sqrt(squared_error.mean())
            results.append({
                "bus_type": bus_type,
                "feature": feat,
                "rmse": rmse,
            })
    
    return pd.DataFrame(results)


def compute_generator_rmse(gen_df: pd.DataFrame) -> float:
    """Compute RMSE for generator active power. Uses parquet column name: p_mw."""
    squared_error = (gen_df["p_mw_pred"] - gen_df["p_mw_true"]) ** 2
    return np.sqrt(squared_error.mean())


def compute_cost_metrics(gen_df: pd.DataFrame) -> Dict[str, float]:
    """
    Compute total generation cost and optimality gap.
    
    Formula: cost = cp0 + cp1 * pg + cp2 * pg^2
    
    Returns:
        Dict with 'mean_optimality_gap_pct' and related statistics.
    """
    # Compute cost per generator. Uses parquet names: p_mw, cp0_eur, cp1_eur_per_mw, cp2_eur_per_mw2
    for suffix in ["pred", "true"]:
        pg = gen_df[f"p_mw_{suffix}"]
        gen_df[f"cost_{suffix}"] = (
            gen_df[f"cp0_eur_{suffix}"]
            + gen_df[f"cp1_eur_per_mw_{suffix}"] * pg
            + gen_df[f"cp2_eur_per_mw2_{suffix}"] * pg ** 2
        )
    
    # Aggregate cost per scenario
    cost_per_scenario = gen_df.groupby("load_scenario_idx").agg({
        "cost_pred": "sum",
        "cost_true": "sum",
    })
    
    # Compute optimality gap (%)
    cost_per_scenario["gap_pct"] = (
        np.abs(cost_per_scenario["cost_pred"] - cost_per_scenario["cost_true"])
        / cost_per_scenario["cost_true"]
        * 100
    )
    
    return {
        "mean_optimality_gap_pct": cost_per_scenario["gap_pct"].mean(),
        "median_optimality_gap_pct": cost_per_scenario["gap_pct"].median(),
        "max_optimality_gap_pct": cost_per_scenario["gap_pct"].max(),
    }