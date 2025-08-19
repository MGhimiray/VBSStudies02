#ifndef FUNCTIONS_H
#define FUNCTIONS_H

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

#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <cstdlib> //as stdlib.h      
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

std::unordered_map< UInt_t, std::vector< std::pair<UInt_t,UInt_t> > > jsonMap;

bool isGoodRunLS(const bool isData, const UInt_t run, const UInt_t lumi) {

  if(not isData) return true;

  if(jsonMap.find(run) == jsonMap.end()) return false; // run not found

  auto& validlumis = jsonMap.at(run);
  auto match = std::lower_bound(std::begin(validlumis), std::end(validlumis), lumi,
                               [](std::pair<unsigned int, unsigned int>& range, unsigned int val) { return range.second < val; });
  return match->first <= lumi && match->second >= lumi;
}

Vec_b cleaningBitmap(const Vec_i& Photon_vidNestedWPBitmap, int var, int cutBased) {

  Vec_b mask(Photon_vidNestedWPBitmap.size(), true);
  for(unsigned int i=0;i<Photon_vidNestedWPBitmap.size();i++) {
    if((Photon_vidNestedWPBitmap[i]>>var&3) >= cutBased) continue;
    mask[i] = false;
  }
  return mask;
}

Vec_b cleaningMask(Vec_i indices, int size) {

  Vec_b mask(size, true);
  for (int idx : indices) {
    if(idx < 0) continue;
    mask[idx] = false;
  }
  return mask;
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

#endif
