#!/bin/sh

export path="fillhisto_zAnalysis1001"
export year=2018
export output="anaZ"

if [ $# -lt 1 ]; then
   echo "TOO FEW PARAMETERS"
   exit
fi

export year=$1

if [ $# -eq 2 ]; then
  export path="fillhisto_zAnalysis"$2
fi

hadd -f ${output}/${path}_${year}_loose_mu_2d.root ${output}/${path}_${year}_0_2d.root ${output}/${path}_${year}_10_2d.root
hadd -f ${output}/${path}_${year}_tightmu0_2d.root ${output}/${path}_${year}_1_2d.root ${output}/${path}_${year}_11_2d.root
hadd -f ${output}/${path}_${year}_tightmu1_2d.root ${output}/${path}_${year}_2_2d.root ${output}/${path}_${year}_12_2d.root
hadd -f ${output}/${path}_${year}_tightmu2_2d.root ${output}/${path}_${year}_3_2d.root ${output}/${path}_${year}_13_2d.root
hadd -f ${output}/${path}_${year}_tightmu3_2d.root ${output}/${path}_${year}_4_2d.root ${output}/${path}_${year}_14_2d.root
hadd -f ${output}/${path}_${year}_tightmu4_2d.root ${output}/${path}_${year}_5_2d.root ${output}/${path}_${year}_15_2d.root
hadd -f ${output}/${path}_${year}_tightmu5_2d.root ${output}/${path}_${year}_6_2d.root ${output}/${path}_${year}_16_2d.root
hadd -f ${output}/${path}_${year}_tightmu6_2d.root ${output}/${path}_${year}_7_2d.root ${output}/${path}_${year}_17_2d.root
hadd -f ${output}/${path}_${year}_tightmu7_2d.root ${output}/${path}_${year}_8_2d.root ${output}/${path}_${year}_18_2d.root
hadd -f ${output}/${path}_${year}_tightmu8_2d.root ${output}/${path}_${year}_9_2d.root ${output}/${path}_${year}_19_2d.root

hadd -f ${output}/${path}_${year}_loose_el_2d.root ${output}/${path}_${year}_20_2d.root ${output}/${path}_${year}_30_2d.root
hadd -f ${output}/${path}_${year}_tightel0_2d.root ${output}/${path}_${year}_21_2d.root ${output}/${path}_${year}_31_2d.root
hadd -f ${output}/${path}_${year}_tightel1_2d.root ${output}/${path}_${year}_22_2d.root ${output}/${path}_${year}_32_2d.root
hadd -f ${output}/${path}_${year}_tightel2_2d.root ${output}/${path}_${year}_23_2d.root ${output}/${path}_${year}_33_2d.root
hadd -f ${output}/${path}_${year}_tightel3_2d.root ${output}/${path}_${year}_24_2d.root ${output}/${path}_${year}_34_2d.root
hadd -f ${output}/${path}_${year}_tightel4_2d.root ${output}/${path}_${year}_25_2d.root ${output}/${path}_${year}_35_2d.root
hadd -f ${output}/${path}_${year}_tightel5_2d.root ${output}/${path}_${year}_26_2d.root ${output}/${path}_${year}_36_2d.root
hadd -f ${output}/${path}_${year}_tightel6_2d.root ${output}/${path}_${year}_27_2d.root ${output}/${path}_${year}_37_2d.root
hadd -f ${output}/${path}_${year}_tightel7_2d.root ${output}/${path}_${year}_28_2d.root ${output}/${path}_${year}_38_2d.root
hadd -f ${output}/${path}_${year}_tightel8_2d.root ${output}/${path}_${year}_29_2d.root ${output}/${path}_${year}_39_2d.root

python3 computeLeptonEff_2d.py --path=${path} --year=${year} --output=${output}
