source /cvmfs/cms.cern.ch/cmsset_default.sh;export APPTAINER_BIND="$PWD";cmssw-cc7 --command-to-run ls;./analysis_condor.sh $1 $2 $3 $4 $5
