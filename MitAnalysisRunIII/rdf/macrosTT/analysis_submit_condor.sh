#!/bin/sh

#./checkJobs.sh fake 1001 20220 condor_q|grep FAI|awk '{split($1,a,"_");split(a[6],b,".");print"nohup ./analysis_slurm.sh "a[4]" "a[5]" "b[1]" "a[3]" "a[2]" >& logs/log_"a[2]"_"a[4]"_"b[1]" &"}'

if [ $# -lt 1 ]; then
   echo "TOO FEW PARAMETERS"
   exit
fi

theAna=$1
whichAna="DUMMY"
group=9

condorJob=1001
if [ $# -ge 2 ]; then
  condorJob=$2
fi

if [ $theAna -eq 0 ]; then
 whichAna="zAnalysis"

elif [ $theAna -eq 1 ]; then
 whichAna="wzAnalysis"

elif [ $theAna -eq 2 ]; then
 whichAna="zzAnalysis"

elif [ $theAna -eq 3 ]; then
 whichAna="sswwAnalysis"

elif [ $theAna -eq 4 ]; then
 whichAna="zmetAnalysis"

elif [ $theAna -eq 5 ]; then
 whichAna="fakeAnalysis"
 if [ $# -ge 3 ]; then
   nohup ./analysis_slurm.sh 110 20220 -1 1002 fakeAnalysis >& logs/log_110 &
   nohup ./analysis_slurm.sh 136 20220 -1 1003 fakeAnalysis >& logs/log_136 &
   nohup ./analysis_slurm.sh 210 20221 -1 1002 fakeAnalysis >& logs/log_210 &
   nohup ./analysis_slurm.sh 236 20221 -1 1003 fakeAnalysis >& logs/log_236 &
   nohup ./analysis_slurm.sh 310 20230 -1 1002 fakeAnalysis >& logs/log_310 &
   nohup ./analysis_slurm.sh 336 20230 -1 1003 fakeAnalysis >& logs/log_336 &
   nohup ./analysis_slurm.sh 410 20231 -1 1002 fakeAnalysis >& logs/log_410 &
   nohup ./analysis_slurm.sh 436 20231 -1 1003 fakeAnalysis >& logs/log_436 &
 fi

elif [ $theAna -eq 6 ]; then
 whichAna="triggerAnalysis"

elif [ $theAna -eq 7 ]; then
 whichAna="metAnalysis"

elif [ $theAna -eq 8 ]; then
 whichAna="wwAnalysis"

fi

if [ ${whichAna} = "DUMMY" ]; then
   echo "BAD PARAMETER";
   exit;
fi

USERPROXY=`id -u`
echo ${USERPROXY}

voms-proxy-init --voms cms --valid 168:00 -pwstdin < $HOME/.grid-cert-passphrase

tar cvzf ${whichAna}.tgz \
*Analysis.py analysis_slurm.sh functions.h utils*.py \
data/* weights_mva/* tmva_helper_xml.* \
mysf.h \
jsns/* config/* jsonpog-integration/*

while IFS= read -r line; do

set -- $line
whichSample=$1
whichYear=$2
passSel=$3

if [ "${passSel}" != "no" ]; then

for whichJob in $(seq 0 $group)
do

cat << EOF > submit
Universe   = vanilla
Executable = analysis_singularity_condor.sh
Arguments  = ${whichSample} ${whichYear} ${whichJob} ${condorJob} ${whichAna}
RequestMemory = 4000
RequestCpus = 1
RequestDisk = DiskUsage
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
Log    = logs/simple_${whichAna}_${condorJob}_${whichSample}_${whichYear}_${whichJob}.log
Output = logs/simple_${whichAna}_${condorJob}_${whichSample}_${whichYear}_${whichJob}.out
Error  = logs/simple_${whichAna}_${condorJob}_${whichSample}_${whichYear}_${whichJob}.error
transfer_input_files = analysis_condor.sh,${whichAna}.tgz
use_x509userproxy = True
x509userproxy = /tmp/x509up_u${USERPROXY}
Requirements = ( BOSCOCluster =!= "t3serv008.mit.edu" && BOSCOCluster =!= "ce03.cmsaf.mit.edu" && BOSCOCluster =!= "eofe8.mit.edu") && (Machine != "t3btch003.mit.edu")
+DESIRED_Sites = "mit_tier2,mit_tier3"
Queue
EOF

condor_submit submit

done

fi

done < ${whichAna}_input_condor_jobs.cfg

rm -f submit
