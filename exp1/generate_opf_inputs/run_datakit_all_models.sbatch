#!/bin/bash
#SBATCH --partition=barnard
#SBATCH --cpus-per-task=64
#SBATCH --mem=450G
#SBATCH --time=02:00:00
#SBATCH --job-name=datakit_case14
#SBATCH --output=logs/datakit_case14_%j.log

cd /home/h4/tibo990i/gridfm-datakit

CONFIG="${1:-exp1/configs/case14_generate_opf_for_forecast_xgb.yaml}"

if [ ! -f "$CONFIG" ]; then
    echo "Error: Config file not found: $CONFIG"
    exit 1
fi

echo "=========================================="
echo "Config: $CONFIG"
echo "Start: $(date)"
echo "=========================================="

python -m gridfm_datakit.cli generate --config "$CONFIG"

echo "=========================================="
echo "End: $(date)"
echo "=========================================="
