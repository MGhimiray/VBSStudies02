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

void makeGammaDataCards(TString InputDir = "anaZ", int fidAna = 0, int mHVal = 0){
  TFile *inputFile;
  TFile *outputFile;

  for(unsigned nPtBin=0; nPtBin<20; nPtBin++) {
    for(unsigned nEtaBin=0; nEtaBin<2; nEtaBin++) {

      TH1D *histo_Baseline[nPlotCategories];
      inputFile = new TFile(Form("%s/fillhisto_gammaAnalysis1001_2018_%d.root",InputDir.Data(),3+4*nEtaBin+10*nPtBin), "read");
      for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
        histo_Baseline[ic]  = (TH1D*)inputFile->Get(Form("histo%d", ic));  histo_Baseline[ic] ->SetDirectory(0);
      }
      delete inputFile;

      inputFile = new TFile(Form("%s/fillhisto_gammaAnalysis1001_2018_%d.root",InputDir.Data(),1+4*nEtaBin+10*nPtBin), "read");
      histo_Baseline[kPlotNonPrompt] = (TH1D*)inputFile->Get(Form("histo%d", kPlotData)); histo_Baseline[kPlotNonPrompt] ->SetDirectory(0);
      delete inputFile;

      TString outputLimits = Form("output_gj_pt%d_eta%d.root",nPtBin,nEtaBin);
      outputFile = new TFile(outputLimits, "RECREATE");
      outputFile->cd();
      printf("%2d %d\n",nPtBin,nEtaBin);
      double SF = 1.0;
      if(histo_Baseline[kPlotData]->GetSumOfWeights()-histo_Baseline[kPlotNonPrompt]->GetSumOfWeights() > 0){
        SF = (histo_Baseline[kPlotData]->GetSumOfWeights()-histo_Baseline[kPlotNonPrompt]->GetSumOfWeights())/histo_Baseline[kPlotOther]->GetSumOfWeights();
      }
      else {
        SF = histo_Baseline[kPlotData]->GetSumOfWeights()/histo_Baseline[kPlotOther]->GetSumOfWeights()/2.0;
      }
      histo_Baseline[kPlotOther]->Scale(SF);
      for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
        histo_Baseline[ic]->SetNameTitle(Form("histo_%s",plotBaseNames[ic].Data()),Form("histo_%s",plotBaseNames[ic].Data()));
        if(ic != kPlotData && ic != kPlotOther && ic != kPlotNonPrompt) continue;
	histo_Baseline[ic]->Write();
	printf("%2d %d %2d %f\n",nPtBin,nEtaBin,ic,histo_Baseline[ic]->GetSumOfWeights());
      }
      outputFile->Close();

      // Filling datacards txt file
      char outputLimitsCard[200];  					  
      sprintf(outputLimitsCard,"datacard_gj_pt%d_eta%d.txt",nPtBin,nEtaBin);
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
        newcardShape << Form("ch1  ");

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
        if     (ic != kPlotOther) newcardShape << Form("%d  ", ic);
        else if(ic == kPlotOther) newcardShape << Form("%d  ", 0);
      }
      newcardShape << Form("\n");

      newcardShape << Form("rate  ");
      for (int ic=0; ic<nPlotCategories; ic++){
        if(!histo_Baseline[ic]) continue;
        if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
        newcardShape << Form("%f  ", histo_Baseline[ic]->GetSumOfWeights());
      }
      newcardShape << Form("\n");

      newcardShape << Form("CMS_gamma_norn    lnN     ");
      for (int ic=0; ic<nPlotCategories; ic++){
        if(!histo_Baseline[ic]) continue;
        if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
        if(ic == kPlotNonPrompt) newcardShape << Form("- ");
        else                     newcardShape << Form("%6.3f ",1.03);
      }
      newcardShape << Form("\n");

      newcardShape << Form("CMS_fake_norn    lnN     ");
      for (int ic=0; ic<nPlotCategories; ic++){
        if(!histo_Baseline[ic]) continue;
        if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
        if(ic == kPlotOther) newcardShape << Form("- ");
        else                 newcardShape << Form("%6.3f ",1.03);
      }
      newcardShape << Form("\n");

      newcardShape << Form("ch1 autoMCStats 0\n");

      newcardShape.close();

    } // Loop nEtaBin
  } // Loop nPtBin
}
