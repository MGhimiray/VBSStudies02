import ROOT
import os, sys, getopt, json
from array import array

ROOT.ROOT.EnableImplicitMT(10)
from utilsCategory import plotCategory
from utilsAna import getMClist, getDATAlist, getTriggerFromJson, getLumi
from utilsAna import SwitchSample
from utilsSelection import selectionGenLepJet, selectionTheoryWeigths, makeFinalVariable

isRun3Sel = False

def analysis(df,count,category,weight,year,PDType,nSel,isData,histo_wwpt,ewkCorrWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm):

    xPtBins = array('d', [20,25,30,35,40,50,60,80,100,150,250,500,1000])
    xEtaBins = array('d', [0.0,0.3,0.6,0.9,1.2,1.5,1.8,2.1,2.5])

    print("starting {0} / {1} / {2} / {3} / {4} / {5} / {6}".format(count,category,weight,year,PDType,nSel,isData))

    theCat = category
    if(theCat > 100): theCat = plotCategory("kPlotData")

    nCat, nHisto = plotCategory("kPlotCategories"), 1200
    histo   = [[0 for x in range(nCat)] for y in range(nHisto)]
    histo2D = [[0 for y in range(nCat)] for x in range(nHisto)]

    ROOT.initHisto1D(histo_wwpt[0],3)
    ROOT.initHisto1D(histo_wwpt[1],4)
    ROOT.initHisto1D(histo_wwpt[2],5)
    ROOT.initHisto1D(histo_wwpt[3],6)
    ROOT.initHisto1D(histo_wwpt[4],7)
    ROOT.initHisto1D(ewkCorrWeights[0],10)
    ROOT.initHisto1D(ewkCorrWeights[1],11)
    ROOT.initHisto1D(ewkCorrWeights[2],12)
    ROOT.initHisto1D(ewkCorrWeights[3],13)

    ROOT.initJSONSFs(year)

    jetEtaCut = 2.5
    ptlCut = 20
    if(nSel == "vbs"):
        print("vbs selection")
        jetEtaCut = 4.7
        ptlCut = 15.0

    df = selectionGenLepJet(df,ptlCut,30,jetEtaCut)

    dfcat = (df.Define("PDType","\"{0}\"".format(PDType))
               .Define("weightForBTag","1.0f")
               .Define("mjjGen", "compute_vbs_gen_variables(0,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass)")
               .Define("GenJet_bHadron","GenJet_pt > 20 && GenJet_hadronFlavour == 5")
               .Define("nGenJet_bHadron","Sum(GenJet_bHadron)")
               .Define("GenJet_bParton","GenJet_pt > 20 && abs(GenJet_partonFlavour) == 5")
               .Define("nGenJet_bParton","Sum(GenJet_bParton)")
               .Define("kPlotEWKWZ", "{0}".format(plotCategory("kPlotEWKWZ")))
               .Filter("{0} != kPlotEWKWZ || nGenJet_bParton == 0".format(theCat), "EWKWZ requirement")
               .Define("weightEWKCorr", "compute_EWKCorr(0,PDType,mjjGen)")
               .Define("weight","{0}*genWeight*weightEWKCorr".format(weight/getLumi(year)))
               .Filter("weight != 0","good weight")
               .Define("weightNoEWKCorr","{0}*genWeight".format(weight/getLumi(year)))
               )

    dfcat = selectionTheoryWeigths(dfcat,weight,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm)

    x = 0

    BinXF = 1
    minXF = -0.5
    maxXF = 0.5

    startF = 140
    for nv in range(0,114):
        histo[startF+0+nv][x] = makeFinalVariable(dfcat,"weightForBTag",theCat,startF+0,x,BinXF,minXF,maxXF,nv)

    dfzllgen = (dfcat
          .Define("gen_z", "GenPart_pdgId == 23 && GenPart_status == 62")
          .Filter("Sum(gen_z) >= 1","nZ >= 1")
          .Filter("Sum(gen_z) == 1","nZ == 1")
          .Define("Zpt", "GenPart_pt[gen_z]")
          .Define("Zeta", "GenPart_eta[gen_z]")
          .Define("Zphi", "abs(GenPart_phi[gen_z])")
          .Define("Zmass", "GenPart_mass[gen_z]")
         #.Filter("abs(Zmass[0]-91.1876) < 15","Zmass cut")
          .Filter("Zmass[0] > 60 && Zmass[0] < 120","Zmass cut")
          .Define("Zrap", "abs(makeRapidity(Zpt[0],Zeta[0],Zphi[0],Zmass[0]))")
            )

    dfwwxgen = dfcat.Filter("ngood_GenDressedLeptons >= 2", "ngood_GenDressedLeptons >= 2")
    if(isRun3Sel == True):
        dfwwxgen = (dfwwxgen
                        .Define("theGenCat0", "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,0)-1.0".format(0))
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

    else:
        dfwwxgen = (dfwwxgen
                        .Define("theGenCat0", "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,0)-1.0".format(0))
                        .Define("theGenCat1", "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,1)-1.0".format(0))
                        .Define("theGenCat",  "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,2)-1.0".format(0))
                        .Filter("theGenCat0 >= 0","theGenCat0 >= 0")
                        .Filter("theGenCat1 >= 0","theGenCat1 >= 0")
                        .Filter("theGenCat  >= 0","theGenCat  >= 0")
                        .Define("theNNLOWeight0", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,0)")
                        .Define("theNNLOWeight1", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,1)")
                        .Define("theNNLOWeight2", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,2)")
                        .Define("theNNLOWeight3", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,3)")
                        .Define("theNNLOWeight4", "weight*compute_ptww_weight(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi,4)")
                        )

    # Z->ll + X study
    histo[10][x] = dfzllgen.Histo1D(("histo_{0}_{1}".format(10,x), "histo_{0}_{1}".format(10,x), 60, 91.1876-15, 91.1876+15), "Zmass","weight")
    histo[11][x] = dfzllgen.Histo1D(("histo_{0}_{1}".format(11,x), "histo_{0}_{1}".format(11,x), 40,  0, 200), "Zpt","weight")
    histo[12][x] = dfzllgen.Histo1D(("histo_{0}_{1}".format(12,x), "histo_{0}_{1}".format(12,x), 50, 0., 5.0), "Zrap","weight")
    histo2D[100][x] = dfzllgen.Histo2D(("histo2d_{0}_{1}".format(100,x),"histo2d_{0}_{1}".format(100,x),10, 0, 5, 40, 0, 100),"Zrap","Zpt","weight")

    startF = 260
    for nv in range(0,114):
        histo[startF+0+nv][x] = makeFinalVariable(dfzllgen,"weightForBTag",theCat,startF+0,x,BinXF,minXF,maxXF,nv)

    dfzllgen = (dfzllgen
          .Define("genLep", "(abs(GenDressedLepton_pdgId) == 11 || abs(GenDressedLepton_pdgId) == 13)")
          .Filter("Sum(genLep) >= 2","genLep >= 2")
          .Define("filter_GenDressedLepton_pt", "GenDressedLepton_pt[genLep]")
          .Define("filter_GenDressedLepton_eta", "GenDressedLepton_eta[genLep]")
            )

    dfzllgen = dfzllgen.Filter("abs(filter_GenDressedLepton_eta[0]) < 2.5 && abs(filter_GenDressedLepton_eta[1]) < 2.5","eta requirements")
    dfzllgen = dfzllgen.Filter("filter_GenDressedLepton_pt[0] > 10 && filter_GenDressedLepton_pt[1] > 10","Minimal pt requirements")

    histo[13][x] = dfzllgen.Histo1D(("histo_{0}_{1}".format(13,x), "histo_{0}_{1}".format(13,x), 40,  0, 200), "Zpt","weight")
    histo[14][x] = dfzllgen.Histo1D(("histo_{0}_{1}".format(14,x), "histo_{0}_{1}".format(14,x), 50, 0., 5.0), "Zrap","weight")

    dfzllgen = dfzllgen.Filter("filter_GenDressedLepton_pt[0] > 25 && filter_GenDressedLepton_pt[1] > 20","Tighter pt requirements")

    histo[15][x] = dfzllgen.Histo1D(("histo_{0}_{1}".format(15,x), "histo_{0}_{1}".format(15,x), 40,  0, 200), "Zpt","weight")
    histo[16][x] = dfzllgen.Histo1D(("histo_{0}_{1}".format(16,x), "histo_{0}_{1}".format(16,x), 50, 0., 5.0), "Zrap","weight")
    histo[17][x] = dfzllgen.Filter("ngood_GenJets == 0").Histo1D(("histo_{0}_{1}".format(17,x), "histo_{0}_{1}".format(17,x), 40,  0, 200), "Zpt","weight")
    histo[18][x] = dfzllgen.Filter("ngood_GenJets == 1").Histo1D(("histo_{0}_{1}".format(18,x), "histo_{0}_{1}".format(18,x), 40,  0, 200), "Zpt","weight")
    histo[19][x] = dfzllgen.Filter("ngood_GenJets >= 2").Histo1D(("histo_{0}_{1}".format(19,x), "histo_{0}_{1}".format(19,x), 40,  0, 200), "Zpt","weight")
    histo2D[101][x] = dfzllgen.Histo2D(("histo2d_{0}_{1}".format(101,x),"histo2d_{0}_{1}".format(100,x),10, 0, 5, 40, 0, 101),"Zrap","Zpt","weight")

    df3lgen = (dfzllgen.Filter("Sum(genLep) == 3","genLep == 3")
                       .Filter("abs(filter_GenDressedLepton_eta[2]) < 2.5 && filter_GenDressedLepton_pt[2] > 10","3rd lepton requirement")
                       )

    histo[380][x] = df3lgen                               .Histo1D(("histo_{0}_{1}".format(380,x), "histo_{0}_{1}".format(380,x), 5, -0.5, 4.5), "nGenJet_bHadron","weight")
    histo[381][x] = df3lgen                               .Histo1D(("histo_{0}_{1}".format(381,x), "histo_{0}_{1}".format(381,x), 5, -0.5, 4.5), "nGenJet_bParton","weight")
    histo[382][x] = df3lgen.Filter("nGenJet_bParton == 0").Histo1D(("histo_{0}_{1}".format(382,x), "histo_{0}_{1}".format(382,x), 5, -0.5, 4.5), "nGenJet_bHadron","weight")
    histo[383][x] = df3lgen.Filter("nGenJet_bHadron == 0").Histo1D(("histo_{0}_{1}".format(383,x), "histo_{0}_{1}".format(383,x), 5, -0.5, 4.5), "nGenJet_bParton","weight")
    histo[384][x] = df3lgen.Filter("nGenJet_bParton >= 1").Histo1D(("histo_{0}_{1}".format(384,x), "histo_{0}_{1}".format(384,x), 5, -0.5, 4.5), "nGenJet_bHadron","weight")
    histo[385][x] = df3lgen.Filter("nGenJet_bHadron >= 1").Histo1D(("histo_{0}_{1}".format(385,x), "histo_{0}_{1}".format(385,x), 5, -0.5, 4.5), "nGenJet_bParton","weight")

    dfwwxgen = (dfwwxgen.Define("ptl1Gen", "good_GenDressedLepton_pt[0]")
                        .Define("ptl2Gen", "good_GenDressedLepton_pt[1]")
                        .Define("etal1Gen","good_GenDressedLepton_eta[0]")
                        .Define("etal2Gen","good_GenDressedLepton_eta[1]")
                        .Define("mllGen",  "Minv2(good_GenDressedLepton_pt[0], good_GenDressedLepton_eta[0], good_GenDressedLepton_phi[0], good_GenDressedLepton_mass[0],good_GenDressedLepton_pt[1], good_GenDressedLepton_eta[1], good_GenDressedLepton_phi[1], good_GenDressedLepton_mass[1]).first")
                        .Define("ptllGen", "Minv2(good_GenDressedLepton_pt[0], good_GenDressedLepton_eta[0], good_GenDressedLepton_phi[0], good_GenDressedLepton_mass[0],good_GenDressedLepton_pt[1], good_GenDressedLepton_eta[1], good_GenDressedLepton_phi[1], good_GenDressedLepton_mass[1]).second")
                        .Define("ptvvGen", "compute_gen_ptvv(good_GenDressedLepton_pt,good_GenDressedLepton_phi,GenMET_pt,GenMET_phi)")
                        )

    if(isRun3Sel == True):
        dfwwxgen = (dfwwxgen
                       .Filter("mllGen > 85", "mllGen > 85")
                       )
    else:
        dfwwxgen = (dfwwxgen
                       .Filter("mllGen > 20", "mllGen > 20")
                       .Filter("ptllGen > 30", "ptllGen > 30")
                       .Filter("GenMET_pt > 20", "GenMET_pt > 20")
                       )

    histo[0][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(0,x), "histo_{0}_{1}".format(0,x), 30, 85., 385.), "mllGen","weight")
    histo[1][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(1,x), "histo_{0}_{1}".format(1,x), 30, 0.,  240.), "ptllGen","weight")
    histo[2][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(2,x), "histo_{0}_{1}".format(2,x), 30, 25., 325.), "ptl1Gen","weight")
    histo[3][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(3,x), "histo_{0}_{1}".format(3,x), 30, 20., 220.), "ptl2Gen","weight")
    histo[4][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(4,x), "histo_{0}_{1}".format(4,x), 25, -2.5,  2.5), "etal1Gen","weight")
    histo[5][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(5,x), "histo_{0}_{1}".format(5,x), 25, -2.5,  2.5), "etal2Gen","weight")
    histo[6][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(6,x), "histo_{0}_{1}".format(6,x), 30, 30.,  330.), "good_GenJet_pt","weight")
    histo[7][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(7,x), "histo_{0}_{1}".format(7,x), 25, -2.5,  2.5), "good_GenJet_eta","weight")
    histo[8][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(8,x), "histo_{0}_{1}".format(8,x), 4, -0.5,  3.5), "ngood_GenJets","weight")
    histo[9][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(9,x), "histo_{0}_{1}".format(9,x), 20, 0.0, 200.0), "ptvvGen","weight")

    histo[500][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[0]) == 13")                      .Histo1D(("histo_{0}_{1}".format(500,x), "histo_{0}_{1}".format(500,x), 20, 20., 320.), "ptl1Gen","weight")
    histo[501][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[1]) == 13")                      .Histo1D(("histo_{0}_{1}".format(501,x), "histo_{0}_{1}".format(501,x), 20, 20., 320.), "ptl2Gen","weight")
    histo[502][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[0]) == 11")                      .Histo1D(("histo_{0}_{1}".format(502,x), "histo_{0}_{1}".format(502,x), 20, 20., 320.), "ptl1Gen","weight")
    histo[503][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[1]) == 11")                      .Histo1D(("histo_{0}_{1}".format(503,x), "histo_{0}_{1}".format(503,x), 20, 20., 320.), "ptl2Gen","weight")
    histo[504][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[0]) == 13 && ngood_GenJets == 0").Histo1D(("histo_{0}_{1}".format(504,x), "histo_{0}_{1}".format(504,x), 20, 20., 320.), "ptl1Gen","weight")
    histo[505][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[1]) == 13 && ngood_GenJets == 0").Histo1D(("histo_{0}_{1}".format(505,x), "histo_{0}_{1}".format(505,x), 20, 20., 320.), "ptl2Gen","weight")
    histo[506][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[0]) == 11 && ngood_GenJets == 0").Histo1D(("histo_{0}_{1}".format(506,x), "histo_{0}_{1}".format(506,x), 20, 20., 320.), "ptl1Gen","weight")
    histo[507][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[1]) == 11 && ngood_GenJets == 0").Histo1D(("histo_{0}_{1}".format(507,x), "histo_{0}_{1}".format(507,x), 20, 20., 320.), "ptl2Gen","weight")
    histo[508][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[0]) == 13 && ngood_GenJets == 1").Histo1D(("histo_{0}_{1}".format(508,x), "histo_{0}_{1}".format(508,x), 20, 20., 320.), "ptl1Gen","weight")
    histo[509][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[1]) == 13 && ngood_GenJets == 1").Histo1D(("histo_{0}_{1}".format(509,x), "histo_{0}_{1}".format(509,x), 20, 20., 320.), "ptl2Gen","weight")
    histo[510][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[0]) == 11 && ngood_GenJets == 1").Histo1D(("histo_{0}_{1}".format(510,x), "histo_{0}_{1}".format(510,x), 20, 20., 320.), "ptl1Gen","weight")
    histo[511][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[1]) == 11 && ngood_GenJets == 1").Histo1D(("histo_{0}_{1}".format(511,x), "histo_{0}_{1}".format(511,x), 20, 20., 320.), "ptl2Gen","weight")
    histo[512][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[0]) == 13 && ngood_GenJets >= 2").Histo1D(("histo_{0}_{1}".format(512,x), "histo_{0}_{1}".format(512,x), 20, 20., 320.), "ptl1Gen","weight")
    histo[513][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[1]) == 13 && ngood_GenJets >= 2").Histo1D(("histo_{0}_{1}".format(513,x), "histo_{0}_{1}".format(513,x), 20, 20., 320.), "ptl2Gen","weight")
    histo[514][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[0]) == 11 && ngood_GenJets >= 2").Histo1D(("histo_{0}_{1}".format(514,x), "histo_{0}_{1}".format(514,x), 20, 20., 320.), "ptl1Gen","weight")
    histo[515][x] = dfwwxgen.Filter("abs(GenDressedLepton_pdgId[1]) == 11 && ngood_GenJets >= 2").Histo1D(("histo_{0}_{1}".format(515,x), "histo_{0}_{1}".format(515,x), 20, 20., 320.), "ptl2Gen","weight")
    histo[516][x] = dfwwxgen                                                                     .Histo1D(("histo_{0}_{1}".format(516,x), "histo_{0}_{1}".format(516,x), 20, 85., 485.), "mllGen","weight")
    histo[517][x] = dfwwxgen.Filter("ngood_GenJets == 0")                                        .Histo1D(("histo_{0}_{1}".format(517,x), "histo_{0}_{1}".format(517,x), 20, 85., 485.), "mllGen","weight")
    histo[518][x] = dfwwxgen.Filter("ngood_GenJets == 1")                                        .Histo1D(("histo_{0}_{1}".format(518,x), "histo_{0}_{1}".format(518,x), 20, 85., 485.), "mllGen","weight")
    histo[519][x] = dfwwxgen.Filter("ngood_GenJets >= 2")                                        .Histo1D(("histo_{0}_{1}".format(519,x), "histo_{0}_{1}".format(519,x), 20, 85., 485.), "mllGen","weight")
    histo[520][x] = dfwwxgen                                                                     .Histo1D(("histo_{0}_{1}".format(520,x), "histo_{0}_{1}".format(520,x), 20,  0., 300.), "ptllGen","weight")
    histo[521][x] = dfwwxgen.Filter("ngood_GenJets == 0")                                        .Histo1D(("histo_{0}_{1}".format(521,x), "histo_{0}_{1}".format(521,x), 20,  0., 300.), "ptllGen","weight")
    histo[522][x] = dfwwxgen.Filter("ngood_GenJets == 1")                                        .Histo1D(("histo_{0}_{1}".format(522,x), "histo_{0}_{1}".format(522,x), 20,  0., 300.), "ptllGen","weight")
    histo[523][x] = dfwwxgen.Filter("ngood_GenJets >= 2")                                        .Histo1D(("histo_{0}_{1}".format(523,x), "histo_{0}_{1}".format(523,x), 20,  0., 300.), "ptllGen","weight")

    BinXF = 3
    minXF = -0.5
    maxXF = 2.5

    startF = 20
    for nv in range(0,114):
        histo[startF+nv][x] = makeFinalVariable(dfwwxgen,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,nv)

    histo[134][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(134,x), "histo_{0}_{1}".format(134,x),BinXF,minXF,maxXF),"theGenCat","weight")
    histo[135][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(135,x), "histo_{0}_{1}".format(135,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight0")
    histo[136][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(136,x), "histo_{0}_{1}".format(136,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight1")
    histo[137][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(137,x), "histo_{0}_{1}".format(137,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight2")
    histo[138][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(138,x), "histo_{0}_{1}".format(138,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight3")
    histo[139][x] = dfwwxgen.Histo1D(("histo_{0}_{1}".format(139,x), "histo_{0}_{1}".format(139,x),BinXF,minXF,maxXF),"theGenCat","theNNLOWeight4")

    dfvbswwgen = dfcat.Filter("ngood_GenDressedLeptons >= 2 && ngood_GenJets >=2", "ngood_GenDressedLeptons >= 2 && ngood_GenJets >=2")

    dfvbswzgen = dfcat.Filter("ngood_GenDressedLeptons >= 3", "ngood_GenDressedLeptons >= 3")

    dfvbswwgen = (dfvbswwgen.Define("theSelCat1" , "compute_vbs_gen_category(1,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,1)")
                            .Filter("theSelCat1 > 0", "theSelCat1 > 0")
                            .Define("theSelCat2" , "compute_vbs_gen_category(1,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,2)")
                            .Filter("theSelCat2 > 0", "theSelCat2 > 0")
                            .Define("theSelCat3" , "compute_vbs_gen_category(1,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,3)")
                            .Filter("theSelCat3 > 0", "theSelCat3 > 0")
                            .Define("theSelCat4" , "compute_vbs_gen_category(1,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,4)")
                            .Filter("theSelCat4 > 0", "theSelCat4 > 0")
                            .Define("theSelCat5" , "compute_vbs_gen_category(1,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,5)")
                            .Filter("theSelCat5 > 0", "theSelCat5 > 0")
                            .Define("theGenCat1" , "compute_vbs_gen_category(1,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,5)-1")
                            .Define("theGenCat2" , "compute_vbs_gen_category(2,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,5)-1")
                            .Define("theGenCat3" , "compute_vbs_gen_category(3,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,5)-1")
                            .Define("theGenCat4" , "compute_vbs_gen_category(4,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,5)-1")
                            .Define("theGenCat5" , "compute_vbs_gen_category(5,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,5)-1")
                            )
    dfvbswzgen = (dfvbswzgen.Define("theSelCat1", "compute_vbs_gen_category(1,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,11)")
                            .Filter("theSelCat1 > 0", "theSelCat1 > 0")
                            .Define("theSelCat2", "compute_vbs_gen_category(1,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,12)")
                            .Filter("theSelCat2 > 0", "theSelCat2 > 0")
                            .Define("theSelCat3", "compute_vbs_gen_category(1,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,13)")
                            .Filter("theSelCat3 > 0", "theSelCat3 > 0")
                            .Define("theSelCat4", "compute_vbs_gen_category(1,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,14)")
                            .Filter("theSelCat4 > 0", "theSelCat4 > 0")
                            .Define("theSelCat5", "compute_vbs_gen_category(1,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,15)")
                            .Filter("theSelCat5 > 0", "theSelCat5 > 0")
                            .Define("theGenCat",  "compute_vbs_gen_category(1,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,15)-1")
                            .Define("mll",   "compute_mll_gen_category(0,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass)")
                            .Define("mllSS", "compute_mll_gen_category(1,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass)")
                            .Define("mllZ",  "compute_mll_gen_category(2,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass)")
                            )


    histo[524][x] = dfvbswwgen.Histo1D(("histo_{0}_{1}".format(524,x), "histo_{0}_{1}".format(524,x),4,-0.5, 3.5),"theGenCat1","weightNoEWKCorr")

    histo[525][x] = dfvbswzgen.Histo1D(("histo_{0}_{1}".format(525,x), "histo_{0}_{1}".format(525,x),40,0,160),"mll","weight")
    histo[526][x] = dfvbswzgen.Histo1D(("histo_{0}_{1}".format(526,x), "histo_{0}_{1}".format(526,x),40,0,160),"mllSS","weight")

    dfvbswzgen = dfvbswzgen.Filter("mllZ < 15", "mllZ < 15")

    histo[527][x] = dfvbswzgen.Histo1D(("histo_{0}_{1}".format(527,x), "histo_{0}_{1}".format(527,x),4,-0.5, 3.5),"theGenCat","weightNoEWKCorr")

    BinXF = 4
    minXF = -0.5
    maxXF = 3.5
    startF = 386
    for nv in range(0,114):
        histo[startF+nv][x] = makeFinalVariable(dfvbswzgen,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,nv)

    BinXF = 4
    minXF = -0.5
    maxXF = 3.5
    startF = 530
    for nv in range(0,114):
        histo[startF+nv][x] = makeFinalVariable(dfvbswwgen,"theGenCat1",theCat,startF,x,BinXF,minXF,maxXF,nv)

    BinXF = 4
    minXF = -0.5
    maxXF = 3.5
    startF = 650
    for nv in range(0,114):
        histo[startF+nv][x] = makeFinalVariable(dfvbswwgen,"theGenCat2",theCat,startF,x,BinXF,minXF,maxXF,nv)

    BinXF = 2
    minXF = -0.5
    maxXF = 1.5
    startF = 770
    for nv in range(0,114):
        histo[startF+nv][x] = makeFinalVariable(dfvbswwgen,"theGenCat3",theCat,startF,x,BinXF,minXF,maxXF,nv)

    BinXF = 4
    minXF = -0.5
    maxXF = 3.5
    startF = 890
    for nv in range(0,114):
        histo[startF+nv][x] = makeFinalVariable(dfvbswwgen,"theGenCat4",theCat,startF,x,BinXF,minXF,maxXF,nv)

    BinXF = 4
    minXF = -0.5
    maxXF = 3.5
    startF = 1010
    for nv in range(0,114):
        histo[startF+nv][x] = makeFinalVariable(dfvbswwgen,"theGenCat5",theCat,startF,x,BinXF,minXF,maxXF,nv)

    report0 = dfzllgen.Report()
    report1 = dfwwxgen.Report()
    report2 = dfvbswwgen.Report()
    report3 = dfvbswzgen.Report()
    print("---------------- SUMMARY ZLL -------------")
    report0.Print()
    print("---------------- SUMMARY WW -------------")
    report1.Print()
    print("---------------- SUMMARY VBSWW -------------")
    report2.Print()
    print("---------------- SUMMARY VBSWZ -------------")
    report3.Print()
    
    output_dir = "/mnt/home/mghimiray/VBSStudies/Outputs_VBS/GenXs/"
    os.makedirs(output_dir, exist_ok=True)
    myfile = ROOT.TFile("{0}/fillhisto_genAnalysis_sample{1}_year{2}_job-1.root".format(output_dir,count,year),'RECREATE')
    for nc in range(nCat):
        for j in range(nHisto):
            if(histo[j][nc] == 0): continue

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

def readMCSample(sampleNOW, year, skimType, nSel, histo_wwpt, ewkCorrWeights):

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
            if(hasattr(dfRuns,"nPSSumw") and dfRuns.Min("nPSSumw").GetValue() > n):
                dfRuns = dfRuns.Define("genEventSumPSWeight{0}".format(n),"PSSumw[{0}]".format(n))
                genEventSumPSWeight[n] = dfRuns.Sum("genEventSumPSWeight{0}".format(n)).GetValue()
            elif(hasattr(dfRuns,"nPSSumw")):
                genEventSumPSWeight[n] = dfRuns.Count().GetValue()
                nTheoryReplicas[2] = int(dfRuns.Min("nPSSumw").GetValue())
            else:
                genEventSumPSWeight[n] = 1.0
                nTheoryReplicas[2] = 4
        except Exception as e:
            genEventSumPSWeight[n] = dfRuns.Count().GetValue()
            nTheoryReplicas[2] = n
            print("Problem with PSWeights {0}".format(e))
    genEventSumPSWeight[4] = dfRuns.Count().GetValue()
    runGetEntries = dfRuns.Count().GetValue()

    print("Number of Theory replicas: {0} / {1} / {2}".format(nTheoryReplicas[0],nTheoryReplicas[1],nTheoryReplicas[2]))

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

    nevents = df.Count().GetValue()

    print("genEventSum({0}): {1} / Events(total/ntuple): {2} / {3}".format(runGetEntries,genEventSumWeight,genEventSumNoWeight,nevents))
    print("WeightExact/Approx %f / %f / Cross section: %f" %(weight, weightApprox, SwitchSample(sampleNOW, skimType)[1]))

    PDType = os.path.basename(SwitchSample(sampleNOW, skimType)[0]).split('+')[0]

    analysis(df, sampleNOW, SwitchSample(sampleNOW,skimType)[2], weight, year, PDType, nSel, "false",histo_wwpt,ewkCorrWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm)

if __name__ == "__main__":

    year = 20240
    process = 592
    skimType = "2l"
    nSel = "ww"

    valid = ['year=', "process=", "sel=", 'help']
    usage  =  "Usage: ana.py --year=<{0}>\n".format(year)
    usage +=  "              --process=<{0}>".format(process)
    usage +=  "              --sel=<{0}>".format(nSel)
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
        if opt == "--process":
            process = int(arg)
        if opt == "--sel":
            nSel = str(arg)

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

    ewkCorrWeights = []
    ewkCorrPath = "data/VV_NLO_LO_CMS_mjj.root"
    fewkCorrFile = ROOT.TFile(ewkCorrPath)
    ewkCorrWeights.append(fewkCorrFile.Get("hWW13p6_KF_CMS"))
    ewkCorrWeights.append(fewkCorrFile.Get("hWZ13p0_KF_CMS"))
    ewkCorrWeights.append(fewkCorrFile.Get("hWW13p6_KF_CMSUp"))
    ewkCorrWeights.append(fewkCorrFile.Get("hWZ13p0_KF_CMSUp"))
    for x in range(4):
        ewkCorrWeights[x].SetDirectory(0)
    fewkCorrFile.Close()

    try:
        readMCSample(process,year, skimType, nSel, histo_wwpt, ewkCorrWeights)
    except Exception as e:
        print("FAILED {0}".format(e))