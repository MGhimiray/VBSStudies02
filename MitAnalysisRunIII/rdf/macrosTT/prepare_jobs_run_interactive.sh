#!/bin/sh

if [ $# -lt 1 ]; then
   echo "TOO FEW PARAMETERS"
   exit
fi

theAna=$1

if [ $theAna -eq 0 ]; then
 cat zAnalysis_input_condor_jobs.cfg|grep -v no|awk '{print"nohup ./analysis_slurm.sh "$1" "$2 " -1 1001 zAnalysis >& logz_"NR"&"}' > lll_z

elif [ $theAna -eq 1 ]; then
 cat wzAnalysis_input_condor_jobs.cfg|grep -v no|awk '{print"nohup ./analysis_slurm.sh "$1" "$2 " -1 1001 wzAnalysis >& logwz_"NR"&"}' > lll_wz

elif [ $theAna -eq 2 ]; then
 cat zzAnalysis_input_condor_jobs.cfg|grep -v no|awk '{print"nohup ./analysis_slurm.sh "$1" "$2 " -1 1001 zzAnalysis >& logzz_"NR"&"}' > lll_zz

elif [ $theAna -eq 3 ]; then
 cat sswwAnalysis_input_condor_jobs.cfg|grep -v no|awk '{print"nohup ./analysis_slurm.sh "$1" "$2 " -1 1001 sswwAnalysis >& logssww_"NR"&"}' > lll_ssww

elif [ $theAna -eq 4 ]; then
 cat zmetAnalysis_input_condor_jobs.cfg|grep -v no|awk '{print"nohup ./analysis_slurm.sh "$1" "$2 " -1 1001 zmetAnalysis >& logzmet_"NR"&"}' > lll_zmet

elif [ $theAna -eq 5 ]; then
 cat fakeAnalysis_input_condor_jobs.cfg|grep -v no|awk '{print"nohup ./analysis_slurm.sh "$1" "$2 " -1 1001 fakeAnalysis >& logfake_"NR"&"}' > lll_fake

elif [ $theAna -eq 6 ]; then
 cat triggerAnalysis_input_condor_jobs.cfg|grep -v no|awk '{print"nohup ./analysis_slurm.sh "$1" "$2 " -1 1001 triggerAnalysis >& logtrigger_"NR"&"}' > lll_trigger

elif [ $theAna -eq 7 ]; then
 cat metAnalysis_input_condor_jobs.cfg|grep -v no|awk '{print"nohup ./analysis_slurm.sh "$1" "$2 " -1 1001 metAnalysis >& logmet_"NR"&"}' > lll_met

elif [ $theAna -eq 8 ]; then
 cat wwAnalysis_input_condor_jobs.cfg|grep -v no|awk '{print"nohup ./analysis_slurm.sh "$1" "$2 " -1 1001 wwAnalysis >& logww_"NR"&"}' > lll_ww

elif [ $theAna -eq 9 ]; then
 cat puAnalysis_input_condor_jobs.cfg|grep -v no|awk '{print"nohup ./analysis_slurm.sh "$1" "$2 " -1 1001 puAnalysis >& logpu_"NR"&"}' > lll_pu

elif [ $theAna -eq 11 ]; then
 cat wzAnalysis_inc_input_condor_jobs.cfg|grep -v no|awk '{print"nohup ./analysis_slurm.sh "$1" "$2 " -1 1001 wzAnalysis >& logwzinc_"NR"&"}' > lll_wzinc

fi
