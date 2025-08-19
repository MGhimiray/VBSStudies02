import ROOT
import correctionlib
import os, sys, getopt, glob
from array import array

xPtBins = array('d', [20.0,25.0,30.0,35.0,40.0,45.0,50.0,55.0,60.0,65.0,70.0,75.0,80.0,85.0,90.0,95.0,100.0])
xEtaBins = array('d', [0.5,1.0,1.5])
yearVal = [20220, 20221]


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


    #listMethod = ["deepJet_kinfit", "deepJet_ptrel", "deepJet_tnp", "particleNet_kinfit", "particleNet_ptrel", "particleNet_tnp", "robustParticleTransformer_kinfit", "robustParticleTransformer_ptrel", "robustParticleTransformer_tnp"]
    listMethod = ["deepJet_comb", "deepJet_mujets", "deepJet_mujets", "particleNet_comb", "particleNet_mujets", "particleNet_mujets", "robustParticleTransformer_comb", "robustParticleTransformer_mujets", "robustParticleTransformer_mujets"]

    workingPoint = ["T", "M", "L"]

    histo_btv0 = [[[0 for y in range(len(yearVal))] for x in range(len(xEtaBins))] for z in range(len(workingPoint))]
    histo_btv1 = [[[0 for y in range(len(yearVal))] for x in range(len(xEtaBins))] for z in range(len(workingPoint))]
    histo_btv2 = [[[0 for y in range(len(yearVal))] for x in range(len(xEtaBins))] for z in range(len(workingPoint))]
    histo_btv3 = [[[0 for y in range(len(yearVal))] for x in range(len(xEtaBins))] for z in range(len(workingPoint))]
    histo_btv4 = [[[0 for y in range(len(yearVal))] for x in range(len(xEtaBins))] for z in range(len(workingPoint))]
    histo_btv5 = [[[0 for y in range(len(yearVal))] for x in range(len(xEtaBins))] for z in range(len(workingPoint))]
    histo_btv6 = [[[0 for y in range(len(yearVal))] for x in range(len(xEtaBins))] for z in range(len(workingPoint))]
    histo_btv7 = [[[0 for y in range(len(yearVal))] for x in range(len(xEtaBins))] for z in range(len(workingPoint))]
    histo_btv8 = [[[0 for y in range(len(yearVal))] for x in range(len(xEtaBins))] for z in range(len(workingPoint))]

    for ny in range(len(yearVal)):
        jsnFolder = ""
        if(yearVal[ny] == 20220):
            jsnFolder = "2022_Summer22"
        elif(yearVal[ny] == 20221):
            jsnFolder = "2022_Summer22EE"

        print("************** {0} **************".format(yearVal[ny]))

        #evaluator_btv = correctionlib._core.CorrectionSet.from_file("jsonpog-integration/POG/BTV/{0}/btagging_v0_hf_jan24.json.gz".format(jsnFolder))
        evaluator_btv = correctionlib._core.CorrectionSet.from_file("jsonpog-integration/POG/BTV/{0}/btagging_v1_mar24.json.gz".format(jsnFolder))

        for eta in range(len(xEtaBins)):
            for wp in range(len(workingPoint)):
                histo_btv0[wp][eta][ny] = ROOT.TH1D("histo_btv0_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), "histo_btv0_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), len(xPtBins)-1, xPtBins)
                histo_btv1[wp][eta][ny] = ROOT.TH1D("histo_btv1_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), "histo_btv1_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), len(xPtBins)-1, xPtBins)
                histo_btv2[wp][eta][ny] = ROOT.TH1D("histo_btv2_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), "histo_btv2_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), len(xPtBins)-1, xPtBins)
                histo_btv3[wp][eta][ny] = ROOT.TH1D("histo_btv3_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), "histo_btv3_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), len(xPtBins)-1, xPtBins)
                histo_btv4[wp][eta][ny] = ROOT.TH1D("histo_btv4_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), "histo_btv4_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), len(xPtBins)-1, xPtBins)
                histo_btv5[wp][eta][ny] = ROOT.TH1D("histo_btv5_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), "histo_btv5_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), len(xPtBins)-1, xPtBins)
                histo_btv6[wp][eta][ny] = ROOT.TH1D("histo_btv6_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), "histo_btv6_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), len(xPtBins)-1, xPtBins)
                histo_btv7[wp][eta][ny] = ROOT.TH1D("histo_btv7_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), "histo_btv7_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), len(xPtBins)-1, xPtBins)
                histo_btv8[wp][eta][ny] = ROOT.TH1D("histo_btv8_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), "histo_btv8_{0}_{1}_{2}".format(workingPoint[wp],eta,yearVal[ny]), len(xPtBins)-1, xPtBins)

                syst = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                for pt in range(len(xPtBins)-1):
                    syst[0] = evaluator_btv[listMethod[0]].evaluate("central" , workingPoint[wp], 5, xEtaBins[eta], xPtBins[pt]+0.001)
                    syst[1] = evaluator_btv[listMethod[1]].evaluate("central" , workingPoint[wp], 5, xEtaBins[eta], xPtBins[pt]+0.001)
                    syst[2] = evaluator_btv[listMethod[2]].evaluate("central" , workingPoint[wp], 5, xEtaBins[eta], xPtBins[pt]+0.001)
                    syst[3] = evaluator_btv[listMethod[3]].evaluate("central" , workingPoint[wp], 5, xEtaBins[eta], xPtBins[pt]+0.001)
                    syst[4] = evaluator_btv[listMethod[4]].evaluate("central" , workingPoint[wp], 5, xEtaBins[eta], xPtBins[pt]+0.001)
                    syst[5] = evaluator_btv[listMethod[5]].evaluate("central" , workingPoint[wp], 5, xEtaBins[eta], xPtBins[pt]+0.001)
                    syst[6] = evaluator_btv[listMethod[6]].evaluate("central" , workingPoint[wp], 5, xEtaBins[eta], xPtBins[pt]+0.001)
                    syst[7] = evaluator_btv[listMethod[7]].evaluate("central" , workingPoint[wp], 5, xEtaBins[eta], xPtBins[pt]+0.001)
                    syst[8] = evaluator_btv[listMethod[8]].evaluate("central" , workingPoint[wp], 5, xEtaBins[eta], xPtBins[pt]+0.001)
                    histo_btv0[wp][eta][ny].SetBinContent(pt+1,syst[0])
                    histo_btv1[wp][eta][ny].SetBinContent(pt+1,syst[1])
                    histo_btv2[wp][eta][ny].SetBinContent(pt+1,syst[2])
                    histo_btv3[wp][eta][ny].SetBinContent(pt+1,syst[3])
                    histo_btv4[wp][eta][ny].SetBinContent(pt+1,syst[4])
                    histo_btv5[wp][eta][ny].SetBinContent(pt+1,syst[5])
                    histo_btv6[wp][eta][ny].SetBinContent(pt+1,syst[6])
                    histo_btv7[wp][eta][ny].SetBinContent(pt+1,syst[7])
                    histo_btv8[wp][eta][ny].SetBinContent(pt+1,syst[8])
                    if(debug == 1):
                        print("SF({0}/{1:.1f}/{2:.0f}) ({3:.3f}/{4:.3f}/{5:.3f}) ({6:.3f}/{7:.3f}/{8:.3f}) ({9:.3f}/{10:.3f}/{11:.3f})".format(workingPoint[wp],xEtaBins[eta],xPtBins[pt],syst[0],syst[1],syst[2],syst[3],syst[4],syst[5],syst[6],syst[7],syst[8]))

        theWorkingPoint = workingPoint[2]
        theListMethod = listMethod[0]
        for npt in range(20):
            for neta in range(25):
                theEta = float(neta)/10.
                thePt = float(npt)*10+20
                val = evaluator_btv[theListMethod].evaluate("central", theWorkingPoint, 5, theEta, thePt)
                if(debug == 2):
                    print("SF({0}/{1:.1f}/{2:.0f}) {3:.5f}".format(theWorkingPoint,theEta,thePt,val))

    fileBTVSFsName = "histoBTVSFs.root"
    outFileBTVSFs = ROOT.TFile(fileBTVSFsName,"recreate")
    outFileBTVSFs.cd()
    for ny in range(len(yearVal)):
        for eta in range(len(xEtaBins)):
            for wp in range(len(workingPoint)):
                histo_btv0[wp][eta][ny].Write()
                histo_btv1[wp][eta][ny].Write()
                histo_btv2[wp][eta][ny].Write()
                histo_btv3[wp][eta][ny].Write()
                histo_btv4[wp][eta][ny].Write()
                histo_btv5[wp][eta][ny].Write()
                histo_btv6[wp][eta][ny].Write()
                histo_btv7[wp][eta][ny].Write()
                histo_btv8[wp][eta][ny].Write()
    outFileBTVSFs.Close()
