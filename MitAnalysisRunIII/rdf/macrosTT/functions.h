#include "TROOT.h"
#include "TFile.h"
#include "TH1.h"
#include "TF2.h"
#include "TString.h"
#include "TRandom.h"
#include "TRandom3.h"
#include "TSpline.h"
#include "TCanvas.h"
#include "TGraphAsymmErrors.h"
#include "TLorentzVector.h"
#include "TEfficiency.h"
#include "TVector2.h"
#include "Math/GenVector/LorentzVector.h"
#include "Math/GenVector/PtEtaPhiM4D.h"
#include "Math/GenVector/PxPyPzM4D.h"

#include "mysf.h"

#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <cstdlib>
#include <cstdio>
#include <cmath>
#include <array>
#include <string>
#include <vector>
#include <unordered_map>
#include <utility>
#include <algorithm>
#include <limits>
#include <map>

#include <ROOT/RVec.hxx>
#include <ROOT/RDataFrame.hxx>

using Vec_b = ROOT::VecOps::RVec<bool>;
using Vec_d = ROOT::VecOps::RVec<double>;
using Vec_f = ROOT::VecOps::RVec<float>;
using Vec_i = ROOT::VecOps::RVec<int>;
using Vec_ui = ROOT::VecOps::RVec<unsigned int>;

typedef ROOT::Math::LorentzVector<ROOT::Math::PtEtaPhiM4D<double> > PtEtaPhiMVector;
typedef ROOT::Math::LorentzVector<ROOT::Math::PxPyPzM4D<double> > PxPyPzMVector;
std::unordered_map< UInt_t, std::vector< std::pair<UInt_t,UInt_t> > > jsonMap;

TH2D histoFakeEtaPt_mu[9];
TH2D histoFakeEtaPt_el[9];
TH2D histoLepSFEtaPt_mu;
TH2D histoLepSFEtaPt_el;
TH2D histoTriggerSFEtaPt_0_0;
TH2D histoTriggerSFEtaPt_0_1;
TH2D histoTriggerSFEtaPt_0_2;
TH2D histoTriggerSFEtaPt_0_3;
TH2D histoTriggerSFEtaPt_1_0;
TH2D histoTriggerSFEtaPt_1_1;
TH2D histoTriggerSFEtaPt_1_2;
TH2D histoTriggerSFEtaPt_1_3;
TH2D histoTriggerSFEtaPt_2_0;
TH2D histoTriggerSFEtaPt_2_1;
TH2D histoTriggerSFEtaPt_2_2;
TH2D histoTriggerSFEtaPt_2_3;
TH2D histoTriggerSFEtaPt_3_0;
TH2D histoTriggerSFEtaPt_3_1;
TH2D histoTriggerSFEtaPt_3_2;
TH2D histoTriggerSFEtaPt_3_3;
TH2D histoBTVEffEtaPtLF;
TH2D histoBTVEffEtaPtCJ;
TH2D histoBTVEffEtaPtBJ;
TH1D puWeights;
TH1D puWeightsUp;
TH1D puWeightsDown;
TH1D histo_wwpt;
TH1D histo_wwpt_scaleup;
TH1D histo_wwpt_scaledown;
TH1D histo_wwpt_resumup;
TH1D histo_wwpt_resumdown;
TH1D histoWSEtaSF;
TH1D histoWSEtaSF_unc;
TH2D histoWSEtaPtSF;
TH2D histoTriggerDAEtaPt[10];
TH2D histoTriggerMCEtaPt[10];
TH1D hVV_KF_EWK[2]; // 0 (WW), 1 (WZ)
TH1D hVV_KF_EWK_unc[2]; // 0 (WW), 1 (WZ)
auto corrSFs = MyCorrections(2018);

void initHisto2D(TH2D h, int nsel){
  if     (nsel ==  0) histoFakeEtaPt_mu[0] = h;
  else if(nsel ==  1) histoFakeEtaPt_el[0] = h;
  else if(nsel ==  2) histoLepSFEtaPt_mu = h;
  else if(nsel ==  3) histoLepSFEtaPt_el = h;
  else if(nsel ==  4) histoTriggerSFEtaPt_0_0 = h;
  else if(nsel ==  5) histoTriggerSFEtaPt_0_1 = h;
  else if(nsel ==  6) histoTriggerSFEtaPt_0_2 = h;
  else if(nsel ==  7) histoTriggerSFEtaPt_0_3 = h;
  else if(nsel ==  8) histoTriggerSFEtaPt_1_0 = h;
  else if(nsel ==  9) histoTriggerSFEtaPt_1_1 = h;
  else if(nsel == 10) histoTriggerSFEtaPt_1_2 = h;
  else if(nsel == 11) histoTriggerSFEtaPt_1_3 = h;
  else if(nsel == 12) histoTriggerSFEtaPt_2_0 = h;
  else if(nsel == 13) histoTriggerSFEtaPt_2_1 = h;
  else if(nsel == 14) histoTriggerSFEtaPt_2_2 = h;
  else if(nsel == 15) histoTriggerSFEtaPt_2_3 = h;
  else if(nsel == 16) histoTriggerSFEtaPt_3_0 = h;
  else if(nsel == 17) histoTriggerSFEtaPt_3_1 = h;
  else if(nsel == 18) histoTriggerSFEtaPt_3_2 = h;
  else if(nsel == 19) histoTriggerSFEtaPt_3_3 = h;
  else if(nsel == 20) histoBTVEffEtaPtLF = h;
  else if(nsel == 21) histoBTVEffEtaPtCJ = h;
  else if(nsel == 22) histoBTVEffEtaPtBJ = h;
  else if(nsel == 23) histoFakeEtaPt_mu[1] = h;
  else if(nsel == 24) histoFakeEtaPt_mu[2] = h;
  else if(nsel == 25) histoFakeEtaPt_mu[3] = h;
  else if(nsel == 26) histoFakeEtaPt_mu[4] = h;
  else if(nsel == 27) histoFakeEtaPt_mu[5] = h;
  else if(nsel == 28) histoFakeEtaPt_mu[6] = h;
  else if(nsel == 29) histoFakeEtaPt_mu[7] = h;
  else if(nsel == 30) histoFakeEtaPt_mu[8] = h;
  else if(nsel == 31) histoFakeEtaPt_el[1] = h;
  else if(nsel == 32) histoFakeEtaPt_el[2] = h;
  else if(nsel == 33) histoFakeEtaPt_el[3] = h;
  else if(nsel == 34) histoFakeEtaPt_el[4] = h;
  else if(nsel == 35) histoFakeEtaPt_el[5] = h;
  else if(nsel == 36) histoFakeEtaPt_el[6] = h;
  else if(nsel == 37) histoFakeEtaPt_el[7] = h;
  else if(nsel == 38) histoFakeEtaPt_el[8] = h;
  else if(nsel == 39) histoWSEtaPtSF = h;
  else if(nsel == 40) histoTriggerDAEtaPt[0] = h;
  else if(nsel == 41) histoTriggerDAEtaPt[1] = h;
  else if(nsel == 42) histoTriggerDAEtaPt[2] = h;
  else if(nsel == 43) histoTriggerDAEtaPt[3] = h;
  else if(nsel == 44) histoTriggerDAEtaPt[4] = h;
  else if(nsel == 45) histoTriggerDAEtaPt[5] = h;
  else if(nsel == 46) histoTriggerDAEtaPt[6] = h;
  else if(nsel == 47) histoTriggerDAEtaPt[7] = h;
  else if(nsel == 48) histoTriggerDAEtaPt[8] = h;
  else if(nsel == 49) histoTriggerDAEtaPt[9] = h;
  else if(nsel == 50) histoTriggerMCEtaPt[0] = h;
  else if(nsel == 51) histoTriggerMCEtaPt[1] = h;
  else if(nsel == 52) histoTriggerMCEtaPt[2] = h;
  else if(nsel == 53) histoTriggerMCEtaPt[3] = h;
  else if(nsel == 54) histoTriggerMCEtaPt[4] = h;
  else if(nsel == 55) histoTriggerMCEtaPt[5] = h;
  else if(nsel == 56) histoTriggerMCEtaPt[6] = h;
  else if(nsel == 57) histoTriggerMCEtaPt[7] = h;
  else if(nsel == 58) histoTriggerMCEtaPt[8] = h;
  else if(nsel == 59) histoTriggerMCEtaPt[9] = h;
}

void initHisto1D(TH1D h, int nsel){
  if     (nsel ==  0) puWeights = h;
  else if(nsel ==  1) puWeightsUp = h;
  else if(nsel ==  2) puWeightsDown = h;
  else if(nsel ==  3) histo_wwpt = h;
  else if(nsel ==  4) histo_wwpt_scaleup = h;
  else if(nsel ==  5) histo_wwpt_scaledown = h;
  else if(nsel ==  6) histo_wwpt_resumup = h;
  else if(nsel ==  7) histo_wwpt_resumdown = h;
  else if(nsel ==  8) histoWSEtaSF = h;
  else if(nsel ==  9) histoWSEtaSF_unc = h;
  else if(nsel == 10) hVV_KF_EWK[0] = h;
  else if(nsel == 11) hVV_KF_EWK[1] = h;
  else if(nsel == 12) hVV_KF_EWK_unc[0] = h;
  else if(nsel == 13) hVV_KF_EWK_unc[1] = h;
}

float getValFromTH1(const TH1& h, const float& x, const float& sumError=0.0) {
  int xbin = std::max(1, std::min(h.GetNbinsX(), h.GetXaxis()->FindFixBin(x)));
  if (sumError)
    return h.GetBinContent(xbin) + sumError * h.GetBinError(xbin);
  else
    return h.GetBinContent(xbin);
}

float getValFromTH2(const TH2& h, const float& x, const float& y, const float& sumError=0.0) {
  //std::cout << "x,y --> " << x << "," << y << std::endl;
  int xbin = std::max(1, std::min(h.GetNbinsX(), h.GetXaxis()->FindFixBin(x)));
  int ybin = std::max(1, std::min(h.GetNbinsY(), h.GetYaxis()->FindFixBin(y)));
  //std::cout << "xbin,ybin --> " << xbin << "," << ybin << std::endl;
  if (sumError)
    return h.GetBinContent(xbin, ybin) + sumError * h.GetBinError(xbin, ybin);
  else
    return h.GetBinContent(xbin, ybin);
}

void initJSONSFs(int year){
  corrSFs = MyCorrections(year);
}

// PUJetID SFs
float compute_JSONS_PUJetID_SF(Vec_f jet_pt, Vec_f jet_eta, unsigned int sel)
{
  //printf("pujetidsf: %lu %lu %d\n",jet_pt.size(),jet_eta.size(),sel);
  double sfTot = 1.0;
  char *valType = (char*)"T";
  if     (sel == 0) {valType = (char*)"T";}
  else if(sel == 1) {valType = (char*)"M";}
  else if(sel == 2) {valType = (char*)"L";}
  for(unsigned int i=0;i<jet_pt.size();i++) {
    if(jet_pt[i] <= 30 || fabs(jet_eta[i]) >= 5.0) continue;
    double sf = corrSFs.eval_puJetIDSF((char*)"nom",valType,jet_eta[i],min(jet_pt[i],999.999f));
    sfTot *= sf;
    //printf("pujetidsf(%d) %.3f %.3f %.3f %.3f\n",i,jet_pt[i],jet_eta[i],sfTot,sf);
  }
  return sfTot;
}

// JetSel Veto
Vec_b cleaningJetSelMask(unsigned int sel, Vec_f jet_eta, Vec_f jet_chHEF, Vec_f jet_neHEF, Vec_f jet_chEmEF, Vec_f jet_neEmEF, Vec_f jet_muEF, Vec_f jet_chMultiplicity, Vec_f jet_neMultiplicity, Vec_ui jet_jetId, int year){

  Vec_b jet_Sel_mask(jet_eta.size(), true);
  bool debug = false;
  if(debug) printf("seljetID: %lu %d\n",jet_eta.size(),sel);
  float result = 0.0;

  for(unsigned int i=0;i<jet_eta.size();i++) {
    if(year >= 20240) {
      result = corrSFs.eval_jetSel(sel, jet_eta[i], jet_chHEF[i], jet_neHEF[i], jet_chEmEF[i], jet_neEmEF[i], jet_muEF[i], jet_chMultiplicity[i], jet_neMultiplicity[i]);

      if(debug) {
        float resultTest = 0.0;
        if(sel >= 0){
          bool jet_passJetIdTight = false;
          if      (abs(jet_eta[i]) <= 2.6) jet_passJetIdTight = (jet_neHEF[i] < 0.99) && (jet_neEmEF[i] < 0.9) && (jet_chMultiplicity[i]+jet_neMultiplicity[i] > 1) && (jet_chHEF[i] > 0.01) && (jet_chMultiplicity[i] > 0);
          else if (abs(jet_eta[i]) > 2.6 && abs(jet_eta[i]) <= 2.7) jet_passJetIdTight = (jet_neHEF[i] < 0.90) && (jet_neEmEF[i] < 0.99);
          else if (abs(jet_eta[i]) > 2.7 && abs(jet_eta[i]) < 3.0) jet_passJetIdTight = (jet_neHEF[i] < 0.99);
          else if (abs(jet_eta[i]) >= 3.0) jet_passJetIdTight = (jet_neMultiplicity[i] >= 2) && (jet_neEmEF[i] < 0.4);
          if(jet_passJetIdTight == true) resultTest = 1.0;

          if(sel == 1) {
            bool jet_passJetIdTightLepVeto = false;
            if (abs(jet_eta[i]) <= 2.7) jet_passJetIdTightLepVeto = jet_passJetIdTight && (jet_muEF[i] < 0.8) && (jet_chEmEF[i] < 0.8);
            else jet_passJetIdTightLepVeto = jet_passJetIdTight;
            if(jet_passJetIdTightLepVeto == true) resultTest = 1.0;
          } // sel == 1
          if(result != resultTest) printf("Different jetID results! %f / %f\n",result,resultTest);
        } // sel == 0 / 1
      } // debug == true
    }
    else {
      result = 0.0;
      if(sel >= 0){
        bool jet_passJetIdTight = false;
        if      (abs(jet_eta[i]) <= 2.7) jet_passJetIdTight = jet_jetId[i] & (1 << 1);
        else if (abs(jet_eta[i]) > 2.7 && abs(jet_eta[i]) <= 3.0) jet_passJetIdTight = (jet_jetId[i] & (1 << 1)) && (jet_neHEF[i] < 0.99);
        else if (abs(jet_eta[i]) > 3.0) jet_passJetIdTight = (jet_jetId[i] & (1 << 1)) && (jet_neEmEF[i] < 0.4);

        if(sel == 0 && jet_passJetIdTight == true) result = 1.0;

        if(sel == 1) {
          bool jet_passJetIdTightLepVeto = false;
          if (abs(jet_eta[i]) <= 2.7) jet_passJetIdTightLepVeto = jet_passJetIdTight && (jet_muEF[i] < 0.8) && (jet_chEmEF[i] < 0.8);
          else jet_passJetIdTightLepVeto = jet_passJetIdTight;

          if(jet_passJetIdTightLepVeto == true) result = 1.0;
        } // sel == 1
      } // sel == 0 / 1
    }

    if(result == 0) jet_Sel_mask[i] = false;
    if(debug) printf("seljetID(%d/%d): %.1f / %.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f\n",i, sel, result, jet_eta[i], jet_chHEF[i], jet_neHEF[i], jet_chEmEF[i], jet_neEmEF[i], jet_muEF[i], jet_chMultiplicity[i], jet_neMultiplicity[i]);
  }

  return jet_Sel_mask;
}

float compute_JSON_PU_SF(double NumTrueInteractions, std::string type){
  bool debug = false;
  double sf = corrSFs.eval_puSF(std::min((float)NumTrueInteractions,74.999f),type);
  if(debug) printf("pusf(%s): %f / %f\n",type.c_str(),NumTrueInteractions,sf);
  return sf;
}

// BTag SFs
float compute_JSON_BTV_SF(Vec_f jet_pt, Vec_f jet_eta, Vec_f jet_btag, Vec_i jet_flavor, std::string keyS, int flavorToStudy, const int sel, const float bcut)
{
  // flavorToStudy = 0 (central) / > 0 (BC) / < 0 (LF)
  bool debug = false;
  if(debug) printf("btagsf(%s): %lu %lu %lu %lu %d %d\n",keyS.c_str(),jet_pt.size(),jet_eta.size(),jet_btag.size(),jet_flavor.size(),flavorToStudy,sel);
  double sfTot[2] = {1.0, 1.0};
  const char *key = keyS.c_str();
  char *valType = (char*)"T";
  if     (sel == 0) {valType = (char*)"T";}
  else if(sel == 1) {valType = (char*)"M";}
  else if(sel == 2) {valType = (char*)"L";}
  for(unsigned int i=0;i<jet_pt.size();i++) {
    if(jet_flavor[i] != 0 && jet_flavor[i] != 4 && jet_flavor[i] != 5) continue;
    if(jet_pt[i] <= 20 || fabs(jet_eta[i]) >= 2.5) continue;
    double sf = 1.0;
    if     (flavorToStudy == 0) sf = corrSFs.eval_btvSF((char*)"central",valType,abs(jet_eta[i]),min(jet_pt[i],999.999f),jet_flavor[i]);
    else if(flavorToStudy > 0 && 
            jet_flavor[i] != 0) sf = corrSFs.eval_btvSF(key,valType,abs(jet_eta[i]),min(jet_pt[i],999.999f),jet_flavor[i]);
    else if(flavorToStudy > 0 && 
            jet_flavor[i] == 0) sf = corrSFs.eval_btvSF((char*)"central",valType,abs(jet_eta[i]),min(jet_pt[i],999.999f),jet_flavor[i]);
    else if(flavorToStudy < 0 && 
            jet_flavor[i] != 0) sf = corrSFs.eval_btvSF((char*)"central",valType,abs(jet_eta[i]),min(jet_pt[i],999.999f),jet_flavor[i]);
    else if(flavorToStudy < 0 && 
            jet_flavor[i] == 0) sf = corrSFs.eval_btvSF(key,valType,abs(jet_eta[i]),min(jet_pt[i],999.999f),jet_flavor[i]);
    else printf("btag flavorToStudy no possible\n");

    double eff = 1;
    if     (jet_flavor[i] == 0) {const TH2D& hcorr0 = histoBTVEffEtaPtLF; eff = getValFromTH2(hcorr0, fabs(jet_eta[i]),min(jet_pt[i],999.999f));}
    else if(jet_flavor[i] == 4) {const TH2D& hcorr1 = histoBTVEffEtaPtCJ; eff = getValFromTH2(hcorr1, fabs(jet_eta[i]),min(jet_pt[i],999.999f));}
    else if(jet_flavor[i] == 5) {const TH2D& hcorr2 = histoBTVEffEtaPtBJ; eff = getValFromTH2(hcorr2, fabs(jet_eta[i]),min(jet_pt[i],999.999f));}
    if(jet_btag[i] > bcut) {
      sfTot[0] *= sf * eff; sfTot[1] *= eff;
    }
    else {
      sfTot[0] *= (1.0 - sf * eff); sfTot[1] *= (1.0 - eff);
    }
    if(debug) {
      printf("btagsf(%d) %.3f %.3f %d %d %.3f %.3f %.3f %.3f --> ",i,jet_pt[i],jet_eta[i],jet_flavor[i],jet_btag[i] > bcut,sfTot[0],sfTot[1],sf,eff);
      if(sfTot[1] > 0) printf("%.3f\n",sfTot[0]/sfTot[1]); else printf("1.0\n");
    }
  }

  if(sfTot[1] > 0) return sfTot[0]/sfTot[1];
  return 1.0;
}

float compute_JSON_MUO_SFs(std::string valType0S, std::string valType1S, std::string valType2S, 
                           const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_f& mu_p, const double type){
  if(mu_pt.size() == 0) return 1.0;
  bool debug = false;
  if(debug) printf("muoeff: %lu\n",mu_pt.size());
  double sfTot = 1.0;

  const char *valType0 = valType0S.c_str();
  const char *valType1 = valType1S.c_str();
  const char *valType2 = valType2S.c_str();

  for(unsigned int i=0;i<mu_pt.size();i++) {
    double sf0 = corrSFs.eval_muonTRKSF(mu_eta[i],mu_pt[i],mu_p[i],"nominal"); if(valType0S != "nominal") sf0 = sf0 + type * sqrt(TMath::Power(corrSFs.eval_muonTRKSF(mu_eta[i],mu_pt[i],mu_p[i],valType0),2)+TMath::Power(corrSFs.eval_muonTRKSF(mu_eta[i],mu_pt[i],mu_p[i],"stat"),2));
    double sf1 = corrSFs.eval_muonIDSF (mu_eta[i],mu_pt[i]        ,"nominal"); if(valType1S != "nominal") sf1 = sf1 + type * sqrt(TMath::Power(corrSFs.eval_muonIDSF (mu_eta[i],mu_pt[i]        ,valType1),2)+TMath::Power(corrSFs.eval_muonIDSF (mu_eta[i],mu_pt[i]        ,"stat"),2));
    double sf2 = corrSFs.eval_muonISOSF(mu_eta[i],mu_pt[i]        ,"nominal"); if(valType2S != "nominal") sf2 = sf2 + type * sqrt(TMath::Power(corrSFs.eval_muonISOSF(mu_eta[i],mu_pt[i]        ,valType2),2)+TMath::Power(corrSFs.eval_muonISOSF(mu_eta[i],mu_pt[i]        ,"stat"),2));
    sfTot = sfTot*sf0*sf1*sf2;
    if(debug) printf("muoeff(%d-%s/%s/%s) %.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f\n",i,valType0,valType1,valType2,mu_pt[i],mu_eta[i],mu_p[i],sf0,sf1,sf2,sf0*sf1*sf2,sfTot);
  }

  return sfTot;
}

float compute_JSON_ELE_SFs(std::string yearS, std::string valType0S, std::string valType1S, 
                           std::string workingPointS, const Vec_f& el_pt, const Vec_f& el_eta, const Vec_f& el_phi){
  if(el_pt.size() == 0) return 1.0;
  bool debug = false;
  if(debug) printf("eleeff: %lu\n",el_pt.size());
  double sfTot = 1.0;

  const char *year = yearS.c_str();
  const char *valType0 = valType0S.c_str();
  const char *valType1 = valType1S.c_str();
  const char *workingPoint = workingPointS.c_str();

  for(unsigned int i=0;i<el_pt.size();i++) {
    char *recoNameAux = (char*)"RecoAbove75";
    double pt_used = max(el_pt[i],20.001f);
    if     (pt_used < 20) recoNameAux = (char*)"RecoBelow20";
    else if(pt_used < 75) recoNameAux = (char*)"Reco20to75";
    const char *recoName = recoNameAux;
    double sf0 = corrSFs.eval_electronTRKSF(year,valType0,    recoName,el_eta[i],pt_used,el_phi[i]);
    double sf1 = corrSFs.eval_electronIDSF (year,valType1,workingPoint,el_eta[i],pt_used,el_phi[i]);
    sfTot = sfTot*sf0*sf1;
    if(debug) printf("eleff(%d-%s/%s) %.3f %.3f %.3f %.3f %.3f %.3f %.3f\n",i,valType0,valType1,el_pt[i],el_eta[i],el_phi[i],sf0,sf1,sf0*sf1,sfTot);
  }

  return sfTot;
}

float compute_JSON_PHO_SFs(std::string yearS, std::string valTypeS, std::string workingPointS,
                           const Vec_f& ph_pt, const Vec_f& ph_eta, const Vec_f& ph_phi){
  if(ph_pt.size() == 0) return 1.0;
  bool debug = false;
  if(debug) printf("phoeff: %lu\n",ph_pt.size());
  double sfTot = 1.0;

  const char *year = yearS.c_str();
  const char *valType = valTypeS.c_str();
  const char *workingPoint = workingPointS.c_str();

  for(unsigned int i=0;i<ph_pt.size();i++) {
    double sf = corrSFs.eval_photonSF(year,valType,workingPoint,ph_eta[i],ph_pt[i],ph_phi[i]);
    sfTot = sfTot*sf;
    if(debug) printf("phoeff(%d) %.3f %.3f %.3f %.3f %.3f\n",i,ph_pt[i],ph_eta[i],ph_phi[i],sf,sfTot);
  }

  return sfTot;
}

float compute_JSON_TAU_SFs(const Vec_f& tau_pt, const Vec_f& tau_eta, const Vec_i& tau_dm, const Vec_i& tau_gen, std::string valTypeS){
  if(tau_pt.size() == 0) return 1.0;
  bool debug = false;
  if(debug) printf("taueff: %lu\n",tau_pt.size());
  double sfTot = 1.0;

  const char *valType = valTypeS.c_str();

  for(unsigned int i=0;i<tau_pt.size();i++) {
    double sf0 = corrSFs.eval_tauJETSF(tau_pt[i],tau_dm[i],tau_gen[i],"Tight","Tight",valType);
    double sf1 = 1.0;
    double sf2 = 1.0;
    sfTot = sfTot*sf0*sf1*sf2;
    if(debug) printf("taueff(%d) %.3f %.3f %2d %2d %.3f %.3f %.3f %.3f %.3f\n",i,tau_pt[i],tau_eta[i],tau_dm[i],tau_gen[i],sf0,sf1,sf2,sf0*sf1*sf2,sfTot);
  }

  return sfTot;
}

Vec_f compute_JSON_JES_Unc(const Vec_f& jet_pt, const Vec_f& jet_eta, const Vec_f& jet_phi, const Vec_f& jet_rawFactor, const Vec_f& jet_area, const double rho, const int run, int type, int jetTypeCorr){
  // jetTypeCorr == -1 (MC) 0/1/2/... A/B/C/... (DATA)
  bool debug = false;
  if(debug) printf("jes: %lu %f %d\n",jet_pt.size(),rho,type);
  Vec_f new_jet_pt(jet_pt.size(), 1.0);

  for (unsigned int idx = 0; idx < jet_pt.size(); ++idx) {
    if     (type ==  0) {
      double sf = corrSFs.eval_jetCORR(jet_area[idx], jet_eta[idx], jet_phi[idx], jet_pt[idx]*(1-jet_rawFactor[idx]), rho, run, jetTypeCorr);
      new_jet_pt[idx] = jet_pt[idx] * (1-jet_rawFactor[idx]) * sf;
      if(debug) printf("jes(%d): %.3f %.3f %.3f %.3f %.3f %.3f %.3f\n",idx,jet_area[idx],jet_eta[idx],jet_pt[idx]*(1-jet_rawFactor[idx]), jet_pt[idx],1./(1-jet_rawFactor[idx]),sf,new_jet_pt[idx]);
    }
    else {
      double unc = corrSFs.eval_jesUnc(jet_eta[idx], jet_pt[idx], abs(type)-1);
      int sign = type/abs(type);
      new_jet_pt[idx] = jet_pt[idx] * (1.0+sign*unc);
      if(debug) printf("jes(%d): %.3f %.3f %.3f %.3f\n",idx,jet_pt[idx],jet_eta[idx],unc,new_jet_pt[idx]);
    }
  }

  return new_jet_pt;
}

Vec_f compute_JSON_JER_Unc(const Vec_f& jet_pt, const Vec_f& jet_eta, const Vec_i& jet_genJetIdx, const Vec_f& GenJet_pt, const double rho, int type){
  bool debug = false;
  if(debug) printf("jer: %lu %f %d\n",jet_pt.size(),rho,type);
  Vec_f new_jet_pt(jet_pt.size(), 1.0);

  for (unsigned int idx = 0; idx < jet_pt.size(); ++idx) {
    double s_jer = corrSFs.eval_jerScaleFactor(jet_eta[idx], jet_pt[idx], type);
    double pt_res_gen = corrSFs.eval_jerPtResolution(jet_eta[idx], jet_pt[idx], rho);
    double pt_diff_rel = 100.0;
    double sf = 1.0;

    bool isMatchedJet = false;
    if(jet_genJetIdx[idx] >= 0 && GenJet_pt.size() > (unsigned)jet_genJetIdx[idx]) {
      pt_diff_rel = (jet_pt[idx]-GenJet_pt[jet_genJetIdx[idx]])/jet_pt[idx];
      double maxSigmaPtRel = 3;
      if(pt_diff_rel < maxSigmaPtRel*pt_res_gen){
          isMatchedJet = true;
          sf = max(1.0 + (s_jer-1.0)*pt_diff_rel, 0.0);
      }
    } // gen matched jets
    if(isMatchedJet == false && (fabs(jet_eta[idx]) < 2.5 || fabs(jet_eta[idx]) > 3.0)) {
      sf = max(1.0 + gRandom->Gaus(0.0,pt_res_gen) * sqrt(max(s_jer*s_jer-1.0, 0.0)), 0.0);
    }
    // new jet pt
    new_jet_pt[idx] = jet_pt[idx] * sf;
    if(debug) printf("jerScaleFactor(%d): %.3f %.3f %.3f / %.3f / %d %.3f %.3f / %.3f %.3f\n",idx,jet_eta[idx],jet_pt[idx],rho,new_jet_pt[idx],isMatchedJet,pt_diff_rel,sf,s_jer,pt_res_gen);
  }

  return new_jet_pt;
}

float compute_JSON_MET_Unc(const double MET_pt, const double MET_phi, const double RAWMET_pt, const double RAWMET_phi, 
const Vec_f& Jet_chEmEF, const Vec_f& Jet_neEmEF, const Vec_f& Jet_muonSubtrFactor, const Vec_f& Jet_rawFactor,
const Vec_f& Jet_pt_def, const Vec_f& Jet_pt_mod, const Vec_f& Jet_eta, const Vec_f& Jet_phi, const Vec_f& Jet_mass, int type){
  bool debug = false;
  if(debug) printf("MET: %lu %d\n",Jet_pt_def.size(),type);
  if(Jet_pt_def.size() != Jet_pt_mod.size()) printf("Different jet sizes in MET corrector!!!\n");

  double ini_met[2] = {MET_pt * cos(MET_phi), MET_pt * sin(MET_phi)};
  if(type < 0){
    ini_met[0] = RAWMET_pt * cos(RAWMET_phi);
    ini_met[1] = RAWMET_pt * sin(RAWMET_phi);
  }

  for (unsigned int idx = 0; idx < Jet_pt_def.size(); ++idx) {
    if(Jet_chEmEF[idx] + Jet_neEmEF[idx] >= 0.9) continue;
    if(Jet_pt_def[idx] * (1-Jet_muonSubtrFactor[idx]) < 15) continue;
    PtEtaPhiMVector jetForMET_raw = PtEtaPhiMVector(Jet_pt_def[idx] * (1-Jet_rawFactor[idx]) * (1-Jet_muonSubtrFactor[idx]), Jet_eta[idx], Jet_phi[idx], Jet_mass[idx]);
    PtEtaPhiMVector jetForMET_def = PtEtaPhiMVector(Jet_pt_def[idx] *                          (1-Jet_muonSubtrFactor[idx]), Jet_eta[idx], Jet_phi[idx], Jet_mass[idx]);
    PtEtaPhiMVector jetForMET_mod = PtEtaPhiMVector(Jet_pt_mod[idx] *                          (1-Jet_muonSubtrFactor[idx]), Jet_eta[idx], Jet_phi[idx], Jet_mass[idx]);
    if(type > 0){
      ini_met[0] = ini_met[0] - jetForMET_mod.Px() + jetForMET_def.Px();
      ini_met[1] = ini_met[1] - jetForMET_mod.Py() + jetForMET_def.Py();
    } else {
      ini_met[0] = ini_met[0] - jetForMET_def.Px() + jetForMET_raw.Px();
      ini_met[1] = ini_met[1] - jetForMET_def.Py() + jetForMET_raw.Py();
    }
  }
  PxPyPzMVector newMET = PxPyPzMVector(ini_met[0],ini_met[1],0.0,0.0);
  if(debug) printf("%6.1f %6.1f %6.1f | %6.2f %6.2f %6.2f\n",MET_pt,RAWMET_pt,newMET.Pt(),MET_phi,RAWMET_phi,newMET.Phi());

  if     (abs(type) == 1) return newMET.Pt();
  else if(abs(type) == 2) return newMET.Phi(); 
  
  return 0;
}

float compute_JSON_MET(const std::string pt_phiS, const std::string met_typeS, const int year, const std::string dtmcS, const std::string variationS, const float met_pt, const float met_phi, const float npvGood) {

  const char *pt_phi = pt_phiS.c_str();
  const char *met_type = met_typeS.c_str();
  const char *epoch = "";
  if     (year == 20220) epoch = (char*)"2022";
  else if(year == 20221) epoch = (char*)"2022EE";
  else if(year == 20230) epoch = (char*)"2023";
  else if(year == 20231) epoch = (char*)"2023BPix";
  else if(year == 20240) epoch = (char*)"2023BPix";
  const char *dtmc = dtmcS.c_str();
  const char *variation = variationS.c_str();

  float result = corrSFs.eval_met_corr(pt_phi, met_type, epoch, dtmc, variation, met_pt,met_phi,npvGood);

  // NO CORRECTION APPLIED FOR 2024!!!
  if     (year == 20240 && pt_phiS == "pt") result = met_pt;
  else if(year == 20240 && pt_phiS == "phi") result = met_phi;

  bool debug = false;
  if(debug) printf("MET: %s / %s / %s / %s / %s / %.2f / %.2f / %.2f: %.2f\n",pt_phi,met_type,epoch,dtmc,variation,met_pt,met_phi,npvGood,result);

  return result;
}

Vec_b cleaningJetVetoMapMask(const Vec_f& jet_eta, const Vec_f& jet_phi, int jetTypeCorr, const int year) {
  Vec_b jet_vetoMap_mask(jet_eta.size(), true);

  if     (jetTypeCorr == -1 && year == 20220) jetTypeCorr = 0;
  else if(jetTypeCorr == -1 && year == 20221) jetTypeCorr = 4;
  else if(jetTypeCorr == -1 && year == 20230) jetTypeCorr = 2;
  else if(jetTypeCorr == -1 && year == 20231) jetTypeCorr = 3;
  else if(jetTypeCorr == -1) return jet_vetoMap_mask;

  bool debug = false;
  if(debug) printf("cleaningJetVetoMapMask: %lu %d\n",jet_eta.size(),jetTypeCorr);

  for (unsigned int idx = 0; idx < jet_eta.size(); ++idx) {
    double jetVetoMap = corrSFs.eval_jetVetoMap(jet_eta[idx], jet_phi[idx], jetTypeCorr);
    if(jetVetoMap > 0) jet_vetoMap_mask[idx] = false;
    if(debug) printf("jetVetoMapMask(%d): %6.2f %6.2f %d\n",idx,jet_eta[idx],jet_phi[idx],jet_vetoMap_mask[idx]);
  }

  return jet_vetoMap_mask;
}

Vec_f compute_MUOPT_Unc(const int year, const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_f& mu_phi, const Vec_i& mu_charge, const Vec_f& mu_nTrackerLayers, int type){
  Vec_f new_mu_pt(mu_pt.size(), 1.0);
  bool debug = false;
  if(debug) printf("muonEnergy: %lu %d\n",mu_pt.size(),type);
  /*if     (year == 20220){
    for(unsigned int i=0;i<mu_pt.size();i++) {
       if     (type == +1 && abs(mu_eta[i]) <  1.5) new_mu_pt[i] = mu_pt[i]*(1.0014+gRandom->Gaus(0.0,0.0030));
       else if(type ==  0 && abs(mu_eta[i]) <  1.5) new_mu_pt[i] = mu_pt[i]*(0.9994+gRandom->Gaus(0.0,0.0030));
       else if(type == -1 && abs(mu_eta[i]) <  1.5) new_mu_pt[i] = mu_pt[i]*(0.9974+gRandom->Gaus(0.0,0.0030));
       else if(type == +1 && abs(mu_eta[i]) >= 1.5) new_mu_pt[i] = mu_pt[i]*(1.0014+gRandom->Gaus(0.0,0.0050));
       else if(type ==  0 && abs(mu_eta[i]) >= 1.5) new_mu_pt[i] = mu_pt[i]*(0.9994+gRandom->Gaus(0.0,0.0050));
       else if(type == -1 && abs(mu_eta[i]) >= 1.5) new_mu_pt[i] = mu_pt[i]*(0.9974+gRandom->Gaus(0.0,0.0050));
       else printf("PROBLEM in compute_MUOPT_Unc\n");
    }
  }
  else if(year == 20221){
    for(unsigned int i=0;i<mu_pt.size();i++) {
       if     (type == +1 && abs(mu_eta[i]) <  1.5) new_mu_pt[i] = mu_pt[i]*(1.0015+gRandom->Gaus(0.0,0.0030));
       else if(type ==  0 && abs(mu_eta[i]) <  1.5) new_mu_pt[i] = mu_pt[i]*(0.9995+gRandom->Gaus(0.0,0.0030));
       else if(type == -1 && abs(mu_eta[i]) <  1.5) new_mu_pt[i] = mu_pt[i]*(0.9975+gRandom->Gaus(0.0,0.0030));
       else if(type == +1 && abs(mu_eta[i]) >= 1.5) new_mu_pt[i] = mu_pt[i]*(1.0008+gRandom->Gaus(0.0,0.0110));
       else if(type ==  0 && abs(mu_eta[i]) >= 1.5) new_mu_pt[i] = mu_pt[i]*(0.9988+gRandom->Gaus(0.0,0.0110));
       else if(type == -1 && abs(mu_eta[i]) >= 1.5) new_mu_pt[i] = mu_pt[i]*(0.9968+gRandom->Gaus(0.0,0.0110));
       else printf("PROBLEM in compute_MUOPT_Unc\n");
    }
  }
  else if(year == 20230){
    for(unsigned int i=0;i<mu_pt.size();i++) {
       if     (type == +1 && abs(mu_eta[i]) <  1.5) new_mu_pt[i] = mu_pt[i]*(1.0013+gRandom->Gaus(0.0,0.0040));
       else if(type ==  0 && abs(mu_eta[i]) <  1.5) new_mu_pt[i] = mu_pt[i]*(0.9993+gRandom->Gaus(0.0,0.0040));
       else if(type == -1 && abs(mu_eta[i]) <  1.5) new_mu_pt[i] = mu_pt[i]*(0.9973+gRandom->Gaus(0.0,0.0040));
       else if(type == +1 && abs(mu_eta[i]) >= 1.5) new_mu_pt[i] = mu_pt[i]*(1.0004+gRandom->Gaus(0.0,0.0100));
       else if(type ==  0 && abs(mu_eta[i]) >= 1.5) new_mu_pt[i] = mu_pt[i]*(0.9984+gRandom->Gaus(0.0,0.0100));
       else if(type == -1 && abs(mu_eta[i]) >= 1.5) new_mu_pt[i] = mu_pt[i]*(0.9964+gRandom->Gaus(0.0,0.0100));
       else printf("PROBLEM in compute_MUOPT_Unc\n");
    }
  }
  else if(year == 20231){
    for(unsigned int i=0;i<mu_pt.size();i++) {
       if     (type == +1 && abs(mu_eta[i]) <  1.5) new_mu_pt[i] = mu_pt[i]*(1.0014+gRandom->Gaus(0.0,0.0040));
       else if(type ==  0 && abs(mu_eta[i]) <  1.5) new_mu_pt[i] = mu_pt[i]*(0.9994+gRandom->Gaus(0.0,0.0040));
       else if(type == -1 && abs(mu_eta[i]) <  1.5) new_mu_pt[i] = mu_pt[i]*(0.9974+gRandom->Gaus(0.0,0.0040));
       else if(type == +1 && abs(mu_eta[i]) >= 1.5) new_mu_pt[i] = mu_pt[i]*(1.0008+gRandom->Gaus(0.0,0.0110));
       else if(type ==  0 && abs(mu_eta[i]) >= 1.5) new_mu_pt[i] = mu_pt[i]*(0.9988+gRandom->Gaus(0.0,0.0110));
       else if(type == -1 && abs(mu_eta[i]) >= 1.5) new_mu_pt[i] = mu_pt[i]*(0.9968+gRandom->Gaus(0.0,0.0110));
       else printf("PROBLEM in compute_MUOPT_Unc\n");
    }
  }*/
  if(year == 20220 || year == 20221 || year == 20230 || year == 20231 || year == 20240){
    for(unsigned int i=0;i<mu_pt.size();i++) {
      if(type == 10) new_mu_pt[i] = corrSFs.eval_muon_pt_scale(1, mu_pt[i], mu_eta[i], mu_phi[i], mu_charge[i]);
      else {
        float pt_scale_corr = corrSFs.eval_muon_pt_scale(0, mu_pt[i], mu_eta[i], mu_phi[i], mu_charge[i]);
        float pt_corr = corrSFs.eval_muon_pt_resol(pt_scale_corr, mu_eta[i], float(mu_nTrackerLayers[i]));
        if     (type ==  0) new_mu_pt[i] = pt_corr;
        else if(type == +1) {
          float pt_scale_unc = corrSFs.eval_muon_pt_scale_var(pt_corr, mu_eta[i], mu_phi[i], mu_charge[i], "up");
          float pt_resol_unc = corrSFs.eval_muon_pt_resol_var(pt_scale_corr, pt_corr, mu_eta[i], "up");
          if(fabs(pt_scale_unc-pt_corr) > fabs(pt_resol_unc-pt_corr)) new_mu_pt[i] = pt_scale_unc;
          else                                                        new_mu_pt[i] = pt_resol_unc;
        }
        else if(type == -1) {
          float pt_scale_unc = corrSFs.eval_muon_pt_scale_var(pt_corr, mu_eta[i], mu_phi[i], mu_charge[i], "dn");
          float pt_resol_unc = corrSFs.eval_muon_pt_resol_var(pt_scale_corr, pt_corr, mu_eta[i], "dn");
          if(fabs(pt_scale_unc-pt_corr) > fabs(pt_resol_unc-pt_corr)) new_mu_pt[i] = pt_scale_unc;
          else                                                        new_mu_pt[i] = pt_resol_unc;
        }
      }
      if(debug) printf("muon(%d)-%d: %.3f %.3f\n",i,type,mu_pt[i],new_mu_pt[i]);
    }
  }
  else {
    for(unsigned int i=0;i<mu_pt.size();i++) {
       new_mu_pt[i] = mu_pt[i];
    }
  }

  return new_mu_pt;
}

Vec_f compute_ELEPT_Unc(const int year, const int type, const Vec_i& gain, const int run, const Vec_f& eta, const Vec_f& r9, const Vec_f& pt){
  Vec_f new_pt(pt.size(), 1.0);
  bool debug = false;
  if(debug) printf("eleEnergy: %lu %d\n",pt.size(),type);

  const bool applySSEtDependent = true;

  if(applySSEtDependent == false &&
     (year == 20220 || year == 20221 || year == 20230 || year == 20231 || year == 20240)){
    if    (type == 10) { // data
      for(unsigned int i=0;i<pt.size();i++) {
        new_pt[i] = pt[i]*corrSFs.eval_electronScale((char*)"total_correction", gain[i], (double)run, eta[i], r9[i], pt[i]);
        if(debug) printf("eleSS(%d)-%d: %.3f %.3f\n",i,type,pt[i],new_pt[i]);
      }
    }
    else if(type == 0) { // MC default
      for(unsigned int i=0;i<pt.size();i++) {
        double rho = corrSFs.eval_electronSmearing((char*)"rho", eta[i], r9[i]);
        new_pt[i] = pt[i]*gRandom->Gaus(1.0,rho);
        if(debug) printf("eleSS(%d)-%d: %.3f %.3f %.6f\n",i,type,pt[i],new_pt[i],rho);
      }
    }
    else if(type == -1 || type == +1) { // MC smearing uncertainty
      for(unsigned int i=0;i<pt.size();i++) {
        double rho     = corrSFs.eval_electronSmearing((char*)"rho", eta[i], r9[i]);
        double rho_unc = corrSFs.eval_electronSmearing((char*)"err_rho", eta[i], r9[i]);
        double scale_unc = corrSFs.eval_electronScale((char*)"total_uncertainty", gain[i], 1.0, eta[i], r9[i], pt[i]);
        new_pt[i] = pt[i]*gRandom->Gaus(1.0,rho+(double)type*(rho_unc+scale_unc));
        if(debug) printf("eleSS(%d)-%d: %.3f %.3f %.6f %.6f %.6f\n",i,type,pt[i],new_pt[i],rho,rho_unc,scale_unc);
      }
    }
  }
  else if(applySSEtDependent == true &&
     (year == 20220 || year == 20221 || year == 20230 || year == 20231 || year == 20240)){
    if    (type == 10) { // data
      for(unsigned int i=0;i<pt.size();i++) {
        new_pt[i] = pt[i]*corrSFs.eval_electronEtDependentScale((char*)"scale", (double)run, eta[i], r9[i], pt[i], gain[i]);
        if(debug) printf("eleSSEtDependent(%d)-%d: %.3f %.3f\n",i,type,pt[i],new_pt[i]);
      }
    }
    else if(type == 0) { // MC default
      for(unsigned int i=0;i<pt.size();i++) {
        double smear = corrSFs.eval_electronEtDependentSmearing((char*)"smear", pt[i], r9[i], eta[i]);
        new_pt[i] = pt[i]*(1.0 + smear * gRandom->Gaus(0.0,1.0));
        if(debug) printf("eleSSEtDependent(%d)-%d: %.3f %.3f %.6f\n",i,type,pt[i],new_pt[i],smear);
      }
    }
    else if(type == -1 || type == +1) { // MC smearing uncertainty
      for(unsigned int i=0;i<pt.size();i++) {
        double smear  = corrSFs.eval_electronEtDependentSmearing((char*)"smear",  pt[i], r9[i], eta[i]);
        double esmear = corrSFs.eval_electronEtDependentSmearing((char*)"esmear", pt[i], r9[i], eta[i]);
        new_pt[i] = pt[i]*(1.0 + (smear + (double)type*esmear) * gRandom->Gaus(0.0,1.0));
        if(debug) printf("eleSSEtDependent(%d)-%d: %.3f %.3f %.6f %.6f\n",i,type,pt[i],new_pt[i],smear,esmear);
      }
    }
  }
  else {
    for(unsigned int i=0;i<pt.size();i++) {
       new_pt[i] = pt[i];
    }
  }

  return new_pt;
}

Vec_f compute_PHOPT_Unc(const Vec_f& ph_pt, int type){
  Vec_f new_ph_pt(ph_pt.size(), 1.0);
  for(unsigned int i=0;i<ph_pt.size();i++) {
     if     (type == +1) new_ph_pt[i] = ph_pt[i]*1.01;
     else if(type == -1) new_ph_pt[i] = ph_pt[i]*0.99;
  }

  return new_ph_pt;
}


float compute_bdt_test(const Vec_f& bdt){
  if(bdt.size() != 1) {
    printf("bdt size != 1 %lu\n",bdt.size());
    return -10.0;
  }
  return bdt[0];
}

Vec_b cleaningBitmap(const Vec_i& Photon_vidNestedWPBitmap, int var, int cutBased) {

  Vec_b mask(Photon_vidNestedWPBitmap.size(), true);
  for(unsigned int i=0;i<Photon_vidNestedWPBitmap.size();i++) {
    if((Photon_vidNestedWPBitmap[i]>>var&3) >= cutBased) continue;
    mask[i] = false;
  }
  return mask;
}

float compute_photon_test(const Vec_f& Photon_pt, const Vec_f& Photon_eta, const Vec_f& Photon_phi, 
const Vec_i& Photon_cutBased, const Vec_f& Photon_pfRelIso03_all, const Vec_f& Photon_pfRelIso03_chg, 
const Vec_f& Photon_hoe, const Vec_f& Photon_sieie, const Vec_i& Photon_vidNestedWPBitmap)
{
  for(unsigned int i=0;i<Photon_pt.size();i++) {
  int pass0 = (Photon_vidNestedWPBitmap[i]>>4&3);  // H/E
  int pass1 = (Photon_vidNestedWPBitmap[i]>>6&3);  // sigmaiEtaiEta
  int pass2 = (Photon_vidNestedWPBitmap[i]>>8&3);  // ChIso
  int pass3 = (Photon_vidNestedWPBitmap[i]>>10&3); // NeuIso
  int pass4 = (Photon_vidNestedWPBitmap[i]>>12&3); // PhoIso
  printf("test %5.1f %d %d %.5f %.4f %.4f %.4f %.4f | %d %d %d %d %d\n",Photon_pt[i],(int)(Photon_eta[i]<1.5),Photon_cutBased[i],Photon_hoe[i],Photon_sieie[i],
  Photon_pfRelIso03_all[i]*Photon_pt[i],Photon_pfRelIso03_chg[i]*Photon_pt[i],(Photon_pfRelIso03_all[i]-Photon_pfRelIso03_chg[i])*Photon_pt[i],
  pass0,pass1,pass2,pass3,pass4);

  //printf("test %5.1f %d %d %.5f %.4f %.4f %.4f %.4f | %d %d | %d %d | %d %d | %d %d | %d %d | %d %d | %d %d\n",Photon_pt[i],(int)(Photon_eta[i]<1.5),Photon_cutBased[i],Photon_hoe[i],Photon_sieie[i],
  //Photon_pfRelIso03_all[i]*Photon_pt[i],Photon_pfRelIso03_chg[i]*Photon_pt[i],(Photon_pfRelIso03_all[i]-Photon_pfRelIso03_chg[i])*Photon_pt[i],
  //(Photon_vidNestedWPBitmap[i]&(1<<0))==(1<<0),(Photon_vidNestedWPBitmap[i]&(1<<1))==(1<<1),(Photon_vidNestedWPBitmap[i]&(1<<2))==(1<<2),(Photon_vidNestedWPBitmap[i]&(1<<3))==(1<<3),
  //(Photon_vidNestedWPBitmap[i]&(1<<4))==(1<<4),(Photon_vidNestedWPBitmap[i]&(1<<5))==(1<<5),(Photon_vidNestedWPBitmap[i]&(1<<6))==(1<<6),(Photon_vidNestedWPBitmap[i]&(1<<7))==(1<<7),
  //(Photon_vidNestedWPBitmap[i]&(1<<8))==(1<<8),(Photon_vidNestedWPBitmap[i]&(1<<9))==(1<<9),(Photon_vidNestedWPBitmap[i]&(1<<10))==(1<<10),(Photon_vidNestedWPBitmap[i]&(1<<11))==(1<<11),
  //(Photon_vidNestedWPBitmap[i]&(1<<12))==(1<<12),(Photon_vidNestedWPBitmap[i]&(1<<13))==(1<<13));
  }
  return 1.0;
}

float compute_test(const Vec_f& mu_pt, const Vec_f& mu_eta, TH2D histo_mu){
  printf("test %f\n",histo_mu.GetBinContent(2,2));
  return 1.0;
}

struct WeightsComputer {
   TH2D *fHist2D;
   WeightsComputer(TH2D *h) : fHist2D(h) {}

   float operator()(const Vec_f &mu_pt, const Vec_f &mu_eta) {
      return compute_test(mu_pt, mu_eta, *fHist2D);
  }
};

int compute_number_WS(const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_i& mu_charge, const Vec_i& mu_genPartIdx,
                      const Vec_f& el_pt, const Vec_f& el_eta, const Vec_i& el_charge, const Vec_i& el_genPartIdx,
                      const Vec_i& GenPart_pdgId){

  int nWS = 0;
  for(unsigned int i=0;i<mu_pt.size();i++) {
    if(mu_genPartIdx[i] < 0) continue; // no gen particle matched
    if(abs(GenPart_pdgId[mu_genPartIdx[i]]) != 13) continue; // no gen muon matched
    if(GenPart_pdgId[mu_genPartIdx[i]] * mu_charge[i] > 0) { // Wrong charge
      nWS++;
    }
  }

  for(unsigned int i=0;i<el_pt.size();i++) {
    if(el_genPartIdx[i] < 0) continue; // no gen particle matched
    if(abs(GenPart_pdgId[el_genPartIdx[i]]) != 11) continue; // no gen electron matched
    if(GenPart_pdgId[el_genPartIdx[i]] * el_charge[i] > 0) { // Wrong charge
      nWS++;
    }
  }

  return nWS;
}

float compute_WSSF(const int type, 
                   const Vec_f& el_pt, const Vec_f& el_eta, const Vec_i& el_charge, const Vec_i& el_genPartIdx,
                   const Vec_i& GenPart_pdgId){

  if(type == 0) return 1.0;
  bool debug = false;
  if(debug) printf("WSSFTot: %d %lu\n",type,el_pt.size());

  double sfTot = 1.0;
  for(unsigned int i=0;i<el_pt.size();i++) {
    if(el_genPartIdx[i] < 0) continue; // no gen particle matched
    if(abs(GenPart_pdgId[el_genPartIdx[i]]) != 11) continue; // no gen electron matched
    if(GenPart_pdgId[el_genPartIdx[i]] * el_charge[i] > 0) { // Wrong charge
      double sf = 1.0;
      if     (type == 1){
        const TH1D& hcorr = histoWSEtaSF;
        sf = getValFromTH1(hcorr, std::min(fabs(el_eta[i]),2.4999f));
      }
      else if(type == 2){
        const TH1D& hcorr = histoWSEtaSF_unc;
        sf = getValFromTH1(hcorr, std::min(fabs(el_eta[i]),2.4999f));
      }
      else if(type == 3){
        const TH2D& hcorr = histoWSEtaPtSF;
        sf = getValFromTH2(hcorr, std::min(fabs(el_eta[i]),2.4999f), std::min(el_pt[i],49.999f));
      }
      sfTot = sfTot * sf;
      if(debug) printf("WSSF(%d) %.3f %.3f %.3f %.3f\n",i,el_pt[i],el_eta[i],sf,sfTot);
    }
  }

  return sfTot;
}

float compute_EWKCorr(const int type, const TString theCat, const float mjjGen){

  bool debug = false;
  float sf = 1.0;

  // Careful here, names will need be added to the list!
  if(mjjGen < 500) {
    sf = 1.0;
  }
  else if(theCat.Contains("VBS-SSWW") || theCat.Contains("WWto2L2Nu-2Jets_OS_noTop_EW") || theCat.Contains("WWto2L2Nu-2Jets_SS_noTop_EW")
                                      || theCat.Contains("WWJJto2L2Nu-OS-noTop-EWK")    || theCat.Contains("WWJJto2L2Nu-SS-noTop-EWK")) {
    if(type == 0) {
      const TH1D& hcorr = hVV_KF_EWK[0];
      sf = getValFromTH1(hcorr, mjjGen);
    }
    else if(type == 1) {
      const TH1D& hcorr = hVV_KF_EWK_unc[0];
      sf = getValFromTH1(hcorr, mjjGen);
    }
  }
  else if(theCat.Contains("WZto3LNu-2Jets_EW")
       || theCat.Contains("WZJJto3LNu-EWK")) {
    if(type == 0) {
      const TH1D& hcorr = hVV_KF_EWK[1];
      sf = getValFromTH1(hcorr, mjjGen);
    }
    else if(type == 1) {
      const TH1D& hcorr = hVV_KF_EWK_unc[1];
      sf = getValFromTH1(hcorr, mjjGen);
    }
  }

  if(debug) printf("EWKCorr: %d %s %f %f\n",type,theCat.Data(),mjjGen,sf);

  return sf;
}

float compute_PTWWCorr(const int type, const TString theCat, const float ptww){

  bool debug = false;
  float sf = 1.0;

  // Careful here, names will need be added to the list!
  if(ptww > 100) {
    sf = 1.0;
  }
  else if(theCat.Contains("WWto2L2Nu_TuneCP5")
       || theCat.Contains("GluGlutoContintoWW")
       || theCat.Contains("ggWWto2L2Nu")) {
    float p[3] = {1.36457, -0.0140161, 6.97266e-05};
    sf = p[0] + ptww * p[1] + ptww * ptww * p[2];
  }

  if(debug) printf("PTWWCorr: %d %s %f %f\n",type,theCat.Data(),ptww,sf);

  return sf;
}

float compute_fakeRate(const bool isData,
                       const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_f& mu_jetRelIso, const Vec_i& tight_mu, const int mType,
                       const Vec_f& el_pt, const Vec_f& el_eta, const Vec_f& el_jetRelIso, const Vec_i& tight_el, const int eType,
                       const int whichAna){

  bool debug = false;
  if(debug) printf("fakeRate: %d %d %d\n",mType,eType,whichAna);

  // 0/1/2 - 1001/1002/1003 anaType 1 njets30  > 0
  // 3/4/5 - 1001/1002/1003 anaType 2 nbjets20 > 0
  // 6/7/8 - 1001/1002/1003 anaType 3 nbjets50 > 0
  // def 2, unc 5 / 1 / 8

  double addSF[2] {1.0, 1.0};
  if(whichAna == 1) {addSF[0] = 1.0; addSF[1] = 1.0;}

  if(mu_pt.size() != tight_mu.size() || el_pt.size() != tight_el.size()) {
    printf("PROBLEM in compute_fakeRate (%zu/%zu) (%zu/%zu)!\n",mu_pt.size(),tight_mu.size(),el_pt.size(),tight_el.size());
    return 0;
  }

  double sfTot = 1.0;
  for(unsigned int i=0;i<mu_pt.size();i++) {
    if(tight_mu[i] == 1) continue;
    const TH2D& hcorr = histoFakeEtaPt_mu[mType];
    float ptFakeVar = mu_pt[i];
    if(whichAna == 3) ptFakeVar = mu_pt[i]*(1+std::max(mu_jetRelIso[i],0.0f))*0.9;
    double sf = getValFromTH2(hcorr, fabs(mu_eta[i]),ptFakeVar) * addSF[0];
    sfTot = -sfTot*sf/(1-sf);
    if(debug) printf("fakemu(%d) %.3f %.3f %.3f %.3f %.3f\n",i,ptFakeVar,mu_eta[i],sf,sf/(1-sf),sfTot);
  }

  for(unsigned int i=0;i<el_pt.size();i++) {
    if(tight_el[i] == 1) continue;
    const TH2D& hcorr = histoFakeEtaPt_el[eType];
    float ptFakeVar = el_pt[i];
    if(whichAna == 3) ptFakeVar = el_pt[i]*(1+std::max(el_jetRelIso[i],0.0f))*0.9;
    double sf = getValFromTH2(hcorr, fabs(el_eta[i]), ptFakeVar) * addSF[1];
    sfTot = -sfTot*sf/(1-sf);
    if(debug) printf("fakeel(%d) %.3f %.3f %.3f %.3f %.3f\n",i,el_pt[i],ptFakeVar,sf,sf/(1-sf),sfTot);
  }
      
  if(sfTot != 1 && isData) sfTot = -sfTot;
  return sfTot;
}

float compute_MuonSF(const Vec_f& mu_pt, const Vec_f& mu_eta){

  bool debug = false;
  if(debug) printf("mueff: %lu\n",mu_pt.size());
  double sfTot = 1.0;
  for(unsigned int i=0;i<mu_pt.size();i++) {
    const TH2D& hcorr = histoLepSFEtaPt_mu;
    double sf = getValFromTH2(hcorr, fabs(mu_eta[i]),mu_pt[i]);
    sfTot = sfTot*sf;
    if(debug) printf("lepmu(%d) %.3f %.3f %.3f %.3f\n",i,mu_pt[i],mu_eta[i],sf,sfTot);
  }
      
  return sfTot;
}

float compute_ElectronSF(const Vec_f& el_pt, const Vec_f& el_eta){

  bool debug = false;
  if(debug) printf("eleff: %lu\n",el_pt.size());
  double sfTot = 1.0;
  for(unsigned int i=0;i<el_pt.size();i++) {
    const TH2D& hcorr = histoLepSFEtaPt_el;
    double sf = getValFromTH2(hcorr, fabs(el_eta[i]), el_pt[i]);
    sfTot = sfTot*sf;
    if(debug) printf("lepel(%d) %.3f %.3f %.3f %.3f\n",i,el_pt[i],el_eta[i],sf,sfTot);
  }
      
  return sfTot;
}

float compute_PURecoSF(const Vec_f& mu_pt, const Vec_f& mu_eta,
                       const Vec_f& el_pt, const Vec_f& el_eta,
                       const float nPU, const int type){
  bool debug = false;
  if(debug) printf("lepeff: %lu %lu\n",mu_pt.size(),el_pt.size());
  double sfTot = 1.0;

  double sf = 1.0;
  if     (type == 0){
    const TH1D& hcorr = puWeights;
    sf = getValFromTH1(hcorr, std::min(nPU,72.999f));
  }
  else if(type == 1){
    const TH1D& hcorr = puWeightsUp;
    sf = getValFromTH1(hcorr, std::min(nPU,72.999f));
  }
  else if(type == 2){
    const TH1D& hcorr = puWeightsDown;
    sf = getValFromTH1(hcorr, std::min(nPU,72.999f));
  }
  else {
    printf("Wrong type %d\n",type);
  }
  sfTot = sfTot*std::min(sf,4.0);
  if(debug) printf("pu %.3f %.3f %.3f\n",nPU,sf,sfTot);

  return sfTot;
}

float compute_TriggerSF(float ptl1, float ptl2, float etal1, float etal2, int ltype, float unc){

  if(ltype >= 4) return 1.0;

  TH2D hcorr;
  if     (etal1 <= 1.5 && etal2 <= 1.5 && ltype == 0) hcorr = histoTriggerSFEtaPt_0_0;
  else if(etal1 >  1.5 && etal2 <= 1.5 && ltype == 0) hcorr = histoTriggerSFEtaPt_0_1;
  else if(etal1 <= 1.5 && etal2 >  1.5 && ltype == 0) hcorr = histoTriggerSFEtaPt_0_2;
  else if(etal1 >  1.5 && etal2 >  1.5 && ltype == 0) hcorr = histoTriggerSFEtaPt_0_3;
  else if(etal1 <= 1.5 && etal2 <= 1.5 && ltype == 1) hcorr = histoTriggerSFEtaPt_1_0;
  else if(etal1 >  1.5 && etal2 <= 1.5 && ltype == 1) hcorr = histoTriggerSFEtaPt_1_1;
  else if(etal1 <= 1.5 && etal2 >  1.5 && ltype == 1) hcorr = histoTriggerSFEtaPt_1_2;
  else if(etal1 >  1.5 && etal2 >  1.5 && ltype == 1) hcorr = histoTriggerSFEtaPt_1_3;
  else if(etal1 <= 1.5 && etal2 <= 1.5 && ltype == 2) hcorr = histoTriggerSFEtaPt_2_0;
  else if(etal1 >  1.5 && etal2 <= 1.5 && ltype == 2) hcorr = histoTriggerSFEtaPt_2_1;
  else if(etal1 <= 1.5 && etal2 >  1.5 && ltype == 2) hcorr = histoTriggerSFEtaPt_2_2;
  else if(etal1 >  1.5 && etal2 >  1.5 && ltype == 2) hcorr = histoTriggerSFEtaPt_2_3;
  else if(etal1 <= 1.5 && etal2 <= 1.5 && ltype == 3) hcorr = histoTriggerSFEtaPt_3_0;
  else if(etal1 >  1.5 && etal2 <= 1.5 && ltype == 3) hcorr = histoTriggerSFEtaPt_3_1;
  else if(etal1 <= 1.5 && etal2 >  1.5 && ltype == 3) hcorr = histoTriggerSFEtaPt_3_2;
  else if(etal1 >  1.5 && etal2 >  1.5 && ltype == 3) hcorr = histoTriggerSFEtaPt_3_3;
  else printf("Problem trigger type (%d) %f %f\n",ltype,etal1,etal2);
  float sf = getValFromTH2(hcorr, ptl1, ptl2, unc);
  if(sf == 0) {sf = 1.0; /*printf("PROBLEM sf==0! %.3f %.3f %.2f %.2f %d\n",ptl1,ptl2,etal1,etal2,ltype);*/}
  return sf;
}

float compute_TriggerForSingleLegsSF(float ptl1, float ptl2, float etal1, float etal2, int ltype){
  // triggerEff_da_sel  0
  // triggerEff_da_smu  1
  // triggerEff_da_del0 2
  // triggerEff_da_del1 3
  // triggerEff_da_dmu0 4
  // triggerEff_da_dmu1 5
  // triggerEff_da_emu0 6
  // triggerEff_da_emu1 7
  // triggerEff_da_mue0 8
  // triggerEff_da_mue1 9
  bool debug = false;

  if(ltype >= 4) return 1.0;
  
  float effda_sgl_1 = 1; float effda_sgl_2 = 1; float effda_dbl_leadingleg = 1; float effda_dbl_trailingleg = 1;
  float effmc_sgl_1 = 1; float effmc_sgl_2 = 1; float effmc_dbl_leadingleg = 1; float effmc_dbl_trailingleg = 1;
  if     (ltype == 0){ // mm
    effda_sgl_1           = getValFromTH2(histoTriggerDAEtaPt[1], fabs(etal1), ptl1);
    effda_sgl_2           = getValFromTH2(histoTriggerDAEtaPt[1], fabs(etal2), ptl2);
    effda_dbl_leadingleg  = getValFromTH2(histoTriggerDAEtaPt[4], fabs(etal1), ptl1);
    effda_dbl_trailingleg = getValFromTH2(histoTriggerDAEtaPt[5], fabs(etal2), ptl2);

    effmc_sgl_1           = getValFromTH2(histoTriggerMCEtaPt[1], fabs(etal1), ptl1);
    effmc_sgl_2           = getValFromTH2(histoTriggerMCEtaPt[1], fabs(etal2), ptl2);
    effmc_dbl_leadingleg  = getValFromTH2(histoTriggerMCEtaPt[4], fabs(etal1), ptl1);
    effmc_dbl_trailingleg = getValFromTH2(histoTriggerMCEtaPt[5], fabs(etal2), ptl2);
  }
  else if(ltype == 1){ // ee
    effda_sgl_1           = getValFromTH2(histoTriggerDAEtaPt[0], fabs(etal1), ptl1);
    effda_sgl_2           = getValFromTH2(histoTriggerDAEtaPt[0], fabs(etal2), ptl2);
    effda_dbl_leadingleg  = getValFromTH2(histoTriggerDAEtaPt[2], fabs(etal1), ptl1);
    effda_dbl_trailingleg = getValFromTH2(histoTriggerDAEtaPt[3], fabs(etal2), ptl2);

    effmc_sgl_1           = getValFromTH2(histoTriggerMCEtaPt[0], fabs(etal1), ptl1);
    effmc_sgl_2           = getValFromTH2(histoTriggerMCEtaPt[0], fabs(etal2), ptl2);
    effmc_dbl_leadingleg  = getValFromTH2(histoTriggerMCEtaPt[2], fabs(etal1), ptl1);
    effmc_dbl_trailingleg = getValFromTH2(histoTriggerMCEtaPt[3], fabs(etal2), ptl2);
  }
  else if(ltype == 2){ // me
    effda_sgl_1           = getValFromTH2(histoTriggerDAEtaPt[1], fabs(etal1), ptl1);
    effda_sgl_2           = getValFromTH2(histoTriggerDAEtaPt[0], fabs(etal2), ptl2);
    effda_dbl_leadingleg  = getValFromTH2(histoTriggerDAEtaPt[8], fabs(etal1), ptl1);
    effda_dbl_trailingleg = getValFromTH2(histoTriggerDAEtaPt[9], fabs(etal2), ptl2);

    effmc_sgl_1           = getValFromTH2(histoTriggerMCEtaPt[1], fabs(etal1), ptl1);
    effmc_sgl_2           = getValFromTH2(histoTriggerMCEtaPt[0], fabs(etal2), ptl2);
    effmc_dbl_leadingleg  = getValFromTH2(histoTriggerMCEtaPt[8], fabs(etal1), ptl1);
    effmc_dbl_trailingleg = getValFromTH2(histoTriggerMCEtaPt[9], fabs(etal2), ptl2);
  }
  else if(ltype == 3){ // em
    effda_sgl_1           = getValFromTH2(histoTriggerDAEtaPt[0], fabs(etal1), ptl1);
    effda_sgl_2           = getValFromTH2(histoTriggerDAEtaPt[1], fabs(etal2), ptl2);
    effda_dbl_leadingleg  = getValFromTH2(histoTriggerDAEtaPt[6], fabs(etal1), ptl1);
    effda_dbl_trailingleg = getValFromTH2(histoTriggerDAEtaPt[7], fabs(etal2), ptl2);

    effmc_sgl_1           = getValFromTH2(histoTriggerMCEtaPt[0], fabs(etal1), ptl1);
    effmc_sgl_2           = getValFromTH2(histoTriggerMCEtaPt[1], fabs(etal2), ptl2);
    effmc_dbl_leadingleg  = getValFromTH2(histoTriggerMCEtaPt[6], fabs(etal1), ptl1);
    effmc_dbl_trailingleg = getValFromTH2(histoTriggerMCEtaPt[7], fabs(etal2), ptl2);
  }
  
  float evt_effda =  effda_sgl_1 * (1-effda_sgl_2)
                   + effda_sgl_2 * (1-effda_sgl_1)
                   + effda_sgl_1 * effda_sgl_2
                   + (1-effda_sgl_1) * (1-effda_sgl_2) * effda_dbl_leadingleg * effda_dbl_trailingleg;
  
  float evt_effmc =  effmc_sgl_1 * (1-effmc_sgl_2)
                   + effmc_sgl_2 * (1-effmc_sgl_1)
                   + effmc_sgl_1 * effmc_sgl_2
                   + (1-effmc_sgl_1) * (1-effmc_sgl_2) * effmc_dbl_leadingleg * effmc_dbl_trailingleg;

  if(debug) printf("trgeff (%.2f/%.2f/%.2f/%.2f/%d): %.3f/%.3f %.3f/%.3f %.3f/%.3f %.3f/%.3f -> %.3f/%.3f = %.3f\n",ptl1,ptl2,etal1,etal2,ltype,effda_sgl_1,effmc_sgl_1,effda_sgl_2,effmc_sgl_2,effda_dbl_leadingleg,effmc_dbl_leadingleg,effda_dbl_trailingleg,effmc_dbl_trailingleg,evt_effda,evt_effmc,evt_effda/evt_effmc);
  if(evt_effda > 0 && evt_effmc > 0) return evt_effda/evt_effmc;
  return 1.0;
}

float compute_lumiFakeRate(const Vec_f& mu_pt, const Vec_f& el_pt, const int nTrigger, const int year){
  double lumiPrescalesM[3] = {0.182/1000., 0.769/1000., 0.769/1000.}; // Mu8/17/19
  double lumiPrescalesE[3] = {0.134/1000., 0.754/1000., 0.754/1000.}; // El8/12/23
  if     (year == 20220 || year == 20221){
  }
  else if(year == 20230 || year == 20231){
    lumiPrescalesM[0] =  5.8/27693.1;
    lumiPrescalesM[1] = 79.6/27693.1;
    lumiPrescalesM[2] = 79.6/27693.1;
    lumiPrescalesE[0] =  4.8/27693.1;
    lumiPrescalesE[1] = 27.6/27693.1;
    lumiPrescalesE[2] = 27.6/27693.1;
  }
  else if(year == 20240){
    lumiPrescalesM[0] =  12.3/108296.7;
    lumiPrescalesM[1] = 333.2/108296.7;
    lumiPrescalesM[2] = 333.2/108296.7;
    lumiPrescalesE[0] =  12.0/108296.7;
    lumiPrescalesE[1] =  69.9/108296.7;
    lumiPrescalesE[2] =  69.9/108296.7;
  }
  else {
    printf("compute_lumiFakeRate error year (%d)\n",year);
  }
  if     (nTrigger == -1 && mu_pt.size() == 1 && mu_pt[0] <  20) return lumiPrescalesM[0];
  else if(nTrigger == -1 && mu_pt.size() == 1 && mu_pt[0] >= 20) return lumiPrescalesM[1];
  else if(nTrigger == -1 && el_pt.size() == 1 && el_pt[0] <  15) return lumiPrescalesE[0];
  else if(nTrigger == -1 && el_pt.size() == 1 && el_pt[0] >= 15) return lumiPrescalesE[1];

  else if(mu_pt.size() >= 1 && nTrigger == 0) return lumiPrescalesM[0];
  else if(mu_pt.size() >= 1 && nTrigger == 1) return lumiPrescalesM[1];
  else if(mu_pt.size() >= 1 && nTrigger == 2) return lumiPrescalesM[2];
  else if(el_pt.size() >= 1 && nTrigger == 0) return lumiPrescalesE[0];
  else if(el_pt.size() >= 1 && nTrigger == 1) return lumiPrescalesE[1];
  else if(el_pt.size() >= 1 && nTrigger == 2) return lumiPrescalesE[2];

  else printf("PROBLEM in compute_lumiFakeRate\n");

  return 1.0;
}

bool isGoodRunLS(const bool isData, const UInt_t run, const UInt_t lumi) {

  if(not isData) return true;

  if(jsonMap.find(run) == jsonMap.end()) return false; // run not found

  auto& validlumis = jsonMap.at(run);
  auto match = std::lower_bound(std::begin(validlumis), std::end(validlumis), lumi,
                                [](std::pair<unsigned int, unsigned int>& range, unsigned int val) { return range.second < val; });
  return match->first <= lumi && match->second >= lumi;
}

float deltaPhi(float phi1, float phi2) {
  float result = phi1 - phi2;
  while (result > float(M_PI)) result -= float(2*M_PI);
  while (result <= -float(M_PI)) result += float(2*M_PI);
  return fabs(result);
}

float deltaR2(float eta1, float phi1, float eta2, float phi2) {
  float deta = eta1-eta2;
  float dphi = deltaPhi(phi1,phi2);
  return deta*deta + dphi*dphi;
}

float deltaR(float eta1, float phi1, float eta2, float phi2) {
  return std::sqrt(deltaR2(eta1,phi1,eta2,phi2));
}

Vec_f compute_deltaR_var(Vec_f eta, Vec_f phi, float eta1, float phi1){
  Vec_f dR(eta.size(), 0.0);
  for (unsigned int idx = 0; idx < eta.size(); idx++) {
    dR[idx] = std::sqrt(deltaR2(eta[idx],phi[idx],eta1,phi1));
  }
  return dR;
}

Vec_b cleaningMask(Vec_i indices, int size) {

  Vec_b mask(size, true);
  for (int idx : indices) {
    if(idx < 0) continue;
    mask[idx] = false;
  }
  return mask;
}

// 0 => CaloIdL_TrackIdL_IsoVL, 1 => 1e (WPTight), 2 => 1e (WPLoose), 
// 3 => OverlapFilter PFTau, 4 => 2e, 5 => 1e-1mu, 6 => 1e-1tau, 7 => 3e, 
// 8 => 2e-1mu, 9 => 1e-2mu, 10 => 1e (32_L1DoubleEG_AND_L1SingleEGOr), 11 => 1e (CaloIdVT_GsfTrkIdT), 
// 12 => 1e (PFJet), 13 => 1e (Photon175_OR_Photon200) for Electron (PixelMatched e/gamma);

// 0 => hltEG33L1EG26HEFilter, 1 => hltEG50HEFilter, 2 => hltEG75HEFilter, 3 => hltEG90HEFilter, 
// 4 => hltEG120HEFilter, 5 => hltEG150HEFilter, 6 => hltEG150HEFilter, 7 => hltEG200HEFilter, 
// 8 => hltHtEcal800, 9 => hltEG110EBTightIDTightIsoTrackIsoFilter, 10 => hltEG120EBTightIDTightIsoTrackIsoFilter, 11 => 1mu-1photon for Photon;

// 0 => TrkIsoVVL, 1 => Iso, 2 => OverlapFilter PFTau, 3 => 1mu, 
// 4 => 2mu, 5 => 1mu-1e, 6 => 1mu-1tau, 7 => 3mu, 
// 8 => 2mu-1e, 9 => 1mu-2e, 10 => 1mu (Mu50), 11 => 1mu (Mu100), 
// 12 => 1mu-1photon for Muon;
bool hasTriggerMatch(const float& eta, const float& phi, const Vec_f& TrigObj_eta, const Vec_f& TrigObj_phi,
                     const Vec_i& TrigObj_id, const Vec_i& TrigObj_filterBits,
                     const int whichId, const int selectTriggerLep, const bool applyTriggerLep = true) {
  bool debug = false;
  if(debug) printf("triggerMatch(%.2f,%.2f): %d %d %lu\n",eta,phi,whichId,selectTriggerLep,TrigObj_eta.size());
  int whichBits[5] = {0,0,0,0,0};
  // selectTriggerLep = 0 (double lep), = 1 (single lep), 2 (fake lep)
  if     (whichId == 13 && selectTriggerLep == 0){
    whichBits[0] = 0;
    whichBits[1] = 4;
    whichBits[2] = 5;
    whichBits[3] = 5;
    whichBits[4] = 5;
  }
  else if(whichId == 13 && selectTriggerLep == 1){
    whichBits[0] = 1;
    whichBits[1] = 3;
    whichBits[2] = 10;
    whichBits[3] = 11;
    whichBits[4] = 11;
  }
  else if(whichId == 13 && selectTriggerLep == 2){
    whichBits[0] = 0;
    whichBits[1] = 0;
    whichBits[2] = 0;
    whichBits[3] = 0;
    whichBits[4] = 0;
  }
  else if(whichId == 11 && selectTriggerLep == 0){
    whichBits[0] = 0;
    whichBits[1] = 4;
    whichBits[2] = 5;
    whichBits[3] = 5;
    whichBits[4] = 5;
  }
  else if(whichId == 11 && selectTriggerLep == 1){
    whichBits[0] = 1;
    whichBits[1] = 2;
    whichBits[2] = 10;
    whichBits[3] = 11;
    whichBits[4] = 13;
  }
  else if(whichId == 11 && selectTriggerLep == 2){
    whichBits[0] = 0;
    whichBits[1] = 0;
    whichBits[2] = 0;
    whichBits[3] = 0;
    whichBits[4] = 0;
  }
  else {
    printf("whichId / selectTriggerLep problem! %d / %d\n",whichId,selectTriggerLep);
  }

  for (unsigned int jtrig = 0; jtrig < TrigObj_eta.size(); ++jtrig) {
    if(TrigObj_id[jtrig] != whichId && applyTriggerLep == true) continue;
    bool passTriggerLep = ((TrigObj_filterBits[jtrig] & (1<<whichBits[0]))!=0) || ((TrigObj_filterBits[jtrig] & (1<<whichBits[1]))!=0) ||
                          ((TrigObj_filterBits[jtrig] & (1<<whichBits[2]))!=0) || ((TrigObj_filterBits[jtrig] & (1<<whichBits[3]))!=0) ||
                          ((TrigObj_filterBits[jtrig] & (1<<whichBits[4]))!=0);
    if(applyTriggerLep == false) passTriggerLep = true;
    if(passTriggerLep == false)  continue;
    double dRlt = deltaR(eta, phi, TrigObj_eta[jtrig], TrigObj_phi[jtrig]);
    if(debug) printf("(%d,%.2f,%.2f,%.2f): %d/%d/%d/%d/%d - %d - %d\n",TrigObj_filterBits[jtrig],TrigObj_eta[jtrig],TrigObj_phi[jtrig],dRlt,
    ((TrigObj_filterBits[jtrig] & (1<<whichBits[0]))!=0),((TrigObj_filterBits[jtrig] & (1<<whichBits[1]))!=0),
    ((TrigObj_filterBits[jtrig] & (1<<whichBits[2]))!=0),((TrigObj_filterBits[jtrig] & (1<<whichBits[3]))!=0),
    ((TrigObj_filterBits[jtrig] & (1<<whichBits[4]))!=0),
    passTriggerLep,dRlt<0.3);
    if (dRlt < 0.3) return true;
  }
  return false;
}

float get_variable_index(Vec_f var, Vec_f pt, const unsigned int index){

  if(var.size() < index) return 0.0;

  for(unsigned int i=0;i<pt.size();i++) {
    for(unsigned int j=i+1;j<pt.size();j++) {
      if(pt[i]<pt[j]) {
        float temp0 = pt[i]; float temp1 = var[i];
        pt[i] = pt[j]; var[i] = var[j];
        pt[j] = temp0; var[j] = temp1;
      }
    }
  }
  
  return var[index];

}

// Muon Id variables
int compute_muid_var(const Vec_b& mu_mediumId, const Vec_b& mu_tightId, const Vec_i& mu_pfIsoId,
                     const Vec_i& mu_miniIsoId, const Vec_f& mu_promptMVA, const Vec_b& mu_mediumPromptId,
                     unsigned int nsel)
{
  if(mu_mediumId.size() < nsel+1) return -1;

  int var = 0;
  if(mu_mediumId[nsel] == true && mu_pfIsoId[nsel] >= 4) var = var + 1;
  if(mu_tightId[nsel] == true && mu_pfIsoId[nsel] >= 4) var = var + 2;
  if(mu_mediumPromptId[nsel] == true &&  mu_pfIsoId[nsel] >= 4) var = var + 4;
  if(mu_tightId[nsel] == true && mu_miniIsoId[nsel] >= 3) var = var + 8;
  if(mu_mediumPromptId[nsel] == true && mu_miniIsoId[nsel] >= 3) var = var + 16;
  if(mu_mediumPromptId[nsel] == true && mu_promptMVA[nsel] > 0.7) var = var + 32;
  if(mu_tightId[nsel] == true && mu_promptMVA[nsel] > 0.7) var = var + 64;
  if(mu_mediumPromptId[nsel] == true && mu_miniIsoId[nsel] >= 4) var = var + 128;
  if(mu_mediumPromptId[nsel] == true && mu_promptMVA[nsel] > 0.5) var = var + 256;

  return var;
}

// Electron Id variables
int compute_elid_var(const Vec_i& el_cutBased, const Vec_b& el_mvaNoIso_WP80, const Vec_b& el_mvaIso_WP80,
                     const Vec_b& el_mvaIso_WP90, const Vec_i& el_tightCharge, const Vec_f& el_promptMVA,
                     const Vec_f& el_pfRelIso03_chg, const Vec_f& el_pfRelIso03_all,
                     unsigned int nsel)
{
  if(el_cutBased.size() < nsel+1) return -1;

  int var = 0;
  if(el_cutBased[nsel] >= 3) var = var + 1;
  if(el_cutBased[nsel] >= 4) var = var + 2;
  if(el_mvaNoIso_WP80[nsel] == true && el_pfRelIso03_chg[nsel] < 0.15) var = var + 4;
  if(el_mvaIso_WP80[nsel] == true) var = var + 8;
  if(el_promptMVA[nsel] > 0.5) var = var + 16;
  if(el_mvaIso_WP90[nsel] == true) var = var + 32;
  if(el_mvaIso_WP80[nsel] == true && el_tightCharge[nsel] == 2) var = var + 64;
  if(el_promptMVA[nsel] > 0.5 && el_tightCharge[nsel] == 2) var = var + 128;
  if(el_mvaNoIso_WP80[nsel] == true && el_pfRelIso03_all[nsel] < 0.20) var = var + 256;

  return var;
}

// Met-lepton-gamma variables
float compute_met_lepton_gamma_var(Vec_f pt, Vec_f eta, Vec_f phi, Vec_f mass, 
                                   const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_f& mu_phi, const Vec_f& mu_mass,
                                   const Vec_f& el_pt, const Vec_f& el_eta, const Vec_f& el_phi, const Vec_f& el_mass,
                                   const float met_pt, const float met_phi,
                                   const Vec_f& ph_pt, const Vec_f& ph_eta, const Vec_f& ph_phi,
                                   unsigned int var)
{
  if(mu_pt.size() + el_pt.size() < 2) return -1;
  if(ph_pt.size() < 1) return -1;

  float HT[2]= {0,0};
  PtEtaPhiMVector p4llgmom = PtEtaPhiMVector(0.0,0.0,0.0,0.0);

  for(unsigned int i=0;i<mu_pt.size();i++) {
    HT[0] += mu_pt[i];
    p4llgmom += PtEtaPhiMVector(mu_pt[i],mu_eta[i],mu_phi[i],mu_mass[i]);
  }

  for(unsigned int i=0;i<el_pt.size();i++) {
    HT[0] += el_pt[i];
    p4llgmom += PtEtaPhiMVector(el_pt[i],el_eta[i],el_phi[i],el_mass[i]);
  }

  HT[0] += ph_pt[0];
  p4llgmom += PtEtaPhiMVector(ph_pt[0],ph_eta[0],ph_phi[0],0.0);

  PtEtaPhiMVector p4jetmom = PtEtaPhiMVector(met_pt,0.0,met_phi,0.0);
  float dPhiJMET = 999.;
  for(unsigned int i=0;i<pt.size();i++) {
    HT[1] += pt[i];
    p4jetmom += PtEtaPhiMVector(pt[i],eta[i],phi[i],mass[i]);
    if(dPhiJMET > deltaPhi(phi[i],met_phi)) dPhiJMET = deltaPhi(phi[i],met_phi);
  }

  double theVar = 0;
  if     (var == 0) theVar = fabs(p4llgmom.Pt()-met_pt)/p4llgmom.Pt();
  else if(var == 1) theVar = fabs(p4llgmom.Pt()-p4jetmom.Pt())/p4llgmom.Pt();
  else if(var == 2) theVar = deltaPhi(p4llgmom.Phi(),met_phi);
  else if(var == 3) theVar = deltaPhi(p4llgmom.Phi(),p4jetmom.Phi());
  else if(var == 4) theVar = sqrt(2*ph_pt[0]*met_pt*(1-cos(deltaPhi(ph_phi[0],met_phi))));
  else if(var == 5) theVar = HT[1]/(HT[0]+HT[1]);
  else if(var == 6) theVar = ph_pt[0];
  else if(var == 7) theVar = p4llgmom.M();
  return theVar;
}

// Met-lepton variables
float compute_met_lepton_var(Vec_f pt, Vec_f eta, Vec_f phi, Vec_f mass, 
                             const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_f& mu_phi, const Vec_f& mu_mass,
                             const Vec_f& el_pt, const Vec_f& el_eta, const Vec_f& el_phi, const Vec_f& el_mass,
                             const float met_pt, const float met_phi,
                             unsigned int var)
{
  if(mu_pt.size() + el_pt.size() < 2) return -1;

  float HT[2]= {0,0};
  PtEtaPhiMVector p4llmom = PtEtaPhiMVector(0.0,0.0,0.0,0.0);

  for(unsigned int i=0;i<mu_pt.size();i++) {
    HT[0] += mu_pt[i];
    p4llmom += PtEtaPhiMVector(mu_pt[i],mu_eta[i],mu_phi[i],mu_mass[i]);
  }

  for(unsigned int i=0;i<el_pt.size();i++) {
    HT[0] += el_pt[i];
    p4llmom += PtEtaPhiMVector(el_pt[i],el_eta[i],el_phi[i],el_mass[i]);
  }

  PtEtaPhiMVector p4jetmom = PtEtaPhiMVector(met_pt,0.0,met_phi,0.0);
  float dPhiJMET = 999.;
  for(unsigned int i=0;i<pt.size();i++) {
    HT[1] += pt[i];
    p4jetmom += PtEtaPhiMVector(pt[i],eta[i],phi[i],mass[i]);
    if(dPhiJMET > deltaPhi(phi[i],met_phi)) dPhiJMET = deltaPhi(phi[i],met_phi);
  }

  double theVar = 0;
  if     (var == 0) theVar = fabs(p4llmom.Pt()-met_pt)/p4llmom.Pt();
  else if(var == 1) theVar = fabs(p4llmom.Pt()-p4jetmom.Pt())/p4llmom.Pt();
  else if(var == 2) theVar = deltaPhi(p4llmom.Phi(),met_phi);
  else if(var == 3) theVar = deltaPhi(p4llmom.Phi(),p4jetmom.Phi());
  else if(var == 4) theVar = sqrt(2*p4llmom.Pt()*met_pt*(1-cos(deltaPhi(p4llmom.Phi(),met_phi))));
  else if(var == 5) theVar = HT[1]/(HT[0]+HT[1]);
  else if(var == 6) theVar = dPhiJMET;
  return theVar;
}

// Jet-X-gamma variables
float compute_jet_x_gamma_var(Vec_f pt, Vec_f eta, Vec_f phi, Vec_f mass, 
                             const float  x_pt, const float  x_eta, const float  x_phi, const float x_mass,
                             const float ph_pt, const float ph_eta, const float pt_phi,
		             unsigned int var)
{
  if(pt.size() < 2) return -1;

  PtEtaPhiMVector p1(pt[0], eta[0], phi[0], mass[0]);
  PtEtaPhiMVector p2(pt[1], eta[1], phi[1], mass[1]);
  //if(p1.Pt() < p2.Pt()) printf("Pt jet reversed!\n");
  for(unsigned int i=0;i<pt.size();i++) {
    for(unsigned int j=i+1;j<pt.size();j++) {
      if(pt[i]<pt[j]) {
        float temp0 = pt[i]; float temp1 = eta[i]; float temp2 = phi[i]; float temp3 = mass[i];
        pt[i] = pt[j];	     eta[i] = eta[j];	   phi[i] = phi[j];      mass[i] = mass[j];
        pt[j] = temp0;	     eta[j] = temp1;	   phi[j] = temp2;	 mass[j] = temp3;
      }
    }
  }

  float deltaEtaJJ = fabs(p1.Eta()-p2.Eta());
  float sumHT = p1.Pt() + p2.Pt() + x_pt + ph_pt;

  PtEtaPhiMVector p4momX  = PtEtaPhiMVector( x_pt, x_eta, x_phi, x_mass);
  PtEtaPhiMVector p4momPh = PtEtaPhiMVector(ph_pt,ph_eta,pt_phi, 0);

  PtEtaPhiMVector p4momVV = p4momX + p4momPh;
  PtEtaPhiMVector p4momTot = p4momX + p4momPh + p1 + p2;

  float maxZ = fabs(x_eta-(p1.Eta()+p2.Eta())/2.)/deltaEtaJJ;
  if(fabs(ph_eta-(p1.Eta()+p2.Eta())/2.)/deltaEtaJJ > maxZ) maxZ = fabs(ph_eta-(p1.Eta()+p2.Eta())/2.)/deltaEtaJJ;

  double theVar = 0;
  if     (var == 0) theVar = fabs(p4momVV.Eta()-(p1.Eta()+p2.Eta())/2.)/deltaEtaJJ;
  else if(var == 1) theVar = maxZ;
  else if(var == 2) theVar = sumHT;
  else if(var == 3) theVar = p4momVV.Pt();
  else if(var == 4) theVar = p4momTot.Pt();
  else if(var == 5) theVar = fabs(p4momVV.Eta()-p1.Eta());
  else if(var == 6) theVar = fabs(p4momVV.Eta()-p2.Eta());
  else if(var == 7) theVar = (p4momVV.Pt()-(p1+p2).Pt())/(p1+p2).Pt();
  return theVar;
}
// Jet-lepton final variables
float compute_jet_lepton_final_var(const float mjj, const float detajj, const float dphijj, const float zepvv, const float bdt, const float mll, const int njets, unsigned int var)
{
  if     (var < 10){
    int typeSelAux1 = -1;
    if     (mjj <  900) typeSelAux1 = 0;
    else if(mjj < 1300) typeSelAux1 = 1;
    else if(mjj < 2000) typeSelAux1 = 2;
    else                typeSelAux1 = 3;
  
    float typeSelAux2 = -1;
    if     (mll <  80) typeSelAux2 = 0;
    else if(mll < 140) typeSelAux2 = 1;
    else if(mll < 220) typeSelAux2 = 2;
    else               typeSelAux2 = 3;
    
    float typeSelAux3 = -1;
    if     (njets <= 2) typeSelAux3 = 0;
    else if(njets == 3) typeSelAux3 = 1;
    else                typeSelAux3 = 2;
  
    float typeSelAux4 = -1;
    if     (detajj < 3.6) typeSelAux4 = 0;
    else if(detajj < 4.5) typeSelAux4 = 1;
    else if(detajj < 5.5) typeSelAux4 = 2;
    else                  typeSelAux4 = 3;
  
    float typeSelAux5 = -1;
    if     (dphijj < 1.8) typeSelAux5 = 0;
    else if(dphijj < 2.5) typeSelAux5 = 1;
    else if(dphijj < 2.9) typeSelAux5 = 2;
    else                  typeSelAux5 = 3;

    if     (var == 1 | var == 2){ // VBS W+W+ SR mjj - mll
      return (float)(typeSelAux1+4*typeSelAux2);
    }
    else if(var == 3){ // VBS W+W+ SR mjj - njets
      return (float)(typeSelAux1+4*typeSelAux3);
    }
    else if(var == 4){ // VBS W+W+ SR mjj - detajj
      if(typeSelAux4 == 3) typeSelAux1 = std::max(typeSelAux1-1.0,0.0);
      return (float)(typeSelAux1+4*typeSelAux4);
    }
    else if(var == 5){ // VBS W+W+ SR mjj - dphijj
      return (float)(typeSelAux1+4*typeSelAux5);
    }
    else if(var == 9){ // VBS W+W+ btagged CR
      return (float)(typeSelAux1);
    }
    
    return 0.0;
  }
  else if(var == 20){ // mjj
    int typeSelAux = -1;
    if     (mjj <  700) typeSelAux = 0;
    else if(mjj <  900) typeSelAux = 1;
    else if(mjj < 1100) typeSelAux = 2;
    else if(mjj < 1300) typeSelAux = 3;
    else if(mjj < 1600) typeSelAux = 4;
    else if(mjj < 2000) typeSelAux = 5;
    else if(mjj < 2700) typeSelAux = 6;
    else                typeSelAux = 7;

    return (float)(typeSelAux);
  }
  else if(var == 21){ // mll
    float typeSelAux = -1;
    if     (mll <  50) typeSelAux = 0;
    else if(mll <  80) typeSelAux = 1;
    else if(mll < 110) typeSelAux = 2;
    else if(mll < 140) typeSelAux = 3;
    else if(mll < 170) typeSelAux = 4;
    else if(mll < 220) typeSelAux = 5;
    else if(mll < 300) typeSelAux = 6;
    else               typeSelAux = 7;

    return (float)(typeSelAux);
  }
  else if(var == 22){ // detajj
    float typeSelAux = -1;
    if     (detajj < 3.1) typeSelAux = 0;
    else if(detajj < 3.6) typeSelAux = 1;
    else if(detajj < 4.0) typeSelAux = 2;
    else if(detajj < 4.5) typeSelAux = 3;
    else if(detajj < 5.0) typeSelAux = 4;
    else if(detajj < 5.5) typeSelAux = 5;
    else if(detajj < 6.5) typeSelAux = 6;
    else                  typeSelAux = 7;

    return (float)(typeSelAux);
  }
  else if(var == 23){ // dphijj
    float typeSelAux = -1;
    if     (dphijj < 1.1) typeSelAux = 0;
    else if(dphijj < 1.8) typeSelAux = 1;
    else if(dphijj < 2.2) typeSelAux = 2;
    else if(dphijj < 2.5) typeSelAux = 3;
    else if(dphijj < 2.7) typeSelAux = 4;
    else if(dphijj < 2.9) typeSelAux = 5;
    else if(dphijj < 3.0) typeSelAux = 6;
    else                  typeSelAux = 7;

    return (float)(typeSelAux);
  }
  else if(var == 10 || var == 11){
    int typeSelAux1 = -1;
    if     (mjj <  900) typeSelAux1 = 0;
    else if(mjj < 1300) typeSelAux1 = 1;
    else if(mjj < 2000) typeSelAux1 = 2;
    else                typeSelAux1 = 3;
  
    int typeSelAux2 = -1;
    if     (detajj < 3.75) typeSelAux2 = 0;
    else if(detajj < 4.75) typeSelAux2 = 1;
    else                   typeSelAux2 = 2;

    float typeSelAux3 = -1;
    if     (zepvv >= 0.25) typeSelAux3 = 0;
    else                   typeSelAux3 = 1;

    if     (var == 10){ // VBS WZ SR cut-based
      return (float)(typeSelAux1+4*typeSelAux2+12*typeSelAux3);
    }
    else if(var == 11){ // VBS WZ btagged CR
      return (float)(typeSelAux1);
    }
  }
  else if(var == 12){ // VBS WZ SR MVA based
    float bdtNew = std::min(std::max(bdt+1.0,0.001),1.999);
    float typeSelAux3 = -1;
    if     (zepvv >= 0.25) typeSelAux3 = 0;
    else                   typeSelAux3 = 1;

    return (float)(bdtNew+2.0*typeSelAux3);
    //return (float)(bdtNew);
  }
  return 0.0;
}


// Jet-lepton variables
float compute_jet_lepton_var(Vec_f pt, Vec_f eta, Vec_f phi, Vec_f mass, 
                             const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_f& mu_phi, const Vec_f& mu_mass,
                             const Vec_f& el_pt, const Vec_f& el_eta, const Vec_f& el_phi, const Vec_f& el_mass,
                             const float met_pt, const float met_phi, unsigned int var)
{
  if(mu_pt.size() + el_pt.size() == 0) return -1;
  if(pt.size() < 2) return -1;

  PtEtaPhiMVector p1(pt[0], eta[0], phi[0], mass[0]);
  PtEtaPhiMVector p2(pt[1], eta[1], phi[1], mass[1]);
  //if(p1.Pt() < p2.Pt()) printf("Pt jet reversed!\n");
  for(unsigned int i=0;i<pt.size();i++) {
    for(unsigned int j=i+1;j<pt.size();j++) {
      if(pt[i]<pt[j]) {
        float temp0 = pt[i]; float temp1 = eta[i]; float temp2 = phi[i]; float temp3 = mass[i];
        pt[i] = pt[j];	     eta[i] = eta[j];	   phi[i] = phi[j];      mass[i] = mass[j];
        pt[j] = temp0;	     eta[j] = temp1;	   phi[j] = temp2;	 mass[j] = temp3;
      }
    }
  }

  float deltaEtaJJ = fabs(p1.Eta()-p2.Eta());
  float maxZ = 0.0;
  float sumHT = p1.Pt() + p2.Pt() + met_pt;

  vector<PtEtaPhiMVector> p4mom;

  for(unsigned int i=0;i<mu_pt.size();i++) {
    p4mom.push_back(PtEtaPhiMVector(mu_pt[i],mu_eta[i],mu_phi[i],mu_mass[i]));
    if(fabs(mu_eta[i]-(p1.Eta()+p2.Eta())/2.)/deltaEtaJJ > maxZ) maxZ = fabs(mu_eta[i]-(p1.Eta()+p2.Eta())/2.)/deltaEtaJJ;
    sumHT += mu_pt[i];
  }

  for(unsigned int i=0;i<el_pt.size();i++) {
    p4mom.push_back(PtEtaPhiMVector(el_pt[i],el_eta[i],el_phi[i],el_mass[i]));   
    if(fabs(el_eta[i]-(p1.Eta()+p2.Eta())/2.)/deltaEtaJJ > maxZ) maxZ = fabs(el_eta[i]-(p1.Eta()+p2.Eta())/2.)/deltaEtaJJ;
    sumHT += el_pt[i];
  }

  PtEtaPhiMVector p4momVV = PtEtaPhiMVector(met_pt,0,met_phi,0);
  PtEtaPhiMVector p4momTot = PtEtaPhiMVector(met_pt,0,met_phi,0) + p1 + p2;
  for(unsigned int i=0; i<p4mom.size(); i++){
    p4momVV = p4momVV + p4mom[i];
    p4momTot = p4momTot + p4mom[i];
  }

  double theVar = 0;
  if     (var == 0) theVar = fabs(p4momVV.Eta()-(p1.Eta()+p2.Eta())/2.)/deltaEtaJJ;
  else if(var == 1) theVar = maxZ;
  else if(var == 2) theVar = sumHT;
  else if(var == 3) theVar = p4momVV.Pt();
  else if(var == 4) theVar = p4momTot.Pt();
  else if(var == 5) theVar = fabs(p4momVV.Eta()-p1.Eta());
  else if(var == 6) theVar = fabs(p4momVV.Eta()-p2.Eta());
  else if(var == 7) theVar = (p4momVV.Pt()-(p1+p2).Pt())/(p1+p2).Pt();
  return theVar;
}

// Jet variables
float compute_jet_var(Vec_f pt, Vec_f eta, Vec_f phi, Vec_f mass, unsigned int var)
{
  if(pt.size() < 2) return -1;
  PtEtaPhiMVector p1(pt[0], eta[0], phi[0], mass[0]);
  PtEtaPhiMVector p2(pt[1], eta[1], phi[1], mass[1]);
  //if(p1.Pt() < p2.Pt()) printf("Pt jet reversed!\n");
  for(unsigned int i=0;i<pt.size();i++) {
    for(unsigned int j=i+1;j<pt.size();j++) {
      if(pt[i]<pt[j]) {
        float temp0 = pt[i]; float temp1 = eta[i]; float temp2 = phi[i]; float temp3 = mass[i];
        pt[i] = pt[j];	     eta[i] = eta[j];	   phi[i] = phi[j];      mass[i] = mass[j];
        pt[j] = temp0;	     eta[j] = temp1;	   phi[j] = temp2;	 mass[j] = temp3;
      }
    }
  }

  double theVar = 0;
  if	 (var == 0) theVar = (p1 + p2).M();
  else if(var == 1) theVar = (p1 + p2).Pt();
  else if(var == 2) theVar = fabs(p1.Eta()-p2.Eta());
  else if(var == 3) theVar = deltaPhi(p1.Phi(), p2.Phi());
  else if(var == 4) theVar = p1.Pt();
  else if(var == 5) theVar = p2.Pt();
  else if(var == 6) theVar = abs(p1.Eta());
  else if(var == 7) theVar = abs(p2.Eta());
  return theVar;
}

// lepton+met variables
float compute_lmet_var(const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_f& mu_phi, const Vec_f& mu_jetRelIso,
                       const Vec_f& el_pt, const Vec_f& el_eta, const Vec_f& el_phi, const Vec_f& el_jetRelIso,
		       const float met_pt, const float met_phi,
		       unsigned int var)
{
   float ptl, etal, phil, ptCone;
   if(mu_pt.size() == 1){
       ptl = mu_pt[0]; etal = mu_eta[0]; phil = mu_phi[0]; ptCone = mu_pt[0]*(1+std::max(mu_jetRelIso[0],0.0f))*0.9;
   }
   else if(el_pt.size() == 1){
       ptl = el_pt[0]; etal = el_eta[0]; phil = el_phi[0]; ptCone = el_pt[0]*(1+std::max(el_jetRelIso[0],0.0f))*0.9;
   }
   else {
      return 0;
   }

   double theVar = 0;
   if     (var == 0) theVar = std::sqrt(2*ptl*met_pt*(1-std::cos(deltaPhi(phil,met_phi))));
   else if(var == 1) theVar = deltaPhi(phil,met_phi);
   else if(var == 2) theVar = std::sqrt(2*35.0*met_pt*(1-std::cos(deltaPhi(phil,met_phi))));
   else if(var == 3) theVar = ptl;
   else if(var == 4) theVar = etal;
   else if(var == 5) theVar = phil;
   else if(var == 6) theVar = fabs(etal);
   else if(var == 7) theVar = std::max(ptCone, 10.001f);

   theVar = std::min(theVar, 199.999);
   
   return theVar;
}

// Dilepton variables
float compute_ll_var(const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_f& mu_phi, const Vec_f& mu_mass,
                     const Vec_f& el_pt, const Vec_f& el_eta, const Vec_f& el_phi, const Vec_f& el_mass,
		     unsigned int var)
{
   if(mu_pt.size() + el_pt.size() != 2) return 0;

   float pt[2], eta[2], phi[2], mass[2];
   if(mu_pt.size() == 2){
       pt[0] = mu_pt[0]; eta[0] = mu_eta[0]; phi[0] = mu_phi[0]; mass[0] = mu_mass[0];
       pt[1] = mu_pt[1]; eta[1] = mu_eta[1]; phi[1] = mu_phi[1]; mass[1] = mu_mass[1];
   }
   else if(el_pt.size() == 2){
       pt[0] = el_pt[0]; eta[0] = el_eta[0]; phi[0] = el_phi[0]; mass[0] = el_mass[0];
       pt[1] = el_pt[1]; eta[1] = el_eta[1]; phi[1] = el_phi[1]; mass[1] = el_mass[1];
   }
   else if(mu_pt.size() == 1 && el_pt.size() == 1){
       pt[0] = mu_pt[0]; eta[0] = mu_eta[0]; phi[0] = mu_phi[0]; mass[0] = mu_mass[0];
       pt[1] = el_pt[0]; eta[1] = el_eta[0]; phi[1] = el_phi[0]; mass[1] = el_mass[0];
   }
   else {
      return 0;
   }

   PtEtaPhiMVector p1(pt[0],eta[0],phi[0],mass[0]);
   PtEtaPhiMVector p2(pt[1],eta[1],phi[1],mass[1]);
   if(pt[0] < pt[1]){
     PtEtaPhiMVector paux = p2;
     p2 = p1;
     p1 = paux;
   }
   if(p1.Pt() < p2.Pt()) printf("Pt lepton reversed!\n");

   double theVar = 0;
   if     (var == 0) theVar = (p1 + p2).M();
   else if(var == 1) theVar = (p1 + p2).Pt();
   else if(var == 2) theVar = deltaR(p1.Eta(), p1.Phi(), p2.Eta(), p2.Phi());
   else if(var == 3) theVar = deltaPhi(p1.Phi(), p2.Phi());
   else if(var == 4) theVar = p1.Pt();
   else if(var == 5) theVar = p2.Pt();
   else if(var == 6) theVar = p1.Eta();
   else if(var == 7) theVar = p2.Eta();
   return theVar;
}

// Trilepton variables
float compute_3l_var(const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_f& mu_phi, const Vec_f& mu_mass, const Vec_f& mu_charge,
                     const Vec_f& el_pt, const Vec_f& el_eta, const Vec_f& el_phi, const Vec_f& el_mass, const Vec_f& el_charge,
		     const float met_pt, const float met_phi, unsigned int var)
{
   if(mu_pt.size() + el_pt.size() != 3) return 0;

   vector<PtEtaPhiMVector> p4mom;
   vector<int> charge, ltype;
   if     (mu_pt.size() == 3){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[1],mu_eta[1],mu_phi[1],mu_mass[1])); charge.push_back(mu_charge[1]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[2],mu_eta[2],mu_phi[2],mu_mass[2])); charge.push_back(mu_charge[2]); ltype.push_back(0);
   }
   else if(mu_pt.size() == 2){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[1],mu_eta[1],mu_phi[1],mu_mass[1])); charge.push_back(mu_charge[1]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 1){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[1],el_eta[1],el_phi[1],el_mass[1])); charge.push_back(el_charge[1]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 0){
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[1],el_eta[1],el_phi[1],el_mass[1])); charge.push_back(el_charge[1]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[2],el_eta[2],el_phi[2],el_mass[2])); charge.push_back(el_charge[2]); ltype.push_back(1);
   }
   else {
      printf("3l impossible combination\n");
      return 0;
   }

   for(unsigned int i=0; i<p4mom.size(); i++){
     for(unsigned int j=i+1; j<p4mom.size(); j++){
       if(p4mom[i].Pt() < p4mom[j].Pt()){
         PtEtaPhiMVector paux = p4mom[j]; int chargeaux = charge[j]; int ltypeaux = ltype[j];
         p4mom[j] = p4mom[i];                 charge[j] = charge[i];     ltype[j] = ltype[i];
         p4mom[i] = paux;                     charge[i] = chargeaux;     ltype[i] = ltypeaux;
       }
     }
   }

   float mllmin = 10000; float drllmin = 10000; float mllAllmin = 10000;
   PtEtaPhiMVector p4momTot = p4mom[0];
   for(unsigned int i=0; i<p4mom.size(); i++){
     if(i != 0) p4momTot = p4momTot + p4mom[i];
     for(unsigned int j=i+1; j<p4mom.size(); j++){
       if((p4mom[i]+p4mom[j]).M() < mllAllmin) mllAllmin = (p4mom[i]+p4mom[j]).M();
       if(charge[i] == charge[j]) continue;
       if((p4mom[i]+p4mom[j]).M() < mllmin) mllmin = (p4mom[i]+p4mom[j]).M();
       if(deltaR(p4mom[i].Eta(),p4mom[i].Phi(),p4mom[j].Eta(),p4mom[j].Phi()) < drllmin){
         drllmin = deltaR(p4mom[i].Eta(), p4mom[i].Phi(), p4mom[j].Eta(), p4mom[j].Phi());
       }
     }
   }

   double mllZ = 10000; double mllSSZ = 10000;
   int tagZ[2] = {-1, -1}; int tagW = -1;
   double theVar = 0;
   if     (var == 0) theVar = p4momTot.M();
   else if(var == 1) theVar = mllmin;
   else if(var == 2) theVar = drllmin;
   else if(var == 3) theVar = p4mom[0].Pt();
   else if(var == 4) theVar = p4mom[1].Pt();
   else if(var == 5) theVar = p4mom[2].Pt();
   else if(var == 6) theVar = p4mom[0].Eta();
   else if(var == 7) theVar = p4mom[1].Eta();
   else if(var == 8) theVar = p4mom[2].Eta();
   else if(var == 9) theVar = mllAllmin;
   else {
     for(int i=0; i<3; i++){
       for(int j=i+1; j<3; j++){  
         if(charge[i] != charge[j] && ltype[i] == ltype[j]){
           if(fabs((p4mom[i]+p4mom[j]).M()-91.1876) < fabs(mllZ-91.1876)) {
	     mllZ = (p4mom[i]+p4mom[j]).M();
	     tagZ[0] = i;
	     tagZ[1] = j;
	   }
         }
         if(charge[i] == charge[j] && ltype[i] == ltype[j]){
           if(fabs((p4mom[i]+p4mom[j]).M()-91.1876) < fabs(mllSSZ-91.1876)) {
	     mllSSZ = (p4mom[i]+p4mom[j]).M();
	   }
         }
       }
     }
     if(var == 11) theVar = mllSSZ;
     else if(tagZ[0] == -1) return -1;
     for(int i=0; i<3; i++){
       if(i != tagZ[0] && i != tagZ[1]) tagW = i;
     }
     
     if     (var == 10) theVar = mllZ;
     else if(var == 12) theVar = p4mom[tagZ[0]].Pt();
     else if(var == 13) theVar = p4mom[tagZ[1]].Pt();
     else if(var == 14) theVar = p4mom[tagW].Pt();
     else if(var == 15) theVar = p4mom[tagW].Eta();
     else if(var == 16) theVar = std::sqrt(2*p4mom[tagW].Pt()*met_pt*(1-std::cos(deltaPhi(p4mom[tagW].Phi(),met_phi))));
   }
   return theVar;
}

// Fourlepton variables
float compute_4l_var(const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_f& mu_phi, const Vec_f& mu_mass, const Vec_f& mu_charge,
                     const Vec_f& el_pt, const Vec_f& el_eta, const Vec_f& el_phi, const Vec_f& el_mass, const Vec_f& el_charge,
		     const float met_pt, const float met_phi, unsigned int var)
{
   if(mu_pt.size() + el_pt.size() != 4) return 0;

   vector<PtEtaPhiMVector> p4mom;
   vector<int> charge, ltype;
   if     (mu_pt.size() == 4){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[1],mu_eta[1],mu_phi[1],mu_mass[1])); charge.push_back(mu_charge[1]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[2],mu_eta[2],mu_phi[2],mu_mass[2])); charge.push_back(mu_charge[2]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[3],mu_eta[3],mu_phi[3],mu_mass[3])); charge.push_back(mu_charge[3]); ltype.push_back(0);
   }
   else if(mu_pt.size() == 3){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[1],mu_eta[1],mu_phi[1],mu_mass[1])); charge.push_back(mu_charge[1]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[2],mu_eta[2],mu_phi[2],mu_mass[2])); charge.push_back(mu_charge[2]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 2){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[1],mu_eta[1],mu_phi[1],mu_mass[1])); charge.push_back(mu_charge[1]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[1],el_eta[1],el_phi[1],el_mass[1])); charge.push_back(el_charge[1]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 1){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[1],el_eta[1],el_phi[1],el_mass[1])); charge.push_back(el_charge[1]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[2],el_eta[2],el_phi[2],el_mass[2])); charge.push_back(el_charge[2]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 0){
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[1],el_eta[1],el_phi[1],el_mass[1])); charge.push_back(el_charge[1]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[2],el_eta[2],el_phi[2],el_mass[2])); charge.push_back(el_charge[2]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[3],el_eta[3],el_phi[3],el_mass[3])); charge.push_back(el_charge[3]); ltype.push_back(1);
   }
   else {
      printf("4l impossible combination\n");
      return 0;
   }

   for(unsigned int i=0; i<p4mom.size(); i++){
     for(unsigned int j=i+1; j<p4mom.size(); j++){
       if(p4mom[i].Pt() < p4mom[j].Pt()){
         PtEtaPhiMVector paux = p4mom[j]; int chargeaux = charge[j]; int ltypeaux = ltype[j];
         p4mom[j] = p4mom[i];                 charge[j] = charge[i];     ltype[j] = ltype[i];
         p4mom[i] = paux;                     charge[i] = chargeaux;     ltype[i] = ltypeaux;
       }
     }
   }

   float mllmin = 10000; float ptmax = 0;
   PtEtaPhiMVector p4momTot = p4mom[0];
   for(unsigned int i=0; i<p4mom.size(); i++){
     if(p4mom[i].Pt() > ptmax) ptmax = p4mom[i].Pt();
     if(i != 0) p4momTot = p4momTot + p4mom[i];
     for(unsigned int j=i+1; j<p4mom.size(); j++){
       if((p4mom[i]+p4mom[j]).M() < mllmin) mllmin = (p4mom[i]+p4mom[j]).M();
     }
   }
   
   float mllZ1 = 100000; float mllZ2 = 100000; float mllxy = 0;
   int tagZ1[2] = {-1, -1}; int tagZ2[2] = {-1, -1};
   float theVar = 0;
   if     (var == 0) theVar = p4momTot.M();
   else if(var == 1) theVar = ptmax;
   else if(var == 2) theVar = mllmin;
   else {
     for(int i=0; i<4; i++){
       for(int j=i+1; j<4; j++){  
         if(charge[i] != charge[j] && ltype[i] == ltype[j]){
           if(fabs((p4mom[i]+p4mom[j]).M()-91.1876) < fabs(mllZ1-91.1876)) {
	     mllZ1 = (p4mom[i]+p4mom[j]).M();
	     tagZ1[0] = i;
	     tagZ1[1] = j;
	   }
         }
       }
     }
     if(tagZ1[0] == -1) return -1;
     for(int i=0; i<4; i++){
       if(i != tagZ1[0] && i != tagZ1[1] && tagZ2[0] == -1) tagZ2[0] = i;
     }
     for(int i=0; i<4; i++){
       if(i != tagZ1[0] && i != tagZ1[1] && i != tagZ2[0]) tagZ2[1] = i;
     }

     if(charge[tagZ2[0]] != charge[tagZ2[1]] && ltype[tagZ2[0]] == ltype[tagZ2[1]]){     
       mllZ2 = (p4mom[tagZ2[0]]+p4mom[tagZ2[1]]).M();
     }
     else if(tagZ2[0] >= 0 && tagZ2[1] >= 0 && charge[tagZ2[0]] != charge[tagZ2[1]]){     
       mllxy = (p4mom[tagZ2[0]]+p4mom[tagZ2[1]]).M();
     }
     else if(tagZ2[0] >= 0 && tagZ2[1] >= 0){     
       mllxy = 0.0;
       printf("mllxy same-sign leptons %d %d\n",tagZ2[0],tagZ2[1]);
     }
     else {     
       printf("mllxy problem %d %d\n",tagZ2[0],tagZ2[1]);
     }
     
     if     (var ==  3) theVar = fabs(mllZ1-91.1876);
     else if(var ==  4) theVar = fabs(mllZ2-91.1876);
     else if(var ==  5) theVar = p4mom[tagZ1[0]].Pt();
     else if(var ==  6) theVar = p4mom[tagZ1[1]].Pt();
     else if(var ==  7) theVar = p4mom[tagZ2[0]].Pt();
     else if(var ==  8) theVar = p4mom[tagZ2[1]].Pt();
     else if(var ==  9) theVar = mllxy;
     else if(var == 10) theVar = (p4mom[tagZ1[0]]+p4mom[tagZ1[1]]).Pt();
     else if(var == 11) theVar = (p4mom[tagZ2[0]]+p4mom[tagZ2[1]]).Pt();
     else if(var == 12) theVar = std::sqrt(2*(p4mom[tagZ2[0]]+p4mom[tagZ2[1]]).Pt()*met_pt*(1-std::cos(deltaPhi((p4mom[tagZ2[0]]+p4mom[tagZ2[1]]).Phi(),met_phi))));
   }
   return theVar;
}


// Multilepton variables
float compute_nl_var(const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_f& mu_phi, const Vec_f& mu_mass, const Vec_f& mu_charge,
                     const Vec_f& el_pt, const Vec_f& el_eta, const Vec_f& el_phi, const Vec_f& el_mass, const Vec_f& el_charge,
		     const float met_pt, const float met_phi, unsigned int var)
{
   if(mu_pt.size() + el_pt.size() < 2 || mu_pt.size() + el_pt.size() > 4) return 0;

   vector<PtEtaPhiMVector> p4mom;
   vector<int> charge, ltype;
   if     (mu_pt.size() == 4 && el_pt.size() == 0){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[1],mu_eta[1],mu_phi[1],mu_mass[1])); charge.push_back(mu_charge[1]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[2],mu_eta[2],mu_phi[2],mu_mass[2])); charge.push_back(mu_charge[2]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[3],mu_eta[3],mu_phi[3],mu_mass[3])); charge.push_back(mu_charge[3]); ltype.push_back(0);
   }
   else if(mu_pt.size() == 3 && el_pt.size() == 1){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[1],mu_eta[1],mu_phi[1],mu_mass[1])); charge.push_back(mu_charge[1]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[2],mu_eta[2],mu_phi[2],mu_mass[2])); charge.push_back(mu_charge[2]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 2 && el_pt.size() == 2){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[1],mu_eta[1],mu_phi[1],mu_mass[1])); charge.push_back(mu_charge[1]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[1],el_eta[1],el_phi[1],el_mass[1])); charge.push_back(el_charge[1]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 1 && el_pt.size() == 3){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[1],el_eta[1],el_phi[1],el_mass[1])); charge.push_back(el_charge[1]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[2],el_eta[2],el_phi[2],el_mass[2])); charge.push_back(el_charge[2]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 0 && el_pt.size() == 4){
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[1],el_eta[1],el_phi[1],el_mass[1])); charge.push_back(el_charge[1]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[2],el_eta[2],el_phi[2],el_mass[2])); charge.push_back(el_charge[2]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[3],el_eta[3],el_phi[3],el_mass[3])); charge.push_back(el_charge[3]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 3 && el_pt.size() == 0){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[1],mu_eta[1],mu_phi[1],mu_mass[1])); charge.push_back(mu_charge[1]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[2],mu_eta[2],mu_phi[2],mu_mass[2])); charge.push_back(mu_charge[2]); ltype.push_back(0);
   }
   else if(mu_pt.size() == 2 && el_pt.size() == 1){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[1],mu_eta[1],mu_phi[1],mu_mass[1])); charge.push_back(mu_charge[1]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 1 && el_pt.size() == 2){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[1],el_eta[1],el_phi[1],el_mass[1])); charge.push_back(el_charge[1]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 0 && el_pt.size() == 3){
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[1],el_eta[1],el_phi[1],el_mass[1])); charge.push_back(el_charge[1]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[2],el_eta[2],el_phi[2],el_mass[2])); charge.push_back(el_charge[2]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 2 && el_pt.size() == 0){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(mu_pt[1],mu_eta[1],mu_phi[1],mu_mass[1])); charge.push_back(mu_charge[1]); ltype.push_back(0);
   }
   else if(mu_pt.size() == 1 && el_pt.size() == 1){
       p4mom.push_back(PtEtaPhiMVector(mu_pt[0],mu_eta[0],mu_phi[0],mu_mass[0])); charge.push_back(mu_charge[0]); ltype.push_back(0);
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
   }
   else if(mu_pt.size() == 0 && el_pt.size() == 2){
       p4mom.push_back(PtEtaPhiMVector(el_pt[0],el_eta[0],el_phi[0],el_mass[0])); charge.push_back(el_charge[0]); ltype.push_back(1);
       p4mom.push_back(PtEtaPhiMVector(el_pt[1],el_eta[1],el_phi[1],el_mass[1])); charge.push_back(el_charge[1]); ltype.push_back(1);
   }
   else {
      printf("Impossible combination %lu %lu\n",mu_pt.size(),el_pt.size());
      return 0;
   }

   for(unsigned int i=0; i<p4mom.size(); i++){
     for(unsigned int j=i+1; j<p4mom.size(); j++){
       if(p4mom[i].Pt() < p4mom[j].Pt()){
         PtEtaPhiMVector paux = p4mom[j]; int chargeaux = charge[j]; int ltypeaux = ltype[j];
         p4mom[j] = p4mom[i];                 charge[j] = charge[i];     ltype[j] = ltype[i];
         p4mom[i] = paux;                     charge[i] = chargeaux;     ltype[i] = ltypeaux;
       }
     }
   }

   float mllmin = 10000;
   PtEtaPhiMVector p4momTot = p4mom[0];
   for(unsigned int i=0; i<p4mom.size(); i++){
     if(i != 0) p4momTot = p4momTot + p4mom[i];
     for(unsigned int j=i+1; j<p4mom.size(); j++){
       if((p4mom[i]+p4mom[j]).M() < mllmin) mllmin = (p4mom[i]+p4mom[j]).M();
     }
   }

   float theVar = -1;
   if     (var == 0) theVar = p4momTot.M();
   else if(var == 1) theVar = mllmin;
   else if(var == 2) {
     if     (p4mom.size() == 2 && ltype[0] == 0 && ltype[1] == 0) theVar = 0.;
     else if(p4mom.size() == 2 && ltype[0] == 1 && ltype[1] == 1) theVar = 1.;
     else if(p4mom.size() == 2 && ltype[0] == 0 && ltype[1] == 1) theVar = 2.;
     else if(p4mom.size() == 2 && ltype[0] == 1 && ltype[1] == 0) theVar = 3.;
     else if(p4mom.size() == 3) theVar = 4.;
     else if(p4mom.size() == 4) theVar = 5.;
     else printf("Impossible ltype %lu %lu\n",mu_pt.size(),el_pt.size());
   }
   else {
     if     (var ==  3) theVar = p4mom[0].Pt();
     else if(var ==  4) theVar = p4mom[p4mom.size()-1].Pt();
     else if(var ==  5) theVar = abs(p4mom[0].Eta());
     else if(var ==  6) theVar = abs(p4mom[p4mom.size()-1].Eta());
     else if(var ==  7 || var == 8) {
       double dPhilMETMin = deltaPhi(p4mom[0].Phi(),met_phi);
       for(unsigned int i=1; i<p4mom.size(); i++){
         if(deltaPhi(p4mom[i].Phi(),met_phi) < dPhilMETMin) dPhilMETMin = deltaPhi(p4mom[i].Phi(),met_phi);
       }
       if(var == 7) theVar = dPhilMETMin;
       else {
         if(dPhilMETMin > TMath::Pi()/2) theVar = met_pt;
         else theVar = met_pt*sin(dPhilMETMin);
       }
     }
     else if(var ==  9) {
       PtEtaPhiMVector p4metmom = PtEtaPhiMVector(met_pt,0.0,met_phi,0.0);
       p4metmom = p4metmom + p4momTot;
       theVar = p4metmom.Pt();
     }
     else if(var ==  10) {
       theVar = p4momTot.M()/sqrt((p4mom[0].Pt()/(p4mom[0].Pt()+met_pt))*(p4mom[1].Pt()/(p4mom[1].Pt()+met_pt)));
     }
   }
   return theVar;
}

int applySkim(const Vec_f& mu_pt, const Vec_f& mu_eta, const Vec_f& mu_phi, const Vec_f& mu_mass,
              const Vec_f& el_pt, const Vec_f& el_eta, const Vec_f& el_phi, const Vec_f& el_mass,
	      const int lep_charge, const float met_pt)
{
   if     (mu_pt.size() + el_pt.size() < 2) return 0;
   else if(mu_pt.size() + el_pt.size() > 2) return 1;

   float pt[2], eta[2], phi[2], mass[2];
   if(mu_pt.size() == 2){
       pt[0] = mu_pt[0]; eta[0] = mu_eta[0]; phi[0] = mu_phi[0]; mass[0] = mu_mass[0];
       pt[1] = mu_pt[1]; eta[1] = mu_eta[1]; phi[1] = mu_phi[1]; mass[1] = mu_mass[1];
   }
   else if(el_pt.size() == 2){
       pt[0] = el_pt[0]; eta[0] = el_eta[0]; phi[0] = el_phi[0]; mass[0] = el_mass[0];
       pt[1] = el_pt[1]; eta[1] = el_eta[1]; phi[1] = el_phi[1]; mass[1] = el_mass[1];
   }
   else if(mu_pt.size() == 1 && el_pt.size() == 1){
       pt[0] = mu_pt[0]; eta[0] = mu_eta[0]; phi[0] = mu_phi[0]; mass[0] = mu_mass[0];
       pt[1] = el_pt[0]; eta[1] = el_eta[0]; phi[1] = el_phi[0]; mass[1] = el_mass[0];
   }
   else {
      printf("This lep comb can not happen\n");
      return 0;
   }

   PtEtaPhiMVector p1(pt[0],eta[0],phi[0],mass[0]);
   PtEtaPhiMVector p2(pt[1],eta[1],phi[1],mass[1]);
   if(pt[0] < pt[1]){
     PtEtaPhiMVector paux = p2;
     p2 = p1;
     p1 = paux;
   }
   if(p1.Pt() < p2.Pt()) printf("Pt lepton reversed!\n");

   double mll = (p1 + p2).M();
   if(mll <= 10) return 0;

   if     (lep_charge != 0) return 2;
   else if(met_pt > 50 && (p1 + p2).Pt() > 50) return 3;
   else return 4;

   printf("This can not happen\n");
   return 0;
}

// Select meson-photon pair
Vec_i HiggsCandFromRECO(const Vec_f& meson_pt, const Vec_f& meson_eta, const Vec_f& meson_phi, const Vec_f& meson_mass,
                        const Vec_f& ph_pt, const Vec_f& ph_eta, const Vec_f& ph_phi) {

  Vec_i idx(2, -1); // initialize with -1 a vector of size 2
  if(ph_pt.size() == 0 || meson_pt.size() == 0) return idx;

  //float Minv = -1;
  //float ptHiggs = -1;
  float ptCandMax=0;

  PtEtaPhiMVector p_ph(ph_pt[0], ph_eta[0], ph_phi[0], 0);
  int indexPhoton = 0;
  for(unsigned int i=1; i<ph_pt.size(); i++){
    if(ph_pt[i] > p_ph.Pt()) {
      p_ph.SetPt(ph_pt[i]);
      p_ph.SetEta(ph_eta[i]);
      p_ph.SetPhi(ph_phi[i]);
      indexPhoton = i;
    }
  }

  // loop over all the phiCand
  for (unsigned int i=0; i<meson_pt.size(); i++) {

    PtEtaPhiMVector p_meson(meson_pt[i], meson_eta[i], meson_phi[i], meson_mass[i]);
    // save the leading Pt
    float ptCand = p_meson.pt();
    if( ptCand < ptCandMax ) continue;
    ptCandMax=ptCand;
    //Minv = (p_meson + p_ph).mass();
    //ptHiggs = (p_meson + p_ph).pt();
    idx[0] = i;
    idx[1] = indexPhoton;
  }

  return idx;

}

float makeRapidity(const float& pt, const float& eta, const float& phi, const float& m) {
  PtEtaPhiMVector p_x(pt, eta, phi, m);
  return p_x.Rapidity();
}

Vec_f computeMomentum(const Vec_f& pt, const Vec_f& eta, const Vec_f& phi, const Vec_f& m) {

  Vec_f momentum(pt.size(), 1.0);
  for (unsigned int idx = 0; idx < pt.size(); ++idx) {
    PtEtaPhiMVector particle(pt[idx], eta[idx], phi[idx], m[idx]);
    momentum[idx] = particle.P();
  }
  return momentum;
}

// cleaning jets close-by to the meson
Vec_b cleaningJetFromMeson(Vec_f & Jeta, Vec_f & Jphi, float & eta, float & phi) {

  Vec_b mask(Jeta.size(), true);
  for (unsigned int idx = 0; idx < Jeta.size(); ++idx) {
    if(deltaR(Jeta[idx], Jphi[idx], eta, phi)<0.4) mask[idx] = false;
  }
  return mask;
}

// cleaning jets close-by to the leptons
Vec_b cleaningJetFromLepton(Vec_f & Jeta, Vec_f & Jphi, Vec_f & Leta, Vec_f & Lphi) {

  Vec_b mask(Jeta.size(), true);
  for (unsigned int jdx = 0; jdx < Jeta.size(); ++jdx) {
    for (unsigned int ldx = 0; ldx < Leta.size(); ++ldx) {
      if(deltaR(Jeta[jdx], Jphi[jdx], Leta[ldx], Lphi[ldx]) < 0.4) {mask[jdx] = false; break;}
    }
  }
  return mask;
}

int compute_nPileupJets(const Vec_f& jet_pt, const Vec_f& jet_eta, const Vec_f& jet_phi,
                          const Vec_f& genjet_pt, const Vec_f& genjet_eta, const Vec_f& genjet_phi){

  int nPileupJets = 0;
  for (unsigned int ij = 0; ij < jet_pt.size(); ++ij) {
    bool isPileupJet = true;
    for (unsigned int ig = 0; ig < genjet_pt.size(); ++ig) {
      if(genjet_pt[ig] <= 10) continue;
      if(deltaR(jet_eta[ij], jet_phi[ij], genjet_eta[ig], genjet_phi[ig]) < 0.4) {isPileupJet = false; break;}
    }
    if(isPileupJet == true) nPileupJets++;
  }
  
  int nPileupJetsPlot = std::min((int)jet_pt.size(),3);
  if(nPileupJets > 0){
    if     (jet_pt.size() == 1 && nPileupJets == 1) nPileupJetsPlot = 3 + 1;
    else if(jet_pt.size() == 2 && nPileupJets == 1) nPileupJetsPlot = 3 + 2;
    else if(jet_pt.size() == 2 && nPileupJets == 2) nPileupJetsPlot = 3 + 3;
    else if(jet_pt.size() >= 3 && nPileupJets == 1) nPileupJetsPlot = 3 + 4;
    else if(jet_pt.size() >= 3 && nPileupJets == 2) nPileupJetsPlot = 3 + 5;
    else if(jet_pt.size() >= 3 && nPileupJets == 3) nPileupJetsPlot = 3 + 6;
  }

  return nPileupJetsPlot;
}

// Minv2
std::pair<float, float>  Minv2(const float& pt, const float& eta, const float& phi, const float& m,
                               const float& ph_pt, const float& ph_eta, const float& ph_phi, const float& ph_m) {

  PtEtaPhiMVector p_M(pt, eta, phi, m);
  PtEtaPhiMVector p_ph(ph_pt, ph_eta, ph_phi, ph_m);

  float Minv = (p_M + p_ph).mass();
  float ptPair = (p_M + p_ph).pt();

  std::pair<float, float> pairRECO = std::make_pair(Minv , ptPair);
  return pairRECO;
}

float compute_gen_ptvv(const Vec_f& GenDressedLepton_pt, const Vec_f& GenDressedLepton_phi, const float met_pt, const float met_phi){

  if(GenDressedLepton_pt.size() < 2) return 0.0;

  PtEtaPhiMVector p4mom = PtEtaPhiMVector(met_pt,0.0,met_phi,0.0);
  for(unsigned int i=0; i<GenDressedLepton_pt.size(); i++){
    p4mom = p4mom + PtEtaPhiMVector(GenDressedLepton_pt[i],0.0,GenDressedLepton_phi[i],0.0);
  }

  return p4mom.Pt();
}

float compute_ptww_weight(const Vec_f& GenDressedLepton_pt, const Vec_f& GenDressedLepton_phi, const float met_pt, const float met_phi, int nsel){

  if(GenDressedLepton_pt.size() < 2) return 1.0;

  PtEtaPhiMVector p4mom = PtEtaPhiMVector(met_pt,0.0,met_phi,0.0);
  for(unsigned int i=0; i<GenDressedLepton_pt.size(); i++){
    p4mom = p4mom + PtEtaPhiMVector(GenDressedLepton_pt[i],0.0,GenDressedLepton_phi[i],0.0);
  }
  double ptww = std::min(p4mom.Pt(),499.999);

  double sf = 1.0;
  if     (nsel == 0){
    const TH1D& hcorr = histo_wwpt;
    sf = getValFromTH1(hcorr, ptww);
  }
  else if(nsel == 1){
    const TH1D& hcorr = histo_wwpt_scaleup;
    sf = getValFromTH1(hcorr, ptww);
  }
  else if(nsel == 2){
    const TH1D& hcorr = histo_wwpt_scaledown;
    sf = getValFromTH1(hcorr, ptww);
  }
  else if(nsel == 3){
    const TH1D& hcorr = histo_wwpt_resumup;
    sf = getValFromTH1(hcorr, ptww);
  }
  else if(nsel == 4){
    const TH1D& hcorr = histo_wwpt_resumdown;
    sf = getValFromTH1(hcorr, ptww);
  }
  else {
    printf("WRONG option!\n");
  }
  bool debug = false;
  if(debug) printf("ptww_weights(%lu): %f %f\n",GenDressedLepton_pt.size(),ptww,sf);
  return sf;
}

// compute category
int compute_category(const int mc, const int typeFake, const int typeWS, const int nFake, const int nTight, const int nWS){
  if     (nFake > nTight) return typeFake;
  else if(nFake < nTight) {printf("IMPOSSIBLE compute_category\n"); return -1;}
  if(nWS > 0) return typeWS;
  return mc;
}

// compute gen category
int compute_gen_category(const int mc, const int ngood_GenJets, const int ngood_GenDressedLeptons, const Vec_i& GenDressedLepton_pdgId, 
                         const Vec_b& GenDressedLepton_hasTauAnc,
                         const Vec_f& GenDressedLepton_pt, const Vec_f& GenDressedLepton_eta, const Vec_f& GenDressedLepton_phi, const Vec_f& GenDressedLepton_mass,
                         const int applyTightSel){
  if(ngood_GenDressedLeptons <= 1) return 0;
  if(GenDressedLepton_pdgId[0] * GenDressedLepton_pdgId[1] > 0)  return 0;
  if(abs(GenDressedLepton_pdgId[0]) == abs(GenDressedLepton_pdgId[1]))  return 0;

  if(applyTightSel >= 1) {
    if(GenDressedLepton_pt[1] > GenDressedLepton_pt[0]) {printf("PROBLEM, ptl2 > ptl1 at gen level\n");}
    bool passTightGenSel = GenDressedLepton_pt[0] > 25 &&  GenDressedLepton_pt[1] > 20;
    if(applyTightSel >= 2) passTightGenSel = passTightGenSel && GenDressedLepton_hasTauAnc[0] == 0 && GenDressedLepton_hasTauAnc[1] == 0;
    if(applyTightSel >= 3) {
      float mllGen = Minv2(GenDressedLepton_pt[0], GenDressedLepton_eta[0], GenDressedLepton_phi[0], GenDressedLepton_mass[0],
                           GenDressedLepton_pt[1], GenDressedLepton_eta[1], GenDressedLepton_phi[1], GenDressedLepton_mass[1]).first;
      passTightGenSel = passTightGenSel && mllGen > 85;
    }
    if(passTightGenSel == false) return 0;
  }

  if     (ngood_GenJets == 0) return 1;
  else if(ngood_GenJets == 1) return 2;
  else if(ngood_GenJets >= 2) return 3;
  return 0;
}

// compute vbs gen category
int compute_vbs_gen_category(const int nSel, const int ngood_GenJets, const Vec_f& good_GenJet_pt, const Vec_f& good_GenJet_eta,  const Vec_f& good_GenJet_phi, const Vec_f& good_GenJet_mass,
                             const int ngood_GenDressedLeptons, const Vec_i& GenDressedLepton_pdgId, const Vec_b& GenDressedLepton_hasTauAnc,
                             const Vec_f& GenDressedLepton_pt, const Vec_f& GenDressedLepton_eta, const Vec_f& GenDressedLepton_phi, const Vec_f& GenDressedLepton_mass,
                             const int applyTightSel){

  if(ngood_GenDressedLeptons <= 1) return 0;
  if(ngood_GenJets < 2) return 0;

  float mjjGen = Minv2(good_GenJet_pt[0], good_GenJet_eta[0], good_GenJet_phi[0], good_GenJet_mass[0],
                       good_GenJet_pt[1], good_GenJet_eta[1], good_GenJet_phi[1], good_GenJet_mass[1]).first;

  float mllGen = Minv2(GenDressedLepton_pt[0], GenDressedLepton_eta[0], GenDressedLepton_phi[0], GenDressedLepton_mass[0],
                       GenDressedLepton_pt[1], GenDressedLepton_eta[1], GenDressedLepton_phi[1], GenDressedLepton_mass[1]).first;

  float detajjGen = fabs(good_GenJet_eta[0]-good_GenJet_eta[1]);
  float dphijjGen = deltaPhi(good_GenJet_phi[0],good_GenJet_phi[1]);
 
  if(applyTightSel >= 1 && applyTightSel <= 10) {
    if(GenDressedLepton_pt[1] > GenDressedLepton_pt[0]) {printf("PROBLEM, ptl2 > ptl1 at gen level\n");}
    bool passTightGenSel = ngood_GenDressedLeptons == 2 && GenDressedLepton_pdgId[0] * GenDressedLepton_pdgId[1] > 0 &&
                           GenDressedLepton_pt[0] > 25 &&  GenDressedLepton_pt[1] > 20;
    if(applyTightSel >= 2) passTightGenSel = passTightGenSel && GenDressedLepton_hasTauAnc[0] == 0 && GenDressedLepton_hasTauAnc[1] == 0;
    if(applyTightSel >= 3) {
      passTightGenSel = passTightGenSel && mllGen > 20;
    }
    if(applyTightSel >= 4) {
      passTightGenSel = passTightGenSel && mjjGen > 500 && detajjGen > 2.5;
    }
    if(passTightGenSel == false) return 0;
  }
  else if(applyTightSel >= 11 && applyTightSel <= 20) {
    if(GenDressedLepton_pt[1] > GenDressedLepton_pt[0] || GenDressedLepton_pt[2] > GenDressedLepton_pt[1]) {printf("PROBLEM, ptl2 > ptl1 at gen level\n");}
    bool passTightGenSel = ngood_GenDressedLeptons == 3 &&
                           GenDressedLepton_pt[0] > 25 && GenDressedLepton_pt[1] > 20 && GenDressedLepton_pt[2] > 15;
    if(applyTightSel >= 12) passTightGenSel = passTightGenSel && GenDressedLepton_hasTauAnc[0] == 0 && GenDressedLepton_hasTauAnc[1] == 0 && GenDressedLepton_hasTauAnc[2] == 0;
    if(applyTightSel >= 13) {
      passTightGenSel = passTightGenSel && mjjGen > 500 && detajjGen > 2.5;
    }
    if(passTightGenSel == false) return 0;
  }

  if     (nSel == 1){
    if     (mjjGen <  900) return 1;
    else if(mjjGen < 1300) return 2;
    else if(mjjGen < 2000) return 3;
    else                   return 4;
  }
  else if(nSel == 2){
    if     (mllGen <  80) return 1;
    else if(mllGen < 140) return 2;
    else if(mllGen < 220) return 3;
    else                  return 4;
  }
  else if(nSel == 3){
    if     (ngood_GenJets == 2) return 1;
    else if(ngood_GenJets >= 3) return 2;
  }
  else if(nSel == 4){
    if     (detajjGen < 3.6) return 1;
    else if(detajjGen < 4.5) return 2;
    else if(detajjGen < 5.5) return 3;
    else                     return 4;
  }
  else if(nSel == 5){
    if     (dphijjGen < 1.8) return 1;
    else if(dphijjGen < 2.5) return 2;
    else if(dphijjGen < 2.9) return 3;
    else                     return 4;
  }
  
  return 0;
}

// compute vbs gen variables
int compute_vbs_gen_variables(const int nCat, const int ngood_GenJets, const Vec_f& good_GenJet_pt, const Vec_f& good_GenJet_eta,  const Vec_f& good_GenJet_phi, const Vec_f& good_GenJet_mass,
                              const int ngood_GenDressedLeptons, const Vec_i& GenDressedLepton_pdgId, const Vec_b& GenDressedLepton_hasTauAnc,
                              const Vec_f& GenDressedLepton_pt, const Vec_f& GenDressedLepton_eta, const Vec_f& GenDressedLepton_phi, const Vec_f& GenDressedLepton_mass){

  float genVar = -1;

  if     (nCat == 0 && ngood_GenJets >= 2){
    genVar = Minv2(good_GenJet_pt[0], good_GenJet_eta[0], good_GenJet_phi[0], good_GenJet_mass[0],
                   good_GenJet_pt[1], good_GenJet_eta[1], good_GenJet_phi[1], good_GenJet_mass[1]).first;
  }
  else if(nCat == 1 && ngood_GenDressedLeptons >= 2){
    genVar = Minv2(GenDressedLepton_pt[0], GenDressedLepton_eta[0], GenDressedLepton_phi[0], GenDressedLepton_mass[0],
                   GenDressedLepton_pt[1], GenDressedLepton_eta[1], GenDressedLepton_phi[1], GenDressedLepton_mass[1]).first;
  }

  return std::min(genVar,2899.999f);
}

// compute category
float compute_weights(const float weight, const float genWeight, const TString theCat,
                      const Vec_f& mu_genPartFlav, const Vec_f& el_genPartFlav, unsigned int var){
  if(theCat.Contains("WJetsToLNu") && genWeight > 10000) {
    printf("Huge genWeight: %f\n",genWeight);
    return 0.0;
  }
  if(var == 1) {
    bool isRealGenLep = true;
    for(unsigned int i=0;i<mu_genPartFlav.size();i++) {
       if(mu_genPartFlav[i] != 1 && mu_genPartFlav[i] != 15) {isRealGenLep = false; break;}
    }
    if(isRealGenLep == false) return 0.0;

    for(unsigned int i=0;i<el_genPartFlav.size();i++) {
       if(el_genPartFlav[i] != 1 && el_genPartFlav[i] != 15) {isRealGenLep = false; break;}
    }
    if(isRealGenLep == false) return 0.0;
  }
  return weight*genWeight;
}

// print information
int print_info(const UInt_t run, const UInt_t lumi, const ULong64_t event){

  printf("INFO: %d %d %llu\n",run,lumi,event);

  return 1;
}
