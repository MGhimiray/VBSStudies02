import ROOT
from ROOT import TFile, TH1D, TH2D
import os, sys, getopt, glob
from utilsCategory import plotCategory

if __name__ == "__main__":
    path = "fillhisto_zAnalysis1001"
    year = 2022
    output = "anaZ"

    valid = ['path=', "year=", 'output=', 'help']
    usage  =  "Usage: ana.py --path=<{0}>\n".format(path)
    usage +=  "              --year=<{0}>\n".format(year)
    usage +=  "              --output=<{0}>".format(output)
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

    nCat = plotCategory("kPlotCategories")
    numberOfBits = 9

    # MB, ME, EB, EE
    fileLep = [TFile("{0}/{1}_{2}_muB.root".format(output,path,year)),
               TFile("{0}/{1}_{2}_muE.root".format(output,path,year)),
               TFile("{0}/{1}_{2}_elB.root".format(output,path,year)),
               TFile("{0}/{1}_{2}_elE.root".format(output,path,year))
              ]

    for thePlot in range(4):
        sumBits = [[0 for x in range(numberOfBits)] for y in range(2)]
        effBits = [[0 for x in range(numberOfBits)] for y in range(2)]
        uncBits = [[1 for x in range(numberOfBits)] for y in range(2)]
        histoLepDA = fileLep[thePlot].Get("histo{0}".format(plotCategory("kPlotData")))
        histoLepDY = fileLep[thePlot].Get("histo{0}".format(plotCategory("kPlotDY")))
        histoLepBG = fileLep[thePlot].Get("histo{0}".format(plotCategory("kPlotSignal3")))
        for nc in range(nCat):
            if(nc == plotCategory("kPlotData") or nc == plotCategory("kPlotDY") or nc == plotCategory("kPlotSignal3")): continue
            histoLepBG.Add(fileLep[thePlot].Get("histo{0}".format(nc)))

        print("Channel({0}) = ({1}-{2})/{3} = {4}".format(thePlot,histoLepDA.GetSumOfWeights(),histoLepBG.GetSumOfWeights(),histoLepDY.GetSumOfWeights(),
             (histoLepDA.GetSumOfWeights()-histoLepBG.GetSumOfWeights())/histoLepDY.GetSumOfWeights()))

        den = [histoLepDA.GetSumOfWeights()-histoLepBG.GetSumOfWeights(), histoLepDY.GetSumOfWeights()]
        denSum = [0, 0]
        for i in range(numberOfBits):
            denSum = [0, 0]
            for j in range(histoLepDA.GetNbinsX()):
                denSum[0] += (histoLepDA.GetBinContent(j+1)-histoLepBG.GetBinContent(j+1))
                denSum[1] +=  histoLepDY.GetBinContent(j+1)
                if((j & (1<<i))!=0):
                    sumBits[0][i] += (histoLepDA.GetBinContent(j+1)-histoLepBG.GetBinContent(j+1))
                    sumBits[1][i] +=  histoLepDY.GetBinContent(j+1)

            for k in range(2):
                if(abs(den[k]-denSum[k])>0.00001): print("Problem with total sum ({0}): {1} / {2}".format(k,den[k],denSum[k]))

                if(den[k] > 0 and sumBits[k][i] > 0 and sumBits[k][i] < den[k]):
                    effBits[k][i] = sumBits[k][i] / den[k]
                    uncBits[k][i] = pow(effBits[k][i]*(1-effBits[k][i])/den[k],0.5)

                elif(den[k] > 0 and sumBits[k][i] > 0):
                    effBits[k][i] = 1.0
                    uncBits[k][i] = pow(1.0/den[k],0.5)

                elif(den[k] > 0):
                    effBits[k][i] = 0.0
                    uncBits[k][i] = min(pow(1.0/den[k],0.5),0.999)

            print("({0},{1}): {2:10.1f}/{3:10.1f} = {4:0.3f} +/- {5:0.3f} / {6:10.1f}/{7:10.1f} = {8:0.3f} +/- {9:0.3f}".format(thePlot,i,
                sumBits[0][i],den[0],effBits[0][i],uncBits[0][i],sumBits[1][i],den[1],effBits[1][i],uncBits[1][i]))
