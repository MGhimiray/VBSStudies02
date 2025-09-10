import ROOT
import os, sys, getopt, json
from array import array

ROOT.ROOT.EnableImplicitMT(10)
from utilsCategory import plotCategory
from utilsAna import getMClist, getDATAlist
from utilsAna import SwitchSample, groupFiles, getTriggerFromJson, getLeptomSelFromJson, getLumi
from utilsSelection import selectionJetMet, selectionElMu, selectionTrigger1L

# 0 = T, 1 = M, 2 = L
bTagSel = 1

useFR = 1

selectionJsonPath = "config/selection.json"

with open(selectionJsonPath) as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

JSON = jsonObject['JSON']

VBSSEL = jsonObject['VBSSEL']

def selection1L(df,year,PDType,isData,TRIGGERFAKEMU,TRIGGERFAKEEL,count):

    dftag = selectionTrigger1L(df,year,PDType,JSON,isData,TRIGGERFAKEMU,TRIGGERFAKEEL)

    overallLeptonSel = jsonObject['leptonSel']
    FAKE_MU   = getLeptomSelFromJson(overallLeptonSel, "FAKE_MU",   year)
    TIGHT_MU0 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU0", year)
    TIGHT_MU1 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU1", year)
    TIGHT_MU2 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU2", year)
    TIGHT_MU3 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU3", year)
    TIGHT_MU4 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU4", year)
    TIGHT_MU5 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU5", year)
    TIGHT_MU6 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU6", year)
    TIGHT_MU7 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU7", year)
    TIGHT_MU8 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU8", year)

    FAKE_EL   = getLeptomSelFromJson(overallLeptonSel, "FAKE_EL",   year)
    TIGHT_EL0 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL0", year)
    TIGHT_EL1 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL1", year)
    TIGHT_EL2 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL2", year)
    TIGHT_EL3 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL3", year)
    TIGHT_EL4 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL4", year)
    TIGHT_EL5 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL5", year)
    TIGHT_EL6 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL6", year)
    TIGHT_EL7 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL7", year)
    TIGHT_EL8 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL8", year)

    dftag = selectionElMu(dftag,year,FAKE_MU,TIGHT_MU0,FAKE_EL,TIGHT_EL0)

    dftag =(dftag.Filter("nLoose == 1","Only one loose lepton")
                 .Filter("nFake == 1","Only one fake lepton")
                 .Define("tight_mu0", "{0}".format(TIGHT_MU0))
                 .Define("tight_mu1", "{0}".format(TIGHT_MU1))
                 .Define("tight_mu2", "{0}".format(TIGHT_MU2))
                 .Define("tight_mu3", "{0}".format(TIGHT_MU3))
                 .Define("tight_mu4", "{0}".format(TIGHT_MU4))
                 .Define("tight_mu5", "{0}".format(TIGHT_MU5))
                 .Define("tight_mu6", "{0}".format(TIGHT_MU6))
                 .Define("tight_mu7", "{0}".format(TIGHT_MU7))
                 .Define("tight_mu8", "{0}".format(TIGHT_MU8))
                 .Define("tight_el0", "{0}".format(TIGHT_EL0))
                 .Define("tight_el1", "{0}".format(TIGHT_EL1))
                 .Define("tight_el2", "{0}".format(TIGHT_EL2))
                 .Define("tight_el3", "{0}".format(TIGHT_EL3))
                 .Define("tight_el4", "{0}".format(TIGHT_EL4))
                 .Define("tight_el5", "{0}".format(TIGHT_EL5))
                 .Define("tight_el6", "{0}".format(TIGHT_EL6))
                 .Define("tight_el7", "{0}".format(TIGHT_EL7))
                 .Define("tight_el8", "{0}".format(TIGHT_EL8))
                 .Define("mt"      ,"compute_lmet_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_jetRelIso, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_jetRelIso, PuppiMET_pt, PuppiMET_phi,0)")
                 .Define("dphilmet","compute_lmet_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_jetRelIso, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_jetRelIso, PuppiMET_pt, PuppiMET_phi,1)")
                 .Define("mtfix"   ,"compute_lmet_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_jetRelIso, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_jetRelIso, PuppiMET_pt, PuppiMET_phi,2)")
                 .Define("ptl"     ,"compute_lmet_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_jetRelIso, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_jetRelIso, PuppiMET_pt, PuppiMET_phi,3)")
                 .Define("etal"    ,"compute_lmet_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_jetRelIso, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_jetRelIso, PuppiMET_pt, PuppiMET_phi,4)")
                 .Define("phil"    ,"compute_lmet_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_jetRelIso, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_jetRelIso, PuppiMET_pt, PuppiMET_phi,5)")
                 .Define("absetal" ,"compute_lmet_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_jetRelIso, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_jetRelIso, PuppiMET_pt, PuppiMET_phi,6)")
                 .Define("ptlcone" ,"compute_lmet_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_jetRelIso, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_jetRelIso, PuppiMET_pt, PuppiMET_phi,7)")
                 .Define("sumMETMT","PuppiMET_pt+mt")
                 .Define("sumMETMTFIX","PuppiMET_pt+mtfix")
                )

    dftag = selectionJetMet(dftag,year,bTagSel,isData,count,5.0)

    return dftag

def analysis(df,count,category,weight,year,PDType,isData,whichJob,puWeights):

    print("starting {0} / {1} / {2} / {3} / {4} / {5} / {6}".format(count,category,weight,year,PDType,isData,whichJob))

    xPtDistBins = array('d', [10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 100.0])
    xPtBins     = array('d', [10.0, 15.0, 20.0, 25.0, 30.0, 40.0])
    xEtaBins = array('d', [0.0, 0.5, 1.0, 1.5, 2.0, 2.5])
    totalxPtDistBins = len(xPtDistBins)-1

    theCat = category
    if(theCat > 100): theCat = plotCategory("kPlotData")

    mtfixCut = 30

    nCat, nHisto = plotCategory("kPlotCategories"), 500
    histo   = [[0 for y in range(nCat)] for x in range(nHisto)]
    histo2D = [[0 for y in range(nCat)] for x in range(nHisto)]

    ROOT.initHisto1D(puWeights,0)

    ROOT.initJSONSFs(year)

    overallTriggers = jsonObject['triggers']
    TRIGGERFAKEMU = getTriggerFromJson(overallTriggers, "TRIGGERFAKEMU", year)
    TRIGGERFAKEEL = getTriggerFromJson(overallTriggers, "TRIGGERFAKEEL", year)

    list_TRIGGERFAKEMU = TRIGGERFAKEMU.split('(')[1].split(')')[0].split('||')
    list_TRIGGERFAKEEL = TRIGGERFAKEEL.split('(')[1].split(')')[0].split('||')
    list_TRIGGERFAKE = list_TRIGGERFAKEMU
    list_TRIGGERFAKE.extend(list_TRIGGERFAKEEL)
    print("Total number of fake trigger paths: {0}".format(len(list_TRIGGERFAKE)))

    dfbase = selection1L(df,year,PDType,isData,TRIGGERFAKEMU,TRIGGERFAKEEL,count)

    if(theCat == plotCategory("kPlotData")):
        dfbase = (dfbase.Define("weight","1.0")
                        .Define("weightFakeSel0", "1.0")
                        .Define("weightFakeSel1", "1.0")
                        .Define("weightFakeSel2", "1.0")
                        )
    elif(theCat == plotCategory("kPlotNonPrompt")):
        dfbase =(dfbase.Define("PDType","\"{0}\"".format(PDType))
                       .Define("fake_Muon_genPartFlav","Muon_genPartFlav[fake_mu]")
                       .Define("fake_Electron_genPartFlav","Electron_genPartFlav[fake_el]")
                       .Define("weightPURecoSF","compute_PURecoSF(fake_Muon_pt,fake_Muon_eta,fake_Electron_pt,fake_Electron_eta,Pileup_nTrueInt,0)")
                       .Define("weight","compute_weights({0},genWeight,PDType,fake_Muon_genPartFlav,fake_Electron_genPartFlav,{1})*compute_lumiFakeRate(fake_Muon_pt,fake_Electron_pt,-1,{2})*weightPURecoSF".format(weight,0,year))
                       .Filter("weight != 0","good weight")
                       .Define("weightFakeSel0", "compute_weights({0},genWeight,PDType,fake_Muon_genPartFlav,fake_Electron_genPartFlav,{1})*compute_lumiFakeRate(fake_Muon_pt,fake_Electron_pt,0,{2})*weightPURecoSF".format(weight,0,year))
                       .Define("weightFakeSel1", "compute_weights({0},genWeight,PDType,fake_Muon_genPartFlav,fake_Electron_genPartFlav,{1})*compute_lumiFakeRate(fake_Muon_pt,fake_Electron_pt,1,{2})*weightPURecoSF".format(weight,0,year))
                       .Define("weightFakeSel2", "compute_weights({0},genWeight,PDType,fake_Muon_genPartFlav,fake_Electron_genPartFlav,{1})*compute_lumiFakeRate(fake_Muon_pt,fake_Electron_pt,2,{2})*weightPURecoSF".format(weight,0,year))
                       )
    else:
        dfbase =(dfbase.Define("PDType","\"{0}\"".format(PDType))
                       .Define("fake_Muon_genPartFlav","Muon_genPartFlav[fake_mu]")
                       .Define("fake_Electron_genPartFlav","Electron_genPartFlav[fake_el]")
                       .Define("weightPURecoSF","compute_PURecoSF(fake_Muon_pt,fake_Muon_eta,fake_Electron_pt,fake_Electron_eta,Pileup_nTrueInt,0)")
                       .Define("weight","compute_weights({0},genWeight,PDType,fake_Muon_genPartFlav,fake_Electron_genPartFlav,{1})*compute_lumiFakeRate(fake_Muon_pt,fake_Electron_pt,-1,{2})*weightPURecoSF".format(weight,useFR,year))
                       .Filter("weight != 0","good weight")
                       .Define("weightFakeSel0", "compute_weights({0},genWeight,PDType,fake_Muon_genPartFlav,fake_Electron_genPartFlav,{1})*compute_lumiFakeRate(fake_Muon_pt,fake_Electron_pt,0,{2})*weightPURecoSF".format(weight,useFR,year))
                       .Define("weightFakeSel1", "compute_weights({0},genWeight,PDType,fake_Muon_genPartFlav,fake_Electron_genPartFlav,{1})*compute_lumiFakeRate(fake_Muon_pt,fake_Electron_pt,1,{2})*weightPURecoSF".format(weight,useFR,year))
                       .Define("weightFakeSel2", "compute_weights({0},genWeight,PDType,fake_Muon_genPartFlav,fake_Electron_genPartFlav,{1})*compute_lumiFakeRate(fake_Muon_pt,fake_Electron_pt,2,{2})*weightPURecoSF".format(weight,useFR,year))
                       )

    FILTERMU0 = "(Sum(fake_mu) == 1 && ptl <  20 && HLT_Mu8_TrkIsoVVL)"
    FILTERMU1 = "(Sum(fake_mu) == 1 && ptl >= 20 && HLT_Mu17_TrkIsoVVL)"
    FILTEREL0 = "(Sum(fake_el) == 1 && ptl <  15 && HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30)"
    FILTEREL1 = "(Sum(fake_el) == 1 && ptl >= 15 && HLT_Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30)"
    FILTERLEP = "({0}||{1}||{2}||{3})".format(FILTERMU0,FILTERMU1,FILTEREL0,FILTEREL1)
    FILTERLEP0 = "({0}||{1})".format(FILTERMU0,FILTEREL0)
    FILTERLEP1 = "({0}||{1})".format(FILTERMU1,FILTEREL1)
    list_FILTERLEP = [FILTERLEP0, FILTERLEP1]
    print("FILTERMU0: {0}".format(FILTERMU0))
    print("FILTERMU1: {0}".format(FILTERMU1))
    print("FILTEREL0: {0}".format(FILTEREL0))
    print("FILTEREL1: {0}".format(FILTEREL1))

    tagTriggerMuSel0 = "(Sum(fake_mu) == 1 and hasTriggerMatch(fake_Muon_eta[0],fake_Muon_phi[0],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,13,0))"
    tagTriggerElSel0 = "(Sum(fake_el) == 1 and hasTriggerMatch(fake_Electron_eta[0],fake_Electron_phi[0],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,11,0))"
    tagTriggerSel0 = "({0} || {1})".format(tagTriggerMuSel0,tagTriggerElSel0)

    tagTriggerMuSel1 = "(Sum(fake_mu) == 1 and hasTriggerMatch(fake_Muon_eta[0],fake_Muon_phi[0],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,13,1))"
    tagTriggerElSel1 = "(Sum(fake_el) == 1 and hasTriggerMatch(fake_Electron_eta[0],fake_Electron_phi[0],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,11,1))"
    tagTriggerSel1 = "({0} || {1})".format(tagTriggerMuSel1,tagTriggerElSel1)

    tagTriggerMuSel2 = "(Sum(fake_mu) == 1 and hasTriggerMatch(fake_Muon_eta[0],fake_Muon_phi[0],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,13,2))"
    tagTriggerElSel2 = "(Sum(fake_el) == 1 and hasTriggerMatch(fake_Electron_eta[0],fake_Electron_phi[0],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,11,2))"
    tagTriggerSel2 = "({0} || {1})".format(tagTriggerMuSel2,tagTriggerElSel2)

    tagTriggerMuSel3 = "(Sum(fake_mu) == 1 and hasTriggerMatch(fake_Muon_eta[0],fake_Muon_phi[0],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,13,0,0))"
    tagTriggerElSel3 = "(Sum(fake_el) == 1 and hasTriggerMatch(fake_Electron_eta[0],fake_Electron_phi[0],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,11,0,0))"
    tagTriggerSel3 = "({0} || {1})".format(tagTriggerMuSel3,tagTriggerElSel3)

    dfcat = []
    dffakecat = []
    dfjet30cat = []
    dfjet50cat = []
    dfbjet20cat = []
    dftrgcat = []
    dfptcat = []
    for y in range(nCat):
        for ltype in range(2):
            dfcat.append(dfbase.Filter("Sum(fake_mu)+2*Sum(fake_el)-1=={0}".format(ltype), "flavor type == {0}".format(ltype))
                               .Define("kPlotNonPrompt", "{0}".format(plotCategory("kPlotNonPrompt")))
                               .Define("kPlotWS", "{0}".format(plotCategory("kPlotWS")))
                               .Define("theCat{0}".format(y), "compute_category({0},kPlotNonPrompt,kPlotWS,1,1,0)".format(theCat))
                               .Filter("theCat{0}=={1}".format(y,y), "correct category ({0})".format(y))
                               .Filter("ptl < {0}".format(xPtDistBins[len(xPtDistBins)-1]), "ptl < {0}".format(xPtDistBins[len(xPtDistBins)-1]))
                               )

            for trgfake in range(3):
                if(ltype == 0):
                    dftrgcat.append(dfcat[2*y+ltype].Filter("{0}".format(list_TRIGGERFAKEMU[trgfake])))
                else:
                    dftrgcat.append(dfcat[2*y+ltype].Filter("{0}".format(list_TRIGGERFAKEEL[trgfake])))

                histo[trgfake+3*ltype+ 0][y] = dftrgcat[(2*y+ltype)*3+trgfake].Histo1D(("histo_{0}_{1}".format(trgfake+3*ltype+ 0,y), "histo_{0}_{1}".format(trgfake+3*ltype+ 0,y),90, 10, 100), "ptl","weightFakeSel{0}".format(trgfake))
                histo[trgfake+3*ltype+ 6][y] = dftrgcat[(2*y+ltype)*3+trgfake].Histo1D(("histo_{0}_{1}".format(trgfake+3*ltype+ 6,y), "histo_{0}_{1}".format(trgfake+3*ltype+ 6,y),50,0.0,2.5), "absetal","weightFakeSel{0}".format(trgfake))
                histo[trgfake+3*ltype+12][y] = dftrgcat[(2*y+ltype)*3+trgfake].Histo1D(("histo_{0}_{1}".format(trgfake+3*ltype+12,y), "histo_{0}_{1}".format(trgfake+3*ltype+12,y),90, 10, 100), "ptlcone","weightFakeSel{0}".format(trgfake))

            dfcat[2*y+ltype] = dfcat[2*y+ltype].Filter(FILTERLEP)

            histo[ltype+18][y] = dfcat[2*y+ltype].Histo1D(("histo_{0}_{1}".format(ltype+18,y), "histo_{0}_{1}".format(ltype+18,y),90, 10, 100), "ptl","weight")

            for npt in range(totalxPtDistBins):
                dfptcat.append(dfcat[2*y+ltype].Filter("ptl > {0} && ptl < {1}".format(xPtDistBins[npt],xPtDistBins[npt+1])))

                histo[npt+totalxPtDistBins*ltype+ 20][y] = dfptcat[(2*y+ltype)*totalxPtDistBins+npt].Histo1D(("histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+ 20,y), "histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+ 20,y),40, 0, 200), "mt","weight")
                histo[npt+totalxPtDistBins*ltype+ 40][y] = dfptcat[(2*y+ltype)*totalxPtDistBins+npt].Histo1D(("histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+ 40,y), "histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+ 40,y),40, 0, 200), "mtfix","weight")
                histo[npt+totalxPtDistBins*ltype+ 60][y] = dfptcat[(2*y+ltype)*totalxPtDistBins+npt].Histo1D(("histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+ 60,y), "histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+ 60,y),40, 0, 200), "PuppiMET_pt","weight")
                histo[npt+totalxPtDistBins*ltype+ 80][y] = dfptcat[(2*y+ltype)*totalxPtDistBins+npt].Histo1D(("histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+ 80,y), "histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+ 80,y),40, 0, 200), "sumMETMT","weight")
                histo[npt+totalxPtDistBins*ltype+100][y] = dfptcat[(2*y+ltype)*totalxPtDistBins+npt].Histo1D(("histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+100,y), "histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+100,y),40, 0, 200), "sumMETMTFIX","weight")
                if(ltype == 0):
                    histo[npt+totalxPtDistBins*ltype+120][y] = dfptcat[(2*y+ltype)*totalxPtDistBins+npt].Filter("Sum(tight_mu2)==1").Histo1D(("histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+120,y), "histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+120,y),40, 0, 200), "mtfix","weight")
                if(ltype == 1):
                    histo[npt+totalxPtDistBins*ltype+120][y] = dfptcat[(2*y+ltype)*totalxPtDistBins+npt].Filter("Sum(tight_el3)==1").Histo1D(("histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+120,y), "histo_{0}_{1}".format(npt+totalxPtDistBins*ltype+120,y),40, 0, 200), "mtfix","weight")

            dffakecat.append(dfcat[2*y+ltype].Filter("mtfix < {0} && ptl < {1}".format(mtfixCut,xPtBins[len(xPtBins)-1]), "mtfixCut < X && ptl < Y"))

            dfjet30cat .append(dffakecat[2*y+ltype].Filter("ngood_jets > 0","at least one jet30").Define("drljet","deltaR(good_Jet_eta[0],good_Jet_phi[0],etal,phil)"))
            dfjet50cat .append(dffakecat[2*y+ltype].Filter("nvbs_jets > 0","at least one jet50").Define("drljet","deltaR(vbs_Jet_eta[0],vbs_Jet_phi[0],etal,phil)"))
            dfbjet20cat.append(dffakecat[2*y+ltype].Filter("nbtag_goodbtag_Jet_bjet > 0","at least one btagjet20").Define("drljet","deltaR(goodbtag_Jet_eta[0],goodbtag_Jet_phi[0],etal,phil)"))

            histo[ltype+140][y] = dffakecat  [2*y+ltype].Histo1D(("histo_{0}_{1}".format(ltype+140,y), "histo_{0}_{1}".format(ltype+140,y),80,-0.5,79.5), "PV_npvsGood","weight")
            histo[ltype+142][y] = dfjet30cat [2*y+ltype].Histo1D(("histo_{0}_{1}".format(ltype+142,y), "histo_{0}_{1}".format(ltype+142,y),50,0,5.0), "drljet","weight")
            histo[ltype+144][y] = dfjet50cat [2*y+ltype].Histo1D(("histo_{0}_{1}".format(ltype+144,y), "histo_{0}_{1}".format(ltype+144,y),50,0,5.0), "drljet","weight")
            histo[ltype+146][y] = dfbjet20cat[2*y+ltype].Histo1D(("histo_{0}_{1}".format(ltype+146,y), "histo_{0}_{1}".format(ltype+146,y),50,0,5.0), "drljet","weight")

            dfjet30cat [2*y+ltype] = dfjet30cat [2*y+ltype].Filter("drljet > 0.7", "drljet > 0.7")
            dfjet50cat [2*y+ltype] = dfjet50cat [2*y+ltype].Filter("drljet > 0.7", "drljet > 0.7")
            dfbjet20cat[2*y+ltype] = dfbjet20cat[2*y+ltype].Filter("drljet > 0.7", "drljet > 0.7")

            strLep = "mu"
            strMVA = "fake_Muon_promptMVA"
            if(ltype == 1):
               strLep = "el"
               strMVA = "fake_Electron_promptMVA"

            histo[ltype+148][y] = dfjet30cat [2*y+ltype].Histo1D(("histo_{0}_{1}".format(ltype+148,y), "histo_{0}_{1}".format(ltype+148,y),100, -1.0, 1.0), "{0}".format(strMVA),"weight")
            histo[ltype+150][y] = dfjet50cat [2*y+ltype].Histo1D(("histo_{0}_{1}".format(ltype+150,y), "histo_{0}_{1}".format(ltype+150,y),100, -1.0, 1.0), "{0}".format(strMVA),"weight")
            histo[ltype+152][y] = dfbjet20cat[2*y+ltype].Histo1D(("histo_{0}_{1}".format(ltype+152,y), "histo_{0}_{1}".format(ltype+152,y),100, -1.0, 1.0), "{0}".format(strMVA),"weight")

            for ptbin in range(2):
                nHist = ptbin*100
                ptVar = "ptl"
                if(ptbin == 1):
                    ptVar = "ptlcone"
                histo2D[ltype+nHist+ 0][y] = dffakecat[2*y+ltype]                                            .Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+ 0,y), "histo2d_{0}_{1}".format(ltype+nHist+ 0,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+ 2][y] = dffakecat[2*y+ltype].Filter("Sum(tight_{0}0)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+ 2,y), "histo2d_{0}_{1}".format(ltype+nHist+ 2,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+ 4][y] = dffakecat[2*y+ltype].Filter("Sum(tight_{0}1)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+ 4,y), "histo2d_{0}_{1}".format(ltype+nHist+ 4,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+ 6][y] = dffakecat[2*y+ltype].Filter("Sum(tight_{0}2)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+ 6,y), "histo2d_{0}_{1}".format(ltype+nHist+ 6,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+ 8][y] = dffakecat[2*y+ltype].Filter("Sum(tight_{0}3)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+ 8,y), "histo2d_{0}_{1}".format(ltype+nHist+ 8,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+10][y] = dffakecat[2*y+ltype].Filter("Sum(tight_{0}4)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+10,y), "histo2d_{0}_{1}".format(ltype+nHist+10,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+12][y] = dffakecat[2*y+ltype].Filter("Sum(tight_{0}5)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+12,y), "histo2d_{0}_{1}".format(ltype+nHist+12,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+14][y] = dffakecat[2*y+ltype].Filter("Sum(tight_{0}6)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+14,y), "histo2d_{0}_{1}".format(ltype+nHist+14,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+16][y] = dffakecat[2*y+ltype].Filter("Sum(tight_{0}7)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+16,y), "histo2d_{0}_{1}".format(ltype+nHist+16,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+18][y] = dffakecat[2*y+ltype].Filter("Sum(tight_{0}8)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+18,y), "histo2d_{0}_{1}".format(ltype+nHist+18,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")

                histo2D[ltype+nHist+20][y] = dfjet30cat[2*y+ltype]					       .Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+20,y), "histo2d_{0}_{1}".format(ltype+nHist+20,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+22][y] = dfjet30cat[2*y+ltype] .Filter("Sum(tight_{0}0)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+22,y), "histo2d_{0}_{1}".format(ltype+nHist+22,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+24][y] = dfjet30cat[2*y+ltype] .Filter("Sum(tight_{0}1)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+24,y), "histo2d_{0}_{1}".format(ltype+nHist+24,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+26][y] = dfjet30cat[2*y+ltype] .Filter("Sum(tight_{0}2)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+26,y), "histo2d_{0}_{1}".format(ltype+nHist+26,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+28][y] = dfjet30cat[2*y+ltype] .Filter("Sum(tight_{0}3)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+28,y), "histo2d_{0}_{1}".format(ltype+nHist+28,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+30][y] = dfjet30cat[2*y+ltype] .Filter("Sum(tight_{0}4)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+30,y), "histo2d_{0}_{1}".format(ltype+nHist+30,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+32][y] = dfjet30cat[2*y+ltype] .Filter("Sum(tight_{0}5)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+32,y), "histo2d_{0}_{1}".format(ltype+nHist+32,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+34][y] = dfjet30cat[2*y+ltype] .Filter("Sum(tight_{0}6)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+34,y), "histo2d_{0}_{1}".format(ltype+nHist+34,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+36][y] = dfjet30cat[2*y+ltype] .Filter("Sum(tight_{0}7)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+36,y), "histo2d_{0}_{1}".format(ltype+nHist+36,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+38][y] = dfjet30cat[2*y+ltype] .Filter("Sum(tight_{0}8)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+38,y), "histo2d_{0}_{1}".format(ltype+nHist+38,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")

                histo2D[ltype+nHist+40][y] = dfbjet20cat[2*y+ltype]					       .Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+40,y), "histo2d_{0}_{1}".format(ltype+nHist+40,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+42][y] = dfbjet20cat[2*y+ltype].Filter("Sum(tight_{0}0)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+42,y), "histo2d_{0}_{1}".format(ltype+nHist+42,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+44][y] = dfbjet20cat[2*y+ltype].Filter("Sum(tight_{0}1)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+44,y), "histo2d_{0}_{1}".format(ltype+nHist+44,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+46][y] = dfbjet20cat[2*y+ltype].Filter("Sum(tight_{0}2)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+46,y), "histo2d_{0}_{1}".format(ltype+nHist+46,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+48][y] = dfbjet20cat[2*y+ltype].Filter("Sum(tight_{0}3)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+48,y), "histo2d_{0}_{1}".format(ltype+nHist+48,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+50][y] = dfbjet20cat[2*y+ltype].Filter("Sum(tight_{0}4)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+50,y), "histo2d_{0}_{1}".format(ltype+nHist+50,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+52][y] = dfbjet20cat[2*y+ltype].Filter("Sum(tight_{0}5)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+52,y), "histo2d_{0}_{1}".format(ltype+nHist+52,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+54][y] = dfbjet20cat[2*y+ltype].Filter("Sum(tight_{0}6)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+54,y), "histo2d_{0}_{1}".format(ltype+nHist+54,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+56][y] = dfbjet20cat[2*y+ltype].Filter("Sum(tight_{0}7)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+56,y), "histo2d_{0}_{1}".format(ltype+nHist+56,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+58][y] = dfbjet20cat[2*y+ltype].Filter("Sum(tight_{0}8)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+58,y), "histo2d_{0}_{1}".format(ltype+nHist+58,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")

                histo2D[ltype+nHist+60][y] = dfjet50cat[2*y+ltype]					       .Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+60,y), "histo2d_{0}_{1}".format(ltype+nHist+60,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+62][y] = dfjet50cat[2*y+ltype] .Filter("Sum(tight_{0}0)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+62,y), "histo2d_{0}_{1}".format(ltype+nHist+62,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+64][y] = dfjet50cat[2*y+ltype] .Filter("Sum(tight_{0}1)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+64,y), "histo2d_{0}_{1}".format(ltype+nHist+64,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+66][y] = dfjet50cat[2*y+ltype] .Filter("Sum(tight_{0}2)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+66,y), "histo2d_{0}_{1}".format(ltype+nHist+66,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+68][y] = dfjet50cat[2*y+ltype] .Filter("Sum(tight_{0}3)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+68,y), "histo2d_{0}_{1}".format(ltype+nHist+68,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+70][y] = dfjet50cat[2*y+ltype] .Filter("Sum(tight_{0}4)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+70,y), "histo2d_{0}_{1}".format(ltype+nHist+70,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+72][y] = dfjet50cat[2*y+ltype] .Filter("Sum(tight_{0}5)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+72,y), "histo2d_{0}_{1}".format(ltype+nHist+72,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+74][y] = dfjet50cat[2*y+ltype] .Filter("Sum(tight_{0}6)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+74,y), "histo2d_{0}_{1}".format(ltype+nHist+74,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+76][y] = dfjet50cat[2*y+ltype] .Filter("Sum(tight_{0}7)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+76,y), "histo2d_{0}_{1}".format(ltype+nHist+76,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")
                histo2D[ltype+nHist+78][y] = dfjet50cat[2*y+ltype] .Filter("Sum(tight_{0}8)==1".format(strLep)).Histo2D(("histo2d_{0}_{1}".format(ltype+nHist+78,y), "histo2d_{0}_{1}".format(ltype+nHist+78,y), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "absetal", "{0}".format(ptVar),"weight")

    report = []
    for y in range(nCat):
        for ltype in range(2):
            report.append(dfjet30cat[2*y+ltype].Report())
            if(y != theCat): continue
            print("---------------- SUMMARY 2*{0}+{1} = {2} -------------".format(y,ltype,2*y+ltype))
            report[2*y+ltype].Print()

    myfile = ROOT.TFile("fillhisto_fakeAnalysis_sample{0}_year{1}_job{2}.root".format(count,year,whichJob),'RECREATE')
    for i in range(nCat):
        for j in range(nHisto):
            if(histo[j][i] == 0): continue
            #if(histo[j][i].GetSumOfWeights() > 0): print("({0},{1}): {2}".format(j,i,histo[j][i].GetSumOfWeights()))
            histo[j][i].Write()
        for j in range(nHisto):
            if(histo2D[j][i] == 0): continue
            #if(histo2D[j][i].GetSumOfWeights() > 0): print("({0},{1}): {2}".format(j,i,histo2D[j][i].GetSumOfWeights()))
            histo2D[j][i].Write()
    myfile.Close()

def readMCSample(sampleNOW, year, skimType, whichJob, group, puWeights):

    files = getMClist(sampleNOW, skimType)
    print("Total files: {0}".format(len(files)))

    dfRuns = ROOT.RDataFrame("Runs", files)
    genEventSumWeight = dfRuns.Sum("genEventSumw").GetValue()
    genEventSumNoWeight = dfRuns.Sum("genEventCount").GetValue()
    runGetEntries = dfRuns.Count().GetValue()

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

    analysis(df, sampleNOW, SwitchSample(sampleNOW, skimType)[2], weight, year, PDType, "false", whichJob, puWeights)

def readDASample(sampleNOW, year, skimType, whichJob, group, puWeights):

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

    weight=1.
    nevents = df.Count().GetValue()
    print("%s entries in the dataset" %nevents)

    analysis(df, sampleNOW, sampleNOW, weight, year, PDType, "true", whichJob, puWeights)

if __name__ == "__main__":

    group = 5

    skimType = "1l"
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

    puPath = "data/puWeights_UL_{0}.root".format(year)
    fPuFile = ROOT.TFile(puPath)
    puWeights = fPuFile.Get("puWeights")
    puWeights.SetDirectory(0)
    fPuFile.Close()

    try:
        if(process >= 0 and process < 1000):
            readMCSample(process,year,skimType,whichJob,group, puWeights)
        elif(process >= 1000):
            readDASample(process,year,skimType,whichJob,group, puWeights)
    except Exception as e:
        print("FAILED {0}".format(e))
