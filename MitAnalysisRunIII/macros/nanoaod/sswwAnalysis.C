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

#include "TMVA/Reader.h"
#include "nanoAOD.C"
#include "nanoAODRun.C"

const int nPlotCategories = 1;

void sswwAnalysis(
int year = 2016
){
  TString filesPath;
  vector<TString> infileName_;
  vector<int> infileCat_;  
  if     (year == 2016) {
    filesPath = Form("/afs/cern.ch/work/c/ceballos/public/samples/nanoaod/");
    infileName_.push_back(Form("%sWpWpJJ_EWK_TuneCP5_13TeV-madgraph-pythia8.root" ,filesPath.Data())); infileCat_.push_back(0);
  }

  int nBinPlot      = 200;
  double xminPlot   = 0.0;
  double xmaxPlot   = 200.0;
  const int allPlots = 5;
  TH1D* histo[allPlots][1];
  for(int thePlot=0; thePlot<allPlots; thePlot++){
    if     (thePlot >=   0 && thePlot <=   0) {nBinPlot = 3; xminPlot = -0.5; xmaxPlot = 2.5;}
    else if(thePlot >=   1 && thePlot <=   1) {nBinPlot = 10; xminPlot = -0.5; xmaxPlot = 9.5;}
    if     (thePlot >=   0 && thePlot <=   4) for(int i=0; i<nPlotCategories; i++) histo[thePlot][i] = new TH1D(Form("histo_%d_%d",thePlot,i), Form("histo_%d_%d",thePlot,i), nBinPlot, xminPlot, xmaxPlot);
  }

  for(UInt_t ifile=0; ifile<infileName_.size(); ifile++) {
    printf("sampleNames(%d): %s\n",ifile,infileName_[ifile].Data());
    TFile *the_input_file = TFile::Open(infileName_[ifile].Data());
    TTree *the_input_tree = (TTree*)the_input_file->FindObjectAny("Events");
    TTree *the_input_treeRun = (TTree*)the_input_file->FindObjectAny("Runs");

    nanoAODRun thePandaRun(the_input_treeRun);
    Long64_t nentriesRun = thePandaRun.fChain->GetEntriesFast();
    thePandaRun.LoadTree(0);
    thePandaRun.fChain->GetEntry(0);
    double allEventsWeight = thePandaRun.genEventSumw;

    nanoAOD thePandaFlat(the_input_tree);
    double theMCPrescale = 1.0;
    Long64_t nentries = thePandaFlat.fChain->GetEntriesFast();
    Long64_t nbytes = 0, nb = 0;
    for (Long64_t jentry=0; jentry<nentries;jentry++) {
      Long64_t ientry = thePandaFlat.LoadTree(jentry);
      if (ientry < 0) break;
      nb = thePandaFlat.fChain->GetEntry(jentry);   nbytes += nb;
      if (jentry%100000 == 0) printf("--- reading event %8lld (%8lld) of %8lld\n",jentry,ientry,nentries);

      vector<TLorentzVector> vLoose;
      vector<bool> looseLepSelBit;
      vector<int> looseLepPdgId;
      int ptSelCuts[3] = {0,0,0};
      for(unsigned int i=0; i<thePandaFlat.nMuon; i++){
        if(!thePandaFlat.Muon_tightId[i]) continue;
        if(thePandaFlat.Muon_pfRelIso03_all[i] >= 0.15) continue;
        if(thePandaFlat.Muon_pt[i] <= 10) continue;
        TLorentzVector vLepTemp; vLepTemp.SetPtEtaPhiM(thePandaFlat.Muon_pt[i],thePandaFlat.Muon_eta[i],thePandaFlat.Muon_phi[i],0.1000);
        vLoose.push_back(vLepTemp);
        looseLepSelBit.push_back(thePandaFlat.Muon_looseId[i]);
        looseLepPdgId.push_back(thePandaFlat.Muon_charge[i]*13);
	if(vLoose[vLoose.size()-1].Pt() > 25) ptSelCuts[0]++;
	if(vLoose[vLoose.size()-1].Pt() > 20) ptSelCuts[1]++;
	if(vLoose[vLoose.size()-1].Pt() > 10) ptSelCuts[2]++;
      }
      for(unsigned int i=0; i<thePandaFlat.nElectron; i++){
        if(thePandaFlat.Electron_pt[i] <= 10) continue;
        if(!thePandaFlat.Electron_mvaFall17V2Iso_WP80[i]) continue;
        if(thePandaFlat.Electron_tightCharge[i] != 2) continue;
        TLorentzVector vLepTemp; vLepTemp.SetPtEtaPhiM(thePandaFlat.Electron_pt[i],thePandaFlat.Electron_eta[i],thePandaFlat.Electron_phi[i],0.0005);
        vLoose.push_back(vLepTemp);
        looseLepSelBit.push_back(1);
        looseLepPdgId.push_back(thePandaFlat.Electron_charge[i]*11);
	if(vLoose[vLoose.size()-1].Pt() > 25) ptSelCuts[0]++;
	if(vLoose[vLoose.size()-1].Pt() > 20) ptSelCuts[1]++;
	if(vLoose[vLoose.size()-1].Pt() > 10) ptSelCuts[2]++;
      }

      double totalWeight = thePandaFlat.genWeight * 0.0269642 * 60000. / allEventsWeight;
      histo[1][0]->Fill(0.0,totalWeight);
      if(!(ptSelCuts[0] >= 1 && ptSelCuts[1] >= 2 && vLoose.size() == 2 && looseLepPdgId[0]*looseLepPdgId[1] > 0)) continue;

      bool isBtagged = false;
      vector<TLorentzVector> vJet;
      for(unsigned int i=0; i<thePandaFlat.nJet; i++){
        if(thePandaFlat.Jet_jetId[i] != 6) continue;
        if(thePandaFlat.Jet_pt[i] > 20 && thePandaFlat.Jet_btagDeepB[i] > 0.4184) isBtagged = true;
        if(thePandaFlat.Jet_pt[i] <= 50) continue;
        TLorentzVector vJetTemp; vJetTemp.SetPtEtaPhiM(thePandaFlat.Jet_pt[i],thePandaFlat.Jet_eta[i],thePandaFlat.Jet_phi[i],0.0);
        double dRMin = 999;
        for(unsigned int i=0; i<vLoose.size(); i++) {
          double dRMinAux = TMath::Sqrt(
                            TMath::Abs(vLoose[i].Eta()-vJetTemp.Eta()) * TMath::Abs(vLoose[i].Eta()-vJetTemp.Eta()) +
                            vLoose[i].DeltaPhi(vJetTemp) * vLoose[i].DeltaPhi(vJetTemp));
          if(dRMinAux < dRMin) dRMin = dRMinAux;
        }
        if(dRMin < 0.4) continue;
        vJet.push_back(vJetTemp);
      }

      histo[1][0]->Fill(1.0,totalWeight);
      if(vJet.size() < 2) continue;

      double massJJ     = (vJet[0]+vJet[1]).M();
      double deltaEtaJJ = TMath::Abs(vJet[0].Eta()-vJet[1].Eta());

      histo[1][0]->Fill(2.0,totalWeight);
      if(deltaEtaJJ < 2.5) continue;

      histo[1][0]->Fill(3.0,totalWeight);
      if(massJJ <= 500) continue;

      double maxLeptonZep = 0;
      for(unsigned int i=0; i<vLoose.size(); i++) {
        if(TMath::Abs(vLoose[i].Eta()-(vJet[0].Eta()+vJet[1].Eta())/2.)/deltaEtaJJ > maxLeptonZep)
          maxLeptonZep = TMath::Abs(vLoose[i].Eta()-(vJet[0].Eta()+vJet[1].Eta())/2.)/deltaEtaJJ;
      }

      histo[1][0]->Fill(4.0,totalWeight);
      if(maxLeptonZep >= 0.75) continue;

      histo[1][0]->Fill(5.0,totalWeight);
      if(isBtagged == true) continue;

      histo[1][0]->Fill(6.0,totalWeight);
      if(thePandaFlat.MET_pt <= 30) continue;

      histo[1][0]->Fill(7.0,totalWeight);
      if((vLoose[0]+vLoose[1]).M() <= 20) continue;

      int lepType = -1;
      if     (vLoose.size() == 2){
        if     (abs(looseLepPdgId[0])==13 && abs(looseLepPdgId[1])==13) {lepType = 0;}
        else if(abs(looseLepPdgId[0])==11 && abs(looseLepPdgId[1])==11) {lepType = 1;}
        else  {lepType = 2;}
      }

      histo[1][0]->Fill(8.0,totalWeight);
      if(lepType == 1 && TMath::Abs((vLoose[0]+vLoose[1]).M()-91.1876) <= 15) continue;


      histo[1][0]->Fill(9.0,totalWeight);
      histo[0][0]->Fill(TMath::Min((double)lepType,6.4999),totalWeight);

    }
  }

  printf("(%.1f)",histo[0][0]->GetSumOfWeights());
  for(int nb=1; nb<=histo[0][0]->GetNbinsX(); nb++) printf(" %.1f",histo[0][0]->GetBinContent(nb));
  printf("\n");

  printf("(%.1f)",histo[1][0]->GetSumOfWeights());
  for(int nb=1; nb<=histo[1][0]->GetNbinsX(); nb++) printf(" %.1f",histo[1][0]->GetBinContent(nb));
  printf("\n");
}
