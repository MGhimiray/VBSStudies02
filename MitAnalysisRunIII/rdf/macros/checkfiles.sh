#!/usr/bin/env bash
# Usage: ./checkfiles.sh <year> <whichana>
# Example: ./checkfiles.sh 2022 1001
# Optional: DRYRUN=1 ./checkfiles.sh ...

set -uo pipefail

year=${1:?Usage: $0 YEAR WHICHANA}
whichana=${2:?Usage: $0 YEAR WHICHANA}

# Verify the capitalization ("matrix_method" vs "Matrix_method") matches your FS.
outdir="/mnt/home/mghimiray/VBSStudies/Outputs_VBS/matrix_method/${whichana}/histo/fillhisto_sswwAnalysis"

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
    samples["20230"]="1022 1032 1042"
    samples["20231"]="1023 1033 1043"
    ;;
  2024)
    tags=(20240)
    common="1022 1023 1024 1025 1026 1027 1028 1032 1033 1034 1035 1036 1037 1038 1042 1043 1044 1045 1046 1047 1048"
    samples["20240"]="$common"
    ;;
  2022)
    tags=(20220 20221)
    samples["20220"]="1001 1002 1011 1012 1021 1022 1023 1031 1032 1033 1042 1043"
    samples["20221"]="1024 1025 1026 1034 1035 1036 1044 1045 1046"
    ;;
  *)
    echo "Unsupported year: $year"
    exit 3
    ;;
esac

# Helper: infer the highest completed job index already present for a (tag, sample).
# Returns -1 if none found.
get_max_seen_job() {
  local tag="$1" sample="$2"
  shopt -s nullglob
  local arr=( "$outdir"/fillhisto_sswwAnalysis1001_sample"${sample}"_year"${tag}"1_job*.root )
  shopt -u nullglob
  local max=-1 f
  for f in "${arr[@]}"; do
    if [[ "$f" =~ _job([0-9]+)\.root$ ]]; then
      local j="${BASH_REMATCH[1]}"
      (( j > max )) && max="$j"
    fi
  done
  echo "$max"
}

missing_detail=()            # rows: "year whichana tag sample job path"
declare -A missing_pairs     # keys: "tag sample"
total_expected=0
total_found=0

for tag in "${tags[@]}"; do
  for sample in ${samples[$tag]}; do
    for job in $jobs_list; do
      f="$outdir/fillhisto_sswwAnalysis${whichana}_sample${sample}_year${tag}1_job${job}.root"
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

    # Heuristic: if we already have some outputs for this (tag,sample),
    # don't bother resubmitting jobs above the max seen index (likely empty shards).
    max_seen=$(get_max_seen_job "$tag" "$sample")
    if (( max_seen >= 0 && job > max_seen )); then
      echo "skip: $tag $sample job $job (no input group; max seen job index is $max_seen)"
      continue
    fi

    echo "./submit_cis_analysis.sh $tag $sample $job"
    if [[ -z "${DRYRUN:-}" ]]; then
      sbatch -p INTEL_HASWELL --time=70:00:00 --cpus-per-task=1 --nodes=1 \
             --job-name="vbsmatrixmethod_${year}_${sample}_${job}" \
             --output="log/vbs__${year}_${sample}_${job}.out" \
             --error="log/vbs__${year}_${sample}_${job}.err" \
             submit_cis_analysis.sh "$tag" "$sample" "$job" \
        || echo "  (warn) submit failed for $tag $sample $job"
    fi
  done < <(printf "%s\n" "${missing_detail[@]}")

  exit 1
else
  echo " All expected files are present."
fi
