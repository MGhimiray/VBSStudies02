#!/bin/sh

export path="fillhisto_zAnalysis1001"
export year=2022
export output="anaZ"

if [ $# -lt 1 ]; then
   echo "TOO FEW PARAMETERS"
   exit
fi

export year=$1

if [ $# -eq 2 ]; then
  export path="fillhisto_zAnalysis"$2
fi

hadd -f ${output}/${path}_${year}_muB.root ${output}/${path}_${year}_128.root ${output}/${path}_${year}_129.root
hadd -f ${output}/${path}_${year}_muE.root ${output}/${path}_${year}_130.root ${output}/${path}_${year}_131.root
hadd -f ${output}/${path}_${year}_elB.root ${output}/${path}_${year}_132.root ${output}/${path}_${year}_133.root
hadd -f ${output}/${path}_${year}_elE.root ${output}/${path}_${year}_134.root ${output}/${path}_${year}_135.root

python3 computeLeptonEff.py --path=${path} --year=${year} --output=${output}
