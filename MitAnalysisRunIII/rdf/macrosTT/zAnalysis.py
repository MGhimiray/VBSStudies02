import ROOT
import os, sys, getopt, json
from array import array

ROOT.ROOT.EnableImplicitMT(10)
from utilsCategory import plotCategory
from utilsAna import getMClist, getDATAlist
from utilsAna import SwitchSample, groupFiles, getTriggerFromJson, getLeptomSelFromJson, getLumi
from utilsSelection import selectionTauVeto, selectionPhoton, selectionJetMet, selection2LVar, selectionTrigger2L, selectionElMu, selectionWeigths, selectionGenLepJet
#from utilsAna import loadCorrectionSet

print_info = False
# 0 = T, 1 = M, 2 = L
bTagSel = 1
useBTaggingWeights = 0

correctionString = ""

useFR = 0

altMass = "Def"

jetEtaCut = 4.9

selectionJsonPath = "config/selection.json"

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

def selectionLL(df,year,PDType,isData,TRIGGERMUEG,TRIGGERDMU,TRIGGERSMU,TRIGGERDEL,TRIGGERSEL,count):

    dftag = selectionTrigger2L(df,year,PDType,JSON,isData,TRIGGERSEL,TRIGGERDEL,TRIGGERSMU,TRIGGERDMU,TRIGGERMUEG)

    overallLeptonSel = jsonObject['leptonSel']
    FAKE_MU   = getLeptomSelFromJson(overallLeptonSel, "FAKE_MU",   year)
    TIGHT_MU  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU{0}".format(muSelChoice),  year, 1)
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
    TIGHT_EL  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL{0}".format(elSelChoice),  year, 1)
    TIGHT_EL0 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL0", year)
    TIGHT_EL1 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL1", year)
    TIGHT_EL2 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL2", year)
    TIGHT_EL3 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL3", year)
    TIGHT_EL4 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL4", year)
    TIGHT_EL5 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL5", year)
    TIGHT_EL6 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL6", year)
    TIGHT_EL7 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL7", year)
    TIGHT_EL8 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL8", year)

    dftag = selectionElMu(dftag,year,FAKE_MU,TIGHT_MU,FAKE_EL,TIGHT_EL)

    dftag = (dftag.Define("tight_mu0", "{0}".format(TIGHT_MU0))
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

                  .Filter("nLoose >= 2","At least two loose leptons")
                  .Filter("nLoose == 2","Only two loose leptons")
                  .Filter("nFake == 2","Two fake leptons")

                  .Filter("(Sum(fake_mu) > 0 and Max(fake_Muon_pt) > 25) or (Sum(fake_el) > 0 and Max(fake_Electron_pt) > 25)","At least one high pt lepton")
                  )

    if(useFR == 0):
        dftag = dftag.Filter("nTight == 2","Two tight leptons")

    dftag = selectionTauVeto(dftag,year,isData)
    dftag = selectionPhoton (dftag,year,BARRELphotons,ENDCAPphotons)
    dftag = selectionJetMet (dftag,year,bTagSel,isData,count,jetEtaCut)
    dftag = selection2LVar  (dftag,year,isData)

    return dftag


def analysis(df,count,category,weight,year,PDType,isData,whichJob,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3):

    print("starting {0} / {1} / {2} / {3} / {4} / {5} / {6}".format(count,category,weight,year,PDType,isData,whichJob))

    xPtBins = array('d', [10,15,20,25,30,35,40,50,60,70,85,100,200,1000])
    xEtaBins = array('d', [0.0,0.3,0.6,0.9,1.2,1.5,1.8,2.1,2.5])

    xPtTrgbins = array('d', [25,30,35,40,45,50,55,60,65,70,75,80,90,105,120,150,200])

    theCat = category
    if(theCat > 100): theCat = plotCategory("kPlotData")

    nCat, nHisto = plotCategory("kPlotCategories"), 500
    histo   = [[0 for y in range(nCat)] for x in range(nHisto)]
    histo2D = [[0 for y in range(nCat)] for x in range(nHisto)]
    histo_test = [[0 for y in range(nCat)] for x in range(3)]

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

    if(isData == "false"):
        dfbase = selectionGenLepJet(dfbase,20,30,5.0)
        dfbase = (dfbase.Define("mjjGen", "compute_vbs_gen_variables(0,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass)")
                      )
    else:
        dfbase = (dfbase.Define("mjjGen", "{0}".format(0))
                      )

    dfbase = selectionWeigths(dfbase,isData,year,PDType,weight,useFR,bTagSel,useBTaggingWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,MUOWP,ELEWP,correctionString,0)

    overallMETFilters = jsonObject['met_filters']
    METFILTERS = getTriggerFromJson(overallMETFilters, "All", year)
    dfbase = dfbase.Define("METFILTERS", "{0}".format(METFILTERS))

    xMllMin = [91.1876-15,  30, 91.1876-15]
    xMllMax = [91.1876+15, 330, 91.1876+15]
    dfcat = []
    dfzllcat = []
    dfjetcat = []
    dfzgcat = []
    dfzemcat = []
    dfzmecat = []
    dftightsscat = []
    dftightoscat = []
    for x in range(nCat):
        for ltype in range(3):
            dfcat.append(dfbase.Filter("DiLepton_flavor=={0}".format(ltype), "flavor type == {0}".format(ltype))
                               .Define("kPlotNonPrompt", "{0}".format(plotCategory("kPlotNonPrompt")))
                               .Define("kPlotWS", "{0}".format(plotCategory("kPlotWS")))
                               .Define("theCat{0}".format(x), "compute_category({0},kPlotNonPrompt,kPlotWS,nFake,nTight,0)".format(theCat))
                               .Filter("theCat{0}=={1}".format(x,x), "correct category ({0})".format(x))
                               )

            dfzgcat.append(dfcat[3*x+ltype].Filter("Sum(fake_Muon_charge)+Sum(fake_Muon_charge) == 0 && ptl1 > 25 && ptl2 > 20 && mll > 10 && Sum(good_Photons) > 0 && Max(good_Photons_pt) > 20")
              .Define("kPlotDY", "{0}".format(plotCategory("kPlotDY")))
              .Filter("theCat{0}!=kPlotDY".format(x))
              .Define("ptg", "compute_met_lepton_gamma_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, thePuppiMET_pt, thePuppiMET_phi, good_Photons_pt, good_Photons_eta, good_Photons_phi, 6)")
              .Define("mllg","compute_met_lepton_gamma_var(good_Jet_pt, good_Jet_eta, good_Jet_phi, good_Jet_mass, fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, thePuppiMET_pt, thePuppiMET_phi, good_Photons_pt, good_Photons_eta, good_Photons_phi, 7)")
            )

            histo[ltype+36][x] = dfcat[3*x+ltype].Filter("Sum(fake_Muon_charge)+Sum(fake_Electron_charge) == 0 && mll{0} > 60 && mll{0} < 180".format(altMass)).Histo1D(("histo_{0}_{1}".format(ltype+36,x), "histo_{0}_{1}".format(ltype+36,x), 60, 60, 180), "mll{0}".format(altMass),"weight")

            dfcat[3*x+ltype] = dfcat[3*x+ltype].Filter("(DiLepton_flavor != 1 && abs(mll{0}-91.1876) < 15) || (DiLepton_flavor == 1 && mll{0} > 30 && ptl2 > 25)".format(altMass),"mll cut")

            dfzllcat.append(dfcat[3*x+ltype].Filter("Sum(fake_Muon_charge)+Sum(fake_Electron_charge) == 0", "Opposite-sign leptons"))

            histo[ltype+ 0][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+ 0,x), "histo_{0}_{1}".format(ltype+ 0,x), 60, xMllMin[ltype], xMllMax[ltype]), "mll{0}".format(altMass),"weight")
            histo[ltype+ 3][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+ 3,x), "histo_{0}_{1}".format(ltype+ 3,x), 40,  0, 200), "ptll","weight")
            histo[ltype+ 6][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+ 6,x), "histo_{0}_{1}".format(ltype+ 6,x), 50,  0, 5),   "drll","weight")
            histo[ltype+ 9][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+ 9,x), "histo_{0}_{1}".format(ltype+ 9,x), 50,  0, 3.1416), "dphill","weight")
            histo[ltype+12][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+12,x), "histo_{0}_{1}".format(ltype+12,x), 40, 25, 225), "ptl1","weight")
            histo[ltype+15][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+15,x), "histo_{0}_{1}".format(ltype+15,x), 40, 10, 210), "ptl2","weight")
            histo[ltype+18][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+18,x), "histo_{0}_{1}".format(ltype+18,x), 25,  0,2.5), "etal1","weight")
            histo[ltype+21][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+21,x), "histo_{0}_{1}".format(ltype+21,x), 25,  0,2.5), "etal2","weight")
            histo[ltype+24][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+24,x), "histo_{0}_{1}".format(ltype+24,x), 6,-0.5,5.5), "ngood_jets","weight")
            histo[ltype+27][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+27,x), "histo_{0}_{1}".format(ltype+27,x), 5,-0.5,4.5), "nbtag_goodbtag_Jet_bjet","weightBTag")
            histo[ltype+30][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+30,x), "histo_{0}_{1}".format(ltype+30,x), 80,-0.5,79.5), "PV_npvsGood","weight")
            histo[ltype+33][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+33,x), "histo_{0}_{1}".format(ltype+33,x), 100, 0, 200), "CaloMET_pt","weight")
            if((year // 10) < 2024):
                histo[ltype+39][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+39,x), "histo_{0}_{1}".format(ltype+39,x), 100, 0, 200), "MET_pt","weight")
            else:
                histo[ltype+39][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+39,x), "histo_{0}_{1}".format(ltype+39,x), 100, 0, 200), "PFMET_pt","weight")
            histo[ltype+42][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+42,x), "histo_{0}_{1}".format(ltype+42,x), 100, 0, 200), "thePuppiMET_pt","weight")
            #histo[ltype+45][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+45,x), "histo_{0}_{1}".format(ltype+45,x), 100, 0, 200), "TkMET_pt","weight")
            histo[ltype+48][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+48,x), "histo_{0}_{1}".format(ltype+48,x), 80,-0.5,79.5), "Rho_fixedGridRhoFastjetAll","weight")
            if((year // 10) < 2024):
                histo[ltype+51][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+51,x), "histo_{0}_{1}".format(ltype+51,x), 100, -3.1416, 3.1416), "MET_phi","weight")
            else:
                histo[ltype+51][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+51,x), "histo_{0}_{1}".format(ltype+51,x), 100, -3.1416, 3.1416), "PFMET_phi","weight")
            histo[ltype+54][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+54,x), "histo_{0}_{1}".format(ltype+54,x), 100, -3.1416, 3.1416), "thePuppiMET_phi","weight")

            if(x == plotCategory("kPlotData") and print_info == True):
                histo_test[ltype][x] = (dfzllcat[3*x+ltype].Define("print_info","print_info(run,luminosityBlock,event)")
                                       .Filter("print_info > 0")
                                       .Histo1D(("test_{0}_{1}".format(ltype,x), "test_{0}_{1}".format(ltype,x), 4,-0.5,3.5), "ngood_jets","weight"))

            if(ltype == 2):
                dftightsscat.append(dfcat[3*x+ltype].Filter("Sum(fake_Electron_charge)==0 && DiLepton_flavor==2 && tight_el7[0]==true && tight_el7[1]==true && mll{0}>80 && mll{0}<100".format(altMass)))
                dftightoscat.append(dfcat[3*x+ltype].Filter("Sum(fake_Electron_charge)!=0 && DiLepton_flavor==2 && tight_el7[0]==true && tight_el7[1]==true && mll{0}>80 && mll{0}<100".format(altMass)))
                histo[58][x] = dftightsscat[x].Histo1D(("histo_{0}_{1}".format(58,x), "histo_{0}_{1}".format(58,x),100,80,100), "mll{0}".format(altMass),"weight")
                histo[59][x] = dftightoscat[x].Histo1D(("histo_{0}_{1}".format(59,x), "histo_{0}_{1}".format(59,x),100,80,100), "mll{0}".format(altMass),"weight")
                coutWSStudy = 0
                for j1 in (0.0, 0.5, 1.0, 1.5, 2.0):
                    for j2 in (0.0, 0.5, 1.0, 1.5, 2.0):
                        histo[60+coutWSStudy][x] = dftightsscat[x].Filter("etal1>=0.0+{0}&&etal1<0.5+{0}&&etal2>=0.0+{1}&&etal2<0.5+{1}".format(j1,j2)).Histo1D(("histo_{0}_{1}".format(60+coutWSStudy,x), "histo_{0}_{1}".format(60+coutWSStudy,x),100,80,100), "mll{0}".format(altMass),"weight")
                        histo[61+coutWSStudy][x] = dftightoscat[x].Filter("etal1>=0.0+{0}&&etal1<0.5+{0}&&etal2>=0.0+{1}&&etal2<0.5+{1}".format(j1,j2)).Histo1D(("histo_{0}_{1}".format(61+coutWSStudy,x), "histo_{0}_{1}".format(61+coutWSStudy,x),100,80,100), "mll{0}".format(altMass),"weight")
                        coutWSStudy = coutWSStudy + 2

                isCatWSStudyE1 = ["etal1 < 1.5 && ptl1 > 25 && ptl1 < 40", # 0
                                  "etal1 < 1.5 && ptl1 > 40",		   # 1
                                  "etal1 > 1.5 && ptl1 > 25 && ptl1 < 40", # 2
                                  "etal1 > 1.5 && ptl1 > 40"		   # 3
                                 ]
                isCatWSStudyE2 = ["etal2 < 1.5 && ptl2 > 10 && ptl2 < 25", # 0
                                  "etal2 < 1.5 && ptl2 > 25 && ptl2 < 40", # 1
                                  "etal2 < 1.5 && ptl2 > 40",		   # 2
                                  "etal2 > 1.5 && ptl2 > 10 && ptl2 < 25", # 3
                                  "etal2 > 1.5 && ptl2 > 25 && ptl2 < 40", # 4
                                  "etal2 > 1.5 && ptl2 > 40"		   # 5
                                 ]
                coutWSStudy = 0
                for j1 in range(len(isCatWSStudyE1)):
                    for j2 in range(len(isCatWSStudyE2)):
                        if((j1==0 and j2==2)or(j1==0 and j2==5)or(j1==2 and j2==2)or(j1==2 and j2==5)): continue
                        histo[400+coutWSStudy][x] = dftightsscat[x].Filter("{0} and {1}".format(isCatWSStudyE1[j1],isCatWSStudyE2[j2])).Histo1D(("histo_{0}_{1}".format(400+coutWSStudy,x), "histo_{0}_{1}".format(400+coutWSStudy,x),100,80,100), "mll{0}".format(altMass),"weight")
                        histo[401+coutWSStudy][x] = dftightoscat[x].Filter("{0} and {1}".format(isCatWSStudyE1[j1],isCatWSStudyE2[j2])).Histo1D(("histo_{0}_{1}".format(401+coutWSStudy,x), "histo_{0}_{1}".format(401+coutWSStudy,x),100,80,100), "mll{0}".format(altMass),"weight")
                        coutWSStudy = coutWSStudy + 2

            dfjetcat.append(dfzllcat[3*x+ltype].Filter("ngood_jets >= 1", "At least one jet"))
            histo[ltype+110][x] = dfjetcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+110,x), "histo_{0}_{1}".format(ltype+110,x), 50,0,1), "good_Jet_btagUnifiedParTB","weight")
            histo[ltype+113][x] = dfjetcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+113,x), "histo_{0}_{1}".format(ltype+113,x), 6,-0.5,5.5), "nbtag_goodbtag_Jet_bjet","weightBTag")

            dfjetcat[3*x+ltype] = dfjetcat[3*x+ltype].Filter("DiLepton_flavor != 1 || nbtag_goodbtag_Jet_bjet >= 1", "At least one b-jet")
            histo[ltype+116][x] = dfjetcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+116,x), "histo_{0}_{1}".format(ltype+116,x), 50,30,230), "ptj1","weight")
            histo[ltype+119][x] = dfjetcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+119,x), "histo_{0}_{1}".format(ltype+119,x), 50,0.0,5.0), "etaj1","weight")
            histo[ltype+122][x] = dfjetcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+122,x), "histo_{0}_{1}".format(ltype+122,x), 50, 0, 200), "thePuppiMET_pt","weight")
            histo[ltype+125][x] = dfjetcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+125,x), "histo_{0}_{1}".format(ltype+125,x), 50, 0, 200), "ptll","weight")

            if(ltype == 0):
                histo[128][x] = dfzllcat[3*x+ltype].Filter("etal1<1.5").Histo1D(("histo_{0}_{1}".format(128,x), "histo_{0}_{1}".format(128,x), 512, -0.5, 511.5), "muid1","weight")
                histo[129][x] = dfzllcat[3*x+ltype].Filter("etal2<1.5").Histo1D(("histo_{0}_{1}".format(129,x), "histo_{0}_{1}".format(129,x), 512, -0.5, 511.5), "muid2","weight")
                histo[130][x] = dfzllcat[3*x+ltype].Filter("etal1>1.5").Histo1D(("histo_{0}_{1}".format(130,x), "histo_{0}_{1}".format(130,x), 512, -0.5, 511.5), "muid1","weight")
                histo[131][x] = dfzllcat[3*x+ltype].Filter("etal2>1.5").Histo1D(("histo_{0}_{1}".format(131,x), "histo_{0}_{1}".format(131,x), 512, -0.5, 511.5), "muid2","weight")
            if(ltype == 2):
                histo[132][x] = dfzllcat[3*x+ltype].Filter("etal1<1.5").Histo1D(("histo_{0}_{1}".format(132,x), "histo_{0}_{1}".format(132,x), 512, -0.5, 511.5), "elid1","weight")
                histo[133][x] = dfzllcat[3*x+ltype].Filter("etal2<1.5").Histo1D(("histo_{0}_{1}".format(133,x), "histo_{0}_{1}".format(133,x), 512, -0.5, 511.5), "elid2","weight")
                histo[134][x] = dfzllcat[3*x+ltype].Filter("etal1>1.5").Histo1D(("histo_{0}_{1}".format(134,x), "histo_{0}_{1}".format(134,x), 512, -0.5, 511.5), "elid1","weight")
                histo[135][x] = dfzllcat[3*x+ltype].Filter("etal2>1.5").Histo1D(("histo_{0}_{1}".format(135,x), "histo_{0}_{1}".format(135,x), 512, -0.5, 511.5), "elid2","weight")

            histo[ltype+136][x] = dfzgcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+136,x), "histo_{0}_{1}".format(ltype+136,x), 40, 10, 210), "mllg","weight")
            dfzgcat[3*x+ltype] = dfzgcat[3*x+ltype].Filter("abs(mllg-91.1876)<15")
            histo[ltype+139][x] = dfzgcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+139,x), "histo_{0}_{1}".format(ltype+139,x), 20, 20, 120), "ptg","weight")

            dfjetcat[3*x+ltype] = dfjetcat[3*x+ltype].Define("good_Jet_neEmEF0","good_Jet_neEmEF[0]").Define("good_Jet_neHEF0","good_Jet_neHEF[0]").Define("good_Jet_chEF0","good_Jet_chEmEF[0]+good_Jet_chHEF[0]")
            histo[ltype+142][x] = dfjetcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+142,x), "histo_{0}_{1}".format(ltype+142,x),50,-5.0,5.0), "good_Jet_eta","weight")
            histo[ltype+145][x] = dfjetcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+145,x), "histo_{0}_{1}".format(ltype+145,x),50,-5.0,5.0), "vbs_Jet_eta","weight")
            histo[ltype+148][x] = dfjetcat[3*x+ltype].Filter("etaj1 > 2.6 && etaj1 < 2.8").Histo1D(("histo_{0}_{1}".format(ltype+148,x), "histo_{0}_{1}".format(ltype+148,x),40,0.0,1.0), "good_Jet_neEmEF0","weight")
            histo[ltype+151][x] = dfjetcat[3*x+ltype].Filter("etaj1 > 2.6 && etaj1 < 2.8").Histo1D(("histo_{0}_{1}".format(ltype+151,x), "histo_{0}_{1}".format(ltype+151,x),40,0.0,1.0), "good_Jet_neHEF0","weight")
            histo[ltype+154][x] = dfjetcat[3*x+ltype].Filter("etaj1 > 2.6 && etaj1 < 2.8").Histo1D(("histo_{0}_{1}".format(ltype+154,x), "histo_{0}_{1}".format(ltype+154,x),40,0.0,1.0), "good_Jet_chEF0","weight")
            if(ltype != 2):
              histo[ltype+264][x] = dfzllcat[3*x+ltype].Filter("ngood_jets == 0").Histo1D(("histo_{0}_{1}".format(ltype+264,x), "histo_{0}_{1}".format(ltype+264,x), 40,  0, 200), "ptll","weight")
              histo[ltype+266][x] = dfzllcat[3*x+ltype].Filter("ngood_jets == 0").Histo1D(("histo_{0}_{1}".format(ltype+266,x), "histo_{0}_{1}".format(ltype+266,x), 40, 25, 225), "ptl1","weight")
              histo[ltype+268][x] = dfzllcat[3*x+ltype].Filter("ngood_jets == 0").Histo1D(("histo_{0}_{1}".format(ltype+268,x), "histo_{0}_{1}".format(ltype+268,x), 40, 10, 210), "ptl2","weight")
              histo[ltype+270][x] = dfzllcat[3*x+ltype].Filter("ngood_jets == 1").Histo1D(("histo_{0}_{1}".format(ltype+270,x), "histo_{0}_{1}".format(ltype+270,x), 40,  0, 200), "ptll","weight")
              histo[ltype+272][x] = dfzllcat[3*x+ltype].Filter("ngood_jets == 1").Histo1D(("histo_{0}_{1}".format(ltype+272,x), "histo_{0}_{1}".format(ltype+272,x), 40, 25, 225), "ptl1","weight")
              histo[ltype+274][x] = dfzllcat[3*x+ltype].Filter("ngood_jets == 1").Histo1D(("histo_{0}_{1}".format(ltype+274,x), "histo_{0}_{1}".format(ltype+274,x), 40, 10, 210), "ptl2","weight")
              histo[ltype+276][x] = dfzllcat[3*x+ltype].Filter("ngood_jets == 2").Histo1D(("histo_{0}_{1}".format(ltype+276,x), "histo_{0}_{1}".format(ltype+276,x), 40,  0, 200), "ptll","weight")
              histo[ltype+278][x] = dfzllcat[3*x+ltype].Filter("ngood_jets == 2").Histo1D(("histo_{0}_{1}".format(ltype+278,x), "histo_{0}_{1}".format(ltype+278,x), 40, 25, 225), "ptl1","weight")
              histo[ltype+280][x] = dfzllcat[3*x+ltype].Filter("ngood_jets == 2").Histo1D(("histo_{0}_{1}".format(ltype+280,x), "histo_{0}_{1}".format(ltype+280,x), 40, 10, 210), "ptl2","weight")
              histo[ltype+282][x] = dfjetcat[3*x+ltype].Filter("ngood_jets >= 3").Histo1D(("histo_{0}_{1}".format(ltype+282,x), "histo_{0}_{1}".format(ltype+282,x), 40,  0, 200), "ptll","weight")
              histo[ltype+284][x] = dfjetcat[3*x+ltype].Filter("ngood_jets >= 3").Histo1D(("histo_{0}_{1}".format(ltype+284,x), "histo_{0}_{1}".format(ltype+284,x), 40, 25, 225), "ptl1","weight")
              histo[ltype+286][x] = dfjetcat[3*x+ltype].Filter("ngood_jets >= 3").Histo1D(("histo_{0}_{1}".format(ltype+286,x), "histo_{0}_{1}".format(ltype+286,x), 40, 10, 210), "ptl2","weight")

            dfjetcat[3*x+ltype] = dfjetcat[3*x+ltype].Filter("ngood_jets >= 2", "At least two jets")
            histo[ltype+157][x] = dfjetcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+157,x), "histo_{0}_{1}".format(ltype+157,x), 50,0,2000), "mjj","weight")
            histo[ltype+160][x] = dfjetcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+160,x), "histo_{0}_{1}".format(ltype+160,x), 50,0,400), "ptjj","weight")
            histo[ltype+163][x] = dfjetcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+163,x), "histo_{0}_{1}".format(ltype+163,x), 50,0,3.1416), "dphijj","weight")

            histo[ltype+166][x] = dfzllcat[3*x+ltype].Filter("METFILTERS > 0").Histo1D(("histo_{0}_{1}".format(ltype+166,x), "histo_{0}_{1}".format(ltype+166,x), 100, 0, 200), "thePuppiMET_pt","weight")
            histo[ltype+169][x] = dfzllcat[3*x+ltype].Filter("METFILTERS ==0").Histo1D(("histo_{0}_{1}".format(ltype+169,x), "histo_{0}_{1}".format(ltype+169,x), 100, 0, 200), "thePuppiMET_pt","weight")

            histo[ltype+179][x] = dfzllcat[3*x+ltype].Filter("triggerMUEG> 0").Histo1D(("histo_{0}_{1}".format(ltype+179,x), "histo_{0}_{1}".format(ltype+179,x), 60, xMllMin[ltype], xMllMax[ltype]), "mll","weight")
            histo[ltype+182][x] = dfzllcat[3*x+ltype].Filter("triggerDMU > 0").Histo1D(("histo_{0}_{1}".format(ltype+182,x), "histo_{0}_{1}".format(ltype+182,x), 60, xMllMin[ltype], xMllMax[ltype]), "mll","weight")
            histo[ltype+185][x] = dfzllcat[3*x+ltype].Filter("triggerSMU > 0").Histo1D(("histo_{0}_{1}".format(ltype+185,x), "histo_{0}_{1}".format(ltype+185,x), 60, xMllMin[ltype], xMllMax[ltype]), "mll","weight")
            histo[ltype+188][x] = dfzllcat[3*x+ltype].Filter("triggerDEL > 0").Histo1D(("histo_{0}_{1}".format(ltype+188,x), "histo_{0}_{1}".format(ltype+188,x), 60, xMllMin[ltype], xMllMax[ltype]), "mll","weight")
            histo[ltype+191][x] = dfzllcat[3*x+ltype].Filter("triggerSEL > 0").Histo1D(("histo_{0}_{1}".format(ltype+191,x), "histo_{0}_{1}".format(ltype+191,x), 60, xMllMin[ltype], xMllMax[ltype]), "mll","weight")
            histo[ltype+194][x] = dfzllcat[3*x+ltype].Filter("triggerMUEG == 0 && triggerDMU > 0")                                                         .Histo1D(("histo_{0}_{1}".format(ltype+194,x), "histo_{0}_{1}".format(ltype+194,x), 60, xMllMin[ltype], xMllMax[ltype]), "mll","weight")
            histo[ltype+197][x] = dfzllcat[3*x+ltype].Filter("triggerMUEG == 0 && triggerDMU == 0 && triggerSMU > 0")                                      .Histo1D(("histo_{0}_{1}".format(ltype+197,x), "histo_{0}_{1}".format(ltype+197,x), 60, xMllMin[ltype], xMllMax[ltype]), "mll","weight")
            histo[ltype+200][x] = dfzllcat[3*x+ltype].Filter("triggerMUEG == 0 && triggerDMU == 0 && triggerSMU == 0 && triggerDEL > 0")                   .Histo1D(("histo_{0}_{1}".format(ltype+200,x), "histo_{0}_{1}".format(ltype+200,x), 60, xMllMin[ltype], xMllMax[ltype]), "mll","weight")
            histo[ltype+203][x] = dfzllcat[3*x+ltype].Filter("triggerMUEG == 0 && triggerDMU == 0 && triggerSMU == 0 && triggerDEL == 0 && triggerSEL > 0").Histo1D(("histo_{0}_{1}".format(ltype+203,x), "histo_{0}_{1}".format(ltype+203,x), 60, xMllMin[ltype], xMllMax[ltype]), "mll","weight")
            # em
            if(ltype == 1):
                dfzmecat.append(dfzllcat[3*x+ltype].Filter("triggerSMU > 0 && fake_Muon_pt[0] > 30")
                                                  .Define("pttag","Max(fake_Muon_pt)")
                                                  .Define("ptprobe","Max(fake_Electron_pt)")
                                                  )
                dfzemcat.append(dfzllcat[3*x+ltype].Filter("triggerSEL > 0 && fake_Electron_pt[0] > 30")
                                                  .Define("pttag","Max(fake_Electron_pt)")
                                                  .Define("ptprobe","Max(fake_Muon_pt)")
                                                  )
                histo[206][x] = dfzmecat[x].Histo1D(("histo_{0}_{1}".format(206,x), "histo_{0}_{1}".format(206,x), 20, 30, 130), "pttag","weight")
                histo[207][x] = dfzemcat[x].Histo1D(("histo_{0}_{1}".format(207,x), "histo_{0}_{1}".format(207,x), 20, 30, 130), "pttag","weight")

                dfzmecat[x] = dfzmecat[x].Filter("hasTriggerMatch(fake_Muon_eta[0],fake_Muon_phi[0],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,13,1)")
                dfzemcat[x] = dfzemcat[x].Filter("hasTriggerMatch(fake_Electron_eta[0],fake_Electron_phi[0],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,11,1)")

                histo[208][x] = dfzmecat[x].Histo1D(("histo_{0}_{1}".format(208,x), "histo_{0}_{1}".format(208,x), 20, 30, 130), "pttag","weight")
                histo[209][x] = dfzemcat[x].Histo1D(("histo_{0}_{1}".format(209,x), "histo_{0}_{1}".format(209,x), 20, 30, 130), "pttag","weight")
                histo[210][x] = dfzmecat[x].Histo1D(("histo_{0}_{1}".format(210,x), "histo_{0}_{1}".format(210,x), len(xPtTrgbins)-1, xPtTrgbins), "ptprobe","weight")
                histo[211][x] = dfzemcat[x].Histo1D(("histo_{0}_{1}".format(211,x), "histo_{0}_{1}".format(211,x), len(xPtTrgbins)-1, xPtTrgbins), "ptprobe","weight")

                histo[212][x] = dfzmecat[x].Filter("triggerMUEG > 0").Histo1D(("histo_{0}_{1}".format(212,x), "histo_{0}_{1}".format(212,x), len(xPtTrgbins)-1, xPtTrgbins), "ptprobe","weight")
                histo[213][x] = dfzemcat[x].Filter("triggerMUEG > 0").Histo1D(("histo_{0}_{1}".format(213,x), "histo_{0}_{1}".format(213,x), len(xPtTrgbins)-1, xPtTrgbins), "ptprobe","weight")

                histo[214][x] = dfzmecat[x].Filter("triggerSEL  > 0").Histo1D(("histo_{0}_{1}".format(214,x), "histo_{0}_{1}".format(214,x), len(xPtTrgbins)-1, xPtTrgbins), "ptprobe","weight")
                histo[215][x] = dfzemcat[x].Filter("triggerSMU  > 0").Histo1D(("histo_{0}_{1}".format(215,x), "histo_{0}_{1}".format(215,x), len(xPtTrgbins)-1, xPtTrgbins), "ptprobe","weight")

            # mm or ee
            else:
                varPlot = 0
                if(ltype == 2): varPlot = 1
                histo[varPlot+216][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(varPlot+216,x), "histo_{0}_{1}".format(varPlot+216,x), len(xPtBins)-1, xPtBins), "ptl1","weight")
                histo[varPlot+218][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(varPlot+218,x), "histo_{0}_{1}".format(varPlot+218,x), len(xPtBins)-1, xPtBins), "ptl1","weight0")
                histo[varPlot+220][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(varPlot+220,x), "histo_{0}_{1}".format(varPlot+220,x), len(xPtBins)-1, xPtBins), "ptl1","weight1")
                histo[varPlot+222][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(varPlot+222,x), "histo_{0}_{1}".format(varPlot+222,x), len(xPtBins)-1, xPtBins), "ptl1","weight2")
                histo[varPlot+224][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(varPlot+224,x), "histo_{0}_{1}".format(varPlot+224,x), len(xPtBins)-1, xPtBins), "ptl1","weight3")
                histo[varPlot+226][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(varPlot+226,x), "histo_{0}_{1}".format(varPlot+226,x), len(xPtBins)-1, xPtBins), "ptl1","weight4")
                histo[varPlot+228][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(varPlot+228,x), "histo_{0}_{1}".format(varPlot+228,x), len(xPtBins)-1, xPtBins), "ptl1","weight5")
                histo[varPlot+230][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(varPlot+230,x), "histo_{0}_{1}".format(varPlot+230,x), len(xPtBins)-1, xPtBins), "ptl1","weight6")
                histo[varPlot+232][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(varPlot+232,x), "histo_{0}_{1}".format(varPlot+232,x), len(xPtBins)-1, xPtBins), "ptl1","weight7")
                histo[varPlot+234][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(varPlot+234,x), "histo_{0}_{1}".format(varPlot+234,x), len(xPtBins)-1, xPtBins), "ptl1","weightBTag")
                histo[varPlot+236][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(varPlot+236,x), "histo_{0}_{1}".format(varPlot+236,x), len(xPtBins)-1, xPtBins), "ptl1","weightNoBTag")

            isBB = "(etal1<1.5 and etal2<1.5)"
            isEB = "true" # "((etal1>1.5 and etal2<1.5) || (etal1<1.5 and etal2>1.5))"
            isEE = "(etal1>1.5 and etal2>1.5)"
            altShapes = ["", "Def", "MuonMomUp", "MuonMomDown", "", "Def", "ElectronMomUp", "ElectronMomDown"]

            if(ltype == 0):
                histo[240][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isBB,altShapes[0])).Histo1D(("histo_{0}_{1}".format(240,x), "histo_{0}_{1}".format(240,x),100, 81, 101), "mll{0}".format(altShapes[0]),"weight")
                histo[241][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEB,altShapes[0])).Histo1D(("histo_{0}_{1}".format(241,x), "histo_{0}_{1}".format(241,x),100, 81, 101), "mll{0}".format(altShapes[0]),"weight")
                histo[242][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEE,altShapes[0])).Histo1D(("histo_{0}_{1}".format(242,x), "histo_{0}_{1}".format(242,x),100, 81, 101), "mll{0}".format(altShapes[0]),"weight")

                histo[243][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isBB,altShapes[1])).Histo1D(("histo_{0}_{1}".format(243,x), "histo_{0}_{1}".format(243,x),100, 81, 101), "mll{0}".format(altShapes[1]),"weight")
                histo[244][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEB,altShapes[1])).Histo1D(("histo_{0}_{1}".format(244,x), "histo_{0}_{1}".format(244,x),100, 81, 101), "mll{0}".format(altShapes[1]),"weight")
                histo[245][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEE,altShapes[1])).Histo1D(("histo_{0}_{1}".format(245,x), "histo_{0}_{1}".format(245,x),100, 81, 101), "mll{0}".format(altShapes[1]),"weight")

                histo[246][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isBB,altShapes[2])).Histo1D(("histo_{0}_{1}".format(246,x), "histo_{0}_{1}".format(246,x),100, 81, 101), "mll{0}".format(altShapes[2]),"weight")
                histo[247][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEB,altShapes[2])).Histo1D(("histo_{0}_{1}".format(247,x), "histo_{0}_{1}".format(247,x),100, 81, 101), "mll{0}".format(altShapes[2]),"weight")
                histo[248][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEE,altShapes[2])).Histo1D(("histo_{0}_{1}".format(248,x), "histo_{0}_{1}".format(248,x),100, 81, 101), "mll{0}".format(altShapes[2]),"weight")

                histo[249][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isBB,altShapes[3])).Histo1D(("histo_{0}_{1}".format(249,x), "histo_{0}_{1}".format(249,x),100, 81, 101), "mll{0}".format(altShapes[3]),"weight")
                histo[250][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEB,altShapes[3])).Histo1D(("histo_{0}_{1}".format(250,x), "histo_{0}_{1}".format(250,x),100, 81, 101), "mll{0}".format(altShapes[3]),"weight")
                histo[251][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEE,altShapes[3])).Histo1D(("histo_{0}_{1}".format(251,x), "histo_{0}_{1}".format(251,x),100, 81, 101), "mll{0}".format(altShapes[3]),"weight")
            elif(ltype == 2):
                histo[252][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isBB,altShapes[4])).Histo1D(("histo_{0}_{1}".format(252,x), "histo_{0}_{1}".format(252,x),100, 81, 101), "mll{0}".format(altShapes[4]),"weight")
                histo[253][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEB,altShapes[4])).Histo1D(("histo_{0}_{1}".format(253,x), "histo_{0}_{1}".format(253,x),100, 81, 101), "mll{0}".format(altShapes[4]),"weight")
                histo[254][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEE,altShapes[4])).Histo1D(("histo_{0}_{1}".format(254,x), "histo_{0}_{1}".format(254,x),100, 81, 101), "mll{0}".format(altShapes[4]),"weight")

                histo[255][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isBB,altShapes[5])).Histo1D(("histo_{0}_{1}".format(255,x), "histo_{0}_{1}".format(255,x),100, 81, 101), "mll{0}".format(altShapes[5]),"weight")
                histo[256][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEB,altShapes[5])).Histo1D(("histo_{0}_{1}".format(256,x), "histo_{0}_{1}".format(256,x),100, 81, 101), "mll{0}".format(altShapes[5]),"weight")
                histo[257][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEE,altShapes[5])).Histo1D(("histo_{0}_{1}".format(257,x), "histo_{0}_{1}".format(257,x),100, 81, 101), "mll{0}".format(altShapes[5]),"weight")

                histo[258][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isBB,altShapes[6])).Histo1D(("histo_{0}_{1}".format(258,x), "histo_{0}_{1}".format(258,x),100, 81, 101), "mll{0}".format(altShapes[6]),"weight")
                histo[259][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEB,altShapes[6])).Histo1D(("histo_{0}_{1}".format(259,x), "histo_{0}_{1}".format(259,x),100, 81, 101), "mll{0}".format(altShapes[6]),"weight")
                histo[260][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEE,altShapes[6])).Histo1D(("histo_{0}_{1}".format(260,x), "histo_{0}_{1}".format(260,x),100, 81, 101), "mll{0}".format(altShapes[6]),"weight")

                histo[261][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isBB,altShapes[7])).Histo1D(("histo_{0}_{1}".format(261,x), "histo_{0}_{1}".format(261,x),100, 81, 101), "mll{0}".format(altShapes[7]),"weight")
                histo[262][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEB,altShapes[7])).Histo1D(("histo_{0}_{1}".format(262,x), "histo_{0}_{1}".format(262,x),100, 81, 101), "mll{0}".format(altShapes[7]),"weight")
                histo[263][x] = dfzllcat[3*x+ltype].Filter("{0} and mll{1} > 81 and mll{1} < 101".format(isEE,altShapes[7])).Histo1D(("histo_{0}_{1}".format(263,x), "histo_{0}_{1}".format(263,x),100, 81, 101), "mll{0}".format(altShapes[7]),"weight")

            if(ltype == 0):
                histo2D[ 0][x] = dfzllcat[3*x+ltype]                               .Histo2D(("histo2d_{0}_{1}".format( 0, x), "histo2d_{0}_{1}".format( 0, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[ 1][x] = dfzllcat[3*x+ltype].Filter("tight_mu0[0] == true").Histo2D(("histo2d_{0}_{1}".format( 1, x), "histo2d_{0}_{1}".format( 1, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[ 2][x] = dfzllcat[3*x+ltype].Filter("tight_mu1[0] == true").Histo2D(("histo2d_{0}_{1}".format( 2, x), "histo2d_{0}_{1}".format( 2, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[ 3][x] = dfzllcat[3*x+ltype].Filter("tight_mu2[0] == true").Histo2D(("histo2d_{0}_{1}".format( 3, x), "histo2d_{0}_{1}".format( 3, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[ 4][x] = dfzllcat[3*x+ltype].Filter("tight_mu3[0] == true").Histo2D(("histo2d_{0}_{1}".format( 4, x), "histo2d_{0}_{1}".format( 4, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[ 5][x] = dfzllcat[3*x+ltype].Filter("tight_mu4[0] == true").Histo2D(("histo2d_{0}_{1}".format( 5, x), "histo2d_{0}_{1}".format( 5, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[ 6][x] = dfzllcat[3*x+ltype].Filter("tight_mu5[0] == true").Histo2D(("histo2d_{0}_{1}".format( 6, x), "histo2d_{0}_{1}".format( 6, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[ 7][x] = dfzllcat[3*x+ltype].Filter("tight_mu6[0] == true").Histo2D(("histo2d_{0}_{1}".format( 7, x), "histo2d_{0}_{1}".format( 7, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[ 8][x] = dfzllcat[3*x+ltype].Filter("tight_mu7[0] == true").Histo2D(("histo2d_{0}_{1}".format( 8, x), "histo2d_{0}_{1}".format( 8, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[ 9][x] = dfzllcat[3*x+ltype].Filter("tight_mu8[0] == true").Histo2D(("histo2d_{0}_{1}".format( 9, x), "histo2d_{0}_{1}".format( 9, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")

                histo2D[10][x] = dfzllcat[3*x+ltype]                               .Histo2D(("histo2d_{0}_{1}".format(10, x), "histo2d_{0}_{1}".format(10, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[11][x] = dfzllcat[3*x+ltype].Filter("tight_mu0[1] == true").Histo2D(("histo2d_{0}_{1}".format(11, x), "histo2d_{0}_{1}".format(11, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[12][x] = dfzllcat[3*x+ltype].Filter("tight_mu1[1] == true").Histo2D(("histo2d_{0}_{1}".format(12, x), "histo2d_{0}_{1}".format(12, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[13][x] = dfzllcat[3*x+ltype].Filter("tight_mu2[1] == true").Histo2D(("histo2d_{0}_{1}".format(13, x), "histo2d_{0}_{1}".format(13, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[14][x] = dfzllcat[3*x+ltype].Filter("tight_mu3[1] == true").Histo2D(("histo2d_{0}_{1}".format(14, x), "histo2d_{0}_{1}".format(14, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[15][x] = dfzllcat[3*x+ltype].Filter("tight_mu4[1] == true").Histo2D(("histo2d_{0}_{1}".format(15, x), "histo2d_{0}_{1}".format(15, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[16][x] = dfzllcat[3*x+ltype].Filter("tight_mu5[1] == true").Histo2D(("histo2d_{0}_{1}".format(16, x), "histo2d_{0}_{1}".format(16, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[17][x] = dfzllcat[3*x+ltype].Filter("tight_mu6[1] == true").Histo2D(("histo2d_{0}_{1}".format(17, x), "histo2d_{0}_{1}".format(17, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[18][x] = dfzllcat[3*x+ltype].Filter("tight_mu7[1] == true").Histo2D(("histo2d_{0}_{1}".format(18, x), "histo2d_{0}_{1}".format(18, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[19][x] = dfzllcat[3*x+ltype].Filter("tight_mu8[1] == true").Histo2D(("histo2d_{0}_{1}".format(19, x), "histo2d_{0}_{1}".format(19, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")

            if(ltype == 2):
                histo2D[20][x] = dfzllcat[3*x+ltype]                               .Histo2D(("histo2d_{0}_{1}".format(20, x), "histo2d_{0}_{1}".format(20, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[21][x] = dfzllcat[3*x+ltype].Filter("tight_el0[0] == true").Histo2D(("histo2d_{0}_{1}".format(21, x), "histo2d_{0}_{1}".format(21, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[22][x] = dfzllcat[3*x+ltype].Filter("tight_el1[0] == true").Histo2D(("histo2d_{0}_{1}".format(22, x), "histo2d_{0}_{1}".format(22, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[23][x] = dfzllcat[3*x+ltype].Filter("tight_el2[0] == true").Histo2D(("histo2d_{0}_{1}".format(23, x), "histo2d_{0}_{1}".format(23, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[24][x] = dfzllcat[3*x+ltype].Filter("tight_el3[0] == true").Histo2D(("histo2d_{0}_{1}".format(24, x), "histo2d_{0}_{1}".format(24, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[25][x] = dfzllcat[3*x+ltype].Filter("tight_el4[0] == true").Histo2D(("histo2d_{0}_{1}".format(25, x), "histo2d_{0}_{1}".format(25, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[26][x] = dfzllcat[3*x+ltype].Filter("tight_el5[0] == true").Histo2D(("histo2d_{0}_{1}".format(26, x), "histo2d_{0}_{1}".format(26, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[27][x] = dfzllcat[3*x+ltype].Filter("tight_el6[0] == true").Histo2D(("histo2d_{0}_{1}".format(27, x), "histo2d_{0}_{1}".format(27, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[28][x] = dfzllcat[3*x+ltype].Filter("tight_el7[0] == true").Histo2D(("histo2d_{0}_{1}".format(28, x), "histo2d_{0}_{1}".format(28, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")
                histo2D[29][x] = dfzllcat[3*x+ltype].Filter("tight_el8[0] == true").Histo2D(("histo2d_{0}_{1}".format(29, x), "histo2d_{0}_{1}".format(29, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal1", "ptl1","weight")

                histo2D[30][x] = dfzllcat[3*x+ltype]                               .Histo2D(("histo2d_{0}_{1}".format(30, x), "histo2d_{0}_{1}".format(30, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[31][x] = dfzllcat[3*x+ltype].Filter("tight_el0[1] == true").Histo2D(("histo2d_{0}_{1}".format(31, x), "histo2d_{0}_{1}".format(31, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[32][x] = dfzllcat[3*x+ltype].Filter("tight_el1[1] == true").Histo2D(("histo2d_{0}_{1}".format(32, x), "histo2d_{0}_{1}".format(32, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[33][x] = dfzllcat[3*x+ltype].Filter("tight_el2[1] == true").Histo2D(("histo2d_{0}_{1}".format(33, x), "histo2d_{0}_{1}".format(33, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[34][x] = dfzllcat[3*x+ltype].Filter("tight_el3[1] == true").Histo2D(("histo2d_{0}_{1}".format(34, x), "histo2d_{0}_{1}".format(34, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[35][x] = dfzllcat[3*x+ltype].Filter("tight_el4[1] == true").Histo2D(("histo2d_{0}_{1}".format(35, x), "histo2d_{0}_{1}".format(35, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[36][x] = dfzllcat[3*x+ltype].Filter("tight_el5[1] == true").Histo2D(("histo2d_{0}_{1}".format(36, x), "histo2d_{0}_{1}".format(36, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[37][x] = dfzllcat[3*x+ltype].Filter("tight_el6[1] == true").Histo2D(("histo2d_{0}_{1}".format(37, x), "histo2d_{0}_{1}".format(37, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[38][x] = dfzllcat[3*x+ltype].Filter("tight_el7[1] == true").Histo2D(("histo2d_{0}_{1}".format(38, x), "histo2d_{0}_{1}".format(38, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")
                histo2D[39][x] = dfzllcat[3*x+ltype].Filter("tight_el8[1] == true").Histo2D(("histo2d_{0}_{1}".format(39, x), "histo2d_{0}_{1}".format(39, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal2", "ptl2","weight")

            dfzllcat[3*x+ltype] = dfzllcat[3*x+ltype].Filter("ptl1 > 25 && ptl2 > 25")
            histo[ltype+300][x] = dfzllcat[3*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+300,x), "histo_{0}_{1}".format(ltype+300,x), 20, 25, 125), "ptl2","weight")
            for nTrg in range(len(list_TRIGGER)):
                histo[3*nTrg+ltype+303][x] = dfzllcat[3*x+ltype].Filter("{0} > 0".format(list_TRIGGER[nTrg])).Histo1D(("histo_{0}_{1}".format(3*nTrg+ltype+303,x), "histo_{0}_{1}".format(3*nTrg+ltype+303,x), 20, 25, 125), "ptl2","weight")

    report = []
    for x in range(nCat):
        for ltype in range(3):
            report.append(dfjetcat[3*x+ltype].Report())
            if(x != theCat): continue
            print("---------------- SUMMARY 3*{0}+{1} = {2} -------------".format(x,ltype,3*x+ltype))
            report[3*x+ltype].Print()

    #for i in range(nCat):
    #    if(histo[28][i].GetSumOfWeights() != 0): print("AAA({0}) {1}".format(i,histo[28][i].GetSumOfWeights()))
    myfile = ROOT.TFile("fillhisto_zAnalysis_sample{0}_year{1}_job{2}.root".format(count,year,whichJob),'RECREATE')
    for i in range(nCat):
        for j in range(nHisto):
            if(histo[j][i] == 0): continue
            histo[j][i].Write()
        for j in range(nHisto):
            if(histo2D[j][i] == 0): continue
            #if(histo2D[j][i].GetSumOfWeights() > 0): print("({0},{1}): {2}".format(j,i,histo2D[j][i].GetSumOfWeights()))
            histo2D[j][i].Write()
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

    '''
    runTree = ROOT.TChain("Runs")
    for f in range(len(files)):
        runTree.AddFile(files[f])
    for i in range(runTree.GetEntries()):
        runTree.GetEntry(i)
        genEventSumWeight += runTree.genEventSumw
        genEventSumNoWeight += runTree.genEventCount
        if(runTree.FindBranch("nLHEPdfSumw") and runTree.nLHEPdfSumw < nTheoryReplicas[0]):
            nTheoryReplicas[0] = runTree.nLHEPdfSumw
        for n in range(9):
            if(n < runTree.nLHEScaleSumw):
                genEventSumLHEScaleWeight[n] += runTree.LHEScaleSumw[n]
            else:
                genEventSumLHEScaleWeight[n] += 1.0
                nTheoryReplicas[1] = runTree.nLHEScaleSumw
        for n in range(4):
            if(n < runTree.nPSSumw):
                genEventSumPSWeight[n] += runTree.PSSumw[n]
            else:
                genEventSumPSWeight[n] += 1.0
                nTheoryReplicas[2] = runTree.nPSSumw
        genEventSumPSWeight[4] += 1
    runGetEntries = runTree.GetEntries()
    '''

    print(genEventSumWeight,genEventSumNoWeight)
    print(genEventSumLHEScaleWeight)
    print(genEventSumPSWeight)
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
