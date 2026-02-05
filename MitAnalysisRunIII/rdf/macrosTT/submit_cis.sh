#!/bin/bash

# Define mapping between years and corresponding processes
# to run ./submit_cis.sh year (year = 2022/2023/2024)
whichyear=$1
if [ "$whichyear" = "2023" ]; then
    declare -A year_process_map
    year_process_map["20230"]="1022 1032 1042"
    year_process_map["20231"]="1023 1033 1043"
    which_job="0 1 2 3 4 5 6 7 8 9"
elif [ "$whichyear" = "2024" ]; then
    year_process_map["20240"]="1022 1023 1024 1025 1026 1027 1028 1032 1033 1034 1035 1036 1037 1038 1042 1043 1044 1045 1046 1047 1048"
    which_job="0 1 2 3 4 5 6 7 8 9"
elif [ "$whichyear" = "2022" ]; then
    year_process_map["20220"]="1001 1002 1011 1012 1021 1022 1023 1031 1032 1033 1042 1043 "
    year_process_map["20221"]="1024 1025 1026 1034 1035 1036 1044 1045 1046 "
    which_job="0 1 2 3 4 5 6 7 8 9"
elif [ "$whichyear" = "2025" ]; then
    year_process_map["20250"]="1021 1022 1023 1024 1025 1026 1031 1032 1033 1034 1035 1036 1041 1042 1043 1044 1045 1046"
    which_job="0 1 2 3 4 5 6 7 8 9"
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
               --job-name="vbsTT_${year}_${process}_${jobs}" \
               --output="log/vbs__${year}_${process}_${jobs}.out" \
               --error="log/vbs__${year}_${process}_${jobs}.err" \
               submit_cis_analysis.sh "$year" "$process" "$jobs"
    done
    done
done
