import ROOT
import os, sys, getopt, json

ROOT.ROOT.EnableImplicitMT(10)
from utilsCategory import plotCategory
from utilsAna import getMClist, getDATAlist
from utilsAna import SwitchSample, groupFiles, getTriggerFromJson, getLeptomSelFromJson, getLumi
from utilsSelection import selectionTauVeto, selectionPhoton, selectionJetMet, selection2LVar, selectionTrigger2L, selectionElMu, selectionWeigths, selectionGenLepJet, makeFinalVariable2D
import tmva_helper_xml

correctionString = "_correction"
makeDataCards = 0 # 1 (mjj diff), 2 (mll diff), 3 (njets diff), 4 (detajj diff), 5 (dphijj diff), 6 (mjj), 7 (mll), 8 (detajj), 9 (dphijj)
genVBSSel = makeDataCards
if(genVBSSel == 6):
    genVBSSel = 1
elif(genVBSSel == 7):
    genVBSSel = 2
elif(genVBSSel == 8):
    genVBSSel = 4
elif(genVBSSel == 9):
    genVBSSel = 5

doNtuples = False
# 0 = T, 1 = M, 2 = L
bTagSel = 2
useBTaggingWeights = 1

useFR = 1
whichAna = 1

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
VBSQCDSEL = jsonObject['VBSQCDSEL']

altMass = "Def"
jetEtaCut = 4.9
metCut = 30.0

muSelChoice = 8
MUOWP = "Medium"

elSelChoice = 7
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

    FAKE_EL   = getLeptomSelFromJson(overallLeptonSel, "FAKE_EL",   year)
    TIGHT_EL  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL{0}".format(elSelChoice),  year, 1)

    dftag = selectionElMu(dftag,year,FAKE_MU,TIGHT_MU,FAKE_EL,TIGHT_EL)

    dftag =(dftag.Filter("nLoose == 2","Only two loose leptons")
                 .Filter("nFake == 2","Two fake leptons")
                 .Filter("Sum(fake_Muon_charge)+Sum(fake_Electron_charge) != 0", "Sign-sign leptons")
                 .Define("eventNum", "event")
                 )

    if(useFR == 0):
        dftag = dftag.Filter("nTight == 2","Two tight leptons")

    dftag = selectionTauVeto(dftag,year,isData)
    dftag = selectionPhoton (dftag,year,BARRELphotons,ENDCAPphotons)
    dftag = selectionJetMet (dftag,year,bTagSel,isData,count,jetEtaCut)
    dftag = selection2LVar  (dftag,year,isData)

    dftag = (dftag.Filter("ptl1{0} > 25 && ptl2{0} > 20".format(altMass),"ptl1 > 25 && ptl2 > 20")
                  .Filter("mll{0} > 20".format(altMass),"mll > 20 GeV")
                  )

    return dftag

def analysis(df,count,category,weight,year,PDType,isData,whichJob,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,ewkCorrWeights,wsWeights,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3):

    print("starting {0} / {1} / {2} / {3} / {4} / {5} / {6}".format(count,category,weight,year,PDType,isData,whichJob))

    theCat = category
    if(theCat > 100): theCat = plotCategory("kPlotData")
    if(theCat == plotCategory("kPlotqqWW") or theCat == plotCategory("kPlotggWW") or
       theCat == plotCategory("kPlotDY") or theCat == plotCategory("kPlotTT") or
       theCat == plotCategory("kPlotTW")):
        theCat = plotCategory("kPlotWS")
    elif(theCat == plotCategory("kPlotHiggs")):
        theCat = plotCategory("kPlotVVV")

    nCat, nHisto, nhistoWS, nhistoNonPrompt, nHistoMVA = plotCategory("kPlotCategories"), 600, 20, 50, 1200
    histo = [[0 for y in range(nCat)] for x in range(nHisto)]
    histoWS = [0 for y in range(nhistoWS)]
    histoNonPrompt = [0 for y in range(nhistoNonPrompt)]
    histo2D  = [[0 for y in range(nCat)] for x in range(nHistoMVA)]
    histoMVA = [[0 for y in range(nCat)] for x in range(nHistoMVA)]

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
    ROOT.initHisto2D(wsWeights[2],39)
    ROOT.initHisto1D(puWeights[0],0)
    ROOT.initHisto1D(puWeights[1],1)
    ROOT.initHisto1D(puWeights[2],2)
    ROOT.initHisto1D(wsWeights[0],8)
    ROOT.initHisto1D(wsWeights[1],9)
    ROOT.initHisto1D(ewkCorrWeights[0],10)
    ROOT.initHisto1D(ewkCorrWeights[1],11)
    ROOT.initHisto1D(ewkCorrWeights[2],12)
    ROOT.initHisto1D(ewkCorrWeights[3],13)

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

    #ROOT.gInterpreter.ProcessLine('''
    #TMVA::Experimental::RReader model("weights_mva/bdt_BDTG_vbfinc_v0.weights.xml");
    #computeModel = TMVA::Experimental::Compute<15, float>(model);
    #''')
    #variables = ROOT.model.GetVariableNames()
    #print(variables)

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

    dfbase = selectionWeigths(dftag,isData,year,PDType,weight,useFR,bTagSel,useBTaggingWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,MUOWP,ELEWP,correctionString,whichAna)

    dfbase = (dfbase.Define("kPlotNonPrompt", "{0}".format(plotCategory("kPlotNonPrompt")))
                    .Define("kPlotWS", "{0}".format(plotCategory("kPlotWS")))
                    .Define("theCat","compute_category({0},kPlotNonPrompt,kPlotWS,nFake,nTight,nWS)".format(theCat))
                   #.Define("bdt_vbfinc", ROOT.computeModel, ROOT.model.GetVariableNames())
                    )
    dfbase = tmva_helper.run_inference(dfbase,"bdt_vbfinc")

    dfwwcat = []
    dfwwbcat = []
    dfwwvbscat = []
    dfwwbvbscat = []
    dfwwjjcat = []
    dfwwbjjcat = []

    dfwwvbs2Jcat              = []
    dfwwvbs3Jcat              = []
    dfwwvbs4Jcat              = []
    dfwwvbscatMuonMomUp       = []
    dfwwvbscatElectronMomUp   = []
    dfwwvbscatJes00Up         = []
    dfwwvbscatJes01Up         = []
    dfwwvbscatJes02Up         = []
    dfwwvbscatJes03Up         = []
    dfwwvbscatJes04Up         = []
    dfwwvbscatJes05Up         = []
    dfwwvbscatJes06Up         = []
    dfwwvbscatJes07Up         = []
    dfwwvbscatJes08Up         = []
    dfwwvbscatJes09Up         = []
    dfwwvbscatJes10Up         = []
    dfwwvbscatJes11Up         = []
    dfwwvbscatJes12Up         = []
    dfwwvbscatJes13Up         = []
    dfwwvbscatJes14Up         = []
    dfwwvbscatJes15Up         = []
    dfwwvbscatJes16Up         = []
    dfwwvbscatJes17Up         = []
    dfwwvbscatJes18Up         = []
    dfwwvbscatJes19Up         = []
    dfwwvbscatJes20Up         = []
    dfwwvbscatJes21Up         = []
    dfwwvbscatJes22Up         = []
    dfwwvbscatJes23Up         = []
    dfwwvbscatJes24Up         = []
    dfwwvbscatJes25Up         = []
    dfwwvbscatJes26Up         = []
    dfwwvbscatJes27Up         = []
    dfwwvbscatJerUp           = []
    dfwwvbscatJERUp           = []
    dfwwvbscatJESUp           = []
    dfwwvbscatUnclusteredUp   = []

    dfwwbvbs2Jcat             = []
    dfwwbvbs3Jcat             = []
    dfwwbvbs4Jcat             = []
    dfwwbvbscatMuonMomUp      = []
    dfwwbvbscatElectronMomUp  = []
    dfwwbvbscatJes00Up        = []
    dfwwbvbscatJes01Up        = []
    dfwwbvbscatJes02Up        = []
    dfwwbvbscatJes03Up        = []
    dfwwbvbscatJes04Up        = []
    dfwwbvbscatJes05Up        = []
    dfwwbvbscatJes06Up        = []
    dfwwbvbscatJes07Up        = []
    dfwwbvbscatJes08Up        = []
    dfwwbvbscatJes09Up        = []
    dfwwbvbscatJes10Up        = []
    dfwwbvbscatJes11Up        = []
    dfwwbvbscatJes12Up        = []
    dfwwbvbscatJes13Up        = []
    dfwwbvbscatJes14Up        = []
    dfwwbvbscatJes15Up        = []
    dfwwbvbscatJes16Up        = []
    dfwwbvbscatJes17Up        = []
    dfwwbvbscatJes18Up        = []
    dfwwbvbscatJes19Up        = []
    dfwwbvbscatJes20Up        = []
    dfwwbvbscatJes21Up        = []
    dfwwbvbscatJes22Up        = []
    dfwwbvbscatJes23Up        = []
    dfwwbvbscatJes24Up        = []
    dfwwbvbscatJes25Up        = []
    dfwwbvbscatJes26Up        = []
    dfwwbvbscatJes27Up        = []
    dfwwbvbscatJerUp          = []
    dfwwbvbscatJERUp          = []
    dfwwbvbscatJESUp          = []
    dfwwbvbscatUnclusteredUp  = []
    for x in range(nCat):
        dfwwcat.append(dfbase.Filter("theCat=={0}".format(x), "correct category ({0})".format(x)))

        if((x == plotCategory("kPlotEWKSSWW")) and isData == "false"):
            dfwwcat[x] = (dfwwcat[x].Define("theGenCat", "compute_vbs_gen_category({0},ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass,0)".format(genVBSSel))
                                    )
        else:
            dfwwcat[x] = (dfwwcat[x].Define("theGenCat", "{0}".format(0))
                                    )
        dfwwvbscatMuonMomUp    .append(dfwwcat[x])
        dfwwvbscatElectronMomUp.append(dfwwcat[x])
        dfwwvbscatJes00Up      .append(dfwwcat[x])
        dfwwvbscatJes01Up      .append(dfwwcat[x])
        dfwwvbscatJes02Up      .append(dfwwcat[x])
        dfwwvbscatJes03Up      .append(dfwwcat[x])
        dfwwvbscatJes04Up      .append(dfwwcat[x])
        dfwwvbscatJes05Up      .append(dfwwcat[x])
        dfwwvbscatJes06Up      .append(dfwwcat[x])
        dfwwvbscatJes07Up      .append(dfwwcat[x])
        dfwwvbscatJes08Up      .append(dfwwcat[x])
        dfwwvbscatJes09Up      .append(dfwwcat[x])
        dfwwvbscatJes10Up      .append(dfwwcat[x])
        dfwwvbscatJes11Up      .append(dfwwcat[x])
        dfwwvbscatJes12Up      .append(dfwwcat[x])
        dfwwvbscatJes13Up      .append(dfwwcat[x])
        dfwwvbscatJes14Up      .append(dfwwcat[x])
        dfwwvbscatJes15Up      .append(dfwwcat[x])
        dfwwvbscatJes16Up      .append(dfwwcat[x])
        dfwwvbscatJes17Up      .append(dfwwcat[x])
        dfwwvbscatJes18Up      .append(dfwwcat[x])
        dfwwvbscatJes19Up      .append(dfwwcat[x])
        dfwwvbscatJes20Up      .append(dfwwcat[x])
        dfwwvbscatJes21Up      .append(dfwwcat[x])
        dfwwvbscatJes22Up      .append(dfwwcat[x])
        dfwwvbscatJes23Up      .append(dfwwcat[x])
        dfwwvbscatJes24Up      .append(dfwwcat[x])
        dfwwvbscatJes25Up      .append(dfwwcat[x])
        dfwwvbscatJes26Up      .append(dfwwcat[x])
        dfwwvbscatJes27Up      .append(dfwwcat[x])
        dfwwvbscatJerUp        .append(dfwwcat[x])
        dfwwvbscatJERUp        .append(dfwwcat[x])
        dfwwvbscatJESUp        .append(dfwwcat[x])
        dfwwvbscatUnclusteredUp.append(dfwwcat[x])

        dfwwbvbscatMuonMomUp    .append(dfwwcat[x])
        dfwwbvbscatElectronMomUp.append(dfwwcat[x])
        dfwwbvbscatJes00Up      .append(dfwwcat[x])
        dfwwbvbscatJes01Up      .append(dfwwcat[x])
        dfwwbvbscatJes02Up      .append(dfwwcat[x])
        dfwwbvbscatJes03Up      .append(dfwwcat[x])
        dfwwbvbscatJes04Up      .append(dfwwcat[x])
        dfwwbvbscatJes05Up      .append(dfwwcat[x])
        dfwwbvbscatJes06Up      .append(dfwwcat[x])
        dfwwbvbscatJes07Up      .append(dfwwcat[x])
        dfwwbvbscatJes08Up      .append(dfwwcat[x])
        dfwwbvbscatJes09Up      .append(dfwwcat[x])
        dfwwbvbscatJes10Up      .append(dfwwcat[x])
        dfwwbvbscatJes11Up      .append(dfwwcat[x])
        dfwwbvbscatJes12Up      .append(dfwwcat[x])
        dfwwbvbscatJes13Up      .append(dfwwcat[x])
        dfwwbvbscatJes14Up      .append(dfwwcat[x])
        dfwwbvbscatJes15Up      .append(dfwwcat[x])
        dfwwbvbscatJes16Up      .append(dfwwcat[x])
        dfwwbvbscatJes17Up      .append(dfwwcat[x])
        dfwwbvbscatJes18Up      .append(dfwwcat[x])
        dfwwbvbscatJes19Up      .append(dfwwcat[x])
        dfwwbvbscatJes20Up      .append(dfwwcat[x])
        dfwwbvbscatJes21Up      .append(dfwwcat[x])
        dfwwbvbscatJes22Up      .append(dfwwcat[x])
        dfwwbvbscatJes23Up      .append(dfwwcat[x])
        dfwwbvbscatJes24Up      .append(dfwwcat[x])
        dfwwbvbscatJes25Up      .append(dfwwcat[x])
        dfwwbvbscatJes26Up      .append(dfwwcat[x])
        dfwwbvbscatJes27Up      .append(dfwwcat[x])
        dfwwbvbscatJerUp        .append(dfwwcat[x])
        dfwwbvbscatJERUp        .append(dfwwcat[x])
        dfwwbvbscatJESUp        .append(dfwwcat[x])
        dfwwbvbscatUnclusteredUp.append(dfwwcat[x])

        dfwwvbscatMuonMomUp     [x] = dfwwvbscatMuonMomUp     [x].Filter("mllMuonMomUp     > 20 && ptl1MuonMomUp     > 25 && ptl2MuonMomUp     > 20 && (DiLepton_flavor != 2 || abs(mllMuonMomUp     -91.1876) > 15) && nbtag_goodbtag_Jet_bjet        == 0 && nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0 && thePuppiMET_pt              > {0}".format(metCut))
        dfwwvbscatElectronMomUp [x] = dfwwvbscatElectronMomUp [x].Filter("mllElectronMomUp > 20 && ptl1ElectronMomUp > 25 && ptl2ElectronMomUp > 20 && (DiLepton_flavor != 2 || abs(mllElectronMomUp -91.1876) > 15) && nbtag_goodbtag_Jet_bjet        == 0 && nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0 && thePuppiMET_pt              > {0}".format(metCut))
        dfwwvbscatJes00Up       [x] = dfwwvbscatJes00Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes00Up == 0 && nvbs_jetsJes00Up >= 2 && vbs_mjjJes00Up > 500 && vbs_detajjJes00Up > 2.5 && vbs_zepvvJes00Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes01Up       [x] = dfwwvbscatJes01Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes01Up == 0 && nvbs_jetsJes01Up >= 2 && vbs_mjjJes01Up > 500 && vbs_detajjJes01Up > 2.5 && vbs_zepvvJes01Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes02Up       [x] = dfwwvbscatJes02Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes02Up == 0 && nvbs_jetsJes02Up >= 2 && vbs_mjjJes02Up > 500 && vbs_detajjJes02Up > 2.5 && vbs_zepvvJes02Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes03Up       [x] = dfwwvbscatJes03Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes03Up == 0 && nvbs_jetsJes03Up >= 2 && vbs_mjjJes03Up > 500 && vbs_detajjJes03Up > 2.5 && vbs_zepvvJes03Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes04Up       [x] = dfwwvbscatJes04Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes04Up == 0 && nvbs_jetsJes04Up >= 2 && vbs_mjjJes04Up > 500 && vbs_detajjJes04Up > 2.5 && vbs_zepvvJes04Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes05Up       [x] = dfwwvbscatJes05Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes05Up == 0 && nvbs_jetsJes05Up >= 2 && vbs_mjjJes05Up > 500 && vbs_detajjJes05Up > 2.5 && vbs_zepvvJes05Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes06Up       [x] = dfwwvbscatJes06Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes06Up == 0 && nvbs_jetsJes06Up >= 2 && vbs_mjjJes06Up > 500 && vbs_detajjJes06Up > 2.5 && vbs_zepvvJes06Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes07Up       [x] = dfwwvbscatJes07Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes07Up == 0 && nvbs_jetsJes07Up >= 2 && vbs_mjjJes07Up > 500 && vbs_detajjJes07Up > 2.5 && vbs_zepvvJes07Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes08Up       [x] = dfwwvbscatJes08Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes08Up == 0 && nvbs_jetsJes08Up >= 2 && vbs_mjjJes08Up > 500 && vbs_detajjJes08Up > 2.5 && vbs_zepvvJes08Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes09Up       [x] = dfwwvbscatJes09Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes09Up == 0 && nvbs_jetsJes09Up >= 2 && vbs_mjjJes09Up > 500 && vbs_detajjJes09Up > 2.5 && vbs_zepvvJes09Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes10Up       [x] = dfwwvbscatJes10Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes10Up == 0 && nvbs_jetsJes10Up >= 2 && vbs_mjjJes10Up > 500 && vbs_detajjJes10Up > 2.5 && vbs_zepvvJes10Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes11Up       [x] = dfwwvbscatJes11Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes11Up == 0 && nvbs_jetsJes11Up >= 2 && vbs_mjjJes11Up > 500 && vbs_detajjJes11Up > 2.5 && vbs_zepvvJes11Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes12Up       [x] = dfwwvbscatJes12Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes12Up == 0 && nvbs_jetsJes12Up >= 2 && vbs_mjjJes12Up > 500 && vbs_detajjJes12Up > 2.5 && vbs_zepvvJes12Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes13Up       [x] = dfwwvbscatJes13Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes13Up == 0 && nvbs_jetsJes13Up >= 2 && vbs_mjjJes13Up > 500 && vbs_detajjJes13Up > 2.5 && vbs_zepvvJes13Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes14Up       [x] = dfwwvbscatJes14Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes14Up == 0 && nvbs_jetsJes14Up >= 2 && vbs_mjjJes14Up > 500 && vbs_detajjJes14Up > 2.5 && vbs_zepvvJes14Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes15Up       [x] = dfwwvbscatJes15Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes15Up == 0 && nvbs_jetsJes15Up >= 2 && vbs_mjjJes15Up > 500 && vbs_detajjJes15Up > 2.5 && vbs_zepvvJes15Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes16Up       [x] = dfwwvbscatJes16Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes16Up == 0 && nvbs_jetsJes16Up >= 2 && vbs_mjjJes16Up > 500 && vbs_detajjJes16Up > 2.5 && vbs_zepvvJes16Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes17Up       [x] = dfwwvbscatJes17Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes17Up == 0 && nvbs_jetsJes17Up >= 2 && vbs_mjjJes17Up > 500 && vbs_detajjJes17Up > 2.5 && vbs_zepvvJes17Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes18Up       [x] = dfwwvbscatJes18Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes18Up == 0 && nvbs_jetsJes18Up >= 2 && vbs_mjjJes18Up > 500 && vbs_detajjJes18Up > 2.5 && vbs_zepvvJes18Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes19Up       [x] = dfwwvbscatJes19Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes19Up == 0 && nvbs_jetsJes19Up >= 2 && vbs_mjjJes19Up > 500 && vbs_detajjJes19Up > 2.5 && vbs_zepvvJes19Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes20Up       [x] = dfwwvbscatJes20Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes20Up == 0 && nvbs_jetsJes20Up >= 2 && vbs_mjjJes20Up > 500 && vbs_detajjJes20Up > 2.5 && vbs_zepvvJes20Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes21Up       [x] = dfwwvbscatJes21Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes21Up == 0 && nvbs_jetsJes21Up >= 2 && vbs_mjjJes21Up > 500 && vbs_detajjJes21Up > 2.5 && vbs_zepvvJes21Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes22Up       [x] = dfwwvbscatJes22Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes22Up == 0 && nvbs_jetsJes22Up >= 2 && vbs_mjjJes22Up > 500 && vbs_detajjJes22Up > 2.5 && vbs_zepvvJes22Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes23Up       [x] = dfwwvbscatJes23Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes23Up == 0 && nvbs_jetsJes23Up >= 2 && vbs_mjjJes23Up > 500 && vbs_detajjJes23Up > 2.5 && vbs_zepvvJes23Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes24Up       [x] = dfwwvbscatJes24Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes24Up == 0 && nvbs_jetsJes24Up >= 2 && vbs_mjjJes24Up > 500 && vbs_detajjJes24Up > 2.5 && vbs_zepvvJes24Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes25Up       [x] = dfwwvbscatJes25Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes25Up == 0 && nvbs_jetsJes25Up >= 2 && vbs_mjjJes25Up > 500 && vbs_detajjJes25Up > 2.5 && vbs_zepvvJes25Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes26Up       [x] = dfwwvbscatJes26Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes26Up == 0 && nvbs_jetsJes26Up >= 2 && vbs_mjjJes26Up > 500 && vbs_detajjJes26Up > 2.5 && vbs_zepvvJes26Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJes27Up       [x] = dfwwvbscatJes27Up       [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes27Up == 0 && nvbs_jetsJes27Up >= 2 && vbs_mjjJes27Up > 500 && vbs_detajjJes27Up > 2.5 && vbs_zepvvJes27Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJerUp         [x] = dfwwvbscatJerUp         [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJerUp   == 0 && nvbs_jetsJerUp   >= 2 && vbs_mjjJerUp   > 500 && vbs_detajjJerUp   > 2.5 && vbs_zepvvJerUp   < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwvbscatJERUp         [x] = dfwwvbscatJERUp         [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjet        == 0 && nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0 && thePuppiMET_ptJERUp         > {1}".format(altMass,metCut))
        dfwwvbscatJESUp         [x] = dfwwvbscatJESUp         [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjet        == 0 && nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0 && thePuppiMET_ptJESUp         > {1}".format(altMass,metCut))
        dfwwvbscatUnclusteredUp [x] = dfwwvbscatUnclusteredUp [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjet        == 0 && nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0 && thePuppiMET_ptUnclusteredUp > {1}".format(altMass,metCut))

        dfwwbvbscatMuonMomUp    [x] = dfwwbvbscatMuonMomUp    [x].Filter("mllMuonMomUp     > 20 && ptl1MuonMomUp     > 25 && ptl2MuonMomUp     > 20 && (DiLepton_flavor != 2 || abs(mllMuonMomUp     -91.1876) > 15) && nbtag_goodbtag_Jet_bjet        >  0 && nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0 && thePuppiMET_pt              > {0}".format(metCut))
        dfwwbvbscatElectronMomUp[x] = dfwwbvbscatElectronMomUp[x].Filter("mllElectronMomUp > 20 && ptl1ElectronMomUp > 25 && ptl2ElectronMomUp > 20 && (DiLepton_flavor != 2 || abs(mllElectronMomUp -91.1876) > 15) && nbtag_goodbtag_Jet_bjet        >  0 && nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0 && thePuppiMET_pt              > {0}".format(metCut))
        dfwwbvbscatJes00Up      [x] = dfwwbvbscatJes00Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes00Up >  0 && nvbs_jetsJes00Up >= 2 && vbs_mjjJes00Up > 500 && vbs_detajjJes00Up > 2.5 && vbs_zepvvJes00Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes01Up      [x] = dfwwbvbscatJes01Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes01Up >  0 && nvbs_jetsJes01Up >= 2 && vbs_mjjJes01Up > 500 && vbs_detajjJes01Up > 2.5 && vbs_zepvvJes01Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes02Up      [x] = dfwwbvbscatJes02Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes02Up >  0 && nvbs_jetsJes02Up >= 2 && vbs_mjjJes02Up > 500 && vbs_detajjJes02Up > 2.5 && vbs_zepvvJes02Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes03Up      [x] = dfwwbvbscatJes03Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes03Up >  0 && nvbs_jetsJes03Up >= 2 && vbs_mjjJes03Up > 500 && vbs_detajjJes03Up > 2.5 && vbs_zepvvJes03Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes04Up      [x] = dfwwbvbscatJes04Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes04Up >  0 && nvbs_jetsJes04Up >= 2 && vbs_mjjJes04Up > 500 && vbs_detajjJes04Up > 2.5 && vbs_zepvvJes04Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes05Up      [x] = dfwwbvbscatJes05Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes05Up >  0 && nvbs_jetsJes05Up >= 2 && vbs_mjjJes05Up > 500 && vbs_detajjJes05Up > 2.5 && vbs_zepvvJes05Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes06Up      [x] = dfwwbvbscatJes06Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes06Up >  0 && nvbs_jetsJes06Up >= 2 && vbs_mjjJes06Up > 500 && vbs_detajjJes06Up > 2.5 && vbs_zepvvJes06Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes07Up      [x] = dfwwbvbscatJes07Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes07Up >  0 && nvbs_jetsJes07Up >= 2 && vbs_mjjJes07Up > 500 && vbs_detajjJes07Up > 2.5 && vbs_zepvvJes07Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes08Up      [x] = dfwwbvbscatJes08Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes08Up >  0 && nvbs_jetsJes08Up >= 2 && vbs_mjjJes08Up > 500 && vbs_detajjJes08Up > 2.5 && vbs_zepvvJes08Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes09Up      [x] = dfwwbvbscatJes09Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes09Up >  0 && nvbs_jetsJes09Up >= 2 && vbs_mjjJes09Up > 500 && vbs_detajjJes09Up > 2.5 && vbs_zepvvJes09Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes10Up      [x] = dfwwbvbscatJes10Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes10Up >  0 && nvbs_jetsJes10Up >= 2 && vbs_mjjJes10Up > 500 && vbs_detajjJes10Up > 2.5 && vbs_zepvvJes10Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes11Up      [x] = dfwwbvbscatJes11Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes11Up >  0 && nvbs_jetsJes11Up >= 2 && vbs_mjjJes11Up > 500 && vbs_detajjJes11Up > 2.5 && vbs_zepvvJes11Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes12Up      [x] = dfwwbvbscatJes12Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes12Up >  0 && nvbs_jetsJes12Up >= 2 && vbs_mjjJes12Up > 500 && vbs_detajjJes12Up > 2.5 && vbs_zepvvJes12Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes13Up      [x] = dfwwbvbscatJes13Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes13Up >  0 && nvbs_jetsJes13Up >= 2 && vbs_mjjJes13Up > 500 && vbs_detajjJes13Up > 2.5 && vbs_zepvvJes13Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes14Up      [x] = dfwwbvbscatJes14Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes14Up >  0 && nvbs_jetsJes14Up >= 2 && vbs_mjjJes14Up > 500 && vbs_detajjJes14Up > 2.5 && vbs_zepvvJes14Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes15Up      [x] = dfwwbvbscatJes15Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes15Up >  0 && nvbs_jetsJes15Up >= 2 && vbs_mjjJes15Up > 500 && vbs_detajjJes15Up > 2.5 && vbs_zepvvJes15Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes16Up      [x] = dfwwbvbscatJes16Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes16Up >  0 && nvbs_jetsJes16Up >= 2 && vbs_mjjJes16Up > 500 && vbs_detajjJes16Up > 2.5 && vbs_zepvvJes16Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes17Up      [x] = dfwwbvbscatJes17Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes17Up >  0 && nvbs_jetsJes17Up >= 2 && vbs_mjjJes17Up > 500 && vbs_detajjJes17Up > 2.5 && vbs_zepvvJes17Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes18Up      [x] = dfwwbvbscatJes18Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes18Up >  0 && nvbs_jetsJes18Up >= 2 && vbs_mjjJes18Up > 500 && vbs_detajjJes18Up > 2.5 && vbs_zepvvJes18Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes19Up      [x] = dfwwbvbscatJes19Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes19Up >  0 && nvbs_jetsJes19Up >= 2 && vbs_mjjJes19Up > 500 && vbs_detajjJes19Up > 2.5 && vbs_zepvvJes19Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes20Up      [x] = dfwwbvbscatJes20Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes20Up >  0 && nvbs_jetsJes20Up >= 2 && vbs_mjjJes20Up > 500 && vbs_detajjJes20Up > 2.5 && vbs_zepvvJes20Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes21Up      [x] = dfwwbvbscatJes21Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes21Up >  0 && nvbs_jetsJes21Up >= 2 && vbs_mjjJes21Up > 500 && vbs_detajjJes21Up > 2.5 && vbs_zepvvJes21Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes22Up      [x] = dfwwbvbscatJes22Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes22Up >  0 && nvbs_jetsJes22Up >= 2 && vbs_mjjJes22Up > 500 && vbs_detajjJes22Up > 2.5 && vbs_zepvvJes22Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes23Up      [x] = dfwwbvbscatJes23Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes23Up >  0 && nvbs_jetsJes23Up >= 2 && vbs_mjjJes23Up > 500 && vbs_detajjJes23Up > 2.5 && vbs_zepvvJes23Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes24Up      [x] = dfwwbvbscatJes24Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes24Up >  0 && nvbs_jetsJes24Up >= 2 && vbs_mjjJes24Up > 500 && vbs_detajjJes24Up > 2.5 && vbs_zepvvJes24Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes25Up      [x] = dfwwbvbscatJes25Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes25Up >  0 && nvbs_jetsJes25Up >= 2 && vbs_mjjJes25Up > 500 && vbs_detajjJes25Up > 2.5 && vbs_zepvvJes25Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes26Up      [x] = dfwwbvbscatJes26Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes26Up >  0 && nvbs_jetsJes26Up >= 2 && vbs_mjjJes26Up > 500 && vbs_detajjJes26Up > 2.5 && vbs_zepvvJes26Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJes27Up      [x] = dfwwbvbscatJes27Up      [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJes27Up >  0 && nvbs_jetsJes27Up >= 2 && vbs_mjjJes27Up > 500 && vbs_detajjJes27Up > 2.5 && vbs_zepvvJes27Up < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJerUp        [x] = dfwwbvbscatJerUp        [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjetJerUp   >  0 && nvbs_jetsJerUp   >= 2 && vbs_mjjJerUp   > 500 && vbs_detajjJerUp   > 2.5 && vbs_zepvvJerUp   < 1.0 && thePuppiMET_pt              > {1}".format(altMass,metCut))
        dfwwbvbscatJERUp        [x] = dfwwbvbscatJERUp        [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjet        >  0 && nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0 && thePuppiMET_ptJERUp         > {1}".format(altMass,metCut))
        dfwwbvbscatJESUp        [x] = dfwwbvbscatJESUp        [x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjet        >  0 && nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0 && thePuppiMET_ptJESUp         > {1}".format(altMass,metCut))
        dfwwbvbscatUnclusteredUp[x] = dfwwbvbscatUnclusteredUp[x].Filter("mll{0}           > 20 && ptl1{0}           > 25 && ptl2{0}           > 20 && (DiLepton_flavor != 2 || abs(mll{0}           -91.1876) > 15) && nbtag_goodbtag_Jet_bjet        >  0 && nvbs_jets        >= 2 && vbs_mjj        > 500 && vbs_detajj        > 2.5 && vbs_zepvv        < 1.0 && thePuppiMET_ptUnclusteredUp > {1}".format(altMass,metCut))

        histo[ 0][x] = dfwwcat[x].Histo1D(("histo_{0}_{1}".format( 0,x), "histo_{0}_{1}".format( 0,x),40, 20, 220), "mll{0}".format(altMass),"weightNoBTag")
        dfwwcat[x] = dfwwcat[x].Filter("DiLepton_flavor != 2 || abs(mll{0}-91.1876) > 15".format(altMass),"Z veto")

        dfwwbcat.append(dfwwcat[x].Filter("nbtag_goodbtag_Jet_bjet > 0","at least one good b-jets"))

        histo[ 1][x] = dfwwcat[x].Histo1D(("histo_{0}_{1}".format( 1,x), "histo_{0}_{1}".format( 1,x), 5,-0.5 ,4.5),     "nbtag_goodbtag_Jet_bjet","weight")
        dfwwcat[x] = dfwwcat[x].Filter("nbtag_goodbtag_Jet_bjet == 0","no good b-jets")

        histo[ 2][x] = dfwwcat[x] .Histo1D(("histo_{0}_{1}".format( 2,x), "histo_{0}_{1}".format( 2,x), 4,-0.5, 3.5), "ltype","weight")
        histo[ 3][x] = dfwwbcat[x].Histo1D(("histo_{0}_{1}".format( 3,x), "histo_{0}_{1}".format( 3,x), 4,-0.5, 3.5), "ltype","weight")
        histo[ 4][x] = dfwwcat[x] .Histo1D(("histo_{0}_{1}".format( 4,x), "histo_{0}_{1}".format( 4,x), 6,-0.5, 5.5), "ngood_jets","weight")
        histo[ 5][x] = dfwwbcat[x].Histo1D(("histo_{0}_{1}".format( 5,x), "histo_{0}_{1}".format( 5,x), 6,-0.5, 5.5), "ngood_jets","weight")

        dfwwcat[x]  = dfwwcat[x] .Filter("nvbs_jets >= 2 && vbs_mjj > 200", "At least two VBS jets")
        dfwwbcat[x] = dfwwbcat[x].Filter("nvbs_jets >= 2 && vbs_mjj > 200", "At least two VBS jets")
        histo[ 6][x] = dfwwcat[x] .Histo1D(("histo_{0}_{1}".format( 6,x), "histo_{0}_{1}".format( 6,x), 4,-0.5, 3.5), "ltype","weight")
        histo[ 7][x] = dfwwbcat[x].Histo1D(("histo_{0}_{1}".format( 7,x), "histo_{0}_{1}".format( 7,x), 4,-0.5, 3.5), "ltype","weight")
        histo[ 8][x] = dfwwcat[x] .Histo1D(("histo_{0}_{1}".format( 8,x), "histo_{0}_{1}".format( 8,x), 4, 1.5, 5.5), "ngood_jets","weight")
        histo[ 9][x] = dfwwbcat[x].Histo1D(("histo_{0}_{1}".format( 9,x), "histo_{0}_{1}".format( 9,x), 4, 1.5, 5.5), "ngood_jets","weight")
        histo[10][x] = dfwwcat[x] .Histo1D(("histo_{0}_{1}".format(10,x), "histo_{0}_{1}".format(10,x), 20,200,2200), "vbs_mjj","weight")
        histo[11][x] = dfwwbcat[x].Histo1D(("histo_{0}_{1}".format(11,x), "histo_{0}_{1}".format(11,x), 20,200,2200), "vbs_mjj","weight")
        histo[12][x] = dfwwcat[x] .Histo1D(("histo_{0}_{1}".format(12,x), "histo_{0}_{1}".format(12,x), 19,0.0,9.5), "vbs_detajj","weight")
        histo[13][x] = dfwwbcat[x].Histo1D(("histo_{0}_{1}".format(13,x), "histo_{0}_{1}".format(13,x), 19,0.0,9.5), "vbs_detajj","weight")
        histo[14][x] = dfwwcat[x] .Histo1D(("histo_{0}_{1}".format(14,x), "histo_{0}_{1}".format(14,x), 20,0,2), "vbs_zepvv","weight")
        histo[15][x] = dfwwbcat[x].Histo1D(("histo_{0}_{1}".format(15,x), "histo_{0}_{1}".format(15,x), 20,0,2), "vbs_zepvv","weight")

        for ltype in range(4):
            histo[60+ltype][x] = dfwwcat[x] .Filter("ltype == {0}".format(ltype)).Histo1D(("histo_{0}_{1}".format(60+ltype,x), "histo_{0}_{1}".format(60+ltype,x),20, 25, 225), "ptl1{0}".format(altMass),"weight")
            histo[64+ltype][x] = dfwwbcat[x].Filter("ltype == {0}".format(ltype)).Histo1D(("histo_{0}_{1}".format(64+ltype,x), "histo_{0}_{1}".format(64+ltype,x),20, 25, 225), "ptl1{0}".format(altMass),"weight")
            histo[68+ltype][x] = dfwwcat[x] .Filter("ltype == {0}".format(ltype)).Histo1D(("histo_{0}_{1}".format(68+ltype,x), "histo_{0}_{1}".format(68+ltype,x),20, 20, 120), "ptl2{0}".format(altMass),"weight")
            histo[72+ltype][x] = dfwwbcat[x].Filter("ltype == {0}".format(ltype)).Histo1D(("histo_{0}_{1}".format(72+ltype,x), "histo_{0}_{1}".format(72+ltype,x),20, 20, 120), "ptl2{0}".format(altMass),"weight")
            histo[76+ltype][x] = dfwwcat[x] .Filter("ltype == {0}".format(ltype)).Histo1D(("histo_{0}_{1}".format(76+ltype,x), "histo_{0}_{1}".format(76+ltype,x),25, 0, 2.5), "etal1","weight")
            histo[80+ltype][x] = dfwwbcat[x].Filter("ltype == {0}".format(ltype)).Histo1D(("histo_{0}_{1}".format(80+ltype,x), "histo_{0}_{1}".format(80+ltype,x),25, 0, 2.5), "etal1","weight")
            histo[84+ltype][x] = dfwwcat[x] .Filter("ltype == {0}".format(ltype)).Histo1D(("histo_{0}_{1}".format(84+ltype,x), "histo_{0}_{1}".format(84+ltype,x),25, 0, 2.5), "etal2","weight")
            histo[88+ltype][x] = dfwwbcat[x].Filter("ltype == {0}".format(ltype)).Histo1D(("histo_{0}_{1}".format(88+ltype,x), "histo_{0}_{1}".format(88+ltype,x),25, 0, 2.5), "etal2","weight")

        dfwwvbscat .append(dfwwcat[x] .Filter(VBSSEL, "VBS selection"))
        dfwwbvbscat.append(dfwwbcat[x].Filter(VBSSEL, "VBS selection"))
        histo[16][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(16,x), "histo_{0}_{1}".format(16,x),25,  0, 250), "thePuppiMET_pt","weight")
        histo[17][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(17,x), "histo_{0}_{1}".format(17,x),25,  0, 250), "thePuppiMET_pt","weight")

        dfwwvbscat[x]  = dfwwvbscat[x] .Filter("thePuppiMET_pt > {0}".format(metCut), "thePuppiMET_pt > {0}".format(metCut))
        dfwwbvbscat[x] = dfwwbvbscat[x].Filter("thePuppiMET_pt > {0}".format(metCut), "thePuppiMET_pt > {0}".format(metCut))
        histo[18][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(18,x), "histo_{0}_{1}".format(18,x), 4,-0.5, 3.5), "ltype","weight")
        histo[19][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(19,x), "histo_{0}_{1}".format(19,x), 4,-0.5, 3.5), "ltype","weight")
        histo[20][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(20,x), "histo_{0}_{1}".format(20,x), 4, 1.5, 5.5), "ngood_jets","weight")
        histo[21][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(21,x), "histo_{0}_{1}".format(21,x), 4, 1.5, 5.5), "ngood_jets","weight")

        histo[22][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(22,x), "histo_{0}_{1}".format(22,x), 25,500,3000), "vbs_mjj","weight")
        histo[23][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(23,x), "histo_{0}_{1}".format(23,x), 25,500,3000), "vbs_mjj","weight")
        histo[24][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(24,x), "histo_{0}_{1}".format(24,x), 14,2.5,9.5), "vbs_detajj","weight")
        histo[25][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(25,x), "histo_{0}_{1}".format(25,x), 14,2.5,9.5), "vbs_detajj","weight")
        histo[26][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(26,x), "histo_{0}_{1}".format(26,x), 10,0,3.1416), "vbs_dphijj","weight")
        histo[27][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(27,x), "histo_{0}_{1}".format(27,x), 10,0,3.1416), "vbs_dphijj","weight")
        histo[28][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(28,x), "histo_{0}_{1}".format(28,x), 10,0,1), "vbs_zepvv","weight")
        histo[29][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(29,x), "histo_{0}_{1}".format(29,x), 10,0,1), "vbs_zepvv","weight")
        histo[30][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(30,x), "histo_{0}_{1}".format(30,x), 20,-1,1), "bdt_vbfinc","weight")
        histo[31][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(31,x), "histo_{0}_{1}".format(31,x), 20,-1,1), "bdt_vbfinc","weight")
        histo[32][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(32,x), "histo_{0}_{1}".format(32,x),25, 50, 300), "vbs_ptj1","weight")
        histo[33][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(33,x), "histo_{0}_{1}".format(33,x),25, 50, 300), "vbs_ptj1","weight")
        histo[34][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(34,x), "histo_{0}_{1}".format(34,x),25, 50, 300), "vbs_ptj2","weight")
        histo[35][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(35,x), "histo_{0}_{1}".format(35,x),25, 50, 300), "vbs_ptj2","weight")
        histo[36][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(36,x), "histo_{0}_{1}".format(36,x),25, 0, 5), "vbs_etaj1","weight")
        histo[37][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(37,x), "histo_{0}_{1}".format(37,x),25, 0, 5), "vbs_etaj1","weight")
        histo[38][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(38,x), "histo_{0}_{1}".format(38,x),25, 0, 5), "vbs_etaj2","weight")
        histo[39][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(39,x), "histo_{0}_{1}".format(39,x),25, 0, 5), "vbs_etaj2","weight")

        dfwwjjcat .append(dfwwcat[x] .Filter("thePuppiMET_pt > {0}".format(metCut), "thePuppiMET_pt > {0}".format(metCut)).Filter(VBSQCDSEL, "dijet non-vbf selection"))
        dfwwbjjcat.append(dfwwbcat[x].Filter("thePuppiMET_pt > {0}".format(metCut), "thePuppiMET_pt > {0}".format(metCut)).Filter(VBSQCDSEL, "dijet non-vbf selection"))
        histo[40][x] = dfwwjjcat[x] .Histo1D(("histo_{0}_{1}".format(40,x), "histo_{0}_{1}".format(40,x), 14,0.0,7), "vbs_detajj","weight")
        histo[41][x] = dfwwbjjcat[x].Histo1D(("histo_{0}_{1}".format(41,x), "histo_{0}_{1}".format(41,x), 14,0.0,7), "vbs_detajj","weight")
        histo[42][x] = dfwwjjcat[x] .Histo1D(("histo_{0}_{1}".format(42,x), "histo_{0}_{1}".format(42,x), 4,-0.5, 3.5), "ltype","weight")
        histo[43][x] = dfwwbjjcat[x].Histo1D(("histo_{0}_{1}".format(43,x), "histo_{0}_{1}".format(43,x), 4,-0.5, 3.5), "ltype","weight")
        histo[44][x] = dfwwjjcat[x] .Histo1D(("histo_{0}_{1}".format(44,x), "histo_{0}_{1}".format(44,x), 4, 1.5, 5.5), "ngood_jets","weight")
        histo[45][x] = dfwwbjjcat[x].Histo1D(("histo_{0}_{1}".format(45,x), "histo_{0}_{1}".format(45,x), 4, 1.5, 5.5), "ngood_jets","weight")
        histo[46][x] = dfwwjjcat[x] .Histo1D(("histo_{0}_{1}".format(46,x), "histo_{0}_{1}".format(46,x),25, 50, 300), "vbs_ptj1","weight")
        histo[47][x] = dfwwbjjcat[x].Histo1D(("histo_{0}_{1}".format(47,x), "histo_{0}_{1}".format(47,x),25, 50, 300), "vbs_ptj1","weight")
        histo[48][x] = dfwwjjcat[x] .Histo1D(("histo_{0}_{1}".format(48,x), "histo_{0}_{1}".format(48,x),25, 50, 300), "vbs_ptj2","weight")
        histo[49][x] = dfwwbjjcat[x].Histo1D(("histo_{0}_{1}".format(49,x), "histo_{0}_{1}".format(49,x),25, 50, 300), "vbs_ptj2","weight")
        histo[50][x] = dfwwjjcat[x] .Histo1D(("histo_{0}_{1}".format(50,x), "histo_{0}_{1}".format(50,x),25, 0, 5), "vbs_etaj1","weight")
        histo[51][x] = dfwwbjjcat[x].Histo1D(("histo_{0}_{1}".format(51,x), "histo_{0}_{1}".format(51,x),25, 0, 5), "vbs_etaj1","weight")
        histo[52][x] = dfwwjjcat[x] .Histo1D(("histo_{0}_{1}".format(52,x), "histo_{0}_{1}".format(52,x),25, 0, 5), "vbs_etaj2","weight")
        histo[53][x] = dfwwbjjcat[x].Histo1D(("histo_{0}_{1}".format(53,x), "histo_{0}_{1}".format(53,x),25, 0, 5), "vbs_etaj2","weight")

        # Set output directory
        if (isData == "true"):
            output_dir = "/mnt/home/mghimiray/VBSStudies/Outputs_VBS/matrix_method/ntuple/"
        elif (isData == "false"):
            output_dir = "/mnt/home/mghimiray/VBSStudies/Outputs_VBS/OriginalTT/ntuple/"
        
        # Debugging print
 #       print(f"isData={isData}, doNtuples={doNtuples}, x={x}, theCat={theCat}, output_dir={output_dir}")


        print(f"doNtuples={doNtuples}, x={x}, theCat={theCat}")  # for checking the output files
        if(doNtuples == True and x == theCat):            
            outputFile = f"{output_dir}/ntupleSSWWAna_sample{count}_year{year}_job{whichJob}.root"
            dfwwvbscat[x].Snapshot("events", outputFile, branchList)


        histo[ 99][x] = dfwwvbscat[x].Histo1D(("histo_{0}_{1}".format( 99,x), "histo_{0}_{1}".format( 99,x),12,500,3500), "vbs_mjj","weight")
        histo[100][x] = dfwwvbscat[x].Histo1D(("histo_{0}_{1}".format(100,x), "histo_{0}_{1}".format(100,x),12,500,3500), "vbs_mjj","weight0")
        histo[101][x] = dfwwvbscat[x].Histo1D(("histo_{0}_{1}".format(101,x), "histo_{0}_{1}".format(101,x),12,500,3500), "vbs_mjj","weight1")
        histo[102][x] = dfwwvbscat[x].Histo1D(("histo_{0}_{1}".format(102,x), "histo_{0}_{1}".format(102,x),12,500,3500), "vbs_mjj","weight2")
        histo[103][x] = dfwwvbscat[x].Histo1D(("histo_{0}_{1}".format(103,x), "histo_{0}_{1}".format(103,x),12,500,3500), "vbs_mjj","weight3")
        histo[104][x] = dfwwvbscat[x].Histo1D(("histo_{0}_{1}".format(104,x), "histo_{0}_{1}".format(104,x),12,500,3500), "vbs_mjj","weight4")
        histo[105][x] = dfwwvbscat[x].Histo1D(("histo_{0}_{1}".format(105,x), "histo_{0}_{1}".format(105,x),12,500,3500), "vbs_mjj","weight5")
        histo[106][x] = dfwwvbscat[x].Histo1D(("histo_{0}_{1}".format(106,x), "histo_{0}_{1}".format(106,x),12,500,3500), "vbs_mjj","weight6")
        histo[107][x] = dfwwvbscat[x].Histo1D(("histo_{0}_{1}".format(107,x), "histo_{0}_{1}".format(107,x),12,500,3500), "vbs_mjj","weight7")
        histo[108][x] = dfwwvbscat[x].Histo1D(("histo_{0}_{1}".format(108,x), "histo_{0}_{1}".format(108,x),12,500,3500), "vbs_mjj","weightWSUnc0")
        histo[109][x] = dfwwvbscat[x].Histo1D(("histo_{0}_{1}".format(109,x), "histo_{0}_{1}".format(109,x),12,500,3500), "vbs_mjj","weightWSUnc1")

        BinXF1 = 10
        minXF1 = 0
        maxXF1 = 1
        BinXF2 = 10
        minXF2 = 0
        maxXF2 = 1
        if(makeDataCards >= 1):
            BinYF = 5
            minYF = -0.5
            maxYF = 4.5

            varSel = makeDataCards
            if(makeDataCards == 6):
                varSel = 20
            elif(makeDataCards == 7):
                varSel = 21
            elif(makeDataCards == 8):
                varSel = 22
            elif(makeDataCards == 9):
                varSel = 23
            dfwwvbscat             [x] = dfwwvbscat             [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj,vbs_detajj,vbs_dphijj,0.0,0.0,mll{0},ngood_jets,{1})".format(altMass,varSel))
            dfwwvbscatMuonMomUp    [x] = dfwwvbscatMuonMomUp    [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj,vbs_detajj,vbs_dphijj,0.0,0.0,mllMuonMomUp,ngood_jets,{1})".format(altMass,varSel))
            dfwwvbscatElectronMomUp[x] = dfwwvbscatElectronMomUp[x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj,vbs_detajj,vbs_dphijj,0.0,0.0,mllElectronMomUp,ngood_jets,{1})".format(altMass,varSel))
            dfwwvbscatJes00Up      [x] = dfwwvbscatJes00Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes00Up,vbs_detajjJes00Up,vbs_dphijjJes00Up,0.0,0.0,mll{0},ngood_jetsJes00Up,{1})".format(altMass,varSel))
            dfwwvbscatJes01Up      [x] = dfwwvbscatJes01Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes01Up,vbs_detajjJes01Up,vbs_dphijjJes01Up,0.0,0.0,mll{0},ngood_jetsJes01Up,{1})".format(altMass,varSel))
            dfwwvbscatJes02Up      [x] = dfwwvbscatJes02Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes02Up,vbs_detajjJes02Up,vbs_dphijjJes02Up,0.0,0.0,mll{0},ngood_jetsJes02Up,{1})".format(altMass,varSel))
            dfwwvbscatJes03Up      [x] = dfwwvbscatJes03Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes03Up,vbs_detajjJes03Up,vbs_dphijjJes03Up,0.0,0.0,mll{0},ngood_jetsJes03Up,{1})".format(altMass,varSel))
            dfwwvbscatJes04Up      [x] = dfwwvbscatJes04Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes04Up,vbs_detajjJes04Up,vbs_dphijjJes04Up,0.0,0.0,mll{0},ngood_jetsJes04Up,{1})".format(altMass,varSel))
            dfwwvbscatJes05Up      [x] = dfwwvbscatJes05Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes05Up,vbs_detajjJes05Up,vbs_dphijjJes05Up,0.0,0.0,mll{0},ngood_jetsJes05Up,{1})".format(altMass,varSel))
            dfwwvbscatJes06Up      [x] = dfwwvbscatJes06Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes06Up,vbs_detajjJes06Up,vbs_dphijjJes06Up,0.0,0.0,mll{0},ngood_jetsJes06Up,{1})".format(altMass,varSel))
            dfwwvbscatJes07Up      [x] = dfwwvbscatJes07Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes07Up,vbs_detajjJes07Up,vbs_dphijjJes07Up,0.0,0.0,mll{0},ngood_jetsJes07Up,{1})".format(altMass,varSel))
            dfwwvbscatJes08Up      [x] = dfwwvbscatJes08Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes08Up,vbs_detajjJes08Up,vbs_dphijjJes08Up,0.0,0.0,mll{0},ngood_jetsJes08Up,{1})".format(altMass,varSel))
            dfwwvbscatJes09Up      [x] = dfwwvbscatJes09Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes09Up,vbs_detajjJes09Up,vbs_dphijjJes09Up,0.0,0.0,mll{0},ngood_jetsJes09Up,{1})".format(altMass,varSel))
            dfwwvbscatJes10Up      [x] = dfwwvbscatJes10Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes10Up,vbs_detajjJes10Up,vbs_dphijjJes10Up,0.0,0.0,mll{0},ngood_jetsJes10Up,{1})".format(altMass,varSel))
            dfwwvbscatJes11Up      [x] = dfwwvbscatJes11Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes11Up,vbs_detajjJes11Up,vbs_dphijjJes11Up,0.0,0.0,mll{0},ngood_jetsJes11Up,{1})".format(altMass,varSel))
            dfwwvbscatJes12Up      [x] = dfwwvbscatJes12Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes12Up,vbs_detajjJes12Up,vbs_dphijjJes12Up,0.0,0.0,mll{0},ngood_jetsJes12Up,{1})".format(altMass,varSel))
            dfwwvbscatJes13Up      [x] = dfwwvbscatJes13Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes13Up,vbs_detajjJes13Up,vbs_dphijjJes13Up,0.0,0.0,mll{0},ngood_jetsJes13Up,{1})".format(altMass,varSel))
            dfwwvbscatJes14Up      [x] = dfwwvbscatJes14Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes14Up,vbs_detajjJes14Up,vbs_dphijjJes14Up,0.0,0.0,mll{0},ngood_jetsJes14Up,{1})".format(altMass,varSel))
            dfwwvbscatJes15Up      [x] = dfwwvbscatJes15Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes15Up,vbs_detajjJes15Up,vbs_dphijjJes15Up,0.0,0.0,mll{0},ngood_jetsJes15Up,{1})".format(altMass,varSel))
            dfwwvbscatJes16Up      [x] = dfwwvbscatJes16Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes16Up,vbs_detajjJes16Up,vbs_dphijjJes16Up,0.0,0.0,mll{0},ngood_jetsJes16Up,{1})".format(altMass,varSel))
            dfwwvbscatJes17Up      [x] = dfwwvbscatJes17Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes17Up,vbs_detajjJes17Up,vbs_dphijjJes17Up,0.0,0.0,mll{0},ngood_jetsJes17Up,{1})".format(altMass,varSel))
            dfwwvbscatJes18Up      [x] = dfwwvbscatJes18Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes18Up,vbs_detajjJes18Up,vbs_dphijjJes18Up,0.0,0.0,mll{0},ngood_jetsJes18Up,{1})".format(altMass,varSel))
            dfwwvbscatJes19Up      [x] = dfwwvbscatJes19Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes19Up,vbs_detajjJes19Up,vbs_dphijjJes19Up,0.0,0.0,mll{0},ngood_jetsJes19Up,{1})".format(altMass,varSel))
            dfwwvbscatJes20Up      [x] = dfwwvbscatJes20Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes20Up,vbs_detajjJes20Up,vbs_dphijjJes20Up,0.0,0.0,mll{0},ngood_jetsJes20Up,{1})".format(altMass,varSel))
            dfwwvbscatJes21Up      [x] = dfwwvbscatJes21Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes21Up,vbs_detajjJes21Up,vbs_dphijjJes21Up,0.0,0.0,mll{0},ngood_jetsJes21Up,{1})".format(altMass,varSel))
            dfwwvbscatJes22Up      [x] = dfwwvbscatJes22Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes22Up,vbs_detajjJes22Up,vbs_dphijjJes22Up,0.0,0.0,mll{0},ngood_jetsJes22Up,{1})".format(altMass,varSel))
            dfwwvbscatJes23Up      [x] = dfwwvbscatJes23Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes23Up,vbs_detajjJes23Up,vbs_dphijjJes23Up,0.0,0.0,mll{0},ngood_jetsJes23Up,{1})".format(altMass,varSel))
            dfwwvbscatJes24Up      [x] = dfwwvbscatJes24Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes24Up,vbs_detajjJes24Up,vbs_dphijjJes24Up,0.0,0.0,mll{0},ngood_jetsJes24Up,{1})".format(altMass,varSel))
            dfwwvbscatJes25Up      [x] = dfwwvbscatJes25Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes25Up,vbs_detajjJes25Up,vbs_dphijjJes25Up,0.0,0.0,mll{0},ngood_jetsJes25Up,{1})".format(altMass,varSel))
            dfwwvbscatJes26Up      [x] = dfwwvbscatJes26Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes26Up,vbs_detajjJes26Up,vbs_dphijjJes26Up,0.0,0.0,mll{0},ngood_jetsJes26Up,{1})".format(altMass,varSel))
            dfwwvbscatJes27Up      [x] = dfwwvbscatJes27Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes27Up,vbs_detajjJes27Up,vbs_dphijjJes27Up,0.0,0.0,mll{0},ngood_jetsJes27Up,{1})".format(altMass,varSel))
            dfwwvbscatJerUp        [x] = dfwwvbscatJerUp        [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJerUp  ,vbs_detajjJerUp  ,vbs_dphijjJerUp  ,0.0,0.0,mll{0},ngood_jetsJerUp  ,{1})".format(altMass,varSel))
            dfwwvbscatJERUp        [x] = dfwwvbscatJERUp        [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj       ,vbs_detajj       ,vbs_dphijj       ,0.0,0.0,mll{0},ngood_jets       ,{1})".format(altMass,varSel))
            dfwwvbscatJESUp        [x] = dfwwvbscatJESUp        [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj       ,vbs_detajj       ,vbs_dphijj       ,0.0,0.0,mll{0},ngood_jets       ,{1})".format(altMass,varSel))
            dfwwvbscatUnclusteredUp[x] = dfwwvbscatUnclusteredUp[x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj       ,vbs_detajj       ,vbs_dphijj       ,0.0,0.0,mll{0},ngood_jets       ,{1})".format(altMass,varSel))

            varSel = 9
            if(makeDataCards == 6):
                varSel = 20
            elif(makeDataCards == 7):
                varSel = 21
            elif(makeDataCards == 8):
                varSel = 22
            elif(makeDataCards == 9):
                varSel = 23
            dfwwbvbscat             [x] = dfwwbvbscat             [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj,vbs_detajj,vbs_dphijj,0.0,0.0,mll{0},ngood_jets,{1})".format(altMass,varSel))
            dfwwbvbscatMuonMomUp    [x] = dfwwbvbscatMuonMomUp    [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj,vbs_detajj,vbs_dphijj,0.0,0.0,mllMuonMomUp,ngood_jets,{1})".format(altMass,varSel))
            dfwwbvbscatElectronMomUp[x] = dfwwbvbscatElectronMomUp[x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj,vbs_detajj,vbs_dphijj,0.0,0.0,mllElectronMomUp,ngood_jets,{1})".format(altMass,varSel))
            dfwwbvbscatJes00Up      [x] = dfwwbvbscatJes00Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes00Up,vbs_detajjJes00Up,vbs_dphijjJes00Up,0.0,0.0,mll{0},ngood_jetsJes00Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes01Up      [x] = dfwwbvbscatJes01Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes01Up,vbs_detajjJes01Up,vbs_dphijjJes01Up,0.0,0.0,mll{0},ngood_jetsJes01Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes02Up      [x] = dfwwbvbscatJes02Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes02Up,vbs_detajjJes02Up,vbs_dphijjJes02Up,0.0,0.0,mll{0},ngood_jetsJes02Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes03Up      [x] = dfwwbvbscatJes03Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes03Up,vbs_detajjJes03Up,vbs_dphijjJes03Up,0.0,0.0,mll{0},ngood_jetsJes03Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes04Up      [x] = dfwwbvbscatJes04Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes04Up,vbs_detajjJes04Up,vbs_dphijjJes04Up,0.0,0.0,mll{0},ngood_jetsJes04Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes05Up      [x] = dfwwbvbscatJes05Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes05Up,vbs_detajjJes05Up,vbs_dphijjJes05Up,0.0,0.0,mll{0},ngood_jetsJes05Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes06Up      [x] = dfwwbvbscatJes06Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes06Up,vbs_detajjJes06Up,vbs_dphijjJes06Up,0.0,0.0,mll{0},ngood_jetsJes06Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes07Up      [x] = dfwwbvbscatJes07Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes07Up,vbs_detajjJes07Up,vbs_dphijjJes07Up,0.0,0.0,mll{0},ngood_jetsJes07Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes08Up      [x] = dfwwbvbscatJes08Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes08Up,vbs_detajjJes08Up,vbs_dphijjJes08Up,0.0,0.0,mll{0},ngood_jetsJes08Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes09Up      [x] = dfwwbvbscatJes09Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes09Up,vbs_detajjJes09Up,vbs_dphijjJes09Up,0.0,0.0,mll{0},ngood_jetsJes09Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes10Up      [x] = dfwwbvbscatJes10Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes10Up,vbs_detajjJes10Up,vbs_dphijjJes10Up,0.0,0.0,mll{0},ngood_jetsJes10Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes11Up      [x] = dfwwbvbscatJes11Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes11Up,vbs_detajjJes11Up,vbs_dphijjJes11Up,0.0,0.0,mll{0},ngood_jetsJes11Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes12Up      [x] = dfwwbvbscatJes12Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes12Up,vbs_detajjJes12Up,vbs_dphijjJes12Up,0.0,0.0,mll{0},ngood_jetsJes12Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes13Up      [x] = dfwwbvbscatJes13Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes13Up,vbs_detajjJes13Up,vbs_dphijjJes13Up,0.0,0.0,mll{0},ngood_jetsJes13Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes14Up      [x] = dfwwbvbscatJes14Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes14Up,vbs_detajjJes14Up,vbs_dphijjJes14Up,0.0,0.0,mll{0},ngood_jetsJes14Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes15Up      [x] = dfwwbvbscatJes15Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes15Up,vbs_detajjJes15Up,vbs_dphijjJes15Up,0.0,0.0,mll{0},ngood_jetsJes15Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes16Up      [x] = dfwwbvbscatJes16Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes16Up,vbs_detajjJes16Up,vbs_dphijjJes16Up,0.0,0.0,mll{0},ngood_jetsJes16Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes17Up      [x] = dfwwbvbscatJes17Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes17Up,vbs_detajjJes17Up,vbs_dphijjJes17Up,0.0,0.0,mll{0},ngood_jetsJes17Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes18Up      [x] = dfwwbvbscatJes18Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes18Up,vbs_detajjJes18Up,vbs_dphijjJes18Up,0.0,0.0,mll{0},ngood_jetsJes18Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes19Up      [x] = dfwwbvbscatJes19Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes19Up,vbs_detajjJes19Up,vbs_dphijjJes19Up,0.0,0.0,mll{0},ngood_jetsJes19Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes20Up      [x] = dfwwbvbscatJes20Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes20Up,vbs_detajjJes20Up,vbs_dphijjJes20Up,0.0,0.0,mll{0},ngood_jetsJes20Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes21Up      [x] = dfwwbvbscatJes21Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes21Up,vbs_detajjJes21Up,vbs_dphijjJes21Up,0.0,0.0,mll{0},ngood_jetsJes21Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes22Up      [x] = dfwwbvbscatJes22Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes22Up,vbs_detajjJes22Up,vbs_dphijjJes22Up,0.0,0.0,mll{0},ngood_jetsJes22Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes23Up      [x] = dfwwbvbscatJes23Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes23Up,vbs_detajjJes23Up,vbs_dphijjJes23Up,0.0,0.0,mll{0},ngood_jetsJes23Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes24Up      [x] = dfwwbvbscatJes24Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes24Up,vbs_detajjJes24Up,vbs_dphijjJes24Up,0.0,0.0,mll{0},ngood_jetsJes24Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes25Up      [x] = dfwwbvbscatJes25Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes25Up,vbs_detajjJes25Up,vbs_dphijjJes25Up,0.0,0.0,mll{0},ngood_jetsJes25Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes26Up      [x] = dfwwbvbscatJes26Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes26Up,vbs_detajjJes26Up,vbs_dphijjJes26Up,0.0,0.0,mll{0},ngood_jetsJes26Up,{1})".format(altMass,varSel))
            dfwwbvbscatJes27Up      [x] = dfwwbvbscatJes27Up      [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJes27Up,vbs_detajjJes27Up,vbs_dphijjJes27Up,0.0,0.0,mll{0},ngood_jetsJes27Up,{1})".format(altMass,varSel))
            dfwwbvbscatJerUp        [x] = dfwwbvbscatJerUp        [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjjJerUp  ,vbs_detajjJerUp  ,vbs_dphijjJerUp  ,0.0,0.0,mll{0},ngood_jetsJerUp  ,{1})".format(altMass,varSel))
            dfwwbvbscatJERUp        [x] = dfwwbvbscatJERUp        [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj       ,vbs_detajj       ,vbs_dphijj       ,0.0,0.0,mll{0},ngood_jets       ,{1})".format(altMass,varSel))
            dfwwbvbscatJESUp        [x] = dfwwbvbscatJESUp        [x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj       ,vbs_detajj       ,vbs_dphijj       ,0.0,0.0,mll{0},ngood_jets       ,{1})".format(altMass,varSel))
            dfwwbvbscatUnclusteredUp[x] = dfwwbvbscatUnclusteredUp[x].Define("finalVar", "compute_jet_lepton_final_var(vbs_mjj       ,vbs_detajj       ,vbs_dphijj       ,0.0,0.0,mll{0},ngood_jets       ,{1})".format(altMass,varSel))

            njString2JCut = " >= 2" # " == 2"
            njString3JCut = " == 3"
            njString4JCut = " >= 4"
            dfwwvbs2Jcat .append(dfwwvbscat[x] .Filter("ngood_jets{0}".format(njString2JCut)))
            dfwwvbs3Jcat .append(dfwwvbscat[x] .Filter("ngood_jets{0}".format(njString3JCut)))
            dfwwvbs4Jcat .append(dfwwvbscat[x] .Filter("ngood_jets{0}".format(njString4JCut)))
            dfwwbvbs2Jcat.append(dfwwbvbscat[x].Filter("ngood_jets{0}".format(njString2JCut)))
            dfwwbvbs3Jcat.append(dfwwbvbscat[x].Filter("ngood_jets{0}".format(njString3JCut)))
            dfwwbvbs4Jcat.append(dfwwbvbscat[x].Filter("ngood_jets{0}".format(njString4JCut)))

            if(makeDataCards == 1 or makeDataCards == 2 or makeDataCards == 5):
                BinXF1 = 16
                minXF1 = -0.5
                maxXF1 = 15.5
            elif(makeDataCards == 3):
                BinXF1 = 12
                minXF1 = -0.5
                maxXF1 = 11.5
            elif(makeDataCards == 4):
                BinXF1 = 15
                minXF1 = -0.5
                maxXF1 = 14.5
            elif(makeDataCards == 6 or makeDataCards == 7 or makeDataCards == 8 or makeDataCards == 9):
                BinXF1 = 8
                minXF1 = -0.5
                maxXF1 =  7.5
            histo[110][x] = dfwwvbscat[x] .Histo1D(("histo_{0}_{1}".format(110,x), "histo_{0}_{1}".format(110,x),BinXF1,minXF1,maxXF1), "finalVar","weight")

            BinXF2 = 4
            minXF2 = -0.5
            maxXF2 =  3.5
            if(makeDataCards == 6 or makeDataCards == 7 or makeDataCards == 8 or makeDataCards == 9):
                BinXF2 = 8
                minXF2 = -0.5
                maxXF2 =  7.5
            histo[111][x] = dfwwbvbscat[x].Histo1D(("histo_{0}_{1}".format(111,x), "histo_{0}_{1}".format(111,x),BinXF2,minXF2,maxXF2), "finalVar","weight")

            # loop over Njets for ssww and sswwb regions (not used)
            for nj in range(0,1):
                njStringCut = njString2JCut
                if(nj == 1):   njStringCut = njString3JCut
                elif(nj == 2): njStringCut = njString4JCut

                startF = 0+nj*400
                if(nj == 0):
                    for nv in range(0,136):
                        histo2D[startF+nv][x] = makeFinalVariable2D(dfwwvbs2Jcat[x],"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,nv)
                elif(nj == 1):
                    for nv in range(0,136):
                        histo2D[startF+nv][x] = makeFinalVariable2D(dfwwvbs3Jcat[x],"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,nv)
                elif(nj == 2):
                    for nv in range(0,136):
                        histo2D[startF+nv][x] = makeFinalVariable2D(dfwwvbs4Jcat[x],"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,nv)
                histo2D[startF+136][x]    = makeFinalVariable2D(dfwwvbscatMuonMomUp    [x].Filter("ngood_jets       {0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,136)
                histo2D[startF+137][x]    = makeFinalVariable2D(dfwwvbscatElectronMomUp[x].Filter("ngood_jets       {0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,137)
                histo2D[startF+138][x]    = makeFinalVariable2D(dfwwvbscatJes00Up      [x].Filter("ngood_jetsJes00Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,138)
                histo2D[startF+139][x]    = makeFinalVariable2D(dfwwvbscatJes01Up      [x].Filter("ngood_jetsJes01Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,139)
                histo2D[startF+140][x]    = makeFinalVariable2D(dfwwvbscatJes02Up      [x].Filter("ngood_jetsJes02Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,140)
                histo2D[startF+141][x]    = makeFinalVariable2D(dfwwvbscatJes03Up      [x].Filter("ngood_jetsJes03Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,141)
                histo2D[startF+142][x]    = makeFinalVariable2D(dfwwvbscatJes04Up      [x].Filter("ngood_jetsJes04Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,142)
                histo2D[startF+143][x]    = makeFinalVariable2D(dfwwvbscatJes05Up      [x].Filter("ngood_jetsJes05Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,143)
                histo2D[startF+144][x]    = makeFinalVariable2D(dfwwvbscatJes06Up      [x].Filter("ngood_jetsJes06Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,144)
                histo2D[startF+145][x]    = makeFinalVariable2D(dfwwvbscatJes07Up      [x].Filter("ngood_jetsJes07Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,145)
                histo2D[startF+146][x]    = makeFinalVariable2D(dfwwvbscatJes08Up      [x].Filter("ngood_jetsJes08Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,146)
                histo2D[startF+147][x]    = makeFinalVariable2D(dfwwvbscatJes09Up      [x].Filter("ngood_jetsJes09Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,147)
                histo2D[startF+148][x]    = makeFinalVariable2D(dfwwvbscatJes10Up      [x].Filter("ngood_jetsJes10Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,148)
                histo2D[startF+149][x]    = makeFinalVariable2D(dfwwvbscatJes11Up      [x].Filter("ngood_jetsJes11Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,149)
                histo2D[startF+150][x]    = makeFinalVariable2D(dfwwvbscatJes12Up      [x].Filter("ngood_jetsJes12Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,150)
                histo2D[startF+151][x]    = makeFinalVariable2D(dfwwvbscatJes13Up      [x].Filter("ngood_jetsJes13Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,151)
                histo2D[startF+152][x]    = makeFinalVariable2D(dfwwvbscatJes14Up      [x].Filter("ngood_jetsJes14Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,152)
                histo2D[startF+153][x]    = makeFinalVariable2D(dfwwvbscatJes15Up      [x].Filter("ngood_jetsJes15Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,153)
                histo2D[startF+154][x]    = makeFinalVariable2D(dfwwvbscatJes16Up      [x].Filter("ngood_jetsJes16Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,154)
                histo2D[startF+155][x]    = makeFinalVariable2D(dfwwvbscatJes17Up      [x].Filter("ngood_jetsJes17Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,155)
                histo2D[startF+156][x]    = makeFinalVariable2D(dfwwvbscatJes18Up      [x].Filter("ngood_jetsJes18Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,156)
                histo2D[startF+157][x]    = makeFinalVariable2D(dfwwvbscatJes19Up      [x].Filter("ngood_jetsJes19Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,157)
                histo2D[startF+158][x]    = makeFinalVariable2D(dfwwvbscatJes20Up      [x].Filter("ngood_jetsJes20Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,158)
                histo2D[startF+159][x]    = makeFinalVariable2D(dfwwvbscatJes21Up      [x].Filter("ngood_jetsJes21Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,159)
                histo2D[startF+160][x]    = makeFinalVariable2D(dfwwvbscatJes22Up      [x].Filter("ngood_jetsJes22Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,160)
                histo2D[startF+161][x]    = makeFinalVariable2D(dfwwvbscatJes23Up      [x].Filter("ngood_jetsJes23Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,161)
                histo2D[startF+162][x]    = makeFinalVariable2D(dfwwvbscatJes24Up      [x].Filter("ngood_jetsJes24Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,162)
                histo2D[startF+163][x]    = makeFinalVariable2D(dfwwvbscatJes25Up      [x].Filter("ngood_jetsJes25Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,163)
                histo2D[startF+164][x]    = makeFinalVariable2D(dfwwvbscatJes26Up      [x].Filter("ngood_jetsJes26Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,164)
                histo2D[startF+165][x]    = makeFinalVariable2D(dfwwvbscatJes27Up      [x].Filter("ngood_jetsJes27Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,165)
                histo2D[startF+166][x]    = makeFinalVariable2D(dfwwvbscatJerUp        [x].Filter("ngood_jetsJerUp  {0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,166)
                histo2D[startF+167][x]    = makeFinalVariable2D(dfwwvbscatJERUp        [x].Filter("ngood_jets       {0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,167)
                histo2D[startF+168][x]    = makeFinalVariable2D(dfwwvbscatJESUp        [x].Filter("ngood_jets       {0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,168)
                histo2D[startF+169][x]    = makeFinalVariable2D(dfwwvbscatUnclusteredUp[x].Filter("ngood_jets       {0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF1,minXF1,maxXF1,BinYF,minYF,maxYF,169)
                if(x == plotCategory("kPlotWS")):
                    startWS = 0+nj*4
                    if(nj == 0):
                        histoWS[0+startWS] = dfwwvbs2Jcat[x].Histo1D(("histoWS_{0}".format(0+startWS), "histoWS_{0}".format(0+startWS), BinXF1,minXF1,maxXF1), "finalVar","weightWSUnc0")
                        histoWS[1+startWS] = dfwwvbs2Jcat[x].Histo1D(("histoWS_{0}".format(1+startWS), "histoWS_{0}".format(1+startWS), BinXF1,minXF1,maxXF1), "finalVar","weightWSUnc1")
                    elif(nj == 1):
                        histoWS[0+startWS] = dfwwvbs3Jcat[x].Histo1D(("histoWS_{0}".format(0+startWS), "histoWS_{0}".format(0+startWS), BinXF1,minXF1,maxXF1), "finalVar","weightWSUnc0")
                        histoWS[1+startWS] = dfwwvbs3Jcat[x].Histo1D(("histoWS_{0}".format(1+startWS), "histoWS_{0}".format(1+startWS), BinXF1,minXF1,maxXF1), "finalVar","weightWSUnc1")
                    elif(nj == 2):
                        histoWS[0+startWS] = dfwwvbs4Jcat[x].Histo1D(("histoWS_{0}".format(0+startWS), "histoWS_{0}".format(0+startWS), BinXF1,minXF1,maxXF1), "finalVar","weightWSUnc0")
                        histoWS[1+startWS] = dfwwvbs4Jcat[x].Histo1D(("histoWS_{0}".format(1+startWS), "histoWS_{0}".format(1+startWS), BinXF1,minXF1,maxXF1), "finalVar","weightWSUnc1")
                if(x == plotCategory("kPlotNonPrompt")):
                    startNonPrompt = 0+nj*12
                    if(nj == 0):
                        histoNonPrompt[0+startNonPrompt] = dfwwvbs2Jcat[x].Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAltm0")
                        histoNonPrompt[1+startNonPrompt] = dfwwvbs2Jcat[x].Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAltm1")
                        histoNonPrompt[2+startNonPrompt] = dfwwvbs2Jcat[x].Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAltm2")
                        histoNonPrompt[3+startNonPrompt] = dfwwvbs2Jcat[x].Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAlte0")
                        histoNonPrompt[4+startNonPrompt] = dfwwvbs2Jcat[x].Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAlte1")
                        histoNonPrompt[5+startNonPrompt] = dfwwvbs2Jcat[x].Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAlte2")
                    elif(nj == 1):
                        histoNonPrompt[0+startNonPrompt] = dfwwvbs3Jcat[x].Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAltm0")
                        histoNonPrompt[1+startNonPrompt] = dfwwvbs3Jcat[x].Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAltm1")
                        histoNonPrompt[2+startNonPrompt] = dfwwvbs3Jcat[x].Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAltm2")
                        histoNonPrompt[3+startNonPrompt] = dfwwvbs3Jcat[x].Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAlte0")
                        histoNonPrompt[4+startNonPrompt] = dfwwvbs3Jcat[x].Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAlte1")
                        histoNonPrompt[5+startNonPrompt] = dfwwvbs3Jcat[x].Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAlte2")
                    elif(nj == 2):
                        histoNonPrompt[0+startNonPrompt] = dfwwvbs4Jcat[x].Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAltm0")
                        histoNonPrompt[1+startNonPrompt] = dfwwvbs4Jcat[x].Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAltm1")
                        histoNonPrompt[2+startNonPrompt] = dfwwvbs4Jcat[x].Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAltm2")
                        histoNonPrompt[3+startNonPrompt] = dfwwvbs4Jcat[x].Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAlte0")
                        histoNonPrompt[4+startNonPrompt] = dfwwvbs4Jcat[x].Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAlte1")
                        histoNonPrompt[5+startNonPrompt] = dfwwvbs4Jcat[x].Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF1,minXF1,maxXF1), "finalVar","weightFakeAlte2")

                startF = 200+nj*400
                if(nj == 0):
                    for nv in range(0,136):
                        histo2D[startF+nv][x] = makeFinalVariable2D(dfwwbvbs2Jcat[x],"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,nv)
                elif(nj == 1):
                    for nv in range(0,136):
                        histo2D[startF+nv][x] = makeFinalVariable2D(dfwwbvbs3Jcat[x],"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,nv)
                elif(nj == 2):
                    for nv in range(0,136):
                        histo2D[startF+nv][x] = makeFinalVariable2D(dfwwbvbs4Jcat[x],"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,nv)
                histo2D[startF+136][x]    = makeFinalVariable2D(dfwwbvbscatMuonMomUp    [x].Filter("ngood_jets       {0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,136)
                histo2D[startF+137][x]    = makeFinalVariable2D(dfwwbvbscatElectronMomUp[x].Filter("ngood_jets       {0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,137)
                histo2D[startF+138][x]    = makeFinalVariable2D(dfwwbvbscatJes00Up      [x].Filter("ngood_jetsJes00Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,138)
                histo2D[startF+139][x]    = makeFinalVariable2D(dfwwbvbscatJes01Up      [x].Filter("ngood_jetsJes01Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,139)
                histo2D[startF+140][x]    = makeFinalVariable2D(dfwwbvbscatJes02Up      [x].Filter("ngood_jetsJes02Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,140)
                histo2D[startF+141][x]    = makeFinalVariable2D(dfwwbvbscatJes03Up      [x].Filter("ngood_jetsJes03Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,141)
                histo2D[startF+142][x]    = makeFinalVariable2D(dfwwbvbscatJes04Up      [x].Filter("ngood_jetsJes04Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,142)
                histo2D[startF+143][x]    = makeFinalVariable2D(dfwwbvbscatJes05Up      [x].Filter("ngood_jetsJes05Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,143)
                histo2D[startF+144][x]    = makeFinalVariable2D(dfwwbvbscatJes06Up      [x].Filter("ngood_jetsJes06Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,144)
                histo2D[startF+145][x]    = makeFinalVariable2D(dfwwbvbscatJes07Up      [x].Filter("ngood_jetsJes07Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,145)
                histo2D[startF+146][x]    = makeFinalVariable2D(dfwwbvbscatJes08Up      [x].Filter("ngood_jetsJes08Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,146)
                histo2D[startF+147][x]    = makeFinalVariable2D(dfwwbvbscatJes09Up      [x].Filter("ngood_jetsJes09Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,147)
                histo2D[startF+148][x]    = makeFinalVariable2D(dfwwbvbscatJes10Up      [x].Filter("ngood_jetsJes10Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,148)
                histo2D[startF+149][x]    = makeFinalVariable2D(dfwwbvbscatJes11Up      [x].Filter("ngood_jetsJes11Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,149)
                histo2D[startF+150][x]    = makeFinalVariable2D(dfwwbvbscatJes12Up      [x].Filter("ngood_jetsJes12Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,150)
                histo2D[startF+151][x]    = makeFinalVariable2D(dfwwbvbscatJes13Up      [x].Filter("ngood_jetsJes13Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,151)
                histo2D[startF+152][x]    = makeFinalVariable2D(dfwwbvbscatJes14Up      [x].Filter("ngood_jetsJes14Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,152)
                histo2D[startF+153][x]    = makeFinalVariable2D(dfwwbvbscatJes15Up      [x].Filter("ngood_jetsJes15Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,153)
                histo2D[startF+154][x]    = makeFinalVariable2D(dfwwbvbscatJes16Up      [x].Filter("ngood_jetsJes16Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,154)
                histo2D[startF+155][x]    = makeFinalVariable2D(dfwwbvbscatJes17Up      [x].Filter("ngood_jetsJes17Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,155)
                histo2D[startF+156][x]    = makeFinalVariable2D(dfwwbvbscatJes18Up      [x].Filter("ngood_jetsJes18Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,156)
                histo2D[startF+157][x]    = makeFinalVariable2D(dfwwbvbscatJes19Up      [x].Filter("ngood_jetsJes19Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,157)
                histo2D[startF+158][x]    = makeFinalVariable2D(dfwwbvbscatJes20Up      [x].Filter("ngood_jetsJes20Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,158)
                histo2D[startF+159][x]    = makeFinalVariable2D(dfwwbvbscatJes21Up      [x].Filter("ngood_jetsJes21Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,159)
                histo2D[startF+160][x]    = makeFinalVariable2D(dfwwbvbscatJes22Up      [x].Filter("ngood_jetsJes22Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,160)
                histo2D[startF+161][x]    = makeFinalVariable2D(dfwwbvbscatJes23Up      [x].Filter("ngood_jetsJes23Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,161)
                histo2D[startF+162][x]    = makeFinalVariable2D(dfwwbvbscatJes24Up      [x].Filter("ngood_jetsJes24Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,162)
                histo2D[startF+163][x]    = makeFinalVariable2D(dfwwbvbscatJes25Up      [x].Filter("ngood_jetsJes25Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,163)
                histo2D[startF+164][x]    = makeFinalVariable2D(dfwwbvbscatJes26Up      [x].Filter("ngood_jetsJes26Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,164)
                histo2D[startF+165][x]    = makeFinalVariable2D(dfwwbvbscatJes27Up      [x].Filter("ngood_jetsJes27Up{0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,165)
                histo2D[startF+166][x]    = makeFinalVariable2D(dfwwbvbscatJerUp        [x].Filter("ngood_jetsJerUp  {0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,166)
                histo2D[startF+167][x]    = makeFinalVariable2D(dfwwbvbscatJERUp        [x].Filter("ngood_jets       {0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,167)
                histo2D[startF+168][x]    = makeFinalVariable2D(dfwwbvbscatJESUp        [x].Filter("ngood_jets       {0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,168)
                histo2D[startF+169][x]    = makeFinalVariable2D(dfwwbvbscatUnclusteredUp[x].Filter("ngood_jets       {0}".format(njStringCut)),"finalVar","theGenCat",theCat,startF,x,BinXF2,minXF2,maxXF2,BinYF,minYF,maxYF,169)
                if(x == plotCategory("kPlotWS")):
                    startWS = 2+nj*4
                    if(nj == 0):
                        histoWS[0+startWS] = dfwwbvbs2Jcat[x].Histo1D(("histoWS_{0}".format(0+startWS), "histoWS_{0}".format(0+startWS), BinXF2,minXF2,maxXF2), "finalVar","weightWSUnc0")
                        histoWS[1+startWS] = dfwwbvbs2Jcat[x].Histo1D(("histoWS_{0}".format(1+startWS), "histoWS_{0}".format(1+startWS), BinXF2,minXF2,maxXF2), "finalVar","weightWSUnc1")
                    elif(nj == 1):
                        histoWS[0+startWS] = dfwwbvbs3Jcat[x].Histo1D(("histoWS_{0}".format(0+startWS), "histoWS_{0}".format(0+startWS), BinXF2,minXF2,maxXF2), "finalVar","weightWSUnc0")
                        histoWS[1+startWS] = dfwwbvbs3Jcat[x].Histo1D(("histoWS_{0}".format(1+startWS), "histoWS_{0}".format(1+startWS), BinXF2,minXF2,maxXF2), "finalVar","weightWSUnc1")
                    elif(nj == 2):
                        histoWS[0+startWS] = dfwwbvbs4Jcat[x].Histo1D(("histoWS_{0}".format(0+startWS), "histoWS_{0}".format(0+startWS), BinXF2,minXF2,maxXF2), "finalVar","weightWSUnc0")
                        histoWS[1+startWS] = dfwwbvbs4Jcat[x].Histo1D(("histoWS_{0}".format(1+startWS), "histoWS_{0}".format(1+startWS), BinXF2,minXF2,maxXF2), "finalVar","weightWSUnc1")
                if(x == plotCategory("kPlotNonPrompt")):
                    startNonPrompt = 6+nj*12
                    if(nj == 0):
                        histoNonPrompt[0+startNonPrompt] = dfwwbvbs2Jcat[x].Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAltm0")
                        histoNonPrompt[1+startNonPrompt] = dfwwbvbs2Jcat[x].Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAltm1")
                        histoNonPrompt[2+startNonPrompt] = dfwwbvbs2Jcat[x].Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAltm2")
                        histoNonPrompt[3+startNonPrompt] = dfwwbvbs2Jcat[x].Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAlte0")
                        histoNonPrompt[4+startNonPrompt] = dfwwbvbs2Jcat[x].Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAlte1")
                        histoNonPrompt[5+startNonPrompt] = dfwwbvbs2Jcat[x].Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAlte2")
                    elif(nj == 1):
                        histoNonPrompt[0+startNonPrompt] = dfwwbvbs3Jcat[x].Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAltm0")
                        histoNonPrompt[1+startNonPrompt] = dfwwbvbs3Jcat[x].Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAltm1")
                        histoNonPrompt[2+startNonPrompt] = dfwwbvbs3Jcat[x].Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAltm2")
                        histoNonPrompt[3+startNonPrompt] = dfwwbvbs3Jcat[x].Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAlte0")
                        histoNonPrompt[4+startNonPrompt] = dfwwbvbs3Jcat[x].Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAlte1")
                        histoNonPrompt[5+startNonPrompt] = dfwwbvbs3Jcat[x].Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAlte2")
                    elif(nj == 2):
                        histoNonPrompt[0+startNonPrompt] = dfwwbvbs4Jcat[x].Histo1D(("histoNonPrompt_{0}".format(0+startNonPrompt), "histoNonPrompt_{0}".format(0+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAltm0")
                        histoNonPrompt[1+startNonPrompt] = dfwwbvbs4Jcat[x].Histo1D(("histoNonPrompt_{0}".format(1+startNonPrompt), "histoNonPrompt_{0}".format(1+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAltm1")
                        histoNonPrompt[2+startNonPrompt] = dfwwbvbs4Jcat[x].Histo1D(("histoNonPrompt_{0}".format(2+startNonPrompt), "histoNonPrompt_{0}".format(2+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAltm2")
                        histoNonPrompt[3+startNonPrompt] = dfwwbvbs4Jcat[x].Histo1D(("histoNonPrompt_{0}".format(3+startNonPrompt), "histoNonPrompt_{0}".format(3+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAlte0")
                        histoNonPrompt[4+startNonPrompt] = dfwwbvbs4Jcat[x].Histo1D(("histoNonPrompt_{0}".format(4+startNonPrompt), "histoNonPrompt_{0}".format(4+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAlte1")
                        histoNonPrompt[5+startNonPrompt] = dfwwbvbs4Jcat[x].Histo1D(("histoNonPrompt_{0}".format(5+startNonPrompt), "histoNonPrompt_{0}".format(5+startNonPrompt), BinXF2,minXF2,maxXF2), "finalVar","weightFakeAlte2")

    report = []
    for x in range(nCat):
        report.append(dfwwvbscat[x].Report())
        if(x != theCat): continue
        print("---------------- SUMMARY {0} -------------".format(x))
        report[x].Print()

    if(makeDataCards >= 1):
        for j in range(0,nHistoMVA):
            if((j >= 0 and j < 200) or (j >= 400 and j < 600) or (j >= 800 and j < 1000)):
                for x in range(nCat):
                    histoMVA[j][x] = ROOT.TH1D("histoMVA_{0}_{1}".format(j,x), "histoMVA_{0}_{1}".format(j,x), BinXF1,minXF1,maxXF1)
            else:
                for x in range(nCat):
                    histoMVA[j][x] = ROOT.TH1D("histoMVA_{0}_{1}".format(j,x), "histoMVA_{0}_{1}".format(j,x), BinXF2,minXF2,maxXF2)

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

            if(x == plotCategory("kPlotEWKSSWW")):
                histoMVA[j][plotCategory("kPlotEWKSSWW")].SetBinError(1,0.0)
                histoMVA[j][plotCategory("kPlotSignal0")].SetBinError(1,0.0)
                histoMVA[j][plotCategory("kPlotSignal1")].SetBinError(1,0.0)
                histoMVA[j][plotCategory("kPlotSignal2")].SetBinError(1,0.0)
                histoMVA[j][plotCategory("kPlotSignal3")].SetBinError(1,0.0)
                for i in range(histoMVA[j][x].GetNbinsX()):
                    histoMVA[j][plotCategory("kPlotEWKSSWW")].SetBinContent(i+1,        histoMVA[j][plotCategory("kPlotEWKSSWW")].GetBinContent(i+1)+       histo2D[j][x].GetBinContent(i+1,1))
                    histoMVA[j][plotCategory("kPlotEWKSSWW")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotEWKSSWW")].GetBinError  (i+1),2)+pow(histo2D[j][x].GetBinError  (i+1,1),2),0.5))

                    histoMVA[j][plotCategory("kPlotSignal0")].SetBinContent(i+1,        histoMVA[j][plotCategory("kPlotSignal0")].GetBinContent(i+1)+       histo2D[j][x].GetBinContent(i+1,2))
                    histoMVA[j][plotCategory("kPlotSignal0")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotSignal0")].GetBinError  (i+1),2)+pow(histo2D[j][x].GetBinError  (i+1,2),2),0.5))

                    histoMVA[j][plotCategory("kPlotSignal1")].SetBinContent(i+1,        histoMVA[j][plotCategory("kPlotSignal1")].GetBinContent(i+1)+       histo2D[j][x].GetBinContent(i+1,3))
                    histoMVA[j][plotCategory("kPlotSignal1")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotSignal1")].GetBinError  (i+1),2)+pow(histo2D[j][x].GetBinError  (i+1,3),2),0.5))

                    histoMVA[j][plotCategory("kPlotSignal2")].SetBinContent(i+1,        histoMVA[j][plotCategory("kPlotSignal2")].GetBinContent(i+1)+       histo2D[j][x].GetBinContent(i+1,4))
                    histoMVA[j][plotCategory("kPlotSignal2")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotSignal2")].GetBinError  (i+1),2)+pow(histo2D[j][x].GetBinError  (i+1,4),2),0.5))

                    histoMVA[j][plotCategory("kPlotSignal3")].SetBinContent(i+1,        histoMVA[j][plotCategory("kPlotSignal3")].GetBinContent(i+1)+       histo2D[j][x].GetBinContent(i+1,5))
                    histoMVA[j][plotCategory("kPlotSignal3")].SetBinError  (i+1,pow(pow(histoMVA[j][plotCategory("kPlotSignal3")].GetBinError  (i+1),2)+pow(histo2D[j][x].GetBinError  (i+1,5),2),0.5))

            else:
                for i in range(histoMVA[j][x].GetNbinsX()):
                    histoMVA[j][x].SetBinContent(i+1,        histoMVA[j][x].GetBinContent(i+1)+       histo2D[j][x].GetBinContent(i+1,1))
                    histoMVA[j][x].SetBinError  (i+1,pow(pow(histoMVA[j][x].GetBinError  (i+1),2)+pow(histo2D[j][x].GetBinError  (i+1,1),2),0.5))

    if (isData == "true"):
        output_dir2 = "/mnt/home/mghimiray/VBSStudies/Outputs_VBS/matrix_method/histo/fillhisto_sswwAnalysis/" 
    elif (isData == "false"):
        output_dir2 = "/mnt/home/mghimiray/VBSStudies/Outputs_VBS/OriginalTT/histo/fillhisto_sswwAnalysis/" # Defining output directory for histograms


    myfile = ROOT.TFile("{3}/fillhisto_sswwAnalysis1001_sample{0}_year{1}_job{2}.root".format(count,year,whichJob,output_dir2),'RECREATE')
    for i in range(nCat):
        for j in range(nHisto):
            if(histo[j][i] == 0): continue
            histo[j][i].Write()
        for j in range(nHistoMVA):
            if(histoMVA[j][i] == 0): continue
            histoMVA[j][i].Write()
    for i in range(nhistoWS):
        if(histoWS[i] == 0): continue
        histoWS[i].Write()
    for i in range(nhistoNonPrompt):
        if(histoNonPrompt[i] == 0): continue
        histoNonPrompt[i].Write()
    myfile.Close()

def readMCSample(sampleNOW,year,skimType,whichJob,group,ewkCorrWeights,wsWeights,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3):

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
    if(SwitchSample(sampleNOW,skimType)[2] == plotCategory("kPlotEWKSSWW") or
       SwitchSample(sampleNOW,skimType)[2] == plotCategory("kPlotWZ") or
       SwitchSample(sampleNOW,skimType)[2] == plotCategory("kPlotEWKWZ")):
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

    analysis(df,sampleNOW,SwitchSample(sampleNOW,skimType)[2],weight,year,PDType,"false",whichJob,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,ewkCorrWeights,wsWeights,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3)

def readDASample(sampleNOW,year,skimType,whichJob,group,ewkCorrWeights,wsWeights,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3):

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

    analysis(df,sampleNOW,sampleNOW,weight,year,PDType,"true",whichJob,0,genEventSumLHEScaleRenorm,genEventSumPSRenorm,ewkCorrWeights,wsWeights,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3)

if __name__ == "__main__":

    group = 10

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

    ewkCorrWeights = []
    ewkCorrPath = "data/VV_NLO_LO_CMS_mjj.root"
    fewkCorrFile = ROOT.TFile(ewkCorrPath)
    ewkCorrWeights.append(fewkCorrFile.Get("hWW_KF_CMS"))
    ewkCorrWeights.append(fewkCorrFile.Get("hWZ_KF_CMS"))
    ewkCorrWeights.append(fewkCorrFile.Get("hWW_KF_CMSUp"))
    ewkCorrWeights.append(fewkCorrFile.Get("hWZ_KF_CMSUp"))
    for x in range(4):
        ewkCorrWeights[x].SetDirectory(0)
    fewkCorrFile.Close()

    wsWeights = []
    wsPath = "data/histoWSSF_{0}.root".format(year)
    fwsFile = ROOT.TFile(wsPath)
    wsWeights.append(fwsFile.Get("histoWSEtaSF"))
    wsWeights.append(fwsFile.Get("histoWSEtaSF_unc"))
    wsWeights.append(fwsFile.Get("histoWSEtaPtSF"))
    for x in range(3):
        wsWeights[x].SetDirectory(0)
    fwsFile.Close()

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
    if(whichAna == 3):
        fakePath = "data/histoFakeEtaPt_ptlcone_{0}.root".format(year)
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
            readMCSample(process,year,skimType,whichJob,group,ewkCorrWeights,wsWeights,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3)
        elif(process >= 1000):
            readDASample(process,year,skimType,whichJob,group,ewkCorrWeights,wsWeights,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3)
    except Exception as e:
        print("FAILED {0}".format(e))
