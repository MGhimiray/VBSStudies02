#!/bin/sh

if [ $# -lt 2 ]; then
   echo "TOO FEW PARAMETERS"
   exit
fi

export option=$1
export path="fillhisto_zAnalysis1001"
export year=$2
export output="anaZ"

if [ $# -eq 3 ]; then
  export path="fillhisto_zAnalysis"$3
fi

if [ $option -eq 0 ]; then

export bins=15
hadd -f ${output}/${path}_${year}_ele_os_0.root  ${output}/${path}_${year}_60.root
hadd -f ${output}/${path}_${year}_ele_os_1.root  ${output}/${path}_${year}_62.root ${output}/${path}_${year}_70.root
hadd -f ${output}/${path}_${year}_ele_os_2.root  ${output}/${path}_${year}_64.root ${output}/${path}_${year}_80.root
hadd -f ${output}/${path}_${year}_ele_os_3.root  ${output}/${path}_${year}_66.root ${output}/${path}_${year}_90.root
hadd -f ${output}/${path}_${year}_ele_os_4.root  ${output}/${path}_${year}_68.root ${output}/${path}_${year}_100.root
hadd -f ${output}/${path}_${year}_ele_os_5.root  ${output}/${path}_${year}_72.root
hadd -f ${output}/${path}_${year}_ele_os_6.root  ${output}/${path}_${year}_74.root ${output}/${path}_${year}_82.root
hadd -f ${output}/${path}_${year}_ele_os_7.root  ${output}/${path}_${year}_76.root ${output}/${path}_${year}_92.root
hadd -f ${output}/${path}_${year}_ele_os_8.root  ${output}/${path}_${year}_78.root ${output}/${path}_${year}_102.root
hadd -f ${output}/${path}_${year}_ele_os_9.root  ${output}/${path}_${year}_84.root
hadd -f ${output}/${path}_${year}_ele_os_10.root ${output}/${path}_${year}_86.root ${output}/${path}_${year}_94.root
hadd -f ${output}/${path}_${year}_ele_os_11.root ${output}/${path}_${year}_88.root ${output}/${path}_${year}_104.root
hadd -f ${output}/${path}_${year}_ele_os_12.root ${output}/${path}_${year}_96.root
hadd -f ${output}/${path}_${year}_ele_os_13.root ${output}/${path}_${year}_98.root ${output}/${path}_${year}_106.root
hadd -f ${output}/${path}_${year}_ele_os_14.root ${output}/${path}_${year}_108.root

hadd -f ${output}/${path}_${year}_ele_ss_0.root  ${output}/${path}_${year}_61.root
hadd -f ${output}/${path}_${year}_ele_ss_1.root  ${output}/${path}_${year}_63.root ${output}/${path}_${year}_71.root
hadd -f ${output}/${path}_${year}_ele_ss_2.root  ${output}/${path}_${year}_65.root ${output}/${path}_${year}_81.root
hadd -f ${output}/${path}_${year}_ele_ss_3.root  ${output}/${path}_${year}_67.root ${output}/${path}_${year}_91.root
hadd -f ${output}/${path}_${year}_ele_ss_4.root  ${output}/${path}_${year}_69.root ${output}/${path}_${year}_101.root
hadd -f ${output}/${path}_${year}_ele_ss_5.root  ${output}/${path}_${year}_73.root
hadd -f ${output}/${path}_${year}_ele_ss_6.root  ${output}/${path}_${year}_75.root ${output}/${path}_${year}_83.root
hadd -f ${output}/${path}_${year}_ele_ss_7.root  ${output}/${path}_${year}_77.root ${output}/${path}_${year}_93.root
hadd -f ${output}/${path}_${year}_ele_ss_8.root  ${output}/${path}_${year}_79.root ${output}/${path}_${year}_103.root
hadd -f ${output}/${path}_${year}_ele_ss_9.root  ${output}/${path}_${year}_85.root
hadd -f ${output}/${path}_${year}_ele_ss_10.root ${output}/${path}_${year}_87.root ${output}/${path}_${year}_95.root
hadd -f ${output}/${path}_${year}_ele_ss_11.root ${output}/${path}_${year}_89.root ${output}/${path}_${year}_105.root
hadd -f ${output}/${path}_${year}_ele_ss_12.root ${output}/${path}_${year}_97.root
hadd -f ${output}/${path}_${year}_ele_ss_13.root ${output}/${path}_${year}_99.root ${output}/${path}_${year}_107.root
hadd -f ${output}/${path}_${year}_ele_ss_14.root ${output}/${path}_${year}_109.root

elif [ $option -eq 1 ]; then

export bins=20
hadd -f ${output}/${path}_${year}_ele_os_0.root  ${output}/${path}_${year}_400.root
hadd -f ${output}/${path}_${year}_ele_os_1.root  ${output}/${path}_${year}_402.root
hadd -f ${output}/${path}_${year}_ele_os_2.root  ${output}/${path}_${year}_404.root
hadd -f ${output}/${path}_${year}_ele_os_3.root  ${output}/${path}_${year}_406.root
hadd -f ${output}/${path}_${year}_ele_os_4.root  ${output}/${path}_${year}_408.root
hadd -f ${output}/${path}_${year}_ele_os_5.root  ${output}/${path}_${year}_410.root
hadd -f ${output}/${path}_${year}_ele_os_6.root  ${output}/${path}_${year}_412.root
hadd -f ${output}/${path}_${year}_ele_os_7.root  ${output}/${path}_${year}_414.root
hadd -f ${output}/${path}_${year}_ele_os_8.root  ${output}/${path}_${year}_416.root
hadd -f ${output}/${path}_${year}_ele_os_9.root  ${output}/${path}_${year}_418.root
hadd -f ${output}/${path}_${year}_ele_os_10.root ${output}/${path}_${year}_420.root
hadd -f ${output}/${path}_${year}_ele_os_11.root ${output}/${path}_${year}_422.root
hadd -f ${output}/${path}_${year}_ele_os_12.root ${output}/${path}_${year}_424.root
hadd -f ${output}/${path}_${year}_ele_os_13.root ${output}/${path}_${year}_426.root
hadd -f ${output}/${path}_${year}_ele_os_14.root ${output}/${path}_${year}_428.root
hadd -f ${output}/${path}_${year}_ele_os_15.root ${output}/${path}_${year}_430.root
hadd -f ${output}/${path}_${year}_ele_os_16.root ${output}/${path}_${year}_432.root
hadd -f ${output}/${path}_${year}_ele_os_17.root ${output}/${path}_${year}_434.root
hadd -f ${output}/${path}_${year}_ele_os_18.root ${output}/${path}_${year}_436.root
hadd -f ${output}/${path}_${year}_ele_os_19.root ${output}/${path}_${year}_438.root

hadd -f ${output}/${path}_${year}_ele_ss_0.root  ${output}/${path}_${year}_401.root
hadd -f ${output}/${path}_${year}_ele_ss_1.root  ${output}/${path}_${year}_403.root
hadd -f ${output}/${path}_${year}_ele_ss_2.root  ${output}/${path}_${year}_405.root
hadd -f ${output}/${path}_${year}_ele_ss_3.root  ${output}/${path}_${year}_407.root
hadd -f ${output}/${path}_${year}_ele_ss_4.root  ${output}/${path}_${year}_409.root
hadd -f ${output}/${path}_${year}_ele_ss_5.root  ${output}/${path}_${year}_411.root
hadd -f ${output}/${path}_${year}_ele_ss_6.root  ${output}/${path}_${year}_413.root
hadd -f ${output}/${path}_${year}_ele_ss_7.root  ${output}/${path}_${year}_415.root
hadd -f ${output}/${path}_${year}_ele_ss_8.root  ${output}/${path}_${year}_417.root
hadd -f ${output}/${path}_${year}_ele_ss_9.root  ${output}/${path}_${year}_419.root
hadd -f ${output}/${path}_${year}_ele_ss_10.root ${output}/${path}_${year}_421.root
hadd -f ${output}/${path}_${year}_ele_ss_11.root ${output}/${path}_${year}_423.root
hadd -f ${output}/${path}_${year}_ele_ss_12.root ${output}/${path}_${year}_425.root
hadd -f ${output}/${path}_${year}_ele_ss_13.root ${output}/${path}_${year}_427.root
hadd -f ${output}/${path}_${year}_ele_ss_14.root ${output}/${path}_${year}_429.root
hadd -f ${output}/${path}_${year}_ele_ss_15.root ${output}/${path}_${year}_431.root
hadd -f ${output}/${path}_${year}_ele_ss_16.root ${output}/${path}_${year}_433.root
hadd -f ${output}/${path}_${year}_ele_ss_17.root ${output}/${path}_${year}_435.root
hadd -f ${output}/${path}_${year}_ele_ss_18.root ${output}/${path}_${year}_437.root
hadd -f ${output}/${path}_${year}_ele_ss_19.root ${output}/${path}_${year}_439.root

fi

python3 computeWSEff.py --path=${path} --year=${year} --output=${output} --bins=${bins}
