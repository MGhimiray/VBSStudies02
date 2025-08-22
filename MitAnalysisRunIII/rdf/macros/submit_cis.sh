#!/bin/bash

# Define mapping between years and corresponding processes
declare -A year_process_map
year_process_map["20230"]="1022 1032 1042"
year_process_map["20231"]="1023 1033 1043"
which_job="0 1 2 3 4 5 6 7 8 9"

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
               --job-name="vbs_${year}_${process}_${jobs}" \
               --output="log/vbs_${year}_${process}_${jobs}.out" \
               --error="log/vbs_${year}_${process}_${jobs}.err" \
               submit_cis_analysis.sh "$year" "$process" "$jobs"
    done
    done
done
