#include "TROOT.h"
#include "TInterpreter.h"
#include "TFile.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "TStyle.h"
#include "TPad.h"
#include "Math/QuantFuncMathCore.h"
#include "TMath.h"
#include "TGraphAsymmErrors.h"
#include "TSystem.h"
#include "TLegend.h"
#include <iostream>

void computeGenVBSVVXS(TString input = "/mnt/home/mghimiray/VBSStudies/Outputs_VBS/GenXs/fillhisto_genAnalysis_sample192_year2027_job-1.root", int selectType = 6){

  const int nBin4 = 4; const int nBin2 = 2;
  const Float_t xbinsWZMJJ       [nBin4+1] = {500, 900, 1300, 1900, 2500};
  const Float_t xbinsWWMJJ       [nBin4+1] = {500, 900, 1300, 1900, 2500};
  const Float_t xbinsWWMLL       [nBin4+1] = {20, 80, 140, 220, 300};
  const Float_t xbinsWWNJET      [nBin2+1] = {1.5, 2.5, 3.5};
  const Float_t xbinsWWDELTAETAJJ[nBin4+1] = {2.5,3.6,4.5,5.5,8.0};
  const Float_t xbinsWWDELTAPHIJJ[nBin4+1] = {0.0, 1.8, 2.5, 2.9, TMath::Pi()};

  const int number_unc_PS       = 4;
  const int number_unc_QCDScale = 6;
  const int number_unc_PDF      = 101;

  int startF=0; TString nameH = "";
  if     (selectType == 0) {startF=386;  nameH = "hDEWKWZMJJ";}
  else if(selectType == 1) {startF=530;  nameH = "hDEWKWWMJJ";}
  else if(selectType == 2) {startF=650;  nameH = "hDEWKWWMLL";}
  else if(selectType == 3) {startF=770;  nameH = "hDEWKWWNJET";}
  else if(selectType == 4) {startF=890;  nameH = "hDEWKWWDELTAETAJJ";}
  else if(selectType == 5) {startF=1010; nameH = "hDEWKWWDELTAPHIJJ";}
  else if(selectType == 6) {startF=386;  nameH = "hDQCDWZMJJ";}

  TH1D *histo_Aux[1+number_unc_PS+number_unc_QCDScale+number_unc_PDF];
  TH1D *histo_Baseline;
  TH1D *histo_PS[number_unc_PS];
  TH1D *histo_QCDScale[number_unc_QCDScale];
  TH1D *histo_PDF[number_unc_PDF];
  TH1D *histo_PS_unc;
  TH1D *histo_QCDScale_unc;
  TH1D *histo_PDF_unc;

  if     (selectType == 0) {histo_Baseline = new TH1D(Form("%s",nameH.Data()), Form("%s",nameH.Data()), nBin4, xbinsWZMJJ       );}
  else if(selectType == 1) {histo_Baseline = new TH1D(Form("%s",nameH.Data()), Form("%s",nameH.Data()), nBin4, xbinsWWMJJ       );}
  else if(selectType == 2) {histo_Baseline = new TH1D(Form("%s",nameH.Data()), Form("%s",nameH.Data()), nBin4, xbinsWWMLL       );}
  else if(selectType == 3) {histo_Baseline = new TH1D(Form("%s",nameH.Data()), Form("%s",nameH.Data()), nBin2, xbinsWWNJET      );}
  else if(selectType == 4) {histo_Baseline = new TH1D(Form("%s",nameH.Data()), Form("%s",nameH.Data()), nBin4, xbinsWWDELTAETAJJ);}
  else if(selectType == 5) {histo_Baseline = new TH1D(Form("%s",nameH.Data()), Form("%s",nameH.Data()), nBin4, xbinsWWDELTAPHIJJ);}
  else if(selectType == 6) {histo_Baseline = new TH1D(Form("%s",nameH.Data()), Form("%s",nameH.Data()), nBin4, xbinsWZMJJ       );}

  for(int i=0; i<number_unc_PS; i++)       histo_PS[i]       = (TH1D*)histo_Baseline->Clone();
  for(int i=0; i<number_unc_QCDScale; i++) histo_QCDScale[i] = (TH1D*)histo_Baseline->Clone();
  for(int i=0; i<number_unc_PDF; i++)      histo_PDF[i]      = (TH1D*)histo_Baseline->Clone();

  TFile *_fileGenWW = TFile::Open(Form("%s",input.Data()));
  for(int i=0; i<1+number_unc_PS+number_unc_QCDScale+number_unc_PDF; i++) histo_Aux[i] = (TH1D*)_fileGenWW->Get(Form("histo_%d_0",startF+i));
  
  for(int i=0; i<1+number_unc_PS+number_unc_QCDScale+number_unc_PDF; i++){
  histo_Aux[i] = (TH1D*)_fileGenWW->Get(Form("histo_%d_0",startF+i));
  if(!histo_Aux[i]){
    printf("ERROR: missing histo_%d_0 (aux index %d) in %s\n", startF+i, i, input.Data());
    return;
  }
}

  for(int nb=1; nb<=histo_Baseline->GetNbinsX(); nb++){
    histo_Baseline->SetBinContent(nb, histo_Aux[0]->GetBinContent(nb)); histo_Baseline->SetBinError(nb, histo_Aux[0]->GetBinError(nb)); 
    for(int i=0; i<number_unc_PS; i++)       {histo_PS[i]      ->SetBinContent(nb, histo_Aux[1+i]                                  ->GetBinContent(nb));}
    for(int i=0; i<number_unc_QCDScale; i++) {histo_QCDScale[i]->SetBinContent(nb, histo_Aux[1+number_unc_PS+i]                    ->GetBinContent(nb));}
    for(int i=0; i<number_unc_PDF; i++)      {histo_PDF[i]     ->SetBinContent(nb, histo_Aux[1+number_unc_PS+number_unc_QCDScale+i]->GetBinContent(nb));}
  }

  histo_PS_unc       = (TH1D*)histo_Baseline->Clone();
  histo_QCDScale_unc = (TH1D*)histo_Baseline->Clone();
  histo_PDF_unc      = (TH1D*)histo_Baseline->Clone();
  histo_Baseline    ->SetNameTitle(Form("%s"    ,nameH.Data()), Form("%s"    ,nameH.Data()));
  histo_PS_unc      ->SetNameTitle(Form("%s_PS" ,nameH.Data()), Form("%s_PS" ,nameH.Data()));
  histo_QCDScale_unc->SetNameTitle(Form("%s_QCD",nameH.Data()), Form("%s_QCD",nameH.Data()));
  histo_PDF_unc     ->SetNameTitle(Form("%s_PDF",nameH.Data()), Form("%s_PDF",nameH.Data()));

  for(int nb=1; nb<=histo_Baseline->GetNbinsX(); nb++){

    // compute PS uncertainties bin-by-bin
    double diffPS[number_unc_PS] = {
     TMath::Abs(histo_PS[0]->GetBinContent(nb)-histo_Baseline->GetBinContent(nb)),
     TMath::Abs(histo_PS[1]->GetBinContent(nb)-histo_Baseline->GetBinContent(nb)),
     TMath::Abs(histo_PS[2]->GetBinContent(nb)-histo_Baseline->GetBinContent(nb)),
     TMath::Abs(histo_PS[3]->GetBinContent(nb)-histo_Baseline->GetBinContent(nb))};

    double systPS = diffPS[0];
    for(int nps=1; nps<number_unc_PS; nps++) {
      if(diffPS[nps] > systPS) systPS = diffPS[nps];
    }

    if(histo_Baseline->GetBinContent(nb) > 0) 
      systPS = 1.0+systPS/histo_Baseline->GetBinContent(nb);
    else systPS = 1;

    histo_PS_unc->SetBinContent(nb, histo_Baseline->GetBinContent(nb)*systPS);

    // compute QCD scale uncertainties bin-by-bin
    double diffQCDScale[number_unc_QCDScale] = {
     TMath::Abs(histo_QCDScale[0]->GetBinContent(nb)-histo_Baseline->GetBinContent(nb)),
     TMath::Abs(histo_QCDScale[1]->GetBinContent(nb)-histo_Baseline->GetBinContent(nb)),
     TMath::Abs(histo_QCDScale[2]->GetBinContent(nb)-histo_Baseline->GetBinContent(nb)),
     TMath::Abs(histo_QCDScale[3]->GetBinContent(nb)-histo_Baseline->GetBinContent(nb)),
     TMath::Abs(histo_QCDScale[4]->GetBinContent(nb)-histo_Baseline->GetBinContent(nb)),
     TMath::Abs(histo_QCDScale[5]->GetBinContent(nb)-histo_Baseline->GetBinContent(nb))};

    double systQCDScale = diffQCDScale[0];
    for(int nqcd=1; nqcd<number_unc_QCDScale; nqcd++) {
      if(diffQCDScale[nqcd] > systQCDScale) systQCDScale = diffQCDScale[nqcd];
    }

    if(histo_Baseline->GetBinContent(nb) > 0) 
      systQCDScale = 1.0+systQCDScale/histo_Baseline->GetBinContent(nb);
    else systQCDScale = 1;

    histo_QCDScale_unc->SetBinContent(nb, histo_Baseline->GetBinContent(nb)*systQCDScale);

    // compute PDF uncertainties bin-by-bin
    double systPDF = 0.0;
    for(int i=0; i<number_unc_PDF; i++) {
      double diff = TMath::Abs(histo_PDF[i]->GetBinContent(nb)-histo_Baseline->GetBinContent(nb));
      systPDF = systPDF + TMath::Power(diff,2);
      //printf("%d %d %f %f\n",nb,i,diff,sqrt(systPDF));
    }
    systPDF = sqrt(systPDF);

    if(histo_Baseline->GetBinContent(nb) > 0) 
        systPDF = 1.0+systPDF/histo_Baseline->GetBinContent(nb);
    else systPDF = 1;

    histo_PDF_unc->SetBinContent(nb, histo_Baseline->GetBinContent(nb)*systPDF);

    double tot = sqrt((systPS-1)*(systPS-1)+(systQCDScale-1)*(systQCDScale-1)+(systPDF-1)*(systPDF-1));
    printf("bin(%d): %6.2f / %.3f %.3f %.3f / %.3f %6.2f\n",nb,histo_Baseline->GetBinContent(nb),systPS-1,systQCDScale-1,systPDF-1,tot,histo_Baseline->GetBinContent(nb)*tot);
  }

  double tot = sqrt((histo_PS_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1)*(histo_PS_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1)+(histo_QCDScale_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1)*(histo_QCDScale_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1)+(histo_PDF_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1)*(histo_PDF_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1));
  printf("bin(%d): %6.2f / %.3f %.3f %.3f / %.3f %6.2f\n",0,histo_Baseline->GetSumOfWeights(),histo_PS_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1,histo_QCDScale_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1,histo_PDF_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1,tot,histo_Baseline->GetSumOfWeights()*tot);
  TFile *outputFile = TFile::Open(Form("xsgen_vbs_%s.root",nameH.Data()),"recreate");
  outputFile->cd();
  histo_Baseline    ->Write();
  histo_PS_unc      ->Write();
  histo_QCDScale_unc->Write();
  histo_PDF_unc     ->Write();
  outputFile->Close();
}
