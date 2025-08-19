#!/bin/bash

echo "hostname"
hostname
whoami

cd ~/releases/CMSSW_14_1_4/src/;eval `scramv1 runtime -sh`;cd -;

echo "Parameters: " $1 $2 $3 $4 $5

time python3 $5.py --process=$1 --year=$2 --whichJob=$3
status=$?

if [ -f "fillhisto_$5_sample$1_year$2_job$3.root" ]; then
  mv fillhisto_$5_sample$1_year$2_job$3.root fillhisto_$5$4_sample$1_year$2_job$3.root
  echo "DONE"

elif [ $status -eq 0 ]; then
  echo "DONE NO FILES"

else
  echo "FAILED"

fi
