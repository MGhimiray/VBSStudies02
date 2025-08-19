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

// shapeName = shapes_fit_s / shapes_fit_b / shapes_prefit

void producingYields(int jetBin = -1, TString mlfitResult = "/home/submit/ceballos/cards/ww_smp24001/logs_ana1009/fitDiagnosticsww_fid_normalized1_obs.root", TString shapeName = "shapes_fit_s") {

  TFile *mlfit = TFile::Open(mlfitResult); assert(mlfit);
  TH1F* _histoWrite[nPlotCategories];

  int chanAux, regionsAux;
  if     (jetBin >= -1) {
    chanAux = 8;
    regionsAux = 5;
  }
  else if(jetBin == -2 || jetBin == -3) {
    chanAux = 2;
    regionsAux = 1;
  }

  for(int nc=0; nc<nPlotCategories; nc++) {
    _histoWrite[nc] = new TH1F(Form("histo%d",nc), Form("histo%d",nc), regionsAux, -0.5, (float)regionsAux-0.5);
  }
  TH1F* histo_total = new TH1F(Form("histo_total"), Form("histo_total"), regionsAux, -0.5, (float)regionsAux-0.5);

  const int chan = chanAux;
  const int regions = regionsAux;
  TString channelName[chan];
  if     (jetBin >= -1) {
     for(int i=1; i<=8; i++)  channelName[i-1] = Form("ch%d",i);
  }
  else if(jetBin == -2) {
    channelName[0] = Form("ch9");
    channelName[1] = Form("ch10");
  }
  else if(jetBin == -3) {
    channelName[0] = Form("ch11");
    channelName[1] = Form("ch12");
  }

  double yields[regions][nPlotCategories], yieldsE[regions][nPlotCategories];
  bool nonZeroYields[nPlotCategories];
  double total[regions], totalE[regions];
  for(int ic=0; ic<nPlotCategories; ic++) nonZeroYields[ic] = false;
  for(int nr=0; nr<regions; nr++){
    for(int ic=0; ic<nPlotCategories; ic++){
      yields[nr][ic] = 0;
      yieldsE[nr][ic] = 0;
    }
    total[nr] = 0;
    totalE[nr] = 0;
  }

  TH1F* _hist[chan][nPlotCategories+1];
  for(int nc=0; nc<chan; nc++){
    bool passJetBin = false;
    if(jetBin <= -1 || nc%4 == jetBin) passJetBin = true;
    if(!passJetBin) continue;
    for(int ic=0; ic<nPlotCategories; ic++){
      if(ic != kPlotData){
        _hist[nc][ic] = ((TH1F*)mlfit->Get(Form("%s/%s/%s",shapeName.Data(),channelName[nc].Data(),plotBaseNames[ic].Data())));
        if(_hist[nc][ic]){
          for(int nr=0; nr<regions; nr++){
            int theIC = ic;
            if(ic == kPlotqqWW || ic == kPlotggWW ||
               ic == kPlotSignal0 || ic == kPlotSignal1 || ic == kPlotSignal2 ||
               ic == kPlotSignal3 || ic == kPlotSignal4 || ic == kPlotSignal5) theIC = kPlotqqWW;
            if(ic == kPlotTT || ic == kPlotTW) theIC = kPlotTT;
            yields[nr][theIC]  += _hist[nc][ic]->GetBinContent(nr+1);
            yieldsE[nr][theIC] += _hist[nc][ic]->GetBinError(nr+1);
            nonZeroYields[theIC] = true;
          } // loop over regions        
        }
      }
      else {
        nonZeroYields[kPlotData] = true;
        double x,y;
        TGraphAsymmErrors *gr = ((TGraphAsymmErrors*)mlfit->Get(Form("%s/%s/%s",shapeName.Data(),channelName[nc].Data(),"data")));
        for(int nr=0; nr<regions; nr++){
          int a = gr->GetPoint(nr, x, y);
          yields[nr][ic]  += y;
          yieldsE[nr][ic] += y;
        }
      }
    } // loop over categories

    // Special for NonPromptWZ
    if((TH1F*)mlfit->Get(Form("%s/%s/%s",shapeName.Data(),channelName[nc].Data(),"NonPromptWZ"))){
      _hist[nc][kPlotNonPrompt] = ((TH1F*)mlfit->Get(Form("%s/%s/%s",shapeName.Data(),channelName[nc].Data(),"NonPromptWZ")));
      if(_hist[nc][kPlotNonPrompt]){
        for(int nr=0; nr<regions; nr++){
          yields[nr][kPlotNonPrompt]  += _hist[nc][kPlotNonPrompt]->GetBinContent(nr+1);
          yieldsE[nr][kPlotNonPrompt] += _hist[nc][kPlotNonPrompt]->GetBinError(nr+1);
          nonZeroYields[kPlotNonPrompt] = true;
        } // loop over regions
      }
    }

    _hist[nc][nPlotCategories] = ((TH1F*)mlfit->Get(Form("%s/%s/%s",shapeName.Data(),channelName[nc].Data(),"total")));
    for(int nr=0; nr<regions; nr++){
      total[nr]  += _hist[nc][nPlotCategories]->GetBinContent(nr+1);
      totalE[nr] += _hist[nc][nPlotCategories]->GetBinError(nr+1);
    } // loop over regions

  } // loop over jet bins

  for(int ic=0; ic<nPlotCategories; ic++){
    if(nonZeroYields[ic] == true) {
      printf("%20s & ",plotBaseNames[ic].Data());
      for(int nr=0; nr<regions; nr++){
        _histoWrite[ic]->SetBinContent(nr+1, yields[nr][ic]);
        _histoWrite[ic]->SetBinError  (nr+1, yields[nr][ic],yieldsE[nr][ic]);
        yieldsE[nr][kPlotData] = sqrt(yieldsE[nr][kPlotData]);
        if(ic == kPlotData) printf("      %6d         ",(int)yields[nr][ic]);
        else                printf(" %7.1f $\\pm$ %5.1f ",yields[nr][ic],yieldsE[nr][ic]);
        if(nr == regions-1) printf("\\\\"); else printf("&");
      }
      printf("\n");
    }
  }
  printf("%20s & ","Total");
  for(int nr=0; nr<regions; nr++){
    histo_total->SetBinContent(nr+1, total[nr]);
    histo_total->SetBinError  (nr+1, totalE[nr]);
    printf(" %7.1f $\\pm$ %5.1f ",total[nr],totalE[nr]);
    if(nr == regions-1) printf("\\\\"); else printf("&");
  }
  printf("\n");

  TString postfix = "";
  if(strcmp(shapeName.Data(),"shapes_prefit")==0) postfix = "_prefit";
  TFile fileOutput(Form("ww_output_bin%d%s.root",jetBin,postfix.Data()),"RECREATE");
  fileOutput.cd();
  for(int nc=0; nc<nPlotCategories; nc++) {
    _histoWrite[nc]->Write();
  }
  histo_total->Write();
  fileOutput.Close();

}
