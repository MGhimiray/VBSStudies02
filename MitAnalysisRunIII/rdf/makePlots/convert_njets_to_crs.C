#include "TROOT.h"
#include "TFile.h"
#include "TH1F.h"
#include "TColor.h"
#include <map>
#include "common.h"

void convert_njets_to_crs(TString postfix = ""){
  const int njets = 4;

  TFile *fileInput[njets];
  for(int nj=0; nj<njets; nj++) {
    fileInput[nj] = new TFile(Form("ww_output_bin%d%s.root",nj,postfix.Data()), "read");
  }

  TH1F* histo[njets][nPlotCategories];
  TH1F* histo_total[njets];
  for(int nj=0; nj<njets; nj++) for(int nc=0; nc<nPlotCategories; nc++) histo[nj][nc] = NULL;

  for(int nj=0; nj<njets; nj++) {
    for(int nc=0; nc<nPlotCategories; nc++) {
      histo[nj][nc] = (TH1F*)fileInput[nj]->Get(Form("histo%d",nc));
    }
    histo_total[nj] = (TH1F*)fileInput[nj]->Get(Form("histo_total"));
  }

  TH1F* _hist[nPlotCategories];
  TH1F* _histo_total;
  for(int nc=0; nc<nPlotCategories; nc++) {
    _hist[nc] = new TH1F(Form("histo%d",nc), Form("histo%d",nc), 4, -0.5, 3.5);
  }
  _histo_total = new TH1F(Form("histo_total"), Form("histo_total"), 4, -0.5, 3.5);

  for(int ncr=0; ncr<5; ncr++){
    TFile* outFileLimits = new TFile(Form("ww_output_cr%d%s.root",ncr,postfix.Data()),"recreate");
    outFileLimits->cd();
    for(int nc=0; nc<nPlotCategories; nc++) {
      bool isNonZero = false;
      for(int nj=0; nj<njets; nj++) {
        if(!histo[nj][nc]) continue;
        isNonZero = true;
        _hist[nc]->SetBinContent(nj+1, histo[nj][nc]->GetBinContent(ncr+1));
        _hist[nc]->SetBinError  (nj+1, histo[nj][nc]->GetBinError  (ncr+1));

        if(strcmp(postfix.Data(),"_prefit")==0 && ncr == 1 && (nj == 2 || nj == 3) && nc == kPlotTT){
          _hist[nc]->SetBinContent(nj+1, 1.0*_hist[nc]->GetBinContent(nj+1));
        }

      }
      if(isNonZero == true) _hist[nc]->Write();
    }

    if(histo_total[0]){
      for(int nj=0; nj<njets; nj++) {
        _histo_total->SetBinContent(nj+1, histo_total[nj]->GetBinContent(ncr+1));
        _histo_total->SetBinError  (nj+1, histo_total[nj]->GetBinError  (ncr+1));
      }
      _histo_total->Write();
    }

    outFileLimits->Close();
  }
}
