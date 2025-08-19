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

void producingYields_fromHistograms(TString plotName = "/home/submit/ceballos/cards/combine_plots_madgraph_smp24001/ww_output_bin-2.root", int chan = 0, int printOverall = 1) {

  double yields[nPlotCategories], yieldsE[nPlotCategories];
  bool nonZeroYields[nPlotCategories];
  double total, totalE;
  for(int ic=0; ic<nPlotCategories; ic++) nonZeroYields[ic] = false;
  for(int ic=0; ic<nPlotCategories; ic++){
    yields[ic] = 0;
    yieldsE[ic] = 0;
  }
  total = 0;
  totalE = 0;

  TFile* file = new TFile(plotName, "read");  if(!file) {printf("File %s does not exist\n",plotName.Data()); return;}
  TH1F* _hist[nPlotCategories];
  TH1F* _histo_total;
  for(int ic=0; ic<nPlotCategories; ic++){
    _hist[ic] = (TH1F*)file->Get(Form("histo%d",ic));
    _histo_total = (TH1F*)file->Get(Form("histo_total"));
  }
  int sigCat = kPlotqqWW;
  if(chan == 1) sigCat = kPlotEWKSSWW;
  for(int ic=0; ic<nPlotCategories; ic++){
    if(_hist[ic]) {
      if(ic == kPlotggWW ||
         ic == kPlotSignal0 || ic == kPlotSignal1 || ic == kPlotSignal2 ||
         ic == kPlotSignal3 || ic == kPlotSignal4 || ic == kPlotSignal5) {_hist[sigCat]->Add(_hist[ic]); _hist[ic]->Scale(0.0);}
      if(ic == kPlotTW) {_hist[kPlotTT]->Add(_hist[ic]); _hist[ic]->Scale(0.0);}
    }
  }

  for(int ic=0; ic<nPlotCategories; ic++){
    if(_hist[ic]) {
      int theIC = ic;
      if(chan == 0 &&
         (ic == kPlotqqWW || ic == kPlotggWW ||
          ic == kPlotSignal0 || ic == kPlotSignal1 || ic == kPlotSignal2 ||
          ic == kPlotSignal3 || ic == kPlotSignal4 || ic == kPlotSignal5)) theIC = kPlotqqWW;
      else if(chan == 1 &&
         (ic == kPlotEWKSSWW ||
          ic == kPlotSignal0 || ic == kPlotSignal1 || ic == kPlotSignal2 ||
          ic == kPlotSignal3 || ic == kPlotSignal4 || ic == kPlotSignal5)) theIC = kPlotEWKSSWW;
      else if(ic == kPlotTT || ic == kPlotTW) theIC = kPlotTT;
      for(int i=1; i<=_hist[ic]->GetNbinsX(); i++){
        yields[theIC]  += _hist[ic]->GetBinContent(i);
        yieldsE[theIC] += _hist[ic]->GetBinError(i);
      }
      nonZeroYields[theIC] = true;
    }
  }
  for(int ic=0; ic<nPlotCategories; ic++){
    if(_hist[ic] && _hist[ic]->GetSumOfWeights() > 0.0) {
      printf("%20s & ",plotBaseNames[ic].Data());
      if(printOverall == 1){
        if(ic == kPlotData) printf("      %6d         ",(int)yields[ic]);
        else                printf(" %7.1f $\\pm$ %5.1f ",yields[ic],yieldsE[ic]);
        printf("&\n");
      } else {
        for(int i=1; i<=_hist[ic]->GetNbinsX(); i++){
          if(ic == kPlotData)             printf("      %6d         ",(int)_hist[ic]->GetBinContent(i));
          else                            printf(" %7.1f $\\pm$ %5.1f ",_hist[ic]->GetBinContent(i),_hist[ic]->GetBinError(i));
          if(i == _hist[ic]->GetNbinsX()) printf("\\\\"); else printf("&");
        }
        printf("\n");
      }
    }
  }
  printf("%20s & ","Total");
  if(_histo_total && _histo_total->GetSumOfWeights() > 0.0) {
    for(int i=1; i<=_histo_total->GetNbinsX(); i++){
      total  += _histo_total->GetBinContent(i);
      totalE += TMath::Power(_histo_total->GetBinError(i),2);
    }
    if(printOverall == 1){
      printf(" %7.1f $\\pm$ %5.1f ",total,max(sqrt(total),sqrt(totalE)));
      printf("&\n");
    } else {
      for(int i=1; i<=_histo_total->GetNbinsX(); i++){
        printf(" %7.1f $\\pm$ %5.1f ",_histo_total->GetBinContent(i),_histo_total->GetBinError(i));
        if(i == _histo_total->GetNbinsX()) printf("\\\\"); else printf("&");
      }
    }
  }
  printf("\n");

}
