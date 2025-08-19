import ROOT
from ROOT import TFile, TH1D, TH2D
import os, sys, getopt, glob
from utilsCategory import plotCategory

if __name__ == "__main__":
    path = "fillhisto_sswwAnalysis1001"
    year = 2022
    output = "anaZ"
    showUnc = 0

    valid = ['path=', "year=", 'output=', "unc=", 'help']
    usage  =  "Usage: ana.py --path=<{0}>\n".format(path)
    usage +=  "              --year=<{0}>\n".format(year)
    usage +=  "              --output=<{0}>".format(output)
    usage +=  "              --unc=<{0}>".format(showUnc)
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
        if opt == "--path":
            path = str(arg)
        if opt == "--year":
            year = int(arg)
        if opt == "--output":
            output = str(arg)
        if opt == "--unc":
            showUnc = int(arg)

    histo = []
    signalDict0 = []
    signalDict1 = []
    muSignal = []
    if('wwAna' in path):
        histo.append(73)
        signalDict0.append(plotCategory("kPlotNonPrompt"))
        signalDict1.append(plotCategory("kPlotNonPrompt"))
        histo.append(75)
        signalDict0.append(plotCategory("kPlotDY"))
        signalDict1.append(plotCategory("kPlotDY"))
        histo.append(76)
        signalDict0.append(plotCategory("kPlotTT"))
        signalDict1.append(plotCategory("kPlotTW"))
        # WW SR must be the last one
        histo.append(74)
        signalDict0.append(plotCategory("kPlotqqWW"))
        signalDict1.append(plotCategory("kPlotggWW"))

    nCat = plotCategory("kPlotCategories")
    for nh in range(len(histo)):
        print("**********HISTO: {0} **********".format(histo[nh]))
        histoSel = [0 for y in range(nCat)]
        histoPtwwSel = [0, 0, 0]
        inputFile = TFile("{0}/{1}_{2}_{3}.root".format(output,os.path.basename(path),year,histo[nh]),"w")
        theYields  = [0,0,0]
        theYieldsE = [0,0,0]
        theYieldsProcess     = [0 for y in range(nCat)]
        theYieldsProcessUnc  = [0 for y in range(nCat)]
        for i in range(nCat):
            histoSel[i] = (inputFile.Get("histo{0}".format(i))).Clone()
            if(i == plotCategory("kPlotData")):
                histoPtwwSel[0]  = (inputFile.Get("histo{0}".format(i))).Clone()
                histoPtwwSel[1]  = (inputFile.Get("histo{0}".format(i))).Clone()
                histoPtwwSel[2]  = (inputFile.Get("histo{0}".format(i))).Clone()
                histoPtwwSel[0].Scale(0.0)
                histoPtwwSel[1].Scale(0.0)
                histoPtwwSel[2].Scale(0.0)
        for nb in range(1,histoSel[0].GetNbinsX()+1):
            streamYield = ""
            mcYield = 0
            processesWithEvents = []
            for i in range(nCat):
                if(histoSel[i].GetSumOfWeights() > 0 or i == plotCategory("kPlotData")):
                    if(showUnc == 0):
                        streamYield += " {0:7.1f}".format(histoSel[i].GetBinContent(nb))
                    else:
                        streamYield += " {0:7.1f} +/- {1:5.1f}".format(histoSel[i].GetBinContent(nb),histoSel[i].GetBinError(nb))
                    processesWithEvents.append(i)
                theYieldsProcess[i]     += histoSel[i].GetBinContent(nb)
                theYieldsProcessUnc[i]  += histoSel[i].GetBinError(nb)
                if(i == plotCategory("kPlotData")):
                    theYields[0]  += histoSel[i].GetBinContent(nb)
                    theYieldsE[0] += histoSel[i].GetBinError(nb)*histoSel[i].GetBinError(nb)
                elif(i == signalDict0[nh] or i == signalDict1[nh]):
                    theYields[1]  += histoSel[i].GetBinContent(nb)
                    theYieldsE[1] += histoSel[i].GetBinError(nb)*histoSel[i].GetBinError(nb)
                    mcYield += histoSel[i].GetBinContent(nb)
                else:
                    theYields[2]  += histoSel[i].GetBinContent(nb)
                    theYieldsE[2] += histoSel[i].GetBinError(nb)*histoSel[i].GetBinError(nb)
                    mcYield += histoSel[i].GetBinContent(nb)
            streamYield = "({0:2d}) {1:7.1f}".format(nb,mcYield) + streamYield
            if(nb == 1):
                streamProcess = "         "
                for pr in range(len(processesWithEvents)):
                    streamProcess += " {0:7d}".format(processesWithEvents[pr])
                print(streamProcess)
            #print(streamYield)

        streamYield = ""
        for i in range(nCat):
            if(histoSel[i].GetSumOfWeights() > 0 or i == plotCategory("kPlotData")):
                if(showUnc == 0):
                    streamYield += " {0:7.1f}".format(theYieldsProcess[i])
                else:
                    streamYield += " {0:7.1f} +/- {1:5.1f}".format(theYieldsProcess[i],theYieldsProcessUnc[i])
        for i in range(3):
            theYieldsE[i] = pow(theYieldsE[i],0.5)
        streamYield = "(xx) {0:7.1f}".format(theYields[1]+theYields[2]) + streamYield
        print(streamYield)
        print("DA: {0:7.1f} +/- {1:4.1f} / SIG: {2:7.1f} +/- {3:4.1f} / BG: {4:7.1f} +/- {5:4.1f}".format(theYields[0],theYieldsE[0],theYields[1],theYieldsE[1],theYields[2],theYieldsE[2]))
        SB = theYields[1]/theYields[2]
        DataVsPred = theYields[0]/(theYields[1]+theYields[2])
        DataVsPredE = DataVsPred*pow(pow(theYieldsE[0]/theYields[0],2)+pow(theYieldsE[1]/(theYields[1]+theYields[2]),2)+pow(theYieldsE[2]/(theYields[1]+theYields[2]),2),0.5)
        muSignal.append((theYields[0]-theYields[2])/theYields[1])
        print("SB: {0:.2f} / DataVsPred: {1:.2f} +/- {2:.2f} / muSignal = {3:.2f}".format(SB,DataVsPred,DataVsPredE,muSignal[nh-1]))

        if(nh == len(histo)-1):
            for i in range(nCat):
                if(i == plotCategory("kPlotData")):
                    histoPtwwSel[0].Add(histoSel[i])
                elif(i == plotCategory("kPlotqqWW") or i == plotCategory("kPlotggWW")):
                    histoPtwwSel[1].Add(histoSel[i])
                elif(i == plotCategory("kPlotNonPrompt")):
                    histoPtwwSel[2].Add(histoSel[i],muSignal[0])
                elif(i == plotCategory("kPlotDY")):
                    histoPtwwSel[2].Add(histoSel[i],muSignal[1])
                elif(i == plotCategory("kPlotTT") or i == plotCategory("kPlotTW")):
                    histoPtwwSel[2].Add(histoSel[i],muSignal[2])
                else:
                    histoPtwwSel[2].Add(histoSel[i])
            muWW = (histoPtwwSel[0].GetSumOfWeights()-histoPtwwSel[2].GetSumOfWeights())/histoPtwwSel[1].GetSumOfWeights()
            print("DA: {0:7.1f} / SIG: {1:7.1f} / BG: {2:7.1f} -> muWW = {3:5.3f}".format(histoPtwwSel[0].GetSumOfWeights(),histoPtwwSel[1].GetSumOfWeights(),histoPtwwSel[2].GetSumOfWeights(),muWW))
            histoPtwwSel[0].Add(histoPtwwSel[2],-1.0)
            histoPtwwSel[1].Scale(muWW)
            histoPtwwSel[0].Divide(histoPtwwSel[1])
            histoPtwwSel[0].SetDirectory(0)
            outFile = TFile("ptwwRatio.root","recreate")
            outFile.cd()
            histoPtwwSel[0].SetNameTitle("ptwwRatio","ptwwRatio")
            histoPtwwSel[0].Write()
            outFile.Close()
