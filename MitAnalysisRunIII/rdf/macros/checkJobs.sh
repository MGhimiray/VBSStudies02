#!/bin/sh

if [ $# -lt 4 ]; then
   echo "TOO FEW PARAMETERS"
   exit
fi

export theAna=$1
export condorJob=$2
export year=$3
export queue=$4

export group=10

if [ $theAna = 'z' ]; then
 export group=10

elif [ $theAna = 'trigger' ]; then
 export group=10

fi

if [ $4 == 'slurm' ]; then
ls logs/simple_${theAna}Analysis_${condorJob}_*_${year}_0_*.out|wc -l|awk '{printf("%d\n",$1*ENVIRON["group"])}'|awk -f ~/bin/sum2.awk;
grep "Total files" logs/simple_${theAna}Analysis_${condorJob}_*_${year}_0_*.out|awk '{a=$3;if(a>ENVIRON["group"])a=ENVIRON["group"];printf("%d\n",a)}'|awk -f ~/bin/sum2.awk;
grep "Total files" logs/simple_${theAna}Analysis_${condorJob}_*_${year}_1_*.out|awk '{a=$3;if(a>ENVIRON["group"])a=ENVIRON["group"];printf("%d\n",a)}'|awk -f ~/bin/sum2.awk;
grep "Total files" logs/simple_${theAna}Analysis_${condorJob}_*_${year}_2_*.out|awk '{a=$3;if(a>ENVIRON["group"])a=ENVIRON["group"];printf("%d\n",a)}'|awk -f ~/bin/sum2.awk;
else
ls logs/simple_${theAna}Analysis_${condorJob}_*_${year}_3.out|wc -l|awk '{printf("%d\n",$1*ENVIRON["group"])}'|awk -f ~/bin/sum2.awk;
grep "Total files" logs/simple_${theAna}Analysis_${condorJob}_*_${year}_3.out|awk '{a=$3;if(a>ENVIRON["group"])a=ENVIRON["group"];printf("%d\n",a)}'|awk -f ~/bin/sum2.awk;
grep "Total files" logs/simple_${theAna}Analysis_${condorJob}_*_${year}_5.out|awk '{a=$3;if(a>ENVIRON["group"])a=ENVIRON["group"];printf("%d\n",a)}'|awk -f ~/bin/sum2.awk;
grep "Total files" logs/simple_${theAna}Analysis_${condorJob}_*_${year}_7.out|awk '{a=$3;if(a>ENVIRON["group"])a=ENVIRON["group"];printf("%d\n",a)}'|awk -f ~/bin/sum2.awk;
fi

grep FAILED logs/simple_${theAna}Analysis_${condorJob}_*_${year}_*;
grep DONE   logs/simple_${theAna}Analysis_${condorJob}_*_${year}_*|wc;
grep DONE   logs/simple_${theAna}Analysis_${condorJob}_*_${year}_*|grep -v FILES|wc;
ls fillhisto_${theAna}Analysis${condorJob}*year${year}*|wc
