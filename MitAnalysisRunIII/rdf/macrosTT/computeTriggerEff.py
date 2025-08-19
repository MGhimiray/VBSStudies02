import ROOT
from ROOT import TFile, TH1D, TH2D, TCanvas
import os, sys, getopt, glob
from utilsCategory import plotCategory
from array import array

xPtMaxBins = array('d', [25,35,50,80,100])
xPtMinBins = array('d', [10,20,30,40,50,100])
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)

if __name__ == "__main__":
    path = "fillhisto_metAnalysis1001"
    year = 2022
    output = "anaZ"
    formatOutput = "pdf"

    doSavePtEtaHist = False

    valid = ['path=', "year=", 'output=', 'format=', 'help']
    usage  =  "Usage: ana.py --path=<{0}>\n".format(path)
    usage +=  "              --year=<{0}>\n".format(year)
    usage +=  "              --output=<{0}>\n".format(output)
    usage +=  "              --format=<{0}>".format(formatOutput)
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
        if opt == "--format":
            formatOutput = str(arg)

    nCat = plotCategory("kPlotCategories")

    numberOfLep = 6
    numberOfSel = 5
    nLepName = ["mm", "ee", "me", "em", "3l", "4l"]
    nSelName = ["bb", "eb", "be", "ee", "all"]
    histoTriggerV1SFEtaPt = [[0 for y in range(numberOfSel)] for x in range(numberOfLep)]
    histoTriggerV1DAEtaPt = [[0 for y in range(numberOfSel)] for x in range(numberOfLep)]
    histoTriggerV1MCEtaPt = [[0 for y in range(numberOfSel)] for x in range(numberOfLep)]
    histoTriggerV2SFEtaPt = [[0 for y in range(numberOfSel)] for x in range(numberOfLep)]
    histoTriggerV2DAEtaPt = [[0 for y in range(numberOfSel)] for x in range(numberOfLep)]
    histoTriggerV2MCEtaPt = [[0 for y in range(numberOfSel)] for x in range(numberOfLep)]
    histoLepDenDA = [[0 for y in range(numberOfSel)] for x in range(numberOfLep)]
    histoLepDenDY = [[0 for y in range(numberOfSel)] for x in range(numberOfLep)]
    histoLepNumDA = [[0 for y in range(numberOfSel)] for x in range(numberOfLep)]
    histoLepNumDY = [[0 for y in range(numberOfSel)] for x in range(numberOfLep)]

    histoTriggerV1SFPtMax = [[[0 for z in range(len(xPtMinBins)-1)] for y in range(numberOfSel)] for x in range(numberOfLep)]
    histoTriggerV1SFPtMin = [[[0 for z in range(len(xPtMaxBins)-1)] for y in range(numberOfSel)] for x in range(numberOfLep)]

    for nlep in range(numberOfLep):
        for nsel in range(numberOfSel):
            for npt in range(len(xPtMinBins)-1):
                histoTriggerV1SFPtMax[nlep][nsel][npt] = TH1D("histoTriggerV1SFPtMax_{0}_{1}_{2}".format(nLepName[nlep],nSelName[nsel],npt), "histoTriggerV1SFPtMax_{0}_{1}_{2}".format(nLepName[nlep],nSelName[nsel],npt), len(xPtMaxBins)-1, xPtMaxBins)
            for npt in range(len(xPtMaxBins)-1):
                histoTriggerV1SFPtMin[nlep][nsel][npt] = TH1D("histoTriggerV1SFPtMin_{0}_{1}_{2}".format(nLepName[nlep],nSelName[nsel],npt), "histoTriggerV1SFPtMin_{0}_{1}_{2}".format(nLepName[nlep],nSelName[nsel],npt), len(xPtMinBins)-1, xPtMinBins)

            fileTriggerDEN = TFile("{0}/{1}_{2}_{3}_2d.root".format(output,path,year,  nlep+12*nsel))
            fileTriggerDEN.cd()

            histoTriggerV1SFEtaPt[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotSignal3")))).Clone()
            histoTriggerV1DAEtaPt[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotSignal3")))).Clone()
            histoTriggerV1MCEtaPt[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotSignal3")))).Clone()

            histoLepDenDA[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotData")))).Clone()
            histoLepDenDY[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotDY")))).Clone()
            for nc in range(nCat):
                if(nc == plotCategory("kPlotData") or nc == plotCategory("kPlotDY") or nc == plotCategory("kPlotSignal3")): continue
                histoLepDenDY[nlep][nsel].Add(ROOT.gROOT.FindObject("histo2d{0}".format(nc)),1.0)

            histoTriggerV1SFEtaPt[nlep][nsel].SetDirectory(0)
            histoTriggerV1DAEtaPt[nlep][nsel].SetDirectory(0)
            histoTriggerV1MCEtaPt[nlep][nsel].SetDirectory(0)
            histoLepDenDA[nlep][nsel].SetDirectory(0)
            histoLepDenDY[nlep][nsel].SetDirectory(0)

            fileTriggerDEN.Close()

            fileTriggerNUM = TFile("{0}/{1}_{2}_{3}_2d.root".format(output,path,year,6+nlep+12*nsel))
            fileTriggerNUM.cd()

            histoLepNumDA[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotData")))).Clone()
            histoLepNumDY[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotDY")))).Clone()
            for nc in range(nCat):
                if(nc == plotCategory("kPlotData") or nc == plotCategory("kPlotDY")): continue
                histoLepNumDY[nlep][nsel].Add(ROOT.gROOT.FindObject("histo2d{0}".format(nc)),1.0)

            histoLepNumDA[nlep][nsel].SetDirectory(0)
            histoLepNumDY[nlep][nsel].SetDirectory(0)

            fileTriggerNUM.Close()

            if(histoLepDenDA[nlep][nsel].GetSumOfWeights() > 0 and histoLepDenDY[nlep][nsel].GetSumOfWeights() > 0):
                print("AverageLoose({0},{1}) = {2} / {3} = {4}".format(nLepName[nlep],nSelName[nsel],
                      histoLepNumDA[nlep][nsel].GetSumOfWeights()/histoLepDenDA[nlep][nsel].GetSumOfWeights(),
                      histoLepNumDY[nlep][nsel].GetSumOfWeights()/histoLepDenDY[nlep][nsel].GetSumOfWeights(),
                     (histoLepNumDA[nlep][nsel].GetSumOfWeights()/histoLepDenDA[nlep][nsel].GetSumOfWeights())/
                     (histoLepNumDY[nlep][nsel].GetSumOfWeights()/histoLepDenDY[nlep][nsel].GetSumOfWeights())
                     ))

            for i in range(histoLepDenDA[nlep][nsel].GetNbinsX()):
                for j in range(histoLepDenDA[nlep][nsel].GetNbinsY()):
                    den0 = histoLepDenDA[nlep][nsel].GetBinContent(i+1,j+1)
                    num0 = histoLepNumDA[nlep][nsel].GetBinContent(i+1,j+1)
                    eff0 = 0.0
                    unc0 = 0.0
                    if(den0 > 0 and num0 > 0 and num0 < den0):
                        eff0 = num0 / den0
                        unc0 = pow(eff0*(1-eff0)/den0,0.5)

                    elif(den0 > 0 and num0 > 0 and num0 == den0):
                        eff0 = num0 / den0
                        unc0 = pow(1.0/den0,0.5)

                    elif(den0 > 0):
                        eff0 = 0.0
                        unc0 = min(pow(1.0/den0,0.5),0.999)

                    den1 = histoLepDenDY[nlep][nsel].GetBinContent(i+1,j+1)
                    num1 = histoLepNumDY[nlep][nsel].GetBinContent(i+1,j+1)
                    eff1 = 0.0
                    unc1 = 0.0
                    if(den1 > 0 and num1 > 0 and num1 < den1):
                        eff1 = num1 / den1
                        unc1 = pow(eff1*(1-eff1)/den1,0.5)

                    elif(den0 > 1 and num1 > 0 and num1 == den1):
                        eff1 = num1 / den1
                        unc1 = pow(1.0/den1,0.5)

                    elif(den1 > 0):
                        eff1 = 0.0
                        unc1 = min(pow(1.0/den1,0.5),0.999)

                    sf = 0.
                    sfe = 0.
                    if(eff0 > 0 and eff1 > 0):
                        sf = eff0/eff1
                        sfe = sf*min(pow(pow(unc0/eff0,2)+pow(unc1/eff1,2),0.5)/3.0,0.05)
                    elif(histoLepDenDY[nlep][nsel].GetXaxis().GetBinCenter(i+1) >= histoLepDenDY[nlep][nsel].GetXaxis().GetBinCenter(j+1)):
                        sf = 1.00
                        sf = 0.05

                    histoTriggerV1SFEtaPt[nlep][nsel].SetBinContent(i+1,j+1,sf)
                    histoTriggerV1SFEtaPt[nlep][nsel].SetBinError  (i+1,j+1,sfe)
                    histoTriggerV1DAEtaPt[nlep][nsel].SetBinContent(i+1,j+1,eff0)
                    histoTriggerV1DAEtaPt[nlep][nsel].SetBinError  (i+1,j+1,unc0)
                    histoTriggerV1MCEtaPt[nlep][nsel].SetBinContent(i+1,j+1,eff1)
                    histoTriggerV1MCEtaPt[nlep][nsel].SetBinError  (i+1,j+1,unc1)

                    histoTriggerV1SFPtMax[nlep][nsel][j].SetBinContent(i+1,sf)
                    histoTriggerV1SFPtMax[nlep][nsel][j].SetBinError  (i+1,sfe)
                    histoTriggerV1SFPtMin[nlep][nsel][i].SetBinContent(j+1,sf)
                    histoTriggerV1SFPtMin[nlep][nsel][i].SetBinError  (j+1,sfe)

                    print("BinLoose({0:2d},{1:2d}): ( {2:.3f} +/- {3:.3f} ) / ( {4:.3f} - {5:.3f} ) = {6:.3f} / {7:.3f}".format(i+1,j+1,
                          eff0,unc0,eff1,unc1,sf,sfe))


    for nlep in range(numberOfLep):
        for nsel in range(numberOfSel):
            fileTriggerDEN = TFile("{0}/{1}_{2}_{3}_2d.root".format(output,path,year,  nlep+12*nsel+100))
            fileTriggerDEN.cd()

            histoTriggerV2SFEtaPt[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotSignal3")))).Clone()
            histoTriggerV2DAEtaPt[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotSignal3")))).Clone()
            histoTriggerV2MCEtaPt[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotSignal3")))).Clone()

            histoLepDenDA[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotData")))).Clone()
            histoLepDenDY[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotDY")))).Clone()
            for nc in range(nCat):
                if(nc == plotCategory("kPlotData") or nc == plotCategory("kPlotDY") or nc == plotCategory("kPlotSignal3")): continue
                histoLepDenDY[nlep][nsel].Add(ROOT.gROOT.FindObject("histo2d{0}".format(nc)),1.0)

            histoTriggerV2SFEtaPt[nlep][nsel].SetDirectory(0)
            histoTriggerV2DAEtaPt[nlep][nsel].SetDirectory(0)
            histoTriggerV2MCEtaPt[nlep][nsel].SetDirectory(0)
            histoLepDenDA[nlep][nsel].SetDirectory(0)
            histoLepDenDY[nlep][nsel].SetDirectory(0)

            fileTriggerDEN.Close()

            fileTriggerNUM = TFile("{0}/{1}_{2}_{3}_2d.root".format(output,path,year,6+nlep+12*nsel+100))
            fileTriggerNUM.cd()

            histoLepNumDA[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotData")))).Clone()
            histoLepNumDY[nlep][nsel] = (ROOT.gROOT.FindObject("histo2d{0}".format(plotCategory("kPlotDY")))).Clone()
            for nc in range(nCat):
                if(nc == plotCategory("kPlotData") or nc == plotCategory("kPlotDY")): continue
                histoLepNumDY[nlep][nsel].Add(ROOT.gROOT.FindObject("histo2d{0}".format(nc)),1.0)

            histoLepNumDA[nlep][nsel].SetDirectory(0)
            histoLepNumDY[nlep][nsel].SetDirectory(0)

            fileTriggerNUM.Close()

            if(histoLepDenDA[nlep][nsel].GetSumOfWeights() > 0 and histoLepDenDY[nlep][nsel].GetSumOfWeights() > 0):
                print("AverageTight({0},{1}) = {2} / {3} = {4}".format(nLepName[nlep],nSelName[nsel],
                      histoLepNumDA[nlep][nsel].GetSumOfWeights()/histoLepDenDA[nlep][nsel].GetSumOfWeights(),
                      histoLepNumDY[nlep][nsel].GetSumOfWeights()/histoLepDenDY[nlep][nsel].GetSumOfWeights(),
                     (histoLepNumDA[nlep][nsel].GetSumOfWeights()/histoLepDenDA[nlep][nsel].GetSumOfWeights())/
                     (histoLepNumDY[nlep][nsel].GetSumOfWeights()/histoLepDenDY[nlep][nsel].GetSumOfWeights())
                     ))

            for i in range(histoLepDenDA[nlep][nsel].GetNbinsX()):
                for j in range(histoLepDenDA[nlep][nsel].GetNbinsY()):
                    den0 = histoLepDenDA[nlep][nsel].GetBinContent(i+1,j+1)
                    num0 = histoLepNumDA[nlep][nsel].GetBinContent(i+1,j+1)
                    eff0 = 0.0
                    unc0 = 0.0
                    if(den0 > 0 and num0 > 0 and num0 < den0):
                        eff0 = num0 / den0
                        unc0 = pow(eff0*(1-eff0)/den0,0.5)

                    elif(den0 > 0 and num0 > 0 and num0 == den0):
                        eff0 = num0 / den0
                        unc0 = pow(1.0/den0,0.5)

                    elif(den0 > 0):
                        eff0 = 0.0
                        unc0 = min(pow(1.0/den0,0.5),0.999)

                    den1 = histoLepDenDY[nlep][nsel].GetBinContent(i+1,j+1)
                    num1 = histoLepNumDY[nlep][nsel].GetBinContent(i+1,j+1)
                    eff1 = 0.0
                    unc1 = 0.0
                    if(den1 > 0 and num1 > 0 and num1 < den1):
                        eff1 = num1 / den1
                        unc1 = pow(eff1*(1-eff1)/den1,0.5)

                    elif(den0 > 1 and num1 > 0 and num1 == den1):
                        eff1 = num1 / den1
                        unc1 = pow(1.0/den1,0.5)

                    elif(den1 > 0):
                        eff1 = 0.0
                        unc1 = min(pow(1.0/den1,0.5),0.999)

                    sf = 0.
                    sfe = 0.
                    if(eff0 > 0 and eff1 > 0):
                        sf = eff0/eff1
                        sfe = sf*min(pow(pow(unc0/eff0,2)+pow(unc1/eff1,2),0.5)/3.0,0.05)
                    elif(histoLepDenDY[nlep][nsel].GetXaxis().GetBinCenter(i+1) >= histoLepDenDY[nlep][nsel].GetYaxis().GetBinCenter(j+1)):
                        sf = 1.00
                        sf = 0.05

                    histoTriggerV2SFEtaPt[nlep][nsel].SetBinContent(i+1,j+1,sf)
                    histoTriggerV2SFEtaPt[nlep][nsel].SetBinError  (i+1,j+1,sfe)
                    histoTriggerV2DAEtaPt[nlep][nsel].SetBinContent(i+1,j+1,eff0)
                    histoTriggerV2DAEtaPt[nlep][nsel].SetBinError  (i+1,j+1,unc0)
                    histoTriggerV2MCEtaPt[nlep][nsel].SetBinContent(i+1,j+1,eff1)
                    histoTriggerV2MCEtaPt[nlep][nsel].SetBinError  (i+1,j+1,unc1)

                    print("BinTight({0:2d},{1:2d}): ( {2:.3f} +/- {3:.3f} ) / ( {4:.3f} - {5:.3f} ) = {6:.3f} / {7:.3f}".format(i+1,j+1,
                          eff0,unc0,eff1,unc1,sf,sfe))

    fileTriggerEffName = "histoTriggerSFEtaPt_{0}.root".format(year)
    outfileTriggerEff = TFile(fileTriggerEffName,"recreate")
    outfileTriggerEff.cd()
    for nlep in range(numberOfLep):
        for nsel in range(numberOfSel):
            if(doSavePtEtaHist == True):
              for npt in range(len(xPtMinBins)-1):
                  histoTriggerV1SFPtMax[nlep][nsel][npt].Write()
                  histoTriggerV1SFPtMax[nlep][nsel][npt].SetDirectory(0)
              for npt in range(len(xPtMaxBins)-1):
                  histoTriggerV1SFPtMin[nlep][nsel][npt].Write()
                  histoTriggerV1SFPtMin[nlep][nsel][npt].SetDirectory(0)
            histoTriggerV1SFEtaPt[nlep][nsel].SetNameTitle("histoTriggerV1SFEtaPt_{0}_{1}".format(nlep,nsel),"histoTriggerV1SFEtaPt_{0}_{1}".format(nlep,nsel))
            histoTriggerV1SFEtaPt[nlep][nsel].Write()
            histoTriggerV1DAEtaPt[nlep][nsel].SetNameTitle("histoTriggerV1DAEtaPt_{0}_{1}".format(nlep,nsel),"histoTriggerV1DAEtaPt_{0}_{1}".format(nlep,nsel))
            histoTriggerV1DAEtaPt[nlep][nsel].Write()
            histoTriggerV1MCEtaPt[nlep][nsel].SetNameTitle("histoTriggerV1MCEtaPt_{0}_{1}".format(nlep,nsel),"histoTriggerV1MCEtaPt_{0}_{1}".format(nlep,nsel))
            histoTriggerV1MCEtaPt[nlep][nsel].Write()
            histoTriggerV2SFEtaPt[nlep][nsel].SetNameTitle("histoTriggerV2SFEtaPt_{0}_{1}".format(nlep,nsel),"histoTriggerV2SFEtaPt_{0}_{1}".format(nlep,nsel))
            histoTriggerV2SFEtaPt[nlep][nsel].Write()
            histoTriggerV2DAEtaPt[nlep][nsel].SetNameTitle("histoTriggerV2DAEtaPt_{0}_{1}".format(nlep,nsel),"histoTriggerV2DAEtaPt_{0}_{1}".format(nlep,nsel))
            histoTriggerV2DAEtaPt[nlep][nsel].Write()
            histoTriggerV2MCEtaPt[nlep][nsel].SetNameTitle("histoTriggerV2MCEtaPt_{0}_{1}".format(nlep,nsel),"histoTriggerV2MCEtaPt_{0}_{1}".format(nlep,nsel))
            histoTriggerV2MCEtaPt[nlep][nsel].Write()
    outfileTriggerEff.Close()

    if(formatOutput != "none"):
        canvasPtMax = [[[0 for z in range(len(xPtMinBins)-1)] for y in range(numberOfSel)] for x in range(numberOfLep)]
        canvasPtMin = [[[0 for z in range(len(xPtMaxBins)-1)] for y in range(numberOfSel)] for x in range(numberOfLep)]

        for nlep in range(numberOfLep):
            if(nlep > 3): continue
            for nsel in range(numberOfSel):
                if(nsel > 3): continue
                for npt in range(len(xPtMinBins)-1):
                    canvasPtMax[nlep][nsel][npt] = TCanvas("canvasPtMax_{0}_{1}_{2}".format(nLepName[nlep],nSelName[nsel],npt), "canvasPtMax_{0}_{1}_{2}".format(nLepName[nlep],nSelName[nsel],npt), 10, 10, 500, 500)
                    canvasPtMax[nlep][nsel][npt].Divide(1,1)
                    canvasPtMax[nlep][nsel][npt].cd(1)
                    histoTriggerV1SFPtMax[nlep][nsel][npt].DrawCopy()
                    canvasPtMax[nlep][nsel][npt].Draw()
                    canvasPtMax[nlep][nsel][npt].SaveAs("histoTriggerV1SFPtMax_{0}_{1}_{2}_{3}.{4}".format(year,nLepName[nlep],nSelName[nsel],npt,formatOutput))

                for npt in range(len(xPtMaxBins)-1):
                   canvasPtMin[nlep][nsel][npt] = TCanvas("canvasPtMin_{0}_{1}_{2}".format(nLepName[nlep],nSelName[nsel],npt), "canvasPtMin_{0}_{1}_{2}".format(nLepName[nlep],nSelName[nsel],npt), 10, 10, 500, 500)
                   canvasPtMin[nlep][nsel][npt].Divide(1,1)
                   canvasPtMin[nlep][nsel][npt].cd(1)
                   histoTriggerV1SFPtMin[nlep][nsel][npt].DrawCopy()
                   canvasPtMin[nlep][nsel][npt].Draw()
                   canvasPtMin[nlep][nsel][npt].SaveAs("histoTriggerV1SFPtMin_{0}_{1}_{2}_{3}.{4}".format(year,nLepName[nlep],nSelName[nsel],npt,formatOutput))
