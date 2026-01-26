#!/bin/bash

# Define mapping between years and corresponding processes
whichyear=$1
if [ "$whichyear" = "2023" ]; then
    declare -A year_process_map
    year_process_map["20230"]="392"
    year_process_map["20231"]="492"
    which_job="-1"
elif [ "$whichyear" = "2024" ]; then
    year_process_map["20240"]="592"
    which_job="-1"
elif [ "$whichyear" = "2022" ]; then
    year_process_map["20220"]="192"
    year_process_map["20221"]="292"
    which_job="-1"
fi


# Iterate over each year
for year in "${!year_process_map[@]}"; do
    echo "Year: $year"

    # Get the processes for this year
    processes=${year_process_map[$year]}

    # Iterate over processes
    for process in $processes; do
        for jobs in $which_job; do
        echo "Submitting: Year=$year, Process=$process", "Job=$jobs"
        sbatch -p INTEL_HASWELL --time=70:00:00 --cpus-per-task=1 --nodes=1 \
               --job-name="vbsgen_${year}_${process}_${jobs}" \
               --output="loggen/vbs__${year}_${process}_${jobs}.out" \
               --error="loggen/vbs__${year}_${process}_${jobs}.err" \
               submit_cis_genAnalysis.sh "$year" "$process" 
    done
    done
done
