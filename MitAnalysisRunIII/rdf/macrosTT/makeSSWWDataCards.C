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

// whichAna = 0 (SSWW), fidAna = 0/2/4 (WW), 1/3/5 (WWb)
// whichAna = 0 (WZ), fidAna = 0 (WZ), 1 (WZb)

void makeSSWWDataCards(int whichAna = 0, int fidAna = 0, TString InputDir = "anaZ", TString anaSel = "sswwAnalysis1001", int year = 20220){

  if(fidAna < 0 || fidAna > 6) printf("Wrong fidAna(%d)\n",fidAna);

  int isTypeFakeSyst = 2;
  plotBaseNames[kPlotNonPrompt] = "NonPrompt";
  if     (anaSel.Contains("wzAnalysis")) {plotBaseNames[kPlotNonPrompt] = "NonWZPrompt";}
  else if(anaSel.Contains("zzAnalysis")) {plotBaseNames[kPlotNonPrompt] = "NonZZPrompt"; isTypeFakeSyst = 0;}

  int theYear = 0;
  double triggerEffUnc = 1.000;
  if     (year == 20220) {triggerEffUnc = 1.005; theYear = 2022;}
  else if(year == 20221) {triggerEffUnc = 1.005; theYear = 2022;}
  else if(year == 20230) {triggerEffUnc = 1.005; theYear = 2023;}
  else if(year == 20231) {triggerEffUnc = 1.005; theYear = 2023;}
  else {printf("Wrong year!\n"); return;}

  int jumpValue = 200;
  int startHistogram = 0;
  TString postFixFile = "_mva";
  TString postFixHist = "MVA";
  if     (anaSel.Contains("wzAnalysis")) {startHistogram = 300; postFixFile = ""; postFixHist = "";}
  else if(anaSel.Contains("zzAnalysis")) {startHistogram = 300; postFixFile = ""; postFixHist = "";}

  double systValue;
  TFile *inputFile;
  TFile *outputFile;
  const int endTheory = 113;
  const int nSystTotal = 169;
  const int nSystDataCardTotal = 112; // (nSystTotal-endTheory)*2 = nSystDataCardTotal

  TH1D *histo_Baseline[nPlotCategories];
  TH1D *histo_QCDScaleUp[nPlotCategories];
  TH1D *histo_QCDScaleDown[nPlotCategories];
  TH1D *histo_PSUp[nPlotCategories];
  TH1D *histo_PSDown[nPlotCategories];

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
  nameSyst[12 ] = Form("CMS_SMPXXXXX_WWtrigger_%dUp",year);
  nameSyst[13 ] = Form("CMS_SMPXXXXX_WWtrigger_%dDown",year);
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
  nameSyst[42 ] = "ewkCorrUp";
  nameSyst[43 ] = "ewkCorrDown";
  nameSyst[44 ] = Form("CMS_scale_m_%dUp",theYear);
  nameSyst[45 ] = Form("CMS_scale_m_%dDown",theYear);
  nameSyst[46 ] = Form("CMS_scale_e_%dUp",theYear);
  nameSyst[47 ] = Form("CMS_scale_e_%dDown",theYear);
  nameSyst[48 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 0].Data());
  nameSyst[49 ] = Form("CMS_scale_j_%sDown",jesNames[ 0].Data());
  nameSyst[50 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 1].Data());
  nameSyst[51 ] = Form("CMS_scale_j_%sDown",jesNames[ 1].Data());
  nameSyst[52 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 2].Data());
  nameSyst[53 ] = Form("CMS_scale_j_%sDown",jesNames[ 2].Data());
  nameSyst[54 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 3].Data());
  nameSyst[55 ] = Form("CMS_scale_j_%sDown",jesNames[ 3].Data());
  nameSyst[56 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 4].Data());
  nameSyst[57 ] = Form("CMS_scale_j_%sDown",jesNames[ 4].Data());
  nameSyst[58 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 5].Data());
  nameSyst[59 ] = Form("CMS_scale_j_%sDown",jesNames[ 5].Data());
  nameSyst[60 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 6].Data());
  nameSyst[61 ] = Form("CMS_scale_j_%sDown",jesNames[ 6].Data());
  nameSyst[62 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 7].Data());
  nameSyst[63 ] = Form("CMS_scale_j_%sDown",jesNames[ 7].Data());
  nameSyst[64 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 8].Data());
  nameSyst[65 ] = Form("CMS_scale_j_%sDown",jesNames[ 8].Data());
  nameSyst[66 ] = Form("CMS_scale_j_%sUp"  ,jesNames[ 9].Data());
  nameSyst[67 ] = Form("CMS_scale_j_%sDown",jesNames[ 9].Data());
  nameSyst[68 ] = Form("CMS_scale_j_%sUp"  ,jesNames[10].Data());
  nameSyst[69 ] = Form("CMS_scale_j_%sDown",jesNames[10].Data());
  nameSyst[70 ] = Form("CMS_scale_j_%sUp"  ,jesNames[11].Data());
  nameSyst[71 ] = Form("CMS_scale_j_%sDown",jesNames[11].Data());
  nameSyst[72 ] = Form("CMS_scale_j_%sUp"  ,jesNames[12].Data());
  nameSyst[73 ] = Form("CMS_scale_j_%sDown",jesNames[12].Data());
  nameSyst[74 ] = Form("CMS_scale_j_%sUp"  ,jesNames[13].Data());
  nameSyst[75 ] = Form("CMS_scale_j_%sDown",jesNames[13].Data());
  nameSyst[76 ] = Form("CMS_scale_j_%sUp"  ,jesNames[14].Data());
  nameSyst[77 ] = Form("CMS_scale_j_%sDown",jesNames[14].Data());
  nameSyst[78 ] = Form("CMS_scale_j_%sUp"  ,jesNames[15].Data());
  nameSyst[79 ] = Form("CMS_scale_j_%sDown",jesNames[15].Data());
  nameSyst[80 ] = Form("CMS_scale_j_%sUp"  ,jesNames[16].Data());
  nameSyst[81 ] = Form("CMS_scale_j_%sDown",jesNames[16].Data());
  nameSyst[82 ] = Form("CMS_scale_j_%sUp"  ,jesNames[17].Data());
  nameSyst[83 ] = Form("CMS_scale_j_%sDown",jesNames[17].Data());
  nameSyst[84 ] = Form("CMS_scale_j_%sUp"  ,jesNames[18].Data());
  nameSyst[85 ] = Form("CMS_scale_j_%sDown",jesNames[18].Data());
  nameSyst[86 ] = Form("CMS_scale_j_%sUp"  ,jesNames[19].Data());
  nameSyst[87 ] = Form("CMS_scale_j_%sDown",jesNames[19].Data());
  nameSyst[88 ] = Form("CMS_scale_j_%sUp"  ,jesNames[20].Data());
  nameSyst[89 ] = Form("CMS_scale_j_%sDown",jesNames[20].Data());
  nameSyst[90 ] = Form("CMS_scale_j_%sUp"  ,jesNames[21].Data());
  nameSyst[91 ] = Form("CMS_scale_j_%sDown",jesNames[21].Data());
  nameSyst[92 ] = Form("CMS_scale_j_%sUp"  ,jesNames[22].Data());
  nameSyst[93 ] = Form("CMS_scale_j_%sDown",jesNames[22].Data());
  nameSyst[94 ] = Form("CMS_scale_j_%sUp"  ,jesNames[23].Data());
  nameSyst[95 ] = Form("CMS_scale_j_%sDown",jesNames[23].Data());
  nameSyst[96 ] = Form("CMS_scale_j_%sUp"  ,jesNames[24].Data());
  nameSyst[97 ] = Form("CMS_scale_j_%sDown",jesNames[24].Data());
  nameSyst[98 ] = Form("CMS_scale_j_%sUp"  ,jesNames[25].Data());
  nameSyst[99 ] = Form("CMS_scale_j_%sDown",jesNames[25].Data());
  nameSyst[100] = Form("CMS_scale_j_%sUp"  ,jesNames[26].Data());
  nameSyst[101] = Form("CMS_scale_j_%sDown",jesNames[26].Data());
  nameSyst[102] = Form("CMS_scale_j_%sUp"  ,jesNames[27].Data());
  nameSyst[103] = Form("CMS_scale_j_%sDown",jesNames[27].Data());
  nameSyst[104] = Form("CMS_res_j_%dUp",theYear);
  nameSyst[105] = Form("CMS_res_j_%dDown",theYear);
  nameSyst[106] = Form("CMS_met_jer_%dUp",theYear);
  nameSyst[107] = Form("CMS_met_jer_%dDown",theYear);
  nameSyst[108] = Form("CMS_met_jes_%dUp",theYear);
  nameSyst[109] = Form("CMS_met_jes_%dDown",theYear);
  nameSyst[110] = Form("CMS_met_unclustered_%dUp",theYear);
  nameSyst[111] = Form("CMS_met_unclustered_%dDown",theYear);

  int BinXF = 100; double minXF = 0; double maxXF = 1; TString nameFakeSyst = "random";
  if     (anaSel.Contains("sswwAnalysis")) {
    nameFakeSyst = "ssww";
  }
  else if(anaSel.Contains("wzAnalysis")) {
    nameFakeSyst = "wz";
  }
  else if(anaSel.Contains("zzAnalysis")) {
    nameFakeSyst = "zz";
  }
  else {
    printf("Wrong option\n");
    return;
  }

  inputFile = new TFile(Form("%s/fillhisto_%s_%d_%d%s.root",InputDir.Data(),anaSel.Data(),year,startHistogram+fidAna*jumpValue,postFixFile.Data()), "read");
  for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
    histo_Baseline[ic] = (TH1D*)inputFile->Get(Form("histo%s%d", postFixHist.Data(), ic)); assert(histo_Baseline[ic]); histo_Baseline[ic]->SetDirectory(0);
    if(ic == 0){
      BinXF = histo_Baseline[ic]->GetNbinsX();
      minXF = histo_Baseline[ic]->GetXaxis()->GetBinLowEdge(1);
      maxXF = histo_Baseline[ic]->GetXaxis()->GetBinUpEdge(BinXF);
    }
    histo_Baseline[ic]->SetNameTitle(Form("histo_%s",plotBaseNames[ic].Data()),Form("histo_%s",plotBaseNames[ic].Data()));
  }
  delete inputFile;
  printf("BinXF(%d) / minXF(%.2f) / maxXF(%.2f)\n",BinXF,minXF,maxXF);

  for(int ic=0; ic<nPlotCategories; ic++) {
    TString plotBaseNamesTemp =  plotBaseNames[ic];
    if     (ic == kPlotSignal0 || ic == kPlotSignal1 || ic == kPlotSignal2 || ic == kPlotSignal3 || ic == kPlotEWKSSWW) plotBaseNamesTemp = "EWKSSWW";
    histo_QCDScaleUp  [ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_QCD_scale_%s_ACCEPTUp"  , plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
    histo_QCDScaleDown[ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_QCD_scale_%s_ACCEPTDown", plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
    histo_PSUp  [ic]       = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_PS_%s_ACCEPTUp"  , plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
    histo_PSDown[ic]       = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_PS_%s_ACCEPTDown", plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
  }

  for(int j=0; j<nSystTotal; j++){
    for(int ic=0; ic<nPlotCategories; ic++) histo_Syst[j][ic] = new TH1D(Form("histo_%s_%d",plotBaseNames[ic].Data(),j),Form("histo_%s_%d",plotBaseNames[ic].Data(),j), BinXF, minXF, maxXF);
  }
  for(int j=0; j<nSystDataCardTotal; j++){
    for(int ic=0; ic<nPlotCategories; ic++) {
      if(
        (ic == kPlotEWKSSWW ||
         ic == kPlotSignal0 ||
         ic == kPlotSignal1 ||
         ic == kPlotSignal2 ||
         ic == kPlotSignal3) &&
         nameSyst[j].Contains("ewkCorr")) {
        histo_SystDataCard[j][ic] = new TH1D(Form("histo_%s_WW%s",plotBaseNames[ic].Data(),nameSyst[j].Data()),Form("histo_%s_WW%s",plotBaseNames[ic].Data(),nameSyst[j].Data()), BinXF, minXF, maxXF);
      }
      else if(
        (ic == kPlotEWKWZ) &&
         nameSyst[j].Contains("ewkCorr")) {
        histo_SystDataCard[j][ic] = new TH1D(Form("histo_%s_WZ%s",plotBaseNames[ic].Data(),nameSyst[j].Data()),Form("histo_%s_WZ%s",plotBaseNames[ic].Data(),nameSyst[j].Data()), BinXF, minXF, maxXF);
      }
      else {
        histo_SystDataCard[j][ic] = new TH1D(Form("histo_%s_%s",plotBaseNames[ic].Data(),nameSyst[j].Data()),Form("histo_%s_%s",plotBaseNames[ic].Data(),nameSyst[j].Data()), BinXF, minXF, maxXF);
      }
    }
  }
  for(int j=0; j<101; j++){
    for(int ic=0; ic<nPlotCategories; ic++) histo_PDFUp  [j][ic] = new TH1D(Form("histo_%s_pdf%dUp"  ,plotBaseNames[ic].Data(),j),Form("histo_%s_pdf%dUp"  ,plotBaseNames[ic].Data(),j), BinXF, minXF, maxXF);
    for(int ic=0; ic<nPlotCategories; ic++) histo_PDFDown[j][ic] = new TH1D(Form("histo_%s_pdf%dDown",plotBaseNames[ic].Data(),j),Form("histo_%s_pdf%dDown",plotBaseNames[ic].Data(),j), BinXF, minXF, maxXF);
  }

  for(int j=0; j<nSystTotal; j++){
    inputFile = new TFile(Form("%s/fillhisto_%s_%d_%d%s.root",InputDir.Data(),anaSel.Data(),year,startHistogram+fidAna*jumpValue+1+j,postFixFile.Data()), "read");
    for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
      histo_Syst[j][ic] = (TH1D*)inputFile->Get(Form("histo%s%d", postFixHist.Data(), ic)); assert(histo_Syst[j][ic]); histo_Syst[j][ic]->SetDirectory(0);
      // Renormalize distributions
      if(
        (ic == kPlotEWKSSWW ||
         ic == kPlotSignal0 ||
         ic == kPlotSignal1 ||
         ic == kPlotSignal2 ||
         ic == kPlotSignal3 ||
         ic == kPlotWZ ||
         ic == kPlotEWKWZ
        ) && histo_Baseline[ic]->GetSumOfWeights() > 0 &&
        (j == 0 || j == 1 || j == 2 || j == 3 ||
         j == 4 || j == 5 || j == 6 || j == 7 || j == 8 || j == 9 ||
         j == 134)
        ) histo_Syst[j][ic]->Scale(histo_Baseline[ic]->GetSumOfWeights()/histo_Syst[j][ic]->GetSumOfWeights());
    }
    delete inputFile;
  }

  for(unsigned ic=0; ic<nPlotCategories; ic++) {
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
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
  } // loop over categories

  // Begin Nonprompt study
  const int nNonPromptSyst = 12;
  TString namenonPromptSyst[nNonPromptSyst];
  namenonPromptSyst[ 0] = Form("CMS_SMPXXXXXX_fake_%s_m0Up",nameFakeSyst.Data());
  namenonPromptSyst[ 1] = Form("CMS_SMPXXXXXX_fake_%s_m1Down",nameFakeSyst.Data());
  namenonPromptSyst[ 2] = Form("CMS_SMPXXXXXX_fake_%s_m2Up",nameFakeSyst.Data());
  namenonPromptSyst[ 3] = Form("CMS_SMPXXXXXX_fake_%s_e0Up",nameFakeSyst.Data());
  namenonPromptSyst[ 4] = Form("CMS_SMPXXXXXX_fake_%s_e1Up",nameFakeSyst.Data());
  namenonPromptSyst[ 5] = Form("CMS_SMPXXXXXX_fake_%s_e2Up",nameFakeSyst.Data());
  namenonPromptSyst[ 6] = Form("CMS_SMPXXXXXX_fake_%s_m0Down",nameFakeSyst.Data());
  namenonPromptSyst[ 7] = Form("CMS_SMPXXXXXX_fake_%s_m1Up",nameFakeSyst.Data());
  namenonPromptSyst[ 8] = Form("CMS_SMPXXXXXX_fake_%s_m2Down",nameFakeSyst.Data());
  namenonPromptSyst[ 9] = Form("CMS_SMPXXXXXX_fake_%s_e0Down",nameFakeSyst.Data());
  namenonPromptSyst[10] = Form("CMS_SMPXXXXXX_fake_%s_e1Down",nameFakeSyst.Data());
  namenonPromptSyst[11] = Form("CMS_SMPXXXXXX_fake_%s_e2Down",nameFakeSyst.Data());
  const int totalNumberFakeSyst = 6;
  TH1D *histo_InputNonPromtUnc[totalNumberFakeSyst];
  TH1D *histo_NonPromtUnc[nNonPromptSyst];
  if(isTypeFakeSyst != 0){
    inputFile = new TFile(Form("%s/fillhisto_%s_%d_nonprompt.root",InputDir.Data(),anaSel.Data(),year), "read");
    int startH = totalNumberFakeSyst*fidAna;
    for(int j=0; j<totalNumberFakeSyst; j++){
      histo_InputNonPromtUnc[j] = (TH1D*)inputFile->Get(Form("histoNonPrompt_%d", j+startH));
      histo_NonPromtUnc[j+                  0] = (TH1D*)histo_InputNonPromtUnc[j]->Clone(Form("histo_%s_%s", plotBaseNames[kPlotNonPrompt].Data(), namenonPromptSyst[j+                  0].Data())); histo_NonPromtUnc[j+		    0]->SetDirectory(0);
      histo_NonPromtUnc[j+totalNumberFakeSyst] = (TH1D*)histo_InputNonPromtUnc[j]->Clone(Form("histo_%s_%s", plotBaseNames[kPlotNonPrompt].Data(), namenonPromptSyst[j+totalNumberFakeSyst].Data())); histo_NonPromtUnc[j+totalNumberFakeSyst]->SetDirectory(0);
    }
    delete inputFile;

    for(int j=0; j<totalNumberFakeSyst; j++){
      for(int nb=1; nb<=histo_Baseline[kPlotNonPrompt]->GetNbinsX(); nb++){
        histo_NonPromtUnc[j+                  0]->SetBinContent(nb, TMath::Max((float)histo_NonPromtUnc[j+                  0]->GetBinContent(nb),0.0f));
        histo_NonPromtUnc[j+totalNumberFakeSyst]->SetBinContent(nb, TMath::Max((float)histo_NonPromtUnc[j+totalNumberFakeSyst]->GetBinContent(nb),0.0f));
       if(histo_Baseline[kPlotNonPrompt]->GetBinContent(nb) > 0) {
          systValue = histo_NonPromtUnc[j+0]->GetBinContent(nb) / histo_Baseline[kPlotNonPrompt]->GetBinContent(nb);
          if     (systValue > 1.15) systValue = 1.15;
          else if(systValue < 0.85) systValue = 0.85;
          histo_NonPromtUnc[j+0]->SetBinContent(nb,histo_Baseline[kPlotNonPrompt]->GetBinContent(nb)*systValue);
          if(fabs(systValue-1) > 0.10) printf("fake(%d,%d) = %.3f\n",j,nb,systValue);
          if(systValue > 0) histo_NonPromtUnc[j+totalNumberFakeSyst]->SetBinContent(nb,histo_Baseline[kPlotNonPrompt]->GetBinContent(nb)/systValue);
        }
      }
    }
  }
  // End Nonprompt study

  // Begin wrongsign study
  const int nwrongsignSyst = 4;
  TString namewrongsignSyst[nwrongsignSyst];
  namewrongsignSyst[ 0] = "CMS_SMPXXXXXX_wrongsign_statUp";
  namewrongsignSyst[ 1] = "CMS_SMPXXXXXX_wrongsign_methodUp";
  namewrongsignSyst[ 2] = "CMS_SMPXXXXXX_wrongsign_statDown";
  namewrongsignSyst[ 3] = "CMS_SMPXXXXXX_wrongsign_methodDown";
  const int totalNumberWSSyst = 2;
  TH1D *histo_InputWSUnc[totalNumberWSSyst];
  TH1D *histo_WSUnc[nwrongsignSyst];
  if(anaSel.Contains("sswwAnalysis")){
    inputFile = new TFile(Form("%s/fillhisto_%s_%d_wrongsign.root",InputDir.Data(),anaSel.Data(),year), "read");
    int startH = totalNumberWSSyst*fidAna;
    for(int j=0; j<totalNumberWSSyst; j++){
      histo_InputWSUnc[j] = (TH1D*)inputFile->Get(Form("histoWS_%d", j+startH));
      histo_WSUnc[j+                0] = (TH1D*)histo_InputWSUnc[j]->Clone(Form("histo_%s_%s", plotBaseNames[kPlotWS].Data(), namewrongsignSyst[j+                0].Data())); histo_WSUnc[j+                0]->SetDirectory(0);
      histo_WSUnc[j+totalNumberWSSyst] = (TH1D*)histo_InputWSUnc[j]->Clone(Form("histo_%s_%s", plotBaseNames[kPlotWS].Data(), namewrongsignSyst[j+totalNumberWSSyst].Data())); histo_WSUnc[j+totalNumberWSSyst]->SetDirectory(0);
    }
    delete inputFile;

    for(int j=0; j<totalNumberWSSyst; j++){
      for(int nb=1; nb<=histo_Baseline[kPlotWS]->GetNbinsX(); nb++){
        histo_WSUnc[j+                0]->SetBinContent(nb, TMath::Max((float)histo_WSUnc[j+                0]->GetBinContent(nb),0.0f));
        histo_WSUnc[j+totalNumberWSSyst]->SetBinContent(nb, TMath::Max((float)histo_WSUnc[j+totalNumberWSSyst]->GetBinContent(nb),0.0f));
        if(histo_Baseline[kPlotWS]->GetBinContent(nb) > 0) {
          systValue = histo_WSUnc[j+0]->GetBinContent(nb) / histo_Baseline[kPlotWS]->GetBinContent(nb);
          if     (systValue > 1.15) systValue = 1.15;
          else if(systValue < 0.85) systValue = 0.85;
          histo_WSUnc[j+0]->SetBinContent(nb,histo_Baseline[kPlotWS]->GetBinContent(nb)*systValue);
          printf("ws(%d,%d) = %.3f\n",j,nb,systValue);
          if(systValue > 0) histo_WSUnc[j+totalNumberWSSyst]->SetBinContent(nb,histo_Baseline[kPlotWS]->GetBinContent(nb)/systValue);
        }
      }
    }
  }
  // End wrongsign study

  TString additionalSuffix = "";
  if(whichAna != 0){ 
    additionalSuffix = "_alt";
  }

  TString outputLimits = Form("output_%s_%d_bin%d%s.root",anaSel.Data(),year,fidAna,additionalSuffix.Data());
  outputFile = new TFile(outputLimits, "RECREATE");
  outputFile->cd();
  for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
    if(histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    histo_Baseline[ic]->Write();
    for(int j=0; j<nSystDataCardTotal; j++) histo_SystDataCard[j][ic]->Write();

    histo_QCDScaleUp  [ic]->Write();
    histo_QCDScaleDown[ic]->Write();
    histo_PSUp        [ic]->Write();
    histo_PSDown      [ic]->Write();
    for(int npdf=0; npdf<101; npdf++){
      histo_PDFUp  [npdf][ic]->Write();
      histo_PDFDown[npdf][ic]->Write();
    }
  }
  if(isTypeFakeSyst != 0) for(int j=0; j<nNonPromptSyst; j++) histo_NonPromtUnc[j]->Write();
  if(anaSel.Contains("sswwAnalysis")) for(int j=0; j<nwrongsignSyst; j++) histo_WSUnc[j]->Write();
  outputFile->Close();

  // Filling datacards txt file
  char outputLimitsCard[200];
  sprintf(outputLimitsCard,"datacard_%s_%d_bin%d%s.txt",anaSel.Data(),year,fidAna,additionalSuffix.Data());
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
    newcardShape << Form("ch%d ",fidAna);

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
    if     (ic != kPlotEWKSSWW &&
            ic != kPlotSignal0 &&
            ic != kPlotSignal1 &&
            ic != kPlotSignal2 &&
            ic != kPlotSignal3 &&
            ic != kPlotEWKWZ
           ) newcardShape << Form("%d  ", ic);
    else if(ic == kPlotEWKSSWW) newcardShape << Form("%d  ",  0);
    else if(ic == kPlotSignal0) newcardShape << Form("%d  ", -1);
    else if(ic == kPlotSignal1) newcardShape << Form("%d  ", -2);
    else if(ic == kPlotSignal2) newcardShape << Form("%d  ", -3);
    else if(ic == kPlotSignal3) newcardShape << Form("%d  ", -4);
    else if(ic == kPlotEWKWZ)   newcardShape << Form("%d  ", -5);
  }
  newcardShape << Form("\n");

  newcardShape << Form("rate  ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    newcardShape << Form("%f  ", histo_Baseline[ic]->GetSumOfWeights());
  }
  newcardShape << Form("\n");

  if(isTypeFakeSyst == 1){
    newcardShape << Form("CMS_SMPXXXXXX_fake_%s_m      lnN ",nameFakeSyst.Data());
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("%6.3f ",1.15);
      else		       newcardShape << Form("- "); 
    }
    newcardShape << Form("\n");

    newcardShape << Form("CMS_SMPXXXXXX_fake_%s_e lnN ",nameFakeSyst.Data());
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("%6.3f ",1.15);
      else		       newcardShape << Form("- ");
    }
    newcardShape << Form("\n");
  } // isTraditionalSyst == true
  else if(isTypeFakeSyst == 2){
    newcardShape << Form("CMS_SMPXXXXXX_fake_%s_m0 shape ",nameFakeSyst.Data());
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
      else		       newcardShape << Form("- "); 
    }
    newcardShape << Form("\n");

    newcardShape << Form("CMS_SMPXXXXXX_fake_%s_m1 shape ",nameFakeSyst.Data());
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
      else		       newcardShape << Form("- "); 
    }
    newcardShape << Form("\n");

    newcardShape << Form("CMS_SMPXXXXXX_fake_%s_m2 shape ",nameFakeSyst.Data());
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
      else		       newcardShape << Form("- "); 
    }
    newcardShape << Form("\n");

    newcardShape << Form("CMS_SMPXXXXXX_fake_%s_e0 shape ",nameFakeSyst.Data());
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
      else		       newcardShape << Form("- "); 
    }
    newcardShape << Form("\n");

    newcardShape << Form("CMS_SMPXXXXXX_fake_%s_e1 shape ",nameFakeSyst.Data());
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
      else		       newcardShape << Form("- "); 
    }
    newcardShape << Form("\n");

    newcardShape << Form("CMS_SMPXXXXXX_fake_%s_e2 shape ",nameFakeSyst.Data());
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
      else		       newcardShape << Form("- "); 
    }
    newcardShape << Form("\n");
  } // isTraditionalSyst == false

  newcardShape << Form("luminosity_%d   lnN     ",theYear);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("%6.3f ",1.014);
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_SMPXXXXX_WWtrigger_%d   lnN     ",year);
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("%6.3f ",triggerEffUnc);
  }
  newcardShape << Form("\n");

  if(anaSel.Contains("sswwAnalysis")) {
    newcardShape << Form("CMS_SMPXXXXXX_wrongsign_stat shape ");
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotWS) newcardShape << Form("1.0 ");
      else              newcardShape << Form("- "); 
    }
    newcardShape << Form("\n");


    newcardShape << Form("CMS_SMPXXXXXX_wrongsign_method shape ");
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotWS) newcardShape << Form("1.0 ");
      else              newcardShape << Form("- "); 
    }
    newcardShape << Form("\n");
  }

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
    if     (ic == kPlotSignal0 || ic == kPlotSignal1 || ic == kPlotSignal2 || ic == kPlotSignal3 || ic == kPlotEWKSSWW) continue;
    newcardShape << Form("QCD_scale_%s_ACCEPT shape ",plotBaseNames[ic].Data());
    for(unsigned ic2=0; ic2<nPlotCategories; ic2++) {
      if(ic2 == kPlotData || histo_Baseline[ic2]->GetSumOfWeights() <= 0) continue;
      if(ic==ic2) newcardShape << Form("1.0  ");
      else        newcardShape << Form("-  ");
      }
      newcardShape << Form("\n");
  } 

  newcardShape << Form("QCD_scale_EWKSSWW_ACCEPT shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic != kPlotSignal0 &&
            ic != kPlotSignal1 &&
            ic != kPlotSignal2 &&
            ic != kPlotSignal3 &&
            ic != kPlotEWKSSWW
            ) newcardShape << Form("- ");
    else      newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  for(unsigned ic=0; ic<nPlotCategories; ic++) {
    if(ic== kPlotData || ic == kPlotNonPrompt || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotSignal0 || ic == kPlotSignal1 || ic == kPlotSignal2 || ic == kPlotSignal3 || ic == kPlotEWKSSWW) continue;
    newcardShape << Form("PS_%s_ACCEPT shape ",plotBaseNames[ic].Data());
    for(unsigned ic2=0; ic2<nPlotCategories; ic2++) {
      if(ic2 == kPlotData || histo_Baseline[ic2]->GetSumOfWeights() <= 0) continue;
      if(ic==ic2) newcardShape << Form("1.0  ");
      else        newcardShape << Form("-  ");
      }
      newcardShape << Form("\n");
  } 

  newcardShape << Form("PS_EWKSSWW_ACCEPT shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic != kPlotSignal0 &&
            ic != kPlotSignal1 &&
            ic != kPlotSignal2 &&
            ic != kPlotSignal3 &&
            ic != kPlotEWKSSWW
           ) newcardShape << Form("- ");
    else     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("WWewkCorr shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic != kPlotSignal0 &&
            ic != kPlotSignal1 &&
            ic != kPlotSignal2 &&
            ic != kPlotSignal3 &&
            ic != kPlotEWKSSWW
            ) newcardShape << Form("- ");
    else      newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("WZewkCorr shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic != kPlotEWKWZ
            ) newcardShape << Form("- ");
    else      newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

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
    else                     newcardShape << Form("%6.3f ",1.01);
  }
  newcardShape << Form("\n");

  if(anaSel.Contains("sswwAnalysis") || anaSel.Contains("wzAnalysis")){
    if(histo_Baseline[kPlotWZ]->GetSumOfWeights() > 0)
    newcardShape << Form("CMS_ssww_wznorm  rateParam * %s 1 [0.1,4.9]\n",plotBaseNames[kPlotWZ].Data());
    if(histo_Baseline[kPlotEWKWZ]->GetSumOfWeights() > 0)
    newcardShape << Form("CMS_ssww_ewkwznorm  rateParam * %s 1 [0.1,4.9]\n",plotBaseNames[kPlotEWKWZ].Data());
  }
  if(anaSel.Contains("sswwAnalysis")){
    if(histo_Baseline[kPlotNonPrompt]->GetSumOfWeights() > 0)
    newcardShape << Form("CMS_ssww_nonpromptnorm_%d  rateParam * %s 1 [0.1,4.9]\n",(int)(fidAna/2),plotBaseNames[kPlotNonPrompt].Data());
  }
  //newcardShape << Form("CMS_ssww_zznorm  rateParam * %s 1 [0.1,4.9]\n",plotBaseNames[kPlotZZ].Data());

  newcardShape << Form("ch%d autoMCStats 0\n",fidAna);

  newcardShape.close();

}
