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

void makeLepRes(TString InputDir = "anaZ", TString anaSel = "zAnalysis1001", int year = 20221){

  const int startF = 240;
  const int nHisto = 24;
  TH1D *histo_Z[nHisto][nPlotCategories];

  TFile *inputFile;

  for(unsigned nSel=0; nSel<nHisto; nSel++) {
    inputFile = new TFile(Form("%s/fillhisto_%s_%d_%d.root",InputDir.Data(),anaSel.Data(),year,startF+nSel), "read");
    for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
      histo_Z[nSel][ic] = (TH1D*)inputFile->Get(Form("histo%d", ic)); assert(histo_Z[nSel][ic]);
    }
    
    double sfMean =  histo_Z[nSel][kPlotData]->GetMean()/histo_Z[nSel][kPlotDY]->GetMean();
    double smearDA = histo_Z[nSel][kPlotData]->GetRMS(); // sqrt(histo_Z[nSel][kPlotData]->GetRMS()*histo_Z[nSel][kPlotData]->GetRMS()-2.4955*2.4955);
    double smearMC = histo_Z[nSel][kPlotDY  ]->GetRMS(); // sqrt(histo_Z[nSel][kPlotDY  ]->GetRMS()*histo_Z[nSel][kPlotDY  ]->GetRMS()-2.4955*2.4955);
    double smearDiff = sqrt(max(smearDA*smearDA-smearMC*smearMC,0.0))/histo_Z[nSel][kPlotData]->GetMean();
    if(nSel*2 == nHisto) printf("***************************\n");
    printf("bin(%2d) %.4f | %.4f %.4f %.4f\n",nSel,sfMean,smearDA,smearMC,smearDiff);
  }

}
