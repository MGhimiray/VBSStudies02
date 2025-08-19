#include "TROOT.h"
#include "TFile.h"
#include "TH1F.h"
#include "TColor.h"
#include <map>
#include "common.h"

void convert_histograms(bool isModify = false, TString inputSampleName = "/home/submit/ceballos/cards/combine_plots/mytest.root", 
  TString subFoldersName = "combinedMy/mll", TString outputSampleName = "output.root"){

  TFile *fileInput = new TFile(inputSampleName.Data(), "read");

  TH1F* histo[nPlotCategories];
  for(int nc=0; nc<nPlotCategories; nc++) histo[nc] = NULL;
  TH1F* histo_total = NULL;

  for(int nc=0; nc<nPlotCategories; nc++) {
    if((TH1F*)fileInput->Get(Form("%s/histo_%s",subFoldersName.Data(), plotBaseNames[nc].Data()))){
      histo[nc] = (TH1F*)fileInput->Get(Form("%s/histo_%s",subFoldersName.Data(), plotBaseNames[nc].Data()));
      histo[nc]->SetNameTitle(Form("histo%d",nc),Form("histo%d",nc));
      histo[nc]->SetDirectory(0);
    }
  }

  if((TH1F*)fileInput->Get(Form("%s/histo_%s",subFoldersName.Data(), "total"))){
    histo_total = (TH1F*)fileInput->Get(Form("%s/histo_%s",subFoldersName.Data(), "total"));
    histo_total->SetNameTitle(Form("histo_total"),Form("histo_total"));
    histo_total->SetDirectory(0);
    for(int i=1; i<=histo_total->GetNbinsX(); i++) if(isModify == true && inputSampleName.Contains("prefit") == false) histo_total->SetBinError(i,1.5*histo_total->GetBinError(i));
    for(int i=1; i<=histo_total->GetNbinsX(); i++){
      if(i == histo_total->GetNbinsX() || isModify == false) continue;
      if(histo_total->GetBinContent(i) > 0 && histo_total->GetBinContent(i+1) > 0){
        //printf("%d %f %f %f -- ",0,histo_total->GetBinError(i+1),histo_total->GetBinContent(i+1),histo_total->GetBinError(i+1)/histo_total->GetBinContent(i+1));
        if(histo_total->GetBinError(i+1)/histo_total->GetBinContent(i+1) > 
         2*histo_total->GetBinError(i)/histo_total->GetBinContent(i))
           histo_total->SetBinError(i+1,histo_total->GetBinContent(i+1)*histo_total->GetBinError(i)/histo_total->GetBinContent(i));
        //printf("%d %f %f %f\n",0,histo_total->GetBinError(i+1),histo_total->GetBinContent(i+1),histo_total->GetBinError(i+1)/histo_total->GetBinContent(i+1));
      }
    }
  }

  // Special for Data
  if((TH1F*)fileInput->Get(Form("%s/histo_%s",subFoldersName.Data(), "total"))){
    histo[kPlotData] = (TH1F*)fileInput->Get(Form("%s/histo_%s",subFoldersName.Data(), "DATA"));
    histo[kPlotData]->SetNameTitle(Form("histo%d",kPlotData),Form("histo%d",kPlotData));
    histo[kPlotData]->SetDirectory(0);
  }
  // Special for NonPromptWZ
  if     ((TH1F*)fileInput->Get(Form("%s/histo_%s",subFoldersName.Data(), "NonPromptWZ"))){
    histo[kPlotNonPrompt] = (TH1F*)fileInput->Get(Form("%s/histo_%s",subFoldersName.Data(), "NonPromptWZ"));
    histo[kPlotNonPrompt]->SetNameTitle(Form("histo%d",kPlotNonPrompt),Form("histo%d",kPlotNonPrompt));
    histo[kPlotNonPrompt]->SetDirectory(0);
  }
  else if((TH1F*)fileInput->Get(Form("%s/histo_%s",subFoldersName.Data(), "NonWZPrompt"))){
    histo[kPlotNonPrompt] = (TH1F*)fileInput->Get(Form("%s/histo_%s",subFoldersName.Data(), "NonWZPrompt"));
    histo[kPlotNonPrompt]->SetNameTitle(Form("histo%d",kPlotNonPrompt),Form("histo%d",kPlotNonPrompt));
    histo[kPlotNonPrompt]->SetDirectory(0);
  }

  int whichBin = -1;
  double whichWeight = 1.0;
  if     (outputSampleName == "ww_output_bin0.root"){
    whichBin = 5;
    whichWeight = 1;//712./744.;
  }
  else if(outputSampleName == "ww_output_bin2.root"){
    whichBin = 2;
    whichWeight = 1;//4175./4043.;
  }
  else if(outputSampleName == "ww_output_bin3.root"){
    whichBin = 2;
    whichWeight = 1;//1371./1363.;
  }

  if(whichBin != -1) printf("APPLYING SPECIAL WEIGHTS! %d / %f\n",whichBin,whichWeight);

  TFile fileOutput(outputSampleName.Data(),"RECREATE");
  fileOutput.cd();
  for(int nc=0; nc<nPlotCategories; nc++) {
    if(!histo[nc]) continue;
    for(int i=1; i<=histo[nc]->GetNbinsX(); i++) {
      if(i != whichBin || nc == kPlotData) continue;
      histo[nc]->SetBinContent(i,whichWeight*histo[nc]->GetBinContent(i));
    }
    histo[nc]->Write();
  }
  if(histo_total) {
    for(int i=1; i<=histo_total->GetNbinsX(); i++) {
      if(i != whichBin) continue;
      histo_total->SetBinContent(i,whichWeight*histo_total->GetBinContent(i));
    }
    histo_total->Write();
  }
  fileOutput.Close();
}
//root -q -b -l ~/cms/MitAnalysisRunIII/rdf/makePlots/finalPlot.C+'(0,1,"X","Y","output.root","mva",0,2019,"",1.0,0,"",1,"","","")';
