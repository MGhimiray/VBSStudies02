#!/bin/bash

for dir in 1001 1002; do
  for file in /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/${dir}/merge1/fillhisto_sswwAnalysis_2022*.root; do
    newfile=$(echo "$file" | sed "s/sswwAnalysis_/sswwAnalysis${dir}_/")
    mv "$file" "$newfile"
  done
done
