import ROOT
from array import array

inputFilesDA20220 = ["inputs/20220/da/Ele35_pt_eta_Run2022BCD_nominal_Ele_efficiency.txt",    "inputs/20220/da/IsoMu24_pt_eta_Run2022BCD_nominal_Mu_efficiency.txt",    "inputs/20220/da/Ele23_Ele12_leg1_pt_eta_Run2022BCD_nominal_Ele_efficiency.txt",    "inputs/20220/da/Ele23_Ele12_leg2_pt_eta_Run2022BCD_nominal_Ele_efficiency.txt",    "inputs/20220/da/Mu17_Mu8_leg1_pt_eta_Run2022BCD_nominal_Mu_efficiency.txt",    "inputs/20220/da/Mu17_Mu8_leg2_pt_eta_Run2022BCD_nominal_Mu_efficiency.txt",    "inputs/20220/da/Ele23_Ele12_leg1_pt_eta_Run2022BCD_nominal_Ele_efficiency.txt",    "inputs/20220/da/Mu12_Ele23_Muonleg_pt_eta_Run2022BCD_nominal_Mu_efficiency.txt",    "inputs/20220/da/Mu23_Ele12_Muonleg_pt_eta_Run2022BCD_nominal_Mu_efficiency.txt",    "inputs/20220/da/Ele23_Ele12_leg2_pt_eta_Run2022BCD_nominal_Ele_efficiency.txt"]
inputFilesMC20220 = ["inputs/20220/mc/Ele35_pt_eta_DY_Run2022BCD_nominal_Ele_efficiency.txt", "inputs/20220/mc/IsoMu24_pt_eta_DY_Run2022BCD_nominal_Mu_efficiency.txt", "inputs/20220/mc/Ele23_Ele12_leg1_pt_eta_DY_Run2022BCD_nominal_Ele_efficiency.txt", "inputs/20220/mc/Ele23_Ele12_leg2_pt_eta_DY_Run2022BCD_nominal_Ele_efficiency.txt", "inputs/20220/mc/Mu17_Mu8_leg1_pt_eta_DY_Run2022BCD_nominal_Mu_efficiency.txt", "inputs/20220/mc/Mu17_Mu8_leg2_pt_eta_DY_Run2022BCD_nominal_Mu_efficiency.txt", "inputs/20220/mc/Ele23_Ele12_leg1_pt_eta_DY_Run2022BCD_nominal_Ele_efficiency.txt", "inputs/20220/mc/Mu12_Ele23_Muonleg_pt_eta_DY_Run2022BCD_nominal_Mu_efficiency.txt", "inputs/20220/mc/Mu23_Ele12_Muonleg_pt_eta_DY_Run2022BCD_nominal_Mu_efficiency.txt", "inputs/20220/mc/Ele23_Ele12_leg2_pt_eta_DY_Run2022BCD_nominal_Ele_efficiency.txt"]
inputFilesDA20221 = ["inputs/20221/da/Ele35_pt_eta_nominal_Ele_efficiency.txt",               "inputs/20221/da/IsoMu24_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Ele23_Ele12_leg1_pt_eta_nominal_Ele_efficiency.txt",               "inputs/20221/da/Ele23_Ele12_leg2_pt_eta_nominal_Ele_efficiency.txt",               "inputs/20221/da/Mu17_Mu8_leg1_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Mu17_Mu8_leg2_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Ele23_Ele12_leg1_pt_eta_nominal_Ele_efficiency.txt",               "inputs/20221/da/Mu12_Ele23_Muonleg_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Mu23_Ele12_Muonleg_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Ele23_Ele12_leg2_pt_eta_nominal_Ele_efficiency.txt"]
inputFilesMC20221 = ["inputs/20221/mc/Ele35_pt_eta_nominalDY_Ele_efficiency.txt",             "inputs/20221/mc/IsoMu24_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Ele23_Ele12_leg1_pt_eta_nominalDY_Ele_efficiency.txt",             "inputs/20221/mc/Ele23_Ele12_leg2_pt_eta_nominalDY_Ele_efficiency.txt",             "inputs/20221/mc/Mu17_Mu8_leg1_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Mu17_Mu8_leg2_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Ele23_Ele12_leg1_pt_eta_nominalDY_Ele_efficiency.txt",             "inputs/20221/mc/Mu12_Ele23_Muonleg_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Mu23_Ele12_Muonleg_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Ele23_Ele12_leg2_pt_eta_nominalDY_Ele_efficiency.txt"]
inputFilesDA20230 = ["inputs/20230/da/Ele35_pt_eta_Run2022BCD_nominal_Ele_efficiency.txt",    "inputs/20230/da/IsoMu24_pt_eta_Run2022BCD_nominal_Mu_efficiency.txt",    "inputs/20230/da/Ele23_Ele12_leg1_pt_eta_Run2022BCD_nominal_Ele_efficiency.txt",    "inputs/20230/da/Ele23_Ele12_leg2_pt_eta_Run2022BCD_nominal_Ele_efficiency.txt",    "inputs/20230/da/Mu17_Mu8_leg1_pt_eta_Run2022BCD_nominal_Mu_efficiency.txt",    "inputs/20230/da/Mu17_Mu8_leg2_pt_eta_Run2022BCD_nominal_Mu_efficiency.txt",    "inputs/20230/da/Ele23_Ele12_leg1_pt_eta_Run2022BCD_nominal_Ele_efficiency.txt",    "inputs/20230/da/Mu12_Ele23_Muonleg_pt_eta_Run2022BCD_nominal_Mu_efficiency.txt",    "inputs/20230/da/Mu23_Ele12_Muonleg_pt_eta_Run2022BCD_nominal_Mu_efficiency.txt",    "inputs/20230/da/Ele23_Ele12_leg2_pt_eta_Run2022BCD_nominal_Ele_efficiency.txt"]
inputFilesMC20230 = ["inputs/20230/mc/Ele35_pt_eta_DY_Run2022BCD_nominal_Ele_efficiency.txt", "inputs/20230/mc/IsoMu24_pt_eta_DY_Run2022BCD_nominal_Mu_efficiency.txt", "inputs/20230/mc/Ele23_Ele12_leg1_pt_eta_DY_Run2022BCD_nominal_Ele_efficiency.txt", "inputs/20230/mc/Ele23_Ele12_leg2_pt_eta_DY_Run2022BCD_nominal_Ele_efficiency.txt", "inputs/20230/mc/Mu17_Mu8_leg1_pt_eta_DY_Run2022BCD_nominal_Mu_efficiency.txt", "inputs/20230/mc/Mu17_Mu8_leg2_pt_eta_DY_Run2022BCD_nominal_Mu_efficiency.txt", "inputs/20230/mc/Ele23_Ele12_leg1_pt_eta_DY_Run2022BCD_nominal_Ele_efficiency.txt", "inputs/20230/mc/Mu12_Ele23_Muonleg_pt_eta_DY_Run2022BCD_nominal_Mu_efficiency.txt", "inputs/20230/mc/Mu23_Ele12_Muonleg_pt_eta_DY_Run2022BCD_nominal_Mu_efficiency.txt", "inputs/20230/mc/Ele23_Ele12_leg2_pt_eta_DY_Run2022BCD_nominal_Ele_efficiency.txt"]
inputFilesDA20231 = ["inputs/20221/da/Ele35_pt_eta_nominal_Ele_efficiency.txt",               "inputs/20221/da/IsoMu24_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Ele23_Ele12_leg1_pt_eta_nominal_Ele_efficiency.txt",               "inputs/20221/da/Ele23_Ele12_leg2_pt_eta_nominal_Ele_efficiency.txt",               "inputs/20221/da/Mu17_Mu8_leg1_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Mu17_Mu8_leg2_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Ele23_Ele12_leg1_pt_eta_nominal_Ele_efficiency.txt",               "inputs/20221/da/Mu12_Ele23_Muonleg_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Mu23_Ele12_Muonleg_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Ele23_Ele12_leg2_pt_eta_nominal_Ele_efficiency.txt"]
inputFilesMC20231 = ["inputs/20221/mc/Ele35_pt_eta_nominalDY_Ele_efficiency.txt",             "inputs/20221/mc/IsoMu24_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Ele23_Ele12_leg1_pt_eta_nominalDY_Ele_efficiency.txt",             "inputs/20221/mc/Ele23_Ele12_leg2_pt_eta_nominalDY_Ele_efficiency.txt",             "inputs/20221/mc/Mu17_Mu8_leg1_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Mu17_Mu8_leg2_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Ele23_Ele12_leg1_pt_eta_nominalDY_Ele_efficiency.txt",             "inputs/20221/mc/Mu12_Ele23_Muonleg_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Mu23_Ele12_Muonleg_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Ele23_Ele12_leg2_pt_eta_nominalDY_Ele_efficiency.txt"]
inputFilesDA20240 = ["inputs/20221/da/Ele35_pt_eta_nominal_Ele_efficiency.txt",               "inputs/20221/da/IsoMu24_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Ele23_Ele12_leg1_pt_eta_nominal_Ele_efficiency.txt",               "inputs/20221/da/Ele23_Ele12_leg2_pt_eta_nominal_Ele_efficiency.txt",               "inputs/20221/da/Mu17_Mu8_leg1_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Mu17_Mu8_leg2_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Ele23_Ele12_leg1_pt_eta_nominal_Ele_efficiency.txt",               "inputs/20221/da/Mu12_Ele23_Muonleg_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Mu23_Ele12_Muonleg_pt_eta_nominal_efficiency.txt",                  "inputs/20221/da/Ele23_Ele12_leg2_pt_eta_nominal_Ele_efficiency.txt"]
inputFilesMC20240 = ["inputs/20221/mc/Ele35_pt_eta_nominalDY_Ele_efficiency.txt",             "inputs/20221/mc/IsoMu24_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Ele23_Ele12_leg1_pt_eta_nominalDY_Ele_efficiency.txt",             "inputs/20221/mc/Ele23_Ele12_leg2_pt_eta_nominalDY_Ele_efficiency.txt",             "inputs/20221/mc/Mu17_Mu8_leg1_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Mu17_Mu8_leg2_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Ele23_Ele12_leg1_pt_eta_nominalDY_Ele_efficiency.txt",             "inputs/20221/mc/Mu12_Ele23_Muonleg_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Mu23_Ele12_Muonleg_pt_eta_nominalDY_Mu_efficiency.txt",             "inputs/20221/mc/Ele23_Ele12_leg2_pt_eta_nominalDY_Ele_efficiency.txt"]

thePlot = ["sel", "smu", "del0", "del1", "dmu0", "dmu1", "emu0", "emu1", "mue0", "mue1"]
theID = ["20220_da", "20220_mc", "20221_da", "20221_mc", "20230_da", "20230_mc", "20231_da", "20231_mc", "20240_da", "20240_mc"]

histo = [[0 for y in range(len(theID))] for x in range(len(thePlot))]

for nInp in range(len(theID)):
    for nType in range(len(thePlot)):
        inputFile = ""
        if  (nInp == 0): inputFile = inputFilesDA20220[nType]
        elif(nInp == 1): inputFile = inputFilesMC20220[nType]
        elif(nInp == 2): inputFile = inputFilesDA20221[nType]
        elif(nInp == 3): inputFile = inputFilesMC20221[nType]
        elif(nInp == 4): inputFile = inputFilesDA20230[nType]
        elif(nInp == 5): inputFile = inputFilesMC20230[nType]
        elif(nInp == 6): inputFile = inputFilesDA20231[nType]
        elif(nInp == 7): inputFile = inputFilesMC20231[nType]
        elif(nInp == 8): inputFile = inputFilesDA20240[nType]
        elif(nInp == 9): inputFile = inputFilesMC20240[nType]
        print(inputFile)
        xMin = array('d', [])
        xMax = array('d', [])
        yMin = array('d', [])
        yMax = array('d', [])
        val  = array('d', [])
        inputFilesFile = open(inputFile, 'r')
        while True:
            line = inputFilesFile.readline().strip()
            if not line:
                break
            xMin.append(float(line.strip().split()[0]))
            xMax.append(float(line.strip().split()[1]))
            yMin.append(float(line.strip().split()[2]))
            yMax.append(float(line.strip().split()[3]))
            val .append(float(line.strip().split()[4]))
        xBins    = array('d', [])
        xMaxSort = array('d', [])
        yBins    = array('d', [])
        yMaxSort = array('d', [])
        [xBins   .append(x) for x in xMin if x not in xBins   ] 
        [xMaxSort.append(x) for x in xMax if x not in xMaxSort] 
        [yBins   .append(x) for x in yMin if x not in yBins   ] 
        [yMaxSort.append(x) for x in yMax if x not in yMaxSort] 
        xBins.append(xMaxSort[len(xMaxSort)-1])
        yBins.append(yMaxSort[len(yMaxSort)-1])
        print(len(xBins),len(xMaxSort),len(yBins),len(yMaxSort))
        print(xBins)
        print(yBins)
        histo[nType][nInp] = ROOT.TH2D("triggerEff_{0}_{1}".format(theID[nInp],thePlot[nType]), "triggerEff_{0}_{1}".format(theID[nInp],thePlot[nType]), len(xBins)-1, xBins, len(yBins)-1, yBins)
        for nsel in range(len(xMax)):
            x = (xMax[nsel]-xMin[nsel])/2.0 + xMin[nsel]
            y = (yMax[nsel]-yMin[nsel])/2.0 + yMin[nsel]
            xBin = histo[nType][nInp].GetXaxis().FindFixBin(x)
            yBin = histo[nType][nInp].GetYaxis().FindFixBin(y)
            histo[nType][nInp].SetBinContent(xBin, yBin, val[nsel])

fileTriggerEffName = "histoTriggerForSingleLegs.root"
outfileTriggerEff = ROOT.TFile(fileTriggerEffName,"recreate")
outfileTriggerEff.cd()
for nInp in range(len(theID)):
    for nType in range(len(thePlot)):
        histo[nType][nInp].Write()
outfileTriggerEff.Close()
