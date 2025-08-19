import ROOT
import os, json
from utilsCategory import plotCategory

# DeepJet
def getBTagCut_DeepJet(type,year):

    if(type < 0 or type > 2): return 100
    value = [0.7100, 0.2783, 0.0490]
    if(year == 20220):
       value[0] = 0.7183
       value[1] = 0.3086
       value[2] = 0.0583
    elif(year == 20221):
       value[0] = 0.7300
       value[1] = 0.3196
       value[2] = 0.0614
    elif(year == 20230):
       value[0] = 0.6553
       value[1] = 0.2431
       value[2] = 0.0479
    elif(year == 20231):
       value[0] = 0.6563
       value[1] = 0.2435
       value[2] = 0.0480
    elif(year == 20240):
       value[0] = 0.6563
       value[1] = 0.2435
       value[2] = 0.0480

    return value[type]

# PNet
def getBTagCut_PNet(type,year):

    if(type < 0 or type > 2): return 100
    value = [0.6734, 0.2450, 0.0470]
    if(year == 20220):
       value[0] = 0.6734
       value[1] = 0.2450
       value[2] = 0.0470
    elif(year == 20221):
       value[0] = 0.6915
       value[1] = 0.2605
       value[2] = 0.0499
    elif(year == 20230):
       value[0] = 0.6172
       value[1] = 0.1917
       value[2] = 0.0358
    elif(year == 20231):
       value[0] = 0.6133
       value[1] = 0.1919
       value[2] = 0.0359
    elif(year == 20240):
       value[0] = 0.6133
       value[1] = 0.1919
       value[2] = 0.0359

    return value[type]

# UnifiedParT
def getBTagCut(type,year):

    if(type < 0 or type > 2): return 100
    value = [0.8482, 0.4319, 0.0849]
    if(year == 20220):
       value[0] = 0.8482
       value[1] = 0.4319
       value[2] = 0.0849
    elif(year == 20221):
       value[0] = 0.8604
       value[1] = 0.4510
       value[2] = 0.0897
    elif(year == 20230):
       value[0] = 0.7969
       value[1] = 0.3487
       value[2] = 0.0681
    elif(year == 20231):
       value[0] = 0.7994
       value[1] = 0.3494
       value[2] = 0.0683
    elif(year == 20240):
       value[0] = 0.4648
       value[1] = 0.1272
       value[2] = 0.0246

    return value[type]

def selectionGenLepJet(df,ptlcut,ptjcut,etajcut):

    dftag =(df.Define("good_GenDressedLepton", "abs(GenDressedLepton_eta) < 2.5 && GenDressedLepton_pt > {0}".format(ptlcut))
              .Define("good_GenDressedLepton_hasTauAnc", "GenDressedLepton_hasTauAnc[good_GenDressedLepton]")
              .Define("good_GenDressedLepton_pt", "GenDressedLepton_pt[good_GenDressedLepton]")
              .Define("good_GenDressedLepton_eta", "GenDressedLepton_eta[good_GenDressedLepton]")
              .Define("good_GenDressedLepton_phi", "GenDressedLepton_phi[good_GenDressedLepton]")
              .Define("good_GenDressedLepton_mass", "GenDressedLepton_mass[good_GenDressedLepton]")
              .Define("good_GenDressedLepton_pdgId", "GenDressedLepton_pdgId[good_GenDressedLepton]")
              .Define("ngood_GenDressedLeptons","Sum(good_GenDressedLepton)*1.0f")
              .Define("GenJet_mask", "cleaningJetFromLepton(GenJet_eta,GenJet_phi,good_GenDressedLepton_eta,good_GenDressedLepton_phi)")
              .Define("good_GenJet", "GenJet_pt > {0} && abs(GenJet_eta) < {1} && GenJet_mask > 0".format(ptjcut,etajcut))
              .Define("ngood_GenJets","Sum(good_GenJet)*1.0f")
              .Define("good_GenJet_pt",            "GenJet_pt[good_GenJet]")
              .Define("good_GenJet_eta",           "GenJet_eta[good_GenJet]")
              .Define("good_GenJet_phi",           "GenJet_phi[good_GenJet]")
              .Define("good_GenJet_mass",          "GenJet_mass[good_GenJet]")
              .Define("good_GenJet_hadronFlavour", "GenJet_hadronFlavour[good_GenJet]")
              .Define("good_GenJet_partonFlavour", "GenJet_partonFlavour[good_GenJet]")
              )

    return dftag

def selectionTauVeto(df,year,isData):

    dftag =(df.Define("good_tau", "abs(Tau_eta) < 2.5 && Tau_pt > 20 && Tau_idDeepTau2018v2p5VSjet >= 6 && Tau_idDeepTau2018v2p5VSe >= 6 && Tau_idDeepTau2018v2p5VSmu >= 4")
              .Filter("Sum(good_tau) == 0","No selected hadronic taus")
              .Define("good_Tau_pt", "Tau_pt[good_tau]")
              .Define("good_Tau_eta", "Tau_eta[good_tau]")
              .Define("good_Tau_decayMode", "Tau_decayMode[good_tau]")
              )

    if(isData == "false"):
        dftag = dftag.Define("good_Tau_genPartFlav", "Tau_genPartFlav[good_tau]")

    return dftag

def selectionPhoton(df,year,BARRELphotons,ENDCAPphotons):

    dftag =(df.Define("photon_mask", "cleaningMask(Electron_photonIdx[fake_el],nPhoton)")
              .Define("good_Photons", "{}".format(BARRELphotons)+" or {}".format(ENDCAPphotons) )
              .Define("good_Photons_pt", "Photon_pt[good_Photons]")
              .Define("good_Photons_eta", "Photon_eta[good_Photons]")
              .Define("good_Photons_phi", "Photon_phi[good_Photons]")
              )

    return dftag

def makeJES(df,year,postFix,bTagSel,jetEtaCut):
    postFitDef = postFix
    postFitMet = "Def"
    if(postFix == ""):
        postFitDef = "Def"
        postFitMet = ""

    dftag =(df.Define("good_jet{0}".format(postFix), "abs(clean_Jet_eta) < {0} && clean_Jet_pt{1} > 30 && (clean_Jet_pt{1} > 50 or abs(clean_Jet_eta) < 2.5 or abs(clean_Jet_eta) > 3.0)".format(jetEtaCut,postFitDef))
              .Define("ngood_jets{0}".format(postFix), "Sum(good_jet{0})*1.0f".format(postFix))
              .Define("good_Jet_pt{0}".format(postFix), "clean_Jet_pt{0}[good_jet{1}]".format(postFitDef,postFix))
              .Define("good_Jet_eta{0}".format(postFix), "clean_Jet_eta[good_jet{0}]".format(postFix))
              .Define("good_Jet_phi{0}".format(postFix), "clean_Jet_phi[good_jet{0}]".format(postFix))
              .Define("good_Jet_mass{0}".format(postFix), "clean_Jet_mass[good_jet{0}]".format(postFix))
              .Define("good_Jet_area{0}".format(postFix), "clean_Jet_area[good_jet{0}]".format(postFix))
              .Define("good_Jet_rawFactor{0}".format(postFix), "clean_Jet_rawFactor[good_jet{0}]".format(postFix))
              .Define("good_Jet_btagUnifiedParTB{0}".format(postFix), "clean_Jet_btagUnifiedParTB[good_jet{0}]".format(postFix))
              .Define("good_Jet_chEmEF{0}".format(postFix), "clean_Jet_chEmEF[good_jet{0}]".format(postFix))
              .Define("good_Jet_neEmEF{0}".format(postFix), "clean_Jet_neEmEF[good_jet{0}]".format(postFix))
              .Define("good_Jet_chHEF{0}".format(postFix), "clean_Jet_chHEF[good_jet{0}]".format(postFix))
              .Define("good_Jet_neHEF{0}".format(postFix), "clean_Jet_neHEF[good_jet{0}]".format(postFix))

              .Define("mjj{0}".format(postFix),	  "compute_jet_var(good_Jet_pt{0}, good_Jet_eta, good_Jet_phi, good_Jet_mass, 0)".format(postFix))
              .Define("ptjj{0}".format(postFix),  "compute_jet_var(good_Jet_pt{0}, good_Jet_eta, good_Jet_phi, good_Jet_mass, 1)".format(postFix))
              .Define("detajj{0}".format(postFix),"compute_jet_var(good_Jet_pt{0}, good_Jet_eta, good_Jet_phi, good_Jet_mass, 2)".format(postFix))
              .Define("dphijj{0}".format(postFix),"compute_jet_var(good_Jet_pt{0}, good_Jet_eta, good_Jet_phi, good_Jet_mass, 3)".format(postFix))
              .Define("ptj1{0}".format(postFix),  "compute_jet_var(good_Jet_pt{0}, good_Jet_eta, good_Jet_phi, good_Jet_mass, 4)".format(postFix))
              .Define("ptj2{0}".format(postFix),  "compute_jet_var(good_Jet_pt{0}, good_Jet_eta, good_Jet_phi, good_Jet_mass, 5)".format(postFix))
              .Define("etaj1{0}".format(postFix), "compute_jet_var(good_Jet_pt{0}, good_Jet_eta, good_Jet_phi, good_Jet_mass, 6)".format(postFix))
              .Define("etaj2{0}".format(postFix), "compute_jet_var(good_Jet_pt{0}, good_Jet_eta, good_Jet_phi, good_Jet_mass, 7)".format(postFix))

              .Define("goodbtag_jet{0}".format(postFix), "abs(clean_Jet_eta) < 2.5 && clean_Jet_pt{0} > 20".format(postFitDef))
              .Define("goodbtag_Jet_pt{0}".format(postFix), "clean_Jet_pt{0}[goodbtag_jet{1}]".format(postFitDef,postFix))
              .Define("goodbtag_Jet_eta{0}".format(postFix), "abs(clean_Jet_eta[goodbtag_jet{0}])".format(postFix))
              .Define("goodbtag_Jet_phi{0}".format(postFix), "abs(clean_Jet_phi[goodbtag_jet{0}])".format(postFix))

              .Define("goodbtag_Jet_btagUnifiedParTB{0}".format(postFix), "clean_Jet_btagUnifiedParTB[goodbtag_jet{0}]".format(postFix))
              .Define("goodbtag_Jet_bjet{0}".format(postFix), "goodbtag_Jet_btagUnifiedParTB{0} > {1}".format(postFix,getBTagCut(bTagSel,year)))
              .Define("nbtag_goodbtag_Jet_bjet{0}".format(postFix), "Sum(goodbtag_Jet_bjet{0})*1.0f".format(postFix))

              .Define("vbs_jet{0}".format(postFix), "abs(clean_Jet_eta) < 4.9 && clean_Jet_pt{0} > 50".format(postFitDef))
              .Define("nvbs_jets{0}".format(postFix), "Sum(vbs_jet{0})*1.0f".format(postFix))
              .Define("vbs_Jet_pt{0}".format(postFix), "clean_Jet_pt{0}[vbs_jet{1}]".format(postFitDef,postFix))
              .Define("vbs_Jet_eta{0}".format(postFix), "clean_Jet_eta[vbs_jet{0}]".format(postFix))
              .Define("vbs_Jet_phi{0}".format(postFix), "clean_Jet_phi[vbs_jet{0}]".format(postFix))
              .Define("vbs_Jet_mass{0}".format(postFix), "clean_Jet_mass[vbs_jet{0}]".format(postFix))

              .Define("vbs_mjj{0}".format(postFix),   "compute_jet_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, 0)".format(postFix))
              .Define("vbs_ptjj{0}".format(postFix),  "compute_jet_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, 1)".format(postFix))
              .Define("vbs_detajj{0}".format(postFix),"compute_jet_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, 2)".format(postFix))
              .Define("vbs_dphijj{0}".format(postFix),"compute_jet_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, 3)".format(postFix))
              .Define("vbs_ptj1{0}".format(postFix),  "compute_jet_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, 4)".format(postFix))
              .Define("vbs_ptj2{0}".format(postFix),  "compute_jet_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, 5)".format(postFix))
              .Define("vbs_etaj1{0}".format(postFix), "compute_jet_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, 6)".format(postFix))
              .Define("vbs_etaj2{0}".format(postFix), "compute_jet_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, 7)".format(postFix))

              .Define("PuppiMET_pt{0}".format(postFitDef), "compute_JSON_MET_Unc(PuppiMET_pt,PuppiMET_phi,RawPuppiMET_pt,RawPuppiMET_phi,clean_Jet_chEmEF,clean_Jet_neEmEF,clean_Jet_muonSubtrFactor,clean_Jet_rawFactor,clean_Jet_pt{0},clean_Jet_pt{1},clean_Jet_eta,clean_Jet_phi,clean_Jet_mass,1)".format(postFitMet,postFitDef))
              .Define("PuppiMET_phi{0}".format(postFitDef),"compute_JSON_MET_Unc(PuppiMET_pt,PuppiMET_phi,RawPuppiMET_pt,RawPuppiMET_phi,clean_Jet_chEmEF,clean_Jet_neEmEF,clean_Jet_muonSubtrFactor,clean_Jet_rawFactor,clean_Jet_pt{0},clean_Jet_pt{1},clean_Jet_eta,clean_Jet_phi,clean_Jet_mass,2)".format(postFitMet,postFitDef))

              .Define("vbs_zepvv{0}".format(postFix),    "compute_jet_lepton_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt{1}, PuppiMET_phi{2}, 0)".format(postFix,postFitMet,postFitMet))
              .Define("vbs_zepmax{0}".format(postFix),   "compute_jet_lepton_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt{1}, PuppiMET_phi{2}, 1)".format(postFix,postFitMet,postFitMet))
              .Define("vbs_sumHT{0}".format(postFix),    "compute_jet_lepton_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt{1}, PuppiMET_phi{2}, 2)".format(postFix,postFitMet,postFitMet))
              .Define("vbs_ptvv{0}".format(postFix),     "compute_jet_lepton_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt{1}, PuppiMET_phi{2}, 3)".format(postFix,postFitMet,postFitMet))
              .Define("vbs_pttot{0}".format(postFix),    "compute_jet_lepton_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt{1}, PuppiMET_phi{2}, 4)".format(postFix,postFitMet,postFitMet))
              .Define("vbs_detavvj1{0}".format(postFix), "compute_jet_lepton_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt{1}, PuppiMET_phi{2}, 5)".format(postFix,postFitMet,postFitMet))
              .Define("vbs_detavvj2{0}".format(postFix), "compute_jet_lepton_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt{1}, PuppiMET_phi{2}, 6)".format(postFix,postFitMet,postFitMet))
              .Define("vbs_ptbalance{0}".format(postFix),"compute_jet_lepton_var(vbs_Jet_pt{0}, vbs_Jet_eta, vbs_Jet_phi, vbs_Jet_mass, fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt{1}, PuppiMET_phi{2}, 7)".format(postFix,postFitMet,postFitMet))
              )

    return dftag

def selectionJetMet(df,year,bTagSel,isData,count,jetEtaCut):

    jetTypeCorr = -1
    if(count > 1000): jetTypeCorr = count%10
    print("jetTypeCorr: {0}".format(jetTypeCorr))

    BTAGName = "UParTAK4"
    if((year // 10) < 2024): BTAGName = "RobustParTAK4"

    JMEName0 = "Jet_chMultiplicity"
    JMEName1 = "Jet_neMultiplicity"
    JMEName2 = "Jet_nElectrons" # dummy
    if((year // 10) < 2024):
        JMEName0 = "Jet_nElectrons" # dummy
        JMEName1 = "Jet_nElectrons" # dummy
        JMEName2 = "Jet_jetId"

    dftag =(df.Define("jet_mask1", "cleaningMask(Muon_jetIdx[fake_mu],nJet)")
              .Define("jet_mask2", "cleaningMask(Electron_jetIdx[fake_el],nJet)")
              .Define("jet_VetoMapMask", "cleaningJetVetoMapMask(Jet_eta,Jet_phi,{0},{1})".format(jetTypeCorr,year))
              .Define("jet_SelMask0", "cleaningJetSelMask(0,Jet_eta,Jet_chHEF,Jet_neHEF,Jet_chEmEF,Jet_neEmEF,Jet_muEF,{0},{1},{2},{3})".format(JMEName0,JMEName1,JMEName2,year))
              .Define("jet_SelMask1", "cleaningJetSelMask(1,Jet_eta,Jet_chHEF,Jet_neHEF,Jet_chEmEF,Jet_neEmEF,Jet_muEF,{0},{1},{2},{3})".format(JMEName0,JMEName1,JMEName2,year))
              #.Define("clean_jet", "Jet_pt > 10 && jet_mask1 && jet_mask2 && jet_VetoMapMask > 0 && jet_SelMask0 && jet_SelMask1")
              .Define("clean_jet", "Jet_pt > 10 && jet_mask1 && jet_mask2 && jet_VetoMapMask > 0 && jet_SelMask0") # No Tight lepton veto
              .Define("clean_Jet_pt", "Jet_pt[clean_jet]")
              .Define("clean_Jet_eta", "Jet_eta[clean_jet]")
              .Define("clean_Jet_phi", "Jet_phi[clean_jet]")
              .Define("clean_Jet_mass", "Jet_mass[clean_jet]")
              .Define("clean_Jet_area", "Jet_area[clean_jet]")
              .Define("clean_Jet_rawFactor", "Jet_rawFactor[clean_jet]")
              .Define("clean_Jet_btagUnifiedParTB", "Jet_btag{0}B[clean_jet]".format(BTAGName))
              .Define("clean_Jet_muonSubtrFactor", "Jet_muonSubtrFactor[clean_jet]")
              .Define("clean_Jet_chEmEF", "Jet_chEmEF[clean_jet]")
              .Define("clean_Jet_neEmEF", "Jet_neEmEF[clean_jet]")
              .Define("clean_Jet_chHEF",  "Jet_chHEF[clean_jet]")
              .Define("clean_Jet_neHEF",  "Jet_neHEF[clean_jet]")
              )

    if(isData == "false"):
        dftag =(dftag.Define("clean_Jet_genJetIdx", "Jet_genJetIdx[clean_jet]")
                     .Define("clean_Jet_ptRaw"     ,"clean_Jet_pt*(1-clean_Jet_rawFactor)")
                     .Define("clean_Jet_ptNoJESJER","clean_Jet_pt")
                     .Define("clean_Jet_ptNoJES"   ,"compute_JSON_JER_Unc(clean_Jet_pt,clean_Jet_eta,clean_Jet_genJetIdx,GenJet_pt,Rho_fixedGridRhoFastjetAll,0)")
                     .Define("clean_Jet_ptNoJER"   ,"compute_JSON_JES_Unc(clean_Jet_pt,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,0,-1)")
                     .Define("clean_Jet_ptDef"    , "compute_JSON_JER_Unc(clean_Jet_ptNoJER,clean_Jet_eta,clean_Jet_genJetIdx,GenJet_pt,Rho_fixedGridRhoFastjetAll,0)")
                     .Define("clean_Jet_ptJerUp"  , "compute_JSON_JER_Unc(clean_Jet_ptNoJER,clean_Jet_eta,clean_Jet_genJetIdx,GenJet_pt,Rho_fixedGridRhoFastjetAll,+1)")
                     .Define("clean_Jet_ptJes00Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run, +1,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes01Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run, +2,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes02Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run, +3,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes03Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run, +4,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes04Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run, +5,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes05Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run, +6,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes06Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run, +7,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes07Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run, +8,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes08Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run, +9,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes09Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+10,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes10Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+11,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes11Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+12,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes12Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+13,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes13Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+14,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes14Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+15,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes15Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+16,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes16Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+17,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes17Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+18,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes18Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+19,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes19Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+20,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes20Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+21,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes21Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+22,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes22Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+23,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes23Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+24,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes24Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+25,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes25Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+26,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes26Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+27,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptJes27Up", "compute_JSON_JES_Unc(clean_Jet_ptDef,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,+28,{0})".format(jetTypeCorr))
                     .Define("thePuppiMET_phi"             ,"compute_JSON_MET(\"phi\",\"PuppiMET\",{0},\"MC\",\"nom\"  ,PuppiMET_pt,PuppiMET_phi,PV_npvsGood)".format(year))
                     .Define("thePuppiMET_phiJERUp"        ,"compute_JSON_MET(\"phi\",\"PuppiMET\",{0},\"MC\",\"pu_up\",PuppiMET_pt,PuppiMET_phi,PV_npvsGood)".format(year))
                     .Define("thePuppiMET_phiJESUp"        ,"compute_JSON_MET(\"phi\",\"PuppiMET\",{0},\"MC\",\"pu_dn\",PuppiMET_pt,PuppiMET_phi,PV_npvsGood)".format(year))
                     .Define("thePuppiMET_phiUnclusteredUp","compute_JSON_MET(\"phi\",\"PuppiMET\",{0},\"MC\",\"nom\",PuppiMET_ptUnclusteredUp,PuppiMET_phiUnclusteredUp,PV_npvsGood)".format(year))
                     .Define("thePuppiMET_pt"              ,"compute_JSON_MET(\"pt\",\"PuppiMET\",{0},\"MC\",\"nom\"  ,PuppiMET_pt,PuppiMET_phi,PV_npvsGood)".format(year))
                     .Define("thePuppiMET_ptJERUp"         ,"compute_JSON_MET(\"pt\",\"PuppiMET\",{0},\"MC\",\"pu_up\",PuppiMET_pt,PuppiMET_phi,PV_npvsGood)".format(year))
                     .Define("thePuppiMET_ptJESUp"         ,"compute_JSON_MET(\"pt\",\"PuppiMET\",{0},\"MC\",\"pu_dn\",PuppiMET_pt,PuppiMET_phi,PV_npvsGood)".format(year))
                     .Define("thePuppiMET_ptUnclusteredUp" ,"compute_JSON_MET(\"pt\",\"PuppiMET\",{0},\"MC\",\"nom\",PuppiMET_ptUnclusteredUp,PuppiMET_phiUnclusteredUp,PV_npvsGood)".format(year))
                     )

    else:
        dftag =(dftag.Define("clean_Jet_ptRaw"     ,"clean_Jet_pt*(1-clean_Jet_rawFactor)")
                     .Define("clean_Jet_ptNoJESJER","clean_Jet_pt")
                     .Define("clean_Jet_ptNoJES"   ,"clean_Jet_pt")
                     .Define("clean_Jet_ptNoJER"   ,"compute_JSON_JES_Unc(clean_Jet_pt,clean_Jet_eta,clean_Jet_phi,clean_Jet_rawFactor,clean_Jet_area,Rho_fixedGridRhoFastjetAll,run,0,{0})".format(jetTypeCorr))
                     .Define("clean_Jet_ptDef"     ,"clean_Jet_ptNoJER")
                     .Define("clean_Jet_ptJes00Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes01Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes02Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes03Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes04Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes05Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes06Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes07Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes08Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes09Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes10Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes11Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes12Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes13Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes14Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes15Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes16Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes17Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes18Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes19Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes20Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes21Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes22Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes23Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes24Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes25Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes26Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJes27Up", "clean_Jet_ptDef")
                     .Define("clean_Jet_ptJerUp"  , "clean_Jet_ptDef")
                     .Define("thePuppiMET_phi"             ,"compute_JSON_MET(\"phi\",\"PuppiMET\",{0},\"DATA\",\"nom\",PuppiMET_pt,PuppiMET_phi,PV_npvsGood)".format(year))
                     .Define("thePuppiMET_phiJERUp"        ,"thePuppiMET_phi")
                     .Define("thePuppiMET_phiJESUp"        ,"thePuppiMET_phi")
                     .Define("thePuppiMET_phiUnclusteredUp","thePuppiMET_phi")
                     .Define("thePuppiMET_pt"              ,"compute_JSON_MET(\"pt\",\"PuppiMET\",{0},\"DATA\",\"nom\",PuppiMET_pt,PuppiMET_phi,PV_npvsGood)".format(year))
                     .Define("thePuppiMET_ptJERUp"         ,"thePuppiMET_pt")
                     .Define("thePuppiMET_ptJESUp"         ,"thePuppiMET_pt")
                     .Define("thePuppiMET_ptUnclusteredUp" ,"thePuppiMET_pt")
                     )

    dftag = makeJES(dftag,year,""        ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes00Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes01Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes02Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes03Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes04Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes05Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes06Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes07Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes08Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes09Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes10Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes11Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes12Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes13Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes14Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes15Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes16Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes17Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes18Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes19Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes20Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes21Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes22Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes23Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes24Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes25Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes26Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Jes27Up" ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"JerUp"   ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"Raw"     ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"NoJESJER",bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"NoJES"   ,bTagSel,jetEtaCut)
    dftag = makeJES(dftag,year,"NoJER"   ,bTagSel,jetEtaCut)

    return dftag

def makeLGVar(df,postFixMu,postFixEl,postFixPh):

    postFix = ""
    if(postFixMu != ""):
        postFix = postFixMu
    elif(postFixEl != ""):
        postFix = postFixEl
    elif(postFixPh != ""):
        postFix = postFixPh

    dftag =(df.Define("ptbalance{0}".format(postFix), "compute_met_lepton_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, 0)".format(postFixMu,postFixEl))
              .Define("ptjbalance{0}".format(postFix),"compute_met_lepton_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, 1)".format(postFixMu,postFixEl))
              .Define("dphillmet{0}".format(postFix), "compute_met_lepton_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, 2)".format(postFixMu,postFixEl))
              .Define("dphilljmet{0}".format(postFix),"compute_met_lepton_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, 3)".format(postFixMu,postFixEl))
              .Define("mt{0}".format(postFix),        "compute_met_lepton_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, 4)".format(postFixMu,postFixEl))
              .Define("jetPtFrac{0}".format(postFix), "compute_met_lepton_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, 5)".format(postFixMu,postFixEl))
              .Define("dphijmet{0}".format(postFix),  "compute_met_lepton_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, 6)".format(postFixMu,postFixEl))
              .Define("ptgbalance{0}".format(postFix), "compute_met_lepton_gamma_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, good_Photons_pt{2}, good_Photons_eta, good_Photons_phi, 0)".format(postFixMu,postFixEl,postFixPh))
              .Define("ptgjbalance{0}".format(postFix),"compute_met_lepton_gamma_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, good_Photons_pt{2}, good_Photons_eta, good_Photons_phi, 1)".format(postFixMu,postFixEl,postFixPh))
              .Define("dphillgmet{0}".format(postFix), "compute_met_lepton_gamma_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, good_Photons_pt{2}, good_Photons_eta, good_Photons_phi, 2)".format(postFixMu,postFixEl,postFixPh))
              .Define("dphillgjmet{0}".format(postFix),"compute_met_lepton_gamma_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, good_Photons_pt{2}, good_Photons_eta, good_Photons_phi, 3)".format(postFixMu,postFixEl,postFixPh))
              .Define("mtg{0}".format(postFix),        "compute_met_lepton_gamma_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, good_Photons_pt{2}, good_Photons_eta, good_Photons_phi, 4)".format(postFixMu,postFixEl,postFixPh))
              .Define("jetPtgFrac{0}".format(postFix), "compute_met_lepton_gamma_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, PuppiMET_pt, PuppiMET_phi, good_Photons_pt{2}, good_Photons_eta, good_Photons_phi, 5)".format(postFixMu,postFixEl,postFixPh))
	      )

    return dftag

def selectionLGVar(df,year,isData):

    if(isData == "false"):
        dftag =(df.Define("good_Photons_ptPhotonMomUp"  , "compute_PHOPT_Unc(good_Photons_pt,+1)")
                  .Define("good_Photons_ptPhotonMomDown", "compute_PHOPT_Unc(good_Photons_pt,-1)")
                  )
    else:
        dftag =(df.Define("good_Photons_ptPhotonMomUp"  , "good_Photons_pt")
                  .Define("good_Photons_ptPhotonMomDown", "good_Photons_pt")
                  )

    dftag = makeLGVar(dftag,""            ,""              ,"")
    dftag = makeLGVar(dftag,"MuonMomUp"  ,""               ,"")
    dftag = makeLGVar(dftag,"MuonMomDown",""               ,"")
    dftag = makeLGVar(dftag,""           ,"ElectronMomUp"  ,"")
    dftag = makeLGVar(dftag,""           ,"ElectronMomDown","")
    dftag = makeLGVar(dftag,""            ,""              ,"PhotonMomUp")
    dftag = makeLGVar(dftag,""            ,""              ,"PhotonMomDown")

    return dftag


def make4LVar(df,postFixMu,postFixEl):

    postFix = ""
    if(postFixMu != ""):
        postFix = postFixMu
    elif(postFixEl != ""):
        postFix = postFixEl

    dftag =(df.Define("m4l{0}".format(postFix),   "compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 0)".format(postFixMu,postFixEl))
              .Define("ptlmax{0}".format(postFix),"compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 1)".format(postFixMu,postFixEl))
              .Define("mllmin{0}".format(postFix),"compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 2)".format(postFixMu,postFixEl))
              .Define("mllZ1{0}".format(postFix), "compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 3)".format(postFixMu,postFixEl))
              .Define("mllZ2{0}".format(postFix), "compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 4)".format(postFixMu,postFixEl))
              .Define("ptl1Z1{0}".format(postFix),"compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 5)".format(postFixMu,postFixEl))
              .Define("ptl2Z1{0}".format(postFix),"compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 6)".format(postFixMu,postFixEl))
              .Define("ptl1Z2{0}".format(postFix),"compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 7)".format(postFixMu,postFixEl))
              .Define("ptl2Z2{0}".format(postFix),"compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 8)".format(postFixMu,postFixEl))
              .Define("mllxy{0}".format(postFix), "compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 9)".format(postFixMu,postFixEl))
              .Define("ptZ1{0}".format(postFix),  "compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,10)".format(postFixMu,postFixEl))
              .Define("ptZ2{0}".format(postFix),  "compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,11)".format(postFixMu,postFixEl))
              .Define("mtxy{0}".format(postFix),  "compute_4l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,12)".format(postFixMu,postFixEl))
              .Define("ltype{0}".format(postFix), "compute_nl_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,2)".format(postFixMu,postFixEl))
	      )

    return dftag

def selection4LVar(df,year,isData):

    if(isData == "false"):
        dftag =(df.Define("FourLepton_flavor"              , "(Sum(fake_mu)+4*Sum(fake_el)-4)/6")
                  .Define("fake_Muon_ptDef"                , "compute_MUOPT_Unc({0},fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_charge,fake_Muon_nTrackerLayers,0)".format(year))
                  .Define("fake_Muon_ptMuonMomUp"          , "compute_MUOPT_Unc({0},fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_charge,fake_Muon_nTrackerLayers,+1)".format(year))
                  .Define("fake_Muon_ptMuonMomDown"        , "compute_MUOPT_Unc({0},fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_charge,fake_Muon_nTrackerLayers,-1)".format(year))
                  .Define("fake_Electron_ptDef"            , "compute_ELEPT_Unc({0}, 0,fake_Electron_seedGain,run,fake_Electron_superclusterEta,fake_Electron_r9,fake_Electron_pt)".format(year))
                  .Define("fake_Electron_ptElectronMomUp"  , "compute_ELEPT_Unc({0},+1,fake_Electron_seedGain,run,fake_Electron_superclusterEta,fake_Electron_r9,fake_Electron_pt)".format(year))
                  .Define("fake_Electron_ptElectronMomDown", "compute_ELEPT_Unc({0},-1,fake_Electron_seedGain,run,fake_Electron_superclusterEta,fake_Electron_r9,fake_Electron_pt)".format(year))
                  )
    else:
        dftag =(df.Define("FourLepton_flavor"              , "(Sum(fake_mu)+4*Sum(fake_el)-4)/6")
                  .Define("fake_Muon_ptDef"                , "compute_MUOPT_Unc({0},fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_charge,fake_Muon_nTrackerLayers,10)".format(year))
                  .Define("fake_Muon_ptMuonMomUp"          , "fake_Muon_ptDef")
                  .Define("fake_Muon_ptMuonMomDown"        , "fake_Muon_ptDef")
                  .Define("fake_Electron_ptDef"            , "compute_ELEPT_Unc({0},10,fake_Electron_seedGain,run,fake_Electron_superclusterEta,fake_Electron_r9,fake_Electron_pt)".format(year))
                  .Define("fake_Electron_ptElectronMomUp"  , "fake_Electron_ptDef")
                  .Define("fake_Electron_ptElectronMomDown", "fake_Electron_ptDef")
                  )

    dftag = make4LVar(dftag,"","")
    dftag = make4LVar(dftag,"MuonMomUp","")
    dftag = make4LVar(dftag,"MuonMomDown","")
    dftag = make4LVar(dftag,"","ElectronMomUp")
    dftag = make4LVar(dftag,"","ElectronMomDown")
    dftag = make4LVar(dftag,"Def","Def")

    return dftag


def make3LVar(df,postFixMu,postFixEl):

    postFix = ""
    if(postFixMu != ""):
        postFix = postFixMu
    elif(postFixEl != ""):
        postFix = postFixEl

    dftag =(df.Define("m3l{0}".format(postFix),      "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 0)".format(postFixMu,postFixEl))
              .Define("mllmin{0}".format(postFix),   "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 1)".format(postFixMu,postFixEl))
              .Define("drllmin{0}".format(postFix),  "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 2)".format(postFixMu,postFixEl))
              .Define("ptl1{0}".format(postFix),     "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 3)".format(postFixMu,postFixEl))
              .Define("ptl2{0}".format(postFix),     "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 4)".format(postFixMu,postFixEl))
              .Define("ptl3{0}".format(postFix),     "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 5)".format(postFixMu,postFixEl))
              .Define("etal1{0}".format(postFix),    "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 6)".format(postFixMu,postFixEl))
              .Define("etal2{0}".format(postFix),    "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 7)".format(postFixMu,postFixEl))
              .Define("etal3{0}".format(postFix),    "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 8)".format(postFixMu,postFixEl))
              .Define("mllAllmin{0}".format(postFix),"compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi, 9)".format(postFixMu,postFixEl))
              .Define("mll{0}".format(postFix),      "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,10)".format(postFixMu,postFixEl))
              .Define("mllSS{0}".format(postFix),    "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,11)".format(postFixMu,postFixEl))
              .Define("ptl1Z{0}".format(postFix),    "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,12)".format(postFixMu,postFixEl))
              .Define("ptl2Z{0}".format(postFix),    "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,13)".format(postFixMu,postFixEl))
              .Define("ptlW{0}".format(postFix),     "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,14)".format(postFixMu,postFixEl))
              .Define("etalW{0}".format(postFix),"abs(compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,15))".format(postFixMu,postFixEl))
              .Define("mtW{0}".format(postFix),      "compute_3l_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,16)".format(postFixMu,postFixEl))
              .Define("mllZ{0}".format(postFix),     "abs(mll{0}-91.1876)".format(postFix))
              .Define("mllSSZ{0}".format(postFix),   "abs(mllSS{0}-91.1876)".format(postFix))
              .Define("ltype{0}".format(postFix),    "compute_nl_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,2)".format(postFixMu,postFixEl))
              )

    return dftag

def selection3LVar(df,year,isData):

    if(isData == "false"):
        dftag =(df.Define("TriLepton_flavor"               , "(Sum(fake_mu)+3*Sum(fake_el)-3)/2")
                  .Define("fake_Muon_ptDef"                , "compute_MUOPT_Unc({0},fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_charge,fake_Muon_nTrackerLayers,0)".format(year))
                  .Define("fake_Muon_ptMuonMomUp"          , "compute_MUOPT_Unc({0},fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_charge,fake_Muon_nTrackerLayers,+1)".format(year))
                  .Define("fake_Muon_ptMuonMomDown"        , "compute_MUOPT_Unc({0},fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_charge,fake_Muon_nTrackerLayers,-1)".format(year))
                  .Define("fake_Electron_ptDef"            , "compute_ELEPT_Unc({0}, 0,fake_Electron_seedGain,run,fake_Electron_superclusterEta,fake_Electron_r9,fake_Electron_pt)".format(year))
                  .Define("fake_Electron_ptElectronMomUp"  , "compute_ELEPT_Unc({0},+1,fake_Electron_seedGain,run,fake_Electron_superclusterEta,fake_Electron_r9,fake_Electron_pt)".format(year))
                  .Define("fake_Electron_ptElectronMomDown", "compute_ELEPT_Unc({0},-1,fake_Electron_seedGain,run,fake_Electron_superclusterEta,fake_Electron_r9,fake_Electron_pt)".format(year))
                  )
    else:
        dftag =(df.Define("TriLepton_flavor"               , "(Sum(fake_mu)+3*Sum(fake_el)-3)/2")
                  .Define("fake_Muon_ptDef"                , "compute_MUOPT_Unc({0},fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_charge,fake_Muon_nTrackerLayers,10)".format(year))
                  .Define("fake_Muon_ptMuonMomUp"          , "fake_Muon_ptDef")
                  .Define("fake_Muon_ptMuonMomDown"        , "fake_Muon_ptDef")
                  .Define("fake_Electron_ptDef"            , "compute_ELEPT_Unc({0},10,fake_Electron_seedGain,run,fake_Electron_superclusterEta,fake_Electron_r9,fake_Electron_pt)".format(year))
                  .Define("fake_Electron_ptElectronMomUp"  , "fake_Electron_ptDef")
                  .Define("fake_Electron_ptElectronMomDown", "fake_Electron_ptDef")
                  )

    dftag = make3LVar(dftag,"","")
    dftag = make3LVar(dftag,"MuonMomUp","")
    dftag = make3LVar(dftag,"MuonMomDown","")
    dftag = make3LVar(dftag,"","ElectronMomUp")
    dftag = make3LVar(dftag,"","ElectronMomDown")
    dftag = make3LVar(dftag,"Def","Def")

    return dftag

def make2LVar(df,postFixMu,postFixEl):

    postFix = ""
    if(postFixMu != ""):
        postFix = postFixMu
    elif(postFixEl != ""):
        postFix = postFixEl

    dftag =(df.Define("mll{0}".format(postFix),   "compute_ll_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass,0)".format(postFixMu,postFixEl))
              .Define("ptll{0}".format(postFix),  "compute_ll_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass,1)".format(postFixMu,postFixEl))
              .Define("drll{0}".format(postFix),  "compute_ll_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass,2)".format(postFixMu,postFixEl))
              .Define("dphill{0}".format(postFix),"compute_ll_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass,3)".format(postFixMu,postFixEl))
              .Define("ptl1{0}".format(postFix),  "compute_ll_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass,4)".format(postFixMu,postFixEl))
              .Define("ptl2{0}".format(postFix),  "compute_ll_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass,5)".format(postFixMu,postFixEl))
              .Define("etal1{0}".format(postFix), "abs(compute_ll_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass,6))".format(postFixMu,postFixEl))
              .Define("etal2{0}".format(postFix), "abs(compute_ll_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass,7))".format(postFixMu,postFixEl))
              .Define("ltype{0}".format(postFix), "compute_nl_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,2)".format(postFixMu,postFixEl))
              .Define("dPhilMETMin{0}".format(postFix), "compute_nl_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,7)".format(postFixMu,postFixEl))
              .Define("minPMET{0}".format(postFix), "compute_nl_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,8)".format(postFixMu,postFixEl))
              .Define("ptww{0}".format(postFix), "compute_nl_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,9)".format(postFixMu,postFixEl))
              .Define("mcoll{0}".format(postFix), "compute_nl_var(fake_Muon_pt{0}, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt{1}, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,10)".format(postFixMu,postFixEl))
              )

    return dftag

def selection2LVar(df,year,isData):

    if(isData == "false"):
        dftag =(df.Define("DiLepton_flavor"                , "Sum(fake_mu)+2*Sum(fake_el)-2")
                  .Define("fake_Muon_ptDef"                , "compute_MUOPT_Unc({0},fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_charge,fake_Muon_nTrackerLayers,0)".format(year))
                  .Define("fake_Muon_ptMuonMomUp"          , "compute_MUOPT_Unc({0},fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_charge,fake_Muon_nTrackerLayers,+1)".format(year))
                  .Define("fake_Muon_ptMuonMomDown"        , "compute_MUOPT_Unc({0},fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_charge,fake_Muon_nTrackerLayers,-1)".format(year))
                  .Define("fake_Electron_ptDef"            , "compute_ELEPT_Unc({0}, 0,fake_Electron_seedGain,run,fake_Electron_superclusterEta,fake_Electron_r9,fake_Electron_pt)".format(year))
                  .Define("fake_Electron_ptElectronMomUp"  , "compute_ELEPT_Unc({0},+1,fake_Electron_seedGain,run,fake_Electron_superclusterEta,fake_Electron_r9,fake_Electron_pt)".format(year))
                  .Define("fake_Electron_ptElectronMomDown", "compute_ELEPT_Unc({0},-1,fake_Electron_seedGain,run,fake_Electron_superclusterEta,fake_Electron_r9,fake_Electron_pt)".format(year))
                  )
    else:
        dftag =(df.Define("DiLepton_flavor"                , "Sum(fake_mu)+2*Sum(fake_el)-2")
                  .Define("fake_Muon_ptDef"                , "compute_MUOPT_Unc({0},fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_charge,fake_Muon_nTrackerLayers,10)".format(year))
                  .Define("fake_Muon_ptMuonMomUp"          , "fake_Muon_ptDef")
                  .Define("fake_Muon_ptMuonMomDown"        , "fake_Muon_ptDef")
                  .Define("fake_Electron_ptDef"            , "compute_ELEPT_Unc({0},10,fake_Electron_seedGain,run,fake_Electron_superclusterEta,fake_Electron_r9,fake_Electron_pt)".format(year))
                  .Define("fake_Electron_ptElectronMomUp"  , "fake_Electron_ptDef")
                  .Define("fake_Electron_ptElectronMomDown", "fake_Electron_ptDef")
                  )

    dftag =(dftag.Define("ptl3", "0.0f")
                 .Define("muid1", "compute_muid_var(fake_Muon_mediumId, fake_Muon_tightId, fake_Muon_pfIsoId, fake_Muon_miniIsoId, fake_Muon_promptMVA, fake_Muon_mediumPromptId, 0)")
                 .Define("muid2", "compute_muid_var(fake_Muon_mediumId, fake_Muon_tightId, fake_Muon_pfIsoId, fake_Muon_miniIsoId, fake_Muon_promptMVA, fake_Muon_mediumPromptId, 1)")
                 .Define("elid1", "compute_elid_var(fake_Electron_cutBased, fake_Electron_mvaNoIso_WP80, fake_Electron_mvaIso_WP80, fake_Electron_mvaIso_WP90, fake_Electron_tightCharge, fake_Electron_promptMVA, fake_Electron_pfRelIso03_chg, fake_Electron_pfRelIso03_all, 0)")
                 .Define("elid2", "compute_elid_var(fake_Electron_cutBased, fake_Electron_mvaNoIso_WP80, fake_Electron_mvaIso_WP80, fake_Electron_mvaIso_WP90, fake_Electron_tightCharge, fake_Electron_promptMVA, fake_Electron_pfRelIso03_chg, fake_Electron_pfRelIso03_all, 1)")
                 )

    dftag = make2LVar(dftag,"","")
    dftag = make2LVar(dftag,"MuonMomUp","")
    dftag = make2LVar(dftag,"MuonMomDown","")
    dftag = make2LVar(dftag,"","ElectronMomUp")
    dftag = make2LVar(dftag,"","ElectronMomDown")
    dftag = make2LVar(dftag,"Def","Def")

    return dftag

def selectionTrigger2L(df,year,PDType,JSON,isData,triggerSEL,triggerDEL,triggerSMU,triggerDMU,triggerMUEG):

    if(year > 10000): year = year // 10

    triggerLEP = "{0} or {1} or {2} or {3} or {4}".format(triggerSEL,triggerDEL,triggerSMU,triggerDMU,triggerMUEG)

    if(year == 2018 and PDType == "MuonEG"):
        triggerLEP = "{0}".format(triggerMUEG)

    elif(year == 2018 and PDType == "DoubleMuon"):
        triggerLEP = "{0} and not {1}".format(triggerDMU,triggerMUEG)

    elif(year == 2018 and PDType == "SingleMuon"):
        triggerLEP = "{0} and not {1} and not {2}".format(triggerSMU,triggerDMU,triggerMUEG)

    elif(year == 2018 and PDType == "EGamma"):
        triggerLEP = "({0} or {1}) and not {2} and not {3} and not {4}".format(triggerSEL,triggerDEL,triggerSMU,triggerDMU,triggerMUEG)

    elif(year == 2018):
        triggerLEP = "{0} or {1} or {2} or {3} or {4}".format(triggerSEL,triggerDEL,triggerSMU,triggerDMU,triggerMUEG)

    elif(year == 2022 and PDType == "MuonEG"):
        triggerLEP = "{0}".format(triggerMUEG)

    elif(year == 2022 and PDType == "Muon"):
        triggerLEP = "({0} or {1}) and not {2}".format(triggerDMU,triggerSMU,triggerMUEG)

    elif(year == 2022 and PDType == "DoubleMuon"):
        triggerLEP = "{0} and not {1}".format(triggerDMU,triggerMUEG)

    elif(year == 2022 and PDType == "SingleMuon"):
        triggerLEP = "{0} and not {1} and not {2}".format(triggerSMU,triggerDMU,triggerMUEG)

    elif(year == 2022 and PDType == "EGamma"):
        triggerLEP = "({0} or {1}) and not {2} and not {3} and not {4}".format(triggerSEL,triggerDEL,triggerSMU,triggerDMU,triggerMUEG)

    elif(year == 2022):
        triggerLEP = "{0} or {1} or {2} or {3} or {4}".format(triggerSEL,triggerDEL,triggerSMU,triggerDMU,triggerMUEG)

    elif(year == 2023 and PDType == "MuonEG"):
        triggerLEP = "{0}".format(triggerMUEG)

    elif(year == 2023 and PDType == "Muon"):
        triggerLEP = "({0} or {1}) and not {2}".format(triggerDMU,triggerSMU,triggerMUEG)

    elif(year == 2023 and PDType == "EGamma"):
        triggerLEP = "({0} or {1}) and not {2} and not {3} and not {4}".format(triggerSEL,triggerDEL,triggerSMU,triggerDMU,triggerMUEG)

    elif(year == 2023):
        triggerLEP = "{0} or {1} or {2} or {3} or {4}".format(triggerSEL,triggerDEL,triggerSMU,triggerDMU,triggerMUEG)

    elif(year == 2024 and PDType == "MuonEG"):
        triggerLEP = "{0}".format(triggerMUEG)

    elif(year == 2024 and PDType == "Muon"):
        triggerLEP = "({0} or {1}) and not {2}".format(triggerDMU,triggerSMU,triggerMUEG)

    elif(year == 2024 and PDType == "EGamma"):
        triggerLEP = "({0} or {1}) and not {2} and not {3} and not {4}".format(triggerSEL,triggerDEL,triggerSMU,triggerDMU,triggerMUEG)

    elif(year == 2024):
        triggerLEP = "{0} or {1} or {2} or {3} or {4}".format(triggerSEL,triggerDEL,triggerSMU,triggerDMU,triggerMUEG)

    else:
        print("PROBLEM with triggers!!!")

    print("triggerLEP: {0}".format(triggerLEP))

    dftag =(df.Define("isData","{}".format(isData))
              .Define("applyJson","{}".format(JSON)).Filter("applyJson","pass JSON")
              .Define("trigger","{0}".format(triggerLEP))
              .Filter("trigger > 0","Passed trigger")
              .Define("triggerMUEG","{0}".format(triggerMUEG))
              .Define("triggerDMU", "{0}".format(triggerDMU))
              .Define("triggerSMU", "{0}".format(triggerSMU))
              .Define("triggerDEL", "{0}".format(triggerDEL))
              .Define("triggerSEL", "{0}".format(triggerSEL))
              )

    return dftag

def selectionTrigger1L(df,year,PDType,JSON,isData,triggerFAKEMU,triggerFAKEEL):

    if(year > 10000): year = year // 10

    triggerFAKE = "0"

    if(year == 2018 and PDType == "DoubleMuon"):
        triggerFAKE = triggerFAKEMU
    elif(year == 2018 and PDType == "EGamma"):
        triggerFAKE =  triggerFAKEEL
    elif(year == 2022 and PDType == "DoubleMuon"):
        triggerFAKE = triggerFAKEMU
    elif(year == 2022 and PDType == "Muon"):
        triggerFAKE = triggerFAKEMU
    elif(year == 2022 and PDType == "EGamma"):
        triggerFAKE =  triggerFAKEEL
    elif(year == 2023 and PDType == "Muon"):
        triggerFAKE = triggerFAKEMU
    elif(year == 2023 and PDType == "EGamma"):
        triggerFAKE =  triggerFAKEEL
    elif(year == 2024 and PDType == "Muon"):
        triggerFAKE = triggerFAKEMU
    elif(year == 2024 and PDType == "EGamma"):
        triggerFAKE =  triggerFAKEEL
    elif(PDType == "MuonEG"):
        triggerFAKE =  "0"
    elif(year == 2018):
        triggerFAKE = "{0} or {1}".format(triggerFAKEMU,triggerFAKEEL)
    elif(year == 2022):
        triggerFAKE = "{0} or {1}".format(triggerFAKEMU,triggerFAKEEL)
    elif(year == 2023):
        triggerFAKE = "{0} or {1}".format(triggerFAKEMU,triggerFAKEEL)
    elif(year == 2024):
        triggerFAKE = "{0} or {1}".format(triggerFAKEMU,triggerFAKEEL)
    else:
        print("PROBLEM with triggers!!!")

    print("triggerFAKE: {0}".format(triggerFAKE))

    dftag =(df.Define("isData","{}".format(isData))
              .Define("applyJson","{}".format(JSON)).Filter("applyJson","pass JSON")
              .Define("trigger","{0}".format(triggerFAKE))
              .Filter("trigger > 0","Passed trigger1l")
              .Define("triggerFAKEMU","{0}".format(triggerFAKEMU))
              .Define("triggerFAKEEL", "{0}".format(triggerFAKEEL))
	      )

    return dftag

def selectionElMu(df,year,fake_mu,tight_mu,fake_el,tight_el):
    MVAName = "promptMVA"
    if((year // 10) < 2024): MVAName = "mvaTTH"
    SCEtaName = "superclusterEta	"
    if((year // 10) < 2024): SCEtaName = "eta"
    dftag =(df.Define("loose_mu"                  ,"abs(Muon_eta) < 2.4 && Muon_pt > 10 && Muon_looseId == true")
              .Define("fake_mu"                   ,"{0}".format(fake_mu))
              .Define("fake_Muon_pt"              ,"Muon_pt[fake_mu]")
              .Define("fake_Muon_eta"             ,"Muon_eta[fake_mu]")
              .Define("fake_Muon_phi"             ,"Muon_phi[fake_mu]")
              .Define("fake_Muon_dxy"             ,"Muon_dxy[fake_mu]")
              .Define("fake_Muon_dz"              ,"Muon_dz[fake_mu]")
              .Define("fake_Muon_sip3d"           ,"Muon_sip3d[fake_mu]")
              .Define("fake_Muon_mass"            ,"Muon_mass[fake_mu]")
              .Define("fake_Muon_charge"          ,"Muon_charge[fake_mu]")
              .Define("fake_Muon_jetRelIso"       ,"Muon_jetRelIso[fake_mu]")
              .Define("fake_Muon_looseId"         ,"Muon_looseId[fake_mu]")
              .Define("fake_Muon_mediumId"        ,"Muon_mediumId[fake_mu]")
              .Define("fake_Muon_mediumPromptId"  ,"Muon_mediumPromptId[fake_mu]")
              .Define("fake_Muon_tightId"         ,"Muon_tightId[fake_mu]")
              .Define("fake_Muon_pfIsoId"         ,"Muon_pfIsoId[fake_mu]")
              .Define("fake_Muon_mvaMuID"         ,"Muon_mvaMuID[fake_mu]")
              .Define("fake_Muon_miniIsoId"       ,"Muon_miniIsoId[fake_mu]")
              .Define("fake_Muon_promptMVA"       ,"Muon_{0}[fake_mu]".format(MVAName))
              .Define("fake_Muon_mvaLowPt"        ,"Muon_mvaLowPt[fake_mu]")
              .Define("fake_Muon_pfRelIso03_all"  ,"Muon_pfRelIso03_all[fake_mu]")
              .Define("fake_Muon_pfRelIso04_all"  ,"Muon_pfRelIso04_all[fake_mu]")
              .Define("fake_Muon_miniPFRelIso_all","Muon_miniPFRelIso_all[fake_mu]")
              .Define("fake_Muon_nStations"       ,"Muon_nStations[fake_mu]")
              .Define("fake_Muon_nTrackerLayers"  ,"Muon_nTrackerLayers[fake_mu]")
              .Define("fake_Muon_pfRelIso03_chg"  ,"Muon_pfRelIso03_chg[fake_mu]")
              .Define("fake_Muon_p"               ,"computeMomentum(fake_Muon_pt,fake_Muon_eta,fake_Muon_phi,fake_Muon_mass)")
              .Define("fakeable_mu"               ,"(abs(fake_Muon_dxy) < 0.05 && abs(fake_Muon_dz) < 0.10 && abs(fake_Muon_eta) < 2.4 && fake_Muon_pt > 10 && fake_Muon_looseId == true && fake_Muon_mediumId == true && fake_Muon_pfIsoId >= 1 && fake_Muon_jetRelIso < 0.5)")
              .Define("tight_mu"                  ,"{0}".format(tight_mu))

              .Define("loose_el"                          ,"abs(Electron_eta) < 2.5 && Electron_pt > 10 && Electron_cutBased >= 1")
              .Define("fake_el"                           ,"{0}".format(fake_el))
              .Define("fake_Electron_pt"                  ,"Electron_pt[fake_el]")
              .Define("fake_Electron_eta"                 ,"Electron_eta[fake_el]")
              .Define("fake_Electron_phi"                 ,"Electron_phi[fake_el]")
              .Define("fake_Electron_mass"                ,"Electron_mass[fake_el]")
              .Define("fake_Electron_charge"              ,"Electron_charge[fake_el]")
              .Define("fake_Electron_jetRelIso"           ,"Electron_jetRelIso[fake_el]")
              .Define("fake_Electron_dxy"                 ,"Electron_dxy[fake_el]")
              .Define("fake_Electron_dz"                  ,"Electron_dz[fake_el]")
              .Define("fake_Electron_sip3d"               ,"Electron_sip3d[fake_el]")
              .Define("fake_Electron_cutBased"            ,"Electron_cutBased[fake_el]")
              .Define("fake_Electron_mvaNoIso_WP80"       ,"Electron_mvaNoIso_WP80[fake_el]")
              .Define("fake_Electron_mvaIso_WP80"         ,"Electron_mvaIso_WP80[fake_el]")
              .Define("fake_Electron_mvaIso_WP90"         ,"Electron_mvaIso_WP90[fake_el]")
              .Define("fake_Electron_tightCharge"         ,"Electron_tightCharge[fake_el]")
              .Define("fake_Electron_promptMVA"           ,"Electron_{0}[fake_el]".format(MVAName))
              .Define("fake_Electron_mvaIso"              ,"Electron_mvaIso[fake_el]")
              .Define("fake_Electron_mvaNoIso"            ,"Electron_mvaNoIso[fake_el]")
              .Define("fake_Electron_pfRelIso03_all"      ,"Electron_pfRelIso03_all[fake_el]")
              .Define("fake_Electron_miniPFRelIso_all"    ,"Electron_miniPFRelIso_all[fake_el]")
              .Define("fake_Electron_hoe"                 ,"Electron_hoe[fake_el]")
              .Define("fake_Electron_r9"                  ,"Electron_r9[fake_el]")
              .Define("fake_Electron_pfRelIso03_chg"      ,"Electron_pfRelIso03_chg[fake_el]")
              .Define("fake_Electron_seedGain"            ,"Electron_seedGain[fake_el]")
              .Define("fake_Electron_superclusterEta"     ,"Electron_{0}[fake_el]".format(SCEtaName))
              .Define("fakeable_el"                       ,"(abs(fake_Electron_dxy) < 0.05 && abs(fake_Electron_dz) < 0.10 && abs(fake_Electron_eta) < 2.5 && fake_Electron_pt > 10 && fake_Electron_cutBased >= 2 && fake_Electron_jetRelIso < 0.5)")
              .Define("tight_el"                          ,"{0}".format(tight_el))

              .Define("nLoose","Sum(loose_mu)+Sum(loose_el)")
              .Define("nFake","Sum(fake_mu)+Sum(fake_el)")
              .Define("nTight","Sum(tight_mu)+Sum(tight_el)")
              )

    return dftag

def selectionDAWeigths(df,year,PDType,whichAna,fakeRateSel):
    dftag =(df.Define("PDType","\"{0}\"".format(PDType))
              .Define("weightFake","compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[0],fakeRateSel[0],whichAna))
              .Define("weight","weightFake*1.0")
              .Define("nWS","0")
              .Define("weightWS", "1.0")
              .Define("weightEWKCorr", "1.0")
              .Define("weight0","1.0")
              .Define("weight1","weightFake*1.0")
              .Define("weight2","weightFake*1.0")
              .Define("weight3","weightFake*1.0")
              .Define("weight4","weightFake*1.0")
              .Define("weight5","weightFake*1.0")
              .Define("weight6","weightFake*1.0")
              .Define("weight7","weightFake*1.0")
              .Define("weightNoLepSF","weightFake*1.0")
              .Define("weightBTag","weight")
              .Define("weightNoBTag","weight")
              .Define("weightFakeAltm0","weight/weightFake*compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[1],fakeRateSel[0],whichAna))
              .Define("weightFakeAltm1","weight/weightFake*compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[2],fakeRateSel[0],whichAna))
              .Define("weightFakeAltm2","weight/weightFake*compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[3],fakeRateSel[0],whichAna))
              .Define("weightFakeAlte0","weight/weightFake*compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[0],fakeRateSel[1],whichAna))
              .Define("weightFakeAlte1","weight/weightFake*compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[0],fakeRateSel[2],whichAna))
              .Define("weightFakeAlte2","weight/weightFake*compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[0],fakeRateSel[3],whichAna))
              .Define("weightWSUnc0","weight")
              .Define("weightWSUnc1","weight")
              .Define("weightEWKUnc", "weight")
              )

    return dftag

def selectionMCWeigths(df,year,PDType,weight,type,bTagSel,useBTaggingWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,MUOWP,ELEWP,correctionString,whichAna,fakeRateSel):

    hasTheoryColumnName = [True, True, True]
    theoryColumnName = ["PSWeight", "LHEScaleWeight", "LHEPdfWeight"]
    for x in range(len(theoryColumnName)):
        try:
            ColumnType = df.GetColumnType(theoryColumnName[x])
        except Exception as e:
            print("No {0} weights: {1}".format(theoryColumnName[x],e))
            hasTheoryColumnName[x] = False

    MUOYEAR = year
    ELEYEAR = "NULL"
    if  (year == 20220): ELEYEAR = "2022Re-recoBCD"
    elif(year == 20221): ELEYEAR = "2022Re-recoE+PromptFG"
    elif(year == 20230): ELEYEAR = "2023PromptC"
    elif(year == 20231): ELEYEAR = "2023PromptD"
    elif(year == 20240): ELEYEAR = "2024Prompt"
    PHOYEAR = "NULL"
    if  (year == 20220): PHOYEAR = "2022Re-recoBCD"
    elif(year == 20221): PHOYEAR = "2022Re-recoE+PromptFG"
    elif(year == 20230): PHOYEAR = "2023PromptC"
    elif(year == 20231): PHOYEAR = "2023PromptD"
    elif(year == 20240): PHOYEAR = "2024_ID"
    if(correctionString == "_correction"):
        MUOWP = "Medium"
        ELEWP = "Medium"
    print("MUOYEAR/ELEYEAR/PHOYEAR/MUOWP/ELEWP/whichAna: {0}/{1}/{2}/{3}/{4}/{5}".format(MUOYEAR,ELEYEAR,PHOYEAR,MUOWP,ELEWP,whichAna))

    dftag =(df.Define("PDType","\"{0}\"".format(PDType))
              .Define("clean_Jet_hadronFlavour", "Jet_hadronFlavour[clean_jet]")
              .Define("goodbtag_Jet_hadronFlavour","clean_Jet_hadronFlavour[goodbtag_jet]")
              .Define("fake_Muon_genPartFlav","Muon_genPartFlav[fake_mu]")
              .Define("fake_Muon_genPartIdx","Muon_genPartIdx[fake_mu]")
              .Define("fake_Electron_genPartFlav","Electron_genPartFlav[fake_el]")
              .Define("fake_Electron_genPartIdx","Electron_genPartIdx[fake_el]")
              .Define("weightPURecoSF","compute_PURecoSF(fake_Muon_pt,fake_Muon_eta,fake_Electron_pt,fake_Electron_eta,Pileup_nTrueInt,0)")
              .Define("weightMuonSF","compute_MuonSF(fake_Muon_pt,fake_Muon_eta)")
              .Define("weightElectronSF","compute_ElectronSF(fake_Electron_pt,fake_Electron_eta)")
              .Define("weightTriggerSF","compute_TriggerSF(ptl1,ptl2,etal1,etal2,ltype,0)")
             #.Define("weightTriggerSF","compute_TriggerForSingleLegsSF(ptl1,ptl2,etal1,etal2,ltype)")

              .Define("weightMC","compute_weights({0},genWeight,PDType,fake_Muon_genPartFlav,fake_Electron_genPartFlav,{1})".format(weight,type))
              .Filter("weightMC != 0","MC weight")

              .Define("nWS", "compute_number_WS(fake_Muon_pt,fake_Muon_eta,fake_Muon_charge,fake_Muon_genPartIdx,fake_Electron_pt,fake_Electron_eta,fake_Electron_charge,fake_Electron_genPartIdx,GenPart_pdgId)")

              .Define("MUOYEAR","\"{0}\"".format(MUOYEAR))
              .Define("ELEYEAR","\"{0}\"".format(ELEYEAR))
              .Define("PHOYEAR","\"{0}\"".format(PHOYEAR))
              .Define("MUOWP","\"{0}\"".format(MUOWP))
              .Define("ELEWP","\"{0}\"".format(ELEWP))
              .Define("PHOWP","\"Medium\"")

              .Define("weightFake","compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[0],fakeRateSel[0],whichAna))

              .Define("weightBtagSF","compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"central\",0,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))

              .Define("weightMuoSFJSON","compute_JSON_MUO_SFs(\"nominal\",\"nominal\",\"nominal\",fake_Muon_pt,fake_Muon_eta,fake_Muon_p,0)")

              .Define("weightEleSFJSON","compute_JSON_ELE_SFs(ELEYEAR,\"sf\",\"sf\",ELEWP,fake_Electron_pt,fake_Electron_eta,fake_Electron_phi)")

              .Define("weightPUSF_Nom","compute_JSON_PU_SF(Pileup_nTrueInt,\"nominal\")")

              .Define("weightWS", "compute_WSSF({0},fake_Electron_pt,fake_Electron_eta,fake_Electron_charge,fake_Electron_genPartIdx,GenPart_pdgId)".format(whichAna))

              .Define("weightEWKCorr", "compute_EWKCorr(0,PDType,mjjGen)")

              #.Define("weightPTWWCorr", "compute_PTWWCorr(0,PDType,ptww)")
              )

    if(correctionString == "_correction"):
        if(useBTaggingWeights == 1):
            print("BtagCorr/AddCorr: 1/1")
            dftag = (dftag
                     .Define("weight","weightMC*weightFake*weightWS*weightEWKCorr*weightBtagSF*weightPURecoSF*weightTriggerSF*weightMuoSFJSON*weightEleSFJSON*weightMuonSF*weightElectronSF")
                     .Define("weightMuoCorr","weightMuoSFJSON*weightMuonSF")
                     .Define("weightEleCorr","weightEleSFJSON*weightElectronSF")
                    )
        else:
            print("BtagCorr/AddCorr: 0/1")
            dftag = (dftag
                     .Define("weight","weightMC*weightFake*weightWS*weightEWKCorr*weightPURecoSF*weightTriggerSF*weightMuoSFJSON*weightEleSFJSON*weightMuonSF*weightElectronSF")
                     .Define("weightMuoCorr","weightMuoSFJSON*weightMuonSF")
                     .Define("weightEleCorr","weightEleSFJSON*weightElectronSF")
                    )

    else:
        if(useBTaggingWeights == 1):
            print("BtagCorr/AddCorr: 1/0")
            dftag = (dftag
                     .Define("weight","weightMC*weightFake*weightWS*weightEWKCorr*weightBtagSF*weightPURecoSF*weightTriggerSF*weightMuoSFJSON*weightEleSFJSON")
                     .Define("weightMuoCorr","weightMuoSFJSON")
                     .Define("weightEleCorr","weightEleSFJSON")
                    )
        else:
            print("BtagCorr/AddCorr: 0/0")
            dftag = (dftag
                     .Define("weight","weightMC*weightFake*weightWS*weightEWKCorr*weightPURecoSF*weightTriggerSF*weightMuoSFJSON*weightEleSFJSON")
                     .Define("weightMuoCorr","weightMuoSFJSON")
                     .Define("weightEleCorr","weightEleSFJSON")
                    )

    if(useBTaggingWeights == 1):
        dftag = (dftag
                 .Define("weightNoLepSF","weightMC*weightFake*weightWS*weightEWKCorr*weightBtagSF*weightPURecoSF*weightTriggerSF")
                 .Define("weightBTag","weight")
                 .Define("weightNoBTag","weight/weightBtagSF")
                )
    else:
        dftag = (dftag
                 .Define("weightNoLepSF","weightMC*weightFake*weightWS*weightEWKCorr*weightPURecoSF*weightTriggerSF")
                 .Define("weightBTag","weight*weightBtagSF")
                 .Define("weightNoBTag","weight")
                )

    dftag =(dftag.Define("weight0","weight/weightBtagSF")
                 .Define("weight1","weight/weightPURecoSF")
                 .Define("weight2","weight/weightTriggerSF")
                 .Define("weight3","weight/weightMuoCorr")
                 .Define("weight4","weight/weightEleCorr")
                 .Define("weight5","weight/weightWS")
                 .Define("weight6","weightMC*weightFake")
                 .Define("weight7","weight/weightEWKCorr")

                 .Define("weightMuoSFTRKUp","weight/weightMuoSFJSON*compute_JSON_MUO_SFs(\"syst\",\"nominal\",\"nominal\",fake_Muon_pt,fake_Muon_eta,fake_Muon_p,+1)")
                 .Define("weightMuoSFIDUp" ,"weight/weightMuoSFJSON*compute_JSON_MUO_SFs(\"nominal\",\"syst\",\"nominal\",fake_Muon_pt,fake_Muon_eta,fake_Muon_p,+1)")
                 .Define("weightMuoSFISOUp","weight/weightMuoSFJSON*compute_JSON_MUO_SFs(\"nominal\",\"nominal\",\"syst\",fake_Muon_pt,fake_Muon_eta,fake_Muon_p,+1)")

                 .Define("weightMuoSFTRKDown","weight/weightMuoSFJSON*compute_JSON_MUO_SFs(\"syst\",\"nominal\",\"nominal\",fake_Muon_pt,fake_Muon_eta,fake_Muon_p,-1)")
                 .Define("weightMuoSFIDDown" ,"weight/weightMuoSFJSON*compute_JSON_MUO_SFs(\"nominal\",\"syst\",\"nominal\",fake_Muon_pt,fake_Muon_eta,fake_Muon_p,-1)")
                 .Define("weightMuoSFISODown","weight/weightMuoSFJSON*compute_JSON_MUO_SFs(\"nominal\",\"nominal\",\"syst\",fake_Muon_pt,fake_Muon_eta,fake_Muon_p,-1)")

                 .Define("weightEleSFTRKUp","weight/weightEleSFJSON*compute_JSON_ELE_SFs(ELEYEAR,\"sfup\",\"sf\",ELEWP,fake_Electron_pt,fake_Electron_eta,fake_Electron_phi)")
                 .Define("weightEleSFIDUp" ,"weight/weightEleSFJSON*compute_JSON_ELE_SFs(ELEYEAR,\"sf\",\"sfup\",ELEWP,fake_Electron_pt,fake_Electron_eta,fake_Electron_phi)")

                 .Define("weightEleSFTRKDown","weight/weightEleSFJSON*compute_JSON_ELE_SFs(ELEYEAR,\"sfdown\",\"sf\",ELEWP,fake_Electron_pt,fake_Electron_eta,fake_Electron_phi)")
                 .Define("weightEleSFIDDown" ,"weight/weightEleSFJSON*compute_JSON_ELE_SFs(ELEYEAR,\"sf\",\"sfdown\",ELEWP,fake_Electron_pt,fake_Electron_eta,fake_Electron_phi)")

                 #.Define("weightPUSF_Up"  ,"weight/weightPUSF_Nom*compute_JSON_PU_SF(Pileup_nTrueInt,\"up\")")
                 #.Define("weightPUSF_Down","weight/weightPUSF_Nom*compute_JSON_PU_SF(Pileup_nTrueInt,\"down\")")
                 .Define("weightPUSF_Up"  ,"weight/weightPURecoSF*compute_PURecoSF(fake_Muon_pt,fake_Muon_eta,fake_Electron_pt,fake_Electron_eta,Pileup_nTrueInt,1)")
                 .Define("weightPUSF_Down","weight/weightPURecoSF*compute_PURecoSF(fake_Muon_pt,fake_Muon_eta,fake_Electron_pt,fake_Electron_eta,Pileup_nTrueInt,2)")

                 .Define("weightPhoSFJSON","compute_JSON_PHO_SFs(PHOYEAR,\"sf\",PHOWP,good_Photons_pt,good_Photons_eta,good_Photons_phi)")
                 .Filter("weightPhoSFJSON > 0","weightPhoSFJSON > 0")

                 .Define("weightTauSFJSON","compute_JSON_TAU_SFs(good_Tau_pt,good_Tau_eta,good_Tau_decayMode,good_Tau_genPartFlav,\"nom\")")
                 .Filter("weightTauSFJSON > 0","weightTauSFJSON > 0")

                 .Define("weightFakeAltm0","weight/weightFake*compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[1],fakeRateSel[0],whichAna))
                 .Define("weightFakeAltm1","weight/weightFake*compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[2],fakeRateSel[0],whichAna))
                 .Define("weightFakeAltm2","weight/weightFake*compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[3],fakeRateSel[0],whichAna))
                 .Define("weightFakeAlte0","weight/weightFake*compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[0],fakeRateSel[1],whichAna))
                 .Define("weightFakeAlte1","weight/weightFake*compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[0],fakeRateSel[2],whichAna))
                 .Define("weightFakeAlte2","weight/weightFake*compute_fakeRate(isData,fake_Muon_pt,fake_Muon_eta,fake_Muon_jetRelIso,tight_mu,{0},fake_Electron_pt,fake_Electron_eta,fake_Electron_jetRelIso,tight_el,{1},{2})".format(fakeRateSel[0],fakeRateSel[3],whichAna))

                 .Define("weightWSUnc0","weight/weightWS*compute_WSSF({0},fake_Electron_pt,fake_Electron_eta,fake_Electron_charge,fake_Electron_genPartIdx,GenPart_pdgId)".format(2))
                 .Define("weightWSUnc1","weight/weightWS*compute_WSSF({0},fake_Electron_pt,fake_Electron_eta,fake_Electron_charge,fake_Electron_genPartIdx,GenPart_pdgId)".format(3))

                 .Define("weightEWKCorrUnc","weight/weightEWKCorr*compute_EWKCorr(1,PDType,mjjGen)")

                 .Define("weightTriggerSFUp"  ,"weight/weightTriggerSF*compute_TriggerSF(ptl1,ptl2,etal1,etal2,ltype,+1)")
                 .Define("weightTriggerSFDown","weight/weightTriggerSF*compute_TriggerSF(ptl1,ptl2,etal1,etal2,ltype,-1)")

                 )

    dftag =(dftag.Define("weightBtagSFBC_00Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"central\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_01Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"central\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_02Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"central\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_03Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"up_bfragmentation\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_04Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"up_colorreconnection\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_05Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"up_hdamp\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_06Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"up_jer\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_07Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"up_jes\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_08Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"up_pdf\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_09Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"up_pileup\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_10Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"up_topmass\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_11Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"up_type3\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_12Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"up_statistic\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))

                 .Define("weightBtagSFBC_00Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"central\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_01Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"central\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_02Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"central\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_03Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"down_bfragmentation\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_04Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"down_colorreconnection\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_05Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"down_hdamp\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_06Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"down_jer\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_07Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"down_jes\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_08Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"down_pdf\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_09Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"down_pileup\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_10Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"down_topmass\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_11Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"down_type3\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFBC_12Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"down_statistic\",1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))

                 .Define("weightBtagSFLF_00Up"  ,"weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"up\",-1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 .Define("weightBtagSFLF_00Down","weight/weightBtagSF*compute_JSON_BTV_SF(goodbtag_Jet_pt,goodbtag_Jet_eta,goodbtag_Jet_btagUnifiedParTB,goodbtag_Jet_hadronFlavour,\"down\",-1,{0},{1})".format(bTagSel,getBTagCut(bTagSel,year)))
                 )

    if(hasTheoryColumnName[0] == True and nTheoryReplicas[2] == 4):
        dftag =(dftag.Define("weightPS0" ,"weight*PSWeight[0]/{0}".format(genEventSumPSRenorm[0]))
                     .Define("weightPS1" ,"weight*PSWeight[1]/{0}".format(genEventSumPSRenorm[1]))
                     .Define("weightPS2" ,"weight*PSWeight[2]/{0}".format(genEventSumPSRenorm[2]))
                     .Define("weightPS3" ,"weight*PSWeight[3]/{0}".format(genEventSumPSRenorm[3]))
                     )
    else:
        dftag =(dftag.Define("weightPS0" ,"weight*1.0")
                     .Define("weightPS1" ,"weight*1.0")
                     .Define("weightPS2" ,"weight*1.0")
                     .Define("weightPS3" ,"weight*1.0")
                     )

    if(hasTheoryColumnName[1] == True and nTheoryReplicas[1] == 9):
        #LHEScaleWeight 2 / 4 / 6 not used
        dftag =(dftag.Define("weightQCDScale0" ,"weight*LHEScaleWeight[0]/{0}".format(genEventSumLHEScaleRenorm[0]))
                     .Define("weightQCDScale1" ,"weight*LHEScaleWeight[1]/{0}".format(genEventSumLHEScaleRenorm[1]))
                     .Define("weightQCDScale2" ,"weight*LHEScaleWeight[3]/{0}".format(genEventSumLHEScaleRenorm[2]))
                     .Define("weightQCDScale3" ,"weight*LHEScaleWeight[5]/{0}".format(genEventSumLHEScaleRenorm[3]))
                     .Define("weightQCDScale4" ,"weight*LHEScaleWeight[7]/{0}".format(genEventSumLHEScaleRenorm[4]))
                     .Define("weightQCDScale5" ,"weight*LHEScaleWeight[8]/{0}".format(genEventSumLHEScaleRenorm[5]))
                     )
    else:
        dftag =(dftag.Define("weightQCDScale0" ,"weight*1.0")
                     .Define("weightQCDScale1" ,"weight*1.0")
                     .Define("weightQCDScale2" ,"weight*1.0")
                     .Define("weightQCDScale3" ,"weight*1.0")
                     .Define("weightQCDScale4" ,"weight*1.0")
                     .Define("weightQCDScale5" ,"weight*1.0")
                     )

    # 0 (default) 1...100 101/102 (Up/Down for alphas)
    if(hasTheoryColumnName[2] == True):
        for xpdf in range(103):
            if(nTheoryReplicas[0] > xpdf):
                dftag = dftag.Define("weightPDF{0}".format(xpdf),"weight*LHEPdfWeight[{0}]".format(xpdf))
            else:
                dftag = dftag.Define("weightPDF{0}".format(xpdf),"weight*1.0")
    else:
        for xpdf in range(103):
            dftag = dftag.Define("weightPDF{0}".format(xpdf),"weight*1.0")

    return dftag

def selectionTheoryWeigths(dftag,weight,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm):

    hasTheoryColumnName = [True, True, True]
    theoryColumnName = ["PSWeight", "LHEScaleWeight", "LHEPdfWeight"]
    for x in range(len(theoryColumnName)):
        try:
            ColumnType = dftag.GetColumnType(theoryColumnName[x])
        except Exception as e:
            print("No {0} weights: {1}".format(theoryColumnName[x],e))
            hasTheoryColumnName[x] = False

    if(hasTheoryColumnName[0] == True and nTheoryReplicas[2] == 4):
        dftag =(dftag.Define("weightPS0" ,"weight*PSWeight[0]/{0}".format(genEventSumPSRenorm[0]))
                     .Define("weightPS1" ,"weight*PSWeight[1]/{0}".format(genEventSumPSRenorm[1]))
                     .Define("weightPS2" ,"weight*PSWeight[2]/{0}".format(genEventSumPSRenorm[2]))
                     .Define("weightPS3" ,"weight*PSWeight[3]/{0}".format(genEventSumPSRenorm[3]))
                     )
    else:
        dftag =(dftag.Define("weightPS0" ,"weight*1.0")
                     .Define("weightPS1" ,"weight*1.0")
                     .Define("weightPS2" ,"weight*1.0")
                     .Define("weightPS3" ,"weight*1.0")
                     )

    if(hasTheoryColumnName[1] == True and nTheoryReplicas[1] == 9):
        #LHEScaleWeight 2 / 4 / 6 not used
        dftag =(dftag.Define("weightQCDScale0" ,"weight*LHEScaleWeight[0]/{0}".format(genEventSumLHEScaleRenorm[0]))
                     .Define("weightQCDScale1" ,"weight*LHEScaleWeight[1]/{0}".format(genEventSumLHEScaleRenorm[1]))
                     .Define("weightQCDScale2" ,"weight*LHEScaleWeight[3]/{0}".format(genEventSumLHEScaleRenorm[2]))
                     .Define("weightQCDScale3" ,"weight*LHEScaleWeight[5]/{0}".format(genEventSumLHEScaleRenorm[3]))
                     .Define("weightQCDScale4" ,"weight*LHEScaleWeight[7]/{0}".format(genEventSumLHEScaleRenorm[4]))
                     .Define("weightQCDScale5" ,"weight*LHEScaleWeight[8]/{0}".format(genEventSumLHEScaleRenorm[5]))
                     )
    else:
        dftag =(dftag.Define("weightQCDScale0" ,"weight*1.0")
                     .Define("weightQCDScale1" ,"weight*1.0")
                     .Define("weightQCDScale2" ,"weight*1.0")
                     .Define("weightQCDScale3" ,"weight*1.0")
                     .Define("weightQCDScale4" ,"weight*1.0")
                     .Define("weightQCDScale5" ,"weight*1.0")
                     )

    # 0 (default) 1...100 101/102 (Up/Down for alphas)
    if(hasTheoryColumnName[2] == True):
        for xpdf in range(103):
            if(nTheoryReplicas[0] > xpdf):
                dftag = dftag.Define("weightPDF{0}".format(xpdf),"weight*LHEPdfWeight[{0}]".format(xpdf))
            else:
                dftag = dftag.Define("weightPDF{0}".format(xpdf),"weight*1.0")
    else:
        for xpdf in range(103):
            dftag = dftag.Define("weightPDF{0}".format(xpdf),"weight*1.0")

    return dftag

def selectionWeigths(df,isData,year,PDType,weight,type,bTagSel,useBTaggingWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,MUOWP,ELEWP,correctionString,whichAna):
    fakeRateSel = [2, 5, 1, 8] # default, unc1, unc2, unc3
    if(whichAna == 1):
        fakeRateSel[0] = 1
        fakeRateSel[1] = 4
        fakeRateSel[2] = 3
        fakeRateSel[3] = 7
    elif(whichAna == 2 or whichAna == 3):
        fakeRateSel[0] = 0
        fakeRateSel[1] = 1
        fakeRateSel[2] = 3
        fakeRateSel[3] = 6

    if(isData == "true"): return selectionDAWeigths(df,year,PDType,whichAna,fakeRateSel)
    else:                 return selectionMCWeigths(df,year,PDType,weight,type,bTagSel,useBTaggingWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,MUOWP,ELEWP,correctionString,whichAna,fakeRateSel)

def makeFinalVariable(df,var,theCat,start,x,bin,min,max,type):
    histoNumber = start+type
    if(theCat == plotCategory("kPlotData")):
        return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weight")

    if  (type ==  0): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weight")
    elif(type ==  1): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightPS0")
    elif(type ==  2): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightPS1")
    elif(type ==  3): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightPS2")
    elif(type ==  4): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightPS3")
    elif(type ==  5): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightQCDScale0")
    elif(type ==  6): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightQCDScale1")
    elif(type ==  7): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightQCDScale2")
    elif(type ==  8): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightQCDScale3")
    elif(type ==  9): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightQCDScale4")
    elif(type == 10): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightQCDScale5")
    elif(type >= 11 and type <= 113):
                      return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightPDF{0}".format(type-11))

    elif(type == 114): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightMuoSFTRKUp")
    elif(type == 115): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightMuoSFIDUp")
    elif(type == 116): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightMuoSFISOUp")
    elif(type == 117): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightEleSFTRKUp")
    elif(type == 118): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightEleSFIDUp")
    elif(type == 119): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightPUSF_Up")
    elif(type == 120): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightTriggerSFUp")
    elif(type == 121): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_00Up")
    elif(type == 122): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_01Up")
    elif(type == 123): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_02Up")
    elif(type == 124): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_03Up")
    elif(type == 125): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_04Up")
    elif(type == 126): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_05Up")
    elif(type == 127): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_06Up")
    elif(type == 128): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_07Up")
    elif(type == 129): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_08Up")
    elif(type == 130): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_09Up")
    elif(type == 131): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_10Up")
    elif(type == 132): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_11Up")
    elif(type == 133): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFBC_12Up")
    elif(type == 134): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightBtagSFLF_00Up")
    elif(type == 135): return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weightEWKCorrUnc")

    else:              return df.Histo1D(("histo_{0}_{1}".format(histoNumber,x), "histo_{0}_{1}".format(histoNumber,x),bin,min,max), "{0}".format(var),"weight")

def makeFinalVariable2D(df,varX,varY,theCat,start,x,binX,minX,maxX,binY,minY,maxY,type):
    histoNumber = start+type
    if(theCat == plotCategory("kPlotData")):
        return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weight")

    if  (type ==  0): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weight")
    elif(type ==  1): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightPS0")
    elif(type ==  2): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightPS1")
    elif(type ==  3): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightPS2")
    elif(type ==  4): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightPS3")
    elif(type ==  5): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightQCDScale0")
    elif(type ==  6): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightQCDScale1")
    elif(type ==  7): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightQCDScale2")
    elif(type ==  8): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightQCDScale3")
    elif(type ==  9): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightQCDScale4")
    elif(type == 10): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightQCDScale5")
    elif(type >= 11 and type <= 113):
                      return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightPDF{0}".format(type-11))

    elif(type == 114): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightMuoSFTRKUp")
    elif(type == 115): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightMuoSFIDUp")
    elif(type == 116): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightMuoSFISOUp")
    elif(type == 117): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightEleSFTRKUp")
    elif(type == 118): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightEleSFIDUp")
    elif(type == 119): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightPUSF_Up")
    elif(type == 120): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightTriggerSFUp")
    elif(type == 121): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_00Up")
    elif(type == 122): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_01Up")
    elif(type == 123): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_02Up")
    elif(type == 124): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_03Up")
    elif(type == 125): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_04Up")
    elif(type == 126): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_05Up")
    elif(type == 127): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_06Up")
    elif(type == 128): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_07Up")
    elif(type == 129): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_08Up")
    elif(type == 130): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_09Up")
    elif(type == 131): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_10Up")
    elif(type == 132): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_11Up")
    elif(type == 133): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFBC_12Up")
    elif(type == 134): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightBtagSFLF_00Up")
    elif(type == 135): return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weightEWKCorrUnc")

    else:              return df.Histo2D(("histo2d_{0}_{1}".format(histoNumber,x), "histo2d_{0}_{1}".format(histoNumber,x),binX,minX,maxX,binY,minY,maxY), "{0}".format(varX), "{0}".format(varY),"weight")
