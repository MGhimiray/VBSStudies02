import ROOT
import os, sys, getopt, json

ROOT.ROOT.EnableImplicitMT(10)
from utilsCategory import plotCategory
from utilsAna import getMClist, getDATAlist
from utilsAna import SwitchSample, groupFiles, getTriggerFromJson, getLeptomSelFromJson, getLumi
from utilsSelection import selectionTauVeto, selectionPhoton, selectionJetMet, selection2LVar, selectionTrigger2L, selectionElMu, selectionWeigths, selectionGenLepJet, makeFinalVariable2D
#from utilsAna import loadCorrectionSet

print_info = False
makeDataCards = 1
correctionString = "_correction"
whichVarToFit = 0 # 0 (ww-mll), 1 (ww-ptll), 2 (ww-ptl1), 3 (ww-ptl2), 4 (ww-dphill), 5 (ww-ptmiss), 6 (ztautau-xxx)

# 0 = T, 1 = M, 2 = L
bTagSel = 2
useBTaggingWeights = 1

useFR = 1

altMass = "Def"

jetEtaCut = 2.5

selectionJsonPath = "config/selection.json"

with open(selectionJsonPath) as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

JSON = jsonObject['JSON']

BARRELphotons = jsonObject['BARRELphotons']
ENDCAPphotons = jsonObject['ENDCAPphotons']

VBSSEL = jsonObject['VBSSEL']

#2/4/5/8
muSelChoice = 8
MUOWP = "Medium"

#1/3/4/8
elSelChoice = 8
ELEWP = "DUMMY"
if(elSelChoice == 0):
    ELEWP = "Medium"
elif(elSelChoice == 1):
    ELEWP = "Tight"
elif(elSelChoice == 2):
    ELEWP = "wp80noiso"
elif(elSelChoice == 3):
    ELEWP = "wp80iso"
elif(elSelChoice == 4):
    ELEWP = "wp80iso"
elif(elSelChoice == 5):
    ELEWP = "wp90iso"
elif(elSelChoice == 6):
    ELEWP = "wp80iso"
elif(elSelChoice == 7):
    ELEWP = "wp80iso"
elif(elSelChoice == 8):
    ELEWP = "wp80iso"
elif(elSelChoice == 9):
    ELEWP = "Veto"

def selectionLL(df,year,PDType,isData,TRIGGERMUEG,TRIGGERDMU,TRIGGERSMU,TRIGGERDEL,TRIGGERSEL,count):

    dftag = selectionTrigger2L(df,year,PDType,JSON,isData,TRIGGERSEL,TRIGGERDEL,TRIGGERSMU,TRIGGERDMU,TRIGGERMUEG)

    overallLeptonSel = jsonObject['leptonSel']
    FAKE_MU   = getLeptomSelFromJson(overallLeptonSel, "FAKE_MU",   year)
    TIGHT_MU  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU{0}".format(muSelChoice),  year, 1)

    FAKE_EL   = getLeptomSelFromJson(overallLeptonSel, "FAKE_EL",   year)
    TIGHT_EL  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL{0}".format(elSelChoice),  year, 1)

    dftag = selectionElMu(dftag,year,FAKE_MU,TIGHT_MU,FAKE_EL,TIGHT_EL)

    dftag = (dftag.Filter("nLoose >= 2","At least two loose leptons")
                  .Filter("nLoose == 2","Only two loose leptons")
                  .Filter("nFake == 2","Two fake leptons")

                  .Filter("(Sum(fake_mu) == 1 && Sum(fake_el) == 1) or (Sum(fake_Muon_charge)+Sum(fake_Electron_charge) != 0)","e-mu events")

                  )

    if(useFR == 0):
        dftag = dftag.Filter("nTight == 2","Two tight leptons")

    dftag = selection2LVar  (dftag,year,isData)

    dftag = dftag.Filter("mll{0} > 20".format(altMass),"mll > 20")

    dftag = selectionTauVeto(dftag,year,isData)
    dftag = selectionPhoton (dftag,year,BARRELphotons,ENDCAPphotons)
    dftag = selectionJetMet (dftag,year,bTagSel,isData,count,jetEtaCut)

    return dftag


def analysis(df,count,category,weight,year,PDType,isData,whichJob,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,puWeights,histoTriggerDAEtaPt,histoTriggerMCEtaPt,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3):

    print("starting {0} / {1} / {2} / {3} / {4} / {5} / {6}".format(count,category,weight,year,PDType,isData,whichJob))

    theCat = category
    if(theCat > 100): theCat = plotCategory("kPlotData")

    nCat, nHisto, nHistoMVA, nhistoNonPrompt = plotCategory("kPlotCategories"), 500, 1600, 50
    histo    = [[0 for y in range(nCat)] for x in range(nHisto)]
    histo2D  = [[0 for y in range(nCat)] for x in range(nHistoMVA)]
    histoMVA = [[0 for y in range(nCat)] for x in range(nHistoMVA)]
    histoNonPrompt = [0 for y in range(nhistoNonPrompt)]

    ROOT.initHisto2D(histoFakeEtaPt_mu[0],0)
    ROOT.initHisto2D(histoFakeEtaPt_el[0],1)
    ROOT.initHisto2D(histoLepSFEtaPt_mu,2)
    ROOT.initHisto2D(histoLepSFEtaPt_el,3)
    ROOT.initHisto2D(histoTriggerSFEtaPt_0_0, 4)
    ROOT.initHisto2D(histoTriggerSFEtaPt_0_1, 5)
    ROOT.initHisto2D(histoTriggerSFEtaPt_0_2, 6)
    ROOT.initHisto2D(histoTriggerSFEtaPt_0_3, 7)
    ROOT.initHisto2D(histoTriggerSFEtaPt_1_0, 8)
    ROOT.initHisto2D(histoTriggerSFEtaPt_1_1, 9)
    ROOT.initHisto2D(histoTriggerSFEtaPt_1_2,10)
    ROOT.initHisto2D(histoTriggerSFEtaPt_1_3,11)
    ROOT.initHisto2D(histoTriggerSFEtaPt_2_0,12)
    ROOT.initHisto2D(histoTriggerSFEtaPt_2_1,13)
    ROOT.initHisto2D(histoTriggerSFEtaPt_2_2,14)
    ROOT.initHisto2D(histoTriggerSFEtaPt_2_3,15)
    ROOT.initHisto2D(histoTriggerSFEtaPt_3_0,16)
    ROOT.initHisto2D(histoTriggerSFEtaPt_3_1,17)
    ROOT.initHisto2D(histoTriggerSFEtaPt_3_2,18)
    ROOT.initHisto2D(histoTriggerSFEtaPt_3_3,19)
    ROOT.initHisto2D(histoBTVEffEtaPtLF,20)
    ROOT.initHisto2D(histoBTVEffEtaPtCJ,21)
    ROOT.initHisto2D(histoBTVEffEtaPtBJ,22)
    ROOT.initHisto2D(histoFakeEtaPt_mu[1],23)
    ROOT.initHisto2D(histoFakeEtaPt_mu[2],24)
    ROOT.initHisto2D(histoFakeEtaPt_mu[3],25)
    ROOT.initHisto2D(histoFakeEtaPt_mu[4],26)
    ROOT.initHisto2D(histoFakeEtaPt_mu[5],27)
    ROOT.initHisto2D(histoFakeEtaPt_mu[6],28)
    ROOT.initHisto2D(histoFakeEtaPt_mu[7],29)
    ROOT.initHisto2D(histoFakeEtaPt_mu[8],30)
    ROOT.initHisto2D(histoFakeEtaPt_el[1],31)
    ROOT.initHisto2D(histoFakeEtaPt_el[2],32)
    ROOT.initHisto2D(histoFakeEtaPt_el[3],33)
    ROOT.initHisto2D(histoFakeEtaPt_el[4],34)
    ROOT.initHisto2D(histoFakeEtaPt_el[5],35)
    ROOT.initHisto2D(histoFakeEtaPt_el[6],36)
    ROOT.initHisto2D(histoFakeEtaPt_el[7],37)
    ROOT.initHisto2D(histoFakeEtaPt_el[8],38)
    ROOT.initHisto2D(histoTriggerDAEtaPt[0],40)
    ROOT.initHisto2D(histoTriggerDAEtaPt[1],41)
    ROOT.initHisto2D(histoTriggerDAEtaPt[2],42)
    ROOT.initHisto2D(histoTriggerDAEtaPt[3],43)
    ROOT.initHisto2D(histoTriggerDAEtaPt[4],44)
    ROOT.initHisto2D(histoTriggerDAEtaPt[5],45)
    ROOT.initHisto2D(histoTriggerDAEtaPt[6],46)
    ROOT.initHisto2D(histoTriggerDAEtaPt[7],47)
    ROOT.initHisto2D(histoTriggerDAEtaPt[8],48)
    ROOT.initHisto2D(histoTriggerDAEtaPt[9],49)
    ROOT.initHisto2D(histoTriggerMCEtaPt[0],50)
    ROOT.initHisto2D(histoTriggerMCEtaPt[1],51)
    ROOT.initHisto2D(histoTriggerMCEtaPt[2],52)
    ROOT.initHisto2D(histoTriggerMCEtaPt[3],53)
    ROOT.initHisto2D(histoTriggerMCEtaPt[4],54)
    ROOT.initHisto2D(histoTriggerMCEtaPt[5],55)
    ROOT.initHisto2D(histoTriggerMCEtaPt[6],56)
    ROOT.initHisto2D(histoTriggerMCEtaPt[7],57)
    ROOT.initHisto2D(histoTriggerMCEtaPt[8],58)
    ROOT.initHisto2D(histoTriggerMCEtaPt[9],59)
    ROOT.initHisto1D(puWeights[0],0)
    ROOT.initHisto1D(puWeights[1],1)
    ROOT.initHisto1D(puWeights[2],2)

    ROOT.initJSONSFs(year)

    overallTriggers = jsonObject['triggers']
    TRIGGERMUEG = getTriggerFromJson(overallTriggers, "TRIGGERMUEG", year)
    TRIGGERDMU  = getTriggerFromJson(overallTriggers, "TRIGGERDMU", year)
    TRIGGERSMU  = getTriggerFromJson(overallTriggers, "TRIGGERSMU", year)
    TRIGGERDEL  = getTriggerFromJson(overallTriggers, "TRIGGERDEL", year)
    TRIGGERSEL  = getTriggerFromJson(overallTriggers, "TRIGGERSEL", year)

    list_TRIGGERMUEG = TRIGGERMUEG.split('(')[1].split(')')[0].split('||')
    list_TRIGGERDMU  = TRIGGERDMU .split('(')[1].split(')')[0].split('||')
    list_TRIGGERSMU  = TRIGGERSMU .split('(')[1].split(')')[0].split('||')
    list_TRIGGERDEL  = TRIGGERDEL .split('(')[1].split(')')[0].split('||')
    list_TRIGGERSEL  = TRIGGERSEL .split('(')[1].split(')')[0].split('||')

    list_TRIGGER = list_TRIGGERMUEG
    list_TRIGGER.extend(list_TRIGGERDMU)
    list_TRIGGER.extend(list_TRIGGERSMU)
    list_TRIGGER.extend(list_TRIGGERDEL)
    list_TRIGGER.extend(list_TRIGGERSEL)
    print("Total number of trigger paths: {0}".format(len(list_TRIGGER)))

    dfbase = selectionLL(df,year,PDType,isData,TRIGGERMUEG,TRIGGERDMU,TRIGGERSMU,TRIGGERDEL,TRIGGERSEL,count)
    dfbase = dfbase.Define("mjjGen", "{0}".format(0))

    dfbase = selectionWeigths(dfbase,isData,year,PDType,weight,useFR,bTagSel,useBTaggingWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,MUOWP,ELEWP,correctionString,0)

    overallMETFilters = jsonObject['met_filters']
    METFILTERS = getTriggerFromJson(overallMETFilters, "All", year)
    dfbase = dfbase.Define("METFILTERS", "{0}".format(METFILTERS)).Filter("METFILTERS > 0","METFILTERS > 0")

    dfcat = []
    dfssx0cat = []
    dfwwx0cat = []
    dfztt0cat = []
    dftop0cat = []
    dfhwwxcat = []
    dftop1cat = []

    dfssx1cat = []
    dfssx2cat = []

    dfssx0catMuonMomUp       = []
    dfssx0catElectronMomUp   = []
    dfwwx0catMuonMomUp       = []
    dfwwx0catElectronMomUp   = []
    dfztt0catMuonMomUp       = []
    dfztt0catElectronMomUp   = []
    dftop0catMuonMomUp       = []
    dftop0catElectronMomUp   = []
    dftop1catMuonMomUp       = []
    dftop1catElectronMomUp   = []

    for x in range(nCat):
        dfcat.append(dfbase.Define("kPlotNonPrompt", "{0}".format(plotCategory("kPlotNonPrompt")))
                           .Define("kPlotWS", "{0}".format(plotCategory("kPlotWS")))
                           .Define("theCat{0}".format(x), "compute_category({0},kPlotNonPrompt,kPlotWS,nFake,nTight,0)".format(theCat))
                           .Filter("theCat{0}=={1}".format(x,x), "correct category ({0})".format(x))
                           )

        if(isData == "false"):
            dfcat[x] = dfcat[x].Define("nPileupJets", "compute_nPileupJets(good_Jet_pt,good_Jet_eta,good_Jet_phi,GenJet_pt,GenJet_eta,GenJet_phi)")
        else:
            dfcat[x] = dfcat[x].Define("nPileupJets", "ngood_jets")

        dfcat[x] = dfcat[x].Define("weightWW", "weight")

        # Tight gen selection
        if(makeDataCards == -2 and isData == "false"):
            dfcat[x] = selectionGenLepJet(dfcat[x],20,30,jetEtaCut)
            dfcat[x] = (dfcat[x].Define("theGenCat", "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,3)".format(x))
                                .Filter("theGenCat  > 0","theGenCat  > 0")
                                )
        # Loose gen selection
        elif((x == plotCategory("kPlotqqWW") or x == plotCategory("kPlotggWW")) and isData == "false"):
            dfcat[x] = selectionGenLepJet(dfcat[x],20,30,jetEtaCut)
            dfcat[x] = (dfcat[x].Define("theGenCat", "compute_gen_category({0},ngood_GenJets,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,0)".format(x))
                                )
        else:
            dfcat[x] = dfcat[x].Define("theGenCat", "{0}".format(0))

        dfssx0cat.append(dfcat[x].Filter("Sum(fake_Muon_charge)+Sum(fake_Electron_charge) != 0 && Sum(fake_mu) == 1 && Sum(fake_el) == 1", "Same-sign leptons"))
        dfssx1cat.append(dfcat[x].Filter("Sum(fake_Muon_charge)+Sum(fake_Electron_charge) != 0 && Sum(fake_mu) == 2 && Sum(fake_el) == 0", "Same-sign muons"))
        dfssx2cat.append(dfcat[x].Filter("Sum(fake_Muon_charge)+Sum(fake_Electron_charge) != 0 && Sum(fake_mu) == 0 && Sum(fake_el) == 2", "Same-sign electrons"))

        histo[ 0][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format( 0,x), "histo_{0}_{1}".format( 0,x), 60, 20, 320), "mll{0}".format(altMass),"weightWW")
        histo[ 1][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format( 1,x), "histo_{0}_{1}".format( 1,x), 50,  0, 200), "ptll{0}".format(altMass),"weightWW")
        histo[ 2][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format( 2,x), "histo_{0}_{1}".format( 2,x), 5,-0.5,4.5), "nbtag_goodbtag_Jet_bjet","weightWW")

        dfcat[x] = dfcat[x].Filter("Sum(fake_Muon_charge)+Sum(fake_Electron_charge) == 0 && Sum(fake_mu) == 1 && Sum(fake_el) == 1", "Opposite-sign leptons")

        histo[ 3][x] = dfcat[x].Histo1D(("histo_{0}_{1}".format( 3,x), "histo_{0}_{1}".format( 3,x), 60, 20, 320), "mll{0}".format(altMass),"weightWW")
        histo[ 4][x] = dfcat[x].Histo1D(("histo_{0}_{1}".format( 4,x), "histo_{0}_{1}".format( 4,x), 50,  0, 200), "ptll{0}".format(altMass),"weightWW")
        histo[ 5][x] = dfcat[x].Histo1D(("histo_{0}_{1}".format( 5,x), "histo_{0}_{1}".format( 5,x), 5,-0.5,4.5), "nbtag_goodbtag_Jet_bjet","weightWW")
        histo[79][x] = dfcat[x].Filter("ngood_jets==0").Histo1D(("histo_{0}_{1}".format(79,x), "histo_{0}_{1}".format(79,x), 5,-0.5,4.5), "nbtag_goodbtag_Jet_bjet","weightWW")

        dfssx0cat[x] = dfssx0cat[x].Filter("nbtag_goodbtag_Jet_bjet == 0", "No b-jets")
        dfssx0catMuonMomUp      .append(dfssx0cat[x])
        dfssx0catElectronMomUp  .append(dfssx0cat[x])
        dfssx1cat[x] = dfssx1cat[x].Filter("nbtag_goodbtag_Jet_bjet == 0", "No b-jets")
        dfssx2cat[x] = dfssx2cat[x].Filter("nbtag_goodbtag_Jet_bjet == 0", "No b-jets")

        dfssx0catMuonMomUp      [x] = dfssx0catMuonMomUp      [x].Filter("mllMuonMomUp       > 85 && ptl1MuonMomUp       > 25 && ptl2MuonMomUp      > 20")
        dfssx0catElectronMomUp  [x] = dfssx0catElectronMomUp  [x].Filter("mllElectronMomUp   > 85 && ptl1ElectronMomUp   > 25 && ptl2ElectronMomUp  > 20")

        dfssx0cat[x] = dfssx0cat[x].Filter("mll{0} > 85 && ptl1{0} > 25 && ptl2{0} > 20".format(altMass), "mll > 85 && ptl1 > 25 && ptl2 > 20")
        dfssx1cat[x] = dfssx1cat[x].Filter("mll{0} > 50 && ptl1{0} > 25 && ptl2{0} > 20".format(altMass), "mll > 50 && ptl1 > 25 && ptl2 > 20")
        dfssx2cat[x] = dfssx2cat[x].Filter("mll{0} > 50 && ptl1{0} > 25 && ptl2{0} > 20".format(altMass), "mll > 50 && ptl1 > 25 && ptl2 > 20")

        dfwwx0cat.append(dfcat[x].Filter("nbtag_goodbtag_Jet_bjet == 0", "No b-jets"))
        dfwwx0catMuonMomUp      .append(dfwwx0cat[x])
        dfwwx0catElectronMomUp  .append(dfwwx0cat[x])

        dfwwx0catMuonMomUp      [x] = dfwwx0catMuonMomUp      [x].Filter("mllMuonMomUp       > 85 && ptl1MuonMomUp       > 25 && ptl2MuonMomUp      > 20")
        dfwwx0catElectronMomUp  [x] = dfwwx0catElectronMomUp  [x].Filter("mllElectronMomUp   > 85 && ptl1ElectronMomUp   > 25 && ptl2ElectronMomUp  > 20")

        dfwwx0cat[x] = dfwwx0cat[x].Filter("mll{0} > 85 && ptl1{0} > 25 && ptl2{0} > 20".format(altMass), "mll > 85 && ptl1 > 25 && ptl2 > 20")

        dfztt0cat.append(dfcat[x].Filter("nbtag_goodbtag_Jet_bjet == 0", "No b-jets"))
        dfztt0catMuonMomUp      .append(dfztt0cat[x])
        dfztt0catElectronMomUp  .append(dfztt0cat[x])

        dfztt0catMuonMomUp      [x] = dfztt0catMuonMomUp      [x].Filter("ptllMuonMomUp       < 30 && mllMuonMomUp       < 85 && ptl1MuonMomUp       > 25 && ptl2MuonMomUp      > 20")
        dfztt0catElectronMomUp  [x] = dfztt0catElectronMomUp  [x].Filter("ptllElectronMomUp   < 30 && mllElectronMomUp   < 85 && ptl1ElectronMomUp   > 25 && ptl2ElectronMomUp  > 20")

        dfztt0cat[x] = dfztt0cat[x].Filter("ptll{0} < 30 && mll{0} < 85 && ptl1{0} > 25 && ptl2{0} > 20".format(altMass), "ptll < 30 && mll < 85 && ptl1 > 25 && ptl2 > 20")

        dftop0cat.append(dfcat[x].Filter("nbtag_goodbtag_Jet_bjet >= 1 && nbtag_goodbtag_Jet_bjet <= 2", "b-jets"))
        dftop0catMuonMomUp      .append(dftop0cat[x])
        dftop0catElectronMomUp  .append(dftop0cat[x])

        dftop0catMuonMomUp      [x] = dftop0catMuonMomUp      [x].Filter("mllMuonMomUp       > 85 && ptl1MuonMomUp       > 25 && ptl2MuonMomUp      > 20")
        dftop0catElectronMomUp  [x] = dftop0catElectronMomUp  [x].Filter("mllElectronMomUp   > 85 && ptl1ElectronMomUp   > 25 && ptl2ElectronMomUp  > 20")

        dftop0cat[x] = dftop0cat[x].Filter("mll{0} > 85 && ptl1{0} > 25 && ptl2{0} > 20".format(altMass), "mll > 85 && ptl1 > 25 && ptl2 > 20")

        dftop1cat.append(dfcat[x].Filter("nbtag_goodbtag_Jet_bjet == 2", "b-jets"))
        dftop1catMuonMomUp      .append(dftop1cat[x])
        dftop1catElectronMomUp  .append(dftop1cat[x])

        dftop1catMuonMomUp      [x] = dftop1catMuonMomUp      [x].Filter("mllMuonMomUp       > 85 && ptl1MuonMomUp       > 25 && ptl2MuonMomUp      > 20")
        dftop1catElectronMomUp  [x] = dftop1catElectronMomUp  [x].Filter("mllElectronMomUp   > 85 && ptl1ElectronMomUp   > 25 && ptl2ElectronMomUp  > 20")

        dftop1cat[x] = dftop1cat[x].Filter("mll{0} > 85 && ptl1{0} > 25 && ptl2{0} > 20".format(altMass), "mll > 85 && ptl1 > 25 && ptl2 > 20")

        dfhwwxcat.append(dfcat[x].Filter("nbtag_goodbtag_Jet_bjet == 0", "No b-jets")
                                 .Filter("ptll{0} > 30 && mll{0} < 85 && minPMET{0} > 20".format(altMass), "ptll > 30 && mll < 85 && minPMET > 20")
                                 )

        histo[ 6][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format( 6,x), "histo_{0}_{1}".format( 6,x), 50,  0, 3.1416), "dPhilMETMin","weightWW")
        histo[ 7][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format( 7,x), "histo_{0}_{1}".format( 7,x), 50,  0, 3.1416), "dPhilMETMin","weightWW")
        histo[ 8][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format( 8,x), "histo_{0}_{1}".format( 8,x), 50,  0, 3.1416), "dPhilMETMin","weightWW")
        histo[ 9][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format( 9,x), "histo_{0}_{1}".format( 9,x), 50,  0, 3.1416), "dPhilMETMin","weightWW")

        histo[10][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(10,x), "histo_{0}_{1}".format(10,x), 100, 0, 200), "minPMET{0}".format(altMass),"weightWW")
        histo[11][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(11,x), "histo_{0}_{1}".format(11,x), 100, 0, 200), "minPMET{0}".format(altMass),"weightWW")
        histo[12][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(12,x), "histo_{0}_{1}".format(12,x), 100, 0, 200), "minPMET{0}".format(altMass),"weightWW")
        histo[13][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(13,x), "histo_{0}_{1}".format(13,x), 100, 0, 200), "minPMET{0}".format(altMass),"weightWW")

        histo[14][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(14,x), "histo_{0}_{1}".format(14,x), 100, 0, 200), "thePuppiMET_pt","weightWW")
        histo[15][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(15,x), "histo_{0}_{1}".format(15,x), 100, 0, 200), "thePuppiMET_pt","weightWW")
        histo[16][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(16,x), "histo_{0}_{1}".format(16,x), 100, 0, 200), "thePuppiMET_pt","weightWW")
        histo[17][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(17,x), "histo_{0}_{1}".format(17,x), 100, 0, 200), "thePuppiMET_pt","weightWW")

        histo[18][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(18,x), "histo_{0}_{1}".format(18,x), 50,  0, 5), "drll","weightWW")
        histo[19][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(19,x), "histo_{0}_{1}".format(19,x), 50,  0, 5), "drll","weightWW")
        histo[20][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(20,x), "histo_{0}_{1}".format(20,x), 50,  0, 5), "drll","weightWW")
        histo[21][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(21,x), "histo_{0}_{1}".format(21,x), 50,  0, 5), "drll","weightWW")

        histo[22][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(22,x), "histo_{0}_{1}".format(22,x), 50,  0, 3.1416), "dphill","weightWW")
        histo[23][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(23,x), "histo_{0}_{1}".format(23,x), 50,  0, 3.1416), "dphill","weightWW")
        histo[24][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(24,x), "histo_{0}_{1}".format(24,x), 50,  0, 3.1416), "dphill","weightWW")
        histo[25][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(25,x), "histo_{0}_{1}".format(25,x), 50,  0, 3.1416), "dphill","weightWW")

        histo[26][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(26,x), "histo_{0}_{1}".format(26,x), 40, 25, 225), "ptl1{0}".format(altMass),"weightWW")
        histo[27][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(27,x), "histo_{0}_{1}".format(27,x), 40, 25, 225), "ptl1{0}".format(altMass),"weightWW")
        histo[28][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(28,x), "histo_{0}_{1}".format(28,x), 40, 25, 225), "ptl1{0}".format(altMass),"weightWW")
        histo[29][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(29,x), "histo_{0}_{1}".format(29,x), 40, 25, 225), "ptl1{0}".format(altMass),"weightWW")

        histo[30][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(30,x), "histo_{0}_{1}".format(30,x), 40, 20, 220), "ptl2{0}".format(altMass),"weightWW")
        histo[31][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(31,x), "histo_{0}_{1}".format(31,x), 40, 20, 220), "ptl2{0}".format(altMass),"weightWW")
        histo[32][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(32,x), "histo_{0}_{1}".format(32,x), 40, 20, 220), "ptl2{0}".format(altMass),"weightWW")
        histo[33][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(33,x), "histo_{0}_{1}".format(33,x), 40, 20, 220), "ptl2{0}".format(altMass),"weightWW")

        histo[34][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(34,x), "histo_{0}_{1}".format(34,x), 25,  0,2.5), "etal1","weightWW")
        histo[35][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(35,x), "histo_{0}_{1}".format(35,x), 25,  0,2.5), "etal1","weightWW")
        histo[36][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(36,x), "histo_{0}_{1}".format(36,x), 25,  0,2.5), "etal1","weightWW")
        histo[37][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(37,x), "histo_{0}_{1}".format(37,x), 25,  0,2.5), "etal1","weightWW")

        histo[38][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(38,x), "histo_{0}_{1}".format(38,x), 25,  0,2.5), "etal2","weightWW")
        histo[39][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(39,x), "histo_{0}_{1}".format(39,x), 25,  0,2.5), "etal2","weightWW")
        histo[40][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(40,x), "histo_{0}_{1}".format(40,x), 25,  0,2.5), "etal2","weightWW")
        histo[41][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(41,x), "histo_{0}_{1}".format(41,x), 25,  0,2.5), "etal2","weightWW")

        histo[42][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(42,x), "histo_{0}_{1}".format(42,x), 4,-0.5,3.5), "ngood_jets","weightWW")
        histo[43][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(43,x), "histo_{0}_{1}".format(43,x), 4,-0.5,3.5), "ngood_jets","weightWW")
        histo[44][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(44,x), "histo_{0}_{1}".format(44,x), 4,-0.5,3.5), "ngood_jets","weightWW")
        histo[45][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(45,x), "histo_{0}_{1}".format(45,x), 4,-0.5,3.5), "ngood_jets","weightWW")

        histo[46][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(46,x), "histo_{0}_{1}".format(46,x), 50, 85, 385), "mll{0}".format(altMass),"weightWW")
        histo[47][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(47,x), "histo_{0}_{1}".format(47,x), 50, 85, 385), "mll{0}".format(altMass),"weightWW")
        histo[48][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(48,x), "histo_{0}_{1}".format(48,x), 50, 35,  85), "mll{0}".format(altMass),"weightWW")
        histo[49][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(49,x), "histo_{0}_{1}".format(49,x), 50, 85, 385), "mll{0}".format(altMass),"weightWW")

        histo[50][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(50,x), "histo_{0}_{1}".format(50,x), 50,  0, 200), "ptll{0}".format(altMass),"weightWW")
        histo[51][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(51,x), "histo_{0}_{1}".format(51,x), 50,  0, 200), "ptll{0}".format(altMass),"weightWW")
        histo[52][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(52,x), "histo_{0}_{1}".format(52,x), 30,  0,  30), "ptll{0}".format(altMass),"weightWW")
        histo[53][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(53,x), "histo_{0}_{1}".format(53,x), 50,  0, 200), "ptll{0}".format(altMass),"weightWW")

        histo[54][x] = dfhwwxcat[x].Histo1D(("histo_{0}_{1}".format(54,x), "histo_{0}_{1}".format(54,x), 40, 30, 190), "ptll{0}".format(altMass),"weightWW")
        histo[55][x] = dfhwwxcat[x].Histo1D(("histo_{0}_{1}".format(55,x), "histo_{0}_{1}".format(55,x), 100,20, 220), "minPMET{0}".format(altMass),"weightWW")
        histo[56][x] = dfhwwxcat[x].Histo1D(("histo_{0}_{1}".format(56,x), "histo_{0}_{1}".format(56,x), 50,  0, 3.1416), "dphill","weightWW")
        histo[57][x] = dfhwwxcat[x].Histo1D(("histo_{0}_{1}".format(57,x), "histo_{0}_{1}".format(57,x), 4,-0.5,3.5), "ngood_jets","weightWW")
        histo[58][x] = dftop0cat[x].Filter("nbtag_goodbtag_Jet_bjet == 1").Histo1D(("histo_{0}_{1}".format(58,x), "histo_{0}_{1}".format(58,x), 4,-0.5,3.5), "ngood_jets","weightWW")
        histo[59][x] = dftop0cat[x].Filter("nbtag_goodbtag_Jet_bjet == 2").Histo1D(("histo_{0}_{1}".format(59,x), "histo_{0}_{1}".format(59,x), 4,-0.5,3.5), "ngood_jets","weightWW")

        histo[60][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(60,x), "histo_{0}_{1}".format(60,x), 25,-2.5,2.5), "good_Jet_eta","weightWW")
        histo[61][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(61,x), "histo_{0}_{1}".format(61,x), 25,-2.5,2.5), "good_Jet_eta","weightWW")
        histo[62][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(62,x), "histo_{0}_{1}".format(62,x), 25,-2.5,2.5), "good_Jet_eta","weightWW")
        histo[63][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(63,x), "histo_{0}_{1}".format(63,x), 25,-2.5,2.5), "good_Jet_eta","weightWW")

        histo[64][x] = dfwwx0cat[x].Filter("ptll{0} < 20 && thePuppiMET_pt < 20".format(altMass)).Histo1D(("histo_{0}_{1}".format(64,x), "histo_{0}_{1}".format(64,x), 20,25,185), "ptl1","weightWW")
        histo[65][x] = dfwwx0cat[x].Filter("ptll{0} < 20 && thePuppiMET_pt < 20".format(altMass)).Histo1D(("histo_{0}_{1}".format(65,x), "histo_{0}_{1}".format(65,x), 20,20,140), "ptl2","weightWW")

        histo[69][x] = dfssx1cat[x].Histo1D(("histo_{0}_{1}".format(69,x), "histo_{0}_{1}".format(69,x), 60, 50, 410), "mll{0}".format(altMass),"weightWW")
        histo[70][x] = dfssx2cat[x].Histo1D(("histo_{0}_{1}".format(70,x), "histo_{0}_{1}".format(70,x), 60, 50, 410), "mll{0}".format(altMass),"weightWW")
        dfssx2cat[x] = dfssx2cat[x].Filter("mll{0} > 130".format(altMass), "mll > 130")
        histo[71][x] = dfssx1cat[x].Histo1D(("histo_{0}_{1}".format(71,x), "histo_{0}_{1}".format(71,x), 4,-0.5,3.5), "ngood_jets","weightWW")
        histo[72][x] = dfssx2cat[x].Histo1D(("histo_{0}_{1}".format(72,x), "histo_{0}_{1}".format(72,x), 4,-0.5,3.5), "ngood_jets","weightWW")

        histo[73][x] = dfssx0cat[x].Histo1D(("histo_{0}_{1}".format(73,x), "histo_{0}_{1}".format(73,x), 50,  0, 200), "ptww","weightWW")
        histo[74][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(74,x), "histo_{0}_{1}".format(74,x), 50,  0, 200), "ptww","weightWW")
        histo[75][x] = dfztt0cat[x].Histo1D(("histo_{0}_{1}".format(75,x), "histo_{0}_{1}".format(75,x), 30,  0, 200), "ptww","weightWW")
        histo[76][x] = dftop0cat[x].Histo1D(("histo_{0}_{1}".format(76,x), "histo_{0}_{1}".format(76,x), 50,  0, 200), "ptww","weightWW")

        histo[77][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(77,x), "histo_{0}_{1}".format(77,x), 10,-0.5, 9.5), "nPileupJets","weightWW")

        dftop0cat[x] = dftop0cat[x].Filter("nbtag_goodbtag_Jet_bjet == 1")
        dftop0catMuonMomUp      [x] = dftop0catMuonMomUp      [x].Filter("nbtag_goodbtag_Jet_bjet == 1")
        dftop0catElectronMomUp  [x] = dftop0catElectronMomUp  [x].Filter("nbtag_goodbtag_Jet_bjet == 1")

        if(x == plotCategory("kPlotData") and print_info == True):
             histo_test = (dfwwx0cat[x].Define("print_info","print_info(run,luminosityBlock,event)")
                          .Filter("print_info > 0")
                          .Histo1D(("test", "test", 4,-0.5,3.5), "ngood_jets","weightWW"))

        if(makeDataCards == -1):
            histo[100][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(100,x), "histo_{0}_{1}".format(100,x), 4,-0.5,3.5), "ngood_jets","weight")
            histo[101][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(101,x), "histo_{0}_{1}".format(101,x), 4,-0.5,3.5), "ngood_jets","weight0")
            histo[102][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(102,x), "histo_{0}_{1}".format(102,x), 4,-0.5,3.5), "ngood_jets","weight1")
            histo[103][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(103,x), "histo_{0}_{1}".format(103,x), 4,-0.5,3.5), "ngood_jets","weight2")
            histo[104][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(104,x), "histo_{0}_{1}".format(104,x), 4,-0.5,3.5), "ngood_jets","weight3")
            histo[105][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(105,x), "histo_{0}_{1}".format(105,x), 4,-0.5,3.5), "ngood_jets","weight4")
            histo[106][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(106,x), "histo_{0}_{1}".format(106,x), 4,-0.5,3.5), "ngood_jets","weight5")
            histo[107][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(107,x), "histo_{0}_{1}".format(107,x), 4,-0.5,3.5), "ngood_jets","weight6")
            TRIGGERMET = getTriggerFromJson(overallTriggers, "TRIGGERMET", year)
            histo[108][x] = dfwwx0cat[x].Define("triggerMET","{0}".format(TRIGGERMET)).Filter("triggerMET > 0").Histo1D(("histo_{0}_{1}".format(108,x), "histo_{0}_{1}".format(108,x), 4,-0.5,3.5), "ngood_jets","weight")

            histo[109][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(109,x), "histo_{0}_{1}".format(109,x), 4,-0.5,3.5), "ngood_jetsRaw"	 ,"weight")
            histo[110][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(110,x), "histo_{0}_{1}".format(110,x), 4,-0.5,3.5), "ngood_jetsNoJESJER","weight")
            histo[111][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(111,x), "histo_{0}_{1}".format(111,x), 4,-0.5,3.5), "ngood_jetsNoJES"   ,"weight")
            histo[112][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(112,x), "histo_{0}_{1}".format(112,x), 4,-0.5,3.5), "ngood_jetsNoJER"   ,"weight")

            histo[113][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(113,x), "histo_{0}_{1}".format(113,x),40,30,230), "good_Jet_pt"	,"weight")
            histo[114][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(114,x), "histo_{0}_{1}".format(114,x),40,30,230), "good_Jet_ptRaw"	,"weight")
            histo[115][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(115,x), "histo_{0}_{1}".format(115,x),40,30,230), "good_Jet_ptNoJESJER","weight")
            histo[116][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(116,x), "histo_{0}_{1}".format(116,x),40,30,230), "good_Jet_ptNoJES"	,"weight")
            histo[117][x] = dfwwx0cat[x].Histo1D(("histo_{0}_{1}".format(117,x), "histo_{0}_{1}".format(117,x),40,30,230), "good_Jet_ptNoJER"	,"weight")

        elif(makeDataCards == -2 and isData == "false"):
            dfwwx0cat[x] = (dfwwx0cat[x].Define("ptl1Gen", "good_GenDressedLepton_pt[0]")
                                        .Define("ptl2Gen", "good_GenDressedLepton_pt[1]")
                                        .Define("etal1Gen","good_GenDressedLepton_eta[0]")
                                        .Define("etal2Gen","good_GenDressedLepton_eta[1]")
                                        .Define("mllGen",  "Minv2(good_GenDressedLepton_pt[0], good_GenDressedLepton_eta[0], good_GenDressedLepton_phi[0], good_GenDressedLepton_mass[0],good_GenDressedLepton_pt[1], good_GenDressedLepton_eta[1], good_GenDressedLepton_phi[1], good_GenDressedLepton_mass[1]).first")
                                        .Define("ptllGen", "Minv2(good_GenDressedLepton_pt[0], good_GenDressedLepton_eta[0], good_GenDressedLepton_phi[0], good_GenDressedLepton_mass[0],good_GenDressedLepton_pt[1], good_GenDressedLepton_eta[1], good_GenDressedLepton_phi[1], good_GenDressedLepton_mass[1]).second")
                                        )

            histo[120][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[0]) == 13")                      .Histo1D(("histo_{0}_{1}".format(120,x), "histo_{0}_{1}".format(120,x), 20, 20., 320.), "ptl1","weight")
            histo[121][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[1]) == 13")                      .Histo1D(("histo_{0}_{1}".format(121,x), "histo_{0}_{1}".format(121,x), 20, 20., 320.), "ptl2","weight")
            histo[122][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[0]) == 11")                      .Histo1D(("histo_{0}_{1}".format(122,x), "histo_{0}_{1}".format(122,x), 20, 20., 320.), "ptl1","weight")
            histo[123][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[1]) == 11")                      .Histo1D(("histo_{0}_{1}".format(123,x), "histo_{0}_{1}".format(123,x), 20, 20., 320.), "ptl2","weight")
            histo[124][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[0]) == 13 && ngood_GenJets == 0").Histo1D(("histo_{0}_{1}".format(124,x), "histo_{0}_{1}".format(124,x), 20, 20., 320.), "ptl1","weight")
            histo[125][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[1]) == 13 && ngood_GenJets == 0").Histo1D(("histo_{0}_{1}".format(125,x), "histo_{0}_{1}".format(125,x), 20, 20., 320.), "ptl2","weight")
            histo[126][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[0]) == 11 && ngood_GenJets == 0").Histo1D(("histo_{0}_{1}".format(126,x), "histo_{0}_{1}".format(126,x), 20, 20., 320.), "ptl1","weight")
            histo[127][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[1]) == 11 && ngood_GenJets == 0").Histo1D(("histo_{0}_{1}".format(127,x), "histo_{0}_{1}".format(127,x), 20, 20., 320.), "ptl2","weight")
            histo[128][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[0]) == 13 && ngood_GenJets == 1").Histo1D(("histo_{0}_{1}".format(128,x), "histo_{0}_{1}".format(128,x), 20, 20., 320.), "ptl1","weight")
            histo[129][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[1]) == 13 && ngood_GenJets == 1").Histo1D(("histo_{0}_{1}".format(129,x), "histo_{0}_{1}".format(129,x), 20, 20., 320.), "ptl2","weight")
            histo[130][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[0]) == 11 && ngood_GenJets == 1").Histo1D(("histo_{0}_{1}".format(130,x), "histo_{0}_{1}".format(130,x), 20, 20., 320.), "ptl1","weight")
            histo[131][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[1]) == 11 && ngood_GenJets == 1").Histo1D(("histo_{0}_{1}".format(131,x), "histo_{0}_{1}".format(131,x), 20, 20., 320.), "ptl2","weight")
            histo[132][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[0]) == 13 && ngood_GenJets >= 2").Histo1D(("histo_{0}_{1}".format(132,x), "histo_{0}_{1}".format(132,x), 20, 20., 320.), "ptl1","weight")
            histo[133][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[1]) == 13 && ngood_GenJets >= 2").Histo1D(("histo_{0}_{1}".format(133,x), "histo_{0}_{1}".format(133,x), 20, 20., 320.), "ptl2","weight")
            histo[134][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[0]) == 11 && ngood_GenJets >= 2").Histo1D(("histo_{0}_{1}".format(134,x), "histo_{0}_{1}".format(134,x), 20, 20., 320.), "ptl1","weight")
            histo[135][x] = dfwwx0cat[x].Filter("abs(GenDressedLepton_pdgId[1]) == 11 && ngood_GenJets >= 2").Histo1D(("histo_{0}_{1}".format(135,x), "histo_{0}_{1}".format(135,x), 20, 20., 320.), "ptl2","weight")
            histo[136][x] = dfwwx0cat[x]                                                                     .Histo1D(("histo_{0}_{1}".format(136,x), "histo_{0}_{1}".format(136,x), 20, 85., 485.), "mllGen","weight")
            histo[137][x] = dfwwx0cat[x].Filter("ngood_GenJets == 0")                                        .Histo1D(("histo_{0}_{1}".format(137,x), "histo_{0}_{1}".format(137,x), 20, 85., 485.), "mllGen","weight")
            histo[138][x] = dfwwx0cat[x].Filter("ngood_GenJets == 1")                                        .Histo1D(("histo_{0}_{1}".format(138,x), "histo_{0}_{1}".format(138,x), 20, 85., 485.), "mllGen","weight")
            histo[139][x] = dfwwx0cat[x].Filter("ngood_GenJets >= 2")                                        .Histo1D(("histo_{0}_{1}".format(139,x), "histo_{0}_{1}".format(139,x), 20, 85., 485.), "mllGen","weight")
            histo[140][x] = dfwwx0cat[x]                                                                     .Histo1D(("histo_{0}_{1}".format(140,x), "histo_{0}_{1}".format(140,x), 20,  0., 300.), "ptllGen","weight")
            histo[141][x] = dfwwx0cat[x].Filter("ngood_GenJets == 0")                                        .Histo1D(("histo_{0}_{1}".format(141,x), "histo_{0}_{1}".format(141,x), 20,  0., 300.), "ptllGen","weight")
            histo[142][x] = dfwwx0cat[x].Filter("ngood_GenJets == 1")                                        .Histo1D(("histo_{0}_{1}".format(142,x), "histo_{0}_{1}".format(142,x), 20,  0., 300.), "ptllGen","weight")
            histo[143][x] = dfwwx0cat[x].Filter("ngood_GenJets >= 2")                                        .Histo1D(("histo_{0}_{1}".format(143,x), "histo_{0}_{1}".format(143,x), 20,  0., 300.), "ptllGen","weight")

        BinYF = 4
        minYF = -0.5
        maxYF = 3.5
        if(makeDataCards == 1):
            BinXF = 4
            minXF = -0.5
            maxXF = 3.5

            startF = 0
            for nv in range(0,135):
                histo2D[startF+nv][x] = makeFinalVariable2D(dfssx0cat[x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,nv)
            histo2D[startF+135][x]    = makeFinalVariable2D(dfssx0catMuonMomUp      [x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,135)
            histo2D[startF+136][x]    = makeFinalVariable2D(dfssx0catElectronMomUp  [x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,136)
            histo2D[startF+137][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes00Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,137)
            histo2D[startF+138][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes01Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,138)
            histo2D[startF+139][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes02Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,139)
            histo2D[startF+140][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes03Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,140)
            histo2D[startF+141][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes04Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,141)
            histo2D[startF+142][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes05Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,142)
            histo2D[startF+143][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes06Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,143)
            histo2D[startF+144][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes07Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,144)
            histo2D[startF+145][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes08Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,145)
            histo2D[startF+146][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes09Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,146)
            histo2D[startF+147][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes10Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,147)
            histo2D[startF+148][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes11Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,148)
            histo2D[startF+149][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes12Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,149)
            histo2D[startF+150][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes13Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,150)
            histo2D[startF+151][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes14Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,151)
            histo2D[startF+152][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes15Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,152)
            histo2D[startF+153][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes16Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,153)
            histo2D[startF+154][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes17Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,154)
            histo2D[startF+155][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes18Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,155)
            histo2D[startF+156][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes19Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,156)
            histo2D[startF+157][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes20Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,157)
            histo2D[startF+158][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes21Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,158)
            histo2D[startF+159][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes22Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,159)
            histo2D[startF+160][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes23Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,160)
            histo2D[startF+161][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes24Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,161)
            histo2D[startF+162][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes25Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,162)
            histo2D[startF+163][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes26Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,163)
            histo2D[startF+164][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJes27Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,164)
            histo2D[startF+165][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jetsJerUp"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,165)
            histo2D[startF+166][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,166)
            histo2D[startF+167][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,167)
            histo2D[startF+168][x]    = makeFinalVariable2D(dfssx0cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,168)
            if(x == plotCategory("kPlotNonPrompt")):
                startNonPrompt = 0
                histoNonPrompt[0+startNonPrompt] = dfssx0cat[x].Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm0")
                histoNonPrompt[1+startNonPrompt] = dfssx0cat[x].Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm1")
                histoNonPrompt[2+startNonPrompt] = dfssx0cat[x].Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm2")
                histoNonPrompt[3+startNonPrompt] = dfssx0cat[x].Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte0")
                histoNonPrompt[4+startNonPrompt] = dfssx0cat[x].Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte1")
                histoNonPrompt[5+startNonPrompt] = dfssx0cat[x].Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte2")

            startF = 200
            for nv in range(0,135):
                histo2D[startF+nv][x] = makeFinalVariable2D(dfwwx0cat[x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,nv)
            histo2D[startF+135][x]    = makeFinalVariable2D(dfwwx0catMuonMomUp      [x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,135)
            histo2D[startF+136][x]    = makeFinalVariable2D(dfwwx0catElectronMomUp  [x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,136)
            histo2D[startF+137][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes00Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,137)
            histo2D[startF+138][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes01Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,138)
            histo2D[startF+139][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes02Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,139)
            histo2D[startF+140][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes03Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,140)
            histo2D[startF+141][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes04Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,141)
            histo2D[startF+142][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes05Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,142)
            histo2D[startF+143][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes06Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,143)
            histo2D[startF+144][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes07Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,144)
            histo2D[startF+145][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes08Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,145)
            histo2D[startF+146][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes09Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,146)
            histo2D[startF+147][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes10Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,147)
            histo2D[startF+148][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes11Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,148)
            histo2D[startF+149][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes12Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,149)
            histo2D[startF+150][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes13Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,150)
            histo2D[startF+151][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes14Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,151)
            histo2D[startF+152][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes15Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,152)
            histo2D[startF+153][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes16Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,153)
            histo2D[startF+154][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes17Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,154)
            histo2D[startF+155][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes18Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,155)
            histo2D[startF+156][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes19Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,156)
            histo2D[startF+157][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes20Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,157)
            histo2D[startF+158][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes21Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,158)
            histo2D[startF+159][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes22Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,159)
            histo2D[startF+160][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes23Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,160)
            histo2D[startF+161][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes24Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,161)
            histo2D[startF+162][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes25Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,162)
            histo2D[startF+163][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes26Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,163)
            histo2D[startF+164][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJes27Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,164)
            histo2D[startF+165][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jetsJerUp"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,165)
            histo2D[startF+166][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,166)
            histo2D[startF+167][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,167)
            histo2D[startF+168][x]    = makeFinalVariable2D(dfwwx0cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,168)
            if(x == plotCategory("kPlotNonPrompt")):
                startNonPrompt = 6
                histoNonPrompt[0+startNonPrompt] = dfwwx0cat[x].Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm0")
                histoNonPrompt[1+startNonPrompt] = dfwwx0cat[x].Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm1")
                histoNonPrompt[2+startNonPrompt] = dfwwx0cat[x].Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm2")
                histoNonPrompt[3+startNonPrompt] = dfwwx0cat[x].Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte0")
                histoNonPrompt[4+startNonPrompt] = dfwwx0cat[x].Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte1")
                histoNonPrompt[5+startNonPrompt] = dfwwx0cat[x].Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte2")

            startF = 400
            for nv in range(0,135):
                histo2D[startF+nv][x] = makeFinalVariable2D(dfztt0cat[x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,nv)
            histo2D[startF+135][x]    = makeFinalVariable2D(dfztt0catMuonMomUp      [x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,135)
            histo2D[startF+136][x]    = makeFinalVariable2D(dfztt0catElectronMomUp  [x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,136)
            histo2D[startF+137][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes00Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,137)
            histo2D[startF+138][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes01Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,138)
            histo2D[startF+139][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes02Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,139)
            histo2D[startF+140][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes03Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,140)
            histo2D[startF+141][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes04Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,141)
            histo2D[startF+142][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes05Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,142)
            histo2D[startF+143][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes06Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,143)
            histo2D[startF+144][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes07Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,144)
            histo2D[startF+145][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes08Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,145)
            histo2D[startF+146][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes09Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,146)
            histo2D[startF+147][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes10Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,147)
            histo2D[startF+148][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes11Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,148)
            histo2D[startF+149][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes12Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,149)
            histo2D[startF+150][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes13Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,150)
            histo2D[startF+151][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes14Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,151)
            histo2D[startF+152][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes15Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,152)
            histo2D[startF+153][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes16Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,153)
            histo2D[startF+154][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes17Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,154)
            histo2D[startF+155][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes18Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,155)
            histo2D[startF+156][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes19Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,156)
            histo2D[startF+157][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes20Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,157)
            histo2D[startF+158][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes21Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,158)
            histo2D[startF+159][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes22Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,159)
            histo2D[startF+160][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes23Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,160)
            histo2D[startF+161][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes24Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,161)
            histo2D[startF+162][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes25Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,162)
            histo2D[startF+163][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes26Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,163)
            histo2D[startF+164][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJes27Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,164)
            histo2D[startF+165][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jetsJerUp"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,165)
            histo2D[startF+166][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,166)
            histo2D[startF+167][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,167)
            histo2D[startF+168][x]    = makeFinalVariable2D(dfztt0cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,168)
            if(x == plotCategory("kPlotNonPrompt")):
                startNonPrompt = 12
                histoNonPrompt[0+startNonPrompt] = dfztt0cat[x].Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm0")
                histoNonPrompt[1+startNonPrompt] = dfztt0cat[x].Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm1")
                histoNonPrompt[2+startNonPrompt] = dfztt0cat[x].Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm2")
                histoNonPrompt[3+startNonPrompt] = dfztt0cat[x].Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte0")
                histoNonPrompt[4+startNonPrompt] = dfztt0cat[x].Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte1")
                histoNonPrompt[5+startNonPrompt] = dfztt0cat[x].Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte2")

            startF = 600
            for nv in range(0,135):
                histo2D[startF+nv][x] = makeFinalVariable2D(dftop0cat[x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,nv)
            histo2D[startF+135][x]    = makeFinalVariable2D(dftop0catMuonMomUp      [x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,135)
            histo2D[startF+136][x]    = makeFinalVariable2D(dftop0catElectronMomUp  [x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,136)
            histo2D[startF+137][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes00Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,137)
            histo2D[startF+138][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes01Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,138)
            histo2D[startF+139][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes02Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,139)
            histo2D[startF+140][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes03Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,140)
            histo2D[startF+141][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes04Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,141)
            histo2D[startF+142][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes05Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,142)
            histo2D[startF+143][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes06Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,143)
            histo2D[startF+144][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes07Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,144)
            histo2D[startF+145][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes08Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,145)
            histo2D[startF+146][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes09Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,146)
            histo2D[startF+147][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes10Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,147)
            histo2D[startF+148][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes11Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,148)
            histo2D[startF+149][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes12Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,149)
            histo2D[startF+150][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes13Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,150)
            histo2D[startF+151][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes14Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,151)
            histo2D[startF+152][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes15Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,152)
            histo2D[startF+153][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes16Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,153)
            histo2D[startF+154][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes17Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,154)
            histo2D[startF+155][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes18Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,155)
            histo2D[startF+156][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes19Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,156)
            histo2D[startF+157][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes20Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,157)
            histo2D[startF+158][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes21Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,158)
            histo2D[startF+159][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes22Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,159)
            histo2D[startF+160][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes23Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,160)
            histo2D[startF+161][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes24Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,161)
            histo2D[startF+162][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes25Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,162)
            histo2D[startF+163][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes26Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,163)
            histo2D[startF+164][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJes27Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,164)
            histo2D[startF+165][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jetsJerUp"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,165)
            histo2D[startF+166][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,166)
            histo2D[startF+167][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,167)
            histo2D[startF+168][x]    = makeFinalVariable2D(dftop0cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,168)
            if(x == plotCategory("kPlotNonPrompt")):
                startNonPrompt = 18
                histoNonPrompt[0+startNonPrompt] = dftop0cat[x].Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm0")
                histoNonPrompt[1+startNonPrompt] = dftop0cat[x].Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm1")
                histoNonPrompt[2+startNonPrompt] = dftop0cat[x].Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm2")
                histoNonPrompt[3+startNonPrompt] = dftop0cat[x].Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte0")
                histoNonPrompt[4+startNonPrompt] = dftop0cat[x].Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte1")
                histoNonPrompt[5+startNonPrompt] = dftop0cat[x].Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte2")

            startF = 800
            for nv in range(0,135):
                histo2D[startF+nv][x] = makeFinalVariable2D(dftop1cat[x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,nv)
            histo2D[startF+135][x]    = makeFinalVariable2D(dftop1catMuonMomUp      [x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,135)
            histo2D[startF+136][x]    = makeFinalVariable2D(dftop1catElectronMomUp  [x],"ngood_jets","theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,136)
            histo2D[startF+137][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes00Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,137)
            histo2D[startF+138][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes01Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,138)
            histo2D[startF+139][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes02Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,139)
            histo2D[startF+140][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes03Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,140)
            histo2D[startF+141][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes04Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,141)
            histo2D[startF+142][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes05Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,142)
            histo2D[startF+143][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes06Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,143)
            histo2D[startF+144][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes07Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,144)
            histo2D[startF+145][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes08Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,145)
            histo2D[startF+146][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes09Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,146)
            histo2D[startF+147][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes10Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,147)
            histo2D[startF+148][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes11Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,148)
            histo2D[startF+149][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes12Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,149)
            histo2D[startF+150][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes13Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,150)
            histo2D[startF+151][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes14Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,151)
            histo2D[startF+152][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes15Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,152)
            histo2D[startF+153][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes16Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,153)
            histo2D[startF+154][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes17Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,154)
            histo2D[startF+155][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes18Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,155)
            histo2D[startF+156][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes19Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,156)
            histo2D[startF+157][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes20Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,157)
            histo2D[startF+158][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes21Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,158)
            histo2D[startF+159][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes22Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,159)
            histo2D[startF+160][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes23Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,160)
            histo2D[startF+161][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes24Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,161)
            histo2D[startF+162][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes25Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,162)
            histo2D[startF+163][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes26Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,163)
            histo2D[startF+164][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJes27Up"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,164)
            histo2D[startF+165][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jetsJerUp"	    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,165)
            histo2D[startF+166][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,166)
            histo2D[startF+167][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,167)
            histo2D[startF+168][x]    = makeFinalVariable2D(dftop1cat[x],"ngood_jets"		    ,"theGenCat",theCat,startF,x,BinXF,minXF,maxXF,BinYF,minYF,maxYF,168)
            if(x == plotCategory("kPlotNonPrompt")):
                startNonPrompt = 24
                histoNonPrompt[0+startNonPrompt] = dftop1cat[x].Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm0")
                histoNonPrompt[1+startNonPrompt] = dftop1cat[x].Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm1")
                histoNonPrompt[2+startNonPrompt] = dftop1cat[x].Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAltm2")
                histoNonPrompt[3+startNonPrompt] = dftop1cat[x].Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte0")
                histoNonPrompt[4+startNonPrompt] = dftop1cat[x].Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte1")
                histoNonPrompt[5+startNonPrompt] = dftop1cat[x].Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF,minXF,maxXF), "ngood_jets","weightFakeAlte2")

        if(makeDataCards == 2):
            BinXF1 = 20
            minXF1 = 85
            maxXF1 = 385
            varToFit = "mll"
            varMuPtUnc = "MuonMomUp"
            varElPtUnc = "ElectronMomUp"
            altMASS = altMass
            altMET0 = altMass
            altMET1 = altMass
            altMET2 = altMass
            if(whichVarToFit == 1):
                BinXF1 = 20
                minXF1 = 0
                maxXF1 = 200
                varToFit = "ptll"
            elif(whichVarToFit == 2):
                BinXF1 = 20
                minXF1 = 25
                maxXF1 = 225
                varToFit = "ptl1"
            elif(whichVarToFit == 3):
                BinXF1 = 20
                minXF1 = 20
                maxXF1 = 160
                varToFit = "ptl2"
            elif(whichVarToFit == 4):
                BinXF1 = 20
                minXF1 = 0
                maxXF1 = 3.1416
                varToFit = "dphill"
                varMuPtUnc = ""
                varElPtUnc = ""
            elif(whichVarToFit == 5):
                BinXF1 = 20
                minXF1 = 0
                maxXF1 = 200
                varToFit = "thePuppiMET_pt"
                varMuPtUnc = ""
                varElPtUnc = ""
                altMASS = ""
                altMET0 = "JERUp"
                altMET1 = "JESUp"
                altMET2 = "UnclusteredUp"
            elif(whichVarToFit == 6):
                BinXF1 = 10
                minXF1 = 25
                maxXF1 = 55
                varToFit = "ptl1"

            startF = 1000
            for nv in range(0,135):
                histo2D[startF+nv][x] = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jets==0")	,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,nv)
            histo2D[startF+135][x]    = makeFinalVariable2D(dfwwx0catMuonMomUp    [x].Filter("ngood_jets==0"),"{0}{1}".format(varToFit,varMuPtUnc),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,135)
            histo2D[startF+136][x]    = makeFinalVariable2D(dfwwx0catElectronMomUp[x].Filter("ngood_jets==0"),"{0}{1}".format(varToFit,varElPtUnc),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,136)
            histo2D[startF+137][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes00Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,137)
            histo2D[startF+138][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes01Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,138)
            histo2D[startF+139][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes02Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,139)
            histo2D[startF+140][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes03Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,140)
            histo2D[startF+141][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes04Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,141)
            histo2D[startF+142][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes05Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,142)
            histo2D[startF+143][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes06Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,143)
            histo2D[startF+144][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes07Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,144)
            histo2D[startF+145][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes08Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,145)
            histo2D[startF+146][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes09Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,146)
            histo2D[startF+147][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes10Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,147)
            histo2D[startF+148][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes11Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,148)
            histo2D[startF+149][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes12Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,149)
            histo2D[startF+150][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes13Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,150)
            histo2D[startF+151][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes14Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,151)
            histo2D[startF+152][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes15Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,152)
            histo2D[startF+153][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes16Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,153)
            histo2D[startF+154][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes17Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,154)
            histo2D[startF+155][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes18Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,155)
            histo2D[startF+156][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes19Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,156)
            histo2D[startF+157][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes20Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,157)
            histo2D[startF+158][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes21Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,158)
            histo2D[startF+159][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes22Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,159)
            histo2D[startF+160][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes23Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,160)
            histo2D[startF+161][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes24Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,161)
            histo2D[startF+162][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes25Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,162)
            histo2D[startF+163][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes26Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,163)
            histo2D[startF+164][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes27Up==0")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,164)
            histo2D[startF+165][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJerUp==0")	   ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,165)
            histo2D[startF+166][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jets==0")	   ,"{0}{1}".format(varToFit,altMET0),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,166)
            histo2D[startF+167][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jets==0")	   ,"{0}{1}".format(varToFit,altMET1),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,167)
            histo2D[startF+168][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jets==0")	   ,"{0}{1}".format(varToFit,altMET2),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,168)
            if(x == plotCategory("kPlotNonPrompt")):
                startNonPrompt = 30
                histoNonPrompt[0+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets==0").Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAltm0")
                histoNonPrompt[1+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets==0").Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAltm1")
                histoNonPrompt[2+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets==0").Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAltm2")
                histoNonPrompt[3+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets==0").Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAlte0")
                histoNonPrompt[4+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets==0").Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAlte1")
                histoNonPrompt[5+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets==0").Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAlte2")

            startF = 1200
            for nv in range(0,135):
                histo2D[startF+nv][x] = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jets==1")	,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,nv)
            histo2D[startF+135][x]    = makeFinalVariable2D(dfwwx0catMuonMomUp    [x].Filter("ngood_jets==1"),"{0}{1}".format(varToFit,varMuPtUnc),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,135)
            histo2D[startF+136][x]    = makeFinalVariable2D(dfwwx0catElectronMomUp[x].Filter("ngood_jets==1"),"{0}{1}".format(varToFit,varElPtUnc),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,136)
            histo2D[startF+137][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes00Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,137)
            histo2D[startF+138][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes01Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,138)
            histo2D[startF+139][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes02Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,139)
            histo2D[startF+140][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes03Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,140)
            histo2D[startF+141][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes04Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,141)
            histo2D[startF+142][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes05Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,142)
            histo2D[startF+143][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes06Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,143)
            histo2D[startF+144][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes07Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,144)
            histo2D[startF+145][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes08Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,145)
            histo2D[startF+146][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes09Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,146)
            histo2D[startF+147][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes10Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,147)
            histo2D[startF+148][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes11Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,148)
            histo2D[startF+149][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes12Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,149)
            histo2D[startF+150][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes13Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,150)
            histo2D[startF+151][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes14Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,151)
            histo2D[startF+152][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes15Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,152)
            histo2D[startF+153][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes16Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,153)
            histo2D[startF+154][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes17Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,154)
            histo2D[startF+155][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes18Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,155)
            histo2D[startF+156][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes19Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,156)
            histo2D[startF+157][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes20Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,157)
            histo2D[startF+158][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes21Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,158)
            histo2D[startF+159][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes22Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,159)
            histo2D[startF+160][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes23Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,160)
            histo2D[startF+161][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes24Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,161)
            histo2D[startF+162][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes25Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,162)
            histo2D[startF+163][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes26Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,163)
            histo2D[startF+164][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes27Up==1")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,164)
            histo2D[startF+165][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJerUp==1")	   ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,165)
            histo2D[startF+166][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jets==1")	   ,"{0}{1}".format(varToFit,altMET0),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,166)
            histo2D[startF+167][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jets==1")	   ,"{0}{1}".format(varToFit,altMET1),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,167)
            histo2D[startF+168][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jets==1")	   ,"{0}{1}".format(varToFit,altMET2),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,168)
            if(x == plotCategory("kPlotNonPrompt")):
                startNonPrompt = 36
                histoNonPrompt[0+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets==1").Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAltm0")
                histoNonPrompt[1+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets==1").Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAltm1")
                histoNonPrompt[2+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets==1").Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAltm2")
                histoNonPrompt[3+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets==1").Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAlte0")
                histoNonPrompt[4+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets==1").Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAlte1")
                histoNonPrompt[5+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets==1").Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAlte2")

            startF = 1400
            for nv in range(0,135):
                histo2D[startF+nv][x] = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jets>=2")	,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,nv)
            histo2D[startF+135][x]    = makeFinalVariable2D(dfwwx0catMuonMomUp    [x].Filter("ngood_jets>=2"),"{0}{1}".format(varToFit,varMuPtUnc),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,135)
            histo2D[startF+136][x]    = makeFinalVariable2D(dfwwx0catElectronMomUp[x].Filter("ngood_jets>=2"),"{0}{1}".format(varToFit,varElPtUnc),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,136)
            histo2D[startF+137][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes00Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,137)
            histo2D[startF+138][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes01Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,138)
            histo2D[startF+139][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes02Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,139)
            histo2D[startF+140][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes03Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,140)
            histo2D[startF+141][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes04Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,141)
            histo2D[startF+142][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes05Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,142)
            histo2D[startF+143][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes06Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,143)
            histo2D[startF+144][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes07Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,144)
            histo2D[startF+145][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes08Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,145)
            histo2D[startF+146][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes09Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,146)
            histo2D[startF+147][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes10Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,147)
            histo2D[startF+148][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes11Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,148)
            histo2D[startF+149][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes12Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,149)
            histo2D[startF+150][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes13Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,150)
            histo2D[startF+151][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes14Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,151)
            histo2D[startF+152][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes15Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,152)
            histo2D[startF+153][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes16Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,153)
            histo2D[startF+154][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes17Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,154)
            histo2D[startF+155][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes18Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,155)
            histo2D[startF+156][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes19Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,156)
            histo2D[startF+157][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes20Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,157)
            histo2D[startF+158][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes21Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,158)
            histo2D[startF+159][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes22Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,159)
            histo2D[startF+160][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes23Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,160)
            histo2D[startF+161][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes24Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,161)
            histo2D[startF+162][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes25Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,162)
            histo2D[startF+163][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes26Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,163)
            histo2D[startF+164][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJes27Up>=2")    ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,164)
            histo2D[startF+165][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jetsJerUp>=2")	   ,"{0}{1}".format(varToFit,altMASS),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,165)
            histo2D[startF+166][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jets>=2")	   ,"{0}{1}".format(varToFit,altMET0),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,166)
            histo2D[startF+167][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jets>=2")	   ,"{0}{1}".format(varToFit,altMET1),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,167)
            histo2D[startF+168][x]    = makeFinalVariable2D(dfwwx0cat[x].Filter("ngood_jets>=2")	   ,"{0}{1}".format(varToFit,altMET2),"theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,168)
            if(x == plotCategory("kPlotNonPrompt")):
                startNonPrompt = 42
                histoNonPrompt[0+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets>=2").Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAltm0")
                histoNonPrompt[1+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets>=2").Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAltm1")
                histoNonPrompt[2+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets>=2").Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAltm2")
                histoNonPrompt[3+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets>=2").Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAlte0")
                histoNonPrompt[4+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets>=2").Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAlte1")
                histoNonPrompt[5+startNonPrompt] = dfwwx0cat[x].Filter("ngood_jets>=2").Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF1,minXF1,maxXF1), "{0}{1}".format(varToFit,altMASS),"weightFakeAlte2")

    report = []
    for x in range(nCat):
        report.append(dfwwx0cat[x].Report())
        if(x != theCat): continue
        print("---------------- SUMMARY {0} -------------".format(x))
        report[x].Print()

    if(makeDataCards == 1):
        for j in range(0,1000):
            for x in range(nCat):
                histoMVA[j][x] = ROOT.TH1D("histoMVA_{0}_{1}".format(j,x), "histoMVA_{0}_{1}".format(j,x), BinXF,minXF,maxXF)
    elif(makeDataCards == 2):
        for j in range(1000,nHistoMVA):
            for x in range(nCat):
                histoMVA[j][x] = ROOT.TH1D("histoMVA_{0}_{1}".format(j,x), "histoMVA_{0}_{1}".format(j,x), BinXF1,minXF1,maxXF1)

    for j in range(nHistoMVA):
        for x in range(nCat):
            if(histo2D[j][x] == 0):
                histoMVA[j][x] = 0
                continue
            for i in range(histo2D[j][x].GetNbinsX()):
                histo2D[j][x].SetBinContent(i+1,histo2D[j][x].GetNbinsY(),histo2D[j][x].GetBinContent(i+1,histo2D[j][x].GetNbinsY())+histo2D[j][x].GetBinContent(i+1,histo2D[j][x].GetNbinsY()+1))
                histo2D[j][x].SetBinError  (i+1,histo2D[j][x].GetNbinsY(),pow(pow(histo2D[j][x].GetBinError(i+1,histo2D[j][x].GetNbinsY()),2)+pow(histo2D[j][x].GetBinError(i+1,histo2D[j][x].GetNbinsY()+1),2),0.5))
                histo2D[j][x].SetBinContent(i+1,histo2D[j][x].GetNbinsY()+1,0.0)
                histo2D[j][x].SetBinError  (i+1,histo2D[j][x].GetNbinsY()+1,0.0)

            for i in range(histo2D[j][x].GetNbinsY()):
                histo2D[j][x].SetBinContent(histo2D[j][x].GetNbinsX(),i+1,histo2D[j][x].GetBinContent(histo2D[j][x].GetNbinsX(),i+1)+histo2D[j][x].GetBinContent(histo2D[j][x].GetNbinsX()+1,i+1))
                histo2D[j][x].SetBinError  (histo2D[j][x].GetNbinsX(),i+1,pow(pow(histo2D[j][x].GetBinError(histo2D[j][x].GetNbinsX(),i+1),2)+pow(histo2D[j][x].GetBinError(histo2D[j][x].GetNbinsX()+1,i+1),2),0.5))
                histo2D[j][x].SetBinContent(histo2D[j][x].GetNbinsX()+1,i+1,0.0)
                histo2D[j][x].SetBinError  (histo2D[j][x].GetNbinsX()+1,i+1,0.0)

            if(x == plotCategory("kPlotqqWW")):
                for i in range(histoMVA[j][x].GetNbinsX()):
                    histoMVA[j][plotCategory("kPlotqqWW")].SetBinContent(i+1,histoMVA[j][plotCategory("kPlotqqWW")].GetBinContent(i+1)+histo2D[j][x].GetBinContent(i+1,1))
                    histoMVA[j][plotCategory("kPlotqqWW")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotqqWW")].GetBinError(i+1),2)+pow(histo2D[j][x].GetBinError(i+1,1),2),0.5))

                    histoMVA[j][plotCategory("kPlotSignal0")].SetBinContent(i+1,histoMVA[j][plotCategory("kPlotSignal0")].GetBinContent(i+1)+histo2D[j][x].GetBinContent(i+1,2))
                    histoMVA[j][plotCategory("kPlotSignal0")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotSignal0")].GetBinError(i+1),2)+pow(histo2D[j][x].GetBinError(i+1,2),2),0.5))

                    histoMVA[j][plotCategory("kPlotSignal1")].SetBinContent(i+1,histoMVA[j][plotCategory("kPlotSignal1")].GetBinContent(i+1)+histo2D[j][x].GetBinContent(i+1,3))
                    histoMVA[j][plotCategory("kPlotSignal1")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotSignal1")].GetBinError(i+1),2)+pow(histo2D[j][x].GetBinError(i+1,3),2),0.5))

                    histoMVA[j][plotCategory("kPlotSignal2")].SetBinContent(i+1,histoMVA[j][plotCategory("kPlotSignal2")].GetBinContent(i+1)+histo2D[j][x].GetBinContent(i+1,4))
                    histoMVA[j][plotCategory("kPlotSignal2")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotSignal2")].GetBinError(i+1),2)+pow(histo2D[j][x].GetBinError(i+1,4),2),0.5))

            elif(x == plotCategory("kPlotggWW")):
                for i in range(histoMVA[j][x].GetNbinsX()):
                    histoMVA[j][plotCategory("kPlotqqWW")].SetBinContent(i+1,histoMVA[j][plotCategory("kPlotqqWW")].GetBinContent(i+1)+histo2D[j][x].GetBinContent(i+1,1))
                    histoMVA[j][plotCategory("kPlotqqWW")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotqqWW")].GetBinError(i+1),2)+pow(histo2D[j][x].GetBinError(i+1,1),2),0.5))

                    histoMVA[j][plotCategory("kPlotSignal3")].SetBinContent(i+1,histoMVA[j][plotCategory("kPlotSignal3")].GetBinContent(i+1)+histo2D[j][x].GetBinContent(i+1,2))
                    histoMVA[j][plotCategory("kPlotSignal3")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotSignal3")].GetBinError(i+1),2)+pow(histo2D[j][x].GetBinError(i+1,2),2),0.5))

                    histoMVA[j][plotCategory("kPlotSignal4")].SetBinContent(i+1,histoMVA[j][plotCategory("kPlotSignal4")].GetBinContent(i+1)+histo2D[j][x].GetBinContent(i+1,3))
                    histoMVA[j][plotCategory("kPlotSignal4")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotSignal4")].GetBinError(i+1),2)+pow(histo2D[j][x].GetBinError(i+1,3),2),0.5))

                    histoMVA[j][plotCategory("kPlotSignal5")].SetBinContent(i+1,histoMVA[j][plotCategory("kPlotSignal5")].GetBinContent(i+1)+histo2D[j][x].GetBinContent(i+1,4))
                    histoMVA[j][plotCategory("kPlotSignal5")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotSignal5")].GetBinError(i+1),2)+pow(histo2D[j][x].GetBinError(i+1,4),2),0.5))

            else:
                for i in range(histoMVA[j][x].GetNbinsX()):
                    histoMVA[j][x].SetBinContent(i+1,histoMVA[j][x].GetBinContent(i+1)+histo2D[j][x].GetBinContent(i+1,1))
                    histoMVA[j][x].SetBinError  (i+1,pow(pow(histoMVA[j][x].GetBinError(i+1),2)+pow(histo2D[j][x].GetBinError(i+1,1),2),0.5))

    myfile = ROOT.TFile("fillhisto_wwAnalysis_sample{0}_year{1}_job{2}.root".format(count,year,whichJob),'RECREATE')
    for i in range(nCat):
        for j in range(nHisto):
            if(histo[j][i] == 0): continue
            histo[j][i].Write()
        for j in range(nHistoMVA):
            if(histoMVA[j][i] == 0): continue
            histoMVA[j][i].Write()
    for i in range(nhistoNonPrompt):
        if(histoNonPrompt[i] == 0): continue
        histoNonPrompt[i].Write()
    myfile.Close()

def readMCSample(sampleNOW,year,skimType,whichJob,group,puWeights,histoTriggerDAEtaPt,histoTriggerMCEtaPt,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3):

    files = getMClist(sampleNOW, skimType)
    print("Total files: {0}".format(len(files)))

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

    print("Number of Theory replicas: {0} / {1} / {2}".format(nTheoryReplicas[0],nTheoryReplicas[1],nTheoryReplicas[2]))

    genEventSumLHEScaleRenorm = [1, 1, 1, 1, 1, 1]
    genEventSumPSRenorm = [1, 1, 1, 1]
    if(SwitchSample(sampleNOW,skimType)[2] == plotCategory("kPlotqqWW") or
       SwitchSample(sampleNOW,skimType)[2] == plotCategory("kPlotggWW") or
       SwitchSample(sampleNOW,skimType)[2] == plotCategory("kPlotTT") or
       SwitchSample(sampleNOW,skimType)[2] == plotCategory("kPlotTW") or
       SwitchSample(sampleNOW,skimType)[2] == plotCategory("kPlotDY") or
       SwitchSample(sampleNOW,skimType)[2] == plotCategory("kPlotWZ") or
       SwitchSample(sampleNOW,skimType)[2] == plotCategory("kPlotEWKWZ") or
       SwitchSample(sampleNOW,skimType)[2] == plotCategory("kPlotZZ")):
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

    df = ROOT.RDataFrame("Events", files)
    nevents = df.Count().GetValue()

    print("genEventSum({0}): {1} / Events(total/ntuple): {2} / {3}".format(runGetEntries,genEventSumWeight,genEventSumNoWeight,nevents))
    print("WeightExact/Approx %f / %f / Cross section: %f" %(weight, weightApprox, SwitchSample(sampleNOW, skimType)[1]))

    PDType = os.path.basename(SwitchSample(sampleNOW, skimType)[0]).split('+')[0]

    analysis(df,sampleNOW,SwitchSample(sampleNOW,skimType)[2],weight,year,PDType,"false",whichJob,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,puWeights,histoTriggerDAEtaPt,histoTriggerMCEtaPt,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3)

def readDASample(sampleNOW,year,skimType,whichJob,group,puWeights,histoTriggerDAEtaPt,histoTriggerMCEtaPt,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3):

    PDType = "0"
    if  (sampleNOW >= 1000 and sampleNOW <= 1009): PDType = "SingleMuon"
    elif(sampleNOW >= 1010 and sampleNOW <= 1019): PDType = "DoubleMuon"
    elif(sampleNOW >= 1020 and sampleNOW <= 1029): PDType = "MuonEG"
    elif(sampleNOW >= 1030 and sampleNOW <= 1039): PDType = "EGamma"
    elif(sampleNOW >= 1040 and sampleNOW <= 1049): PDType = "Muon"
    elif(sampleNOW >= 1050 and sampleNOW <= 1059): PDType = "MET"

    files = getDATAlist(sampleNOW, year, skimType)
    print("Total files: {0}".format(len(files)))

    if(whichJob != -1):
        groupedFile = groupFiles(files, group)
        files = groupedFile[whichJob]
        if(len(files) == 0):
            print("no files in job/group: {0} / {1}".format(whichJob, group))
            return 0
        print("Used files: {0}".format(len(files)))

    df = ROOT.RDataFrame("Events", files)

    genEventSumLHEScaleRenorm = [1, 1, 1, 1, 1, 1]
    genEventSumPSRenorm = [1, 1, 1, 1]

    weight=1.
    nevents = df.Count().GetValue()
    print("%s entries in the dataset" %nevents)

    analysis(df,sampleNOW,sampleNOW,weight,year,PDType,"true",whichJob,0,genEventSumLHEScaleRenorm,genEventSumPSRenorm,puWeights,histoTriggerDAEtaPt,histoTriggerMCEtaPt,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3)

if __name__ == "__main__":

    group = 5

    skimType = "2l"
    year = 2022
    process = -1
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

    histoFakeEtaPt_mu = []
    histoFakeEtaPt_el = []
    fakePath = "data/histoFakeEtaPt_{0}.root".format(year)
    fFakeFile = ROOT.TFile(fakePath)
    histoFakeEtaPt_mu.append(fFakeFile.Get("histoFakeEffSelEtaPt_0_{0}_fakeAnalysis1001_anaType1".format(muSelChoice)))
    histoFakeEtaPt_mu.append(fFakeFile.Get("histoFakeEffSelEtaPt_0_{0}_fakeAnalysis1002_anaType1".format(muSelChoice)))
    histoFakeEtaPt_mu.append(fFakeFile.Get("histoFakeEffSelEtaPt_0_{0}_fakeAnalysis1003_anaType1".format(muSelChoice)))
    histoFakeEtaPt_mu.append(fFakeFile.Get("histoFakeEffSelEtaPt_0_{0}_fakeAnalysis1001_anaType2".format(muSelChoice)))
    histoFakeEtaPt_mu.append(fFakeFile.Get("histoFakeEffSelEtaPt_0_{0}_fakeAnalysis1002_anaType2".format(muSelChoice)))
    histoFakeEtaPt_mu.append(fFakeFile.Get("histoFakeEffSelEtaPt_0_{0}_fakeAnalysis1003_anaType2".format(muSelChoice)))
    histoFakeEtaPt_mu.append(fFakeFile.Get("histoFakeEffSelEtaPt_0_{0}_fakeAnalysis1001_anaType3".format(muSelChoice)))
    histoFakeEtaPt_mu.append(fFakeFile.Get("histoFakeEffSelEtaPt_0_{0}_fakeAnalysis1002_anaType3".format(muSelChoice)))
    histoFakeEtaPt_mu.append(fFakeFile.Get("histoFakeEffSelEtaPt_0_{0}_fakeAnalysis1003_anaType3".format(muSelChoice)))
    histoFakeEtaPt_el.append(fFakeFile.Get("histoFakeEffSelEtaPt_1_{0}_fakeAnalysis1001_anaType1".format(elSelChoice)))
    histoFakeEtaPt_el.append(fFakeFile.Get("histoFakeEffSelEtaPt_1_{0}_fakeAnalysis1002_anaType1".format(elSelChoice)))
    histoFakeEtaPt_el.append(fFakeFile.Get("histoFakeEffSelEtaPt_1_{0}_fakeAnalysis1003_anaType1".format(elSelChoice)))
    histoFakeEtaPt_el.append(fFakeFile.Get("histoFakeEffSelEtaPt_1_{0}_fakeAnalysis1001_anaType2".format(elSelChoice)))
    histoFakeEtaPt_el.append(fFakeFile.Get("histoFakeEffSelEtaPt_1_{0}_fakeAnalysis1002_anaType2".format(elSelChoice)))
    histoFakeEtaPt_el.append(fFakeFile.Get("histoFakeEffSelEtaPt_1_{0}_fakeAnalysis1003_anaType2".format(elSelChoice)))
    histoFakeEtaPt_el.append(fFakeFile.Get("histoFakeEffSelEtaPt_1_{0}_fakeAnalysis1001_anaType3".format(elSelChoice)))
    histoFakeEtaPt_el.append(fFakeFile.Get("histoFakeEffSelEtaPt_1_{0}_fakeAnalysis1002_anaType3".format(elSelChoice)))
    histoFakeEtaPt_el.append(fFakeFile.Get("histoFakeEffSelEtaPt_1_{0}_fakeAnalysis1003_anaType3".format(elSelChoice)))
    for x in range(9):
        histoFakeEtaPt_mu[x].SetDirectory(0)
        histoFakeEtaPt_el[x].SetDirectory(0)
    fFakeFile.Close()

    lepSFPath = "data/histoLepSFEtaPt_{0}{1}.root".format(year,correctionString)
    fLepSFFile = ROOT.TFile(lepSFPath)
    histoLepSFEtaPt_mu = fLepSFFile.Get("histoLepSFEtaPt_0_{0}".format(muSelChoice))
    histoLepSFEtaPt_el = fLepSFFile.Get("histoLepSFEtaPt_1_{0}".format(elSelChoice))
    histoLepSFEtaPt_mu.SetDirectory(0)
    histoLepSFEtaPt_el.SetDirectory(0)
    fLepSFFile.Close()

    triggerSFPath = "data/histoTriggerSFEtaPt_{0}.root".format(year)
    fTriggerSFFile = ROOT.TFile(triggerSFPath)
    histoTriggerSFEtaPt_0_0 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_0_0")
    histoTriggerSFEtaPt_0_1 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_0_1")
    histoTriggerSFEtaPt_0_2 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_0_2")
    histoTriggerSFEtaPt_0_3 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_0_3")
    histoTriggerSFEtaPt_1_0 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_1_0")
    histoTriggerSFEtaPt_1_1 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_1_1")
    histoTriggerSFEtaPt_1_2 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_1_2")
    histoTriggerSFEtaPt_1_3 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_1_3")
    histoTriggerSFEtaPt_2_0 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_2_0")
    histoTriggerSFEtaPt_2_1 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_2_1")
    histoTriggerSFEtaPt_2_2 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_2_2")
    histoTriggerSFEtaPt_2_3 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_2_3")
    histoTriggerSFEtaPt_3_0 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_3_0")
    histoTriggerSFEtaPt_3_1 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_3_1")
    histoTriggerSFEtaPt_3_2 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_3_2")
    histoTriggerSFEtaPt_3_3 = fTriggerSFFile.Get("histoTriggerV1SFEtaPt_3_3")
    histoTriggerSFEtaPt_0_0.SetDirectory(0)
    histoTriggerSFEtaPt_0_1.SetDirectory(0)
    histoTriggerSFEtaPt_0_2.SetDirectory(0)
    histoTriggerSFEtaPt_0_3.SetDirectory(0)
    histoTriggerSFEtaPt_1_0.SetDirectory(0)
    histoTriggerSFEtaPt_1_1.SetDirectory(0)
    histoTriggerSFEtaPt_1_2.SetDirectory(0)
    histoTriggerSFEtaPt_1_3.SetDirectory(0)
    histoTriggerSFEtaPt_2_0.SetDirectory(0)
    histoTriggerSFEtaPt_2_1.SetDirectory(0)
    histoTriggerSFEtaPt_2_2.SetDirectory(0)
    histoTriggerSFEtaPt_2_3.SetDirectory(0)
    histoTriggerSFEtaPt_3_0.SetDirectory(0)
    histoTriggerSFEtaPt_3_1.SetDirectory(0)
    histoTriggerSFEtaPt_3_2.SetDirectory(0)
    histoTriggerSFEtaPt_3_3.SetDirectory(0)
    fTriggerSFFile.Close()

    BTVEffPath = "data/histoBtagEffSelEtaPt_{0}.root".format(year)
    fBTVEffPathFile = ROOT.TFile(BTVEffPath)
    histoBTVEffEtaPtLF = fBTVEffPathFile.Get("histoBtagEffSelEtaPt_{0}".format(0+3*bTagSel))
    histoBTVEffEtaPtCJ = fBTVEffPathFile.Get("histoBtagEffSelEtaPt_{0}".format(1+3*bTagSel))
    histoBTVEffEtaPtBJ = fBTVEffPathFile.Get("histoBtagEffSelEtaPt_{0}".format(2+3*bTagSel))
    histoBTVEffEtaPtLF.SetDirectory(0)
    histoBTVEffEtaPtCJ.SetDirectory(0)
    histoBTVEffEtaPtBJ.SetDirectory(0)
    fBTVEffPathFile.Close()

    histoTriggerDAEtaPt = []
    histoTriggerMCEtaPt = []
    triggerDataPath = "data/histoTriggerForSingleLegs.root"
    fTriggerDataPathFile = ROOT.TFile(triggerDataPath)
    histoTriggerDAEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_da_sel".format(year)))
    histoTriggerDAEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_da_smu".format(year)))
    histoTriggerDAEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_da_del0".format(year)))
    histoTriggerDAEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_da_del1".format(year)))
    histoTriggerDAEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_da_dmu0".format(year)))
    histoTriggerDAEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_da_dmu1".format(year)))
    histoTriggerDAEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_da_emu0".format(year)))
    histoTriggerDAEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_da_emu1".format(year)))
    histoTriggerDAEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_da_mue0".format(year)))
    histoTriggerDAEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_da_mue1".format(year)))
    histoTriggerMCEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_mc_sel".format(year)))
    histoTriggerMCEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_mc_smu".format(year)))
    histoTriggerMCEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_mc_del0".format(year)))
    histoTriggerMCEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_mc_del1".format(year)))
    histoTriggerMCEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_mc_dmu0".format(year)))
    histoTriggerMCEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_mc_dmu1".format(year)))
    histoTriggerMCEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_mc_emu0".format(year)))
    histoTriggerMCEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_mc_emu1".format(year)))
    histoTriggerMCEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_mc_mue0".format(year)))
    histoTriggerMCEtaPt.append(fTriggerDataPathFile.Get("triggerEff_{0}_mc_mue1".format(year)))
    for x in range(10):
        histoTriggerDAEtaPt[x].SetDirectory(0)
        histoTriggerMCEtaPt[x].SetDirectory(0)
    fTriggerDataPathFile.Close()

    try:
        if(process >= 0 and process < 1000):
            readMCSample(process,year,skimType,whichJob,group,puWeights,histoTriggerDAEtaPt,histoTriggerMCEtaPt,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3)
        elif(process >= 1000):
            readDASample(process,year,skimType,whichJob,group,puWeights,histoTriggerDAEtaPt,histoTriggerMCEtaPt,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3)
    except Exception as e:
        print("FAILED {0}".format(e))
