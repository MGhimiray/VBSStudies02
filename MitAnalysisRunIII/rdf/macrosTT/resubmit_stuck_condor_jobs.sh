#!/bin/sh

rm -f ceballos.txt;
wget --no-check-certificate https://submit.mit.edu/condormon/jobs/ceballos.txt;

grep Running ceballos.txt|awk '{print"nohup ./analysis_slurm.sh "$6" "$7" "$8" "$9" "$10" >& log_"NR"&"}' > lll;
chmod a+x lll;./lll;rm -f lll;

rm -f ceballos.txt;
