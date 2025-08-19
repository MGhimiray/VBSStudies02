import ROOT
import os, sys, getopt, json, time

ROOT.ROOT.EnableImplicitMT(4)
from utilsCategory import plotCategory
from utilsAna import getMClist, getDATAlist
from utilsAna import SwitchSample, groupFiles, getTriggerFromJson, getLeptomSelFromJson, getLumi
from utilsSelection import selectionTauVeto, selectionPhoton, selectionJetMet, selection4LVar, selectionTrigger2L, selectionElMu, selectionWeigths, selectionGenLepJet, makeFinalVariable
from utilsMVA import redefineMVAVariables
import tmva_helper_xml

makeDataCards = 2 # 1 (njets), 2 (lepton flavor), 3 (mjj)

correctionString = "_correction"

doNtuples = False
# 0 = T, 1 = M, 2 = L
bTagSel = 0
useBTaggingWeights = 1

useFR = 0

altMass = "Def"

jetEtaCut = 2.5
if(makeDataCards >= 3): jetEtaCut = 4.9

selectionJsonPath = "config/selection.json"
if(not os.path.exists(selectionJsonPath)):
    selectionJsonPath = "selection.json"

with open(selectionJsonPath) as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

JSON = jsonObject['JSON']

BARRELphotons = jsonObject['BARRELphotons']
ENDCAPphotons = jsonObject['ENDCAPphotons']

VBSSEL = jsonObject['VBSSEL']

muSelChoice = 0
MUOWP = "Medium"

elSelChoice = 0
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

def selectionLL(df,year,PDType,isData,count):

    overallTriggers = jsonObject['triggers']
    TRIGGERMUEG = getTriggerFromJson(overallTriggers, "TRIGGERMUEG", year)
    TRIGGERDMU  = getTriggerFromJson(overallTriggers, "TRIGGERDMU", year)
    TRIGGERSMU  = getTriggerFromJson(overallTriggers, "TRIGGERSMU", year)
    TRIGGERDEL  = getTriggerFromJson(overallTriggers, "TRIGGERDEL", year)
    TRIGGERSEL  = getTriggerFromJson(overallTriggers, "TRIGGERSEL", year)

    dftag = selectionTrigger2L(df,year,PDType,JSON,isData,TRIGGERSEL,TRIGGERDEL,TRIGGERSMU,TRIGGERDMU,TRIGGERMUEG)

    overallLeptonSel = jsonObject['leptonSel']
    FAKE_MU   = getLeptomSelFromJson(overallLeptonSel, "FAKE_MU",   year)
    TIGHT_MU  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU{0}".format(muSelChoice),  year, 1)
    TIGHT_MU_TIGHT  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU{0}".format(5),  year)

    FAKE_EL   = getLeptomSelFromJson(overallLeptonSel, "FAKE_EL",   year)
    TIGHT_EL  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL{0}".format(elSelChoice),  year, 1)
    TIGHT_EL_TIGHT  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL{0}".format(4),  year, 1)

    dftag = selectionElMu(dftag,year,FAKE_MU,TIGHT_MU,FAKE_EL,TIGHT_EL)

    dftag =(dftag.Filter("nLoose == 4","Only four loose leptons")
                 .Filter("nFake == 4","Four fake leptons")
                 .Filter("abs(Sum(fake_Muon_charge)+Sum(fake_Electron_charge)) == 0", "0 net charge")
                 .Define("vtight_mu","{0}".format(TIGHT_MU_TIGHT))
                 .Define("vtight_el","{0}".format(TIGHT_EL_TIGHT))
                 .Define("eventNum", "event")
                 .Define("ptl1","30.0f")
                 .Define("ptl2","30.0f")
                 .Define("etal1","1.0f")
                 .Define("etal2","1.0f")
                 )

    if(useFR == 0):
        dftag = dftag.Filter("nTight == 4","Four tight leptons")

    dftag = selectionTauVeto(dftag,year,isData)
    dftag = selectionPhoton (dftag,year,BARRELphotons,ENDCAPphotons)
    dftag = selectionJetMet (dftag,year,bTagSel,isData,count,jetEtaCut)
    dftag = selection4LVar  (dftag,year,isData)

    dftag = (dftag.Filter("ptlmax{0} > 25".format(altMass), "ptlmax > 25")
            )
    return dftag


def analysis(df,count,category,weight,year,PDType,isData,whichJob,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3):

    print("starting {0} / {1} / {2} / {3} / {4} / {5} / {6}".format(count,category,weight,year,PDType,isData,whichJob))

    theCat = category
    if(theCat > 100): theCat = plotCategory("kPlotData")

    nCat, nHisto = plotCategory("kPlotCategories"), 500
    histo    = [[0 for y in range(nCat)] for x in range(nHisto)]

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
    ROOT.initHisto1D(puWeights[0],0)
    ROOT.initHisto1D(puWeights[1],1)
    ROOT.initHisto1D(puWeights[2],2)

    ROOT.initJSONSFs(year)

    branchList = ROOT.vector('string')()
    for branchName in [
            "eventNum",
            "weight",
            "theCat",
            "ngood_jets",
            "vbs_mjj",
            "vbs_ptjj",
            "vbs_detajj",
            "vbs_dphijj",
            "vbs_ptj1",
            "vbs_ptj2",
            "vbs_etaj1",
            "vbs_etaj2",
            "vbs_zepvv",
            "vbs_zepmax",
            "vbs_sumHT",
            "vbs_ptvv",
            "vbs_pttot",
            "vbs_detavvj1",
            "vbs_detavvj2",
            "vbs_ptbalance"
    ]:
        branchList.push_back(branchName)

    MVAweights = "weights_mva/bdt_BDTG_vbfinc_v0.weights.xml"
    tmva_helper = tmva_helper_xml.TMVAHelperXML(MVAweights)
    print(tmva_helper.variables)

    dftag = selectionLL(df,year,PDType,isData,count)

    if(isData == "false"):
        dftag = selectionGenLepJet(dftag,20,30,5.0)
        dftag = (dftag.Define("mjjGen", "compute_vbs_gen_variables(0,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass)")
                      )
    else:
        dftag = (dftag.Define("mjjGen", "{0}".format(0))
                      )

    dfbase = selectionWeigths(dftag,isData,year,PDType,weight,useFR,bTagSel,useBTaggingWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,MUOWP,ELEWP,correctionString,0)

    dfbase = (dfbase.Define("kPlotNonPrompt", "{0}".format(plotCategory("kPlotNonPrompt")))
                    .Define("kPlotWS", "{0}".format(plotCategory("kPlotWS")))
                    .Define("theCat","compute_category({0},kPlotNonPrompt,kPlotWS,nFake,nTight,0)".format(theCat))
                    )

    dfbase = tmva_helper.run_inference(dfbase,"bdt_vbfinc",0)

    dfzzcat = []
    dfzzxycat = []
    dfzzjjcat = []
    dfzzvbscat = []

    dfzzcatMuonMomUp       = []
    dfzzcatElectronMomUp   = []
    dfzzcatJes00Up         = []
    dfzzcatJes01Up         = []
    dfzzcatJes02Up         = []
    dfzzcatJes03Up         = []
    dfzzcatJes04Up         = []
    dfzzcatJes05Up         = []
    dfzzcatJes06Up         = []
    dfzzcatJes07Up         = []
    dfzzcatJes08Up         = []
    dfzzcatJes09Up         = []
    dfzzcatJes10Up         = []
    dfzzcatJes11Up         = []
    dfzzcatJes12Up         = []
    dfzzcatJes13Up         = []
    dfzzcatJes14Up         = []
    dfzzcatJes15Up         = []
    dfzzcatJes16Up         = []
    dfzzcatJes17Up         = []
    dfzzcatJes18Up         = []
    dfzzcatJes19Up         = []
    dfzzcatJes20Up         = []
    dfzzcatJes21Up         = []
    dfzzcatJes22Up         = []
    dfzzcatJes23Up         = []
    dfzzcatJes24Up         = []
    dfzzcatJes25Up         = []
    dfzzcatJes26Up         = []
    dfzzcatJes27Up         = []
    dfzzcatJerUp           = []
    dfzzcatJERUp           = []
    dfzzcatJESUp           = []
    dfzzcatUnclusteredUp   = []
    for x in range(nCat):
        dfzzcat.append(dfbase.Filter("theCat=={0}".format(x), "correct category ({0})".format(x)))

        histo[ 0][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format( 0,x), "histo_{0}_{1}".format( 0,x),120,  0, 120), "mllmin{0}".format(altMass),"weight")
        dfzzcat[x] = dfzzcat[x].Filter("mllmin{0} > 5".format(altMass),"mllmin cut")

        histo[21][x] = dfzzcat[x].Filter("mllZ1 == -1 && Sum(vtight_mu)+Sum(vtight_el) == 4").Histo1D(("histo_{0}_{1}".format(21,x), "histo_{0}_{1}".format(21,x),3,-0.5, 2.5), "FourLepton_flavor","weight")
        histo[22][x] = dfzzcat[x].Filter("mllZ1 == -1 && Sum(vtight_mu)+Sum(vtight_el) == 4").Histo1D(("histo_{0}_{1}".format(22,x), "histo_{0}_{1}".format(22,x),10, 0, 500), "m4l","weight")
        histo[23][x] = dfzzcat[x].Filter("mllZ1 == -1 && Sum(vtight_mu)+Sum(vtight_el) == 4").Histo1D(("histo_{0}_{1}".format(23,x), "histo_{0}_{1}".format(23,x),5,-0.5 ,4.5), "nbtag_goodbtag_Jet_bjet","weightBTag")

        histo[ 1][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format( 1,x), "histo_{0}_{1}".format( 1,x),100,  0, 100), "mllZ1{0}".format(altMass),"weight")
        dfzzcat[x] = dfzzcat[x].Filter("mllZ1{0} < 10000 && mllZ1{0} > 0".format(altMass),"mllZ1 cut")

        dfzzxycat.append(dfzzcat[x].Filter("mllxy{0} > 0 && Sum(vtight_mu)+Sum(vtight_el) == 4 && mllZ1{0} < 15".format(altMass)))

        histo[ 2][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format( 2,x), "histo_{0}_{1}".format( 2,x),100,  0, 100), "mllZ2{0}".format(altMass),"weight")
        dfzzcat[x] = dfzzcat[x].Filter("mllZ2{0} < 10000".format(altMass),"mllZ2 cut")

        dfzzcatMuonMomUp    .append(dfzzcat[x])
        dfzzcatElectronMomUp.append(dfzzcat[x])
        dfzzcatJes00Up      .append(dfzzcat[x])
        dfzzcatJes01Up      .append(dfzzcat[x])
        dfzzcatJes02Up      .append(dfzzcat[x])
        dfzzcatJes03Up      .append(dfzzcat[x])
        dfzzcatJes04Up      .append(dfzzcat[x])
        dfzzcatJes05Up      .append(dfzzcat[x])
        dfzzcatJes06Up      .append(dfzzcat[x])
        dfzzcatJes07Up      .append(dfzzcat[x])
        dfzzcatJes08Up      .append(dfzzcat[x])
        dfzzcatJes09Up      .append(dfzzcat[x])
        dfzzcatJes10Up      .append(dfzzcat[x])
        dfzzcatJes11Up      .append(dfzzcat[x])
        dfzzcatJes12Up      .append(dfzzcat[x])
        dfzzcatJes13Up      .append(dfzzcat[x])
        dfzzcatJes14Up      .append(dfzzcat[x])
        dfzzcatJes15Up      .append(dfzzcat[x])
        dfzzcatJes16Up      .append(dfzzcat[x])
        dfzzcatJes17Up      .append(dfzzcat[x])
        dfzzcatJes18Up      .append(dfzzcat[x])
        dfzzcatJes19Up      .append(dfzzcat[x])
        dfzzcatJes20Up      .append(dfzzcat[x])
        dfzzcatJes21Up      .append(dfzzcat[x])
        dfzzcatJes22Up      .append(dfzzcat[x])
        dfzzcatJes23Up      .append(dfzzcat[x])
        dfzzcatJes24Up      .append(dfzzcat[x])
        dfzzcatJes25Up      .append(dfzzcat[x])
        dfzzcatJes26Up      .append(dfzzcat[x])
        dfzzcatJes27Up      .append(dfzzcat[x])
        dfzzcatJerUp        .append(dfzzcat[x])
        dfzzcatJERUp        .append(dfzzcat[x])
        dfzzcatJESUp        .append(dfzzcat[x])
        dfzzcatUnclusteredUp.append(dfzzcat[x])
        dfzzcat             [x] = dfzzcat              [x].Filter("nbtag_goodbtag_Jet_bjet        == 0 && m4l{0}           > 150".format(altMass)," nbjets == 0 && m4l > 150")
        dfzzcatMuonMomUp    [x] = dfzzcatMuonMomUp     [x].Filter("nbtag_goodbtag_Jet_bjet        == 0 && m4lMuonMomUp     > 150")
        dfzzcatElectronMomUp[x] = dfzzcatElectronMomUp [x].Filter("nbtag_goodbtag_Jet_bjet        == 0 && m4lElectronMomUp > 150")
        dfzzcatJes00Up      [x] = dfzzcatJes00Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes00Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes01Up      [x] = dfzzcatJes01Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes01Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes02Up      [x] = dfzzcatJes02Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes02Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes03Up      [x] = dfzzcatJes03Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes03Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes04Up      [x] = dfzzcatJes04Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes04Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes05Up      [x] = dfzzcatJes05Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes05Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes06Up      [x] = dfzzcatJes06Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes06Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes07Up      [x] = dfzzcatJes07Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes07Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes08Up      [x] = dfzzcatJes08Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes08Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes09Up      [x] = dfzzcatJes09Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes09Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes10Up      [x] = dfzzcatJes10Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes10Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes11Up      [x] = dfzzcatJes11Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes11Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes12Up      [x] = dfzzcatJes12Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes12Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes13Up      [x] = dfzzcatJes13Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes13Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes14Up      [x] = dfzzcatJes14Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes14Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes15Up      [x] = dfzzcatJes15Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes15Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes16Up      [x] = dfzzcatJes16Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes16Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes17Up      [x] = dfzzcatJes17Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes17Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes18Up      [x] = dfzzcatJes18Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes18Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes19Up      [x] = dfzzcatJes19Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes19Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes20Up      [x] = dfzzcatJes20Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes20Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes21Up      [x] = dfzzcatJes21Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes21Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes22Up      [x] = dfzzcatJes22Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes22Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes23Up      [x] = dfzzcatJes23Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes23Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes24Up      [x] = dfzzcatJes24Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes24Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes25Up      [x] = dfzzcatJes25Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes25Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes26Up      [x] = dfzzcatJes26Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes26Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJes27Up      [x] = dfzzcatJes27Up       [x].Filter("nbtag_goodbtag_Jet_bjetJes27Up == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJerUp        [x] = dfzzcatJerUp         [x].Filter("nbtag_goodbtag_Jet_bjetJerUp   == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJERUp        [x] = dfzzcatJERUp         [x].Filter("nbtag_goodbtag_Jet_bjet        == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatJESUp        [x] = dfzzcatJESUp         [x].Filter("nbtag_goodbtag_Jet_bjet        == 0 && m4l{0}           > 150".format(altMass))
        dfzzcatUnclusteredUp[x] = dfzzcatUnclusteredUp [x].Filter("nbtag_goodbtag_Jet_bjet        == 0 && m4l{0}           > 150".format(altMass))

        if(makeDataCards == 3):
            dfzzcat[x] = dfzzcat[x].Filter("nvbs_jets >= 2 && vbs_mjj > 150")
            dfzzcatMuonMomUp    [x] = dfzzcatMuonMomUp     [x].Filter("nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0")
            dfzzcatElectronMomUp[x] = dfzzcatElectronMomUp [x].Filter("nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0")
            dfzzcatJes00Up      [x] = dfzzcatJes00Up       [x].Filter("nvbs_jetsJes00Up >= 2 && vbs_mjjJes00Up > 500 && vbs_detajjJes00Up > 2.5 && vbs_zepvvJes00Up < 1.0")
            dfzzcatJes01Up      [x] = dfzzcatJes01Up       [x].Filter("nvbs_jetsJes01Up >= 2 && vbs_mjjJes01Up > 500 && vbs_detajjJes01Up > 2.5 && vbs_zepvvJes01Up < 1.0")
            dfzzcatJes02Up      [x] = dfzzcatJes02Up       [x].Filter("nvbs_jetsJes02Up >= 2 && vbs_mjjJes02Up > 500 && vbs_detajjJes02Up > 2.5 && vbs_zepvvJes02Up < 1.0")
            dfzzcatJes03Up      [x] = dfzzcatJes03Up       [x].Filter("nvbs_jetsJes03Up >= 2 && vbs_mjjJes03Up > 500 && vbs_detajjJes03Up > 2.5 && vbs_zepvvJes03Up < 1.0")
            dfzzcatJes04Up      [x] = dfzzcatJes04Up       [x].Filter("nvbs_jetsJes04Up >= 2 && vbs_mjjJes04Up > 500 && vbs_detajjJes04Up > 2.5 && vbs_zepvvJes04Up < 1.0")
            dfzzcatJes05Up      [x] = dfzzcatJes05Up       [x].Filter("nvbs_jetsJes05Up >= 2 && vbs_mjjJes05Up > 500 && vbs_detajjJes05Up > 2.5 && vbs_zepvvJes05Up < 1.0")
            dfzzcatJes06Up      [x] = dfzzcatJes06Up       [x].Filter("nvbs_jetsJes06Up >= 2 && vbs_mjjJes06Up > 500 && vbs_detajjJes06Up > 2.5 && vbs_zepvvJes06Up < 1.0")
            dfzzcatJes07Up      [x] = dfzzcatJes07Up       [x].Filter("nvbs_jetsJes07Up >= 2 && vbs_mjjJes07Up > 500 && vbs_detajjJes07Up > 2.5 && vbs_zepvvJes07Up < 1.0")
            dfzzcatJes08Up      [x] = dfzzcatJes08Up       [x].Filter("nvbs_jetsJes08Up >= 2 && vbs_mjjJes08Up > 500 && vbs_detajjJes08Up > 2.5 && vbs_zepvvJes08Up < 1.0")
            dfzzcatJes09Up      [x] = dfzzcatJes09Up       [x].Filter("nvbs_jetsJes09Up >= 2 && vbs_mjjJes09Up > 500 && vbs_detajjJes09Up > 2.5 && vbs_zepvvJes09Up < 1.0")
            dfzzcatJes10Up      [x] = dfzzcatJes10Up       [x].Filter("nvbs_jetsJes10Up >= 2 && vbs_mjjJes10Up > 500 && vbs_detajjJes10Up > 2.5 && vbs_zepvvJes10Up < 1.0")
            dfzzcatJes11Up      [x] = dfzzcatJes11Up       [x].Filter("nvbs_jetsJes11Up >= 2 && vbs_mjjJes11Up > 500 && vbs_detajjJes11Up > 2.5 && vbs_zepvvJes11Up < 1.0")
            dfzzcatJes12Up      [x] = dfzzcatJes12Up       [x].Filter("nvbs_jetsJes12Up >= 2 && vbs_mjjJes12Up > 500 && vbs_detajjJes12Up > 2.5 && vbs_zepvvJes12Up < 1.0")
            dfzzcatJes13Up      [x] = dfzzcatJes13Up       [x].Filter("nvbs_jetsJes13Up >= 2 && vbs_mjjJes13Up > 500 && vbs_detajjJes13Up > 2.5 && vbs_zepvvJes13Up < 1.0")
            dfzzcatJes14Up      [x] = dfzzcatJes14Up       [x].Filter("nvbs_jetsJes14Up >= 2 && vbs_mjjJes14Up > 500 && vbs_detajjJes14Up > 2.5 && vbs_zepvvJes14Up < 1.0")
            dfzzcatJes15Up      [x] = dfzzcatJes15Up       [x].Filter("nvbs_jetsJes15Up >= 2 && vbs_mjjJes15Up > 500 && vbs_detajjJes15Up > 2.5 && vbs_zepvvJes15Up < 1.0")
            dfzzcatJes16Up      [x] = dfzzcatJes16Up       [x].Filter("nvbs_jetsJes16Up >= 2 && vbs_mjjJes16Up > 500 && vbs_detajjJes16Up > 2.5 && vbs_zepvvJes16Up < 1.0")
            dfzzcatJes17Up      [x] = dfzzcatJes17Up       [x].Filter("nvbs_jetsJes17Up >= 2 && vbs_mjjJes17Up > 500 && vbs_detajjJes17Up > 2.5 && vbs_zepvvJes17Up < 1.0")
            dfzzcatJes18Up      [x] = dfzzcatJes18Up       [x].Filter("nvbs_jetsJes18Up >= 2 && vbs_mjjJes18Up > 500 && vbs_detajjJes18Up > 2.5 && vbs_zepvvJes18Up < 1.0")
            dfzzcatJes19Up      [x] = dfzzcatJes19Up       [x].Filter("nvbs_jetsJes19Up >= 2 && vbs_mjjJes19Up > 500 && vbs_detajjJes19Up > 2.5 && vbs_zepvvJes19Up < 1.0")
            dfzzcatJes20Up      [x] = dfzzcatJes20Up       [x].Filter("nvbs_jetsJes20Up >= 2 && vbs_mjjJes20Up > 500 && vbs_detajjJes20Up > 2.5 && vbs_zepvvJes20Up < 1.0")
            dfzzcatJes21Up      [x] = dfzzcatJes21Up       [x].Filter("nvbs_jetsJes21Up >= 2 && vbs_mjjJes21Up > 500 && vbs_detajjJes21Up > 2.5 && vbs_zepvvJes21Up < 1.0")
            dfzzcatJes22Up      [x] = dfzzcatJes22Up       [x].Filter("nvbs_jetsJes22Up >= 2 && vbs_mjjJes22Up > 500 && vbs_detajjJes22Up > 2.5 && vbs_zepvvJes22Up < 1.0")
            dfzzcatJes23Up      [x] = dfzzcatJes23Up       [x].Filter("nvbs_jetsJes23Up >= 2 && vbs_mjjJes23Up > 500 && vbs_detajjJes23Up > 2.5 && vbs_zepvvJes23Up < 1.0")
            dfzzcatJes24Up      [x] = dfzzcatJes24Up       [x].Filter("nvbs_jetsJes24Up >= 2 && vbs_mjjJes24Up > 500 && vbs_detajjJes24Up > 2.5 && vbs_zepvvJes24Up < 1.0")
            dfzzcatJes25Up      [x] = dfzzcatJes25Up       [x].Filter("nvbs_jetsJes25Up >= 2 && vbs_mjjJes25Up > 500 && vbs_detajjJes25Up > 2.5 && vbs_zepvvJes25Up < 1.0")
            dfzzcatJes26Up      [x] = dfzzcatJes26Up       [x].Filter("nvbs_jetsJes26Up >= 2 && vbs_mjjJes26Up > 500 && vbs_detajjJes26Up > 2.5 && vbs_zepvvJes26Up < 1.0")
            dfzzcatJes27Up      [x] = dfzzcatJes27Up       [x].Filter("nvbs_jetsJes27Up >= 2 && vbs_mjjJes27Up > 500 && vbs_detajjJes27Up > 2.5 && vbs_zepvvJes27Up < 1.0")
            dfzzcatJerUp        [x] = dfzzcatJerUp         [x].Filter("nvbs_jetsJerUp   >= 2 && vbs_mjjJerUp   > 500 && vbs_detajjJerUp   > 2.5 && vbs_zepvvJerUp   < 1.0")
            dfzzcatJERUp        [x] = dfzzcatJERUp         [x].Filter("nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0")
            dfzzcatJESUp        [x] = dfzzcatJESUp         [x].Filter("nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0")
            dfzzcatUnclusteredUp[x] = dfzzcatUnclusteredUp [x].Filter("nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0")

            dfzzcatJes00Up[x] = redefineMVAVariables(dfzzcatJes00Up[x],tmva_helper,"Jes00Up",1)
            dfzzcatJes01Up[x] = redefineMVAVariables(dfzzcatJes01Up[x],tmva_helper,"Jes01Up",1)
            dfzzcatJes02Up[x] = redefineMVAVariables(dfzzcatJes02Up[x],tmva_helper,"Jes02Up",1)
            dfzzcatJes03Up[x] = redefineMVAVariables(dfzzcatJes03Up[x],tmva_helper,"Jes03Up",1)
            dfzzcatJes04Up[x] = redefineMVAVariables(dfzzcatJes04Up[x],tmva_helper,"Jes04Up",1)
            dfzzcatJes05Up[x] = redefineMVAVariables(dfzzcatJes05Up[x],tmva_helper,"Jes05Up",1)
            dfzzcatJes06Up[x] = redefineMVAVariables(dfzzcatJes06Up[x],tmva_helper,"Jes06Up",1)
            dfzzcatJes07Up[x] = redefineMVAVariables(dfzzcatJes07Up[x],tmva_helper,"Jes07Up",1)
            dfzzcatJes08Up[x] = redefineMVAVariables(dfzzcatJes08Up[x],tmva_helper,"Jes08Up",1)
            dfzzcatJes09Up[x] = redefineMVAVariables(dfzzcatJes09Up[x],tmva_helper,"Jes09Up",1)
            dfzzcatJes10Up[x] = redefineMVAVariables(dfzzcatJes10Up[x],tmva_helper,"Jes10Up",1)
            dfzzcatJes11Up[x] = redefineMVAVariables(dfzzcatJes11Up[x],tmva_helper,"Jes11Up",1)
            dfzzcatJes12Up[x] = redefineMVAVariables(dfzzcatJes12Up[x],tmva_helper,"Jes12Up",1)
            dfzzcatJes13Up[x] = redefineMVAVariables(dfzzcatJes13Up[x],tmva_helper,"Jes13Up",1)
            dfzzcatJes14Up[x] = redefineMVAVariables(dfzzcatJes14Up[x],tmva_helper,"Jes14Up",1)
            dfzzcatJes15Up[x] = redefineMVAVariables(dfzzcatJes15Up[x],tmva_helper,"Jes15Up",1)
            dfzzcatJes16Up[x] = redefineMVAVariables(dfzzcatJes16Up[x],tmva_helper,"Jes16Up",1)
            dfzzcatJes17Up[x] = redefineMVAVariables(dfzzcatJes17Up[x],tmva_helper,"Jes17Up",1)
            dfzzcatJes18Up[x] = redefineMVAVariables(dfzzcatJes18Up[x],tmva_helper,"Jes18Up",1)
            dfzzcatJes19Up[x] = redefineMVAVariables(dfzzcatJes19Up[x],tmva_helper,"Jes19Up",1)
            dfzzcatJes20Up[x] = redefineMVAVariables(dfzzcatJes20Up[x],tmva_helper,"Jes20Up",1)
            dfzzcatJes21Up[x] = redefineMVAVariables(dfzzcatJes21Up[x],tmva_helper,"Jes21Up",1)
            dfzzcatJes22Up[x] = redefineMVAVariables(dfzzcatJes22Up[x],tmva_helper,"Jes22Up",1)
            dfzzcatJes23Up[x] = redefineMVAVariables(dfzzcatJes23Up[x],tmva_helper,"Jes23Up",1)
            dfzzcatJes24Up[x] = redefineMVAVariables(dfzzcatJes24Up[x],tmva_helper,"Jes24Up",1)
            dfzzcatJes25Up[x] = redefineMVAVariables(dfzzcatJes25Up[x],tmva_helper,"Jes25Up",1)
            dfzzcatJes26Up[x] = redefineMVAVariables(dfzzcatJes26Up[x],tmva_helper,"Jes26Up",1)
            dfzzcatJes27Up[x] = redefineMVAVariables(dfzzcatJes27Up[x],tmva_helper,"Jes27Up",1)
            dfzzcatJerUp  [x] = redefineMVAVariables(dfzzcatJerUp  [x],tmva_helper,"JerUp"  ,1)

        histo[ 3][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format( 3,x), "histo_{0}_{1}".format( 3,x), 40, 10, 210), "ptl1Z1{0}".format(altMass),"weight")
        histo[ 4][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format( 4,x), "histo_{0}_{1}".format( 4,x), 20, 10, 110), "ptl2Z1{0}".format(altMass),"weight")
        histo[ 5][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format( 5,x), "histo_{0}_{1}".format( 5,x), 40, 10, 210), "ptl1Z2{0}".format(altMass),"weight")
        histo[ 6][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format( 6,x), "histo_{0}_{1}".format( 6,x), 20, 10, 110), "ptl2Z2{0}".format(altMass),"weight")
        histo[ 7][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format( 7,x), "histo_{0}_{1}".format( 7,x), 40,150, 550), "m4l{0}".format(altMass),"weight")
        histo[ 8][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format( 8,x), "histo_{0}_{1}".format( 8,x),3,-0.5, 2.5), "FourLepton_flavor","weight")
        histo[ 9][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format( 9,x), "histo_{0}_{1}".format( 9,x), 4,-0.5, 3.5), "ngood_jets","weight")
        histo[10][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format(10,x), "histo_{0}_{1}".format(10,x), 40,  0, 200), "thePuppiMET_pt","weight")

        dfzzjjcat.append(dfzzcat[x] .Filter("nvbs_jets >= 2", "At least two VBS jets"))
        histo[11][x] = dfzzjjcat[x]  .Histo1D(("histo_{0}_{1}".format(11,x), "histo_{0}_{1}".format(11,x), 4,1.5, 5.5), "ngood_jets","weight")
        histo[12][x] = dfzzjjcat[x]  .Histo1D(("histo_{0}_{1}".format(12,x), "histo_{0}_{1}".format(12,x), 20,0,2000), "vbs_mjj","weight")
        histo[13][x] = dfzzjjcat[x]  .Histo1D(("histo_{0}_{1}".format(13,x), "histo_{0}_{1}".format(13,x), 20,0,10), "vbs_detajj","weight")
        histo[14][x] = dfzzjjcat[x]  .Histo1D(("histo_{0}_{1}".format(14,x), "histo_{0}_{1}".format(14,x), 20,0,3.1416), "vbs_dphijj","weight")
        histo[15][x] = dfzzjjcat[x]  .Histo1D(("histo_{0}_{1}".format(15,x), "histo_{0}_{1}".format(15,x), 20,-1,1), "bdt_vbfinc","weight")

        dfzzvbscat.append(dfzzjjcat[x] .Filter(VBSSEL, "VBS selection"))
        histo[16][x] = dfzzvbscat[x] .Histo1D(("histo_{0}_{1}".format(16,x), "histo_{0}_{1}".format(16,x), 4,1.5, 5.5), "ngood_jets","weight")
        histo[17][x] = dfzzvbscat[x] .Histo1D(("histo_{0}_{1}".format(17,x), "histo_{0}_{1}".format(17,x), 10,500,2500), "vbs_mjj","weight")
        histo[18][x] = dfzzvbscat[x] .Histo1D(("histo_{0}_{1}".format(18,x), "histo_{0}_{1}".format(18,x), 14,2.5,9.5), "vbs_detajj","weight")
        histo[19][x] = dfzzvbscat[x] .Histo1D(("histo_{0}_{1}".format(19,x), "histo_{0}_{1}".format(19,x), 10,0,3.1416), "vbs_dphijj","weight")
        histo[20][x] = dfzzvbscat[x] .Histo1D(("histo_{0}_{1}".format(20,x), "histo_{0}_{1}".format(20,x), 20,-1,1), "bdt_vbfinc","weight")

        if(makeDataCards == 3):
            dfzzcat[x] = dfzzcat[x].Filter(VBSSEL, "VBS selection")

        if(doNtuples == True and x == theCat):
            outputFile = "ntupleZZAna_sample{0}_year{1}_job{2}.root".format(count,year,whichJob)
            dfzzcat[x].Snapshot("events", outputFile, branchList)

        histo[24][x] = dfzzxycat[x].Histo1D(("histo_{0}_{1}".format(24,x), "histo_{0}_{1}".format(24,x),5,-0.5 ,4.5), "nbtag_goodbtag_Jet_bjet","weightBTag")
        histo[25][x] = dfzzxycat[x].Filter("nbtag_goodbtag_Jet_bjet > 0").Histo1D(("histo_{0}_{1}".format(25,x), "histo_{0}_{1}".format(25,x),20, 0, 500), "m4l","weightBTag")

        dfzzxycat[x] = dfzzxycat[x].Filter("nbtag_goodbtag_Jet_bjet == 0")

        histo[26][x] = dfzzxycat[x].Histo1D(("histo_{0}_{1}".format(26,x), "histo_{0}_{1}".format(26,x),3,-0.5, 2.5), "FourLepton_flavor","weightBTag")
        histo[27][x] = dfzzxycat[x].Histo1D(("histo_{0}_{1}".format(27,x), "histo_{0}_{1}".format(27,x),20, 5, 205), "mllxy{0}".format(altMass),"weightBTag")
        histo[28][x] = dfzzxycat[x].Histo1D(("histo_{0}_{1}".format(28,x), "histo_{0}_{1}".format(28,x),20, 0, 200), "thePuppiMET_pt","weightBTag")
        histo[29][x] = dfzzxycat[x].Histo1D(("histo_{0}_{1}".format(29,x), "histo_{0}_{1}".format(29,x),20, 0, 500), "m4l{0}".format(altMass),"weightBTag")
        histo[30][x] = dfzzxycat[x].Histo1D(("histo_{0}_{1}".format(30,x), "histo_{0}_{1}".format(30,x),20, 0, 200), "ptZ2{0}".format(altMass),"weightBTag")
        histo[31][x] = dfzzxycat[x].Histo1D(("histo_{0}_{1}".format(31,x), "histo_{0}_{1}".format(31,x),20, 0, 200), "mtxy{0}".format(altMass),"weightBTag")

        histo[91][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format(91,x), "histo_{0}_{1}".format(91,x),3,-0.5, 2.5), "FourLepton_flavor","weight3")
        histo[92][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format(92,x), "histo_{0}_{1}".format(92,x),3,-0.5, 2.5), "FourLepton_flavor","weight4")
        histo[93][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format(93,x), "histo_{0}_{1}".format(93,x),3,-0.5, 2.5), "FourLepton_flavor","weightBTag")
        histo[94][x] = dfzzcat[x].Histo1D(("histo_{0}_{1}".format(94,x), "histo_{0}_{1}".format(94,x),3,-0.5, 2.5), "FourLepton_flavor","weightNoBTag")

        if(makeDataCards == 1):
            BinXF = 4
            minXF = -0.5
            maxXF = 3.5

            startF = 300
            for nv in range(0,135):
                histo[startF+nv][x] = makeFinalVariable(dfzzcat[x],"ngood_jets",theCat,startF,x,BinXF,minXF,maxXF,nv)
            histo[startF+135][x]    = makeFinalVariable(dfzzcatMuonMomUp      [x],"ngood_jets",theCat,startF,x,BinXF,minXF,maxXF,135)
            histo[startF+136][x]    = makeFinalVariable(dfzzcatElectronMomUp  [x],"ngood_jets",theCat,startF,x,BinXF,minXF,maxXF,136)
            histo[startF+137][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes00Up"        ,theCat,startF,x,BinXF,minXF,maxXF,137)
            histo[startF+138][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes01Up"        ,theCat,startF,x,BinXF,minXF,maxXF,138)
            histo[startF+139][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes02Up"        ,theCat,startF,x,BinXF,minXF,maxXF,139)
            histo[startF+140][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes03Up"        ,theCat,startF,x,BinXF,minXF,maxXF,140)
            histo[startF+141][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes04Up"        ,theCat,startF,x,BinXF,minXF,maxXF,141)
            histo[startF+142][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes05Up"        ,theCat,startF,x,BinXF,minXF,maxXF,142)
            histo[startF+143][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes06Up"        ,theCat,startF,x,BinXF,minXF,maxXF,143)
            histo[startF+144][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes07Up"        ,theCat,startF,x,BinXF,minXF,maxXF,144)
            histo[startF+145][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes08Up"        ,theCat,startF,x,BinXF,minXF,maxXF,145)
            histo[startF+146][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes09Up"        ,theCat,startF,x,BinXF,minXF,maxXF,146)
            histo[startF+147][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes10Up"        ,theCat,startF,x,BinXF,minXF,maxXF,147)
            histo[startF+148][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes11Up"        ,theCat,startF,x,BinXF,minXF,maxXF,148)
            histo[startF+149][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes12Up"        ,theCat,startF,x,BinXF,minXF,maxXF,149)
            histo[startF+150][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes13Up"        ,theCat,startF,x,BinXF,minXF,maxXF,150)
            histo[startF+151][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes14Up"        ,theCat,startF,x,BinXF,minXF,maxXF,151)
            histo[startF+152][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes15Up"        ,theCat,startF,x,BinXF,minXF,maxXF,152)
            histo[startF+153][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes16Up"        ,theCat,startF,x,BinXF,minXF,maxXF,153)
            histo[startF+154][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes17Up"        ,theCat,startF,x,BinXF,minXF,maxXF,154)
            histo[startF+155][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes18Up"        ,theCat,startF,x,BinXF,minXF,maxXF,155)
            histo[startF+156][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes19Up"        ,theCat,startF,x,BinXF,minXF,maxXF,156)
            histo[startF+157][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes20Up"        ,theCat,startF,x,BinXF,minXF,maxXF,157)
            histo[startF+158][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes21Up"        ,theCat,startF,x,BinXF,minXF,maxXF,158)
            histo[startF+159][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes22Up"        ,theCat,startF,x,BinXF,minXF,maxXF,159)
            histo[startF+160][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes23Up"        ,theCat,startF,x,BinXF,minXF,maxXF,160)
            histo[startF+161][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes24Up"        ,theCat,startF,x,BinXF,minXF,maxXF,161)
            histo[startF+162][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes25Up"        ,theCat,startF,x,BinXF,minXF,maxXF,162)
            histo[startF+163][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes26Up"        ,theCat,startF,x,BinXF,minXF,maxXF,163)
            histo[startF+164][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJes27Up"        ,theCat,startF,x,BinXF,minXF,maxXF,164)
            histo[startF+165][x]    = makeFinalVariable(dfzzcat[x],"ngood_jetsJerUp"          ,theCat,startF,x,BinXF,minXF,maxXF,165)
            histo[startF+166][x]    = makeFinalVariable(dfzzcat[x],"ngood_jets"               ,theCat,startF,x,BinXF,minXF,maxXF,166)
            histo[startF+167][x]    = makeFinalVariable(dfzzcat[x],"ngood_jets"               ,theCat,startF,x,BinXF,minXF,maxXF,167)
            histo[startF+168][x]    = makeFinalVariable(dfzzcat[x],"ngood_jets"               ,theCat,startF,x,BinXF,minXF,maxXF,168)

        elif(makeDataCards == 2):
            BinXF = 1
            minXF = -0.5
            maxXF = 2.5

            startF = 300
            for nv in range(0,135):
                histo[startF+nv][x] = makeFinalVariable(dfzzcat[x],"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,nv)
            histo[startF+135][x]    = makeFinalVariable(dfzzcatMuonMomUp      [x],"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,135)
            histo[startF+136][x]    = makeFinalVariable(dfzzcatElectronMomUp  [x],"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,136)
            histo[startF+137][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,137)
            histo[startF+138][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,138)
            histo[startF+139][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,139)
            histo[startF+140][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,140)
            histo[startF+141][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,141)
            histo[startF+142][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,142)
            histo[startF+143][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,143)
            histo[startF+144][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,144)
            histo[startF+145][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,145)
            histo[startF+146][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,146)
            histo[startF+147][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,147)
            histo[startF+148][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,148)
            histo[startF+149][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,149)
            histo[startF+150][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,150)
            histo[startF+151][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,151)
            histo[startF+152][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,152)
            histo[startF+153][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,153)
            histo[startF+154][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,154)
            histo[startF+155][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,155)
            histo[startF+156][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,156)
            histo[startF+157][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,157)
            histo[startF+158][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,158)
            histo[startF+159][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,159)
            histo[startF+160][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,160)
            histo[startF+161][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,161)
            histo[startF+162][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,162)
            histo[startF+163][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,163)
            histo[startF+164][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,164)
            histo[startF+165][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,165)
            histo[startF+166][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,166)
            histo[startF+167][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,167)
            histo[startF+168][x]    = makeFinalVariable(dfzzcat[x]               ,"FourLepton_flavor",theCat,startF,x,BinXF,minXF,maxXF,168)

        elif(makeDataCards == 3):
            BinXF = 4
            minXF = -0.5
            maxXF = 3.5
            varSel = 11

            dfzzcat             [x] = dfzzcat             [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj,vbs_detajj,vbs_dphijj,vbs_zepvv,bdt_vbfinc[0],mllmin{0},ngood_jets,{1})".format(altMass,varSel))
            dfzzcatMuonMomUp    [x] = dfzzcatMuonMomUp    [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj,vbs_detajj,vbs_dphijj,vbs_zepvv,bdt_vbfinc[0],mllminMuonMomUp,ngood_jets,{1})".format(altMass,varSel))
            dfzzcatElectronMomUp[x] = dfzzcatElectronMomUp[x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj,vbs_detajj,vbs_dphijj,vbs_zepvv,bdt_vbfinc[0],mllminElectronMomUp,ngood_jets,{1})".format(altMass,varSel))
            dfzzcatJes00Up      [x] = dfzzcatJes00Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes00Up,vbs_detajjJes00Up,vbs_dphijjJes00Up,vbs_zepvvJes00Up,bdt_vbfincJes00Up[0],mllmin{0},ngood_jetsJes00Up,{1})".format(altMass,varSel))
            dfzzcatJes01Up      [x] = dfzzcatJes01Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes01Up,vbs_detajjJes01Up,vbs_dphijjJes01Up,vbs_zepvvJes01Up,bdt_vbfincJes01Up[0],mllmin{0},ngood_jetsJes01Up,{1})".format(altMass,varSel))
            dfzzcatJes02Up      [x] = dfzzcatJes02Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes02Up,vbs_detajjJes02Up,vbs_dphijjJes02Up,vbs_zepvvJes02Up,bdt_vbfincJes02Up[0],mllmin{0},ngood_jetsJes02Up,{1})".format(altMass,varSel))
            dfzzcatJes03Up      [x] = dfzzcatJes03Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes03Up,vbs_detajjJes03Up,vbs_dphijjJes03Up,vbs_zepvvJes03Up,bdt_vbfincJes03Up[0],mllmin{0},ngood_jetsJes03Up,{1})".format(altMass,varSel))
            dfzzcatJes04Up      [x] = dfzzcatJes04Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes04Up,vbs_detajjJes04Up,vbs_dphijjJes04Up,vbs_zepvvJes04Up,bdt_vbfincJes04Up[0],mllmin{0},ngood_jetsJes04Up,{1})".format(altMass,varSel))
            dfzzcatJes05Up      [x] = dfzzcatJes05Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes05Up,vbs_detajjJes05Up,vbs_dphijjJes05Up,vbs_zepvvJes05Up,bdt_vbfincJes05Up[0],mllmin{0},ngood_jetsJes05Up,{1})".format(altMass,varSel))
            dfzzcatJes06Up      [x] = dfzzcatJes06Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes06Up,vbs_detajjJes06Up,vbs_dphijjJes06Up,vbs_zepvvJes06Up,bdt_vbfincJes06Up[0],mllmin{0},ngood_jetsJes06Up,{1})".format(altMass,varSel))
            dfzzcatJes07Up      [x] = dfzzcatJes07Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes07Up,vbs_detajjJes07Up,vbs_dphijjJes07Up,vbs_zepvvJes07Up,bdt_vbfincJes07Up[0],mllmin{0},ngood_jetsJes07Up,{1})".format(altMass,varSel))
            dfzzcatJes08Up      [x] = dfzzcatJes08Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes08Up,vbs_detajjJes08Up,vbs_dphijjJes08Up,vbs_zepvvJes08Up,bdt_vbfincJes08Up[0],mllmin{0},ngood_jetsJes08Up,{1})".format(altMass,varSel))
            dfzzcatJes09Up      [x] = dfzzcatJes09Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes09Up,vbs_detajjJes09Up,vbs_dphijjJes09Up,vbs_zepvvJes09Up,bdt_vbfincJes09Up[0],mllmin{0},ngood_jetsJes09Up,{1})".format(altMass,varSel))
            dfzzcatJes10Up      [x] = dfzzcatJes10Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes10Up,vbs_detajjJes10Up,vbs_dphijjJes10Up,vbs_zepvvJes10Up,bdt_vbfincJes10Up[0],mllmin{0},ngood_jetsJes10Up,{1})".format(altMass,varSel))
            dfzzcatJes11Up      [x] = dfzzcatJes11Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes11Up,vbs_detajjJes11Up,vbs_dphijjJes11Up,vbs_zepvvJes11Up,bdt_vbfincJes11Up[0],mllmin{0},ngood_jetsJes11Up,{1})".format(altMass,varSel))
            dfzzcatJes12Up      [x] = dfzzcatJes12Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes12Up,vbs_detajjJes12Up,vbs_dphijjJes12Up,vbs_zepvvJes12Up,bdt_vbfincJes12Up[0],mllmin{0},ngood_jetsJes12Up,{1})".format(altMass,varSel))
            dfzzcatJes13Up      [x] = dfzzcatJes13Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes13Up,vbs_detajjJes13Up,vbs_dphijjJes13Up,vbs_zepvvJes13Up,bdt_vbfincJes13Up[0],mllmin{0},ngood_jetsJes13Up,{1})".format(altMass,varSel))
            dfzzcatJes14Up      [x] = dfzzcatJes14Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes14Up,vbs_detajjJes14Up,vbs_dphijjJes14Up,vbs_zepvvJes14Up,bdt_vbfincJes14Up[0],mllmin{0},ngood_jetsJes14Up,{1})".format(altMass,varSel))
            dfzzcatJes15Up      [x] = dfzzcatJes15Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes15Up,vbs_detajjJes15Up,vbs_dphijjJes15Up,vbs_zepvvJes15Up,bdt_vbfincJes15Up[0],mllmin{0},ngood_jetsJes15Up,{1})".format(altMass,varSel))
            dfzzcatJes16Up      [x] = dfzzcatJes16Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes16Up,vbs_detajjJes16Up,vbs_dphijjJes16Up,vbs_zepvvJes16Up,bdt_vbfincJes16Up[0],mllmin{0},ngood_jetsJes16Up,{1})".format(altMass,varSel))
            dfzzcatJes17Up      [x] = dfzzcatJes17Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes17Up,vbs_detajjJes17Up,vbs_dphijjJes17Up,vbs_zepvvJes17Up,bdt_vbfincJes17Up[0],mllmin{0},ngood_jetsJes17Up,{1})".format(altMass,varSel))
            dfzzcatJes18Up      [x] = dfzzcatJes18Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes18Up,vbs_detajjJes18Up,vbs_dphijjJes18Up,vbs_zepvvJes18Up,bdt_vbfincJes18Up[0],mllmin{0},ngood_jetsJes18Up,{1})".format(altMass,varSel))
            dfzzcatJes19Up      [x] = dfzzcatJes19Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes19Up,vbs_detajjJes19Up,vbs_dphijjJes19Up,vbs_zepvvJes19Up,bdt_vbfincJes19Up[0],mllmin{0},ngood_jetsJes19Up,{1})".format(altMass,varSel))
            dfzzcatJes20Up      [x] = dfzzcatJes20Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes20Up,vbs_detajjJes20Up,vbs_dphijjJes20Up,vbs_zepvvJes20Up,bdt_vbfincJes20Up[0],mllmin{0},ngood_jetsJes20Up,{1})".format(altMass,varSel))
            dfzzcatJes21Up      [x] = dfzzcatJes21Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes21Up,vbs_detajjJes21Up,vbs_dphijjJes21Up,vbs_zepvvJes21Up,bdt_vbfincJes21Up[0],mllmin{0},ngood_jetsJes21Up,{1})".format(altMass,varSel))
            dfzzcatJes22Up      [x] = dfzzcatJes22Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes22Up,vbs_detajjJes22Up,vbs_dphijjJes22Up,vbs_zepvvJes22Up,bdt_vbfincJes22Up[0],mllmin{0},ngood_jetsJes22Up,{1})".format(altMass,varSel))
            dfzzcatJes23Up      [x] = dfzzcatJes23Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes23Up,vbs_detajjJes23Up,vbs_dphijjJes23Up,vbs_zepvvJes23Up,bdt_vbfincJes23Up[0],mllmin{0},ngood_jetsJes23Up,{1})".format(altMass,varSel))
            dfzzcatJes24Up      [x] = dfzzcatJes24Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes24Up,vbs_detajjJes24Up,vbs_dphijjJes24Up,vbs_zepvvJes24Up,bdt_vbfincJes24Up[0],mllmin{0},ngood_jetsJes24Up,{1})".format(altMass,varSel))
            dfzzcatJes25Up      [x] = dfzzcatJes25Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes25Up,vbs_detajjJes25Up,vbs_dphijjJes25Up,vbs_zepvvJes25Up,bdt_vbfincJes25Up[0],mllmin{0},ngood_jetsJes25Up,{1})".format(altMass,varSel))
            dfzzcatJes26Up      [x] = dfzzcatJes26Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes26Up,vbs_detajjJes26Up,vbs_dphijjJes26Up,vbs_zepvvJes26Up,bdt_vbfincJes26Up[0],mllmin{0},ngood_jetsJes26Up,{1})".format(altMass,varSel))
            dfzzcatJes27Up      [x] = dfzzcatJes27Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes27Up,vbs_detajjJes27Up,vbs_dphijjJes27Up,vbs_zepvvJes27Up,bdt_vbfincJes27Up[0],mllmin{0},ngood_jetsJes27Up,{1})".format(altMass,varSel))
            dfzzcatJerUp        [x] = dfzzcatJerUp        [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJerUp  ,vbs_detajjJerUp  ,vbs_dphijjJerUp  ,vbs_zepvvJerUp  ,bdt_vbfincJerUp  [0],mllmin{0},ngood_jetsJerUp  ,{1})".format(altMass,varSel))
            dfzzcatJERUp        [x] = dfzzcatJERUp        [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj       ,vbs_detajj       ,vbs_dphijj	 ,vbs_zepvv	  ,bdt_vbfinc	    [0],mllmin{0},ngood_jets	   ,{1})".format(altMass,varSel))
            dfzzcatJESUp        [x] = dfzzcatJESUp        [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj       ,vbs_detajj       ,vbs_dphijj	 ,vbs_zepvv	  ,bdt_vbfinc	    [0],mllmin{0},ngood_jets	   ,{1})".format(altMass,varSel))
            dfzzcatUnclusteredUp[x] = dfzzcatUnclusteredUp[x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj       ,vbs_detajj       ,vbs_dphijj	 ,vbs_zepvv	  ,bdt_vbfinc	    [0],mllmin{0},ngood_jets	   ,{1})".format(altMass,varSel))

            startF = 300
            for nv in range(0,136):
                histo[startF+nv][x] = makeFinalVariable(dfzzcat[x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,nv)
            histo[startF+136][x]    = makeFinalVariable(dfzzcatMuonMomUp    [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,136)
            histo[startF+137][x]    = makeFinalVariable(dfzzcatElectronMomUp[x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,137)
            histo[startF+138][x]    = makeFinalVariable(dfzzcatJes00Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,138)
            histo[startF+139][x]    = makeFinalVariable(dfzzcatJes01Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,139)
            histo[startF+140][x]    = makeFinalVariable(dfzzcatJes02Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,140)
            histo[startF+141][x]    = makeFinalVariable(dfzzcatJes03Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,141)
            histo[startF+142][x]    = makeFinalVariable(dfzzcatJes04Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,142)
            histo[startF+143][x]    = makeFinalVariable(dfzzcatJes05Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,143)
            histo[startF+144][x]    = makeFinalVariable(dfzzcatJes06Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,144)
            histo[startF+145][x]    = makeFinalVariable(dfzzcatJes07Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,145)
            histo[startF+146][x]    = makeFinalVariable(dfzzcatJes08Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,146)
            histo[startF+147][x]    = makeFinalVariable(dfzzcatJes09Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,147)
            histo[startF+148][x]    = makeFinalVariable(dfzzcatJes10Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,148)
            histo[startF+149][x]    = makeFinalVariable(dfzzcatJes11Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,149)
            histo[startF+150][x]    = makeFinalVariable(dfzzcatJes12Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,150)
            histo[startF+151][x]    = makeFinalVariable(dfzzcatJes13Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,151)
            histo[startF+152][x]    = makeFinalVariable(dfzzcatJes14Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,152)
            histo[startF+153][x]    = makeFinalVariable(dfzzcatJes15Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,153)
            histo[startF+154][x]    = makeFinalVariable(dfzzcatJes16Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,154)
            histo[startF+155][x]    = makeFinalVariable(dfzzcatJes17Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,155)
            histo[startF+156][x]    = makeFinalVariable(dfzzcatJes18Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,156)
            histo[startF+157][x]    = makeFinalVariable(dfzzcatJes19Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,157)
            histo[startF+158][x]    = makeFinalVariable(dfzzcatJes20Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,158)
            histo[startF+159][x]    = makeFinalVariable(dfzzcatJes21Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,159)
            histo[startF+160][x]    = makeFinalVariable(dfzzcatJes22Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,160)
            histo[startF+161][x]    = makeFinalVariable(dfzzcatJes23Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,161)
            histo[startF+162][x]    = makeFinalVariable(dfzzcatJes24Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,162)
            histo[startF+163][x]    = makeFinalVariable(dfzzcatJes25Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,163)
            histo[startF+164][x]    = makeFinalVariable(dfzzcatJes26Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,164)
            histo[startF+165][x]    = makeFinalVariable(dfzzcatJes27Up      [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,165)
            histo[startF+166][x]    = makeFinalVariable(dfzzcatJerUp        [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,166)
            histo[startF+167][x]    = makeFinalVariable(dfzzcatJERUp        [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,167)
            histo[startF+168][x]    = makeFinalVariable(dfzzcatJESUp        [x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,168)
            histo[startF+169][x]    = makeFinalVariable(dfzzcatUnclusteredUp[x],"finalVar",theCat,startF,x,BinXF,minXF,maxXF,169)

    report = []
    for x in range(nCat):
        report.append(dfzzvbscat[x].Report())
        if(x != theCat): continue
        print("---------------- SUMMARY {0} -------------".format(x))
        report[x].Print()

    myfile = ROOT.TFile("fillhisto_zzAnalysis_sample{0}_year{1}_job{2}.root".format(count,year,whichJob),'RECREATE')
    for i in range(nCat):
        for j in range(nHisto):
            if(histo[j][i] == 0): continue
            histo[j][i].Write()
    myfile.Close()

def readMCSample(sampleNOW,year,skimType,whichJob,group,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3):

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
    if(SwitchSample(sampleNOW,skimType)[2] == plotCategory("kPlotWZ") or
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

    analysis(df,sampleNOW,SwitchSample(sampleNOW,skimType)[2],weight,year,PDType,"false",whichJob,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3)

def readDASample(sampleNOW,year,skimType,whichJob,group,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3):

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

    analysis(df,sampleNOW,sampleNOW,weight,year,PDType,"true",whichJob,0,genEventSumLHEScaleRenorm,genEventSumPSRenorm,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3)

if __name__ == "__main__":

    group = 2

    skimType = "3l"
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

    try:
        if(process >= 0 and process < 1000):
            readMCSample(process,year,skimType,whichJob,group,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3)
        elif(process >= 1000):
            readDASample(process,year,skimType,whichJob,group,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3)
    except Exception as e:
        print("FAILED {0}".format(e))
