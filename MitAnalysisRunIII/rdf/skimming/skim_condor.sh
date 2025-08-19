#!/bin/sh

if [ $# -lt 1 ]; then
   echo "TOO FEW PARAMETERS"
   exit
fi

YEAR=$1

USERPROXY=`id -u`
echo ${USERPROXY}

#condor_q 1769874.0 -analyze
#transfer_input_files = ""
#transfer_output_remaps = "output_1l_${whichSample}_${whichJob}.root =  /ceph/submit/data/group/cms/store/user/ceballos/nanoaod/skims_submit/1l/${sampleName}/output_1l_${whichSample}_${whichJob}.root; output_2l_${whichSample}_${whichJob}.root =  /ceph/submit/data/group/cms/store/user/ceballos/nanoaod/skims_submit/2l/${sampleName}/output_2l_${whichSample}_${whichJob}.root; output_3l_${whichSample}_${whichJob}.root =  /ceph/submit/data/group/cms/store/user/ceballos/nanoaod/skims_submit/3l/${sampleName}/output_3l_${whichSample}_${whichJob}.root"

voms-proxy-init --voms cms --valid 168:00 -pwstdin < $HOME/.grid-cert-passphrase

cp /tmp/x509up_u${USERPROXY} /home/submit/ceballos/x509up_u${USERPROXY}

tar cvzf skim.tgz --exclude='*.csv' \
skim.py skim_*.cfg \
functions_skim.h haddnanoaod.py \
jsns/* config/*

mkdir -p logs;

while IFS= read -r line; do

set -- $line
whichSample=$1
whichJob=$2
group=$3
sampleName=$4

if [ ! -d " /ceph/submit/data/group/cms/store/user/ceballos/nanoaod/skims_submit/pho/${sampleName}" ]; then
  echo "creating output folders"  /ceph/submit/data/group/cms/store/user/ceballos/nanoaod/skims_submit/nl/${sampleName}
  mkdir -p  /ceph/submit/data/group/cms/store/user/ceballos/nanoaod/skims_submit/1l/${sampleName}
  mkdir -p  /ceph/submit/data/group/cms/store/user/ceballos/nanoaod/skims_submit/2l/${sampleName}
  mkdir -p  /ceph/submit/data/group/cms/store/user/ceballos/nanoaod/skims_submit/3l/${sampleName}
  mkdir -p  /ceph/submit/data/group/cms/store/user/ceballos/nanoaod/skims_submit/met/${sampleName}
  mkdir -p  /ceph/submit/data/group/cms/store/user/ceballos/nanoaod/skims_submit/pho/${sampleName}
fi

cat << EOF > submit
Universe   = vanilla
Executable = skim.sh
Arguments  = ${whichSample} ${whichJob} ${group} skim_input_samples_${YEAR}_fromDAS.cfg skim_input_files_fromDAS.cfg
RequestMemory = 6000
RequestCpus = 1
RequestDisk = DiskUsage
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_output_files = ""
Log    = logs/simple_skim_${whichSample}_${whichJob}.log
Output = logs/simple_skim_${whichSample}_${whichJob}.out
Error  = logs/simple_skim_${whichSample}_${whichJob}.error
transfer_input_files = skim.tgz, skim_within_singularity.sh
use_x509userproxy = True
x509userproxy = /home/submit/ceballos/x509up_u${USERPROXY}
+AccountingGroup = "analysis.ceballos"
Requirements = ( BOSCOCluster =!= "t3serv008.mit.edu" && BOSCOCluster =!= "ce03.cmsaf.mit.edu" && BOSCOCluster =!= "eofe8.mit.edu") && (Machine != "submitxx.mit.edu")
+DESIRED_Sites = "mit_tier3,T2_AT_Vienna,T2_BE_IIHE,T2_BE_UCL,T2_BR_SPRACE,T2_BR_UERJ,T2_CH_CERN,T2_CH_CERN_AI,T2_CH_CERN_HLT,T2_CH_CERN_Wigner,T2_CH_CSCS,T2_CH_CSCS_HPC,T2_CN_Beijing,T2_DE_DESY,T2_DE_RWTH,T2_EE_Estonia,T2_ES_CIEMAT,T2_ES_IFCA,T2_FI_HIP,T2_FR_CCIN2P3,T2_FR_GRIF_IRFU,T2_FR_GRIF_LLR,T2_FR_IPHC,T2_GR_Ioannina,T2_HU_Budapest,T2_IN_TIFR,T2_IT_Bari,T2_IT_Legnaro,T2_IT_Rome,T2_KR_KISTI,T2_MY_SIFIR,T2_MY_UPM_BIRUNI,T2_PK_NCP,T2_PL_Swierk,T2_PL_Warsaw,T2_PT_NCG_Lisbon,T2_RU_IHEP,T2_RU_INR,T2_RU_ITEP,T2_RU_JINR,T2_RU_PNPI,T2_RU_SINP,T2_TH_CUNSTDA,T2_TR_METU,T2_TW_NCHC,T2_UA_KIPT,T2_UK_London_IC,T2_UK_SGrid_Bristol,T2_UK_SGrid_RALPP,T2_US_Caltech,T2_US_Florida,T2_US_MIT,T2_US_Nebraska,T2_US_Purdue,T2_US_UCSD,T2_US_Wisconsin,T3_CH_CERN_CAF,T3_CH_CERN_DOMA,T3_CH_CERN_HelixNebula,T3_CH_CERN_HelixNebula_REHA,T3_CH_CMSAtHome,T3_CH_Volunteer,T3_US_HEPCloud,T3_US_NERSC,T3_US_OSG,T3_US_PSC,T3_US_SDSC"
Queue
EOF

condor_submit submit

done < skim_input_condor_jobs_fromDAS.cfg

rm -f submit
