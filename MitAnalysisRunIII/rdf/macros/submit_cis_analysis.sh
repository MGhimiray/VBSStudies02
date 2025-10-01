#!/bin/bash
#SBATCH --partition=INTEL_HASWELL
#SBATCH --time=70:00:00
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --job-name="vbstf"
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

# activating the vev 
eval "$(/mnt/home/mghimiray/miniforge3/bin/conda shell.bash hook)"
conda activate myenv

# Get the input file and output directory from the command line
years=$1
processes=$2
which_job=$3


# Run the Python script with input file and output directory as arguments
#python3 sswwAnalysis.py --year="$years" --process="$processes" --whichJob="$which_job"
python3 wzAnalysis.py --year="$years" --process="$processes" --whichJob="$which_job"
#python3 sswwAnalysis.py --year=20220 --process=1022 --whichJob=0