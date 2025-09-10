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

void makeFakeAnalysisDataCards(TString InputDir = "anaZ", int year = 2022){
  TFile *inputFile0, *inputFile1, *outputFile;
  for(unsigned ltype=0; ltype<2; ltype++) {
    for(unsigned ptbin=0; ptbin<2; ptbin++) {
      for(unsigned version=0; version<8; version++) {
	double yields[3] = {0, 0, 0};
	TH1D *histo_Baseline[nPlotCategories];
	inputFile0 = new TFile(Form("%s/fillhisto_fakeAnalysis1001_%d_%d.root",InputDir.Data(),year,100+ltype+2*ptbin+2*2*version), "read");
	for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
          histo_Baseline[ic]  = (TH1D*)inputFile0->Get(Form("histo%d", ic));  histo_Baseline[ic] ->SetDirectory(0);
          if     (ic==kPlotData)      yields[0] = histo_Baseline[ic]->GetSumOfWeights();
          else if(ic!=kPlotNonPrompt) yields[1] = yields[1] + histo_Baseline[ic]->GetSumOfWeights();
          else if(histo_Baseline[ic]->GetSumOfWeights() > 0) printf("This category0 (%d) should be 0!\n",ic);
	}
	delete inputFile0;
	inputFile1 = new TFile(Form("%s/fillhisto_fakeAnalysis1003_2022_%d.root",InputDir.Data(),100+ltype+2*ptbin+2*2*version), "read");
	for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
          if(ic!=kPlotNonPrompt) continue;
          histo_Baseline[ic]  = (TH1D*)inputFile1->Get(Form("histo%d", ic));  histo_Baseline[ic] ->SetDirectory(0);
          yields[2] = yields[2] + histo_Baseline[ic]->GetSumOfWeights();
	}
	delete inputFile1;

	double scalingNonPrompt = (yields[0]-yields[1])/yields[2];
	if(scalingNonPrompt > 0) {
          histo_Baseline[kPlotNonPrompt]->Scale(scalingNonPrompt);
	}
	else {
          histo_Baseline[kPlotOther]->Scale(0.9);
          scalingNonPrompt = (yields[0]-yields[1]*0.9)/yields[2];
          histo_Baseline[kPlotNonPrompt]->Scale(scalingNonPrompt);
	}

	for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
          if(ic==kPlotData || ic==kPlotOther || ic==kPlotNonPrompt) continue;
            histo_Baseline[kPlotOther]->Add(histo_Baseline[ic]);
            histo_Baseline[ic]->Scale(0.0);
	}

	TString outputLimits = Form("output_fake_%d_l%d_ptbin%d_version%d.root",year,ltype,ptbin,version);
	outputFile = new TFile(outputLimits, "RECREATE");
	outputFile->cd();
	printf("%d %d %d\n",ltype,ptbin,version);
	for(unsigned ic=kPlotData; ic!=nPlotCategories; ic++) {
          if(histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
          histo_Baseline[ic]->SetNameTitle(Form("histo_%s",plotBaseNames[ic].Data()),Form("histo_%s",plotBaseNames[ic].Data()));
          //if     (ic != kPlotNonPrompt && ic != kPlotOther)	  histo_Baseline[ic]->SetNameTitle(Form("histo_%s",plotBaseNames[ic].Data()),Form("histo_%s",plotBaseNames[ic].Data()));
          //else if(ic == kPlotNonPrompt && (version==0||version==2)) histo_Baseline[ic]->SetNameTitle(Form("histo_NonPrompt0"),Form("histo_NonPrompt0"));
          //else if(ic == kPlotNonPrompt && (version==1||version==3)) histo_Baseline[ic]->SetNameTitle(Form("histo_NonPrompt1"),Form("histo_NonPrompt1"));
          //else if(ic == kPlotOther && (version==0||version==2))	  histo_Baseline[ic]->SetNameTitle(Form("histo_Other0"),Form("histo_Other0"));
          //else if(ic == kPlotOther && (version==1||version==3))	  histo_Baseline[ic]->SetNameTitle(Form("histo_Other1"),Form("histo_Other1"));
          histo_Baseline[ic]->Write();
	}
	outputFile->Close();

	// Filling datacards txt file
	char outputLimitsCard[200];				      
	sprintf(outputLimitsCard,"datacard_fake_%d_l%d_ptbin%d_version%d.txt",year,ptbin,ltype,version);
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
          //if     (ic != kPlotNonPrompt && ic != kPlotOther)	  newcardShape << Form("%s  ", plotBaseNames[ic].Data());
          //else if(ic == kPlotNonPrompt && (version==0||version==2)) newcardShape << Form("NonPrompt0  ");
          //else if(ic == kPlotNonPrompt && (version==1||version==3)) newcardShape << Form("NonPrompt1  ");
          //else if(ic == kPlotOther && (version==0||version==2))	  newcardShape << Form("Other0  ");
          //else if(ic == kPlotOther && (version==1||version==3))	  newcardShape << Form("Other1  ");
	}
	newcardShape << Form("\n");

	newcardShape << Form("process  ");
	for (int ic=0; ic<nPlotCategories; ic++){
          if(!histo_Baseline[ic]) continue;
          if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
          if     (ic != kPlotNonPrompt) newcardShape << Form("%d  ", ic);
          else if(ic == kPlotNonPrompt) newcardShape << Form("%d  ", 0);
          //if     (ic != kPlotNonPrompt && ic != kPlotOther)	  newcardShape << Form("%d  ", ic);
          //else if(ic == kPlotNonPrompt && (version==0||version==2)) newcardShape << Form("%d  ", 0);
          //else if(ic == kPlotNonPrompt && (version==1||version==3)) newcardShape << Form("%d  ", -1);
          //else if(ic == kPlotOther && (version==0||version==2))	  newcardShape << Form("%d  ", 30);
          //else if(ic == kPlotOther && (version==1||version==3))	  newcardShape << Form("%d  ", 31);
	}
	newcardShape << Form("\n");

	newcardShape << Form("rate  ");
	for (int ic=0; ic<nPlotCategories; ic++){
          if(!histo_Baseline[ic]) continue;
          if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
          newcardShape << Form("%f  ", histo_Baseline[ic]->GetSumOfWeights());
	}
	newcardShape << Form("\n");

	newcardShape << Form("CMS_nonprompt_norn    lnN	  ");
	for (int ic=0; ic<nPlotCategories; ic++){
          if(!histo_Baseline[ic]) continue;
          if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
          if(ic == kPlotNonPrompt) newcardShape << Form("%6.3f ",1.05);
          else			 newcardShape << Form("- ");
	}
	newcardShape << Form("\n");

	newcardShape << Form("CMS_mc_norn    lnN     ");
	for (int ic=0; ic<nPlotCategories; ic++){
          if(!histo_Baseline[ic]) continue;
          if(ic == kPlotData || histo_Baseline[ic]->GetSumOfWeights() <= 0) continue;
          if(ic == kPlotNonPrompt) newcardShape << Form("- ");
          else			 newcardShape << Form("%6.3f ",1.05);
	}
	newcardShape << Form("\n");

	newcardShape << Form("ch1 autoMCStats 0\n");

	newcardShape.close();
      } // Loop version
    } // Loop ptbin
  } // Loop ltype
}
