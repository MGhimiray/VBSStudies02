#!/bin/bash

if [ $# -lt 3 ]; then
   echo "TOO FEW PARAMETERS"
   exit
fi

whichAna=$1
whichJob=$2
year=$3

if [ ${whichAna} == 'z' ]; then

    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_910.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_110.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_112.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_913.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_113.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_115.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_916.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_116.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_118.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_919.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_119.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_121.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_922.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_122.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_124.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_925.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_125.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_127.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_942.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_142.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_144.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_945.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_145.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_147.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_948.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_148.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_150.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_951.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_151.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_153.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_954.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_154.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_156.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_957.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_157.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_159.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_960.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_160.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_162.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_963.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_163.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_165.root

elif [ ${whichAna} == 'trigger' ]; then

    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_300.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_100.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_101.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_302.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_102.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_103.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_304.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_104.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_105.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_306.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_106.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_107.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_308.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_108.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_109.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_310.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_110.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_111.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_312.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_112.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_113.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_314.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_114.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_115.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_316.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_116.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_117.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_318.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_118.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_119.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_320.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_120.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_121.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_322.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_122.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_123.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_324.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_124.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_125.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_326.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_126.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_127.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_328.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_128.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_129.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_330.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_130.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_131.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_332.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_132.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_133.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_334.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_134.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_135.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_336.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_136.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_137.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_338.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_138.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_139.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_340.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_140.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_141.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_342.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_142.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_143.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_344.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_144.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_145.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_346.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_146.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_147.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_348.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_148.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_149.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_350.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_150.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_151.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_352.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_152.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_153.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_354.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_154.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_155.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_356.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_156.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_157.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_358.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_158.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_159.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_360.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_160.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_161.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_362.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_162.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_163.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_364.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_164.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_165.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_366.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_166.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_167.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_368.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_168.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_169.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_370.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_170.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_171.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_372.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_172.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_173.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_374.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_174.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_175.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_376.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_176.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_177.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_378.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_178.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_179.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_380.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_180.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_181.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_382.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_182.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_183.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_384.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_184.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_185.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_386.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_186.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_187.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_388.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_188.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_189.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_390.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_190.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_191.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_392.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_192.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_193.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_394.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_194.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_195.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_396.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_196.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_197.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_398.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_198.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_199.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_400.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_200.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_201.root
    hadd -f anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_402.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_202.root anaZ/fillhisto_${whichAna}Analysis${whichJob}_${year}_203.root
fi
