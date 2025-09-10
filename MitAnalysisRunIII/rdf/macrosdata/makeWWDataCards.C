#include <TROOT.h>
#include <TFile.h>
#include <TTree.h>
#include <TSystem.h>
#include <TString.h>
#include <TRandom.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TMath.h>
#include <iostream>
#include <fstream>
#include "TLorentzVector.h"
#include "TColor.h"

#include "../makePlots/common.h"

void makeWWDataCards(int whichAna = 0, int fidAna = 1, TString InputDir = "anaZ", TString anaSel = "wwAnalysis1001", int year = 20221, bool isFiducial = false){
  double WWNNLO_resumSyst[3][4]; // gen jet bin - reco jet bin
  double WWNNLO_scaleSyst[3][4]; // gen jet bin - reco jet bin
  WWNNLO_resumSyst[0][0] = 1.000; WWNNLO_resumSyst[1][0] = 1.002; WWNNLO_resumSyst[2][0] = 1.000;
  WWNNLO_resumSyst[0][1] = 1.001; WWNNLO_resumSyst[1][1] = 1.000; WWNNLO_resumSyst[2][1] = 0.996;
  WWNNLO_resumSyst[0][2] = 1.006; WWNNLO_resumSyst[1][2] = 1.002; WWNNLO_resumSyst[2][2] = 0.997;
  WWNNLO_resumSyst[0][3] = 1.011; WWNNLO_resumSyst[1][3] = 1.006; WWNNLO_resumSyst[2][3] = 0.998;
  WWNNLO_scaleSyst[0][0] = 1.000; WWNNLO_scaleSyst[1][0] = 0.998; WWNNLO_scaleSyst[2][0] = 0.994;
  WWNNLO_scaleSyst[0][1] = 1.006; WWNNLO_scaleSyst[1][1] = 0.998; WWNNLO_scaleSyst[2][1] = 0.989;
  WWNNLO_scaleSyst[0][2] = 1.014; WWNNLO_scaleSyst[1][2] = 1.004; WWNNLO_scaleSyst[2][2] = 0.995;
  WWNNLO_scaleSyst[0][3] = 1.020; WWNNLO_scaleSyst[1][3] = 1.010; WWNNLO_scaleSyst[2][3] = 0.997;

  double WWNNLO_GenJet[3] = {0.974, 0.848, 1.579};

  if(fidAna <= 0 || fidAna >= 5) printf("Wrong fidAna(%d)\n",fidAna);

  int theYear = 0;
  double triggerEffUnc = 1.000;
  if     (year == 20220) {triggerEffUnc = 1.005; theYear = 2022;}
  else if(year == 20221) {triggerEffUnc = 1.005; theYear = 2022;}
  else if(year == 20230) {triggerEffUnc = 1.005; theYear = 2023;}
  else if(year == 20231) {triggerEffUnc = 1.005; theYear = 2023;}
  else {printf("Wrong year!\n"); return;}

  int jumpValue = 200;

  TString addFiducialName = "";
  if(isFiducial == true) addFiducialName = "_isFiducial";

  double systValue;
  TFile *inputFile;
  TFile *outputFile;
  const int endTheory = 113;
  const int nSelTotal = 5;
  const int nSystTotal = 168;
  const int nSystDataCardTotal = 110; // (nSystTotal-endTheory)*2 = nSystDataCardTotal

  TH1D *histo_Auxiliar[nSelTotal][nPlotCategories];
  TH1D *histo_Baseline[nPlotCategories];
  TH1D *histo_QCDScaleUp[nPlotCategories];
  TH1D *histo_QCDScaleDown[nPlotCategories];
  TH1D *histo_PSUp[nPlotCategories];
  TH1D *histo_PSDown[nPlotCategories];
  TH1D *histo_WWNNLO_resumUp[nPlotCategories];
  TH1D *histo_WWNNLO_resumDown[nPlotCategories];
  TH1D *histo_WWNNLO_scaleUp[nPlotCategories];
  TH1D *histo_WWNNLO_scaleDown[nPlotCategories];
  TH1D *histo_WWNNLO_GenJetUp[nPlotCategories];
  TH1D *histo_WWNNLO_GenJetDown[nPlotCategories];
  TH1D *histo_WrongSignUncUp[nPlotCategories];
  TH1D *histo_WrongSignUncDown[nPlotCategories];

  TH1D *histo_Syst[nSystTotal][nPlotCategories];
  TH1D *histo_SystDataCard[nSystDataCardTotal][nPlotCategories];
  TH1D *histo_PDFUp  [101][nPlotCategories];
  TH1D *histo_PDFDown[101][nPlotCategories];

  TString BtagSFBCNames[13] = {"CMS_bc_btag_00", "CMS_bc_btag_01", "CMS_bc_btag_02", "CMS_bc_btag_bfragmentation", "CMS_bc_btag_colorreconnection", "CMS_bc_btag_hdamp", "CMS_bc_btag_jer", "CMS_bc_btag_jes", "CMS_bc_btag_pdf", "CMS_bc_btag_pileup", "CMS_bc_btag_topmass", "CMS_bc_btag_type3", "CMS_bc_btag_statistic"};

  TString jesNames[28] = {"", "AbsoluteMPFBias", "AbsoluteScale", "AbsoluteStat", "FlavorQCD", "Fragmentation", "PileUpDataMC", "PileUpPtBB", "PileUpPtEC1", "PileUpPtEC2", "PileUpPtHF", "PileUpPtRef", "RelativeFSR", "RelativeJEREC1", "RelativeJEREC2", "RelativeJERHF", "RelativePtBB", "RelativePtEC1", "RelativePtEC2", "RelativePtHF", "RelativeBal", "RelativeSample", "RelativeStatEC", "RelativeStatFSR", "RelativeStatHF", "SinglePionECAL", "SinglePionHCAL", "TimePtEta"};

  jesNames[ 3] = Form("%s_%d"  ,jesNames[ 3].Data(),theYear); // AbsoluteStat
  jesNames[13] = Form("%s_%d"  ,jesNames[13].Data(),theYear); // RelativeJEREC1
  jesNames[14] = Form("%s_%d"  ,jesNames[14].Data(),theYear); // RelativeJEREC2
  jesNames[17] = Form("%s_%d"  ,jesNames[17].Data(),theYear); // RelativePtEC1
  jesNames[18] = Form("%s_%d"  ,jesNames[18].Data(),theYear); // RelativePtEC2
  jesNames[21] = Form("%s_%d"  ,jesNames[21].Data(),theYear); // RelativeSample
  jesNames[22] = Form("%s_%d"  ,jesNames[22].Data(),theYear); // RelativeStatEC
  jesNames[23] = Form("%s_%d"  ,jesNames[23].Data(),theYear); // RelativeStatFSR
  jesNames[24] = Form("%s_%d"  ,jesNames[24].Data(),theYear); // RelativeStatHF
  jesNames[27] = Form("%s_%d"  ,jesNames[27].Data(),theYear); // TimePtEta

  TString nameSyst[nSystDataCardTotal];
  nameSyst[  0] = Form("CMS_eff_m_reco_%dUp",theYear);
  nameSyst[  1] = Form("CMS_eff_m_reco_%dDown",theYear);
  nameSyst[  2] = Form("CMS_eff_m_id_%dUp",theYear);
  nameSyst[  3] = Form("CMS_eff_m_id_%dDown",theYear);
  nameSyst[  4] = Form("CMS_eff_m_iso_%dUp",theYear);
  nameSyst[  5] = Form("CMS_eff_m_iso_%dDown",theYear);
  nameSyst[  6] = Form("CMS_eff_e_reco_%dUp",theYear);
  nameSyst[  7] = Form("CMS_eff_e_reco_%dDown",theYear);
  nameSyst[  8] = Form("CMS_eff_e_id_%dUp",theYear);
  nameSyst[  9] = Form("CMS_eff_e_id_%dDown",theYear);
  nameSyst[10 ] = "pileupUp";
  nameSyst[11 ] = "pileupDown";
  nameSyst[12 ] = "CMS_SMP24001_VVtriggerUp";
  nameSyst[13 ] = "CMS_SMP24001_VVtriggerDown";
  nameSyst[14 ] = Form("%sUp"  ,BtagSFBCNames[ 0].Data());
  nameSyst[15 ] = Form("%sDown",BtagSFBCNames[ 0].Data());
  nameSyst[16 ] = Form("%sUp"  ,BtagSFBCNames[ 1].Data());
  nameSyst[17 ] = Form("%sDown",BtagSFBCNames[ 1].Data());
  nameSyst[18 ] = Form("%sUp"  ,BtagSFBCNames[ 2].Data());
  nameSyst[19 ] = Form("%sDown",BtagSFBCNames[ 2].Data());
  nameSyst[20 ] = Form("%sUp"  ,BtagSFBCNames[ 3].Data());
  nameSyst[21 ] = Form("%sDown",BtagSFBCNames[ 3].Data());
  nameSyst[22 ] = Form("%sUp"  ,BtagSFBCNames[ 4].Data());
  nameSyst[23 ] = Form("%sDown",BtagSFBCNames[ 4].Data());
  nameSyst[24 ] = Form("%sUp"  ,BtagSFBCNames[ 5].Data());
  nameSyst[25 ] = Form("%sDown",BtagSFBCNames[ 5].Data());
  nameSyst[26 ] = Form("%sUp"  ,BtagSFBCNames[ 6].Data());
  nameSyst[27 ] = Form("%sDown",BtagSFBCNames[ 6].Data());
  nameSyst[28 ] = Form("%sUp"  ,BtagSFBCNames[ 7].Data());
  nameSyst[29 ] = Form("%sDown",BtagSFBCNames[ 7].Data());
  nameSyst[30 ] = Form("%sUp"  ,BtagSFBCNames[ 8].Data());
  nameSyst[31 ] = Form("%sDown",BtagSFBCNames[ 8].Data());
  nameSyst[32 ] = Form("%sUp"  ,BtagSFBCNames[ 9].Data());
  nameSyst[33 ] = Form("%sDown",BtagSFBCNames[ 9].Data());
  nameSyst[34 ] = Form("%sUp"  ,BtagSFBCNames[10].Data());
  nameSyst[35 ] = Form("%sDown",BtagSFBCNames[10].Data());
  nameSyst[36 ] = Form("%sUp"  ,BtagSFBCNames[11].Data());
  nameSyst[37 ] = Form("%sDown",BtagSFBCNames[11].Data());
  nameSyst[38 ] = Form("%s_%dUp"  ,BtagSFBCNames[12].Data(),year);
  nameSyst[39 ] = Form("%s_%dDown",BtagSFBCNames[12].Data(),year);
  nameSyst[40 ] = "CMS_lf_btagUp";
  nameSyst[41 ] = "CMS_lf_btagDown";
  nameSyst[42 ] = Form("CMS_scale_m_%dUp",theYear);
  nameSyst[43 ] = Form("CMS_scale_m_%dDown",theYear);
  nameSyst[44 ] = Form("CMS_scale_e_%dUp",theYear);
  nameSyst[45 ] = Form("CMS_scale_e_%dDown",theYear);
  nameSyst[46 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 0].Data());
  nameSyst[47 ] = Form("CMS_scale_j_%sDown",jesNames[ 0].Data());
  nameSyst[48 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 1].Data());
  nameSyst[49 ] = Form("CMS_scale_j_%sDown",jesNames[ 1].Data());
  nameSyst[50 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 2].Data());
  nameSyst[51 ] = Form("CMS_scale_j_%sDown",jesNames[ 2].Data());
  nameSyst[52 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 3].Data());
  nameSyst[53 ] = Form("CMS_scale_j_%sDown",jesNames[ 3].Data());
  nameSyst[54 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 4].Data());
  nameSyst[55 ] = Form("CMS_scale_j_%sDown",jesNames[ 4].Data());
  nameSyst[56 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 5].Data());
  nameSyst[57 ] = Form("CMS_scale_j_%sDown",jesNames[ 5].Data());
  nameSyst[58 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 6].Data());
  nameSyst[59 ] = Form("CMS_scale_j_%sDown",jesNames[ 6].Data());
  nameSyst[60 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 7].Data());
  nameSyst[61 ] = Form("CMS_scale_j_%sDown",jesNames[ 7].Data());
  nameSyst[62 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 8].Data());
  nameSyst[63 ] = Form("CMS_scale_j_%sDown",jesNames[ 8].Data());
  nameSyst[64 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 9].Data());
  nameSyst[65 ] = Form("CMS_scale_j_%sDown",jesNames[ 9].Data());
  nameSyst[66 ] = Form("CMS_scale_j_%sUp"  ,jesNames[10].Data());
  nameSyst[67 ] = Form("CMS_scale_j_%sDown",jesNames[10].Data());
  nameSyst[68 ] = Form("CMS_scale_j_%sUp"  ,jesNames[11].Data());
  nameSyst[69 ] = Form("CMS_scale_j_%sDown",jesNames[11].Data());
  nameSyst[70 ] = Form("CMS_scale_j_%sUp"  ,jesNames[12].Data());
  nameSyst[71 ] = Form("CMS_scale_j_%sDown",jesNames[12].Data());
  nameSyst[72 ] = Form("CMS_scale_j_%sUp"  ,jesNames[13].Data());
  nameSyst[73 ] = Form("CMS_scale_j_%sDown",jesNames[13].Data());
  nameSyst[74 ] = Form("CMS_scale_j_%sUp"  ,jesNames[14].Data());
  nameSyst[75 ] = Form("CMS_scale_j_%sDown",jesNames[14].Data());
  nameSyst[76 ] = Form("CMS_scale_j_%sUp"  ,jesNames[15].Data());
  nameSyst[77 ] = Form("CMS_scale_j_%sDown",jesNames[15].Data());
  nameSyst[78 ] = Form("CMS_scale_j_%sUp"  ,jesNames[16].Data());
  nameSyst[79 ] = Form("CMS_scale_j_%sDown",jesNames[16].Data());
  nameSyst[80 ] = Form("CMS_scale_j_%sUp"  ,jesNames[17].Data());
  nameSyst[81 ] = Form("CMS_scale_j_%sDown",jesNames[17].Data());
  nameSyst[82 ] = Form("CMS_scale_j_%sUp"  ,jesNames[18].Data());
  nameSyst[83 ] = Form("CMS_scale_j_%sDown",jesNames[18].Data());
  nameSyst[84 ] = Form("CMS_scale_j_%sUp"  ,jesNames[19].Data());
  nameSyst[85 ] = Form("CMS_scale_j_%sDown",jesNames[19].Data());
  nameSyst[86 ] = Form("CMS_scale_j_%sUp"  ,jesNames[20].Data());
  nameSyst[87 ] = Form("CMS_scale_j_%sDown",jesNames[20].Data());
  nameSyst[88 ] = Form("CMS_scale_j_%sUp"  ,jesNames[21].Data());
  nameSyst[89 ] = Form("CMS_scale_j_%sDown",jesNames[21].Data());
  nameSyst[90 ] = Form("CMS_scale_j_%sUp"  ,jesNames[22].Data());
  nameSyst[91 ] = Form("CMS_scale_j_%sDown",jesNames[22].Data());
  nameSyst[92 ] = Form("CMS_scale_j_%sUp"  ,jesNames[23].Data());
  nameSyst[93 ] = Form("CMS_scale_j_%sDown",jesNames[23].Data());
  nameSyst[94 ] = Form("CMS_scale_j_%sUp"  ,jesNames[24].Data());
  nameSyst[95 ] = Form("CMS_scale_j_%sDown",jesNames[24].Data());
  nameSyst[96 ] = Form("CMS_scale_j_%sUp"  ,jesNames[25].Data());
  nameSyst[97 ] = Form("CMS_scale_j_%sDown",jesNames[25].Data());
  nameSyst[98 ] = Form("CMS_scale_j_%sUp"  ,jesNames[26].Data());
  nameSyst[99 ] = Form("CMS_scale_j_%sDown",jesNames[26].Data());
  nameSyst[100] = Form("CMS_scale_j_%sUp"  ,jesNames[27].Data());
  nameSyst[101] = Form("CMS_scale_j_%sDown",jesNames[27].Data());
  nameSyst[102] = Form("CMS_res_j_%dUp",theYear);
  nameSyst[103] = Form("CMS_res_j_%dDown",theYear);
  nameSyst[104] = Form("CMS_met_jer_%dUp",theYear);
  nameSyst[105] = Form("CMS_met_jer_%dDown",theYear);
  nameSyst[106] = Form("CMS_met_jes_%dUp",theYear);
  nameSyst[107] = Form("CMS_met_jes_%dDown",theYear);
  nameSyst[108] = Form("CMS_met_unclustered_%dUp",theYear);
  nameSyst[109] = Form("CMS_met_unclustered_%dDown",theYear);

  double scaleFactorFiducial[nSelTotal][nPlotCategories];
 for(unsigned nSel=0; nSel<nSelTotal; nSel++) for(int ic=0; ic<nPlotCategories; ic++) scaleFactorFiducial[nSel][ic] = 0.0;

  int BinXF = nSelTotal; double minXF = -0.5; double maxXF = nSelTotal-0.5;
  if     (whichAna == 0){
  }
  else if(whichAna == 1){
    BinXF = 20; minXF = 85; maxXF = 385;
  }
  else if(whichAna == 2){
    BinXF = 20; minXF = 0; maxXF = 200;
  }
  else if(whichAna == 3){
    BinXF = 20; minXF = 25; maxXF = 225;
  }
  else if(whichAna == 4){
    BinXF = 20; minXF = 20; maxXF = 160;
  }
  else if(whichAna == 5){
    BinXF = 20; minXF = 0; maxXF = 3.1416;
  }
  else if(whichAna == 6){
    BinXF = 20; minXF = 0; maxXF = 200;
  }
  else if(whichAna == 7){
    BinXF = 10; minXF = 25; maxXF = 55;
  }
  else {
    printf("WRONG OPTION");
    return;
  }

  for(int ic=0; ic<nPlotCategories; ic++) {
    histo_Baseline[ic] = new TH1D(Form("histo_%s",plotBaseNames[ic].Data()),Form("histo_%s",plotBaseNames[ic].Data()), BinXF, minXF, maxXF);
    TString plotBaseNamesTemp =  plotBaseNames[ic];
    //if     (ic == kPlotSignal0 || ic == kPlotSignal1 || ic == kPlotSignal2 || ic == kPlotqqWW) plotBaseNamesTemp = "qqWW";
    //else if(ic == kPlotSignal3 || ic == kPlotSignal4 || ic == kPlotSignal5 || ic == kPlotggWW) plotBaseNamesTemp = "ggWW";
    histo_QCDScaleUp  [ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_QCD_scale_%s_ACCEPTUp"  , plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
    histo_QCDScaleDown[ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_QCD_scale_%s_ACCEPTDown", plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
    histo_PSUp  [ic]       = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_PS_%s_ACCEPTUp"  , plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
    histo_PSDown[ic]       = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_PS_%s_ACCEPTDown", plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
    histo_WWNNLO_resumUp   [ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_WWNNLO_resumUp"   , plotBaseNames[ic].Data()));
    histo_WWNNLO_resumDown [ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_WWNNLO_resumDown" , plotBaseNames[ic].Data()));
    histo_WWNNLO_scaleUp   [ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_WWNNLO_scaleUp"   , plotBaseNames[ic].Data()));
    histo_WWNNLO_scaleDown [ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_WWNNLO_scaleDown" , plotBaseNames[ic].Data()));
    histo_WWNNLO_GenJetUp  [ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_WWNNLO_%s_GenJetUp"  , plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
    histo_WWNNLO_GenJetDown[ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_WWNNLO_%s_GenJetDown", plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
    histo_WrongSignUncUp   [ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_CMS_SMP24001_wrongsign_eUp"   , plotBaseNames[ic].Data()));
    histo_WrongSignUncDown [ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_CMS_SMP24001_wrongsign_eDown" , plotBaseNames[ic].Data()));
  }

  for(int j=0; j<nSystTotal; j++){
    for(int ic=0; ic<nPlotCategories; ic++) histo_Syst[j][ic] = new TH1D(Form("histo_%s_%d",plotBaseNames[ic].Data(),j),Form("histo_%s_%d",plotBaseNames[ic].Data(),j), BinXF, minXF, maxXF);
  }
  for(int j=0; j<nSystDataCardTotal; j++){
    for(int ic=0; ic<nPlotCategories; ic++) histo_SystDataCard[j][ic] = new TH1D(Form("histo_%s_%s",plotBaseNames[ic].Data(),nameSyst[j].Data()),Form("histo_%s_%s",plotBaseNames[ic].Data(),nameSyst[j].Data()), BinXF, minXF, maxXF);
  }
  for(int j=0; j<101; j++){
    for(int ic=0; ic<nPlotCategories; ic++) histo_PDFUp  [j][ic] = new TH1D(Form("histo_%s_pdf%dUp"  ,plotBaseNames[ic].Data(),j),Form("histo_%s_pdf%dUp"  ,plotBaseNames[ic].Data(),j), BinXF, minXF, maxXF);
    for(int ic=0; ic<nPlotCategories; ic++) histo_PDFDown[j][ic] = new TH1D(Form("histo_%s_pdf%dDown",plotBaseNames[ic].Data(),j),Form("histo_%s_pdf%dDown",plotBaseNames[ic].Data(),j), BinXF, minXF, maxXF);
  }

  if(whichAna == 0){
    // same-sign / WW / DY / Top1 / Top2
    for(unsigned nSel=0; nSel<nSelTotal; nSel++) {
      inputFile = new TFile(Form("%s/fillhisto_%s_%d_%d_mva.root",InputDir.Data(),anaSel.Data(),year,nSel*jumpValue), "read");
      for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
        histo_Auxiliar[nSel][ic] = (TH1D*)inputFile->Get(Form("histoMVA%d", ic)); assert(histo_Auxiliar[nSel][ic]);
        if((ic == kPlotSignal0 || ic == kPlotSignal1 ||
            ic == kPlotSignal2 || ic == kPlotSignal3 ||
            ic == kPlotSignal4 || ic == kPlotSignal5 ||
            ic == kPlotqqWW    || ic == kPlotggWW) && histo_Auxiliar[nSel][ic]->GetSumOfWeights() > 0) scaleFactorFiducial[nSel][ic] = histo_Auxiliar[nSel][ic]->GetSumOfWeights();
        histo_Baseline[ic]->SetBinContent(nSel+1,histo_Auxiliar[nSel][ic]->GetBinContent(fidAna));
        histo_Baseline[ic]->SetBinError  (nSel+1,histo_Auxiliar[nSel][ic]->GetBinError  (fidAna));
      }
      delete inputFile;
    }

    for(int j=0; j<nSystTotal; j++){
      for(unsigned nSel=0; nSel<nSelTotal; nSel++) {
        inputFile = new TFile(Form("%s/fillhisto_%s_%d_%d_mva.root",InputDir.Data(),anaSel.Data(),year,nSel*jumpValue+1+j), "read");
        for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
          histo_Auxiliar[nSel][ic] = (TH1D*)inputFile->Get(Form("histoMVA%d", ic)); assert(histo_Auxiliar[nSel][ic]);

          if(isFiducial == true && 
           (ic == kPlotqqWW ||
            ic == kPlotggWW ||
            ic == kPlotSignal0 ||
            ic == kPlotSignal1 ||
            ic == kPlotSignal2 ||
            ic == kPlotSignal3 ||
            ic == kPlotSignal4 ||
            ic == kPlotSignal5
            ) && histo_Auxiliar[nSel][ic]->GetSumOfWeights() > 0 &&
            (j == 0 || j == 1 || j == 2 || j == 3 ||
             j == 4 || j == 5 || j == 6 || j == 7 || j == 8 || j == 9)
            ) histo_Auxiliar[nSel][ic]->Scale(scaleFactorFiducial[nSel][ic]/histo_Auxiliar[nSel][ic]->GetSumOfWeights());

          histo_Syst[j][ic]->SetBinContent(nSel+1,histo_Auxiliar[nSel][ic]->GetBinContent(fidAna));
          histo_Syst[j][ic]->SetBinError  (nSel+1,histo_Auxiliar[nSel][ic]->GetBinError  (fidAna));
        }
        delete inputFile;
      }
    }

  } // Default analysis
  else if(whichAna != 0){
    inputFile = new TFile(Form("%s/fillhisto_%s_%d_%d_mva.root",InputDir.Data(),anaSel.Data(),year,800+fidAna*jumpValue), "read");
    for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
      histo_Baseline[ic] = (TH1D*)inputFile->Get(Form("histoMVA%d", ic)); assert(histo_Baseline[ic]); histo_Baseline[ic]->SetDirectory(0);
      histo_Baseline[ic]->SetNameTitle(Form("histo_%s",plotBaseNames[ic].Data()),Form("histo_%s",plotBaseNames[ic].Data()));
    }
    delete inputFile;

    for(int j=0; j<nSystTotal; j++){
      inputFile = new TFile(Form("%s/fillhisto_%s_%d_%d_mva.root",InputDir.Data(),anaSel.Data(),year,800+fidAna*jumpValue+1+j), "read");
      for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
        histo_Syst[j][ic] = (TH1D*)inputFile->Get(Form("histoMVA%d", ic)); assert(histo_Syst[j][ic]); histo_Syst[j][ic]->SetDirectory(0);
        histo_Syst[j][ic]->SetNameTitle(Form("histo_%s_%s",plotBaseNames[ic].Data(),nameSyst[j].Data()),Form("histo_%s_%s",plotBaseNames[ic].Data(),nameSyst[j].Data()));
      }
      delete inputFile;
    }

  } // Alternative distributions

  for(unsigned ic=0; ic<nPlotCategories; ic++) {
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;

    histo_WWNNLO_resumUp   [ic]->Add(histo_Baseline[ic]);
    histo_WWNNLO_resumDown [ic]->Add(histo_Baseline[ic]);
    histo_WWNNLO_scaleUp   [ic]->Add(histo_Baseline[ic]);
    histo_WWNNLO_scaleDown [ic]->Add(histo_Baseline[ic]);
    histo_WWNNLO_GenJetUp  [ic]->Add(histo_Baseline[ic]);
    histo_WWNNLO_GenJetDown[ic]->Add(histo_Baseline[ic]);
    int genJetBin = -1;
    if     (ic == kPlotSignal0 || kPlotSignal3) genJetBin = 0;
    else if(ic == kPlotSignal1 || kPlotSignal4) genJetBin = 1;
    else if(ic == kPlotSignal2 || kPlotSignal5) genJetBin = 2;
    if(genJetBin >= 0 && isFiducial == false && whichAna == 0){
      histo_WWNNLO_resumUp   [ic]->Scale(WWNNLO_resumSyst[genJetBin][fidAna-1]);
      histo_WWNNLO_resumDown [ic]->Scale(1./WWNNLO_resumSyst[genJetBin][fidAna-1]);
      histo_WWNNLO_scaleUp   [ic]->Scale(WWNNLO_scaleSyst[genJetBin][fidAna-1]);
      histo_WWNNLO_scaleDown [ic]->Scale(1./WWNNLO_scaleSyst[genJetBin][fidAna-1]);
      histo_WWNNLO_GenJetUp  [ic]->Scale(WWNNLO_GenJet[genJetBin]);
      histo_WWNNLO_GenJetDown[ic]->Scale(1./WWNNLO_GenJet[genJetBin]);
    }

    for(int nb=1; nb<=histo_Baseline[ic]->GetNbinsX(); nb++){
      histo_Baseline[ic]->SetBinContent(nb, TMath::Max((float)histo_Baseline[ic]->GetBinContent(nb),0.0f));

      // compute QCD scale uncertainties bin-by-bin
      double diffQCDScale[6] = {
       TMath::Abs(histo_Syst[4][ic]->GetBinContent(nb)-histo_Baseline[ic]->GetBinContent(nb)),
       TMath::Abs(histo_Syst[5][ic]->GetBinContent(nb)-histo_Baseline[ic]->GetBinContent(nb)),
       TMath::Abs(histo_Syst[6][ic]->GetBinContent(nb)-histo_Baseline[ic]->GetBinContent(nb)),
       TMath::Abs(histo_Syst[7][ic]->GetBinContent(nb)-histo_Baseline[ic]->GetBinContent(nb)),
       TMath::Abs(histo_Syst[8][ic]->GetBinContent(nb)-histo_Baseline[ic]->GetBinContent(nb)),
       TMath::Abs(histo_Syst[9][ic]->GetBinContent(nb)-histo_Baseline[ic]->GetBinContent(nb))};

      double systQCDScale = diffQCDScale[0];
      for(int nqcd=1; nqcd<6; nqcd++) {
        if(diffQCDScale[nqcd] > systQCDScale) systQCDScale = diffQCDScale[nqcd];
      }

      if(histo_Baseline[ic]->GetBinContent(nb) > 0) 
        systQCDScale = 1.0+systQCDScale/histo_Baseline[ic]->GetBinContent(nb);
      else systQCDScale = 1;

      histo_QCDScaleUp  [ic]->SetBinContent(nb, histo_Baseline[ic]->GetBinContent(nb)*systQCDScale);
      histo_QCDScaleDown[ic]->SetBinContent(nb, histo_Baseline[ic]->GetBinContent(nb)/systQCDScale);

      // compute PS uncertainties bin-by-bin
      double diffPS[4] = {
       TMath::Abs(histo_Syst[0][ic]->GetBinContent(nb)-histo_Baseline[ic]->GetBinContent(nb)),
       TMath::Abs(histo_Syst[1][ic]->GetBinContent(nb)-histo_Baseline[ic]->GetBinContent(nb)),
       TMath::Abs(histo_Syst[2][ic]->GetBinContent(nb)-histo_Baseline[ic]->GetBinContent(nb)),
       TMath::Abs(histo_Syst[3][ic]->GetBinContent(nb)-histo_Baseline[ic]->GetBinContent(nb))};

      double systPS = diffPS[0];
      for(int nps=1; nps<4; nps++) {
        if(diffPS[nps] > systPS) systPS = diffPS[nps];
      }

      if(histo_Baseline[ic]->GetBinContent(nb) > 0) 
        systPS = 1.0+systPS/histo_Baseline[ic]->GetBinContent(nb);
      else systPS = 1;

      histo_PSUp  [ic]->SetBinContent(nb, histo_Baseline[ic]->GetBinContent(nb)*systPS);
      histo_PSDown[ic]->SetBinContent(nb, histo_Baseline[ic]->GetBinContent(nb)/systPS);

      histo_Baseline    [ic]->SetBinContent(nb, TMath::Max((float)histo_Baseline    [ic]->GetBinContent(nb),0.0f));
      histo_QCDScaleUp  [ic]->SetBinContent(nb, TMath::Max((float)histo_QCDScaleUp  [ic]->GetBinContent(nb),0.0f));
      histo_QCDScaleDown[ic]->SetBinContent(nb, TMath::Max((float)histo_QCDScaleDown[ic]->GetBinContent(nb),0.0f));
      histo_PSUp        [ic]->SetBinContent(nb, TMath::Max((float)histo_PSUp        [ic]->GetBinContent(nb),0.0f));
      histo_PSDown      [ic]->SetBinContent(nb, TMath::Max((float)histo_PSDown      [ic]->GetBinContent(nb),0.0f));
      for(int j=0; j<nSystTotal; j++) histo_Syst[j][ic]->SetBinContent(nb, TMath::Max((float)histo_Syst[j][ic]->GetBinContent(nb),0.0f));

      // compute PDF uncertainties
      if(histo_Baseline[ic]->GetBinContent(nb) > 0 && TMath::Abs(histo_Baseline[ic]->GetBinContent(nb)-histo_Syst[10][ic]->GetBinContent(nb))/histo_Baseline[ic]->GetBinContent(nb) > 0.001) printf("PDF problem %f %f %f\n", histo_Baseline[ic]->GetBinContent(nb),histo_Syst[10][ic]->GetBinContent(nb),TMath::Abs(histo_Baseline[ic]->GetBinContent(nb)-histo_Syst[10][ic]->GetBinContent(nb)));
      for(int npdf=0; npdf<100; npdf++){
        double diff = 0;
        if(histo_Baseline[ic]->GetBinContent(nb) > 0) diff = TMath::Abs(histo_Syst[npdf+11][ic]->GetBinContent(nb)-histo_Baseline[ic]->GetBinContent(nb))/histo_Baseline[ic]->GetBinContent(nb);
        if(diff > 0.05) printf("Large PDFUnc(%d) %s %d %f\n",npdf,plotBaseNames[ic].Data(),nb,diff);
        diff = min(diff,0.15);
        histo_PDFUp  [npdf][ic]->SetBinContent(nb, histo_Baseline[ic]->GetBinContent(nb)*(1.0+diff));
        histo_PDFDown[npdf][ic]->SetBinContent(nb, histo_Baseline[ic]->GetBinContent(nb)/(1.0+diff));
      }
      histo_PDFUp  [100][ic]->SetBinContent(nb, histo_Syst[111][ic]->GetBinContent(nb));
      histo_PDFDown[100][ic]->SetBinContent(nb, histo_Syst[112][ic]->GetBinContent(nb));

      // making symmetric uncertainties
      if(histo_Baseline[ic]->GetBinContent(nb) > 0) {
        for(int nuis=0; nuis<nSystTotal-endTheory; nuis++) {
          histo_SystDataCard[2*nuis][ic]->SetBinContent(nb,histo_Syst[endTheory+nuis][ic]->GetBinContent(nb));
          systValue = histo_SystDataCard[2*nuis][ic]->GetBinContent(nb) / histo_Baseline[ic]->GetBinContent(nb);
          if(systValue > 0) histo_SystDataCard[2*nuis+1][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb)/systValue);
          else {
                            histo_SystDataCard[2*nuis  ][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb));
                            histo_SystDataCard[2*nuis+1][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb));
               }
        }
        for(int nuis=0; nuis<nSystTotal-endTheory; nuis++) {
          systValue = histo_SystDataCard[2*nuis][ic]->GetBinContent(nb) / histo_Baseline[ic]->GetBinContent(nb);
          if     (systValue > 0 && systValue > 1.15) systValue = 1.15;
          else if(systValue > 0 && systValue < 0.85) systValue = 0.85;
          histo_SystDataCard[2*nuis][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb)*systValue);
          systValue = histo_SystDataCard[2*nuis][ic]->GetBinContent(nb) / histo_Baseline[ic]->GetBinContent(nb);
          if(systValue > 0) histo_SystDataCard[2*nuis+1][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb)/systValue);
          else {
                            histo_SystDataCard[2*nuis  ][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb));
                            histo_SystDataCard[2*nuis+1][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb));
               }
        }
      }
      else {
        for(int nuis=0; nuis<nSystDataCardTotal; nuis++) {
          histo_SystDataCard[nuis][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb));
        }
      }
    } // loop over bins

    histo_WrongSignUncUp  [ic]->Add(histo_Baseline[ic]);
    histo_WrongSignUncDown[ic]->Add(histo_Baseline[ic]);
    if(whichAna == 0 && histo_Baseline[ic]->GetBinContent(1) > 0.0) {
      if(ic == kPlotqqWW || ic == kPlotggWW ||
         ic == kPlotSignal0 || ic == kPlotSignal1 || ic == kPlotSignal2 ||
         ic == kPlotSignal3 || ic == kPlotSignal4 || ic == kPlotSignal5 ||
         ic == kPlotDY      || ic == kPlotTT      || ic == kPlotTW){ // only first bin == same-sign CR
        histo_WrongSignUncUp  [ic]->SetBinContent(1,histo_Baseline[ic]->GetBinContent(1)*1.10);
        histo_WrongSignUncDown[ic]->SetBinContent(1,histo_Baseline[ic]->GetBinContent(1)/1.10);
      }
    }

  } // loop over categories

  // QCD scale uncertainty for ggWW
  for(int ic=0; ic<nPlotCategories; ic++) {
    if(ic == kPlotSignal3 || ic == kPlotSignal4 || ic == kPlotSignal5 || ic == kPlotggWW) {
      histo_QCDScaleUp[ic]  ->Scale(1.05);
      histo_QCDScaleDown[ic]->Scale(1./1.05);
    }
  }

  // Begin Nonprompt study
  const int nNonPromptSyst = 12;
  TString namenonPromptSyst[nSystTotal];
  namenonPromptSyst[ 0] = "CMS_SMP24001_fake_m0Up";
  namenonPromptSyst[ 1] = "CMS_SMP24001_fake_m1Down";
  namenonPromptSyst[ 2] = "CMS_SMP24001_fake_m2Up";
  namenonPromptSyst[ 3] = "CMS_SMP24001_fake_e0Up";
  namenonPromptSyst[ 4] = "CMS_SMP24001_fake_e1Up";
  namenonPromptSyst[ 5] = "CMS_SMP24001_fake_e2Up";
  namenonPromptSyst[ 6] = "CMS_SMP24001_fake_m0Down";
  namenonPromptSyst[ 7] = "CMS_SMP24001_fake_m1Up";
  namenonPromptSyst[ 8] = "CMS_SMP24001_fake_m2Down";
  namenonPromptSyst[ 9] = "CMS_SMP24001_fake_e0Down";
  namenonPromptSyst[10] = "CMS_SMP24001_fake_e1Down";
  namenonPromptSyst[11] = "CMS_SMP24001_fake_e2Down";
  TH1D *histo_NonPromtUnc[nNonPromptSyst];
  for(int j=0; j<nNonPromptSyst; j++){
    histo_NonPromtUnc[j] = new TH1D(Form("histo_%s_%s", plotBaseNames[kPlotNonPrompt].Data(), namenonPromptSyst[j].Data()), Form("histo_%s_%s", plotBaseNames[kPlotNonPrompt].Data(), namenonPromptSyst[j].Data()), BinXF, minXF, maxXF);
  }

  const int totalNumberFakeSyst = 6;
  if(whichAna == 0){ 
    TH1D *histo_InputNonPromtUnc[30];
    inputFile = new TFile(Form("%s/fillhisto_%s_%d_nonprompt.root",InputDir.Data(),anaSel.Data(),year), "read");
    for(int j=0; j<30; j++){
      histo_InputNonPromtUnc[j] = (TH1D*)inputFile->Get(Form("histoNonPrompt_%d", j));
    }
    for(int j=0; j<totalNumberFakeSyst; j++){
      for(unsigned nSel=0; nSel<nSelTotal; nSel++) {
        histo_NonPromtUnc[j]->SetBinContent(nSel+1,histo_InputNonPromtUnc[j+nSel*totalNumberFakeSyst]->GetBinContent(fidAna));
        histo_NonPromtUnc[j]->SetBinError  (nSel+1,histo_InputNonPromtUnc[j+nSel*totalNumberFakeSyst]->GetBinError  (fidAna));
      }
    }
    delete inputFile;
  } else {
    TH1D *histo_InputNonPromtUnc[18];
    inputFile = new TFile(Form("%s/fillhisto_%s_%d_nonprompt.root",InputDir.Data(),anaSel.Data(),year), "read");
    for(int j=0; j<18; j++){
      histo_InputNonPromtUnc[j] = (TH1D*)inputFile->Get(Form("histoNonPrompt_%d", 30+j));
    }
    for(int j=0; j<totalNumberFakeSyst; j++){
      for(int nb=1; nb<=histo_InputNonPromtUnc[j]->GetNbinsX(); nb++){
        histo_NonPromtUnc[j]->SetBinContent(nb,histo_InputNonPromtUnc[j+(fidAna-1)*totalNumberFakeSyst]->GetBinContent(nb));
        histo_NonPromtUnc[j]->SetBinError  (nb,histo_InputNonPromtUnc[j+(fidAna-1)*totalNumberFakeSyst]->GetBinError  (nb));
      }
    }
  }

  for(int j=0; j<totalNumberFakeSyst; j++){
    for(int nb=1; nb<=histo_Baseline[kPlotNonPrompt]->GetNbinsX(); nb++){
      if(histo_Baseline[kPlotNonPrompt]->GetBinContent(nb) > 0) {
        systValue = histo_NonPromtUnc[j+0]->GetBinContent(nb) / histo_Baseline[kPlotNonPrompt]->GetBinContent(nb);
        if     (systValue > 0 && systValue > 1.15) systValue = 1.15;
        else if(systValue > 0 && systValue < 0.85) systValue = 0.85;
        histo_NonPromtUnc[j+0]->SetBinContent(nb,histo_Baseline[kPlotNonPrompt]->GetBinContent(nb)*systValue);
        if(whichAna == 0) printf("fake(%d,%d) = %.3f\n",j,nb,systValue);
        if(systValue > 0) histo_NonPromtUnc[j+totalNumberFakeSyst]->SetBinContent(nb,histo_Baseline[kPlotNonPrompt]->GetBinContent(nb)/systValue);
        else {
                          histo_NonPromtUnc[j+                  0]->SetBinContent(nb,histo_Baseline[kPlotNonPrompt]->GetBinContent(nb));
                          histo_NonPromtUnc[j+totalNumberFakeSyst]->SetBinContent(nb,histo_Baseline[kPlotNonPrompt]->GetBinContent(nb));
             }
      }
      else {
        histo_NonPromtUnc[j+                  0]->SetBinContent(nb,0.0f);
        histo_NonPromtUnc[j+totalNumberFakeSyst]->SetBinContent(nb,0.0f);
      }
    }
  }
  // End Nonprompt study

  TString additionalSuffix = "";
  if(whichAna != 0){ 
    additionalSuffix = "_alt";
  }

  TString outputLimits = Form("output_%s_%d_bin%d%s%s.root",anaSel.Data(),year,fidAna-1,additionalSuffix.Data(),addFiducialName.Data());
  outputFile = new TFile(outputLimits, "RECREATE");
  outputFile->cd();
  for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
    if(histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    histo_Baseline[ic]->Write();
    for(int j=0; j<nSystDataCardTotal; j++) histo_SystDataCard[j][ic]->Write();

    histo_WrongSignUncUp   [ic]->Write();
    histo_WrongSignUncDown [ic]->Write();
    histo_WWNNLO_resumUp   [ic]->Write();
    histo_WWNNLO_resumDown [ic]->Write();
    histo_WWNNLO_scaleUp   [ic]->Write();
    histo_WWNNLO_scaleDown [ic]->Write();
    histo_WWNNLO_GenJetUp  [ic]->Write();
    histo_WWNNLO_GenJetDown[ic]->Write();
    histo_QCDScaleUp  [ic]->Write();
    histo_QCDScaleDown[ic]->Write();
    histo_PSUp        [ic]->Write();
    histo_PSDown      [ic]->Write();
    for(int npdf=0; npdf<101; npdf++){
      histo_PDFUp  [npdf][ic]->Write();
      histo_PDFDown[npdf][ic]->Write();
    }
  }
  for(int j=0; j<nNonPromptSyst; j++) histo_NonPromtUnc[j]->Write();
  outputFile->Close();

  // Filling datacards txt file
  char outputLimitsCard[200];
  sprintf(outputLimitsCard,"datacard_%s_%d_bin%d%s%s.txt",anaSel.Data(),year,fidAna-1,additionalSuffix.Data(),addFiducialName.Data());
  ofstream newcardShape;
  newcardShape.open(outputLimitsCard);
  newcardShape << Form("imax * number of channels\n");
  newcardShape << Form("jmax * number of background minus 1\n");
  newcardShape << Form("kmax * number of nuisance parameters\n");

  newcardShape << Form("shapes    *   *   %s  histo_$PROCESS histo_$PROCESS_$SYSTEMATIC\n",outputLimits.Data());
  newcardShape << Form("shapes data_obs * %s  histo_Data\n",outputLimits.Data());

  newcardShape << Form("Observation %f\n",histo_Baseline[kPlotData]->GetSumOfWeights());

  newcardShape << Form("bin   ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    newcardShape << Form("ch%d ",fidAna-1);

  }
  newcardShape << Form("\n");

  newcardShape << Form("process  ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    newcardShape << Form("%s  ", plotBaseNames[ic].Data());
  }
  newcardShape << Form("\n");

  newcardShape << Form("process  ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic != kPlotSignal0 &&
            ic != kPlotSignal1 &&
            ic != kPlotSignal2 &&
            ic != kPlotSignal3 &&
            ic != kPlotSignal4 &&
            ic != kPlotSignal5 &&
            ic != kPlotqqWW    &&
            ic != kPlotggWW
            ) newcardShape << Form("%d  ", ic);
    else if(ic == kPlotSignal0) newcardShape << Form("%d  ", -1);
    else if(ic == kPlotSignal1) newcardShape << Form("%d  ", -2);
    else if(ic == kPlotSignal2) newcardShape << Form("%d  ", -3);
    else if(ic == kPlotSignal3) newcardShape << Form("%d  ", -4);
    else if(ic == kPlotSignal4) newcardShape << Form("%d  ", -5);
    else if(ic == kPlotSignal5) newcardShape << Form("%d  ", -6);
    else if(ic == kPlotqqWW)    newcardShape << Form("%d  ", -7);
    else if(ic == kPlotggWW)    newcardShape << Form("%d  ", -8);
  }
  newcardShape << Form("\n");

  newcardShape << Form("rate  ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    newcardShape << Form("%f  ", histo_Baseline[ic]->GetSumOfWeights());
  }
  newcardShape << Form("\n");

  //newcardShape << Form("CMS_fakee_norm lnN ");
  //for (int ic=0; ic<nPlotCategories; ic++){
  //  if(!histo_Baseline[ic]) continue;
  //  if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
  //  if(ic == kPlotNonPrompt) newcardShape << Form("%6.3f ",1.15);
  //  else                     newcardShape << Form("- "); 
  //}
  //newcardShape << Form("\n");

  //newcardShape << Form("CMS_fakem_norm   lnN     ");
  //for (int ic=0; ic<nPlotCategories; ic++){
  //  if(!histo_Baseline[ic]) continue;
  //  if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
  //  if(ic == kPlotNonPrompt) newcardShape << Form("%6.3f ",1.15);
  //  else                     newcardShape << Form("- ");
  //}
  //newcardShape << Form("\n");

  if(whichAna == 0) {
    newcardShape << Form("CMS_SMP24001_wrongsign_e shape ");
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotqqWW || ic == kPlotggWW ||
         ic == kPlotSignal0 || ic == kPlotSignal1 || ic == kPlotSignal2 ||
         ic == kPlotSignal3 || ic == kPlotSignal4 || ic == kPlotSignal5 ||
         ic == kPlotDY      || ic == kPlotTT      || ic == kPlotTW) newcardShape << Form("1.0 ");
      else                                                          newcardShape << Form("- "); 
    }
    newcardShape << Form("\n");
  }

  newcardShape << Form("CMS_SMP24001_fake_m0 shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
    else                     newcardShape << Form("- "); 
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_SMP24001_fake_m1 shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
    else                     newcardShape << Form("- "); 
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_SMP24001_fake_m2 shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
    else                     newcardShape << Form("- "); 
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_SMP24001_fake_e0 shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
    else                     newcardShape << Form("- "); 
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_SMP24001_fake_e1 shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
    else                     newcardShape << Form("- "); 
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_SMP24001_fake_e2 shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
    else                     newcardShape << Form("- "); 
  }
  newcardShape << Form("\n");

  newcardShape << Form("luminosity_%d   lnN     ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("%6.3f ",1.014);
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_SMP24001_WWtrigger_%d   lnN     ",year);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("%6.3f ",triggerEffUnc);
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s shape ",BtagSFBCNames[ 0].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s shape ",BtagSFBCNames[ 1].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s shape ",BtagSFBCNames[ 2].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s shape ",BtagSFBCNames[ 3].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s shape ",BtagSFBCNames[ 4].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s shape ",BtagSFBCNames[ 5].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s shape ",BtagSFBCNames[ 6].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s shape ",BtagSFBCNames[ 7].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s shape ",BtagSFBCNames[ 8].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s shape ",BtagSFBCNames[ 9].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s shape ",BtagSFBCNames[10].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s shape ",BtagSFBCNames[11].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("%s_%d shape ",BtagSFBCNames[12].Data(),year);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_lf_btag shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_eff_m_reco_%d shape ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_eff_m_id_%d shape ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_eff_m_iso_%d shape ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_eff_e_reco_%d shape ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_eff_e_id_%d shape ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("pileup shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[1].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[2].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[3].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[4].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[5].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[6].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[7].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[8].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[9].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[10].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[11].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[12].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[13].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[14].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[15].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[16].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[17].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[18].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[19].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[20].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[21].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[22].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[23].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[24].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[25].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[26].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[27].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_res_j_%d shape ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_m_%d shape ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_e_%d shape ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_met_jer_%d shape ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else		     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_met_jes_%d shape ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else		     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_met_unclustered_%d shape ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else		     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  for(unsigned ic=0; ic<nPlotCategories; ic++) {
    if(ic== kPlotData || ic == kPlotNonPrompt || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    //if(ic== kPlotSignal0 || ic == kPlotSignal1 || ic== kPlotSignal2 || ic == kPlotSignal3 || ic == kPlotSignal4 || ic == kPlotSignal5 || ic == kPlotqqWW || ic == kPlotggWW) continue;
    newcardShape << Form("QCD_scale_%s_ACCEPT shape ",plotBaseNames[ic].Data());
    for(unsigned ic2=0; ic2<nPlotCategories; ic2++) {
      if(ic2 == kPlotData || histo_Baseline[ic2]->GetSumOfWeights() <= 0) continue;
      if(ic==ic2) newcardShape << Form("1.0  ");
      else        newcardShape << Form("-  ");
    }
    newcardShape << Form("\n");
  }

  //newcardShape << Form("QCDScale_qqWW_ACCEPT shape ");
  //for (int ic=0; ic<nPlotCategories; ic++){
  //  if(!histo_Baseline[ic]) continue;
  //  if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
  //  if     (ic != kPlotSignal0 &&
  //          ic != kPlotSignal1 &&
  //          ic != kPlotSignal2 &&
  //          ic != kPlotqqWW
  //          ) newcardShape << Form("- ");
  //  else      newcardShape << Form("1.0 ");
  //}
  //newcardShape << Form("\n");

  //newcardShape << Form("QCDScale_ggWW_ACCEPT shape ");
  //for (int ic=0; ic<nPlotCategories; ic++){
  //  if(!histo_Baseline[ic]) continue;
  //  if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
  //  if     (ic != kPlotSignal3 &&
  //          ic != kPlotSignal4 &&
  //          ic != kPlotSignal5 &&
  //          ic != kPlotggWW
  //          ) newcardShape << Form("- ");
  //  else      newcardShape << Form("1.0 ");
  //}
  //newcardShape << Form("\n");

  for(unsigned ic=0; ic<nPlotCategories; ic++) {
    if(ic== kPlotData || ic == kPlotNonPrompt || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    //if(ic== kPlotSignal0 || ic == kPlotSignal1 || ic== kPlotSignal2 || ic == kPlotSignal3 || ic == kPlotSignal4 || ic == kPlotSignal5 || ic == kPlotqqWW || ic == kPlotggWW) continue;
    newcardShape << Form("PS_%s_ACCEPT shape ",plotBaseNames[ic].Data());
    for(unsigned ic2=0; ic2<nPlotCategories; ic2++) {
      if(ic2 == kPlotData || histo_Baseline[ic2]->GetSumOfWeights() <= 0) continue;
      if(ic==ic2) newcardShape << Form("1.0  ");
      else        newcardShape << Form("-  ");
    }
    newcardShape << Form("\n");
  } 

  //newcardShape << Form("PS_qqWW_ACCEPT shape ");
  //for (int ic=0; ic<nPlotCategories; ic++){
  //  if(!histo_Baseline[ic]) continue;
  //  if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
  //  if     (ic != kPlotSignal0 &&
  //          ic != kPlotSignal1 &&
  //          ic != kPlotSignal2 &&
  //          ic != kPlotqqWW
  //          ) newcardShape << Form("- ");
  //  else      newcardShape << Form("1.0 ");
  //}
  //newcardShape << Form("\n");

  //newcardShape << Form("PS_ggWW_ACCEPT shape ");
  //for (int ic=0; ic<nPlotCategories; ic++){
  //  if(!histo_Baseline[ic]) continue;
  //  if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
  //  if     (ic != kPlotSignal3 &&
  //          ic != kPlotSignal4 &&
  //          ic != kPlotSignal5 &&
  //          ic != kPlotggWW
  //          ) newcardShape << Form("- ");
  //  else      newcardShape << Form("1.0 ");
  //}
  //newcardShape << Form("\n");

  if(whichAna == 100){ // Never enter here
    newcardShape << Form("WWNNLO_resum shape ");
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if     (ic != kPlotSignal0 &&
              ic != kPlotSignal1 &&
              ic != kPlotSignal2 &&
              ic != kPlotSignal3 &&
              ic != kPlotSignal4 &&
              ic != kPlotSignal5 &&
              ic != kPlotqqWW    &&
              ic != kPlotggWW
              ) newcardShape << Form("- ");
      else      newcardShape << Form("1.0 ");
    }
    newcardShape << Form("\n");

    newcardShape << Form("WWNNLO_scale shape ");
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if     (ic != kPlotSignal0 &&
              ic != kPlotSignal1 &&
              ic != kPlotSignal2 &&
              ic != kPlotSignal3 &&
              ic != kPlotSignal4 &&
              ic != kPlotSignal5 &&
              ic != kPlotqqWW    &&
              ic != kPlotggWW
              ) newcardShape << Form("- ");
      else      newcardShape << Form("1.0 ");
    }
    newcardShape << Form("\n");
  }

  if(isFiducial == false && whichAna == 200){ // Never enter here
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if     (ic != kPlotSignal0 &&
              ic != kPlotSignal1 &&
              ic != kPlotSignal2 &&
              ic != kPlotSignal3 &&
              ic != kPlotSignal4 &&
              ic != kPlotSignal5
              ) continue;
      newcardShape << Form("WWNNLO_%s_GenJet shape ",plotBaseNames[ic].Data());
      for(unsigned ic2=0; ic2<nPlotCategories; ic2++) {
        if(ic2 == kPlotData || histo_Baseline[ic2]->GetSumOfWeights() <= 0) continue;
        if(ic==ic2) newcardShape << Form("1.0  ");
        else        newcardShape << Form("-  ");
      }
      newcardShape << Form("\n");
    }
  }

  /*for(int npdf=0; npdf<=100; npdf++){
    newcardShape << Form("pdf%d shape ",npdf);
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("- ");
      else if(isFiducial == true && 
           (ic != kPlotSignal0 &&
              ic != kPlotSignal1 &&
              ic != kPlotSignal2 &&
              ic != kPlotSignal3 &&
              ic != kPlotSignal4 &&
              ic != kPlotSignal5 &&
              ic != kPlotqqWW    &&
              ic != kPlotggWW
            ))                 newcardShape << Form("- ");
      else                     newcardShape << Form("1.0 ");
    }
    newcardShape << Form("\n");
  }*/

  for(int npdf=100; npdf<=100; npdf++){
    newcardShape << Form("pdf%d shape ",npdf);
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("- ");
      else                     newcardShape << Form("1.0 ");
    }
    newcardShape << Form("\n");
  }

  newcardShape << Form("pdfqq   lnN     ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("%6.3f ",1.005);
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_ww_fakenorm_bin%d_%d  rateParam * %s 1 [0.1,4.9]\n",fidAna-1,year,plotBaseNames[kPlotNonPrompt].Data());
  newcardShape << Form("CMS_ww_dytautaunorm_bin%d_%d  rateParam * %s 1 [0.1,4.9]\n",fidAna-1,year,plotBaseNames[kPlotDY].Data());
  newcardShape << Form("CMS_ww_topnorm_bin%d_%d  rateParam * %s 1 [0.1,4.9]\n",fidAna-1,year,plotBaseNames[kPlotTT].Data());
  newcardShape << Form("CMS_ww_topnorm_bin%d_%d  rateParam * %s 1 [0.1,4.9]\n",fidAna-1,year,plotBaseNames[kPlotTW].Data());
  //newcardShape << Form("CMS_ww_wznorm rateParam * %s 1 [0.1,4.9]\n",plotBaseNames[kPlotWZ].Data());
  //newcardShape << Form("CMS_ww_zznorm rateParam * %s 1 [0.1,4.9]\n",plotBaseNames[kPlotZZ].Data());

  newcardShape << Form("ch%d autoMCStats 0\n",fidAna-1);

  newcardShape.close();

}
