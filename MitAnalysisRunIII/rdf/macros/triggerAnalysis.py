import ROOT
import os, sys, getopt, json
from array import array

ROOT.ROOT.EnableImplicitMT(10)
from utilsCategory import plotCategory
from utilsAna import getMClist, getDATAlist
from utilsAna import SwitchSample, groupFiles, getTriggerFromJson, getLeptomSelFromJson, getLumi
from utilsSelection import selectionTauVeto, selectionPhoton, selectionJetMet, selection2LVar, selectionTrigger1L, selectionTrigger2L, selectionElMu, selectionWeigths, selectionGenLepJet
#from utilsAna import loadCorrectionSet

# 0 = T, 1 = M, 2 = L
bTagSel = 1
useBTaggingWeights = 0

altMass = "Def"

selectionJsonPath = "config/selection.json"

with open(selectionJsonPath) as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

JSON = jsonObject['JSON']

BARRELphotons = jsonObject['BARRELphotons']
ENDCAPphotons = jsonObject['ENDCAPphotons']

VBSSEL = jsonObject['VBSSEL']

muSelChoice = 0
FAKE_MU0   = "abs(Muon_eta)      < 2.4 && Muon_pt      > 10 && Muon_looseId      == true"
FAKE_MU1   = "abs(fake_Muon_eta) < 2.4 && fake_Muon_pt > 10 && fake_Muon_looseId == true"
MUOWP = "Medium"

elSelChoice = 0
FAKE_EL0   = "abs(Electron_eta)      < 2.5 && Electron_pt      > 10 && Electron_cutBased      >= 1"
FAKE_EL1   = "abs(fake_Electron_eta) < 2.5 && fake_Electron_pt > 10 && fake_Electron_cutBased >= 1"
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

    # This is a hack to avoid fakeable objects
    dftag = selectionElMu(dftag,year,FAKE_MU0,FAKE_MU1,FAKE_EL0,FAKE_EL1)

    overallLeptonSel = jsonObject['leptonSel']
    TIGHT_MU0 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU0", year)
    TIGHT_MU1 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU1", year)
    TIGHT_MU2 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU2", year)
    TIGHT_MU3 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU3", year)
    TIGHT_MU4 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU4", year)
    TIGHT_MU5 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU5", year)
    TIGHT_MU6 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU6", year)
    TIGHT_MU7 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU7", year)
    TIGHT_MU8 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU8", year)
    TIGHT_MU9 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU9", year)

    TIGHT_EL0 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL0", year)
    TIGHT_EL1 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL1", year)
    TIGHT_EL2 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL2", year)
    TIGHT_EL3 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL3", year)
    TIGHT_EL4 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL4", year)
    TIGHT_EL5 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL5", year)
    TIGHT_EL6 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL6", year)
    TIGHT_EL7 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL7", year)
    TIGHT_EL8 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL8", year)
    TIGHT_EL9 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL9", year)

    dftag = (dftag.Define("tight_mu0", "{0}".format(TIGHT_MU0))
                  .Define("tight_mu1", "{0}".format(TIGHT_MU1))
                  .Define("tight_mu2", "{0}".format(TIGHT_MU2))
                  .Define("tight_mu3", "{0}".format(TIGHT_MU3))
                  .Define("tight_mu4", "{0}".format(TIGHT_MU4))
                  .Define("tight_mu5", "{0}".format(TIGHT_MU5))
                  .Define("tight_mu6", "{0}".format(TIGHT_MU6))
                  .Define("tight_mu7", "{0}".format(TIGHT_MU7))
                  .Define("tight_mu8", "{0}".format(TIGHT_MU8))
                  .Define("tight_mu9", "{0}".format(TIGHT_MU9))
                  .Define("tight_el0", "{0}".format(TIGHT_EL0))
                  .Define("tight_el1", "{0}".format(TIGHT_EL1))
                  .Define("tight_el2", "{0}".format(TIGHT_EL2))
                  .Define("tight_el3", "{0}".format(TIGHT_EL3))
                  .Define("tight_el4", "{0}".format(TIGHT_EL4))
                  .Define("tight_el5", "{0}".format(TIGHT_EL5))
                  .Define("tight_el6", "{0}".format(TIGHT_EL6))
                  .Define("tight_el7", "{0}".format(TIGHT_EL7))
                  .Define("tight_el8", "{0}".format(TIGHT_EL8))
                  .Define("tight_el9", "{0}".format(TIGHT_EL9))

                  .Filter("nLoose == 2","Only two loose leptons")
                  .Filter("nFake == 2","Two fake leptons")
                  .Filter("nTight == 2","Two tight leptons")

                  .Filter("(Sum(fake_mu) == 2 and Max(fake_Muon_pt) > 30) or (Sum(fake_el) == 2 and Max(fake_Electron_pt) > 30)","At least one high pt lepton")
                  )

    dftag = selectionTauVeto(dftag,year,isData)
    dftag = selectionPhoton (dftag,year,BARRELphotons,ENDCAPphotons)
    dftag = selectionJetMet (dftag,year,bTagSel,isData,count,5.0)
    dftag = selection2LVar  (dftag,year,isData)

    dftag = (dftag.Filter("mll{0} > 55 && mll{0} < 125".format(altMass),"mll{0} loose cut".format(altMass))
                  .Filter("(Sum(fake_mu) == 2 and triggerSMU > 0) or (Sum(fake_el) == 2 and triggerSEL > 0)","Single trigger requirement")
                  )

    return dftag

def selectionFF(df,year,PDType,isData,TRIGGERFAKEMU,TRIGGERFAKEEL,count):

    dftag = selectionTrigger1L(df,year,PDType,JSON,isData,TRIGGERFAKEMU,TRIGGERFAKEEL)

    overallLeptonSel = jsonObject['leptonSel']
    FAKE_MU   = getLeptomSelFromJson(overallLeptonSel, "FAKE_MU",   year, 1)
    TIGHT_MU1 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU1", year)

    FAKE_EL   = getLeptomSelFromJson(overallLeptonSel, "FAKE_EL",   year, 1)
    TIGHT_EL1 = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL1", year)

    dftag = selectionElMu(dftag,year,FAKE_MU,TIGHT_MU1,FAKE_EL,TIGHT_EL1)

    dftag = (dftag.Filter("nLoose == 2","Only two loose leptons")
                  .Filter("nFake == 2","Two fake leptons")
                  .Filter("nTight == 2","Two tight leptons")
                  .Filter("(Sum(fake_mu) == 2 and triggerFAKEMU > 0 and Sum(fake_Muon_charge) == 0 and fake_Muon_pt[0] > 30 and fake_Muon_pt[1] > 30) or (Sum(fake_el) == 2 and triggerFAKEEL > 0 and Sum(fake_Electron_charge) == 0 and fake_Electron_pt[0] > 30 and fake_Electron_pt[1] > 30)","Two high pt leptons")
                  )

    dftag = selectionTauVeto(dftag,year,isData)
    dftag = selectionPhoton (dftag,year,BARRELphotons,ENDCAPphotons)
    dftag = selectionJetMet (dftag,year,bTagSel,isData,count,5.0)
    dftag = selection2LVar  (dftag,year,isData)

    dftag = (dftag.Filter("mll{0} > 80 && mll{0} < 100".format(altMass),"mll{0} cut".format(altMass))
                  )

    return dftag

def analysis(df,count,category,weight,year,PDType,isData,whichJob,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,puWeights,histoBTVEffEtaPtLF,histoBTVEffEtaPtCJ,histoBTVEffEtaPtBJ,histoFakeEtaPt_mu,histoFakeEtaPt_el,histoLepSFEtaPt_mu,histoLepSFEtaPt_el,histoTriggerSFEtaPt_0_0,histoTriggerSFEtaPt_0_1,histoTriggerSFEtaPt_0_2,histoTriggerSFEtaPt_0_3,histoTriggerSFEtaPt_1_0,histoTriggerSFEtaPt_1_1,histoTriggerSFEtaPt_1_2,histoTriggerSFEtaPt_1_3,histoTriggerSFEtaPt_2_0,histoTriggerSFEtaPt_2_1,histoTriggerSFEtaPt_2_2,histoTriggerSFEtaPt_2_3,histoTriggerSFEtaPt_3_0,histoTriggerSFEtaPt_3_1,histoTriggerSFEtaPt_3_2,histoTriggerSFEtaPt_3_3):

    print("starting {0} / {1} / {2} / {3} / {4} / {5} / {6}".format(count,category,weight,year,PDType,isData,whichJob))

    xMuPtBins = array('d', [10,15,20,25,30,35,40,45,50,55,60,70,80,90,100,150,200,250])
    xMuEtaBins = array('d', [0.0,0.3,0.6,0.9,1.2,1.5,1.8,2.1,2.5])
    xElPtBins = array('d', [10,15,20,25,30,35,40,45,50,55,60,70,80,90,100,150,200,250])
    xElEtaBins = array('d', [0.0,0.3,0.6,0.9,1.2,1.5,1.8,2.1,2.5])
    #xMuPtBins = array('d', [10.0,15.0,20.0,25.0,30.0,40.0,50.0,60.0,120.0,200.0])
    #xMuEtaBins = array('d', [0.0,0.9,1.2,2.1,2.5])
    #xElPtBins = array('d', [10.0,20.0,35.0,50.0,100.0,200.0])
    #xElEtaBins = array('d', [0.0,0.8,1.444,1.566,2.0,2.5])

    theCat = category
    if(theCat > 100): theCat = plotCategory("kPlotData")

    nCat, nHisto = plotCategory("kPlotCategories"), 500
    histo   = [[0 for y in range(nCat)] for x in range(nHisto)]
    histo2D = [[0 for y in range(nCat)] for x in range(nHisto)]

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
    print("Total number of lepton trigger paths: {0}".format(len(list_TRIGGER)))

    dfbase = selectionLL(df,year,PDType,isData,TRIGGERMUEG,TRIGGERDMU,TRIGGERSMU,TRIGGERDEL,TRIGGERSEL,count)

    if(isData == "false"):
        dfbase = selectionGenLepJet(dfbase,20,30,5.0)
        dfbase = (dfbase.Define("mjjGen", "compute_vbs_gen_variables(0,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass)")
                      )
    else:
        dfbase = (dfbase.Define("mjjGen", "{0}".format(0))
                      )

    dfbase = selectionWeigths(dfbase,isData,year,PDType,weight,0,bTagSel,useBTaggingWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,MUOWP,ELEWP,"",0)

    TRIGGERFAKEMU = getTriggerFromJson(overallTriggers, "TRIGGERFAKEMU", year)
    TRIGGERFAKEEL = getTriggerFromJson(overallTriggers, "TRIGGERFAKEEL", year)

    list_TRIGGERFAKEMU = TRIGGERFAKEMU.split('(')[1].split(')')[0].split('||')
    list_TRIGGERFAKEEL = TRIGGERFAKEEL.split('(')[1].split(')')[0].split('||')
    list_TRIGGERFAKE = list_TRIGGERFAKEMU
    list_TRIGGERFAKE.extend(list_TRIGGERFAKEEL)
    print("Total number of fake trigger paths: {0}".format(len(list_TRIGGERFAKE)))

    dffake = selectionFF(df,year,PDType,isData,TRIGGERFAKEMU,TRIGGERFAKEEL,count)

    if(isData == "false"):
        dffake = selectionGenLepJet(dffake,20,30,5.0)
        dffake = (dffake.Define("mjjGen", "compute_vbs_gen_variables(0,ngood_GenJets,good_GenJet_pt,good_GenJet_eta,good_GenJet_phi,good_GenJet_mass,ngood_GenDressedLeptons,good_GenDressedLepton_pdgId,good_GenDressedLepton_hasTauAnc,good_GenDressedLepton_pt,good_GenDressedLepton_eta,good_GenDressedLepton_phi,good_GenDressedLepton_mass)")
                      )
    else:
        dffake = (dffake.Define("mjjGen", "{0}".format(0))
                      )

    dffake = selectionWeigths(dffake,isData,year,PDType,weight,0,bTagSel,useBTaggingWeights,nTheoryReplicas,genEventSumLHEScaleRenorm,genEventSumPSRenorm,MUOWP,ELEWP,"",0)
    if(theCat == plotCategory("kPlotData")):
        dffake = (dffake.Define("weightFakeSel0", "weight")
                        .Define("weightFakeSel1", "weight")
                        .Define("weightFakeSel2", "weight")
                        )
    else:
        dffake = (dffake.Define("weightFakeSel0", "weight*compute_lumiFakeRate(fake_Muon_pt,fake_Electron_pt,0,{0})".format(year))
                        .Define("weightFakeSel1", "weight*compute_lumiFakeRate(fake_Muon_pt,fake_Electron_pt,1,{0})".format(year))
                        .Define("weightFakeSel2", "weight*compute_lumiFakeRate(fake_Muon_pt,fake_Electron_pt,2,{0})".format(year))
                        )

    xMllMin = [ 80,  80]
    xMllMax = [100, 100]
    dfcat = []
    dfzoscat = []
    dfzsscat = []
    dffakecat = []
    dfzosAltcat = []
    for x in range(nCat):
        for ltype in range(2):
            dfcat.append(dfbase.Filter("DiLepton_flavor=={0}".format(2*ltype), "flavor type == {0}".format(2*ltype))
                               .Define("kPlotNonPrompt", "{0}".format(plotCategory("kPlotNonPrompt")))
                               .Define("kPlotWS", "{0}".format(plotCategory("kPlotWS")))
                               .Define("theCat{0}".format(x), "compute_category({0},kPlotNonPrompt,kPlotWS,nFake,nTight,0)".format(theCat))
                               .Filter("theCat{0}=={1}".format(x,x), "correct category ({0})".format(x))
                               )
            dffakecat.append(dffake.Filter("DiLepton_flavor=={0}".format(2*ltype), "flavor type == {0}".format(2*ltype))
                                   .Define("kPlotNonPrompt", "{0}".format(plotCategory("kPlotNonPrompt")))
                                   .Define("kPlotWS", "{0}".format(plotCategory("kPlotWS")))
                                   .Define("theCat{0}".format(x), "compute_category({0},kPlotNonPrompt,kPlotWS,nFake,nTight,0)".format(theCat))
                                   .Filter("theCat{0}=={1}".format(x,x), "correct category ({0})".format(x))
                                   )

            histo[ltype+62][x] = dfcat[2*x+ltype].Filter("Sum(fake_Muon_charge)+Sum(fake_Electron_charge) == 0").Histo1D(("histo_{0}_{1}".format(ltype+62,x), "histo_{0}_{1}".format(ltype+62,x), 140, xMllMin[ltype]-25, xMllMax[ltype]+25), "mll{0}".format(altMass),"weightNoLepSF")
            dfcat[2*x+ltype] = dfcat[2*x+ltype].Filter("mll{0} > {1} && mll{0} < {2}".format(altMass,xMllMin[ltype],xMllMax[ltype]),"mll{0} tight cut".format(altMass))

            # Fake lepton study
            for trgfake in range(3):
                if(ltype == 0):
                    histo[ltype+50+2*trgfake][x] = dffakecat[2*x+ltype].Filter("{0}".format(list_TRIGGERFAKEMU[trgfake])).Histo1D(("histo_{0}_{1}".format(ltype+50+2*trgfake,x), "histo_{0}_{1}".format(ltype+50+2*trgfake,x), 100, xMllMin[ltype], xMllMax[ltype]), "mll{0}".format(altMass),"weightFakeSel{0}".format(trgfake))
                    histo[ltype+56+2*trgfake][x] = dffakecat[2*x+ltype].Filter("{0}".format(list_TRIGGERFAKEMU[trgfake])).Filter("{0}".format(TRIGGERSMU)).Histo1D(("histo_{0}_{1}".format(ltype+56+2*trgfake,x), "histo_{0}_{1}".format(ltype+56+2*trgfake,x), 100, xMllMin[ltype], xMllMax[ltype]), "mll{0}".format(altMass),"weightFakeSel{0}".format(trgfake))
                else:
                    histo[ltype+50+2*trgfake][x] = dffakecat[2*x+ltype].Filter("{0}".format(list_TRIGGERFAKEEL[trgfake])).Histo1D(("histo_{0}_{1}".format(ltype+50+2*trgfake,x), "histo_{0}_{1}".format(ltype+50+2*trgfake,x), 100, xMllMin[ltype], xMllMax[ltype]), "mll{0}".format(altMass),"weightFakeSel{0}".format(trgfake))
                    histo[ltype+56+2*trgfake][x] = dffakecat[2*x+ltype].Filter("{0}".format(list_TRIGGERFAKEEL[trgfake])).Filter("{0}".format(TRIGGERSEL)).Histo1D(("histo_{0}_{1}".format(ltype+56+2*trgfake,x), "histo_{0}_{1}".format(ltype+56+2*trgfake,x), 100, xMllMin[ltype], xMllMax[ltype]), "mll{0}".format(altMass),"weightFakeSel{0}".format(trgfake))

            for ltag in range(2):
                # Real lepton study
                theLeptonSel = "((Sum(fake_mu) == 2 and tight_mu8[{0}] == true) or (Sum(fake_el) == 2 and tight_el8[{1}] == true))".format(ltag,ltag)
                dfzoscat.append(dfcat[2*x+ltype].Filter("Sum(fake_Muon_charge)+Sum(fake_Electron_charge) == 0 and {0}".format(theLeptonSel), "Opposite-sign leptons ({0})".format(ltag)))
                dfzsscat.append(dfcat[2*x+ltype].Filter("Sum(fake_Muon_charge)+Sum(fake_Electron_charge) != 0 and {0}".format(theLeptonSel), "Same-sign leptons ({0})".format(ltag)))

                tagTriggerMuSel = "(Sum(fake_mu) == 2 and hasTriggerMatch(    fake_Muon_eta[{0}],    fake_Muon_phi[{1}],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,13,1))".format(ltag,ltag)
                tagTriggerElSel = "(Sum(fake_el) == 2 and hasTriggerMatch(fake_Electron_eta[{0}],fake_Electron_phi[{1}],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,11,1))".format(ltag,ltag)

                dfzoscat[4*x+2*ltype+ltag] = dfzoscat[4*x+2*ltype+ltag].Filter("{0} or {1}".format(tagTriggerMuSel,tagTriggerElSel),"Tag trigger match ({0})".format(ltag))
                dfzsscat[4*x+2*ltype+ltag] = dfzsscat[4*x+2*ltype+ltag].Filter("{0} or {1}".format(tagTriggerMuSel,tagTriggerElSel),"Tag trigger match ({0})".format(ltag))

                histo[2*ltype+ltag+ 0][x] = dfzoscat[4*x+2*ltype+ltag].Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+ 0,x), "histo_{0}_{1}".format(2*ltype+ltag+ 0,x), 100, xMllMin[ltype], xMllMax[ltype]), "mll{0}".format(altMass),"weightNoLepSF")
                histo[2*ltype+ltag+ 4][x] = dfzsscat[4*x+2*ltype+ltag].Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+ 4,x), "histo_{0}_{1}".format(2*ltype+ltag+ 4,x), 100, xMllMin[ltype], xMllMax[ltype]), "mll{0}".format(altMass),"weightNoLepSF")

                lprobe = 1
                if(ltag == 1): lprobe = 0

                lflavor = "tight_mu"
                if(ltype == 1): lflavor = "tight_el"

                lepSelChoice = muSelChoice
                if(ltype == 1): lepSelChoice = elSelChoice

                xPtBins = xMuPtBins
                xEtaBins = xMuEtaBins
                if(ltype == 1):
                    xPtBins = xElPtBins
                    xEtaBins = xElEtaBins

                histo2D[2*ltype+ltag+ 0][x] = dfzoscat[4*x+2*ltype+ltag]                                                   .Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+ 0, x), "histo2d_{0}_{1}".format(2*ltype+ltag+ 0, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weightNoLepSF")
                histo2D[2*ltype+ltag+ 4][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0}0[{1}] == true".format(lflavor,lprobe)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+ 4, x), "histo2d_{0}_{1}".format(2*ltype+ltag+ 4, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weightNoLepSF")
                histo2D[2*ltype+ltag+ 8][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0}1[{1}] == true".format(lflavor,lprobe)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+ 8, x), "histo2d_{0}_{1}".format(2*ltype+ltag+ 8, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weightNoLepSF")
                histo2D[2*ltype+ltag+12][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0}2[{1}] == true".format(lflavor,lprobe)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+12, x), "histo2d_{0}_{1}".format(2*ltype+ltag+12, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weightNoLepSF")
                histo2D[2*ltype+ltag+16][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0}3[{1}] == true".format(lflavor,lprobe)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+16, x), "histo2d_{0}_{1}".format(2*ltype+ltag+16, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weightNoLepSF")
                histo2D[2*ltype+ltag+20][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0}4[{1}] == true".format(lflavor,lprobe)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+20, x), "histo2d_{0}_{1}".format(2*ltype+ltag+20, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weightNoLepSF")
                histo2D[2*ltype+ltag+24][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0}5[{1}] == true".format(lflavor,lprobe)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+24, x), "histo2d_{0}_{1}".format(2*ltype+ltag+24, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weightNoLepSF")
                histo2D[2*ltype+ltag+28][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0}6[{1}] == true".format(lflavor,lprobe)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+28, x), "histo2d_{0}_{1}".format(2*ltype+ltag+28, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weightNoLepSF")
                histo2D[2*ltype+ltag+32][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0}7[{1}] == true".format(lflavor,lprobe)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+32, x), "histo2d_{0}_{1}".format(2*ltype+ltag+32, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weightNoLepSF")
                histo2D[2*ltype+ltag+36][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0}8[{1}] == true".format(lflavor,lprobe)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+36, x), "histo2d_{0}_{1}".format(2*ltype+ltag+36, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weightNoLepSF")
                histo2D[2*ltype+ltag+40][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0}9[{1}] == true".format(lflavor,lprobe)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+40, x), "histo2d_{0}_{1}".format(2*ltype+ltag+40, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weightNoLepSF")

                histo[2*ltype+ltag+ 8][x] = dfzoscat[4*x+2*ltype+ltag].Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+ 8,x), "histo_{0}_{1}".format(2*ltype+ltag+ 8,x), len(xPtBins)-1, xPtBins), "ptl{0}".format(lprobe+1),"weightNoLepSF")

                histo[2*ltype+ltag+16][x] = dfzoscat[4*x+2*ltype+ltag].Filter("ptl{0} > 10 && ptl{0} < 15".format(lprobe+1)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+16,x), "histo_{0}_{1}".format(2*ltype+ltag+16,x), 100, xMllMin[ltype], xMllMax[ltype]), "mll{0}".format(altMass),"weightNoLepSF")
                histo[2*ltype+ltag+20][x] = dfzoscat[4*x+2*ltype+ltag].Filter("ptl{0} > 15 && ptl{0} < 20".format(lprobe+1)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+20,x), "histo_{0}_{1}".format(2*ltype+ltag+20,x), 100, xMllMin[ltype], xMllMax[ltype]), "mll{0}".format(altMass),"weightNoLepSF")
                histo[2*ltype+ltag+24][x] = dfzoscat[4*x+2*ltype+ltag].Filter("ptl{0} > 20 && ptl{0} < 25".format(lprobe+1)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+24,x), "histo_{0}_{1}".format(2*ltype+ltag+24,x), 100, xMllMin[ltype], xMllMax[ltype]), "mll{0}".format(altMass),"weightNoLepSF")
                histo[2*ltype+ltag+28][x] = dfzoscat[4*x+2*ltype+ltag].Filter("ptl{0} > 25 && ptl{0} < 30".format(lprobe+1)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+28,x), "histo_{0}_{1}".format(2*ltype+ltag+28,x), 100, xMllMin[ltype], xMllMax[ltype]), "mll{0}".format(altMass),"weightNoLepSF")

                if(ltype == 0):
                    histo[2*ltype+ltag+32][x] = dfzoscat[4*x+2*ltype+ltag].Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+32,x), "histo_{0}_{1}".format(2*ltype+ltag+32,x), 100, xMllMin[ltype], xMllMax[ltype]), "mllMuonMomUp","weightNoLepSF")
                    histo[2*ltype+ltag+36][x] = dfzoscat[4*x+2*ltype+ltag].Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+36,x), "histo_{0}_{1}".format(2*ltype+ltag+36,x), 100, xMllMin[ltype], xMllMax[ltype]), "mllMuonMomDown","weightNoLepSF")
                    dfzoscat[4*x+2*ltype+ltag] = (dfzoscat[4*x+2*ltype+ltag].Define("probe_Muon_promptMVA","fake_Muon_promptMVA[{0}]".format(lprobe))
                                                                            .Define("probe_Muon_sip3d","fake_Muon_sip3d[{0}]".format(lprobe))
                                                                            .Define("probe_Muon_jetRelIso","fake_Muon_jetRelIso[{0}]".format(lprobe))
                                                                            .Define("probe_Muon_dxy","fake_Muon_dxy[{0}]".format(lprobe))
                                                                            .Define("probe_Muon_dz","fake_Muon_dz[{0}]".format(lprobe))
                                                                            .Define("probe_Muon_pfRelIso04_all","fake_Muon_pfRelIso04_all[{0}]".format(lprobe))
                                                                            .Define("probe_Muon_miniPFRelIso_all","fake_Muon_miniPFRelIso_all[{0}]".format(lprobe))
                                                                            .Define("probe_Muon_nStations","fake_Muon_nStations[{0}]".format(lprobe))
                                                                            .Define("probe_Muon_nTrackerLayers","fake_Muon_nTrackerLayers[{0}]".format(lprobe))
                                                                            .Define("probe_Muon_pfRelIso03_chg","fake_Muon_pfRelIso03_chg[{0}]".format(lprobe))
                                                                            .Define("probe_Muon_pfRelIso03_neu","max(fake_Muon_pfRelIso04_all[{0}]-fake_Muon_pfRelIso03_chg[{0}],0.0f)".format(lprobe,lprobe))
                                                                            .Define("probe_Muon_mvaMuID","fake_Muon_mvaMuID[{0}]".format(lprobe))
                                                                            .Define("probe_Muon_mvaLowPt","fake_Muon_mvaLowPt[{0}]".format(lprobe))
                                                                            )
                    histo[2*ltype+ltag+100][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+100,x), "histo_{0}_{1}".format(2*ltype+ltag+100,x), 100, 0, 1.0), "probe_Muon_promptMVA","weight")
                    histo[2*ltype+ltag+104][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+104,x), "histo_{0}_{1}".format(2*ltype+ltag+104,x), 100, 0, 1.0), "probe_Muon_promptMVA","weight")
                    histo[2*ltype+ltag+108][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+108,x), "histo_{0}_{1}".format(2*ltype+ltag+108,x), 100, 0,20.0), "probe_Muon_sip3d","weight")
                    histo[2*ltype+ltag+112][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+112,x), "histo_{0}_{1}".format(2*ltype+ltag+112,x), 100, 0,20.0), "probe_Muon_sip3d","weight")
                    histo[2*ltype+ltag+116][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+116,x), "histo_{0}_{1}".format(2*ltype+ltag+116,x), 100, 0, 1.0), "probe_Muon_jetRelIso","weight")
                    histo[2*ltype+ltag+120][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+120,x), "histo_{0}_{1}".format(2*ltype+ltag+120,x), 100, 0, 1.0), "probe_Muon_jetRelIso","weight")
                    histo[2*ltype+ltag+124][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+124,x), "histo_{0}_{1}".format(2*ltype+ltag+124,x), 100, 0, 0.1), "probe_Muon_dxy","weight")
                    histo[2*ltype+ltag+128][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+128,x), "histo_{0}_{1}".format(2*ltype+ltag+128,x), 100, 0, 0.1), "probe_Muon_dxy","weight")
                    histo[2*ltype+ltag+132][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+132,x), "histo_{0}_{1}".format(2*ltype+ltag+132,x), 100, 0, 0.2), "probe_Muon_dz","weight")
                    histo[2*ltype+ltag+136][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+136,x), "histo_{0}_{1}".format(2*ltype+ltag+136,x), 100, 0, 0.2), "probe_Muon_dz","weight")
                    histo[2*ltype+ltag+140][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+140,x), "histo_{0}_{1}".format(2*ltype+ltag+140,x),  90, 0, 0.3), "probe_Muon_pfRelIso04_all","weight")
                    histo[2*ltype+ltag+144][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+144,x), "histo_{0}_{1}".format(2*ltype+ltag+144,x),  90, 0, 0.3), "probe_Muon_pfRelIso04_all","weight")
                    histo[2*ltype+ltag+148][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+148,x), "histo_{0}_{1}".format(2*ltype+ltag+148,x),  90, 0, 0.3), "probe_Muon_miniPFRelIso_all","weight")
                    histo[2*ltype+ltag+152][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+152,x), "histo_{0}_{1}".format(2*ltype+ltag+152,x),  90, 0, 0.3), "probe_Muon_miniPFRelIso_all","weight")
                    histo[2*ltype+ltag+156][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+156,x), "histo_{0}_{1}".format(2*ltype+ltag+156,x), 6, -0.5,5.5), "probe_Muon_nStations","weight")
                    histo[2*ltype+ltag+160][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+160,x), "histo_{0}_{1}".format(2*ltype+ltag+160,x), 6, -0.5,5.5), "probe_Muon_nStations","weight")
                    histo[2*ltype+ltag+164][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+164,x), "histo_{0}_{1}".format(2*ltype+ltag+164,x),20,-0.5,19.5), "probe_Muon_nTrackerLayers","weight")
                    histo[2*ltype+ltag+168][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+168,x), "histo_{0}_{1}".format(2*ltype+ltag+168,x),20,-0.5,19.5), "probe_Muon_nTrackerLayers","weight")
                    histo[2*ltype+ltag+172][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+172,x), "histo_{0}_{1}".format(2*ltype+ltag+172,x),  90, 0, 0.3), "probe_Muon_pfRelIso03_chg","weight")
                    histo[2*ltype+ltag+176][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+176,x), "histo_{0}_{1}".format(2*ltype+ltag+176,x),  90, 0, 0.3), "probe_Muon_pfRelIso03_chg","weight")
                    histo[2*ltype+ltag+180][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+180,x), "histo_{0}_{1}".format(2*ltype+ltag+180,x), 100,0.0,1.0), "probe_Muon_mvaMuID","weight")
                    histo[2*ltype+ltag+184][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+184,x), "histo_{0}_{1}".format(2*ltype+ltag+184,x), 100,0.0,1.0), "probe_Muon_mvaMuID","weight")
                    histo[2*ltype+ltag+188][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+188,x), "histo_{0}_{1}".format(2*ltype+ltag+188,x), 100,-1, 1.0), "probe_Muon_mvaLowPt","weight")
                    histo[2*ltype+ltag+192][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+192,x), "histo_{0}_{1}".format(2*ltype+ltag+192,x), 100,-1, 1.0), "probe_Muon_mvaLowPt","weight")
                    histo[2*ltype+ltag+196][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+196,x), "histo_{0}_{1}".format(2*ltype+ltag+196,x),  90, 0, 0.3), "probe_Muon_pfRelIso03_neu","weight")
                    histo[2*ltype+ltag+200][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Muon_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+200,x), "histo_{0}_{1}".format(2*ltype+ltag+200,x),  90, 0, 0.3), "probe_Muon_pfRelIso03_neu","weight")
                else:
                    histo[2*ltype+ltag+32][x] = dfzoscat[4*x+2*ltype+ltag].Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+32,x), "histo_{0}_{1}".format(2*ltype+ltag+32,x), 100, xMllMin[ltype], xMllMax[ltype]), "mllElectronMomUp","weightNoLepSF")
                    histo[2*ltype+ltag+36][x] = dfzoscat[4*x+2*ltype+ltag].Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+36,x), "histo_{0}_{1}".format(2*ltype+ltag+36,x), 100, xMllMin[ltype], xMllMax[ltype]), "mllElectronMomDown","weightNoLepSF")
                    dfzoscat[4*x+2*ltype+ltag] = (dfzoscat[4*x+2*ltype+ltag].Define("probe_Electron_promptMVA","fake_Electron_promptMVA[{0}]".format(lprobe))
                                                                            .Define("probe_Electron_sip3d","fake_Electron_sip3d[{0}]".format(lprobe))
                                                                            .Define("probe_Electron_jetRelIso","fake_Electron_jetRelIso[{0}]".format(lprobe))
                                                                            .Define("probe_Electron_dxy","fake_Electron_dxy[{0}]".format(lprobe))
                                                                            .Define("probe_Electron_dz","fake_Electron_dz[{0}]".format(lprobe))
                                                                            .Define("probe_Electron_pfRelIso03_all","fake_Electron_pfRelIso03_all[{0}]".format(lprobe))
                                                                            .Define("probe_Electron_miniPFRelIso_all","fake_Electron_miniPFRelIso_all[{0}]".format(lprobe))
                                                                            .Define("probe_Electron_hoe","fake_Electron_hoe[{0}]".format(lprobe))
                                                                            .Define("probe_Electron_r9","fake_Electron_r9[{0}]".format(lprobe))
                                                                            .Define("probe_Electron_pfRelIso03_chg","fake_Electron_pfRelIso03_chg[{0}]".format(lprobe))
                                                                            .Define("probe_Electron_pfRelIso03_neu","max(fake_Electron_pfRelIso03_all[{0}]-fake_Electron_pfRelIso03_chg[{0}],0.0f)".format(lprobe,lprobe))
                                                                            .Define("probe_Electron_mvaIso","fake_Electron_mvaIso[{0}]".format(lprobe))
                                                                            .Define("probe_Electron_mvaNoIso","fake_Electron_mvaNoIso[{0}]".format(lprobe))
                                                                            )
                    histo[2*ltype+ltag+100][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+100,x), "histo_{0}_{1}".format(2*ltype+ltag+100,x), 100, 0, 1.0), "probe_Electron_promptMVA","weight")
                    histo[2*ltype+ltag+104][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+104,x), "histo_{0}_{1}".format(2*ltype+ltag+104,x), 100, 0, 1.0), "probe_Electron_promptMVA","weight")
                    histo[2*ltype+ltag+108][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+108,x), "histo_{0}_{1}".format(2*ltype+ltag+108,x), 100, 0,20.0), "probe_Electron_sip3d","weight")
                    histo[2*ltype+ltag+112][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+112,x), "histo_{0}_{1}".format(2*ltype+ltag+112,x), 100, 0,20.0), "probe_Electron_sip3d","weight")
                    histo[2*ltype+ltag+116][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+116,x), "histo_{0}_{1}".format(2*ltype+ltag+116,x), 100, 0, 1.0), "probe_Electron_jetRelIso","weight")
                    histo[2*ltype+ltag+120][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+120,x), "histo_{0}_{1}".format(2*ltype+ltag+120,x), 100, 0, 1.0), "probe_Electron_jetRelIso","weight")
                    histo[2*ltype+ltag+124][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+124,x), "histo_{0}_{1}".format(2*ltype+ltag+124,x), 100, 0, 0.1), "probe_Electron_dxy","weight")
                    histo[2*ltype+ltag+128][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+128,x), "histo_{0}_{1}".format(2*ltype+ltag+128,x), 100, 0, 0.1), "probe_Electron_dxy","weight")
                    histo[2*ltype+ltag+132][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+132,x), "histo_{0}_{1}".format(2*ltype+ltag+132,x), 100, 0, 0.2), "probe_Electron_dz","weight")
                    histo[2*ltype+ltag+136][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+136,x), "histo_{0}_{1}".format(2*ltype+ltag+136,x), 100, 0, 0.2), "probe_Electron_dz","weight")
                    histo[2*ltype+ltag+140][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+140,x), "histo_{0}_{1}".format(2*ltype+ltag+140,x),  90, 0, 0.3), "probe_Electron_pfRelIso03_all","weight")
                    histo[2*ltype+ltag+144][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+144,x), "histo_{0}_{1}".format(2*ltype+ltag+144,x),  90, 0, 0.3), "probe_Electron_pfRelIso03_all","weight")
                    histo[2*ltype+ltag+148][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+148,x), "histo_{0}_{1}".format(2*ltype+ltag+148,x),  90, 0, 0.3), "probe_Electron_miniPFRelIso_all","weight")
                    histo[2*ltype+ltag+152][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+152,x), "histo_{0}_{1}".format(2*ltype+ltag+152,x),  90, 0, 0.3), "probe_Electron_miniPFRelIso_all","weight")
                    histo[2*ltype+ltag+156][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+156,x), "histo_{0}_{1}".format(2*ltype+ltag+156,x),  40, 0, 0.2), "probe_Electron_hoe","weight")
                    histo[2*ltype+ltag+160][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+160,x), "histo_{0}_{1}".format(2*ltype+ltag+160,x),  40, 0, 0.2), "probe_Electron_hoe","weight")
                    histo[2*ltype+ltag+164][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+164,x), "histo_{0}_{1}".format(2*ltype+ltag+164,x),100, 0.1,1.1), "probe_Electron_r9","weight")
                    histo[2*ltype+ltag+168][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+168,x), "histo_{0}_{1}".format(2*ltype+ltag+168,x),100, 0.1,1.1), "probe_Electron_r9","weight")
                    histo[2*ltype+ltag+172][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+172,x), "histo_{0}_{1}".format(2*ltype+ltag+172,x),  90, 0, 0.3), "probe_Electron_pfRelIso03_chg","weight")
                    histo[2*ltype+ltag+176][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+176,x), "histo_{0}_{1}".format(2*ltype+ltag+176,x),  90, 0, 0.3), "probe_Electron_pfRelIso03_chg","weight")
                    histo[2*ltype+ltag+180][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+180,x), "histo_{0}_{1}".format(2*ltype+ltag+180,x), 200,-1, 1.0), "probe_Electron_mvaIso","weight")
                    histo[2*ltype+ltag+184][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+184,x), "histo_{0}_{1}".format(2*ltype+ltag+184,x), 200,-1, 1.0), "probe_Electron_mvaIso","weight")
                    histo[2*ltype+ltag+188][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+188,x), "histo_{0}_{1}".format(2*ltype+ltag+188,x), 200,-1, 1.0), "probe_Electron_mvaNoIso","weight")
                    histo[2*ltype+ltag+192][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+192,x), "histo_{0}_{1}".format(2*ltype+ltag+192,x), 200,-1, 1.0), "probe_Electron_mvaNoIso","weight")
                    histo[2*ltype+ltag+196][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] > 30".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+196,x), "histo_{0}_{1}".format(2*ltype+ltag+196,x),  90, 0, 0.3), "probe_Electron_pfRelIso03_neu","weight")
                    histo[2*ltype+ltag+200][x] = dfzoscat[4*x+2*ltype+ltag].Filter("fake_Electron_pt[{0}] < 25".format(lprobe)).Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+200,x), "histo_{0}_{1}".format(2*ltype+ltag+200,x),  90, 0, 0.3), "probe_Electron_pfRelIso03_neu","weight")

                # trigger ID to perform trigger efficiency measurements
                dfzosAltcat.append(dfzoscat[4*x+2*ltype+ltag].Filter("{0}{1}[{2}] == true".format(lflavor,9,lprobe),"tight id({0}{1}[{2}])".format(lflavor,9,lprobe)))

                # tighter ID to perform trigger efficiency measurements
                dfzoscat[4*x+2*ltype+ltag] = dfzoscat[4*x+2*ltype+ltag].Filter("{0}{1}[{2}] == true".format(lflavor,lepSelChoice,lprobe),"tight id({0}{1}[{2}])".format(lflavor,lepSelChoice,lprobe))
                dfzsscat[4*x+2*ltype+ltag] = dfzsscat[4*x+2*ltype+ltag].Filter("{0}{1}[{2}] == true".format(lflavor,lepSelChoice,lprobe),"tight id({0}{1}[{2}])".format(lflavor,lepSelChoice,lprobe))

                histo[2*ltype+ltag+12][x] = dfzoscat[4*x+2*ltype+ltag].Histo1D(("histo_{0}_{1}".format(2*ltype+ltag+12,x), "histo_{0}_{1}".format(2*ltype+ltag+12,x), len(xPtBins)-1, xPtBins), "ptl{0}".format(lprobe+1),"weightNoLepSF")
                probeTriggerSMuSel  = "(Sum(fake_mu) == 2 and hasTriggerMatch(    fake_Muon_eta[{0}],    fake_Muon_phi[{1}],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,13,1))".format(lprobe,lprobe)
                probeTriggerSElSel  = "(Sum(fake_el) == 2 and hasTriggerMatch(fake_Electron_eta[{0}],fake_Electron_phi[{1}],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,11,1))".format(lprobe,lprobe)
                probeTriggerDMuSel  = "(Sum(fake_mu) == 2 and hasTriggerMatch(    fake_Muon_eta[{0}],    fake_Muon_phi[{1}],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,13,0))".format(lprobe,lprobe)
                probeTriggerDElSel  = "(Sum(fake_el) == 2 and hasTriggerMatch(fake_Electron_eta[{0}],fake_Electron_phi[{1}],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,11,0))".format(lprobe,lprobe)
                probeTrigger1MuSel0 = "(Sum(fake_mu) == 2 and hasTriggerMatch(    fake_Muon_eta[{0}],    fake_Muon_phi[{1}],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,13,2) &&     fake_Muon_pt[{2}] > 10 && HLT_Mu8_TrkIsoVVL)".format(lprobe,lprobe,lprobe)
                probeTrigger1ElSel0 = "(Sum(fake_el) == 2 and hasTriggerMatch(fake_Electron_eta[{0}],fake_Electron_phi[{1}],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,11,2) && fake_Electron_pt[{2}] > 10 && HLT_Ele8_CaloIdL_TrackIdL_IsoVL_PFJet30)".format(lprobe,lprobe,lprobe)
                probeTrigger1MuSel1 = "(Sum(fake_mu) == 2 and hasTriggerMatch(    fake_Muon_eta[{0}],    fake_Muon_phi[{1}],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,13,2) &&     fake_Muon_pt[{2}] > 20 && HLT_Mu17_TrkIsoVVL)".format(lprobe,lprobe,lprobe)
                probeTrigger1ElSel1 = "(Sum(fake_el) == 2 and hasTriggerMatch(fake_Electron_eta[{0}],fake_Electron_phi[{1}],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,11,2) && fake_Electron_pt[{2}] > 15 && HLT_Ele12_CaloIdL_TrackIdL_IsoVL_PFJet30)".format(lprobe,lprobe,lprobe)
                probeTrigger1MuSel2 = "(Sum(fake_mu) == 2 and hasTriggerMatch(    fake_Muon_eta[{0}],    fake_Muon_phi[{1}],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,13,2) &&     fake_Muon_pt[{2}] > 20 && HLT_Mu19_TrkIsoVVL)".format(lprobe,lprobe,lprobe)
                probeTrigger1ElSel2 = "(Sum(fake_el) == 2 and hasTriggerMatch(fake_Electron_eta[{0}],fake_Electron_phi[{1}],TrigObj_eta,TrigObj_phi,TrigObj_id,TrigObj_filterBits,11,2) && fake_Electron_pt[{2}] > 25 && HLT_Ele23_CaloIdL_TrackIdL_IsoVL_PFJet30)".format(lprobe,lprobe,lprobe)

                histo2D[2*ltype+ltag+50][x] = dfzoscat[4*x+2*ltype+ltag]                                                                     .Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+50, x), "histo2d_{0}_{1}".format(2*ltype+ltag+50, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weight")
                histo2D[2*ltype+ltag+54][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0} or {1}".format(probeTriggerSMuSel,probeTriggerSElSel))  .Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+54, x), "histo2d_{0}_{1}".format(2*ltype+ltag+54, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weight")
                histo2D[2*ltype+ltag+58][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0} or {1}".format(probeTriggerDMuSel,probeTriggerDElSel))  .Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+58, x), "histo2d_{0}_{1}".format(2*ltype+ltag+58, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weight")
                histo2D[2*ltype+ltag+62][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0} or {1}".format(probeTrigger1MuSel0,probeTrigger1ElSel0)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+62, x), "histo2d_{0}_{1}".format(2*ltype+ltag+62, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weight")
                histo2D[2*ltype+ltag+66][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0} or {1}".format(probeTrigger1MuSel1,probeTrigger1ElSel1)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+66, x), "histo2d_{0}_{1}".format(2*ltype+ltag+66, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weight")
                histo2D[2*ltype+ltag+70][x] = dfzoscat[4*x+2*ltype+ltag].Filter("{0} or {1}".format(probeTrigger1MuSel2,probeTrigger1ElSel2)).Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+70, x), "histo2d_{0}_{1}".format(2*ltype+ltag+70, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weight")

                histo2D[2*ltype+ltag+74][x] = dfzosAltcat[4*x+2*ltype+ltag]                                                                  .Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+74, x), "histo2d_{0}_{1}".format(2*ltype+ltag+74, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weight")
                histo2D[2*ltype+ltag+78][x] = dfzosAltcat[4*x+2*ltype+ltag].Filter("{0}or{1}".format(probeTriggerSMuSel,probeTriggerSElSel)) .Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+78, x), "histo2d_{0}_{1}".format(2*ltype+ltag+78, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weight")
                histo2D[2*ltype+ltag+82][x] = dfzosAltcat[4*x+2*ltype+ltag].Filter("{0}or{1}".format(probeTriggerDMuSel,probeTriggerDElSel)) .Histo2D(("histo2d_{0}_{1}".format(2*ltype+ltag+82, x), "histo2d_{0}_{1}".format(2*ltype+ltag+82, x), len(xEtaBins)-1, xEtaBins, len(xPtBins)-1, xPtBins), "etal{0}".format(lprobe+1), "ptl{0}".format(lprobe+1),"weight")

    report = []
    for x in range(nCat):
        for ltype in range(2):
            for ltag in range(2):
                report.append(dfzoscat[4*x+2*ltype+ltag].Report())
                if(x != theCat): continue
                print("---------------- SUMMARY 4*{0}+2*{1}+{2} = {3} -------------".format(x,ltype,ltag,4*x+2*ltype+ltag))
                report[4*x+2*ltype+ltag].Print()

    myfile = ROOT.TFile("fillhisto_triggerAnalysis_sample{0}_year{1}_job{2}.root".format(count,year,whichJob),'RECREATE')
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

    lepSFPath = "data/histoLepSFEtaPt_{0}.root".format(year)
    fLepSFFile = ROOT.TFile(lepSFPath)
    histoLepSFEtaPt_mu = fLepSFFile.Get("histoLepSFEtaPt_0_{0}".format(muSelChoice))
    histoLepSFEtaPt_el = fLepSFFile.Get("histoLepSFEtaPt_0_{0}".format(elSelChoice))
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
