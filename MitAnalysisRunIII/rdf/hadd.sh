#!/bin/bash

for dir in {1001..1009}; do
  inputdir="/mnt/home/mghimiray/VBSStudies/Outputs_VBS/matrix_method/${dir}/histo/fillhisto_sswwAnalysis"
  outdir="/mnt/home/mghimiray/VBSStudies/Outputs_VBS/OriginalTT/${dir}/histo/fillhisto_sswwAnalysis"

  for i in {0..9}; do
    echo "Processing job index $i"
  
    for sample in 1022 1032 1042; do
      year=20230
      hadd "$outdir/fillhisto_sswwAnalysis1001_sample${sample}_year${year}_job${i}.root" \
           "$inputdir/fillhisto_sswwAnalysis1001_sample${sample}_year${year}1_job${i}.root" \
           "$inputdir/fillhisto_sswwAnalysis1001_sample${sample}_year${year}_job${i}.root"
    done
  
    for sample in 1023 1033 1043; do
      year=20231
      hadd "$outdir/fillhisto_sswwAnalysis1001_sample${sample}_year${year}_job${i}.root" \
           "$inputdir/fillhisto_sswwAnalysis1001_sample${sample}_year${year}1_job${i}.root" \
           "$inputdir/fillhisto_sswwAnalysis1001_sample${sample}_year${year}_job${i}.root"
    done
  
  done
done
