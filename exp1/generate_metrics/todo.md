# Outstanding Tasks

## Phase 2: Visualization (Deferred)

GraphKit generates several plots in `test_plots/{dataset}/`:

### Not Yet Implemented
1. **Objective cost scatter plot**
   - X-axis: Ground-truth total cost (EUR)
   - Y-axis: Predicted total cost (EUR)
   - One point per scenario
   - Ideal: points lie on y=x line

2. **Per-feature correlation plots**
   - Scatter plots for: Vm, Va, Pg, Qg
   - Split by bus type (PQ/PV/REF)
   - Shows prediction accuracy visually

3. **Residual histograms**
   - Distribution of power balance residuals (ΔP, ΔQ)
   - For two-step approach, should be near-zero (solver-enforced)
   - Useful to verify solver convergence quality

4. **Voltage profiles**
   - Line plot: bus index vs. voltage magnitude
   - Compare predicted vs. true profiles for sample scenarios

### Implementation Plan
- Create `scripts/compare_two_step_opf/plots.py`
- Add plotting utilities using matplotlib/seaborn
- Extend `compare.py` with `--generate-plots` flag
- Save plots to `{output_dir}/{method}/plots/`

## Phase 3: Extensions (Optional)

1. **Per-scenario error breakdown**
   - CSV with columns: [scenario, mae_pd, rmse_vm, optimality_gap, ...]
   - Identify worst-case scenarios for failure analysis

2. **Temporal analysis**
   - If `forecasts.parquet` has temporal structure (timestamps)
   - Plot error metrics over time (seasonal patterns?)

3. **Statistical significance tests**
   - Paired t-tests between methods
   - Determine if performance differences are statistically significant

4. **Multi-horizon comparison**
   - If `horizon_step` becomes relevant
   - Compare 1-step vs. multi-step forecast accuracy

## Verification Checklist (Before Publishing Results)

- [ ] Confirm with colleague: `bus_data.parquet` Pg is pre-aggregated
- [ ] Confirm with colleague: All units are correctly assumed (MW/MVar/p.u./rad/EUR)
- [ ] Validate scenario alignment: all test scenarios present in both forecast and OPF results
- [ ] Cross-check one method's results manually (spot-check MAE/RMSE calculations)
- [ ] Compare summary table against GraphKit's test output for sanity check