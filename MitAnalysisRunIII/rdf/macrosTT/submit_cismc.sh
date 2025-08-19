#!/bin/bash

# Define mapping between years and corresponding processes
declare -A year_process_map
year_process_map["20230"]="311 312 314 315 316 317 319 320 333 334 335 356 357 374 375 376 377 378 379 382 383"
year_process_map["20231"]="411 412 414 415 416 417 419 420 433 434 435 456 457 474 475 476 477 478 479 482 483"
which_job="0 1 2 3 4 5 6 7 8 9"

#
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
               --job-name="vbsmcTT_${year}_${process}_${jobs}" \
               --output="log/vbs__${year}_${process}_${jobs}.out" \
               --error="log/vbs__${year}_${process}_${jobs}.err" \
               submit_cis_analysis.sh "$year" "$process" "$jobs"
    done
    done
done
