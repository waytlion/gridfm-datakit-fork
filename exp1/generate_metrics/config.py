"""
Configuration for two-step OPF comparison pipeline.
"""

from pathlib import Path

# Paths (relative to repo root)
_REPO_ROOT = Path(__file__).parent.parent.parent  # gridfm-datakit-fork/
FORECASTS_PARQUET = _REPO_ROOT / "exp1" / "data" / "data_in" / "forecasts.parquet"

# Forecast methods available in forecasts.parquet
FORECAST_METHODS = ["xgb", "snaive", "tgt", "sarima"]

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