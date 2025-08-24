#!/bin/bash

for file in /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/merge1/1001/fillhisto_sswwAnalysis_2023*.root; do 
  newfile=$(echo "$file" | sed 's/sswwAnalysis_/sswwAnalysis1001_/') 
  mv "$file" "$newfile" 
done 
