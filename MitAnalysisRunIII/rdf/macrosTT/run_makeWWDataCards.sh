#!/bin/sh

if [ $# -lt 2 ]; then
   echo "TOO FEW PARAMETERS"
   exit
fi

export theOption=$2

if [ $theOption -eq 0 ]; then

  export theAna=wwAnalysis$1

  root -l -q -b makeWWDataCards.C'(0,1,"anaZ","'${theAna}'",20220,0)'
  root -l -q -b makeWWDataCards.C'(0,2,"anaZ","'${theAna}'",20220,0)'
  root -l -q -b makeWWDataCards.C'(0,3,"anaZ","'${theAna}'",20220,0)'
  root -l -q -b makeWWDataCards.C'(0,4,"anaZ","'${theAna}'",20220,0)'
  root -l -q -b makeWWDataCards.C'(0,1,"anaZ","'${theAna}'",20221,0)'
  root -l -q -b makeWWDataCards.C'(0,2,"anaZ","'${theAna}'",20221,0)'
  root -l -q -b makeWWDataCards.C'(0,3,"anaZ","'${theAna}'",20221,0)'
  root -l -q -b makeWWDataCards.C'(0,4,"anaZ","'${theAna}'",20221,0)'

  root -l -q -b makeWWDataCards.C'(0,1,"anaZ","'${theAna}'",20220,1)'
  root -l -q -b makeWWDataCards.C'(0,2,"anaZ","'${theAna}'",20220,1)'
  root -l -q -b makeWWDataCards.C'(0,3,"anaZ","'${theAna}'",20220,1)'
  root -l -q -b makeWWDataCards.C'(0,4,"anaZ","'${theAna}'",20220,1)'
  root -l -q -b makeWWDataCards.C'(0,1,"anaZ","'${theAna}'",20221,1)'
  root -l -q -b makeWWDataCards.C'(0,2,"anaZ","'${theAna}'",20221,1)'
  root -l -q -b makeWWDataCards.C'(0,3,"anaZ","'${theAna}'",20221,1)'
  root -l -q -b makeWWDataCards.C'(0,4,"anaZ","'${theAna}'",20221,1)'

  root -l -q -b makeWWDataCards.C'(0,1,"anaZ","'${theAna}'",20230,0)'
  root -l -q -b makeWWDataCards.C'(0,2,"anaZ","'${theAna}'",20230,0)'
  root -l -q -b makeWWDataCards.C'(0,3,"anaZ","'${theAna}'",20230,0)'
  root -l -q -b makeWWDataCards.C'(0,4,"anaZ","'${theAna}'",20230,0)'
  root -l -q -b makeWWDataCards.C'(0,1,"anaZ","'${theAna}'",20231,0)'
  root -l -q -b makeWWDataCards.C'(0,2,"anaZ","'${theAna}'",20231,0)'
  root -l -q -b makeWWDataCards.C'(0,3,"anaZ","'${theAna}'",20231,0)'
  root -l -q -b makeWWDataCards.C'(0,4,"anaZ","'${theAna}'",20231,0)'

  root -l -q -b makeWWDataCards.C'(0,1,"anaZ","'${theAna}'",20230,1)'
  root -l -q -b makeWWDataCards.C'(0,2,"anaZ","'${theAna}'",20230,1)'
  root -l -q -b makeWWDataCards.C'(0,3,"anaZ","'${theAna}'",20230,1)'
  root -l -q -b makeWWDataCards.C'(0,4,"anaZ","'${theAna}'",20230,1)'
  root -l -q -b makeWWDataCards.C'(0,1,"anaZ","'${theAna}'",20231,1)'
  root -l -q -b makeWWDataCards.C'(0,2,"anaZ","'${theAna}'",20231,1)'
  root -l -q -b makeWWDataCards.C'(0,3,"anaZ","'${theAna}'",20231,1)'
  root -l -q -b makeWWDataCards.C'(0,4,"anaZ","'${theAna}'",20231,1)'

  #export theAna=wzAnalysis$1
  #root -l -q -b makeVVDataCards.C'(0,0,"anaZ","'${theAna}'",20220,0)'
  #root -l -q -b makeVVDataCards.C'(0,0,"anaZ","'${theAna}'",20221,0)'

  #export theAna=zzAnalysis$1
  #root -l -q -b makeVVDataCards.C'(0,0,"anaZ","'${theAna}'",20220,0)'
  #root -l -q -b makeVVDataCards.C'(0,0,"anaZ","'${theAna}'",20221,0)'

elif [ $theOption -eq 1 ]; then
  if [ $# -lt 3 ]; then
     echo "TOO FEW PARAMETERS"
     exit
  fi

  export theAna=wwAnalysis$1
  export whichAna=$3

  root -l -q -b makeWWDataCards.C'('${whichAna}',1,"anaZ","'${theAna}'",20220,0)'
  root -l -q -b makeWWDataCards.C'('${whichAna}',2,"anaZ","'${theAna}'",20220,0)'
  root -l -q -b makeWWDataCards.C'('${whichAna}',3,"anaZ","'${theAna}'",20220,0)'
  root -l -q -b makeWWDataCards.C'('${whichAna}',1,"anaZ","'${theAna}'",20221,0)'
  root -l -q -b makeWWDataCards.C'('${whichAna}',2,"anaZ","'${theAna}'",20221,0)'
  root -l -q -b makeWWDataCards.C'('${whichAna}',3,"anaZ","'${theAna}'",20221,0)'

elif [ $theOption -eq 2 ]; then

  export theAna=wzAnalysis$1
  root -l -q -b makeVVDataCards.C'(0,0,"anaZ","'${theAna}'",20220,1)'
  root -l -q -b makeVVDataCards.C'(0,1,"anaZ","'${theAna}'",20220,1)'
  root -l -q -b makeVVDataCards.C'(0,0,"anaZ","'${theAna}'",20221,1)'
  root -l -q -b makeVVDataCards.C'(0,1,"anaZ","'${theAna}'",20221,1)'

  export theAna=zzAnalysis$1
  root -l -q -b makeVVDataCards.C'(0,0,"anaZ","'${theAna}'",20220,1)'
  root -l -q -b makeVVDataCards.C'(0,0,"anaZ","'${theAna}'",20221,1)'

fi
