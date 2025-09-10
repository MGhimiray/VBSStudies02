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

// whichAna = 0 (WZ), fidAna = 0 (SR), 1 (CR)
// whichAna = 0 (ZZ), fidAna = 0 (SR)

void makeVVDataCards(int whichAna = 0, int fidAna = 0, TString InputDir = "anaZ", TString anaSel = "wwAnalysis1001", int year = 20221, int srAna = 1){

  if(fidAna < 0 || fidAna > 2) printf("Wrong fidAna(%d)\n",fidAna);

  plotBaseNames[kPlotNonPrompt] = "NonPromptWZ";

  double triggerEffUnc = 1.001;

  int jumpValue = 200;

  double systValue;
  TFile *inputFile;
  TFile *outputFile;
  const int endTheory = 113;
  const int nSystTotal = 168;
  const int nSystDataCardTotal = 110; // (nSystTotal-endTheory)*2 = nSystDataCardTotal

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

  TString nameSyst[nSystDataCardTotal];
  nameSyst[  0] = "CMS_eff_m_recoUp";
  nameSyst[  1] = "CMS_eff_m_recoDown";
  nameSyst[  2] = "CMS_eff_m_idUp";
  nameSyst[  3] = "CMS_eff_m_idDown";
  nameSyst[  4] = "CMS_eff_m_isoUp";
  nameSyst[  5] = "CMS_eff_m_isoDown";
  nameSyst[  6] = "CMS_eff_e_recoUp";
  nameSyst[  7] = "CMS_eff_e_recoDown";
  nameSyst[  8] = "CMS_eff_e_idUp";
  nameSyst[  9] = "CMS_eff_e_idDown";
  nameSyst[10 ] = "pileupUp";
  nameSyst[11 ] = "pileupDown";
  nameSyst[12 ] = "CMS_SMP24001_WWtriggerUp";
  nameSyst[13 ] = "CMS_SMP24001_WWtriggerDown";
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
  nameSyst[42 ] = "CMS_scale_mUp";
  nameSyst[43 ] = "CMS_scale_mDown";
  nameSyst[44 ] = "CMS_scale_eUp";
  nameSyst[45 ] = "CMS_scale_eDown";
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
  nameSyst[102] = "CMS_res_jUp";
  nameSyst[103] = "CMS_res_jDown";
  nameSyst[104] = "CMS_met_jerUp";
  nameSyst[105] = "CMS_met_jerDown";
  nameSyst[106] = "CMS_met_jesUp";
  nameSyst[107] = "CMS_met_jesDown";
  nameSyst[108] = "CMS_met_unclusteredUp";
  nameSyst[109] = "CMS_met_unclusteredDown";

  //int BinXF = 4; double minXF = -0.5; double maxXF = 3.5;
  int BinXF = 1; double minXF = -0.5; double maxXF = 3.5;

  if(anaSel.Contains("zzAnalysis")) {
    printf("Modifying default binning\n");
    //BinXF = 3; minXF = -0.5; maxXF = 2.5;
    BinXF = 1; minXF = -0.5; maxXF = 2.5;
  }

  for(int ic=0; ic<nPlotCategories; ic++) {
    histo_Baseline[ic] = new TH1D(Form("histo_%s",plotBaseNames[ic].Data()),Form("histo_%s",plotBaseNames[ic].Data()), BinXF, minXF, maxXF);
    TString plotBaseNamesTemp =  plotBaseNames[ic];
    histo_QCDScaleUp  [ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_QCD_scale_%s_ACCEPTUp"  , plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
    histo_QCDScaleDown[ic] = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_QCD_scale_%s_ACCEPTDown", plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
    histo_PSUp  [ic]       = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_PS_%s_ACCEPTUp"  , plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
    histo_PSDown[ic]       = (TH1D*)histo_Baseline[ic]->Clone(Form("histo_%s_PS_%s_ACCEPTDown", plotBaseNames[ic].Data(), plotBaseNamesTemp.Data()));
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

  inputFile = new TFile(Form("%s/fillhisto_%s_%d_%d.root",InputDir.Data(),anaSel.Data(),year,300+fidAna*jumpValue), "read");
  for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
    histo_Baseline[ic] = (TH1D*)inputFile->Get(Form("histo%d", ic)); assert(histo_Baseline[ic]); histo_Baseline[ic]->SetDirectory(0);
    histo_Baseline[ic]->SetNameTitle(Form("histo_%s",plotBaseNames[ic].Data()),Form("histo_%s",plotBaseNames[ic].Data()));
  }
  delete inputFile;

  for(int j=0; j<nSystTotal; j++){
    inputFile = new TFile(Form("%s/fillhisto_%s_%d_%d.root",InputDir.Data(),anaSel.Data(),year,300+fidAna*jumpValue+1+j), "read");
    for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
      histo_Syst[j][ic] = (TH1D*)inputFile->Get(Form("histo%d", ic)); assert(histo_Syst[j][ic]); histo_Syst[j][ic]->SetDirectory(0);
      histo_Syst[j][ic]->SetNameTitle(Form("histo_%s_%s",plotBaseNames[ic].Data(),nameSyst[j].Data()),Form("histo_%s_%s",plotBaseNames[ic].Data(),nameSyst[j].Data()));
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
        // a
        systValue = histo_SystDataCard[42][ic]->GetBinContent(nb) / histo_Baseline[ic]->GetBinContent(nb);
        if     (systValue > 0 && systValue > 1.15) systValue = 1.15;
        else if(systValue > 0 && systValue < 0.85) systValue = 0.85;
        histo_SystDataCard[42][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb)*systValue);
        systValue = histo_SystDataCard[42][ic]->GetBinContent(nb) / histo_Baseline[ic]->GetBinContent(nb);
        if(systValue > 0) histo_SystDataCard[43][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb)/systValue);
        else {
                          histo_SystDataCard[42][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb));
                          histo_SystDataCard[43][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb));
             }
        // b
        systValue = histo_SystDataCard[44][ic]->GetBinContent(nb) / histo_Baseline[ic]->GetBinContent(nb);
        if     (systValue > 0 && systValue > 1.15) systValue = 1.15;
        else if(systValue > 0 && systValue < 0.85) systValue = 0.85;
        histo_SystDataCard[44][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb)*systValue);
        systValue = histo_SystDataCard[44][ic]->GetBinContent(nb) / histo_Baseline[ic]->GetBinContent(nb);
        if(systValue > 0) histo_SystDataCard[45][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb)/systValue);
        else {
                          histo_SystDataCard[44][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb));
                          histo_SystDataCard[45][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb));
             }
        // c
        systValue = (histo_SystDataCard[102][ic]->GetBinContent(nb)-histo_Baseline[ic]->GetBinContent(nb))/10.0;
        histo_SystDataCard[102][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb)+systValue);
        systValue = histo_SystDataCard[102][ic]->GetBinContent(nb) / histo_Baseline[ic]->GetBinContent(nb);
        if(systValue > 0) histo_SystDataCard[103][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb)/systValue);
        else {
                          histo_SystDataCard[102][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb));
                          histo_SystDataCard[103][ic]->SetBinContent(nb,histo_Baseline[ic]->GetBinContent(nb));
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
  TString namenonPromptSyst[nSystTotal];
  namenonPromptSyst[ 0] = "CMS_SMP24001WZ_fake_m0Up";
  namenonPromptSyst[ 1] = "CMS_SMP24001WZ_fake_m1Down";
  namenonPromptSyst[ 2] = "CMS_SMP24001WZ_fake_m2Up";
  namenonPromptSyst[ 3] = "CMS_SMP24001WZ_fake_e0Up";
  namenonPromptSyst[ 4] = "CMS_SMP24001WZ_fake_e1Up";
  namenonPromptSyst[ 5] = "CMS_SMP24001WZ_fake_e2Up";
  namenonPromptSyst[ 6] = "CMS_SMP24001WZ_fake_m0Down";
  namenonPromptSyst[ 7] = "CMS_SMP24001WZ_fake_m1Up";
  namenonPromptSyst[ 8] = "CMS_SMP24001WZ_fake_m2Down";
  namenonPromptSyst[ 9] = "CMS_SMP24001WZ_fake_e0Down";
  namenonPromptSyst[10] = "CMS_SMP24001WZ_fake_e1Down";
  namenonPromptSyst[11] = "CMS_SMP24001WZ_fake_e2Down";
  const int totalNumberFakeSyst = 6;
  TH1D *histo_InputNonPromtUnc[totalNumberFakeSyst];
  TH1D *histo_NonPromtUnc[nNonPromptSyst];
  if(anaSel.Contains("wzAnalysis")){
    inputFile = new TFile(Form("%s/fillhisto_%s_%d_nonprompt.root",InputDir.Data(),anaSel.Data(),year), "read");
    int startH = 0; if(fidAna == 1) startH = totalNumberFakeSyst;
    for(int j=0; j<totalNumberFakeSyst; j++){
      histo_InputNonPromtUnc[j] = (TH1D*)inputFile->Get(Form("histoNonPrompt_%d", j+startH));
      histo_NonPromtUnc[j+                  0] = (TH1D*)histo_InputNonPromtUnc[j]->Clone(Form("histo_%s_%s", plotBaseNames[kPlotNonPrompt].Data(), namenonPromptSyst[j+                  0].Data())); histo_NonPromtUnc[j+		    0]->SetDirectory(0);
      histo_NonPromtUnc[j+totalNumberFakeSyst] = (TH1D*)histo_InputNonPromtUnc[j]->Clone(Form("histo_%s_%s", plotBaseNames[kPlotNonPrompt].Data(), namenonPromptSyst[j+totalNumberFakeSyst].Data())); histo_NonPromtUnc[j+totalNumberFakeSyst]->SetDirectory(0);
    }
    delete inputFile;

    for(int j=0; j<totalNumberFakeSyst; j++){
      for(int nb=1; nb<=histo_Baseline[kPlotNonPrompt]->GetNbinsX(); nb++){
        if(histo_Baseline[kPlotNonPrompt]->GetBinContent(nb) > 0) {
          systValue = histo_NonPromtUnc[j+0]->GetBinContent(nb) / histo_Baseline[kPlotNonPrompt]->GetBinContent(nb);
          if     (systValue > 1.15) systValue = 1.15;
          else if(systValue < 0.85) systValue = 0.85;
          histo_NonPromtUnc[j+0]->SetBinContent(nb,histo_Baseline[kPlotNonPrompt]->GetBinContent(nb)*systValue);
          printf("fake(%d,%d) = %.3f\n",j,nb,systValue);
          if(systValue > 0) histo_NonPromtUnc[j+totalNumberFakeSyst]->SetBinContent(nb,histo_Baseline[kPlotNonPrompt]->GetBinContent(nb)/systValue);
        }
      }
    }
  }
  // End Nonprompt study

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
  if(anaSel.Contains("wzAnalysis")) for(int j=0; j<nNonPromptSyst; j++) histo_NonPromtUnc[j]->Write();
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
    if     ((ic != kPlotWZ &&
             ic != kPlotZZ) || srAna == 0
            ) newcardShape << Form("%d  ", ic);
    else if(ic == kPlotWZ) newcardShape << Form("%d  ", -1);
    else if(ic == kPlotZZ) newcardShape << Form("%d  ", -2);
  }
  newcardShape << Form("\n");

  newcardShape << Form("rate  ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    newcardShape << Form("%f  ", histo_Baseline[ic]->GetSumOfWeights());
  }
  newcardShape << Form("\n");

  if(anaSel.Contains("wzAnalysis")){
    bool isTraditionalSyst = false;
    if(isTraditionalSyst == true){
      newcardShape << Form("CMS_SMP24001WZ_fake_m      lnN ");
      for (int ic=0; ic<nPlotCategories; ic++){
        if(!histo_Baseline[ic]) continue;
        if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
        if(ic == kPlotNonPrompt) newcardShape << Form("%6.3f ",1.15);
        else                     newcardShape << Form("- "); 
      }
      newcardShape << Form("\n");

      newcardShape << Form("CMS_SMP24001WZ_fake_e lnN ");
      for (int ic=0; ic<nPlotCategories; ic++){
        if(!histo_Baseline[ic]) continue;
        if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
        if(ic == kPlotNonPrompt) newcardShape << Form("%6.3f ",1.15);
        else                     newcardShape << Form("- ");
      }
      newcardShape << Form("\n");
    } // isTraditionalSyst == true
    else {
      newcardShape << Form("CMS_SMP24001WZ_fake_m0 shape ");
      for (int ic=0; ic<nPlotCategories; ic++){
        if(!histo_Baseline[ic]) continue;
        if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
        if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
        else                     newcardShape << Form("- "); 
      }
      newcardShape << Form("\n");

      newcardShape << Form("CMS_SMP24001WZ_fake_m1 shape ");
      for (int ic=0; ic<nPlotCategories; ic++){
        if(!histo_Baseline[ic]) continue;
        if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
        if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
        else                     newcardShape << Form("- "); 
      }
      newcardShape << Form("\n");

      newcardShape << Form("CMS_SMP24001WZ_fake_m2 shape ");
      for (int ic=0; ic<nPlotCategories; ic++){
        if(!histo_Baseline[ic]) continue;
        if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
        if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
        else                     newcardShape << Form("- "); 
      }
      newcardShape << Form("\n");

      newcardShape << Form("CMS_SMP24001WZ_fake_e0 shape ");
      for (int ic=0; ic<nPlotCategories; ic++){
        if(!histo_Baseline[ic]) continue;
        if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
        if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
        else                     newcardShape << Form("- "); 
      }
      newcardShape << Form("\n");

      newcardShape << Form("CMS_SMP24001WZ_fake_e1 shape ");
      for (int ic=0; ic<nPlotCategories; ic++){
        if(!histo_Baseline[ic]) continue;
        if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
        if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
        else                     newcardShape << Form("- "); 
      }
      newcardShape << Form("\n");

      newcardShape << Form("CMS_SMP24001WZ_fake_e2 shape ");
      for (int ic=0; ic<nPlotCategories; ic++){
        if(!histo_Baseline[ic]) continue;
        if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
        if(ic == kPlotNonPrompt) newcardShape << Form("1.0 ");
        else                     newcardShape << Form("- "); 
      }
      newcardShape << Form("\n");
    } // isTraditionalSyst == false
  }

  int yearLumi = year;
  if(year == 20220 || year == 20221) yearLumi = 2022;
  newcardShape << Form("luminosity_%d   lnN     ",yearLumi);
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

  newcardShape << Form("CMS_eff_m_reco shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_eff_m_id shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_eff_m_iso shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  newcardShape << Form("CMS_eff_e_reco shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_eff_e_id shape ");
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
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[2].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[3].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[4].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[5].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[6].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[7].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[8].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[9].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[10].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[11].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[12].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[13].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[14].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[15].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[16].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[17].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[18].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[19].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[20].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[21].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[22].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[23].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[24].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[25].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[26].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_j_%s shape ",jesNames[27].Data());
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if     (ic == kPlotNonPrompt) newcardShape << Form("- ");
    else if(ic == kPlotTT)        newcardShape << Form("- ");
    else if(ic == kPlotTW)        newcardShape << Form("- ");
    else if(ic == kPlotDY)        newcardShape << Form("- ");
    else                          newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_res_j shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_m shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");
 
  newcardShape << Form("CMS_scale_e shape ");
  for (int ic=0; ic<nPlotCategories; ic++){
    if(!histo_Baseline[ic]) continue;
    if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    if(ic == kPlotNonPrompt) newcardShape << Form("- ");
    else                     newcardShape << Form("1.0 ");
  }
  newcardShape << Form("\n");

  if(anaSel.Contains("wzAnalysis")){
    newcardShape << Form("CMS_met_jer shape ");
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("- ");
      else                     newcardShape << Form("1.0 ");
    }
    newcardShape << Form("\n");

    newcardShape << Form("CMS_met_jes shape ");
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("- ");
      else                     newcardShape << Form("1.0 ");
    }
    newcardShape << Form("\n");

    newcardShape << Form("CMS_met_unclustered shape ");
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("- ");
      else                     newcardShape << Form("1.0 ");
    }
    newcardShape << Form("\n");
  }

  for(unsigned ic=0; ic<nPlotCategories; ic++) {
    if(ic== kPlotData || ic == kPlotNonPrompt || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    newcardShape << Form("QCD_scale_%s_ACCEPT shape ",plotBaseNames[ic].Data());
    for(unsigned ic2=0; ic2<nPlotCategories; ic2++) {
      if(ic2 == kPlotData || histo_Baseline[ic2]->GetSumOfWeights() <= 0) continue;
      if(ic==ic2) newcardShape << Form("1.0  ");
      else        newcardShape << Form("-  ");
      }
      newcardShape << Form("\n");
  } 

  for(unsigned ic=0; ic<nPlotCategories; ic++) {
    if(ic== kPlotData || ic == kPlotNonPrompt || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
    newcardShape << Form("PS_%s_ACCEPT shape ",plotBaseNames[ic].Data());
    for(unsigned ic2=0; ic2<nPlotCategories; ic2++) {
      if(ic2 == kPlotData || histo_Baseline[ic2]->GetSumOfWeights() <= 0) continue;
      if(ic==ic2) newcardShape << Form("1.0  ");
      else        newcardShape << Form("-  ");
      }
      newcardShape << Form("\n");
  } 

  for(int npdf=0; npdf<=100; npdf++){
    newcardShape << Form("pdf%d shape ",npdf);
    for (int ic=0; ic<nPlotCategories; ic++){
      if(!histo_Baseline[ic]) continue;
      if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
      if(ic == kPlotNonPrompt) newcardShape << Form("- ");
      else                     newcardShape << Form("1.0 ");
    }
    newcardShape << Form("\n");
  }

  if(srAna == 0){
    newcardShape << Form("CMS_ww_wznorm  rateParam * %s 1 [0.1,4.9]\n",plotBaseNames[kPlotWZ].Data());
    newcardShape << Form("CMS_ww_zznorm  rateParam * %s 1 [0.1,4.9]\n",plotBaseNames[kPlotZZ].Data());
  }

  newcardShape << Form("ch%d autoMCStats 0\n",fidAna);

  newcardShape.close();

}
