# Two-Step OPF Comparison Pipeline

Compares statistical load forecasting + AC-OPF against GraphKit's end-to-end GNN approach.

## Methodology

### Two-Step Approach
1. **Forecast loads** using statistical methods (XGBoost, SARIMA, etc.)
2. **Solve AC-OPF** on forecasted loads via datakit
3. **Compare OPF solutions** against ground-truth OPF (run on true loads)

### Metrics Computed

Matches GraphKit's `ForecastOPFTask` output:

| Category | Metrics | File |
|---|---|---|
| **Load Forecast Quality** | MAE for Pd (MW) | `{dataset}_forecast_MAE.csv` |
| **OPF Output Accuracy** | RMSE for Vm, Va, Pg, Qg by bus type (PQ/PV/REF) | `{dataset}_RMSE.csv` |
| **Generator Dispatch** | RMSE for per-generator Pg | `{dataset}_metrics.csv` |
| **Economic Optimality** | Mean/median/max optimality gap (%) | `{dataset}_metrics.csv` |
| **Physics Feasibility** | N/A (AC-OPF guarantees feasibility) | `{dataset}_metrics.csv` |

**Note on Qd forecasts**: The `forecasts.parquet` file contains only active power (Pd) forecasts. Reactive power (Qd) is not forecasted — datakit's OPF solver determines it endogenously based on power factor assumptions.

## Data Flow

```
forecasts.parquet (Pd forecasts)
    ↓
Datakit AC-OPF Solver
    ↓
OPF Results: {predicted-opf-dir}/{method}/case14_ieee/raw/*.parquet
    |
    ├─ bus_data.parquet (Vm, Va, Pg, Qg per bus)
    ├─ gen_data.parquet (Pg, cost coefficients per generator)
    └─ ...
    ↓
Comparison Script (align with ground truth)
    ↓
Metrics CSVs + Summary Table
```

## Usage

### Basic Usage
```bash
python -m scripts.compare_two_step_opf.compare \
    --ground-truth-dir data_out/3yrs/data_out/no_pertubations/case14_ieee/raw \
    --predicted-opf-base-dir exp1/opf_results \
    --output-dir results/two_step_comparison \
    --dataset case14_ieee
```

### Compare Specific Methods
```bash
python -m scripts.compare_two_step_opf.compare \
    --ground-truth-dir data_out/3yrs/data_out/no_pertubations/case14_ieee/raw \
    --predicted-opf-base-dir exp1/opf_results \
    --output-dir results/two_step_comparison \
    --methods xgb sarima
```

## Directory Structure

### Input
```
exp1/
  forecasts.parquet                # All forecast methods + ground truth
  opf_results/                     # Your OPF solver outputs
    xgb/
      case14_ieee/raw/
        bus_data.parquet
        gen_data.parquet
    sarima/
      case14_ieee/raw/
        ...
```

### Output
```
results/
  two_step_comparison/
    xgb/
      case14_ieee_forecast_MAE.csv
      case14_ieee_RMSE.csv
      case14_ieee_metrics.csv
    sarima/
      ...
    comparison_summary.csv          # Side-by-side comparison
```

## Key Assumptions (Verify with Colleague)

1. **Bus-level Pg aggregation**: `bus_data.parquet` column `Pg` is assumed to be the sum of all generators at that bus. If not, aggregation from `gen_data.parquet` must be added.

2. **Units**: All metrics assume:
   - Active/reactive power: MW/MVar
   - Voltage: per-unit (p.u.)
   - Angles: radians
   - Cost: EUR
   
   No unit conversions are applied.

3. **Horizon step**: The `horizon_step` column in `forecasts.parquet` is currently ignored. All rows are used for comparison.

## Comparison to GraphKit

| Aspect | GraphKit ForecastOPF | Two-Step Approach |
|---|---|---|
| Load forecast | GNN predicts Pd, Qd | Statistical models predict Pd only |
| OPF solution | GNN predicts [Pg, Qg, Vm, Va] directly | AC-OPF solver computes from forecasted loads |
| Physics feasibility | ~10% violation rate (learned constraints) | ~0% violation (solver-enforced) |
| Optimality | May deviate from true optimum | Guaranteed optimal given forecasted loads |

The two-step approach trades end-to-end learning for guaranteed physical consistency and economic optimality.