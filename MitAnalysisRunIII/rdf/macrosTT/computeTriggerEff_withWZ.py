import ROOT
from ROOT import TFile, TH1D, TH2D
import os, sys, getopt, glob
from utilsCategory import plotCategory

if __name__ == "__main__":
    pathWZ = "fillhisto_wzAnalysis1001"
    pathDY = "fillhisto_zAnalysis1001"
    year = 2022
    output = "anaZ"

    valid = ["year=", 'output=', 'help']
    usage  =  "Usage: ana.py --year=<{0}>\n".format(year)
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
        if opt == "--year":
            year = int(arg)
        if opt == "--output":
            output = str(arg)

    nCat = plotCategory("kPlotCategories")

    numberOfSel = 8
    histoTriggerSF = [0 for y in range(numberOfSel)]
    histoLepEFFDA  = [0 for y in range(numberOfSel)]
    histoLepEFFWZ  = [0 for y in range(numberOfSel)]
    histoLepDENDA  = [0 for y in range(numberOfSel)]
    histoLepDENWZ  = [0 for y in range(numberOfSel)]
    histoLepNUMDA  = [0 for y in range(numberOfSel)]
    histoLepNUMWZ  = [0 for y in range(numberOfSel)]

    for nsel in range(numberOfSel):
        pathDEN = "{0}/{1}_{2}_{3}.root".format(output,pathWZ,year,nsel+65)
        if(nsel >= 4 and nsel < 6):
            pathDEN = "{0}/{1}_{2}_{3}.root".format(output,pathDY,year,nsel+210-4)
        elif(nsel >= 6):
            pathDEN = "{0}/{1}_{2}_{3}.root".format(output,pathDY,year,nsel+210-6)

        print(pathDEN)
        fileTriggerDEN = TFile(pathDEN)
        fileTriggerDEN.cd()

        histoTriggerSF[nsel] = (ROOT.gROOT.FindObject("histo{0}".format(plotCategory("kPlotSignal1")))).Clone()
        histoLepEFFDA[nsel]  = (ROOT.gROOT.FindObject("histo{0}".format(plotCategory("kPlotSignal2")))).Clone()
        histoLepEFFWZ[nsel]  = (ROOT.gROOT.FindObject("histo{0}".format(plotCategory("kPlotSignal3")))).Clone()

        histoLepDENDA[nsel] = (ROOT.gROOT.FindObject("histo{0}".format(plotCategory("kPlotData")))).Clone()
        histoLepDENWZ[nsel] = (ROOT.gROOT.FindObject("histo{0}".format(plotCategory("kPlotWZ")))).Clone()
        for nc in range(nCat):
            if(nc == plotCategory("kPlotData") or nc == plotCategory("kPlotWZ") or 
               nc == plotCategory("kPlotSignal1") or nc == plotCategory("kPlotSignal2") or nc == plotCategory("kPlotSignal3")): continue
            histoLepDENWZ[nsel].Add(ROOT.gROOT.FindObject("histo{0}".format(nc)),1.0)

        histoTriggerSF[nsel].SetDirectory(0)
        histoLepEFFDA[nsel].SetDirectory(0)
        histoLepEFFWZ[nsel].SetDirectory(0)
        histoLepDENDA[nsel].SetDirectory(0)
        histoLepDENWZ[nsel].SetDirectory(0)

        fileTriggerDEN.Close()

        pathNUM = "{0}/{1}_{2}_{3}.root".format(output,pathWZ,year,nsel+65+4)
        if(nsel >= 4):
            pathNUM = "{0}/{1}_{2}_{3}.root".format(output,pathDY,year,nsel+212-4)

        print(pathNUM)
        fileTriggerNUM = TFile(pathNUM)
        fileTriggerNUM.cd()

        histoLepNUMDA[nsel] = (ROOT.gROOT.FindObject("histo{0}".format(plotCategory("kPlotData")))).Clone()
        histoLepNUMWZ[nsel] = (ROOT.gROOT.FindObject("histo{0}".format(plotCategory("kPlotWZ")))).Clone()
        for nc in range(nCat):
            if(nc == plotCategory("kPlotData") or nc == plotCategory("kPlotWZ")): continue
            histoLepNUMWZ[nsel].Add(ROOT.gROOT.FindObject("histo{0}".format(nc)),1.0)

        histoLepNUMDA[nsel].SetDirectory(0)
        histoLepNUMWZ[nsel].SetDirectory(0)

        fileTriggerNUM.Close()

        print("({0}) = {1}/{2} = {3}".format(nsel,
              histoLepNUMDA[nsel].GetSumOfWeights()/histoLepDENDA[nsel].GetSumOfWeights(),
              histoLepNUMWZ[nsel].GetSumOfWeights()/histoLepDENWZ[nsel].GetSumOfWeights(),
             (histoLepNUMDA[nsel].GetSumOfWeights()/histoLepDENDA[nsel].GetSumOfWeights())/
             (histoLepNUMWZ[nsel].GetSumOfWeights()/histoLepDENWZ[nsel].GetSumOfWeights())
             ))

        for i in range(histoLepDENDA[nsel].GetNbinsX()):
            den0 = histoLepDENDA[nsel].GetBinContent(i+1)
            num0 = histoLepNUMDA[nsel].GetBinContent(i+1)
            eff0 = 1.0
            unc0 = 0.0
            if(den0 > 0 and num0 > 0 and num0 <= den0):
                eff0 = num0 / den0
                unc0 = pow(eff0*(1-eff0)/den0,0.5)

            elif(den0 > 0):
                eff0 = 0.0
                unc0 = min(pow(1.0/den0,0.5),0.999)

            den1 = histoLepDENWZ[nsel].GetBinContent(i+1)
            num1 = histoLepNUMWZ[nsel].GetBinContent(i+1)
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

            histoTriggerSF[nsel].SetBinContent(i+1,sf)
            histoTriggerSF[nsel].SetBinError  (i+1,sfe)
            histoLepEFFDA[nsel].SetBinContent(i+1,eff0)
            histoLepEFFDA[nsel].SetBinError  (i+1,unc0)
            histoLepEFFWZ[nsel].SetBinContent(i+1,eff1)
            histoLepEFFWZ[nsel].SetBinError  (i+1,unc1)

            print("({0:2d}): ({1:.3f} +/- {2:.3f}) / ({3:.3f} - {4:.3f}) = {5:.3f} +/- {6:.3f}".format(i+1,
                      eff0,unc0,eff1,unc1,sf,sfe))

    fileTriggerEffName = "histoTriggerSFWZ_{0}.root".format(year)
    outfileTriggerEff = TFile(fileTriggerEffName,"recreate")
    outfileTriggerEff.cd()
    for nsel in range(numberOfSel):
        histoTriggerSF[nsel].SetNameTitle("histoTriggerSFWZ_{0}".format(nsel),"histoTriggerSFWZ_{0}".format(nsel))
        histoLepEFFDA[nsel].SetNameTitle("histoLepEFFDA_{0}".format(nsel),"histoLepEFFDA_{0}".format(nsel))
        histoLepEFFWZ[nsel].SetNameTitle("histoLepEFFWZ_{0}".format(nsel),"histoLepEFFWZ_{0}".format(nsel))
        histoTriggerSF[nsel].Write()
        histoLepEFFDA[nsel].Write()
        histoLepEFFWZ[nsel].Write()
    outfileTriggerEff.Close()
