#!/bin/bash
#SBATCH --job-name=gridfm_datakit_gen
#SBATCH --partition=paul
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=02:00:00

#SBATCH --output=logs/datakit_gen_%j.out
#SBATCH --error=logs/datakit_gen_%j.err

# --- Configuration ---
VENV_PATH="$SLURM_SUBMIT_DIR/../thesis_env"
# CONFIG="phase1_generation/configs/phase1_config.yaml"
CONFIG="exp1/configs/cluster_leipzig_opf_for_forecast.yaml"
# ---------------------

module purge
module load Anaconda3

source $VENV_PATH/bin/activate

# Execute the datakit generation pipeline
srun python -m gridfm_datakit.cli generate $CONFIG
