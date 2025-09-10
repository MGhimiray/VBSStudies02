#!/usr/bin/env bash
set -uo pipefail

year="${1:?Usage: $0 <2022|2023|2024>}"
command -v hadd >/dev/null || { echo "ERROR: hadd not found in PATH"; exit 1; }

# for dir in {1001..1009}; do
for dir in 1001; do
  inputdir="/mnt/home/mghimiray/VBSStudies/Outputs_VBS/matrix_method/${dir}/histo/fillhisto_sswwAnalysis"
  outdir="/mnt/home/mghimiray/VBSStudies/Outputs_VBS/OriginalTT/${dir}/histo/fillhisto_sswwAnalysis"
  mkdir -p "$outdir"

  for i in {0..9}; do
    echo "Processing job index $i for year $year"

    if [[ "$year" == "2023" ]]; then
      for sample in 1022 1032 1042; do
        in1="$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year202301_job${i}.root"
        in2="$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20230_job${i}.root"
        out="$outdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20230_job${i}.root"
        if [[ -f "$in1" && -f "$in2" ]]; then
          echo "hadd -> $out"
          hadd -f "$out" "$in1" "$in2"
        else
          echo "SKIP (missing): $in1 or $in2"
        fi
      done
      for sample in 1023 1033 1043; do
        in1="$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year202311_job${i}.root"
        in2="$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20231_job${i}.root"
        out="$outdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20231_job${i}.root"
        if [[ -f "$in1" && -f "$in2" ]]; then
          echo "hadd -> $out"
          hadd -f "$out" "$in1" "$in2"
        else
          echo "SKIP (missing): $in1 or $in2"
        fi
      done

    elif [[ "$year" == "2024" ]]; then
      for sample in 1022 1023 1024 1025 1026 1027 1028 1032 1033 1034 1035 1036 1037 1038 1042 1043 1044 1045 1046 1047 1048; do
        in1="$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year202401_job${i}.root"
        in2="$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20240_job${i}.root"
        out="$outdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20240_job${i}.root"
        if [[ -f "$in1" && -f "$in2" ]]; then
          echo "hadd -> $out"
          hadd -f "$out" "$in1" "$in2"
        else
          echo "SKIP (missing): $in1 or $in2"
        fi
      done

    elif [[ "$year" == "2022" ]]; then
      for sample in 1001 1002 1011 1012 1021 1022 1023 1031 1032 1033 1042 1043; do
        in1="$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year202201_job${i}.root"
        in2="$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20220_job${i}.root"
        out="$outdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20220_job${i}.root"
        if [[ -f "$in1" && -f "$in2" ]]; then
          echo "hadd -> $out"
          hadd -f "$out" "$in1" "$in2"
        else
          echo "SKIP (missing): $in1 or $in2"
        fi
      done
      for sample in 1024 1025 1026 1034 1035 1036 1044 1045 1046; do
        in1="$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year202211_job${i}.root"
        in2="$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20221_job${i}.root"
        out="$outdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20221_job${i}.root"
        if [[ -f "$in1" && -f "$in2" ]]; then
          echo "hadd -> $out"
          hadd -f "$out" "$in1" "$in2"
        else
          echo "SKIP (missing): $in1 or $in2"
        fi
      done

    else
      echo "Unsupported year: $year" >&2
      exit 2
    fi
  done
done
