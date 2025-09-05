#!/bin/bash

year=$1

#for dir in {1001..1009}; do
for dir in {1001};do
  inputdir="/mnt/home/mghimiray/VBSStudies/Outputs_VBS/matrix_method/${dir}/histo/fillhisto_sswwAnalysis"
  outdir="/mnt/home/mghimiray/VBSStudies/Outputs_VBS/OriginalTT/${dir}/histo/fillhisto_sswwAnalysis"

  for i in {0..9}; do
    echo "Processing job index $i for year $year"

    if [ "$year" == "2023" ]; then

      for sample in 1022 1032 1042; do
        hadd "$outdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20230_job${i}.root" \
             "$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year202301_job${i}.root" \
             "$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20230_job${i}.root"
      done

      for sample in 1023 1033 1043; do
        hadd "$outdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20231_job${i}.root" \
             "$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year202311_job${i}.root" \
             "$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20231_job${i}.root"
      done

    elif [ "$year" == "2024" ]; then

      for sample in 1022 1023 1024 1025 1026 1027 1028 1032 1033 1034 1035 1036 1037 1038 1042 1043 1044 1045 1046 1047 1048; do
        hadd "$outdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20240_job${i}.root" \
             "$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year202401_job${i}.root" \
             "$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20240_job${i}.root"
      done

      for sample in 1022 1023 1024 1025 1026 1027 1028 1032 1033 1034 1035 1036 1037 1038 1042 1043 1044 1045 1046 1047 1048; do
        hadd "$outdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20241_job${i}.root" \
             "$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year202411_job${i}.root" \
             "$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20241_job${i}.root"
      done

    elif [ "$year" == "2022" ]; then

      for sample in 1001 1002 1011 1012 1021 1022 1023 1031 1032 1033 1042 1043; do
        hadd "$outdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20220_job${i}.root" \
             "$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year202201_job${i}.root" \
             "$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20220_job${i}.root"
      done

      for sample in 1024 1025 1026 1034 1035 1036 1044 1045 1046; do
        hadd "$outdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20221_job${i}.root" \
             "$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year202211_job${i}.root" \
             "$inputdir/fillhisto_sswwAnalysis${dir}_sample${sample}_year20221_job${i}.root"
      done

    else
      echo "Unsupported year: $year"
    fi

  done
done
