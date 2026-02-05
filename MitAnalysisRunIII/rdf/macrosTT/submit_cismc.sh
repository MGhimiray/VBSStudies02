#!/bin/bash

# Define mapping between years and corresponding processes
whichyear=$1
if [ "$whichyear" = "2023" ]; then
    declare -A year_process_map
    year_process_map["20230"]="300 304 305 308 311 312 314 315 316 317 318 319 320 321 322 323 324 329 330 331 332 333 334 335 337 338 339 340 341 344 345 346 347 348 349 353 354 355 356 357 359 360 361 362 363 364 374 375 376 377 378 379 380 381 382 383 389 390 393 394 "
    year_process_map["20231"]="400 404 405 408 411 412 414 415 416 417 418 419 420 421 422 423 424 429 430 431 432 433 434 435 437 438 439 440 441 444 445 446 447 448 449 453 454 455 456 457 459 460 461 462 463 464 474 475 476 477 478 479 480 481 482 483 489 490 493 494"
    which_job="0 1 2 3 4 5 6 7 8 9"
elif [ "$whichyear" = "2024" ]; then
    year_process_map["20240"]="500 525 527 501 526 528 504 505 508 511 512 514 515 516 517 518 519 520 521 522 523 524 529 530 531 532 534 535 537 538 539 540 541 548 549 553 554 555 556 557 565 566 567 568 569 570 571 572 573 574 575 576 577 578 579 580 581 582 583 586 587 588 589 590 591 593 594"
    which_job="0 1 2 3 4 5 6 7 8 9"
elif [ "$whichyear" = "2022" ]; then
    year_process_map["20220"]="100 104 105 108 111 112 114 115 116 117 118 119 120 121 122 123 124 129 130 131 132 133 134 135 137 138 139 140 141 144 145 146 147 148 149 153 154 155 156 157 159 160 161 162 163 164 174 175 176 177 178 179 180 181 182 183 189 190 193 194"
    year_process_map["20221"]="200 204 205 208 211 212 214 215 216 217 218 219 220 221 222 223 224 229 230 231 232 233 234 235 237 238 239 240 241 244 245 246 247 248 249 253 254 255 256 257 259 260 261 262 263 264 274 275 276 277 278 279 280 281 282 283 289 290 293 294"
    which_job="0 1 2 3 4 5 6 7 8 9"
elif [ "$whichyear" = "2025" ]; then
    year_process_map["20250"]="600 625 627 601 626 628 604 605 608 611 612 614 615 616 617 618 619 620 621 622 623 624 629 630 631 632 634 635 637 638 639 640 641 648 649 653 654 655 656 657 665 666 667 668 669 670 671 672 673 674 675 676 677 678 679 680 681 682 683 686 687 688 689 690 691 693 694"
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
               --job-name="vbsmcTT_${year}_${process}_${jobs}" \
               --output="log/vbs__${year}_${process}_${jobs}.out" \
               --error="log/vbs__${year}_${process}_${jobs}.err" \
               submit_cis_analysis.sh "$year" "$process" "$jobs"
    done
    done
done
