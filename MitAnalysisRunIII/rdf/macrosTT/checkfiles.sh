#!/usr/bin/env bash
# Usage: ./checkfiles.sh <year> <whichana>
# Example: ./checkfiles.sh 2022 1001
# Optional: DRYRUN=1 ./checkfiles.sh ...

set -uo pipefail

year=${1:?Usage: $0 YEAR WHICHANA}
whichana=${2:?Usage: $0 YEAR WHICHANA}

outdir="/mnt/home/mghimiray/VBSStudies/Outputs_VBSwz/OriginalTT/${whichana}/histo/fillhisto_sswwAnalysis"

echo "== Check files =="
echo " year     : $year"
echo " whichana : $whichana"
echo " outdir   : $outdir"
echo

if [[ ! -d "$outdir" ]]; then
  echo "ERROR: Output dir not found: $outdir"
  exit 2
fi

# Jobs we expect to exist (0..9)
jobs_list=$(seq 0 9)

# Map of <yearTag> -> <samples>
declare -A samples
declare -a tags
case "$year" in
  2023)
    tags=(20230 20231)
    samples["20230"]="300 304 305 308 311 312 314 315 316 317 318 319 320 321 322 323 324 333 334 335 337 338 344 345 346 347 348 349 353 354 355 356 357 359 360 361 362 363 364 374 375 376 377 378 379 380 381 382 383"
    samples["20231"]="400 404 405 408 411 412 414 415 416 417 418 419 420 421 422 423 424 433 434 435 437 438 444 445 446 447 448 449 453 454 455 456 457 459 460 461 462 463 464 474 475 476 477 478 479 480 481 482 483"
    ;;
  2024)
    tags=(20240)
    common="500 525 527 501 526 528 504 505 508 511 512 514 515 516 517 521 522 537 538 553 554 555 565 566 567 568 569 570 571 572 573 574 575 576 577 578 579 580 581 582 583 586 587 588"
    samples["20240"]="$common"
    ;;
  2022)
    tags=(20220 20221)
    samples["20220"]="100 104 105 108 111 112 114 115 116 117 118 119 120 121 122 123 124 133 134 135 137 138 144 145 146 147 148 149 153 154 155 156 157 159 160 161 162 163 164 174 175 176 177 178 179 180 181 182 183"
    samples["20221"]="200 204 205 208 211 212 214 215 216 217 218 219 220 221 222 223 224 233 234 235 237 238 244 245 246 247 248 249 253 254 255 256 257 259 260 261 262 263 264 274 275 276 277 278 279 280 281 282 283"
    ;;
  *)
    echo "Unsupported year: $year"
    exit 3
    ;;
esac

# Helper: infer the highest completed job index already present for a (tag, sample).
# Prints -1 if none found.
get_max_seen_job() {
  local tag="$1" sample="$2"

  # Collect matches safely
  shopt -s nullglob
  local -a arr
  arr=( "$outdir"/fillhisto_wzAnalysis1001_sample"${sample}"_year"${tag}"_job*.root )
#  arr=( "$outdir"/fillhisto_sswwAnalysis"${whichana}"_sample"${sample}"_year"${tag}"_job*.root )
  shopt -u nullglob

  local max=-1
  local f
  if ((${#arr[@]})); then
    for f in "${arr[@]}"; do
      if [[ "$f" =~ _job([0-9]+)\.root$ ]]; then
        local j="${BASH_REMATCH[1]}"
        (( j > max )) && max="$j"
      fi
    done
  fi

  echo "$max"
}

missing_detail=()            # rows: "year whichana tag sample job path"
declare -A missing_pairs     # keys: "tag sample"
total_expected=0
total_found=0

for tag in "${tags[@]}"; do
  for sample in ${samples[$tag]}; do
    for job in $jobs_list; do
      f="$outdir/fillhisto_wzAnalysis1001_sample${sample}_year${tag}_job${job}.root"
      (( total_expected++ ))
      if [[ -s "$f" ]]; then
        (( total_found++ ))
      else
        echo "MISSING: $f"
        missing_detail+=("$year $whichana $tag $sample $job $f")
        missing_pairs["$tag $sample"]=1
      fi
    done
  done
done

echo
echo "== Summary =="
echo " Found $total_found / $total_expected files in:"
echo "   $outdir"

if ((${#missing_detail[@]})); then
  echo
  echo " -- Missing files (detailed) --"
  printf "year whichana tag sample job path\n"
  printf "%s\n" "${missing_detail[@]}"

  echo
  echo " -- Missing (yearTag, sample) pairs --"
  for k in "${!missing_pairs[@]}"; do
    printf "%s\n" "$k"
  done | sort -V

  # === Resubmit exactly the missing jobs, but skip "empty groups" ===
  echo
  echo " -- Resubmitting missing jobs --"
  declare -A submitted
  mkdir -p log
  while read -r y wa tag sample job path; do
    key="$tag $sample $job"
    [[ -n "${submitted[$key]:-}" ]] && continue
    submitted["$key"]=1

    # If we already have some outputs for this (tag,sample),
    # don't resubmit jobs above the max seen index (likely empty shards).
    max_seen=$(get_max_seen_job "$tag" "$sample")
    if (( max_seen >= 0 && job > max_seen )); then
      echo "skip: $tag $sample job $job (no input group; max seen job index is $max_seen)"
      continue
    fi

    echo "./submit_cis_analysis.sh $tag $sample $job"
    if [[ -z "${DRYRUN:-}" ]]; then
      command -v sbatch >/dev/null 2>&1 || { echo "ERROR: sbatch not found in PATH"; exit 4; }
      sbatch -p INTEL_HASWELL --time=70:00:00 --cpus-per-task=1 --nodes=1 \
             --job-name="vbsoriginalTT_${tag}_${sample}_${job}" \
             --output="log/vbs__${tag}_${sample}_${job}.out" \
             --error="log/vbs__${tag}_${sample}_${job}.err" \
             submit_cis_analysis.sh "$tag" "$sample" "$job" \
        || echo "  (warn) submit failed for $tag $sample $job"
    fi
  done < <(printf "%s\n" "${missing_detail[@]}")

  exit 1
else
  echo " All expected files are present."
fi
