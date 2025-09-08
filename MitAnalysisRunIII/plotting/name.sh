#!/bin/bash
year=$1
for dir in 1001; do
  for file in /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/${dir}/merge1/fillhisto_sswwAnalysis_${year}*.root; do
    newfile=$(echo "$file" | sed "s/sswwAnalysis_/sswwAnalysis${dir}_/")
    mv "$file" "$newfile"
  done
done
