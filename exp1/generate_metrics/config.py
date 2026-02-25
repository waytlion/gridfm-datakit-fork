"""
Configuration for two-step OPF comparison pipeline.
"""

from pathlib import Path

# Paths
FORECASTS_PARQUET = Path("exp1/forecasts.parquet")

# Forecast methods available in forecasts.parquet
FORECAST_METHODS = ["xgb", "snaive", "tgt", "sarima"]

# Column mappings
COLUMN_MAPPINGS = {
    "forecast_parquet": {
        "scenario": "load_scenario_idx",
        "bus": "bus_id",
        "true": "true",
        # Method columns: xgb, snaive, tgt, sarima (used directly)
    },
    "datakit_bus": {
        "scenario": "load_scenario_idx",
        "bus": "bus",
        "pd": "Pd",
        "qd": "Qd",
        "pg": "Pg",  # NOTE: Assuming already aggregated per bus. Verify with colleague.
        "qg": "Qg",
        "vm": "Vm",
        "va": "Va",
        "pq_flag": "PQ",
        "pv_flag": "PV",
        "ref_flag": "REF",
    },
    "datakit_gen": {
        "scenario": "load_scenario_idx",
        "gen_idx": "idx",
        "bus": "bus",
        "pg": "p_mw",
        "qg": "q_mvar",
        "cp0": "cp0_eur",
        "cp1": "cp1_eur_per_mw",
        "cp2": "cp2_eur_per_mw2",
    },
}

# NOTE: All units assumed as-labeled in parquets (MW, MVar, p.u., rad, EUR).
# No conversion applied. Verify consistency with colleague.

PARQUET_FILES = {
    "bus": "bus_data.parquet",
    "gen": "gen_data.parquet",
    "branch": "branch_fdata.parquet",
}

OUTPUT_TEMPLATES = {
    "forecast_mae": "{dataset}_forecast_MAE.csv",
    "rmse": "{dataset}_RMSE.csv",
    "metrics": "{dataset}_metrics.csv",
    "summary": "comparison_summary.csv",
}