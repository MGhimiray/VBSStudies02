#!/bin/bash

for file in /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/fillhisto_sswwAnalysis_2022*.root; do 
  newfile=$(echo "$file" | sed 's/sswwAnalysis_/sswwAnalysis1001_/') 
  mv "$file" "$newfile" 
done 
