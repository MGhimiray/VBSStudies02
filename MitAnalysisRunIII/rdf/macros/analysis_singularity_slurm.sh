#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh;export APPTAINER_BIND="${thisDir},/ceph/submit";cmssw-el9 --command-to-run ./analysis_slurm_with_singularity.sh $1 $2 $3 $4 $5
