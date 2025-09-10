import ROOT
import os, sys, getopt, json, time
from array import array

ROOT.ROOT.EnableImplicitMT(10)
from utilsCategory import plotCategory
from utilsAna import getMClist, getDATAlist, getLumi
from utilsAna import SwitchSample, groupFiles, getTriggerFromJson, getLeptomSelFromJson
from utilsSelection import selection2LVar, selectionElMu

selectionJsonPath = "config/selection.json"
if(not os.path.exists(selectionJsonPath)):
    selectionJsonPath = "selection.json"

with open(selectionJsonPath) as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

JSON = jsonObject['JSON']

VBSSEL = jsonObject['VBSSEL']

muSelChoice = 0

elSelChoice = 0

def selectionLL(df,year,PDType,isData):

    overallTriggers = jsonObject['triggers']
    TRIGGERMET = getTriggerFromJson(overallTriggers, "TRIGGERMET", year)

    TRIGGERMUEG = getTriggerFromJson(overallTriggers, "TRIGGERMUEG", year)
    TRIGGERDMU  = getTriggerFromJson(overallTriggers, "TRIGGERDMU", year)
    TRIGGERSMU  = getTriggerFromJson(overallTriggers, "TRIGGERSMU", year)
    TRIGGERDEL  = getTriggerFromJson(overallTriggers, "TRIGGERDEL", year)
    TRIGGERSEL  = getTriggerFromJson(overallTriggers, "TRIGGERSEL", year)

    TRIGGERLEP = "{0} or {1} or {2} or {3} or {4}".format(TRIGGERSEL,TRIGGERDEL,TRIGGERSMU,TRIGGERDMU,TRIGGERMUEG)

    dftag =(df.Define("isData","{}".format(isData))
              .Define("applyJson","{}".format(JSON)).Filter("applyJson","pass JSON")
              .Define("triggerMET","{0}".format(TRIGGERMET))
              )

    overallLeptonSel = jsonObject['leptonSel']
    FAKE_MU   = getLeptomSelFromJson(overallLeptonSel, "FAKE_MU",   year)
    TIGHT_MU  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_MU{0}".format(muSelChoice),  year, 1)

    FAKE_EL   = getLeptomSelFromJson(overallLeptonSel, "FAKE_EL",   year)
    TIGHT_EL  = getLeptomSelFromJson(overallLeptonSel, "TIGHT_EL{0}".format(elSelChoice),  year, 1)

    dftag = selectionElMu(dftag,year,FAKE_MU,TIGHT_MU,FAKE_EL,TIGHT_EL)

    dftag = (dftag.Filter("Sum(fake_mu)+Sum(fake_el) >= 2 and Sum(fake_mu)+Sum(fake_el) <= 4","Between two and four tight leptons")
                  .Filter("(Sum(fake_mu) > 0 and Max(fake_Muon_pt) > 25) or (Sum(fake_el) > 0 and Max(fake_Electron_pt) > 25)","At least one high pt lepton")
                  .Define("MultiLepton_flavor", "Sum(fake_mu)+4*Sum(fake_el)-2")\
                  .Define("mtot",  "compute_nl_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,0)")
                  .Define("mllmin","compute_nl_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,1)")
                  .Filter("mllmin > 10")
                  .Define("triggerl","{0}".format(TRIGGERLEP))
                  .Define("ptlmax", "compute_nl_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,3)")
                  .Define("ptlmin", "compute_nl_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,4)")
                  .Define("etalmax","compute_nl_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,5)")
                  .Define("etalmin","compute_nl_var(fake_Muon_pt, fake_Muon_eta, fake_Muon_phi, fake_Muon_mass, fake_Muon_charge, fake_Electron_pt, fake_Electron_eta, fake_Electron_phi, fake_Electron_mass, fake_Electron_charge, PuppiMET_pt, PuppiMET_phi,6)")
                  )

    dftag = selection2LVar(dftag,year,isData)

    return dftag


def analysis(df,count,category,weight,year,PDType,isData,whichJob):

    print("starting {0} / {1} / {2} / {3} / {4} / {5} / {6}".format(count,category,weight,year,PDType,isData,whichJob))

    xPtMaxBinsV1 = array('d', [25,35,50,80,100])
    xPtMaxBinsV2 = array('d', [25,40,55,85,100])

    xPtMinBinsV1 = array('d', [10,20,30,40,50,100])
    xPtMinBinsV2 = array('d', [10,25,40,55,85,100])

    xPtBinsV1 = array('d', [10,25,70])
    xPtBinsV2 = array('d', [10,35,70])

    xEtaBins = array('d', [0.0,1.5,2.5])

    theCat = category
    if(theCat > 100): theCat = plotCategory("kPlotData")

    nCat, nHisto = plotCategory("kPlotCategories"), 200
    histo   = [[0 for y in range(nCat)] for x in range(nHisto)]
    histo2D = [[0 for y in range(nCat)] for x in range(nHisto)]

    ROOT.initJSONSFs(year)

    dfbase = selectionLL(df,year,PDType,isData)

    if(theCat == plotCategory("kPlotData")):
        dfbase = dfbase.Define("weight","1.0")
    else:
        dfbase = dfbase.Define("PDType","\"{0}\"".format(PDType))\
                       .Define("weight","1.0")

    dfcat = []
    for x in range(nCat):
        for ltype in range(6):
            dfcat.append(dfbase.Filter("ltype=={0}".format(ltype), "flavor type == {0}".format(ltype))
                               .Define("kPlotNonPrompt", "{0}".format(plotCategory("kPlotNonPrompt")))
                               .Define("kPlotWS", "{0}".format(plotCategory("kPlotWS")))
                               .Define("theCat{0}".format(x), "compute_category({0},kPlotNonPrompt,kPlotWS,2,2,0)".format(theCat))
                               .Filter("theCat{0}=={1}".format(x,x), "correct category ({0})".format(x)))

            histo[ltype+12][x] = dfcat[6*x+ltype]                                         .Histo1D(("histo_{0}_{1}".format(ltype+12,x), "histo_{0}_{1}".format(ltype+12,x), 40,  0, 400), "ptll","weight")
            histo[ltype+18][x] = dfcat[6*x+ltype].Filter("triggerMET > 0")                .Histo1D(("histo_{0}_{1}".format(ltype+18,x), "histo_{0}_{1}".format(ltype+18,x), 40,  0, 400), "ptll","weight")
            histo[ltype+24][x] = dfcat[6*x+ltype].Filter("triggerl > 0")                  .Histo1D(("histo_{0}_{1}".format(ltype+24,x), "histo_{0}_{1}".format(ltype+24,x), 40,  0, 400), "ptll","weight")
            histo[ltype+30][x] = dfcat[6*x+ltype].Filter("triggerMET > 0 && triggerl > 0").Histo1D(("histo_{0}_{1}".format(ltype+30,x), "histo_{0}_{1}".format(ltype+30,x), 40,  0, 400), "ptll","weight")

            dfcat[6*x+ltype] = dfcat[6*x+ltype].Filter("triggerMET > 0","Passed MET trigger")

            histo[ltype+ 0][x] = dfcat[6*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+ 0,x), "histo_{0}_{1}".format(ltype+ 0,x), 100,  0, 500), "mtot","weight")
            histo[ltype+ 6][x] = dfcat[6*x+ltype].Histo1D(("histo_{0}_{1}".format(ltype+ 6,x), "histo_{0}_{1}".format(ltype+ 6,x), 100,  0, 200), "mllmin","weight")

            iniHisto = 0
            histo2D[ltype+ 0+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax <= 1.5 && etalmin <= 1.5")                       .Histo2D(("histo2d_{0}_{1}".format(ltype+ 0+iniHisto,x), "histo2d_{0}_{1}".format(ltype+ 0+iniHisto,x), len(xPtMaxBinsV1)-1, xPtMaxBinsV1, len(xPtMinBinsV1)-1, xPtMinBinsV1), "ptlmax", "ptlmin","weight")
            histo2D[ltype+ 6+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax <= 1.5 && etalmin <= 1.5").Filter("triggerl > 0").Histo2D(("histo2d_{0}_{1}".format(ltype+ 6+iniHisto,x), "histo2d_{0}_{1}".format(ltype+ 6+iniHisto,x), len(xPtMaxBinsV1)-1, xPtMaxBinsV1, len(xPtMinBinsV1)-1, xPtMinBinsV1), "ptlmax", "ptlmin","weight")

            histo2D[ltype+12+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax >  1.5 && etalmin <= 1.5")                       .Histo2D(("histo2d_{0}_{1}".format(ltype+12+iniHisto,x), "histo2d_{0}_{1}".format(ltype+12+iniHisto,x), len(xPtMaxBinsV1)-1, xPtMaxBinsV1, len(xPtMinBinsV1)-1, xPtMinBinsV1), "ptlmax", "ptlmin","weight")
            histo2D[ltype+18+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax >  1.5 && etalmin <= 1.5").Filter("triggerl > 0").Histo2D(("histo2d_{0}_{1}".format(ltype+18+iniHisto,x), "histo2d_{0}_{1}".format(ltype+18+iniHisto,x), len(xPtMaxBinsV1)-1, xPtMaxBinsV1, len(xPtMinBinsV1)-1, xPtMinBinsV1), "ptlmax", "ptlmin","weight")

            histo2D[ltype+24+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax <= 1.5 && etalmin >  1.5")                       .Histo2D(("histo2d_{0}_{1}".format(ltype+24+iniHisto,x), "histo2d_{0}_{1}".format(ltype+24+iniHisto,x), len(xPtMaxBinsV1)-1, xPtMaxBinsV1, len(xPtMinBinsV1)-1, xPtMinBinsV1), "ptlmax", "ptlmin","weight")
            histo2D[ltype+30+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax <= 1.5 && etalmin >  1.5").Filter("triggerl > 0").Histo2D(("histo2d_{0}_{1}".format(ltype+30+iniHisto,x), "histo2d_{0}_{1}".format(ltype+30+iniHisto,x), len(xPtMaxBinsV1)-1, xPtMaxBinsV1, len(xPtMinBinsV1)-1, xPtMinBinsV1), "ptlmax", "ptlmin","weight")

            histo2D[ltype+36+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax >  1.5 && etalmin >  1.5")                       .Histo2D(("histo2d_{0}_{1}".format(ltype+36+iniHisto,x), "histo2d_{0}_{1}".format(ltype+36+iniHisto,x), len(xPtMaxBinsV1)-1, xPtMaxBinsV1, len(xPtMinBinsV1)-1, xPtMinBinsV1), "ptlmax", "ptlmin","weight")
            histo2D[ltype+42+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax >  1.5 && etalmin >  1.5").Filter("triggerl > 0").Histo2D(("histo2d_{0}_{1}".format(ltype+42+iniHisto,x), "histo2d_{0}_{1}".format(ltype+42+iniHisto,x), len(xPtMaxBinsV1)-1, xPtMaxBinsV1, len(xPtMinBinsV1)-1, xPtMinBinsV1), "ptlmax", "ptlmin","weight")

            histo2D[ltype+48+iniHisto][x] = dfcat[6*x+ltype]                       .Histo2D(("histo2d_{0}_{1}".format(ltype+48+iniHisto, x), "histo2d_{0}_{1}".format(ltype+48+iniHisto, x), len(xEtaBins)-1, xEtaBins, len(xPtBinsV1)-1, xPtBinsV1), "etalmin", "ptlmin","weight")
            histo2D[ltype+54+iniHisto][x] = dfcat[6*x+ltype].Filter("triggerl > 0").Histo2D(("histo2d_{0}_{1}".format(ltype+54+iniHisto, x), "histo2d_{0}_{1}".format(ltype+54+iniHisto, x), len(xEtaBins)-1, xEtaBins, len(xPtBinsV1)-1, xPtBinsV1), "etalmin", "ptlmin","weight")

            #dfcat[6*x+ltype] = dfcat[6*x+ltype].Filter("nTight == nFake","Tight lepton selection")

            iniHisto = 100
            histo2D[ltype+ 0+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax <= 1.5 && etalmin <= 1.5")                       .Histo2D(("histo2d_{0}_{1}".format(ltype+ 0+iniHisto,x), "histo2d_{0}_{1}".format(ltype+ 0+iniHisto,x), len(xPtMaxBinsV2)-1, xPtMaxBinsV2, len(xPtMinBinsV2)-1, xPtMinBinsV2), "ptlmax", "ptlmin","weight")
            histo2D[ltype+ 6+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax <= 1.5 && etalmin <= 1.5").Filter("triggerl > 0").Histo2D(("histo2d_{0}_{1}".format(ltype+ 6+iniHisto,x), "histo2d_{0}_{1}".format(ltype+ 6+iniHisto,x), len(xPtMaxBinsV2)-1, xPtMaxBinsV2, len(xPtMinBinsV2)-1, xPtMinBinsV2), "ptlmax", "ptlmin","weight")

            histo2D[ltype+12+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax >  1.5 && etalmin <= 1.5")                       .Histo2D(("histo2d_{0}_{1}".format(ltype+12+iniHisto,x), "histo2d_{0}_{1}".format(ltype+12+iniHisto,x), len(xPtMaxBinsV2)-1, xPtMaxBinsV2, len(xPtMinBinsV2)-1, xPtMinBinsV2), "ptlmax", "ptlmin","weight")
            histo2D[ltype+18+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax >  1.5 && etalmin <= 1.5").Filter("triggerl > 0").Histo2D(("histo2d_{0}_{1}".format(ltype+18+iniHisto,x), "histo2d_{0}_{1}".format(ltype+18+iniHisto,x), len(xPtMaxBinsV2)-1, xPtMaxBinsV2, len(xPtMinBinsV2)-1, xPtMinBinsV2), "ptlmax", "ptlmin","weight")

            histo2D[ltype+24+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax <= 1.5 && etalmin >  1.5")                       .Histo2D(("histo2d_{0}_{1}".format(ltype+24+iniHisto,x), "histo2d_{0}_{1}".format(ltype+24+iniHisto,x), len(xPtMaxBinsV2)-1, xPtMaxBinsV2, len(xPtMinBinsV2)-1, xPtMinBinsV2), "ptlmax", "ptlmin","weight")
            histo2D[ltype+30+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax <= 1.5 && etalmin >  1.5").Filter("triggerl > 0").Histo2D(("histo2d_{0}_{1}".format(ltype+30+iniHisto,x), "histo2d_{0}_{1}".format(ltype+30+iniHisto,x), len(xPtMaxBinsV2)-1, xPtMaxBinsV2, len(xPtMinBinsV2)-1, xPtMinBinsV2), "ptlmax", "ptlmin","weight")

            histo2D[ltype+36+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax >  1.5 && etalmin >  1.5")                       .Histo2D(("histo2d_{0}_{1}".format(ltype+36+iniHisto,x), "histo2d_{0}_{1}".format(ltype+36+iniHisto,x), len(xPtMaxBinsV2)-1, xPtMaxBinsV2, len(xPtMinBinsV2)-1, xPtMinBinsV2), "ptlmax", "ptlmin","weight")
            histo2D[ltype+42+iniHisto][x] = dfcat[6*x+ltype].Filter("etalmax >  1.5 && etalmin >  1.5").Filter("triggerl > 0").Histo2D(("histo2d_{0}_{1}".format(ltype+42+iniHisto,x), "histo2d_{0}_{1}".format(ltype+42+iniHisto,x), len(xPtMaxBinsV2)-1, xPtMaxBinsV2, len(xPtMinBinsV2)-1, xPtMinBinsV2), "ptlmax", "ptlmin","weight")

            histo2D[ltype+48+iniHisto][x] = dfcat[6*x+ltype]                       .Histo2D(("histo2d_{0}_{1}".format(ltype+48+iniHisto, x), "histo2d_{0}_{1}".format(ltype+48+iniHisto, x), len(xEtaBins)-1, xEtaBins, len(xPtBinsV2)-1, xPtBinsV2), "etalmin", "ptlmin","weight")
            histo2D[ltype+54+iniHisto][x] = dfcat[6*x+ltype].Filter("triggerl > 0").Histo2D(("histo2d_{0}_{1}".format(ltype+54+iniHisto, x), "histo2d_{0}_{1}".format(ltype+54+iniHisto, x), len(xEtaBins)-1, xEtaBins, len(xPtBinsV2)-1, xPtBinsV2), "etalmin", "ptlmin","weight")

    report = []
    for x in range(nCat):
        for ltype in range(6):
            report.append(dfcat[6*x+ltype].Report())
            if(x != theCat): continue
            print("---------------- SUMMARY 6*{0}+{1} = {2} -------------".format(x,ltype,6*x+ltype))
            report[6*x+ltype].Print()

    myfile = ROOT.TFile("fillhisto_metAnalysis_sample{0}_year{1}_job{2}.root".format(count,year,whichJob),'RECREATE')
    for i in range(nCat):
        for j in range(nHisto):
            if(histo[j][i] == 0): continue
            histo[j][i].Write()
        for j in range(nHisto):
            if(histo2D[j][i] == 0): continue
            #if(histo2D[j][i].GetSumOfWeights() > 0): print("({0},{1}): {2}".format(j,i,histo2D[j][i].GetSumOfWeights()))
            histo2D[j][i].Write()
    myfile.Close()

def readMCSample(sampleNOW, year, skimType, whichJob, group):

    files = getMClist(sampleNOW, skimType)
    if(len(files) == 0):
        time.sleep(10)
        files = getMClist(sampleNOW, skimType)
    if(len(files) == 0):
        time.sleep(10)
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

    analysis(df, sampleNOW, SwitchSample(sampleNOW, skimType)[2], weight, year, PDType, "false", whichJob)

def readDASample(sampleNOW, year, skimType, whichJob, group):

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

    analysis(df, sampleNOW, sampleNOW, weight, year, PDType, "true", whichJob)

if __name__ == "__main__":

    group = 5

    skimType = "met"
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

    try:
        if(process >= 0 and process < 1000):
            readMCSample(process,year,skimType,whichJob,group)
        elif(process >= 1000):
            readDASample(process,year,skimType,whichJob,group)
    except Exception as e:
        print("FAILED {0}".format(e))
