#!/bin/sh

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc12
scramv1 project CMSSW CMSSW_13_3_1 # cmsrel is an alias not on the workers
cd CMSSW_13_3_1/src/
eval `scramv1 runtime -sh` # cmsenv is an alias not on the workers
cd ../..

voms-proxy-info

tar xzf $5.tgz

echo $PWD

./analysis_slurm.sh $1 $2 $3 $4 $5

rm -rf functions* *.pyc $5.tgz \
*Analysis.py analysis_slurm.sh functions.h utils*.py \
data weights_mva tmva_helper_xml.* \
mysf.* \
jsns config jsonpog-integration 

ls -l
