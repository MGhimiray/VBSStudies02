import ROOT
import correctionlib
import os, sys, getopt, glob
from array import array

xPtBins = array('d', [10.0,15.0,20.0,25.0,30.0,35.0,40.0,45.0,50.0,55.0,60.0,65.0,70.0,75.0,80.0,85.0,90.0,95.0,100.0])
xEtaBins = array('d', [0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4])
yearVal = [20220, 20221, 20230, 20231]


def syst_electron(year, evaluator_el, elTag, sfSyst, sfDef, selVal, etaVal, ptVal, phiVal):
    etaVal = etaVal+0.001
    ptVal  =  ptVal+0.001
    phiVal = phiVal+0.001
    syst = 0.0

    if(year // 10 <= 2022):
        syst= (evaluator_el(elTag,sfSyst,selVal,etaVal,ptVal)-
               evaluator_el(elTag, sfDef,selVal,etaVal,ptVal))
    else:
        syst= (evaluator_el(elTag,sfSyst,selVal,etaVal,ptVal,phiVal)-
               evaluator_el(elTag, sfDef,selVal,etaVal,ptVal,phiVal))

    return syst

if __name__ == "__main__":
    debug = 0

    valid = ["debug=", 'help']
    usage  =  "Usage: ana.py --debug=<{0}>".format(debug)
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
        if opt == "--debug":
            debug = int(arg)

    histo_mu0 = [0 for x in range(len(yearVal))]
    histo_mu1 = [0 for x in range(len(yearVal))]
    histo_mu2 = [0 for x in range(len(yearVal))]
    histo_mu3 = [0 for x in range(len(yearVal))]
    histo_el0 = [0 for x in range(len(yearVal))]
    for ny in range(len(yearVal)):
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

        print("************** {0} / {1} **************".format(yearVal[ny],jsnFolder))

        evaluator_el = correctionlib._core.CorrectionSet.from_file("jsonpog-integration/POG/EGM/{0}/electron.json.gz".format(jsnFolder))
        evaluator_mu = correctionlib._core.CorrectionSet.from_file("jsonpog-integration/POG/MUO/{0}/muon_Z.json.gz".format(jsnFolder))

        etaVal = xEtaBins
        ptVal = xPtBins
        print("etaBins: {0} / ptBins: {1} -> {2}".format(len(etaVal)-1,len(ptVal)-1,(len(etaVal)-1)*(len(ptVal)-1)))
        histo_mu0[ny] = ROOT.TH2D("histo_{0}_mu0".format(yearVal[ny]), "histo_{0}_mu0".format(yearVal[ny]), len(etaVal)-1, etaVal, len(ptVal)-1, ptVal)
        histo_mu1[ny] = ROOT.TH2D("histo_{0}_mu1".format(yearVal[ny]), "histo_{0}_mu1".format(yearVal[ny]), len(etaVal)-1, etaVal, len(ptVal)-1, ptVal)
        histo_mu2[ny] = ROOT.TH2D("histo_{0}_mu2".format(yearVal[ny]), "histo_{0}_mu2".format(yearVal[ny]), len(etaVal)-1, etaVal, len(ptVal)-1, ptVal)
        histo_mu3[ny] = ROOT.TH2D("histo_{0}_mu3".format(yearVal[ny]), "histo_{0}_mu3".format(yearVal[ny]), len(etaVal)-1, etaVal, len(ptVal)-1, ptVal)
        histo_el0[ny] = ROOT.TH2D("histo_{0}_el0".format(yearVal[ny]), "histo_{0}_el0".format(yearVal[ny]), len(etaVal)-1, etaVal, len(ptVal)-1, ptVal)

        phiVal = 0.5 # electrons

        for eta in range(len(etaVal)-1):
            for pt in range(len(ptVal)-1):

                systm0 = evaluator_mu[muIDTag] .evaluate(etaVal[eta]+0.001,max(ptVal[pt]+0.001,15.001),"syst")
                systm1 = evaluator_mu[muISOTag].evaluate(etaVal[eta]+0.001,max(ptVal[pt]+0.001,15.001),"syst")
                systm2 = evaluator_mu[muIDTag] .evaluate(etaVal[eta]+0.001,max(ptVal[pt]+0.001,15.001),"stat")
                systm3 = evaluator_mu[muISOTag].evaluate(etaVal[eta]+0.001,max(ptVal[pt]+0.001,15.001),"stat")
                histo_mu0[ny].SetBinContent(eta+1,pt+1,systm0)
                histo_mu1[ny].SetBinContent(eta+1,pt+1,systm1)
                histo_mu2[ny].SetBinContent(eta+1,pt+1,systm2)
                histo_mu3[ny].SetBinContent(eta+1,pt+1,systm3)

                syste0 = syst_electron(yearVal[ny], evaluator_el["Electron-ID-SF"].evaluate, elTag, "sfup", "sf", "wp80iso", etaVal[eta], ptVal[pt], phiVal)
                histo_el0[ny].SetBinContent(eta+1,pt+1,syste0)

                if(debug == 1):
                    print("SF({0:.1f}/{1:.0f}) {2:.3f} / {3:.3f} / {4:.3f}".format(etaVal[eta],ptVal[pt],systm0,systm1,syste0))


    fileLepEffSystName = "histoLepSFSystematics.root"
    outFileLepEffSyst = ROOT.TFile(fileLepEffSystName,"recreate")
    outFileLepEffSyst.cd()
    for ny in range(len(yearVal)):
        histo_mu0[ny].Write()    
        histo_mu1[ny].Write()    
        histo_mu2[ny].Write()    
        histo_mu3[ny].Write()    
        histo_el0[ny].Write()    
    outFileLepEffSyst.Close()
