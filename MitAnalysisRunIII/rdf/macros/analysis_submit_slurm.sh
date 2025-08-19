#!/bin/sh

if [ $# -lt 1 ]; then
   echo "TOO FEW PARAMETERS"
   exit
fi

theAna=$1
whichAna="DUMMY"
group=9

condorJob=1001
if [ $# -gt 1 ]; then
  condorJob=$2
fi

if [ $theAna -eq 0 ]; then
 whichAna="zAnalysis"

elif [ $theAna -eq 1 ]; then
 whichAna="wzAnalysis"
 group=1

elif [ $theAna -eq 2 ]; then
 whichAna="zzAnalysis"
 group=1

elif [ $theAna -eq 3 ]; then
 whichAna="sswwAnalysis"
 group=3

elif [ $theAna -eq 4 ]; then
 whichAna="zmetAnalysis"

elif [ $theAna -eq 5 ]; then
 whichAna="fakeAnalysis"
 if [ $# -ge 3 ] && [ $3 = "1" ]; then
   nohup ./analysis_slurm.sh 110 20220 -1 1002 fakeAnalysis >& logs/log_110 &
   nohup ./analysis_slurm.sh 136 20220 -1 1003 fakeAnalysis >& logs/log_136 &
   nohup ./analysis_slurm.sh 210 20221 -1 1002 fakeAnalysis >& logs/log_210 &
   nohup ./analysis_slurm.sh 236 20221 -1 1003 fakeAnalysis >& logs/log_236 &
   nohup ./analysis_slurm.sh 310 20230 -1 1002 fakeAnalysis >& logs/log_310 &
   nohup ./analysis_slurm.sh 336 20230 -1 1003 fakeAnalysis >& logs/log_336 &
   nohup ./analysis_slurm.sh 410 20231 -1 1002 fakeAnalysis >& logs/log_410 &
   nohup ./analysis_slurm.sh 436 20231 -1 1003 fakeAnalysis >& logs/log_436 &
   nohup ./analysis_slurm.sh 510 20240 -1 1002 fakeAnalysis >& logs/log_510 &
   nohup ./analysis_slurm.sh 536 20240 -1 1003 fakeAnalysis >& logs/log_536 &
 fi
 group=4

elif [ $theAna -eq 6 ]; then
 whichAna="triggerAnalysis"

elif [ $theAna -eq 7 ]; then
 whichAna="metAnalysis"
 group=4

elif [ $theAna -eq 8 ]; then
 whichAna="wwAnalysis"
 group=4

elif [ $theAna -eq 9 ]; then
 whichAna="puAnalysis"

fi

if [ ${whichAna} = "DUMMY" ]; then
   echo "BAD PARAMETER";
   exit;
fi

while IFS= read -r line; do

set -- $line
whichSample=$1
whichYear=$2
passSel=$3

if [ "${passSel}" != "no" ]; then

for whichJob in $(seq 0 $group)
do

if [ $theAna -ne 1 ]; then

cat << EOF > submit
#!/bin/bash
#SBATCH --job-name=simple_${whichAna}_${condorJob}_${whichSample}_${whichYear}_${whichJob}
#SBATCH --output=logs/simple_${whichAna}_${condorJob}_${whichSample}_${whichYear}_${whichJob}_%j.out
#SBATCH --error=logs/simple_${whichAna}_${condorJob}_${whichSample}_${whichYear}_${whichJob}_%j.error
#SBATCH --cpus-per-task=4
srun ./analysis_singularity_slurm.sh ${whichSample} ${whichYear} ${whichJob} ${condorJob} ${whichAna}
EOF

else

cat << EOF > submit
#!/bin/bash
#SBATCH --job-name=simple_${whichAna}_${condorJob}_${whichSample}_${whichYear}_${whichJob}
#SBATCH --output=logs/simple_${whichAna}_${condorJob}_${whichSample}_${whichYear}_${whichJob}_%j.out
#SBATCH --error=logs/simple_${whichAna}_${condorJob}_${whichSample}_${whichYear}_${whichJob}_%j.error
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=3000M
srun ./analysis_singularity_slurm.sh ${whichSample} ${whichYear} ${whichJob} ${condorJob} ${whichAna}
EOF

fi

sbatch submit

sleep 0.1

done

fi

done < ${whichAna}_input_condor_jobs.cfg

rm -f submit
#srun ./analysis_slurm.sh ${whichSample} ${whichYear} ${whichJob} ${condorJob} ${whichAna}
##SBATCH --partition=submit-alma9
##SBATCH --exclude=submit[30,81]
#srun ./analysis_singularity_slurm.sh ${whichSample} ${whichYear} ${whichJob} ${condorJob} ${whichAna}
#SBATCH --exclude=submit[52-59]
#scontrol show jobid -dd 644285
