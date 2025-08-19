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

void computeGenPtWWUnc(TString input = "", const int whichAna = 0){

  // whichAna = 0 (gen), 1 (inc), 2 (0j), 3 (1j), 4 (2j), 5 (3j)

  TString anaName[6] = {"gen", "inc", "0j", "1j", "2j", "3j"};

  const int number_unc = 5;
  int startF=134+6*whichAna;
  TH1D *histo_Baseline;
  TH1D *histo_PTWWUnc[number_unc];

  TFile *_fileGenWW = TFile::Open(Form("%s",input.Data()));
  histo_Baseline = (TH1D*)_fileGenWW->Get(Form("histo_%d_0",startF+0));
  for(int i=0; i<number_unc; i++) {
    histo_PTWWUnc[i] = (TH1D*)_fileGenWW->Get(Form("histo_%d_0",startF+1+i));
  }
  double scaleFactor = histo_Baseline->GetSumOfWeights()/histo_PTWWUnc[0]->GetSumOfWeights();

  printf("===> Overall yields, analysis: %s\n",anaName[whichAna].Data());
  printf("%5.1f ",histo_Baseline->GetSumOfWeights());
  for(int i=0; i<number_unc; i++) {
    printf("| %6.1f ",histo_PTWWUnc[i]->GetSumOfWeights());
    histo_PTWWUnc[i]->Scale(scaleFactor);
    printf(" %6.1f ",histo_PTWWUnc[i]->GetSumOfWeights());
  }
  printf("\n");

  printf("===> Overall uncertainties\n");
  for(int nb=1; nb<=histo_Baseline->GetNbinsX(); nb++){
    printf("bin(%d) ",nb);
    for(int i=0; i<number_unc; i++) {
      printf("%.3f ",histo_PTWWUnc[i]->GetBinContent(nb)/histo_Baseline->GetBinContent(nb));
    }
    printf("\n");
  }
  printf("===> Symmetric uncertainties\n");
  for(int nb=1; nb<=histo_Baseline->GetNbinsX(); nb++){
    double unc[6] = {
    abs(histo_PTWWUnc[1]->GetBinContent(nb)-histo_PTWWUnc[2]->GetBinContent(nb))/2.,
    abs(histo_PTWWUnc[3]->GetBinContent(nb)-histo_PTWWUnc[4]->GetBinContent(nb))/2.,
    0.,
    abs(histo_PTWWUnc[1]->GetBinContent(nb)-histo_PTWWUnc[2]->GetBinContent(nb))/2.,
    abs(histo_PTWWUnc[3]->GetBinContent(nb)-histo_PTWWUnc[4]->GetBinContent(nb))/2.,
    0.
    };
    unc[2] = sqrt(unc[0]*unc[0]+unc[1]*unc[1]);
    unc[5] = sqrt(unc[3]*unc[3]+unc[4]*unc[4]);
    printf("bin(%d) ",nb);
    printf("%.3f %.3f -> %.3f | %.3f %.3f -> %.3f",
    unc[0]/histo_PTWWUnc[0]->GetBinContent(nb),
    unc[1]/histo_PTWWUnc[0]->GetBinContent(nb),
    unc[2]/histo_PTWWUnc[0]->GetBinContent(nb),
    unc[3]/histo_Baseline->GetBinContent(nb),
    unc[4]/histo_Baseline->GetBinContent(nb),
    unc[5]/histo_Baseline->GetBinContent(nb));
    printf("\n");
  }

  for(int i=0; i<number_unc; i++) {
    histo_PTWWUnc[i]->Scale(histo_Baseline->GetSumOfWeights()/histo_PTWWUnc[i]->GetSumOfWeights());
  }
  printf("===> Overall rescaled yields, analysis: %s\n",anaName[whichAna].Data());
  printf("%5.1f ",histo_Baseline->GetSumOfWeights());
  for(int i=0; i<number_unc; i++) {
    printf("| %6.1f ",histo_PTWWUnc[i]->GetSumOfWeights());
  }
  printf("\n");

  printf("===> Relative uncertainties\n");
  for(int nb=1; nb<=histo_Baseline->GetNbinsX(); nb++){
    printf("bin(%d) ",nb);
    for(int i=0; i<number_unc; i++) {
      printf("%.3f ",histo_PTWWUnc[i]->GetBinContent(nb)/histo_Baseline->GetBinContent(nb));
    }
    printf("\n");
  }
  printf("===> Relative symmetric uncertainties\n");
  for(int nb=1; nb<=histo_Baseline->GetNbinsX(); nb++){
    double unc[6] = {
    abs(histo_PTWWUnc[1]->GetBinContent(nb)-histo_PTWWUnc[2]->GetBinContent(nb))/2.,
    abs(histo_PTWWUnc[3]->GetBinContent(nb)-histo_PTWWUnc[4]->GetBinContent(nb))/2.,
    0.,
    abs(histo_PTWWUnc[1]->GetBinContent(nb)-histo_PTWWUnc[2]->GetBinContent(nb))/2.,
    abs(histo_PTWWUnc[3]->GetBinContent(nb)-histo_PTWWUnc[4]->GetBinContent(nb))/2.,
    0.
    };
    unc[2] = sqrt(unc[0]*unc[0]+unc[1]*unc[1]);
    unc[5] = sqrt(unc[3]*unc[3]+unc[4]*unc[4]);
    printf("bin(%d) ",nb);
    printf("%.3f %.3f -> %.3f | %.3f %.3f -> %.3f",
    unc[0]/histo_PTWWUnc[0]->GetBinContent(nb),
    unc[1]/histo_PTWWUnc[0]->GetBinContent(nb),
    unc[2]/histo_PTWWUnc[0]->GetBinContent(nb),
    unc[3]/histo_Baseline->GetBinContent(nb),
    unc[4]/histo_Baseline->GetBinContent(nb),
    unc[5]/histo_Baseline->GetBinContent(nb));
    printf("\n");
  }
}
