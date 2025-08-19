import ROOT
import correctionlib
import os, sys, getopt, glob
from array import array

xPtBins = array('d', [10.0,15.0,20.0,25.0,30.0,35.0,40.0,45.0,50.0,55.0,60.0,65.0,70.0,75.0,80.0,85.0,90.0,95.0,100.0])
xEtaBins = array('d', [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4])
xMuPtBins = array('d', [10.0,15.0,20.0,25.0,30.0,40.0,50.0,60.0,120.0,200.0])
xMuEtaBins = array('d', [0.0,0.9,1.2,2.1,2.5])
xElPtBins = array('d', [10.0,20.0,35.0,50.0,100.0,200.0])
xElEtaBins = array('d', [0.0,0.8,1.444,1.566,2.0,2.5])
yearVal = [20220, 20221, 20230, 20231]

def sf_electron(year, evaluator_el, elTag, sfDef, selVal, etaVal, ptVal, phiVal):
    etaVal = etaVal+0.001
    ptVal  =  ptVal+0.001
    phiVal = phiVal+0.001
    sf = 0.0

    if(year // 10 <= 2022):
        sf= evaluator_el(elTag,sfDef,selVal,etaVal,ptVal)
    else:
        sf= evaluator_el(elTag,sfDef,selVal,etaVal,ptVal,phiVal)

    return sf

if __name__ == "__main__":
    input = "data/"
    binOption = 0
    debug = 0

    valid = ['input=', "binOption=", "debug=", 'help']
    usage  =  "Usage: ana.py --input=<{0}>\n".format(input)
    usage +=  "              --binOption=<{0}>\n".format(binOption)
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
        if opt == "--input":
            input = str(arg)
        if opt == "--debug":
            debug = int(arg)
        if opt == "--binOption":
            binOption = int(arg)

    histo_mu = [0 for x in range(len(yearVal))]
    histo_el = [0 for x in range(len(yearVal))]
    for ny in range(len(yearVal)):
        lepSFPath = "{0}histoLepSFEtaPt_{1}.root".format(input,yearVal[ny])
        fLepSFFile = ROOT.TFile(lepSFPath)
        histoLepSFEtaPt_mu = fLepSFFile.Get("histoLepSFEtaPt_0_{0}".format(0)) # Medium
        histoLepSFEtaPt_el = fLepSFFile.Get("histoLepSFEtaPt_1_{0}".format(0)) # Medium
        histoLepSFEtaPt_mu.SetDirectory(0)
        histoLepSFEtaPt_el.SetDirectory(0)
        fLepSFFile.Close()

        muIDTag = "NUM_MediumID_DEN_TrackerMuons"
        muISOTag = "NUM_TightPFIso_DEN_MediumID"
        elTag = ""
        jsnFolder = ""
        if(yearVal[ny] == 20220):
            elTag = "2022Re-recoBCD"
            jsnFolder = "2022_Summer22"
        elif(yearVal[ny] == 20221):
            elTag = "2022Re-recoE+PromptFG"
            jsnFolder = "2022_Summer22EE"
        elif(yearVal[ny] == 20230):
            elTag = "2023PromptC"
            jsnFolder = "2023_Summer23"
        elif(yearVal[ny] == 20231):
            elTag = "2023PromptD"
            jsnFolder = "2023_Summer23BPix"

        print("************** {0} **************".format(yearVal[ny]))

        evaluator_el = correctionlib._core.CorrectionSet.from_file("jsonpog-integration/POG/EGM/{0}/electron.json.gz".format(jsnFolder))
        evaluator_mu = correctionlib._core.CorrectionSet.from_file("jsonpog-integration/POG/MUO/{0}/muon_Z.json.gz".format(jsnFolder))

        phiVal = 0.5 # electrons

        for ltype in range(2):
            etaVal = xEtaBins
            ptVal = xPtBins
            if(binOption == 1 and ltype == 0):
                etaVal = xMuEtaBins
                ptVal = xMuPtBins
            elif(binOption == 1 and ltype == 1):
                etaVal = xElEtaBins
                ptVal = xElPtBins

            print("ltype: {0} / etaBins: {1} / ptBins: {2} -> {3}".format(ltype,len(etaVal)-1,len(ptVal)-1,(len(etaVal)-1)*(len(ptVal)-1)))
            if(ltype == 0):
                histo_mu[ny] = ROOT.TH2D("histo_{0}_mu".format(yearVal[ny]), "histo_{0}_mu".format(yearVal[ny]), len(etaVal)-1, etaVal, len(ptVal)-1, ptVal)
            else:
                histo_el[ny] = ROOT.TH2D("histo_{0}_el".format(yearVal[ny]), "histo_{0}_el".format(yearVal[ny]), len(etaVal)-1, etaVal, len(ptVal)-1, ptVal)

            for eta in range(len(etaVal)-1):
                for pt in range(len(ptVal)-1):

                    sfOff = 1.0
                    sfPri = 1.0
                    sf = 1.0
                    if(ltype == 0):
                        binX = histoLepSFEtaPt_mu.GetXaxis().FindFixBin(etaVal[eta]+0.001)
                        binY = histoLepSFEtaPt_mu.GetYaxis().FindFixBin(ptVal[pt]+0.001)
                        sfPri = histoLepSFEtaPt_mu.GetBinContent(binX,binY)
                        sfOff = evaluator_mu[muIDTag].evaluate(etaVal[eta]+0.001,max(ptVal[pt]+0.001,15.001),"nominal")*evaluator_mu[muISOTag].evaluate(etaVal[eta]+0.001,max(ptVal[pt]+0.001,15.001),"nominal")
                        sf = sfOff/sfPri
                        histo_mu[ny].SetBinContent(eta+1,pt+1,sf)

                    else:
                        binX = histoLepSFEtaPt_el.GetXaxis().FindFixBin(etaVal[eta]+0.001)
                        binY = histoLepSFEtaPt_el.GetYaxis().FindFixBin(ptVal[pt]+0.001)
                        sfPri = histoLepSFEtaPt_el.GetBinContent(binX,binY)
                        sfOff = sf_electron(yearVal[ny], evaluator_el["Electron-ID-SF"].evaluate, elTag, "sf",  "Medium", etaVal[eta], ptVal[pt], phiVal)
                        sf = sfOff/sfPri
                        histo_el[ny].SetBinContent(eta+1,pt+1,sf)

                    if(debug == 1):
                        print("SF({0:1d}/{1:.1f}/{2:.0f}) {3:.3f} / {4:.3f} = {5:.3f}".format(ltype,etaVal[eta],ptVal[pt],sfOff,sfPri,sf))


    fileLepEffCompName = "histoLepSFComparison.root"
    outFileLepEffComp = ROOT.TFile(fileLepEffCompName,"recreate")
    outFileLepEffComp.cd()
    for ny in range(len(yearVal)):
        histo_mu[ny].Write()    
        histo_el[ny].Write()    
    outFileLepEffComp.Close()
