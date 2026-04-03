# WORFLOW
1. Load baseline predictions from cluster "bernard" to local
      -> scp tibo990i@login1.barnard.hpc.tu-dresden.de:/home/tibo990i/Thesis_Repo/phase1_baseline/*parquet exp1\data\data_in
2. On Local: Transform predictions into datakit input format called "precomputed_profiles"
      -> EXECUTE: exp1\generate_opf_inputs\exp1_step2_transform_benchmark_to_datakit.ipynb
      -> OUTPUT:  exp1\data\precomputed_profiles\
      -> OPTIONAL: Load precomputed_profiles .csv files to google drive 
3. On Cluster Leipzig: Run datakit on baseline predictions Leipzig Cluster
      -> EXPORT PRECOMPUTED_PROFILES TO CLUSTER:
            - scp -r .\exp1\data\precomputed_profiles\case118_ieee_horizon24_3yr\ og98ohex@export01.sc.uni-leipzig.de:~/gridfm-datakit-fork/exp1/data/precomputed_profiles/
      -> CONFIG 3 PARAMS IN: exp1\configs\cluster_leipzig_opf_for_forecast.yaml
            - scenarios
            - scenario_file
            - data_dir
      -> EXECUTE: ./cluster_leipzig.sh
      -> IMPORT AC-OPF RESULTS TO LOCAL:
            - scp -r og98ohex@export01.sc.uni-leipzig.de:/home/sc.uni-leipzig.de/og98ohex/gridfm-datakit-fork/data_out/3yr_2019-2021/baseline_preds/case118_horizon_6_3yr exp1\data\data_out\case118_horizon_6_3yr

4. On Local: Compare AC-OPF results derived from predictions with ground truth
      -> NOTE: For t=6 the input bus data should have index for scenario / load _scenario_idx of 23622
      -> READ AND EXECUTE: exp1\generate_metrics\compare.py
      -> OUTPUT: exp1\results\case118_horizon1_3yr2019-2021

# NOTES
1. Qd is not forecasted by baseline models -> derived by applying scaling factor to Pd
2. datakit on cluster cannot be run in parallel -> Julia makes probs

# Abstarct Description
Input: read in the predicted loads (which were predicted in Step 1 in the baseline approach)

PutPut: 
1. For each model. Take the predicted Loads, and transform into format, which can be fed into the datakit. in order to solve OPF
-> i THINK it is only about adding q_mvar, which can be retrieved just as scaling bus specific scalig factor (see generate_precomputed_profile.ipynb) 
2. Solve OPF for predicted loads
3. compute the same metrics as graphkit does

Output:
- for each model, output the metrics of 2-step approach


# compare.py: Detailed metric pipeline summary

## 1) Inputs and expected files

`compare.py` consumes 3 data sources:

1. Forecast parquet (`--forecasts-parquet`)
       - Default: `exp1/data/data_in/benchmark_results.parquet`
       - For horizon runs, use the matching file explicitly:
             - H1: `benchmark_results.parquet` (or equivalent h1 parquet)
             - H6: `case118_ieee_horizon6.parquet`
             - H24: `case118_ieee_horizon24.parquet`
       - Core columns used:
             - `load_scenario_idx`
             - `bus_id`
             - `true`
       - Optional/important columns:
             - `horizon_step` (required for correct H6/H24 remapping)
             - model columns: `xgb`, `snaive`, `sarima`, `tgt` (if present)

2. Predicted OPF output directory (`--predicted-opf-base-dir`)
       - Expected structure per method:
             - `{predicted_opf_base_dir}/{method}/{dataset}/raw/bus_data.parquet`
             - `{predicted_opf_base_dir}/{method}/{dataset}/raw/gen_data.parquet`
       - For precomputed profiles, predicted OPF `load_scenario_idx` is flattened 0..N-1.

3. Ground-truth OPF directory (`--ground-truth-dir`)
       - Expected files:
             - `bus_data.parquet`
             - `gen_data.parquet`


## 2) How scenario indices are remapped/matched

### 2.1 Predicted flattened scenario remap

Predicted OPF data uses flattened scenario index from datakit (`0..N-1`).
`compare.py` remaps this to ground-truth timeline indices before merging.

- If `horizon_step` exists in forecasts parquet (H6/H24 case):
      - Build unique pairs: (`load_scenario_idx`, `horizon_step`)
      - Sort by (`load_scenario_idx`, `horizon_step`) (stable)
      - Enumerate rows to get flattened index `pred_flat_idx = 0..N-1`
      - Map to ground-truth scenario with:
            - `target_load_scenario_idx = load_scenario_idx + horizon_step`
      - Apply this map to predicted `bus_data` and `gen_data` `load_scenario_idx`

- If no `horizon_step` exists (H1 style):
      - Map by sorted unique scenarios directly (`enumerate(sorted(load_scenario_idx))`)

### 2.2 Merge keys (combined keys)

After remapping, alignment uses combined keys:

- Bus-level merge key: (`load_scenario_idx`, `bus`)
- Generator-level merge key: (`load_scenario_idx`, `idx`)

Both merges are `inner` joins.


## 3) Metrics computation

### 3.1 Forecast metrics table (`{dataset}_forecast.csv`)

Computed for all selected methods in one file:
- Rows: one per horizon (`t+1`, ..., `t+H`) plus `GLOBAL`
- Columns:
      - `Model`
      - `Horizon`
      - `Pd (MW) - RMSE`
      - `Pd (MW) - MAE`
      - `Pd (MW) - wMAPE`
      - `Pd (MW) - MASE`
      - `Pd (MW) - MSSE`

Formulas:
- RMSE: `sqrt(mean((pred-true)^2))`
- MAE: `mean(abs(pred-true))`
- wMAPE: `sum(abs(pred-true)) / (sum(abs(true)) + 1e-8)`
- MASE: `MAE_model / (MAE_naive + 1e-8)` where naive is a seasonal baseline from 48 origins earlier.
- MSSE: `MSE_model / (MSE_naive + 1e-8)` where naive is the same seasonal baseline.
- Naive baseline detail (matching ST-GNN): for each forecast origin, take the value from 48 origins earlier and repeat it across all horizon steps of that origin.

### 3.2 Per-method forecast MAE (`{dataset}_forecast_MAE.csv`)

Still produced per method for backward compatibility:
- single MAE value for `Pd`
- no horizon split

### 3.3 OPF metrics (per method)

1. `{dataset}_RMSE.csv`
       - RMSE by bus type (`PQ`, `PV`, `REF`) and feature (`Vm`, `Va`, `Pg`, `Qg`)

2. `{dataset}_metrics.csv`
       - Generator Pg RMSE
       - Mean/Median/Max optimality gap (%)
       - Physics constraint violations note

3. `comparison_summary.csv`
       - one summary row per method

