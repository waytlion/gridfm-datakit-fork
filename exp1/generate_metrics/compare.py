"""
Main CLI script for comparing two-step OPF approach against ground truth.

Usage:
    cd gridfm-datakit-fork/
    python exp1/generate_metrics/compare.py \
        --predicted-opf-base-dir exp1/data/data_out \
        --ground-truth-dir data_out/3yrs/no_pertubations/case14_ieee/raw \
        --output-dir exp1/results \
        --dataset case14_ieee
        
    Or with defaults:
    python exp1/generate_metrics/compare.py  # Uses default paths
    
    Compare specific methods only:
    python exp1/generate_metrics/compare.py --methods xgb sarima
"""

import argparse
from pathlib import Path
import pandas as pd
from config import FORECAST_METHODS, OUTPUT_TEMPLATES
from loaders import (
    load_forecasts,
    load_datakit_bus,
    load_datakit_gen,
    prepare_load_forecast_comparison,
    align_opf_results,
)
from metrics import (
    compute_mae,
    compute_rmse_by_bus_type,
    compute_generator_rmse,
    compute_cost_metrics,
)


def compare_single_method(
    method: str,
    forecasts_df: pd.DataFrame,
    ground_truth_dir: Path,
    predicted_opf_dir: Path,
    output_dir: Path,
    dataset: str,
) -> dict:
    """
    Run complete comparison for a single forecast method.
    
    Returns:
        Dict with summary metrics for aggregation.
    """
    print(f"\n{'='*60}")
    print(f"Processing method: {method}")
    print(f"{'='*60}")
    
    method_output_dir = output_dir / method
    method_output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load forecast MAE (Pd only, since forecasts.parquet has active power only)
    print("Computing load forecast MAE...")
    forecast_comparison = prepare_load_forecast_comparison(forecasts_df, method)
    mae_pd = compute_mae(forecast_comparison.rename(columns={"pred": "pd_pred", "true": "pd_true"}), ["pd"])
    
    # Save forecast MAE
    forecast_mae_df = pd.DataFrame([{
        "Feature": "Pd",
        "MAE": mae_pd["pd"],
        "Unit": "MW (assumed from parquet)",
    }])
    forecast_mae_path = method_output_dir / OUTPUT_TEMPLATES["forecast_mae"].format(dataset=dataset)
    forecast_mae_df.to_csv(forecast_mae_path, index=False)
    print(f"  MAE Pd: {mae_pd['pd']:.4f} MW")
    
    # 2. Load OPF results
    print("Loading OPF results...")
    pred_bus = load_datakit_bus(predicted_opf_dir)
    true_bus = load_datakit_bus(ground_truth_dir)
    pred_gen = load_datakit_gen(predicted_opf_dir)
    true_gen = load_datakit_gen(ground_truth_dir)
    
    # 3. Align OPF results
    print("Aligning OPF results...")
    bus_aligned, gen_aligned = align_opf_results(pred_bus, true_bus, pred_gen, true_gen)
    print(f"  Aligned {len(bus_aligned)} bus observations across {bus_aligned['scenario'].nunique()} scenarios")
    print(f"  Aligned {len(gen_aligned)} generator observations")
    
    # 4. Compute RMSE by bus type
    print("Computing RMSE by bus type...")
    rmse_df = compute_rmse_by_bus_type(bus_aligned, ["vm", "va", "pg", "qg"])
    rmse_path = method_output_dir / OUTPUT_TEMPLATES["rmse"].format(dataset=dataset)
    rmse_df.to_csv(rmse_path, index=False)
    print(f"  Saved RMSE table: {rmse_path}")
    # Extract key RMSE values for summary (aggregate across bus types)
    rmse_summary = rmse_df.groupby("feature")["rmse"].mean().to_dict()
    
    
    # 5. Compute generator RMSE
    print("Computing generator-level RMSE...")
    gen_rmse = compute_generator_rmse(gen_aligned)
    
    # 6. Compute cost metrics
    print("Computing cost/optimality gap...")
    cost_metrics = compute_cost_metrics(gen_aligned)
    
    # 7. Save metrics summary
    metrics_df = pd.DataFrame([{
        "Metric": "Generator Pg RMSE",
        "Value": gen_rmse,
        "Unit": "MW",
    }, {
        "Metric": "Mean Optimality Gap",
        "Value": cost_metrics["mean_optimality_gap_pct"],
        "Unit": "%",
    }, {
        "Metric": "Median Optimality Gap",
        "Value": cost_metrics["median_optimality_gap_pct"],
        "Unit": "%",
    }, {
        "Metric": "Max Optimality Gap",
        "Value": cost_metrics["max_optimality_gap_pct"],
        "Unit": "%",
    }, {
        "Metric": "Physics Constraint Violations",
        "Value": "N/A - AC-OPF solver guarantees feasibility",
        "Unit": "-",
    }])
    
    metrics_path = method_output_dir / OUTPUT_TEMPLATES["metrics"].format(dataset=dataset)
    metrics_df.to_csv(metrics_path, index=False)
    print(f"  Saved metrics: {metrics_path}")
    
    # Return summary for aggregation
    return {
        "method": method,
        "mae_pd": mae_pd["pd"],
        "rmse_vm": rmse_summary.get("VM", float("nan")),
        "rmse_va": rmse_summary.get("VA", float("nan")),
        "rmse_pg_bus": rmse_summary.get("PG", float("nan")),  # Bus-level aggregated
        "rmse_qg": rmse_summary.get("QG", float("nan")),
        "rmse_pg_gen": gen_rmse,  # Generator-level
        "optimality_gap_pct": cost_metrics["mean_optimality_gap_pct"],
    }


def generate_comparison_summary(summaries: list, output_dir: Path, dataset: str):
    """Generate side-by-side comparison table across all methods."""
    summary_df = pd.DataFrame(summaries)
    summary_path = output_dir / OUTPUT_TEMPLATES["summary"].format(dataset=dataset)
    summary_df.to_csv(summary_path, index=False)
    
    print(f"\n{'='*60}")
    print("Comparison Summary")
    print(f"{'='*60}")
    print(summary_df.to_string(index=False))
    print(f"\nSaved to: {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="Compare two-step OPF approach vs ground truth")
    parser.add_argument(
        "--ground-truth-dir", 
        type=Path, 
        default=Path("data_out/3yrs/no_pertubations/case14_ieee/raw"),
        help="Path to ground-truth OPF parquet directory"
    )
    parser.add_argument(
        "--predicted-opf-base-dir", 
        type=Path, 
        default=Path("exp1/data/data_out"),
        help="Base directory containing {method}/case14_ieee/raw subdirs"
    )
    parser.add_argument(
        "--output-dir", 
        type=Path, 
        default=Path("exp1/results"),
        help="Output directory for comparison results"
    )
    parser.add_argument("--dataset", type=str, default="case14_ieee",
                        help="Dataset name for output file naming")
    parser.add_argument("--methods", nargs="+", default=FORECAST_METHODS,
                        help="Forecast methods to compare (default: all)")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.ground_truth_dir.exists():
        raise FileNotFoundError(f"Ground truth directory not found: {args.ground_truth_dir}")
    
    # Load forecasts once (shared across all methods)
    print("Loading forecasts...")
    forecasts_df = load_forecasts()
    print(f"Loaded {len(forecasts_df)} forecast observations for {forecasts_df['scenario'].nunique()} scenarios")
    
    # Process each method
    summaries = []
    for method in args.methods:
        predicted_opf_dir = args.predicted_opf_base_dir / method / args.dataset / "raw"
        
        if not predicted_opf_dir.exists():
            print(f"\n⚠️  Skipping {method}: OPF results not found at {predicted_opf_dir}")
            continue
        
        try:
            summary = compare_single_method(
                method=method,
                forecasts_df=forecasts_df,
                ground_truth_dir=args.ground_truth_dir,
                predicted_opf_dir=predicted_opf_dir,
                output_dir=args.output_dir,
                dataset=args.dataset,
            )
            summaries.append(summary)
        except Exception as e:
            print(f"\n❌ Error processing {method}: {e}")
            raise
    
    # Generate comparison summary
    if summaries:
        generate_comparison_summary(summaries, args.output_dir, args.dataset)
    else:
        print("\n⚠️  No methods successfully processed.")


if __name__ == "__main__":
    main()