import ROOT
from ROOT import TFile, TH1D, TH2D
import os, sys, getopt, glob
from utilsCategory import plotCategory
ROOT.PyConfig.DisableRootLogon = True

if __name__ == "__main__":
    path = "fillhisto_zAnalysis"
    year = 2018
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

    paths_to_watch = path + "_sample*_year" + str(year) + "_job*.root"
    print("paths_to_watch: {0}".format(paths_to_watch))
    inputDataFolders = glob.glob(paths_to_watch)
    print("Total found files: {0}".format(len(inputDataFolders)))

    nCat, nHisto, nhistoNonPrompt, nhistoWS = plotCategory("kPlotCategories"), 1600, 50, 20

    myfile = [0 for x in range(len(inputDataFolders))]
    for nf in range(len(inputDataFolders)):
        myfile[nf] = TFile(inputDataFolders[nf])

    if(not os.path.exists(output)):
        os.makedirs(output)

    # 1DNonPrompt
    isHistoNonPromptUsed = False
    outputFileName = "{0}/{1}_{2}_{3}.root".format(output,os.path.basename(path),year,"nonprompt")
    print("Making 1D {0}".format(outputFileName))
    outputFile = TFile(outputFileName, "RECREATE")
    outputFile.cd()
    histo = [0 for x in range(nhistoNonPrompt)]
    for nc in range(nhistoNonPrompt):
        histo[nc] = myfile[0].Get("histoNonPrompt_{0}".format(nc))
        for nf in range(1,len(inputDataFolders)):
            if(histo[nc]):
                histo[nc].Add(myfile[nf].Get("histoNonPrompt_{0}".format(nc)))
        if(histo[nc]):
            isHistoNonPromptUsed = True
            histo[nc].SetNameTitle("histoNonPrompt_{0}".format(nc),"histoNonPrompt_{0}".format(nc))
            histo[nc].SetBinContent(histo[nc].GetNbinsX(),histo[nc].GetBinContent(histo[nc].GetNbinsX())+histo[nc].GetBinContent(histo[nc].GetNbinsX()+1))
            histo[nc].SetBinError  (histo[nc].GetNbinsX(),pow(pow(histo[nc].GetBinError(histo[nc].GetNbinsX()),2)+pow(histo[nc].GetBinError(histo[nc].GetNbinsX()+1),2),0.5))
            histo[nc].SetBinContent(histo[nc].GetNbinsX()+1,0.0)
            histo[nc].SetBinError  (histo[nc].GetNbinsX()+1,0.0)
            histo[nc].Write()
    outputFile.Close()
    if(isHistoNonPromptUsed == False):
        os.remove(outputFileName)

    # 1Dwrongsign
    isHistowrongsignUsed = False
    outputFileName = "{0}/{1}_{2}_{3}.root".format(output,os.path.basename(path),year,"wrongsign")
    print("Making 1D {0}".format(outputFileName))
    outputFile = TFile(outputFileName, "RECREATE")
    outputFile.cd()
    histo = [0 for x in range(nhistoWS)]
    for nc in range(nhistoWS):
        histo[nc] = myfile[0].Get("histoWS_{0}".format(nc))
        for nf in range(1,len(inputDataFolders)):
            if(histo[nc]):
                histo[nc].Add(myfile[nf].Get("histoWS_{0}".format(nc)))
        if(histo[nc]):
            isHistowrongsignUsed = True
            histo[nc].SetNameTitle("histoWS_{0}".format(nc),"histoWS_{0}".format(nc))
            histo[nc].SetBinContent(histo[nc].GetNbinsX(),histo[nc].GetBinContent(histo[nc].GetNbinsX())+histo[nc].GetBinContent(histo[nc].GetNbinsX()+1))
            histo[nc].SetBinError  (histo[nc].GetNbinsX(),pow(pow(histo[nc].GetBinError(histo[nc].GetNbinsX()),2)+pow(histo[nc].GetBinError(histo[nc].GetNbinsX()+1),2),0.5))
            histo[nc].SetBinContent(histo[nc].GetNbinsX()+1,0.0)
            histo[nc].SetBinError  (histo[nc].GetNbinsX()+1,0.0)
            histo[nc].Write()
    outputFile.Close()
    if(isHistowrongsignUsed == False):
        os.remove(outputFileName)

    for nh in range(nHisto):
        # 1D
        histo = [0 for x in range(nCat)]
        for nc in range(nCat):
            histo[nc] = myfile[0].Get("histo_{0}_{1}".format(nh,nc))
            for nf in range(1,len(inputDataFolders)):
                if(histo[nc]):
                    histo[nc].Add(myfile[nf].Get("histo_{0}_{1}".format(nh,nc)))

        if(histo[0]):
            outputFileName = "{0}/{1}_{2}_{3}.root".format(output,os.path.basename(path),year,nh)
            print("Making 1D {0}".format(outputFileName))
            outputFile = TFile(outputFileName, "RECREATE")
            outputFile.cd()
            for nc in range(nCat):
                histo[nc].SetNameTitle("histo{0}".format(nc),"histo{0}".format(nc))
                histo[nc].SetBinContent(histo[nc].GetNbinsX(),histo[nc].GetBinContent(histo[nc].GetNbinsX())+histo[nc].GetBinContent(histo[nc].GetNbinsX()+1))
                histo[nc].SetBinError  (histo[nc].GetNbinsX(),pow(pow(histo[nc].GetBinError(histo[nc].GetNbinsX()),2)+pow(histo[nc].GetBinError(histo[nc].GetNbinsX()+1),2),0.5))
                histo[nc].SetBinContent(histo[nc].GetNbinsX()+1,0.0)
                histo[nc].SetBinError  (histo[nc].GetNbinsX()+1,0.0)
                histo[nc].Write()
            outputFile.Close()

        # 1DMVA
        histoMVA = [0 for x in range(nCat)]
        for nc in range(nCat):
            histoMVA[nc] = myfile[0].Get("histoMVA_{0}_{1}".format(nh,nc))
            for nf in range(1,len(inputDataFolders)):
                if(histoMVA[nc]):
                    histoMVA[nc].Add(myfile[nf].Get("histoMVA_{0}_{1}".format(nh,nc)))

        if(histoMVA[0]):
            outputFileName = "{0}/{1}_{2}_{3}_mva.root".format(output,os.path.basename(path),year,nh)
            print("Making 1D {0}".format(outputFileName))
            outputFile = TFile(outputFileName, "RECREATE")
            outputFile.cd()
            for nc in range(nCat):
                histoMVA[nc].SetNameTitle("histoMVA{0}".format(nc),"histoMVA{0}".format(nc))
                histoMVA[nc].SetBinContent(histoMVA[nc].GetNbinsX(),histoMVA[nc].GetBinContent(histoMVA[nc].GetNbinsX())+histoMVA[nc].GetBinContent(histoMVA[nc].GetNbinsX()+1))
                histoMVA[nc].SetBinError  (histoMVA[nc].GetNbinsX(),pow(pow(histoMVA[nc].GetBinError(histoMVA[nc].GetNbinsX()),2)+pow(histoMVA[nc].GetBinError(histoMVA[nc].GetNbinsX()+1),2),0.5))
                histoMVA[nc].SetBinContent(histoMVA[nc].GetNbinsX()+1,0.0)
                histoMVA[nc].SetBinError  (histoMVA[nc].GetNbinsX()+1,0.0)
                histoMVA[nc].Write()
            outputFile.Close()

        # 2D
        histo2d = [0 for x in range(nCat)]
        for nc in range(nCat):
            histo2d[nc] = myfile[0].Get("histo2d_{0}_{1}".format(nh,nc))
            for nf in range(1,len(inputDataFolders)):
                if(histo2d[nc]):
                    histo2d[nc].Add(myfile[nf].Get("histo2d_{0}_{1}".format(nh,nc)))

        if(histo2d[0]):
            outputFileName = "{0}/{1}_{2}_{3}_2d.root".format(output,os.path.basename(path),year,nh)
            print("Making 2D {0}".format(outputFileName))
            outputFile = TFile(outputFileName, "RECREATE")
            outputFile.cd()
            for nc in range(nCat):
                histo2d[nc].SetNameTitle("histo2d{0}".format(nc),"histo2d{0}".format(nc))

                for i in range(histo2d[nc].GetNbinsX()):
                    histo2d[nc].SetBinContent(i+1,histo2d[nc].GetNbinsY(),histo2d[nc].GetBinContent(i+1,histo2d[nc].GetNbinsY())+histo2d[nc].GetBinContent(i+1,histo2d[nc].GetNbinsY()+1))
                    histo2d[nc].SetBinError  (i+1,histo2d[nc].GetNbinsY(),pow(pow(histo2d[nc].GetBinError(i+1,histo2d[nc].GetNbinsY()),2)+pow(histo2d[nc].GetBinError(i+1,histo2d[nc].GetNbinsY()+1),2),0.5))
                    histo2d[nc].SetBinContent(i+1,histo2d[nc].GetNbinsY()+1,0.0)
                    histo2d[nc].SetBinError  (i+1,histo2d[nc].GetNbinsY()+1,0.0)

                for i in range(histo2d[nc].GetNbinsY()):
                    histo2d[nc].SetBinContent(histo2d[nc].GetNbinsX(),i+1,histo2d[nc].GetBinContent(histo2d[nc].GetNbinsX(),i+1)+histo2d[nc].GetBinContent(histo2d[nc].GetNbinsX()+1,i+1))
                    histo2d[nc].SetBinError  (histo2d[nc].GetNbinsX(),i+1,pow(pow(histo2d[nc].GetBinError(histo2d[nc].GetNbinsX(),i+1),2)+pow(histo2d[nc].GetBinError(histo2d[nc].GetNbinsX()+1,i+1),2),0.5))
                    histo2d[nc].SetBinContent(histo2d[nc].GetNbinsX()+1,i+1,0.0)
                    histo2d[nc].SetBinError  (histo2d[nc].GetNbinsX()+1,i+1,0.0)

                histo2d[nc].Write()
            outputFile.Close()

    for nf in range(len(inputDataFolders)):
        print("Closing file... {0}".format(nf))
        myfile[nf].Close()

    print("DONE")
