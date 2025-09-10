import ROOT
import os, sys, getopt, json
from array import array

ROOT.ROOT.EnableImplicitMT(10)
from utilsCategory import plotCategory
from utilsAna import getMClist, getDATAlist, groupFiles, getTriggerFromJson, getLeptomSelFromJson, getLumi
from utilsAna import SwitchSample
#from utilsSelectionNanoV9 import getBTagCut
#from utilsSelectionNanoV9 import selectionTrigger2L,selectionElMu,selection2LVar,selectionJetMet
from utilsSelection import getBTagCut
from utilsSelection import selectionTrigger2L,selectionElMu,selection2LVar,selectionJetMet, selectionGenLepJet, selectionTheoryWeigths, makeFinalVariable

selectionJsonPath = "config/selection.json"

with open(selectionJsonPath) as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

JSON = jsonObject['JSON']

VBSSEL = jsonObject['VBSSEL']

# 0 = T, 1 = M, 2 = L
bTagSel = 2
useBTaggingWeights = 1

jetEtaCut = 2.5

muSelChoice = 0

elSelChoice = 0

def selectionWW(df,year,PDType,isData,count):

    overallLeptonSel = jsonObject['leptonSel']
    FAKE_MU   = getLeptomSelFromJson(overallLeptonSel, "FAKE_MU",   year)
    TIGHT_MU  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU{0}".format(muSelChoice),  year, 1)

    FAKE_EL   = getLeptomSelFromJson(overallLeptonSel, "FAKE_EL",   year)
    TIGHT_EL  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL{0}".format(elSelChoice),  year, 1)

    dftag = selectionElMu(df,year,FAKE_MU,TIGHT_MU,FAKE_EL,TIGHT_EL)
    dftag = (dftag.Filter("nLoose >= 2","At least two loose leptons")
                  .Filter("nLoose == 2","Only two loose leptons")
                  .Define("loose_Muon_pt" ,"Muon_pt[loose_mu]")
                  .Define("loose_Electron_pt" ,"Electron_pt[loose_el]")
                  .Filter("(Sum(loose_mu) == 2 && loose_Muon_pt[0] > 20 && loose_Muon_pt[1] > 20)||(Sum(loose_el) == 2 && loose_Electron_pt[0] > 20 && loose_Electron_pt[1] > 20)||(Sum(loose_mu) == 1 && Sum(loose_el) == 1 && loose_Muon_pt[0] > 20 && loose_Electron_pt[0] > 20)","ptl1/2 > 20")
                 #.Filter("Sum(loose_mu) == 1 && Sum(loose_el) == 1","e-mu events")
                  .Filter("Sum(loose_mu)+Sum(loose_el) == 2","2l events")
                  .Filter("nFake == 2","Two fake leptons")
                  .Filter("nTight == 2","Two tight leptons")
                  .Filter("Sum(fake_Muon_charge)+Sum(fake_Electron_charge) == 0", "Opposite-sign leptons")
                  )

    dftag = selection2LVar  (dftag,year,isData)
    dftag = (dftag.Filter("ptl1 > 25", "ptl1 > 25")
                  .Filter("ptl2 > 20", "ptl2 > 20")
                 #.Filter("mll > 20","mll > 20")
                 #.Filter("ptll > 30","ptll > 30")
                  .Filter("mll > 85","mll > 85")
                  )

    dftag = selectionJetMet (dftag,year,bTagSel,isData,count,5.0)
    #dftag = (dftag.Filter("PuppiMET_pt > 20", "PuppiMET_pt > 20")
    #              .Filter("minPMET > 20", "minPMET > 20")
    #              )

    return dftag

def analysis(df,count,category,weight,year,PDType,isData,whichJob,histo_wwpt,puWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm):

    xPtBins = array('d', [20,25,30,35,40,50,60,80,100,150,250,500,1000])
    xEtaBins = array('d', [0.0,0.3,0.6,0.9,1.2,1.5,1.8,2.1,2.5])

    print("starting {0} / {1} / {2} / {3} / {4} / {5} / {6}".format(count,category,weight,year,PDType,isData,whichJob))

    theCat = category
    if(theCat > 100): theCat = plotCategory("kPlotData")

    nCat, nHisto = plotCategory("kPlotCategories"), 200
    histo   = [[0 for x in range(nCat)] for y in range(nHisto)]
    histo2D = [[0 for y in range(nCat)] for x in range(nHisto)]

    ROOT.initHisto1D(histo_wwpt[0],3)
    ROOT.initHisto1D(histo_wwpt[1],4)
    ROOT.initHisto1D(histo_wwpt[2],5)
    ROOT.initHisto1D(histo_wwpt[3],6)
    ROOT.initHisto1D(histo_wwpt[4],7)
    ROOT.initHisto1D(puWeights[0],0)
    ROOT.initHisto1D(puWeights[1],1)
    ROOT.initHisto1D(puWeights[2],2)

    ROOT.initJSONSFs(year)

    dfcat = df.Define("PDType","\"{0}\"".format(PDType))\
              .Define("weightForBTag","1.0f")\
              .Define("weight","{0}*genWeight".format(weight/getLumi(year)))\
              .Filter("weight != 0","good weight")\
              .Define("weightPUSF"     ,"weight*compute_PURecoSF(Muon_pt,Muon_eta,Electron_pt,Electron_eta,Pileup_nTrueInt,0)")\
              .Define("weightPUSF_Up"  ,"weight*compute_PURecoSF(Muon_pt,Muon_eta,Electron_pt,Electron_eta,Pileup_nTrueInt,1)")\
              .Define("weightPUSF_Down","weight*compute_PURecoSF(Muon_pt,Muon_eta,Electron_pt,Electron_eta,Pileup_nTrueInt,2)")\
              .Define("weightLUMPUSF"     ,"weight*compute_JSON_PU_SF(Pileup_nTrueInt,\"nominal\")")\
              .Define("weightLUMPUSF_Up"  ,"weight*compute_JSON_PU_SF(Pileup_nTrueInt,\"up\")")\
              .Define("weightLUMPUSF_Down","weight*compute_JSON_PU_SF(Pileup_nTrueInt,\"down\")")

    dfcat = selectionTheoryWeigths(dfcat,weight,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm)

    x = 0
    histo[ 0][x] = dfcat.Histo1D(("histo_{0}_{1}".format( 0,x), "histo_{0}_{1}".format( 0,x), 100,  0, 100), "Pileup_nTrueInt","weightForBTag")
    histo[ 1][x] = dfcat.Histo1D(("histo_{0}_{1}".format( 1,x), "histo_{0}_{1}".format( 1,x), 100,  0, 100), "Pileup_nTrueInt","weight")
    histo[ 2][x] = dfcat.Histo1D(("histo_{0}_{1}".format( 2,x), "histo_{0}_{1}".format( 2,x), 100,  0, 100), "Pileup_nTrueInt","weightPUSF")
    histo[ 3][x] = dfcat.Histo1D(("histo_{0}_{1}".format( 3,x), "histo_{0}_{1}".format( 3,x), 100,  0, 100), "Pileup_nTrueInt","weightPUSF_Up")
    histo[ 4][x] = dfcat.Histo1D(("histo_{0}_{1}".format( 4,x), "histo_{0}_{1}".format( 4,x), 100,  0, 100), "Pileup_nTrueInt","weightPUSF_Down")
    histo[ 5][x] = dfcat.Histo1D(("histo_{0}_{1}".format( 5,x), "histo_{0}_{1}".format( 5,x), 100,  0, 100), "Pileup_nTrueInt","weightLUMPUSF")
    histo[ 6][x] = dfcat.Histo1D(("histo_{0}_{1}".format( 6,x), "histo_{0}_{1}".format( 6,x), 100,  0, 100), "Pileup_nTrueInt","weightLUMPUSF_Up")
    histo[ 7][x] = dfcat.Histo1D(("histo_{0}_{1}".format( 7,x), "histo_{0}_{1}".format( 7,x), 100,  0, 100), "Pileup_nTrueInt","weightLUMPUSF_Down")

    dfgen = (dfcat
          .Define("gen_z", "GenPart_pdgId == 23 && GenPart_status == 62")
          .Filter("Sum(gen_z) >= 1","nZ >= 1")
          .Filter("Sum(gen_z) == 1","nZ == 1")
          .Define("Zpt", "GenPart_pt[gen_z]")
          .Define("Zeta", "GenPart_eta[gen_z]")
          .Define("Zphi", "abs(GenPart_phi[gen_z])")
          .Define("Zmass", "GenPart_mass[gen_z]")
          .Filter("abs(Zmass[0]-91.1876) < 15","Zmass cut")
          .Define("Zrap", "abs(makeRapidity(Zpt[0],Zeta[0],Zphi[0],Zmass[0]))")
            )

    dfLLgen = (dfcat
          .Define("genLep", "(abs(GenDressedLepton_pdgId) == 11 || abs(GenDressedLepton_pdgId) == 13)")
          .Filter("Sum(genLep) == 2","genLep == 2")
          .Define("filter_GenDressedLepton_pt", "GenDressedLepton_pt[genLep]")
          .Define("filter_GenDressedLepton_eta", "GenDressedLepton_eta[genLep]")
          .Define("filter_GenDressedLepton_phi", "GenDressedLepton_phi[genLep]")
          .Define("filter_GenDressedLepton_mass", "GenDressedLepton_mass[genLep]")
          .Define("mllGen", "Minv2(filter_GenDressedLepton_pt[0], filter_GenDressedLepton_eta[0], filter_GenDressedLepton_phi[0], filter_GenDressedLepton_mass[0],filter_GenDressedLepton_pt[1], filter_GenDressedLepton_eta[1], filter_GenDressedLepton_phi[1], filter_GenDressedLepton_mass[1]).first")
            )

    dfww = selectionWW(dfcat,year,PDType,isData,count)
    dfww = selectionGenLepJet(dfww,20,30,jetEtaCut).Filter("ngood_GenDressedLeptons >= 2", "ngood_GenDressedLeptons >= 2")
    dfww = (dfww.Define("theGenCat0", "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,0)-1.0".format(0))
                .Define("theGenCat1", "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,1)-1.0".format(0))
                .Define("theGenCat2", "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,2)-1.0".format(0))
                .Define("theGenCat" , "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,3)-1.0".format(0))
                .Filter("theGenCat0 >= 0","theGenCat0 >= 0")
                .Filter("theGenCat1 >= 0","theGenCat1 >= 0")
                .Filter("theGenCat2 >= 0","theGenCat2 >= 0")
                .Filter("theGenCat  >= 0","theGenCat  >= 0")
                .Define("theNNLOWeight0", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,0)")
                .Define("theNNLOWeight1", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,1)")
                .Define("theNNLOWeight2", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,2)")
                .Define("theNNLOWeight3", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,3)")
                .Define("theNNLOWeight4", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,4)")
                )

    dfwwgen = selectionGenLepJet(dfcat,20,30,jetEtaCut).Filter("ngood_GenDressedLeptons >= 2", "ngood_GenDressedLeptons >= 2")
    dfwwgen = (dfwwgen.Define("theGenCat0", "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,0)-1.0".format(0))
                      .Define("theGenCat1", "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,1)-1.0".format(0))
                      .Define("theGenCat2", "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,2)-1.0".format(0))
                      .Define("theGenCat" , "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,3)-1.0".format(0))
                      .Filter("theGenCat0 >= 0","theGenCat0 >= 0")
                      .Filter("theGenCat1 >= 0","theGenCat1 >= 0")
                      .Filter("theGenCat2 >= 0","theGenCat2 >= 0")
                      .Filter("theGenCat  >= 0","theGenCat  >= 0")
                      .Define("theNNLOWeight0", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,0)")
                      .Define("theNNLOWeight1", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,1)")
                      .Define("theNNLOWeight2", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,2)")
                      .Define("theNNLOWeight3", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,3)")
                      .Define("theNNLOWeight4", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,4)")
                      )

    BTAGName = "UParTAK4"
    if((year // 10) < 2024): BTAGName = "RobustParTAK4"

    overallLeptonSel = jsonObject['leptonSel']
    FAKE_MU   = getLeptomSelFromJson(overallLeptonSel, "FAKE_MU",   year)
    FAKE_EL   = getLeptomSelFromJson(overallLeptonSel, "FAKE_EL",   year)

    dfcat = (dfcat
          .Define("loose_mu", "abs(Muon_eta) < 2.4 && Muon_pt > 10 && Muon_looseId == true")
          .Define("loose_el", "abs(Electron_eta) < 2.5 && Electron_pt > 10 && Electron_cutBased >= 1")
          .Filter("Sum(loose_mu)+Sum(loose_el) == 2","Two loose leptons")
          .Define("fake_mu","{0}".format(FAKE_MU))
          .Define("fake_el","{0}".format(FAKE_EL))
          .Define("nFake","Sum(fake_mu)+Sum(fake_el)")
          .Filter("nFake == 2","Two fake leptons")
          .Define("fake_Muon_pt"   ,"Muon_pt[fake_mu]")
          .Define("fake_Muon_eta"  ,"Muon_eta[fake_mu]")
          .Define("fake_Muon_phi"  ,"Muon_phi[fake_mu]")
          .Define("fake_Muon_mass" ,"Muon_mass[fake_mu]")
          .Define("fake_Electron_pt"   ,"Electron_pt[fake_el]")
          .Define("fake_Electron_eta"  ,"Electron_eta[fake_el]")
          .Define("fake_Electron_phi"  ,"Electron_phi[fake_el]")
          .Define("fake_Electron_mass" ,"Electron_mass[fake_el]")

          .Define("jet_mask1", "cleaningMask(Muon_jetIdx[fake_mu],nJet)")
          .Define("jet_mask2", "cleaningMask(Electron_jetIdx[fake_el],nJet)")
          .Define("goodloose_jet", "abs(Jet_eta) < 2.5 && Jet_pt > 20 && jet_mask1 && jet_mask2")
          .Define("ngoodloose_jets", "Sum(goodloose_jet)")
          .Define("goodloosejet_pt",           "Jet_pt[goodloose_jet]")
          .Define("goodloosejet_eta",          "abs(Jet_eta[goodloose_jet])")
          .Define("goodloosejet_phi",          "Jet_phi[goodloose_jet]")
          .Define("goodloosejet_mass",         "Jet_mass[goodloose_jet]")
          .Define("goodloosejet_hadronFlavour","Jet_hadronFlavour[goodloose_jet]")
          .Define("goodloosejet_btagUnifiedParTB","Jet_btag{0}B[goodloose_jet]".format(BTAGName))
          .Define("goodloosejet_lf",   "goodloosejet_hadronFlavour == 0")
          .Define("goodloosejet_cj",   "goodloosejet_hadronFlavour == 4")
          .Define("goodloosejet_bj",   "goodloosejet_hadronFlavour == 5")
          .Define("goodloosejet_lf_t", "goodloosejet_hadronFlavour == 0 && goodloosejet_btagUnifiedParTB > {0}".format(getBTagCut(0,year)))
          .Define("goodloosejet_cj_t", "goodloosejet_hadronFlavour == 4 && goodloosejet_btagUnifiedParTB > {0}".format(getBTagCut(0,year)))
          .Define("goodloosejet_bj_t", "goodloosejet_hadronFlavour == 5 && goodloosejet_btagUnifiedParTB > {0}".format(getBTagCut(0,year)))
          .Define("goodloosejet_lf_m", "goodloosejet_hadronFlavour == 0 && goodloosejet_btagUnifiedParTB > {0}".format(getBTagCut(1,year)))
          .Define("goodloosejet_cj_m", "goodloosejet_hadronFlavour == 4 && goodloosejet_btagUnifiedParTB > {0}".format(getBTagCut(1,year)))
          .Define("goodloosejet_bj_m", "goodloosejet_hadronFlavour == 5 && goodloosejet_btagUnifiedParTB > {0}".format(getBTagCut(1,year)))
          .Define("goodloosejet_lf_l", "goodloosejet_hadronFlavour == 0 && goodloosejet_btagUnifiedParTB > {0}".format(getBTagCut(2,year)))
          .Define("goodloosejet_cj_l", "goodloosejet_hadronFlavour == 4 && goodloosejet_btagUnifiedParTB > {0}".format(getBTagCut(2,year)))
          .Define("goodloosejet_bj_l", "goodloosejet_hadronFlavour == 5 && goodloosejet_btagUnifiedParTB > {0}".format(getBTagCut(2,year)))
          .Define("goodloosejet_pt_lf",   "goodloosejet_pt[goodloosejet_lf]")
          .Define("goodloosejet_pt_cj",   "goodloosejet_pt[goodloosejet_cj]")
          .Define("goodloosejet_pt_bj",   "goodloosejet_pt[goodloosejet_bj]")
          .Define("goodloosejet_pt_lf_t", "goodloosejet_pt[goodloosejet_lf_t]")
          .Define("goodloosejet_pt_cj_t", "goodloosejet_pt[goodloosejet_cj_t]")
          .Define("goodloosejet_pt_bj_t", "goodloosejet_pt[goodloosejet_bj_t]")
          .Define("goodloosejet_pt_lf_m", "goodloosejet_pt[goodloosejet_lf_m]")
          .Define("goodloosejet_pt_cj_m", "goodloosejet_pt[goodloosejet_cj_m]")
          .Define("goodloosejet_pt_bj_m", "goodloosejet_pt[goodloosejet_bj_m]")
          .Define("goodloosejet_pt_lf_l", "goodloosejet_pt[goodloosejet_lf_l]")
          .Define("goodloosejet_pt_cj_l", "goodloosejet_pt[goodloosejet_cj_l]")
          .Define("goodloosejet_pt_bj_l", "goodloosejet_pt[goodloosejet_bj_l]")
          .Define("goodloosejet_eta_lf",  "goodloosejet_eta[goodloosejet_lf]")
          .Define("goodloosejet_eta_cj",  "goodloosejet_eta[goodloosejet_cj]")
          .Define("goodloosejet_eta_bj",  "goodloosejet_eta[goodloosejet_bj]")
          .Define("goodloosejet_eta_lf_t","goodloosejet_eta[goodloosejet_lf_t]")
          .Define("goodloosejet_eta_cj_t","goodloosejet_eta[goodloosejet_cj_t]")
          .Define("goodloosejet_eta_bj_t","goodloosejet_eta[goodloosejet_bj_t]")
          .Define("goodloosejet_eta_lf_m","goodloosejet_eta[goodloosejet_lf_m]")
          .Define("goodloosejet_eta_cj_m","goodloosejet_eta[goodloosejet_cj_m]")
          .Define("goodloosejet_eta_bj_m","goodloosejet_eta[goodloosejet_bj_m]")
          .Define("goodloosejet_eta_lf_l","goodloosejet_eta[goodloosejet_lf_l]")
          .Define("goodloosejet_eta_cj_l","goodloosejet_eta[goodloosejet_cj_l]")
          .Define("goodloosejet_eta_bj_l","goodloosejet_eta[goodloosejet_bj_l]")
          )

    histo2D[ 0][x] = dfcat.Histo2D(("histo2d_{0}_{1}".format( 0,x),"histo2d_{0}_{1}".format( 0,x),len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins),"goodloosejet_eta_lf"  ,"goodloosejet_pt_lf"  ,"weightForBTag")
    histo2D[ 1][x] = dfcat.Histo2D(("histo2d_{0}_{1}".format( 1,x),"histo2d_{0}_{1}".format( 1,x),len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins),"goodloosejet_eta_cj"  ,"goodloosejet_pt_cj"  ,"weightForBTag")
    histo2D[ 2][x] = dfcat.Histo2D(("histo2d_{0}_{1}".format( 2,x),"histo2d_{0}_{1}".format( 2,x),len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins),"goodloosejet_eta_bj"  ,"goodloosejet_pt_bj"  ,"weightForBTag")
    histo2D[ 3][x] = dfcat.Histo2D(("histo2d_{0}_{1}".format( 3,x),"histo2d_{0}_{1}".format( 3,x),len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins),"goodloosejet_eta_lf_t","goodloosejet_pt_lf_t","weightForBTag")
    histo2D[ 4][x] = dfcat.Histo2D(("histo2d_{0}_{1}".format( 4,x),"histo2d_{0}_{1}".format( 4,x),len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins),"goodloosejet_eta_cj_t","goodloosejet_pt_cj_t","weightForBTag")
    histo2D[ 5][x] = dfcat.Histo2D(("histo2d_{0}_{1}".format( 5,x),"histo2d_{0}_{1}".format( 5,x),len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins),"goodloosejet_eta_bj_t","goodloosejet_pt_bj_t","weightForBTag")
    histo2D[ 6][x] = dfcat.Histo2D(("histo2d_{0}_{1}".format( 6,x),"histo2d_{0}_{1}".format( 6,x),len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins),"goodloosejet_eta_lf_m","goodloosejet_pt_lf_m","weightForBTag")
    histo2D[ 7][x] = dfcat.Histo2D(("histo2d_{0}_{1}".format( 7,x),"histo2d_{0}_{1}".format( 7,x),len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins),"goodloosejet_eta_cj_m","goodloosejet_pt_cj_m","weightForBTag")
    histo2D[ 8][x] = dfcat.Histo2D(("histo2d_{0}_{1}".format( 8,x),"histo2d_{0}_{1}".format( 8,x),len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins),"goodloosejet_eta_bj_m","goodloosejet_pt_bj_m","weightForBTag")
    histo2D[ 9][x] = dfcat.Histo2D(("histo2d_{0}_{1}".format( 9,x),"histo2d_{0}_{1}".format( 9,x),len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins),"goodloosejet_eta_lf_l","goodloosejet_pt_lf_l","weightForBTag")
    histo2D[10][x] = dfcat.Histo2D(("histo2d_{0}_{1}".format(10,x),"histo2d_{0}_{1}".format(10,x),len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins),"goodloosejet_eta_cj_l","goodloosejet_pt_cj_l","weightForBTag")
    histo2D[11][x] = dfcat.Histo2D(("histo2d_{0}_{1}".format(11,x),"histo2d_{0}_{1}".format(11,x),len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins),"goodloosejet_eta_bj_l","goodloosejet_pt_bj_l","weightForBTag")

    histo[ 8][x] = (dfcat.Filter("Sum(fake_mu)==2")
                         .Define("mll", "Minv2(fake_Muon_pt[0], fake_Muon_eta[0], fake_Muon_phi[0], fake_Muon_mass[0],fake_Muon_pt[1], fake_Muon_eta[1], fake_Muon_phi[1], fake_Muon_mass[1]).first")
                         .Histo1D(("histo_{0}_{1}".format(8,x), "histo_{0}_{1}".format(8,x), 100, 10, 110), "mll","weight")
                         )

    histo[ 9][x] = (dfcat.Filter("Sum(fake_el)==2")
                         .Define("mll", "Minv2(fake_Electron_pt[0], fake_Electron_eta[0], fake_Electron_phi[0], fake_Electron_mass[0],fake_Electron_pt[1], fake_Electron_eta[1], fake_Electron_phi[1], fake_Electron_mass[1]).first")
                         .Histo1D(("histo_{0}_{1}".format(9,x), "histo_{0}_{1}".format(9,x), 100, 10, 110), "mll","weight")
                         )

    histo[10][x] = dfgen.Histo1D(("histo_{0}_{1}".format(10,x), "histo_{0}_{1}".format(10,x), 60, 91.1876-15, 91.1876+15), "Zmass","weight")
    histo[11][x] = dfgen.Histo1D(("histo_{0}_{1}".format(11,x), "histo_{0}_{1}".format(11,x), 50, 0., 100.), "Zpt","weight")
    histo[12][x] = dfgen.Histo1D(("histo_{0}_{1}".format(12,x), "histo_{0}_{1}".format(12,x), 50, 0., 5.0), "Zrap","weight")
    histo2D[100][x] = dfgen.Histo2D(("histo2d_{0}_{1}".format(100,x),"histo2d_{0}_{1}".format(100,x),10, 0, 5, 40, 0, 100),"Zrap","Zpt","weight")

    dfgen = (dfgen
          .Define("genLep", "(abs(GenDressedLepton_pdgId) == 11 || abs(GenDressedLepton_pdgId) == 13)")
          .Filter("Sum(genLep) == 2","genLep == 2")
          .Define("filter_GenDressedLepton_pt", "GenDressedLepton_pt[genLep]")
          .Define("filter_GenDressedLepton_eta", "GenDressedLepton_eta[genLep]")
            )

    dfgen = dfgen.Filter("abs(filter_GenDressedLepton_eta[0]) < 2.5 && abs(filter_GenDressedLepton_eta[1]) < 2.5","eta requirements")
    dfgen = dfgen.Filter("filter_GenDressedLepton_pt[0] > 10 && filter_GenDressedLepton_pt[1] > 10","Minimal pt requirements")

    histo[13][x] = dfgen.Histo1D(("histo_{0}_{1}".format(13,x), "histo_{0}_{1}".format(13,x), 50, 0., 100.), "Zpt","weight")
    histo[14][x] = dfgen.Histo1D(("histo_{0}_{1}".format(14,x), "histo_{0}_{1}".format(14,x), 50, 0., 5.0), "Zrap","weight")

    dfgen = dfgen.Filter("filter_GenDressedLepton_pt[0] > 25 && filter_GenDressedLepton_pt[1] > 25","Tighter pt requirements")

    histo[15][x] = dfgen.Histo1D(("histo_{0}_{1}".format(15,x), "histo_{0}_{1}".format(15,x), 50, 0., 100.), "Zpt","weight")
    histo[16][x] = dfgen.Histo1D(("histo_{0}_{1}".format(16,x), "histo_{0}_{1}".format(16,x), 50, 0., 5.0), "Zrap","weight")
    histo2D[101][x] = dfgen.Histo2D(("histo2d_{0}_{1}".format(101,x),"histo2d_{0}_{1}".format(100,x),10, 0, 5, 40, 0, 101),"Zrap","Zpt","weight")

    histo[17][x] = dfww.Histo1D(("histo_{0}_{1}".format(17,x), "histo_{0}_{1}".format(17,x),3,-0.5,2.5), "ngood_jets","weight")

    dfww = dfww.Filter("nbtag_goodbtag_Jet_bjet == 0", "No b-jets")
    histo[18][x] = dfww.Histo1D(("histo_{0}_{1}".format(18,x), "histo_{0}_{1}".format(18,x),3,-0.5,2.5), "ngood_jets","weight")

    dfww0j = dfww.Filter("ngood_jets == 0")
    dfww1j = dfww.Filter("ngood_jets == 1")
    dfww2j = dfww.Filter("ngood_jets == 2")
    dfww3j = dfww.Filter("ngood_jets >= 3")
    
    BinXF = 3
    minXF = -0.5
    maxXF = 2.5

    histo[140][x] = dfww  .Histo1D(("histo_{0}_{1}".format(140,x), "histo_{0}_{1}".format(140,x),BinXF,minXF,maxXF),"theGenCat","weight")
    histo[141][x] = dfww  .Histo1D(("histo_{0}_{1}".format(141,x), "histo_{0}_{1}".format(141,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight0")
    histo[142][x] = dfww  .Histo1D(("histo_{0}_{1}".format(142,x), "histo_{0}_{1}".format(142,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight1")
    histo[143][x] = dfww  .Histo1D(("histo_{0}_{1}".format(143,x), "histo_{0}_{1}".format(143,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight2")
    histo[144][x] = dfww  .Histo1D(("histo_{0}_{1}".format(144,x), "histo_{0}_{1}".format(144,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight3")
    histo[145][x] = dfww  .Histo1D(("histo_{0}_{1}".format(145,x), "histo_{0}_{1}".format(145,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight4")    

    histo[146][x] = dfww0j.Histo1D(("histo_{0}_{1}".format(146,x), "histo_{0}_{1}".format(146,x),BinXF,minXF,maxXF),"theGenCat","weight")
    histo[147][x] = dfww0j.Histo1D(("histo_{0}_{1}".format(147,x), "histo_{0}_{1}".format(147,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight0")
    histo[148][x] = dfww0j.Histo1D(("histo_{0}_{1}".format(148,x), "histo_{0}_{1}".format(148,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight1")
    histo[149][x] = dfww0j.Histo1D(("histo_{0}_{1}".format(149,x), "histo_{0}_{1}".format(149,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight2")
    histo[150][x] = dfww0j.Histo1D(("histo_{0}_{1}".format(150,x), "histo_{0}_{1}".format(150,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight3")
    histo[151][x] = dfww0j.Histo1D(("histo_{0}_{1}".format(151,x), "histo_{0}_{1}".format(151,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight4")

    histo[152][x] = dfww1j.Histo1D(("histo_{0}_{1}".format(152,x), "histo_{0}_{1}".format(152,x),BinXF,minXF,maxXF),"theGenCat","weight")
    histo[153][x] = dfww1j.Histo1D(("histo_{0}_{1}".format(153,x), "histo_{0}_{1}".format(153,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight0")
    histo[154][x] = dfww1j.Histo1D(("histo_{0}_{1}".format(154,x), "histo_{0}_{1}".format(154,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight1")
    histo[155][x] = dfww1j.Histo1D(("histo_{0}_{1}".format(155,x), "histo_{0}_{1}".format(155,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight2")
    histo[156][x] = dfww1j.Histo1D(("histo_{0}_{1}".format(156,x), "histo_{0}_{1}".format(156,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight3")
    histo[157][x] = dfww1j.Histo1D(("histo_{0}_{1}".format(157,x), "histo_{0}_{1}".format(157,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight4")

    histo[158][x] = dfww2j.Histo1D(("histo_{0}_{1}".format(158,x), "histo_{0}_{1}".format(158,x),BinXF,minXF,maxXF),"theGenCat","weight")
    histo[159][x] = dfww2j.Histo1D(("histo_{0}_{1}".format(159,x), "histo_{0}_{1}".format(159,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight0")
    histo[160][x] = dfww2j.Histo1D(("histo_{0}_{1}".format(160,x), "histo_{0}_{1}".format(160,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight1")
    histo[161][x] = dfww2j.Histo1D(("histo_{0}_{1}".format(161,x), "histo_{0}_{1}".format(161,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight2")
    histo[162][x] = dfww2j.Histo1D(("histo_{0}_{1}".format(162,x), "histo_{0}_{1}".format(162,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight3")
    histo[163][x] = dfww2j.Histo1D(("histo_{0}_{1}".format(163,x), "histo_{0}_{1}".format(163,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight4")

    histo[164][x] = dfww3j.Histo1D(("histo_{0}_{1}".format(164,x), "histo_{0}_{1}".format(164,x),BinXF,minXF,maxXF),"theGenCat","weight")
    histo[165][x] = dfww3j.Histo1D(("histo_{0}_{1}".format(165,x), "histo_{0}_{1}".format(165,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight0")
    histo[166][x] = dfww3j.Histo1D(("histo_{0}_{1}".format(166,x), "histo_{0}_{1}".format(166,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight1")
    histo[167][x] = dfww3j.Histo1D(("histo_{0}_{1}".format(167,x), "histo_{0}_{1}".format(167,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight2")
    histo[168][x] = dfww3j.Histo1D(("histo_{0}_{1}".format(168,x), "histo_{0}_{1}".format(168,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight3")
    histo[169][x] = dfww3j.Histo1D(("histo_{0}_{1}".format(169,x), "histo_{0}_{1}".format(169,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight4")

    histo[19][x] = dfLLgen.Histo1D(("histo_{0}_{1}".format(19,x), "histo_{0}_{1}".format(19,x), 100, 10, 110), "mllGen","weight")

    startF = 0
    histo[startF+20][x] = dfwwgen.Histo1D(("histo_{0}_{1}".format(startF+20,x), "histo_{0}_{1}".format(startF+20,x),BinXF,minXF,maxXF),"theGenCat","weight")
    for nv in range(1,114):
        histo[startF+20+nv][x] = makeFinalVariable(dfwwgen,"theGenCat",theCat,startF+20,x,BinXF,minXF,maxXF,nv)

    histo[134][x] = dfwwgen.Histo1D(("histo_{0}_{1}".format(134,x), "histo_{0}_{1}".format(134,x),BinXF,minXF,maxXF),"theGenCat","weight")
    histo[135][x] = dfwwgen.Histo1D(("histo_{0}_{1}".format(135,x), "histo_{0}_{1}".format(135,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight0")
    histo[136][x] = dfwwgen.Histo1D(("histo_{0}_{1}".format(136,x), "histo_{0}_{1}".format(136,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight1")
    histo[137][x] = dfwwgen.Histo1D(("histo_{0}_{1}".format(137,x), "histo_{0}_{1}".format(137,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight2")
    histo[138][x] = dfwwgen.Histo1D(("histo_{0}_{1}".format(138,x), "histo_{0}_{1}".format(138,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight3")
    histo[139][x] = dfwwgen.Histo1D(("histo_{0}_{1}".format(139,x), "histo_{0}_{1}".format(139,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight4")

    #branches = ["nElectron", "nPhoton", "nMuon", "Photon_pt", "Muon_pt", "PuppiMET_pt", "nbtag"]
    #dfcat.Snapshot("Events", "test.root", branches)

    report0 = dfcat.Report()
    report1 = dfgen.Report()
    report2 = dfLLgen.Report()
    report3 = dfww.Report()
    report4 = dfwwgen.Report()
    print("---------------- SUMMARY -------------")
    report0.Print()
    report1.Print()
    report2.Print()
    report3.Print()
    report4.Print()

    myfile = ROOT.TFile("fillhisto_puAnalysis_sample{0}_year{1}_job{2}.root".format(count,year,whichJob),'RECREATE')
    for nc in range(nCat):
        for j in range(nHisto):
            if(histo[j][nc] == 0): continue
            if(j==0): histo[j][nc].SetNameTitle("pileup","pileup")

            histo[j][nc].SetBinContent(histo[j][nc].GetNbinsX(),histo[j][nc].GetBinContent(histo[j][nc].GetNbinsX())+histo[j][nc].GetBinContent(histo[j][nc].GetNbinsX()+1))
            histo[j][nc].SetBinError  (histo[j][nc].GetNbinsX(),pow(pow(histo[j][nc].GetBinError(histo[j][nc].GetNbinsX()),2)+pow(histo[j][nc].GetBinError(histo[j][nc].GetNbinsX()+1),2),0.5))
            histo[j][nc].SetBinContent(histo[j][nc].GetNbinsX()+1,0.0)
            histo[j][nc].SetBinError  (histo[j][nc].GetNbinsX()+1,0.0)

            histo[j][nc].Write()

        for j in range(nHisto):
            if(histo2D[j][nc] == 0): continue

            for i in range(histo2D[j][nc].GetNbinsX()):
               histo2D[j][nc].SetBinContent(i+1,histo2D[j][nc].GetNbinsY(),histo2D[j][nc].GetBinContent(i+1,histo2D[j][nc].GetNbinsY())+histo2D[j][nc].GetBinContent(i+1,histo2D[j][nc].GetNbinsY()+1))
               histo2D[j][nc].SetBinError  (i+1,histo2D[j][nc].GetNbinsY(),pow(pow(histo2D[j][nc].GetBinError(i+1,histo2D[j][nc].GetNbinsY()),2)+pow(histo2D[j][nc].GetBinError(i+1,histo2D[j][nc].GetNbinsY()+1),2),0.5))
               histo2D[j][nc].SetBinContent(i+1,histo2D[j][nc].GetNbinsY()+1,0.0)
               histo2D[j][nc].SetBinError  (i+1,histo2D[j][nc].GetNbinsY()+1,0.0)

            for i in range(histo2D[j][nc].GetNbinsY()):
               histo2D[j][nc].SetBinContent(histo2D[j][nc].GetNbinsX(),i+1,histo2D[j][nc].GetBinContent(histo2D[j][nc].GetNbinsX(),i+1)+histo2D[j][nc].GetBinContent(histo2D[j][nc].GetNbinsX()+1,i+1))
               histo2D[j][nc].SetBinError  (histo2D[j][nc].GetNbinsX(),i+1,pow(pow(histo2D[j][nc].GetBinError(histo2D[j][nc].GetNbinsX(),i+1),2)+pow(histo2D[j][nc].GetBinError(histo2D[j][nc].GetNbinsX()+1,i+1),2),0.5))
               histo2D[j][nc].SetBinContent(histo2D[j][nc].GetNbinsX()+1,i+1,0.0)
               histo2D[j][nc].SetBinError  (histo2D[j][nc].GetNbinsX()+1,i+1,0.0)

            histo2D[j][nc].Write()

    myfile.Close()

    print("ending {0} / {1} / {2} / {3} / {4} / {5}".format(count,category,weight,year,PDType,isData))

def readMCSample(sampleNOW, year, PDType, skimType, whichJob, group, histo_wwpt, puWeights):

    files = getMClist(sampleNOW, skimType)
    print("Total files: {0}".format(len(files)))

    df = ROOT.RDataFrame("Events", files)

    genEventSumWeight = 0
    genEventSumNoWeight = 0
    nTheoryReplicas = [103, 9, 4]
    genEventSumLHEScaleWeight = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    genEventSumPSWeight = [0, 0, 0, 0, 0]

    dfRuns = ROOT.RDataFrame("Runs", files)
    genEventSumWeight = dfRuns.Sum("genEventSumw").GetValue()
    genEventSumNoWeight = dfRuns.Sum("genEventCount").GetValue()
    try:
        if(dfRuns.Min("nLHEPdfSumw").GetValue() < nTheoryReplicas[0]):
            nTheoryReplicas[0] = int(dfRuns.Min("nLHEPdfSumw").GetValue())
    except Exception as e:
        nTheoryReplicas[0] = 0
    for n in range(9):
        try:
            if(dfRuns.Min("nLHEScaleSumw").GetValue() > n):
                dfRuns = dfRuns.Define("genEventSumLHEScaleWeight{0}".format(n),"LHEScaleSumw[{0}]".format(n))
                genEventSumLHEScaleWeight[n] = dfRuns.Sum("genEventSumLHEScaleWeight{0}".format(n)).GetValue()
            else:
                genEventSumLHEScaleWeight[n] = dfRuns.Count().GetValue()
                nTheoryReplicas[1] = int(dfRuns.Min("nLHEScaleSumw").GetValue())
        except Exception as e:
            genEventSumLHEScaleWeight[n] = dfRuns.Count().GetValue()
            nTheoryReplicas[1] = n
            print("Problem with LHEScaleWeights {0}".format(e))
    for n in range(4):
        try:
            if(dfRuns.Min("nPSSumw").GetValue() > n):
                dfRuns = dfRuns.Define("genEventSumPSWeight{0}".format(n),"PSSumw[{0}]".format(n))
                genEventSumPSWeight[n] = dfRuns.Sum("genEventSumPSWeight{0}".format(n)).GetValue()
            else:
                genEventSumPSWeight[n] = dfRuns.Count().GetValue()
                nTheoryReplicas[2] = int(dfRuns.Min("nPSSumw").GetValue())
        except Exception as e:
            genEventSumPSWeight[n] = dfRuns.Count().GetValue()
            nTheoryReplicas[2] = n
            print("Problem with PSWeights {0}".format(e))
    genEventSumPSWeight[4] = dfRuns.Count().GetValue()
    runGetEntries = dfRuns.Count().GetValue()

    genEventSumLHEScaleRenorm = [1, 1, 1, 1, 1, 1]
    genEventSumPSRenorm = [1, 1, 1, 1]
    if(0):
        genEventSumLHEScaleRenorm[0] = genEventSumLHEScaleWeight[0] / genEventSumLHEScaleWeight[4]
        genEventSumLHEScaleRenorm[1] = genEventSumLHEScaleWeight[1] / genEventSumLHEScaleWeight[4]
        genEventSumLHEScaleRenorm[2] = genEventSumLHEScaleWeight[3] / genEventSumLHEScaleWeight[4]
        genEventSumLHEScaleRenorm[3] = genEventSumLHEScaleWeight[5] / genEventSumLHEScaleWeight[4]
        genEventSumLHEScaleRenorm[4] = genEventSumLHEScaleWeight[7] / genEventSumLHEScaleWeight[4]
        genEventSumLHEScaleRenorm[5] = genEventSumLHEScaleWeight[8] / genEventSumLHEScaleWeight[4]
        for n in range(4):
            genEventSumPSRenorm[n] = genEventSumPSWeight[n] / genEventSumPSWeight[4]
    print("genEventSumLHEScaleRenorm: ",genEventSumLHEScaleRenorm)
    print("genEventSumPSRenorm: ",genEventSumPSRenorm)

    weight = (SwitchSample(sampleNOW, skimType)[1] / genEventSumWeight)*getLumi(year)
    weightApprox = (SwitchSample(sampleNOW, skimType)[1] / genEventSumNoWeight)*getLumi(year)

    if(whichJob != -1):
        groupedFile = groupFiles(files, group)
        files = groupedFile[whichJob]
        if(len(files) == 0):
            print("no files in job/group: {0} / {1}".format(whichJob, group))
            return 0
        print("Used files: {0}".format(len(files)))

    nevents = df.Count().GetValue()

    print("genEventSum({0}): {1} / Events(total/ntuple): {2} / {3}".format(runGetEntries,genEventSumWeight,genEventSumNoWeight,nevents))
    print("WeightExact/Approx %f / %f / Cross section: %f" %(weight, weightApprox, SwitchSample(sampleNOW, skimType)[1]))

    analysis(df, sampleNOW, SwitchSample(sampleNOW,skimType)[2], weight, year, PDType, "false",whichJob,histo_wwpt,puWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm)

if __name__ == "__main__":

    group = 10

    year = 2022
    process = 399
    skimType = "2l"
    whichJob = -1

    valid = ['year=', "process=", 'whichJob=', 'help']
    usage  =  "Usage: ana.py --year=<{0}>\n".format(year)
    usage +=  "              --process=<{0}>\n".format(process)
    usage +=  "              --whichJob=<{0}>".format(whichJob)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", valid)
    except getopt.GetoptError as ex:
        print(usage)
        print(str(ex))
        sys.exit(1)

    for opt, arg in opts:
        if opt == "--help":
            print(usage)
            sys.exit(1)
        if opt == "--year":
            year = int(arg)
        if opt == "--process":
            process = int(arg)
        if opt == "--whichJob":
            whichJob = int(arg)

    puWeights = []
    puPath = "data/puWeights_UL_{0}.root".format(year)
    fPuFile = ROOT.TFile(puPath)
    puWeights.append(fPuFile.Get("puWeights"))
    puWeights.append(fPuFile.Get("puWeightsUp"))
    puWeights.append(fPuFile.Get("puWeightsDown"))
    for x in range(3):
        puWeights[x].SetDirectory(0)
    fPuFile.Close()

    histo_wwpt = []
    fPtwwWeightPath = ROOT.TFile("data/MyRatioWWpTHistogramAll.root")
    histo_wwpt.append(fPtwwWeightPath.Get("wwpt"))
    histo_wwpt.append(fPtwwWeightPath.Get("wwpt_scaleup"))
    histo_wwpt.append(fPtwwWeightPath.Get("wwpt_scaledown"))
    histo_wwpt.append(fPtwwWeightPath.Get("wwpt_resumup"))
    histo_wwpt.append(fPtwwWeightPath.Get("wwpt_resumdown"))
    for x in range(5):
        histo_wwpt[x].SetDirectory(0)
    fPtwwWeightPath.Close()

    try:
        readMCSample(process,year,"All",skimType,whichJob,group,histo_wwpt,puWeights)
    except Exception as e:
        print("FAILED {0}".format(e))
