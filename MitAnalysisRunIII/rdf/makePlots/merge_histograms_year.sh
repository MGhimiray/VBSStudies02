#!/bin/sh

if [ $# -lt 3 ]; then
   echo "TOO FEW PARAMETERS"
   exit
fi

theAna=$1;
theCondor=$2;
theYear=$3;
group=10
outdir="/mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge3"
mkdir -p "$outdir"

if [ ${theYear} = 2027 ]; then

for i in `seq 0 600`;
do
    if [[ -f /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/${theAna}${theCondor}_20220_${i}.root ]]; then

    hadd -f ${outdir}/${theAna}${theCondor}_${theYear}_${i}.root /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/${theAna}${theCondor}_2022?_${i}.root /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/${theAna}${theCondor}_2023?_${i}.root /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/${theAna}${theCondor}_2024?_${i}.root

    fi
 
    if [[ -f /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/${theAna}${theCondor}_20220_${i}_2d.root ]]; then

     hadd -f ${outdir}/${theAna}${theCondor}_${theYear}_${i}_2d.root /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/${theAna}${theCondor}_2022?_${i}_2d.root /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/${theAna}${theCondor}_2023?_${i}_2d.root /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/${theAna}${theCondor}_2024?_${i}_2d.root

    fi

done

else

for i in `seq 0 600`;
do
    if [[ -f /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/${theAna}${theCondor}_${theYear}0_${i}.root ]]; then

     hadd -f ${outdir}/${theAna}${theCondor}_${theYear}_${i}.root /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/${theAna}${theCondor}_${theYear}?_${i}.root

    fi

    if [[ -f /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/${theAna}${theCondor}_${theYear}0_${i}_2d.root ]]; then

     hadd -f ${outdir}/${theAna}${theCondor}_${theYear}_${i}_2d.root /mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge1/${theAna}${theCondor}_${theYear}?_${i}_2d.root

    fi

done

fi
