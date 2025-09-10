import ROOT
from ROOT import TFile, TH1D, TH2D
import os, sys, getopt, glob
from utilsCategory import plotCategory

if __name__ == "__main__":
    path = "fillhisto_puAnalysis_sample000"
    year = 2022
    output = "anaZ"
    debug = 1
    maxTolerance = 0.03

    valid = ['path=', "year=", 'output=', 'help']
    usage  =  "Usage: ana.py --path=<{0}>\n".format(path)
    usage +=  "              --year=<{0}>\n".format(year)
    usage +=  "              --output=<{0}>\n".format(output)
    usage +=  "              --debug=<{0}>".format(debug)
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
        if opt == "--debug":
            debug = int(arg)

    nCat = plotCategory("kPlotCategories")

    fileBTV = TFile("{0}/{1}_year{2}.root".format(output,path,year))
    print("{0}/{1}_year{2}.root".format(output,path,year))

    numberOfSel = 3
    histoBtagDenSelEtaPt = [0 for y in range(numberOfSel)]
    numberOfSel = 9
    histoBtagNumSelEtaPt = [0 for y in range(numberOfSel)]
    numberOfSel = 9
    histoBtagEffSelEtaPt = [0 for y in range(numberOfSel)]

    fileLepEffName = "histoBtagEffSelEtaPt_{0}.root".format(year)
    outFileLepEff = TFile(fileLepEffName,"recreate")
    outFileLepEff.cd()

    histoBtagDenSelEtaPt[0] = (fileBTV.Get("histo2d_0_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagDenSelEtaPt[1] = (fileBTV.Get("histo2d_1_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagDenSelEtaPt[2] = (fileBTV.Get("histo2d_2_{0}".format(plotCategory("kPlotData")))).Clone()

    histoBtagNumSelEtaPt[0] = (fileBTV.Get("histo2d_3_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagNumSelEtaPt[1] = (fileBTV.Get("histo2d_4_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagNumSelEtaPt[2] = (fileBTV.Get("histo2d_5_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagNumSelEtaPt[3] = (fileBTV.Get("histo2d_6_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagNumSelEtaPt[4] = (fileBTV.Get("histo2d_7_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagNumSelEtaPt[5] = (fileBTV.Get("histo2d_8_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagNumSelEtaPt[6] = (fileBTV.Get("histo2d_9_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagNumSelEtaPt[7] = (fileBTV.Get("histo2d_10_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagNumSelEtaPt[8] = (fileBTV.Get("histo2d_11_{0}".format(plotCategory("kPlotData")))).Clone()

    histoBtagEffSelEtaPt[0] = (fileBTV.Get("histo2d_3_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagEffSelEtaPt[1] = (fileBTV.Get("histo2d_4_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagEffSelEtaPt[2] = (fileBTV.Get("histo2d_5_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagEffSelEtaPt[3] = (fileBTV.Get("histo2d_6_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagEffSelEtaPt[4] = (fileBTV.Get("histo2d_7_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagEffSelEtaPt[5] = (fileBTV.Get("histo2d_8_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagEffSelEtaPt[6] = (fileBTV.Get("histo2d_9_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagEffSelEtaPt[7] = (fileBTV.Get("histo2d_10_{0}".format(plotCategory("kPlotData")))).Clone()
    histoBtagEffSelEtaPt[8] = (fileBTV.Get("histo2d_11_{0}".format(plotCategory("kPlotData")))).Clone()

    for theNumSel in range(0,numberOfSel):
        theDenSel = theNumSel%3
        if(debug >= 1):
            print("******** {0} ({1}) / {2} ({3})".format(theNumSel,histoBtagNumSelEtaPt[theNumSel].GetSumOfWeights(),theDenSel,histoBtagDenSelEtaPt[theDenSel].GetSumOfWeights()))
        for i in range(histoBtagDenSelEtaPt[theDenSel].GetNbinsX()):
            for j in range(histoBtagDenSelEtaPt[theDenSel].GetNbinsY()):
                den0 = histoBtagDenSelEtaPt[theDenSel].GetBinContent(i+1,j+1)
                num0 = histoBtagNumSelEtaPt[theNumSel].GetBinContent(i+1,j+1)
                eff0 = 1.0
                unc0 = 0.0
                if(den0 > 0 and num0 > 0 and num0 <= den0):
                    eff0 = num0 / den0
                    unc0 = pow(eff0*(1-eff0)/den0,0.5)

                elif(den0 > 0):
                    eff0 = 0.0
                    unc0 = min(pow(1.0/den0,0.5),0.999)

                histoBtagEffSelEtaPt[theNumSel].SetBinContent(i+1,j+1,eff0)
                histoBtagEffSelEtaPt[theNumSel].SetBinError  (i+1,j+1,unc0)

                if(debug >= 2):
                    print("({0:2d},{1:2d}): ({2:.3f} +/- {3:.3f})".format(i+1,j+1,eff0,unc0))
                if(unc0 > maxTolerance):
                    print("LARGE UNC ({0:2d},{1:2d}): ({2:.3f} +/- {3:.3f})".format(i+1,j+1,eff0,unc0))

        histoBtagEffSelEtaPt[theNumSel].SetNameTitle("histoBtagEffSelEtaPt_{0}".format(theNumSel),"histoBtagEffSelEtaPt_{0}".format(theNumSel))
        histoBtagEffSelEtaPt[theNumSel].Write()
