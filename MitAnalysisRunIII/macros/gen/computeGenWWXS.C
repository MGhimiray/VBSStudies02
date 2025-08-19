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

void computeGenWWXS(TString input = "", int selectType = 0, TString output = "output.root"){

  const int number_unc_PS       = 4;
  const int number_unc_QCDScale = 6;
  const int number_unc_PDF      = 101;

  int startF=20; // WW fiducial
  if     (selectType == 1) startF=140; // No requirements
  else if(selectType == 2) startF=260; // mZ requirement
  else if(selectType == 3) startF=380; // mZ + 3l requirements

  TH1D *histo_Baseline;
  TH1D *histo_PS[number_unc_PS];
  TH1D *histo_QCDScale[number_unc_QCDScale];
  TH1D *histo_PDF[number_unc_PDF];
  TH1D *histo_PS_unc;
  TH1D *histo_QCDScale_unc;
  TH1D *histo_PDF_unc;

  TFile *_fileGenWW = TFile::Open(Form("%s",input.Data()));
  histo_Baseline = (TH1D*)_fileGenWW->Get(Form("histo_%d_0",startF+0));
  for(int i=0; i<number_unc_PS; i++)       histo_PS[i]       = (TH1D*)_fileGenWW->Get(Form("histo_%d_0",startF+1+i));
  for(int i=0; i<number_unc_QCDScale; i++) histo_QCDScale[i] = (TH1D*)_fileGenWW->Get(Form("histo_%d_0",startF+1+number_unc_PS+i));
  for(int i=0; i<number_unc_PDF; i++)      histo_PDF[i]      = (TH1D*)_fileGenWW->Get(Form("histo_%d_0",startF+1+number_unc_PS+number_unc_QCDScale+i));

  histo_PS_unc       = (TH1D*)histo_Baseline->Clone();
  histo_QCDScale_unc = (TH1D*)histo_Baseline->Clone();
  histo_PDF_unc      = (TH1D*)histo_Baseline->Clone();
  histo_Baseline    ->SetNameTitle("hDWWNJETS"    ,"hDWWNJETS"    );
  histo_PS_unc      ->SetNameTitle("hDWWNJETS_PS" ,"hDWWNJETS_PS" );
  histo_QCDScale_unc->SetNameTitle("hDWWNJETS_QCD","hDWWNJETS_QCD");
  histo_PDF_unc     ->SetNameTitle("hDWWNJETS_PDF","hDWWNJETS_PDF");


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
    printf("bin(%d): %6.1f / %.3f %.3f %.3f / %.3f %6.1f\n",nb,histo_Baseline->GetBinContent(nb),systPS-1,systQCDScale-1,systPDF-1,tot,histo_Baseline->GetBinContent(nb)*tot);
  }
  double tot = sqrt((histo_PS_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1)*(histo_PS_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1)+(histo_QCDScale_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1)*(histo_QCDScale_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1)+(histo_PDF_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1)*(histo_PDF_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1));
  printf("bin(%d): %6.1f / %.3f %.3f %.3f / %.3f %6.1f\n",0,histo_Baseline->GetSumOfWeights(),histo_PS_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1,histo_QCDScale_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1,histo_PDF_unc->GetSumOfWeights()/histo_Baseline->GetSumOfWeights()-1,tot,histo_Baseline->GetSumOfWeights()*tot);
  TFile *outputFile = TFile::Open(Form("%s",output.Data()),"recreate");
  outputFile->cd();
  histo_Baseline    ->Write();
  histo_PS_unc      ->Write();
  histo_QCDScale_unc->Write();
  histo_PDF_unc     ->Write();
  outputFile->Close();
}
