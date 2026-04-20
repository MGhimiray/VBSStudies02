#!/bin/bash

for dir in 1001; do
  for file in /mnt/home/mghimiray/VBSStudies/Outputs_VBS/EFT2026/${dir}/merge1/fillhisto_sswwAnalysis_202*.root; do
    newfile=$(echo "$file" | sed "s/sswwAnalysis_/sswwAnalysis${dir}_/")
    mv "$file" "$newfile"
  done
done
