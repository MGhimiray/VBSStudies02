#!/bin/bash

# Define mapping between years and corresponding processes
whichyear=$1
if [ "$whichyear" = "2023" ]; then
    declare -A year_process_map
    year_process_map["20230"]="300 304 305 308 311 312 314 315 316 317 318 319 320 321 322 323 324 333 334 335 337 338 344 345 346 347 348 349 353 354 355 356 357 359 360 361 362 363 364 374 375 376 377 378 379 380 381 382 383"
    year_process_map["20231"]="400 404 405 408 411 412 414 415 416 417 418 419 420 421 422 423 424 433 434 435 437 438 444 445 446 447 448 449 453 454 455 456 457 459 460 461 462 463 464 474 475 476 477 478 479 480 481 482 483"
    which_job="0 1 2 3 4 5 6 7 8 9"
elif [ "$whichyear" = "2024" ]; then
    year_process_map["20240"]="500 525 527 501 526 528 504 505 508 511 512 514 515 516 517 521 522 537 538 553 554 555 565 566 567 568 569 570 571 572 573 574 575 576 577 578 579 580 581 582 583 586 587 588 "
    which_job="0 1 2 3 4 5 6 7 8 9"
elif [ "$whichyear" = "2022" ]; then
    year_process_map["20220"]="100 104 105 108 111 112 114 115 116 117 118 119 120 121 122 123 124 133 134 135 137 138 144 145 146 147 148 149 153 154 155 156 157 159 160 161 162 163 164 174 175 176 177 178 179 180 181 182 183"
    year_process_map["20221"]="200 204 205 208 211 212 214 215 216 217 218 219 220 221 222 223 224 233 234 235 237 238 244 245 246 247 248 249 253 254 255 256 257 259 260 261 262 263 264 274 275 276 277 278 279 280 281 282 283"
    which_job="0 1 2 3 4 5 6 7 8 9"
fi

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
