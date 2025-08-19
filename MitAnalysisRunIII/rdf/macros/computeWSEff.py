import ROOT
from ROOT import TFile, TH1D, TH2D
import os, sys, getopt, glob
from utilsCategory import plotCategory

if __name__ == "__main__":
    path = "fillhisto_zAnalysis1001"
    year = 2022
    output = "anaZ"
    numberOfBins = 15

    valid = ['path=', "year=", 'output=', 'bins=', 'help']
    usage  =  "Usage: ana.py --path=<{0}>\n".format(path)
    usage +=  "              --year=<{0}>\n".format(year)
    usage +=  "              --output=<{0}\n>".format(output)
    usage +=  "              --bins=<{0}>".format(numberOfBins)
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
        if opt == "--bins":
            numberOfBins = int(arg)

    nCat = plotCategory("kPlotCategories")

    histoWSSFEta = TH1D("histoWSSFEta","histoWSSFEta",numberOfBins,-0.5,numberOfBins-0.5)
    histoLepOSDA = [0 for x in range(numberOfBins)]
    histoLepOSDY = [0 for x in range(numberOfBins)]
    histoLepSSDA = [0 for x in range(numberOfBins)]
    histoLepSSDY = [0 for x in range(numberOfBins)]

    for nbin in range(numberOfBins):
        fileTriggerDEN = TFile("{0}/{1}_{2}_ele_os_{3}.root".format(output,path,year,nbin))
        fileTriggerDEN.cd()

        histoLepOSDA[nbin] = (ROOT.gROOT.FindObject("histo{0}".format(plotCategory("kPlotData")))).Clone()
        histoLepOSDY[nbin] = (ROOT.gROOT.FindObject("histo{0}".format(plotCategory("kPlotDY")))).Clone()
        for nc in range(nCat):
            if(nc == plotCategory("kPlotData") or nc == plotCategory("kPlotDY") or nc == plotCategory("kPlotSignal3")): continue
            histoLepOSDY[nbin].Add(ROOT.gROOT.FindObject("histo{0}".format(nc)),1.0)

        histoLepOSDA[nbin].SetDirectory(0)
        histoLepOSDY[nbin].SetDirectory(0)

        fileTriggerDEN.Close()

        fileTriggerNUM = TFile("{0}/{1}_{2}_ele_ss_{3}.root".format(output,path,year,nbin))
        fileTriggerNUM.cd()

        histoLepSSDA[nbin] = (ROOT.gROOT.FindObject("histo{0}".format(plotCategory("kPlotData")))).Clone()
        histoLepSSDY[nbin] = (ROOT.gROOT.FindObject("histo{0}".format(plotCategory("kPlotDY")))).Clone()
        for nc in range(nCat):
            if(nc == plotCategory("kPlotData") or nc == plotCategory("kPlotDY")): continue
            histoLepSSDY[nbin].Add(ROOT.gROOT.FindObject("histo{0}".format(nc)),1.0)

        histoLepSSDA[nbin].SetDirectory(0)
        histoLepSSDY[nbin].SetDirectory(0)

        fileTriggerNUM.Close()

        den0 = histoLepOSDA[nbin].GetSumOfWeights()
        num0 = histoLepSSDA[nbin].GetSumOfWeights()
        eff0 = 1.0
        unc0 = 0.0
        if(den0 > 0 and num0 > 0 and num0 <= den0):
            eff0 = num0 / den0
            unc0 = pow(eff0*(1-eff0)/den0,0.5)
 
        elif(den0 > 0):
            eff0 = 0.0
            unc0 = min(pow(1.0/den0,0.5),0.999)

        den1 = histoLepOSDY[nbin].GetSumOfWeights()
        num1 = histoLepSSDY[nbin].GetSumOfWeights()
        eff1 = 1.0
        unc1 = 0.0
        if(den1 > 0 and num1 > 0 and num1 <= den1):
            eff1 = num1 / den1
            unc1 = pow(eff1*(1-eff1)/den1,0.5)

        elif(den1 > 0):
            eff1 = 0.0
            unc1 = min(pow(1.0/den1,0.5),0.999)

        sf = 1.
        sfe = 0.
        if(eff0 > 0 and eff1 > 0):
            sf = eff0/eff1
            sfe = sf*pow(pow(unc0/eff0,2)+pow(unc1/eff1,2),0.5)

        print("zA[{0:2d}]={1:.6f};errorzA[{0:2d}]={2:.6f};zB[{0:2d}]={3:.6f};errorzB[{0:2d}]={4:.6f}; // {5:.3f} / {6:.3f}".format(nbin,eff0,unc0,eff1,unc1,sf,sfe))
        
        histoWSSFEta.SetBinContent(nbin, sf)
        histoWSSFEta.SetBinError(nbin, sfe)

    #fileWSEffName = "histoWSSFEta_{0}.root".format(year)
    #outfileWSEff = TFile(fileWSEffName,"recreate")
    #outfileWSEff.cd()
    #histoWSSFEta.Write()
    #outfileWSEff.Close()
	
