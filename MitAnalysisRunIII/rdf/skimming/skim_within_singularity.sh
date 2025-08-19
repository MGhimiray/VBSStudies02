#!/bin/sh

unset X509_USER_KEY
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
scramv1 project CMSSW CMSSW_14_1_4 # cmsrel is an alias not on the workers
cd CMSSW_14_1_4/src/
eval `scramv1 runtime -sh` # cmsenv is an alias not on the workers
cd ../..

voms-proxy-info

echo "hostname"
hostname
whoami

tar xvzf skim.tgz

ls -l
echo $PWD

python3 skim.py --whichSample=$1 --whichJob=$2 --group=$3 --inputSamplesCfg=$4 --inputFilesCfg=$5
status=$?

rm -rf skim.tgz skim.py skim_*.cfg functions_skim.h haddnanoaod.py jsns config

if [ $status -eq 0 ]; then
  echo "SUCCESS"

else
  echo "FAILURE"

fi

ls -l
