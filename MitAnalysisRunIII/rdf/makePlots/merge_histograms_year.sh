#!/bin/sh

if [ $# -lt 3 ]; then
   echo "TOO FEW PARAMETERS"
   exit
fi

theAna=$1;
theCondor=$2;
theYear=$3;
group=9

if [ ${theYear} = 2027 ]; then

for i in `seq 0 600`;
do
    if [[ -f anaZ/${theAna}${theCondor}_20220_${i}.root ]]; then

    hadd -f anaZ/${theAna}${theCondor}_${theYear}_${i}.root anaZ/${theAna}${theCondor}_2022?_${i}.root anaZ/${theAna}${theCondor}_2023?_${i}.root anaZ/${theAna}${theCondor}_2024?_${i}.root

    fi
 
    if [[ -f anaZ/${theAna}${theCondor}_20220_${i}_2d.root ]]; then

    hadd -f anaZ/${theAna}${theCondor}_${theYear}_${i}_2d.root anaZ/${theAna}${theCondor}_2022?_${i}_2d.root anaZ/${theAna}${theCondor}_2023?_${i}_2d.root anaZ/${theAna}${theCondor}_2024?_${i}_2d.root

    fi

done

else

for i in `seq 0 600`;
do
    if [[ -f anaZ/${theAna}${theCondor}_${theYear}0_${i}.root ]]; then

    hadd -f anaZ/${theAna}${theCondor}_${theYear}_${i}.root anaZ/${theAna}${theCondor}_${theYear}?_${i}.root

    fi

    if [[ -f anaZ/${theAna}${theCondor}_${theYear}0_${i}_2d.root ]]; then

    hadd -f anaZ/${theAna}${theCondor}_${theYear}_${i}_2d.root anaZ/${theAna}${theCondor}_${theYear}?_${i}_2d.root

    fi

done

fi
