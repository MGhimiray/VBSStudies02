#!/bin/sh

rm -rf /ceph/submit/data/group/cms/store/user/ceballos/test0
cp -r /home/submit/ceballos/cms/MitAnalysisRunIII/rdf/skimming /ceph/submit/data/group/cms/store/user/ceballos/test0
cd /ceph/submit/data/group/cms/store/user/ceballos/test0
rm config jsns
cp -r /home/submit/ceballos/cms/MitAnalysisRunIII/rdf/macros/jsns .
cp -r /home/submit/ceballos/cms/MitAnalysisRunIII/rdf/macros/config .
rm -rf logs

grep -Ev "tar|rm" skim_within_singularity.sh > skim_new.sh
diff skim_new.sh skim_within_singularity.sh
mv skim_new.sh skim_within_singularity.sh
chmod a+x skim_within_singularity.sh

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=el9_amd64_gcc12
scramv1 project CMSSW CMSSW_14_1_4 # cmsrel is an alias not on the workers
cd CMSSW_14_1_4/src/
eval `scramv1 runtime -sh` # cmsenv is an alias not on the workers
cd ../..

cat skim_input_condor_jobs_fromDAS.cfg|awk '{print"./skim_within_singularity.sh "$1" "$2" "$3" skim_input_samples_2023_fromDAS.cfg skim_input_files_fromDAS.cfg"}' > lll
chmod a+x lll

echo "DONE"
