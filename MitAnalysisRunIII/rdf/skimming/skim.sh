#!/bin/bash
hostname
thisDir=$PWD
echo ${thisDir}
ls -l
source /cvmfs/cms.cern.ch/cmsset_default.sh;export APPTAINER_BIND="${thisDir}";cmssw-el9 --command-to-run ${thisDir}/skim_within_singularity.sh $1 $2 $3 $4 $5
