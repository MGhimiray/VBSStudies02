#include "TROOT.h"
#include "Math/ProbFuncMathCore.h"
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
#include "CMS_lumi.C"
#include "TRandom.h"
#include "common.h"
#include "StandardPlot.C"
#include "GoodStyle.C"

double scaling[8] = {1,1,1,1,1,1,1,1};
//double scaling[8] = {73.496/69.913,1.2,168.114/157.695,404.402/361.347,2.583/2.537,1,1,1}; // EM/Zjets/WZ/ZZ/VVV
//double scaling[8] = {0.94,1.04,1.04,1.01,1.00,1.02,1.01,1.05}; // EWK/QCD/VV/VVV/WS/WG/DPS/Wjets

bool isLogSpecial = false;
bool isLogX = false;
bool printRatios = false;
bool printYieldsBinByBin = false;

void eraselabel(TPad *p,Double_t h){
  p->cd();
  TPad *pe = new TPad("pe","pe",0.02,0,p->GetLeftMargin()-0.007,h);
  pe->Draw();
  pe->SetFillColor(p->GetFillColor()); 
  pe->SetBorderMode(0);
}

void atributes(TH1D *histo, TString xtitle = "", TString ytitle = "Fraction", TString units = ""){

  histo->SetTitle("");
  //histo->SetMarkerStyle(20);
  //histo->SetMarkerSize(0.8);
  //histo->SetLineWidth(4);
  if(strcmp(units.Data(),"")==0){
    histo->GetXaxis()->SetTitle(xtitle.Data());
  } else {
    units = units.ReplaceAll("BIN","");
    if(strcmp(units.Data(),"")==0){
      histo->GetXaxis()->SetTitle(Form("%s",xtitle.Data()));
    }
    else {
      histo->GetXaxis()->SetTitle(Form("%s [%s]",xtitle.Data(),units.Data()));
    }
  }
  histo->GetXaxis()->SetLabelFont  (   42);
  histo->GetXaxis()->SetLabelOffset(0.015);
  histo->GetXaxis()->SetLabelSize  (0.135);
  histo->GetXaxis()->SetNdivisions (  505);
  histo->GetXaxis()->SetTitleFont  (   42);
  histo->GetXaxis()->SetTitleOffset( 1.00);
  histo->GetXaxis()->SetTitleSize  (0.140);
  //histo->GetXaxis()->SetTickLength (0.07 );

  histo->GetYaxis()->SetTitle(ytitle.Data());
  histo->GetYaxis()->SetLabelFont  (   42);
  histo->GetYaxis()->SetLabelOffset(0.015);
  histo->GetYaxis()->SetLabelSize  (0.150);
  histo->GetYaxis()->SetNdivisions (  505);
  histo->GetYaxis()->SetTitleFont  (   42);
  histo->GetYaxis()->SetTitleOffset( 0.45);
  histo->GetYaxis()->SetTitleSize  (0.140);
  //histo->GetYaxis()->SetTickLength (0.03 );

  histo->SetLineColor  (kBlack);
  histo->SetMarkerSize(0.8);
  histo->SetMarkerStyle(kFullCircle);
}

void finalPlot(int nsel = 0, int ReBin = 1, TString XTitle = "N_{jets}", TString units = "", TString plotName = "histoWW_56.root", TString outputName = "njets",
                bool isLogY = false, int year = 2017, TString higgsLabel = "", double lumi = 1.0, bool isBlind = false, TString extraLabel = "",
		bool show2D = true, bool applyScaling = false,
		TString mlfitResult = "", TString channelName = "", bool applyBBBBSF = false,
		TString plotExtraName = "", TString higgs2Label = "", bool applySmoothing = false) {

  if(isBlind) show2D = false;

  bool makeRootFile = false; if(!plotName.Contains("2019") && plotName.Contains("VBFG")) makeRootFile = true;
  if(units.Contains("ROOT")) {makeRootFile = true; units = units.ReplaceAll("ROOT","");}
  bool isSignalStack = false;
  if(units.Contains("Stack")) {isSignalStack = true; units = units.ReplaceAll("Stack","");}
  bool isRemoveBSM = false;
  if(units.Contains("NoBSM")) {isRemoveBSM = true; units = units.ReplaceAll("NoBSM","");}
  bool doApplyBinWidth = false;
  if(units.Contains("BinWidth")) {doApplyBinWidth = true; units = units.ReplaceAll("BinWidth","");}

  //gInterpreter->ExecuteMacro("MitAnalysisRunII/panda/makePlots/GoodStyle.C");
  GoodStyle();
  //gROOT->LoadMacro("StandardPlot.C");
  gStyle->SetOptStat(0);
  TGaxis::SetMaxDigits(3); 
  TGaxis::SetExponentOffset(-0.00, 0.00, "x");
  TGaxis::SetExponentOffset(-0.08, 0.01, "y");

  TH1F* _hist[nPlotCategories];
  TH1F* _histo_total;
  StandardPlot myPlot;
  myPlot.setDoApplyBinWidth(doApplyBinWidth);
  myPlot.setLumi(lumi);
  myPlot.setLabel(XTitle);
  myPlot.addLabel(extraLabel.Data());
  myPlot.setHiggsLabel(higgsLabel.Data());
  myPlot.setHiggs2Label(higgs2Label.Data());
  myPlot.setUnits(units);

  TFile* file = new TFile(plotName, "read");  if(!file) {printf("File %s does not exist\n",plotName.Data()); return;}

  double totalSystUnc = 0.0;
  double totalStatUnc = 0.0;
  double SF_yield[nPlotCategories]; 
  double SF_yield_unc[nPlotCategories];
  TFile *mlfit=0;
  if(mlfitResult!="") {
    mlfit=TFile::Open(mlfitResult); assert(mlfit);
  }
  TH1F* hData = 0;
  TH1F* hBck = 0;
  for(int ic=0; ic<nPlotCategories; ic++){
    _hist[ic] = (TH1F*)file->Get(Form("histo%d",ic));
    _histo_total = (TH1F*)file->Get(Form("histo_total"));
  }

  int isVBS[2] = {0, 0};
  if     (plotName.Contains("fiducial6"))                                    isVBS[0] = 2;
  else if(plotName.Contains("ww_output"))                                    isVBS[0] = 3;
  else if(_hist[kPlotEWKSSWW] && _hist[kPlotEWKSSWW]->GetSumOfWeights() > 0) isVBS[0] = 1;
  else if(_hist[kPlotSignal0] && _hist[kPlotSignal0]->GetSumOfWeights() > 0) isVBS[0] = 1;
  else if(_hist[kPlotSignal1] && _hist[kPlotSignal1]->GetSumOfWeights() > 0) isVBS[0] = 1;
  else if(_hist[kPlotSignal2] && _hist[kPlotSignal2]->GetSumOfWeights() > 0) isVBS[0] = 1;
  else if(_hist[kPlotSignal3] && _hist[kPlotSignal3]->GetSumOfWeights() > 0) isVBS[0] = 1;
  if(_hist[kPlotEWKWZ] && _hist[kPlotEWKWZ]  ->GetSumOfWeights() > 0) isVBS[1] = 1;

  for(int ic=0; ic<nPlotCategories; ic++){
    if(!_hist[ic]) continue;
    //printf("DEBUG0 %d %d %d\n",ic,isVBS[0],isVBS[1]);
    //for(int i=1; i<=_hist[ic]->GetNbinsX(); i++) if(_hist[ic]->GetSumOfWeights() > 0) printf("%10s(%2d): %.1f\n",plotBaseNames[ic].Data(),i,_hist[ic]->GetBinContent(i));
    // begin btaging study
    //_hist[ic]->SetBinContent(1,0);
    //if(ic != kPlotNonPrompt && ic != kPlotTVX && ic != kPlotWS && ic != kPlotData) {hData->Add(_hist[ic],-1);_hist[ic]->Scale(0);}
    // end btaging study
    for(int i=1; i<=_hist[ic]->GetNbinsX(); i++) if(_hist[ic]->GetBinContent(i)<0) {_hist[ic]->SetBinContent(i,0);_hist[ic]->SetBinError(i,0);}
    if(ic == kPlotData) {
      //for(int i=1; i<=_hist[ic]->GetNbinsX(); i++){
      //  if(i>20)_hist[ic]->SetBinContent(i,0);
      //}
      hData = (TH1F*)_hist[ic]->Clone();
      hBck  = (TH1F*)_hist[ic]->Clone("hBck"); hBck->Scale(0);
    }
    else if(applySmoothing && _hist[ic]->GetSumOfWeights() > 0 && ic != kPlotBSM && ic != kPlotVG &&
      ic != kPlotSignal0 && ic != kPlotSignal1 &&
      ic != kPlotSignal2 && ic != kPlotSignal3) {double scale = _hist[ic]->GetSumOfWeights(); _hist[ic]->Smooth(); if(_hist[ic]->GetSumOfWeights() > 0) _hist[ic]->Scale(scale/_hist[ic]->GetSumOfWeights());}

    if(isBlind == true && ic == kPlotData) continue;

    if(!(mlfitResult=="" || ic == kPlotData || ic == kPlotBSM || (ic == kPlotSignal1 && isVBS[0] == 2))) {
      SF_yield[ic]     = 1.0;
      SF_yield_unc[ic] = 0.0;
      if     ((TH1F*)mlfit->Get(Form("shapes_prefit/%s/%s",channelName.Data(),plotBaseNames[ic].Data()))) {
        double sum[3] = {0, 0, 0};
        for(int i=1; i<=((TH1F*)mlfit->Get(Form("shapes_fit_s/%s/%s",channelName.Data(),plotBaseNames[ic].Data())))->GetNbinsX(); i++){
          //sum[0] = sum[0] + ((TH1F*)mlfit->Get(Form("shapes_fit_s/%s/%s",channelName.Data(),plotBaseNames[ic].Data()))) ->GetBinContent(i);
	  //sum[1] = sum[1] + ((TH1F*)mlfit->Get(Form("shapes_prefit/%s/%s",channelName.Data(),plotBaseNames[ic].Data())))->GetBinContent(i);
	  sum[2] = sum[2] + ((TH1F*)mlfit->Get(Form("shapes_fit_s/%s/%s",channelName.Data(),plotBaseNames[ic].Data())))->GetBinError(i);
	  if(((TH1F*)mlfit->Get(Form("shapes_fit_s/%s/%s",channelName.Data(),plotBaseNames[ic].Data())))->GetNbinsX() ==_hist[ic]->GetNbinsX() && 
	     applyBBBBSF == true){
	     _hist[ic]->SetBinContent(i,((TH1F*)mlfit->Get(Form("shapes_fit_s/%s/%s",channelName.Data(),plotBaseNames[ic].Data()))) ->GetBinContent(i));
             _hist[ic]->SetBinError(i,((TH1F*)mlfit->Get(Form("shapes_fit_s/%s/%s",channelName.Data(),plotBaseNames[ic].Data())))->GetBinError(i));
	  }
        }
        sum[0] = ((TH1F*)mlfit->Get(Form("shapes_fit_s/%s/%s",channelName.Data(),plotBaseNames[ic].Data()))) ->GetSumOfWeights();
	sum[1] = ((TH1F*)mlfit->Get(Form("shapes_prefit/%s/%s",channelName.Data(),plotBaseNames[ic].Data())))->GetSumOfWeights();
	if(((TH1F*)mlfit->Get(Form("shapes_fit_s/%s/%s",channelName.Data(),plotBaseNames[ic].Data())))->GetNbinsX() ==_hist[ic]->GetNbinsX() && 
	   applyBBBBSF == true){
          // do nothing
	}
	else {   
          SF_yield[ic]     = sum[0] / sum[1];
          SF_yield_unc[ic] = sum[2] / sum[0];
        }
	printf("POST FIT SFs: SF[%s] = %.3f +/- %.3f | %.3f\n",plotBaseNames[ic].Data(),SF_yield[ic],SF_yield_unc[ic],
	       ((TH1F*)mlfit->Get(Form("shapes_fit_s/%s/%s",channelName.Data(),plotBaseNames[ic].Data()))) ->GetSumOfWeights()/
	       ((TH1F*)mlfit->Get(Form("shapes_prefit/%s/%s",channelName.Data(),plotBaseNames[ic].Data())))->GetSumOfWeights());
      }
      _hist[ic]->Scale(SF_yield[ic]);
      totalSystUnc = totalSystUnc + TMath::Power(_hist[ic]->GetSumOfWeights()*SF_yield_unc[ic],2);
      for(int i=1; i<=_hist[ic]->GetNbinsX(); i++){
        double theStat = _hist[ic]->GetBinError(i);
        double theSyst = _hist[ic]->GetBinContent(i)*SF_yield_unc[ic];
        totalStatUnc = totalStatUnc + TMath::Power(theStat,2);
        _hist[ic]->SetBinError(i,TMath::Min(TMath::Sqrt(TMath::Power(theStat,2)+TMath::Power(theSyst,2)),_hist[ic]->GetBinContent(i)));
      }
    } // mltFit result

    //printf("DEBUG1 %d\n",ic);
    if(ic != kPlotData) _hist[ic]->Scale(lumi);

    if(printYieldsBinByBin && _hist[ic]->GetSumOfWeights() > 0){
      printf("Yields(%s) = %.3f\n",plotBaseNames[ic].Data(),_hist[ic]->GetSumOfWeights());
      for(int i=1; i<=_hist[ic]->GetNbinsX(); i++) printf("%7.3f +/- %.3f\n",_hist[ic]->GetBinContent(i),_hist[ic]->GetBinError(i));
    }

    //printf("DEBUG2 %d\n",ic);
    if     (isRemoveBSM && ic == kPlotBSM) _hist[ic]->Scale(0);

    if(ic == kPlotggWW && _hist[ic]) {_hist[kPlotqqWW]->Add(_hist[ic]);_hist[ic]->Scale(0);}
    if(ic == kPlotTW   && _hist[ic]) {_hist[kPlotTT]  ->Add(_hist[ic]);_hist[ic]->Scale(0);}

    else if(isVBS[0] == 2 && ic == kPlotSignal1)                  {_hist[kPlotBSM]->Add(_hist[ic]);_hist[ic]->Scale(0);}
    else if(isVBS[0] == 1 && ic == kPlotqqWW)                     {_hist[kPlotEWKSSWW]->Add(_hist[ic]); _hist[ic]->Scale(0);}
    else if(isVBS[0] == 1 && ic == kPlotQCDSSWW)                  {_hist[kPlotEWKSSWW]->Add(_hist[ic]); _hist[ic]->Scale(0);}
    else if(isVBS[0] == 1 && ic == kPlotSignal0 && !makeRootFile) {_hist[kPlotEWKSSWW]->Add(_hist[ic]); _hist[ic]->Scale(0);}
    else if(isVBS[0] == 1 && ic == kPlotSignal1 && !makeRootFile) {_hist[kPlotEWKSSWW]->Add(_hist[ic]); _hist[ic]->Scale(0);}
    else if(isVBS[0] == 1 && ic == kPlotSignal2 && !makeRootFile) {_hist[kPlotEWKSSWW]->Add(_hist[ic]); _hist[ic]->Scale(0);}
    else if(isVBS[0] == 1 && ic == kPlotSignal3 && !makeRootFile) {_hist[kPlotEWKSSWW]->Add(_hist[ic]); _hist[ic]->Scale(0);}

    else if(isVBS[1] == 1 && ic == kPlotggWW)    {_hist[kPlotEWKWZ]  ->Add(_hist[ic]); _hist[ic]->Scale(0);}

    else if(isVBS[0] == 3 && ic == kPlotSignal0 && _hist[ic])     {_hist[kPlotqqWW]->Add(_hist[ic]);_hist[ic]->Scale(0);}
    else if(isVBS[0] == 3 && ic == kPlotSignal1 && _hist[ic])     {_hist[kPlotqqWW]->Add(_hist[ic]);_hist[ic]->Scale(0);}
    else if(isVBS[0] == 3 && ic == kPlotSignal2 && _hist[ic])     {_hist[kPlotqqWW]->Add(_hist[ic]);_hist[ic]->Scale(0);}
    else if(isVBS[0] == 3 && ic == kPlotSignal3 && _hist[ic])     {_hist[kPlotqqWW]->Add(_hist[ic]);_hist[ic]->Scale(0);}
    else if(isVBS[0] == 3 && ic == kPlotSignal4 && _hist[ic])     {_hist[kPlotqqWW]->Add(_hist[ic]);_hist[ic]->Scale(0);}
    else if(isVBS[0] == 3 && ic == kPlotSignal5 && _hist[ic])     {_hist[kPlotqqWW]->Add(_hist[ic]);_hist[ic]->Scale(0);}
    //printf("DEBUG3 %d\n",ic);
  }
  
  for(int ic=0; ic<nPlotCategories; ic++){
    if(!_hist[ic]) continue;
    //printf("DEBUG4 %d\n",ic);
    if(ic != kPlotData && ic != kPlotBSM && ic != kPlotSignal0 && ic != kPlotSignal1 && ic != kPlotSignal2 && ic != kPlotSignal3) {
      hBck->Add(_hist[ic]);
      if(mlfitResult==""){
        for(int i=1; i<=_hist[ic]->GetNbinsX(); i++){
          totalStatUnc = totalStatUnc + TMath::Power(_hist[ic]->GetBinError(i),2);
        }
      }
    }
  }

  if(_histo_total){
    for(int i=1; i<=hBck->GetNbinsX(); i++){
      printf("(%2d) %7.1f +/- %5.1f | %7.1f +/- %5.1f\n",i,hBck->GetBinContent(i),hBck->GetBinError(i),_histo_total->GetBinContent(i),_histo_total->GetBinError(i));
      if(hBck->GetBinContent(i) > 0 && abs(hBck->GetBinContent(i)-_histo_total->GetBinContent(i))/hBck->GetBinContent(i) > 0.01) printf("Big difference!\n");
      hBck->SetBinError(i,_histo_total->GetBinError(i));
    }
  }

  if(printYieldsBinByBin && hBck->GetSumOfWeights() > 0){
    printf("Yields(Bck) = %.3f\n",hBck->GetSumOfWeights());
    for(int i=1; i<=hBck->GetNbinsX(); i++) printf("%7.3f +/- %.3f\n",hBck->GetBinContent(i),hBck->GetBinError(i));
  }

  TFile* fileExtra;
  if(plotExtraName != ""){
     fileExtra = new TFile(plotExtraName, "read");
      _hist[kPlotSignal0] = (TH1F*)fileExtra->Get(Form("histo%d",kPlotBSM));
     _hist[kPlotSignal0]->SetNameTitle(Form("histo%d",kPlotSignal0),Form("histo%d",kPlotSignal0));
     for(int i=1; i<=_hist[kPlotSignal0]->GetNbinsX(); i++) if(_hist[kPlotSignal0]->GetBinContent(i)<0) _hist[kPlotSignal0]->SetBinContent(i,0);
     if(isVBS[0] == 2){
       _hist[kPlotSignal1] = (TH1F*)fileExtra->Get(Form("histo%d",kPlotSignal1));
       for(int i=1; i<=_hist[kPlotSignal1]->GetNbinsX(); i++) if(_hist[kPlotSignal1]->GetBinContent(i)<0) _hist[kPlotSignal1]->SetBinContent(i,0);
       _hist[kPlotSignal0]->Add(_hist[kPlotSignal1]);
     }
     myPlot.setMCHist(kPlotSignal0, _hist[kPlotSignal0]);
  }

  if(hBck->GetSumOfWeights() <= 0 || (isBlind == false && hData->GetSumOfWeights() <= 0)) return;
  double scale = hData->GetSumOfWeights()/hBck->GetSumOfWeights();
  double daUnc = 1.0; if(hData->GetSumOfWeights() > 0) daUnc = 1/hData->GetSumOfWeights();
  double mcUnc = (totalStatUnc+totalSystUnc)/hBck->GetSumOfWeights()/hBck->GetSumOfWeights();
  printf("%s data/bck: %f / %f +/- %f/%f/%f = %f +/- %f\n",plotName.Data(),hData->GetSumOfWeights(),hBck->GetSumOfWeights(),TMath::Sqrt(totalStatUnc),TMath::Sqrt(totalSystUnc),TMath::Sqrt(totalStatUnc+totalSystUnc),scale,TMath::Sqrt(daUnc+mcUnc)*scale);
  if(applyScaling == true) hBck->Scale(scale);

  for(int ic=0; ic<nPlotCategories; ic++){
    if(!_hist[ic]) continue;
    if(isBlind == true && ic == kPlotData) continue;
    if(applyScaling == true && ic != kPlotData && ic != kPlotBSM) _hist[ic]->Scale(scale);
    if(ic == kPlotBSM && higgsLabel == "W_{L}W_{L}") {_hist[ic]->Scale(10.0); myPlot.setHiggsLabel("W_{L}W_{L} x 10");}
    if(_hist[ic]->GetSumOfWeights() > 0) myPlot.setMCHist(ic, _hist[ic]);
  }
   myPlot.setAllHist(hBck);

  myPlot.setOverlaid(false);
  if(isSignalStack == true){
    //if(_hist[kPlotSignal0]->GetSumOfWeights() > 0 &&
    //   _hist[kPlotBSM]    ->GetSumOfWeights() > 0) { _hist[kPlotSignal0]->Add(_hist[kPlotBSM],-1); myPlot.setMCHist(kPlotSignal0, _hist[kPlotSignal0]);}
    if(_hist[kPlotSignal0]->GetSumOfWeights() > 0) { _hist[kPlotSignal0]->Add(hBck); myPlot.setMCHist(kPlotSignal0, _hist[kPlotSignal0]);}
    if(_hist[kPlotBSM]    ->GetSumOfWeights() > 0) { _hist[kPlotBSM    ]->Add(hBck); myPlot.setMCHist(kPlotBSM,     _hist[kPlotBSM    ]);}
    //myPlot.setOverlaid(true);
  }

  TCanvas* c1 = new TCanvas("c1", "c1",5,5,500,500);

  double maxRatio = 0.0;
  double minRatio = 1.0;

  if(show2D==false){
  if(isLogY == true) c1->SetLogy();
  if(isLogX == true) c1->SetLogx();
  myPlot.Draw(ReBin);  // Can pass a rebin 
  CMS_lumi( c1, year, 1);
  } else {
  c1->SetBottomMargin(0.1);
  c1->cd();
  TPad *pad1 = new TPad("pad1", "pad1",0.00,0.30,1.00,1.00);
  TPad *pad2 = new TPad("pad2", "pad2",0.00,0.00,1.00,0.29);
  pad1->SetBottomMargin(0);
  pad2->SetTopMargin(0);
  pad2->SetBottomMargin(0.3);
  pad1->Draw();
  pad2->Draw();

  pad1->cd();
  pad1->RedrawAxis();
  if(isLogY == true) c1->SetLogy();
  if(isLogY == true) pad1->SetLogy();
  if(isLogX == true) c1->SetLogx();
  if(isLogX == true) pad1->SetLogx();
  
  if(isLogSpecial) {c1->SetLogx();pad1->SetLogx();pad2->SetLogx();}

  myPlot.Draw(ReBin);
  CMS_lumi( pad1, year, 1);

  pad2->cd();
  pad2->RedrawAxis();
  //pad2->SetGridy();
  hBck ->Rebin(ReBin);
  hData->Rebin(ReBin);
  TH1D* hTotalDivision = (TH1D*) hData->Clone();
  hTotalDivision->Reset();
  TH1D* hDataDivision = (TH1D*) hData->Clone();
  hDataDivision->Reset();
  TH1D* hRatio = (TH1D*) hData->Clone();
  hRatio->Reset();
  TH1D* hBand = (TH1D*) hData->Clone();
  hBand->Reset();

  hDataDivision ->Add(hData );
  hTotalDivision->Add(hBck  );

  hRatio->Add(hDataDivision);
  hRatio->Divide(hTotalDivision);

  bool showPulls = false;
  bool useGarwood = false;
  if(showPulls) atributes(hRatio,XTitle.Data(),"Pull",units.Data());
  else          atributes(hRatio,XTitle.Data(),"Data/SM",units.Data());
  if(showPulls) atributes(hBand,XTitle.Data(),"Pull",units.Data());
  else          atributes(hBand,XTitle.Data(),"Data/SM",units.Data());

  TGraphAsymmErrors *gStatic = new TGraphAsymmErrors(hDataDivision);
  TGraphAsymmErrors *g = new TGraphAsymmErrors(hRatio);
  for(int i=1; i<=hDataDivision->GetNbinsX(); i++){
    if(showPulls){
      double pull = 0.0;
      if(useGarwood == false){
        if((hDataDivision->GetBinError(i) > 0 || hTotalDivision->GetBinError(i) > 0) && hDataDivision->GetBinContent(i) > 0){
          pull = (hDataDivision->GetBinContent(i)-hTotalDivision->GetBinContent(i))/sqrt(hDataDivision->GetBinError(i)*hDataDivision->GetBinError(i)+hTotalDivision->GetBinError(i)*hTotalDivision->GetBinError(i));
        }
      } 
      else {
        pull = TMath::Sqrt(2)*TMath::ErfInverse(-1+2*ROOT::Math::poisson_cdf(hDataDivision->GetBinContent(i),hTotalDivision->GetBinContent(i))); 
      }
      hRatio->SetBinContent(i,pull);
      hRatio->SetBinError(i,1.0);
      if(printRatios) printf("pull(%3d): da: %f pred: %f --> %f\n",i,hDataDivision ->GetBinContent(i),hTotalDivision->GetBinContent(i),pull);
    }
    else {
      hBand->SetBinContent(i,1);
      hBand->SetBinError(i,hTotalDivision->GetBinError(i)/hTotalDivision->GetBinContent(i));
      hTotalDivision->SetBinError(i,0);
      double N = gStatic->GetY()[i-1];
      double alpha=(1-0.6827);
      double L = (N==0) ? 0 : (ROOT::Math::gamma_quantile(alpha/2,N,1.));
      double U = ROOT::Math::gamma_quantile_c(alpha/2,N+1,1);
      if( N != hDataDivision ->GetBinContent(i)) cout << "PROBLEM" << endl;
      //double diff = hDataDivision->GetBinError(i);
      double diffUp   = U-double(N);
      double diffDown = double(N)-L;
      double pull = 1.0; double pullerr = 0.0;
      if(hDataDivision->GetBinContent(i) && hTotalDivision->GetBinContent(i) > 0){
        pull = (hDataDivision->GetBinContent(i)/hTotalDivision->GetBinContent(i));
	pullerr = pull*(diffUp+diffDown)/2/hDataDivision->GetBinContent(i);
        g->SetPointEYlow (i-1, pull*diffDown/hDataDivision->GetBinContent(i));
        g->SetPointEYhigh(i-1, pull*diffUp  /hDataDivision->GetBinContent(i));
      }
      else if(hTotalDivision->GetBinContent(i) > 0){
        pull = (hDataDivision->GetBinContent(i)/hTotalDivision->GetBinContent(i));
	pullerr = diffUp/hTotalDivision->GetBinContent(i);
        g->SetPointEYlow (i-1, 0);
        g->SetPointEYhigh(i-1, diffUp/hTotalDivision->GetBinContent(i));
      }
      else {
        g->SetPointEYlow (i-1, 0);
        g->SetPointEYhigh(i-1, 0);
      }
      
      g->SetPointEXlow (i-1, 0);
      g->SetPointEXhigh(i-1, 0);
      //if(pull<0.97) pull = 0.98+gRandom->Uniform()*0.01;
      //if(pull>1.05) pull = 1.05+gRandom->Uniform()*0.02;
      //hRatio->SetBinContent(i,pull);
      //hRatio->SetBinError(i,pullerr);
      //if(pull<0.97||pull>1.03)
      if(pull+pullerr > maxRatio) maxRatio = pull+pullerr;
      if(pull-pullerr < minRatio) minRatio = pull-pullerr;
      if(printRatios) printf("ratio(%3d): %f +/- %f --> da: %f +/- %f (%f) pred: %f +/- %f\n",i,pull,pullerr,hDataDivision ->GetBinContent(i),hDataDivision ->GetBinError(i),(diffUp+diffDown)/2,hTotalDivision->GetBinContent(i),hTotalDivision->GetBinError(i));
    }
  }
  //TGraphAsymmErrors gd(5);
  //gd.Divide(hDataDivision,hTotalDivision,"pois");
//printf("%d %d %d\n",hDataDivision->GetNbinsX(),hTotalDivision->GetNbinsX(),gd.GetN () );

  //hRatio->Draw("e");
  hBand->SetFillColor(12);
  hBand->SetFillStyle(3345);
  hBand->SetMarkerSize(0);
  hBand->SetLineWidth(0);
  hBand->Draw("E2");
  g->Draw("P,same,z");

  // Draw a line throgh y=0
  double theLines[2] = {1.0, 0.5};
  if(showPulls) {theLines[0] = 0.0; theLines[1] = 1.5;}
  TLine* baseline = new TLine(hRatio->GetXaxis()->GetXmin(), theLines[0],
                              hRatio->GetXaxis()->GetXmax(), theLines[0]);
  baseline->SetLineStyle(kDashed);
  baseline->Draw();
  // Set the y-axis range symmetric around y=0
  Double_t dy = TMath::Max(TMath::Abs(hRatio->GetMaximum()),
                           TMath::Abs(hRatio->GetMinimum())) + theLines[1];
  minRatio = TMath::Min(TMath::Max(minRatio-0.03,0.000),0.810);
  maxRatio = TMath::Min(TMath::Max(maxRatio+0.03,1.190),2.999);
  if(showPulls) hBand->GetYaxis()->SetRangeUser(-dy, +dy);
  else          hBand->GetYaxis()->SetRangeUser(minRatio,maxRatio);
  hRatio->GetYaxis()->CenterTitle();
  eraselabel(pad1,hData->GetXaxis()->GetLabelSize());
  }

  char CommandToExec[300];
  sprintf(CommandToExec,"mkdir -p plots");
  gSystem->Exec(CommandToExec);  

  if(strcmp(outputName.Data(),"") != 0){
    TString myOutputFile;
    outputName = Form("%s_%d",outputName.Data(),year);
    myOutputFile = Form("plots/%s.eps",outputName.Data());
    //c1->SaveAs(myOutputFile.Data());
    myOutputFile = Form("plots/%s.png",outputName.Data());
    c1->SaveAs(myOutputFile.Data());
    myOutputFile = Form("plots/%s.pdf",outputName.Data());
    c1->SaveAs(myOutputFile.Data());
    if(makeRootFile) {
      for(int i=1; i<=_hist[kPlotData]->GetNbinsX(); i++) if(_hist[kPlotData]->GetBinContent(i)<0) {_hist[kPlotData]->SetBinContent(i,0); _hist[kPlotData]->SetBinError(i,0);}
      TFile output(Form("plots/%s.root",outputName.Data()),"RECREATE");
      hBck->Scale(0.0);
      for(int ic=0; ic<nPlotCategories; ic++){
        if(!_hist[ic]) continue;
        _hist[ic]->Write();
        if(ic != kPlotData && ic != kPlotBSM)  hBck->Add(_hist[ic]);
      }
      hBck->Write();
      output.Close();
    }
  }

  bool computePU = false;
  if(computePU || plotName.Contains("_npv.root") == true){
    hBck->Scale(hData->GetSumOfWeights()/hBck->GetSumOfWeights());
    TH1D * npvWeights =  (TH1D*)hData->Clone("npvWeights");
    npvWeights->Sumw2();
    npvWeights->Divide(hBck);
    for(int i=1; i<=npvWeights->GetNbinsX(); i++){
      if(npvWeights->GetBinContent(i) > 3) {
        printf("Big number in (%d): %f, set to 3\n",i,npvWeights->GetBinContent(i));npvWeights->SetBinContent(i,3);
      }
    }
    TFile output(Form("npvWeights_%d.root",year),"RECREATE");
    npvWeights->Write();
    output.Close();
  }

}
