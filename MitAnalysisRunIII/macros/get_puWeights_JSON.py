import ROOT
import correctionlib
import os, sys, getopt, glob
from array import array

if __name__ == "__main__":
    debug = 0
    year = 0

    valid = ["debug=", "year=", 'help']
    usage  =  "Usage: ana.py --debug=<{0}>\n".format(debug)
    usage +=  "Usage: ana.py --year=<{0}>".format(year)
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
        if opt == "--year":
            year = int(arg)


    jsnFolder = ""
    listMethod = ""
    if(year == 20220):
        jsnFolder = "2022_Summer22"
        listMethod = "Collisions2022_355100_357900_eraBCD_GoldenJson"
    elif(year == 20221):
        jsnFolder = "2022_Summer22EE"
        listMethod = "Collisions2022_359022_362760_eraEFG_GoldenJson"
    else:
        print("Wrong year: {0}".format(year))
        sys.exit(1)

    histo_lum  = [0 for y in range(3)]
    histo_lum[0] = ROOT.TH1D("puWeights",     "puWeights",     100, 0, 100)
    histo_lum[1] = ROOT.TH1D("puWeightsUp",   "puWeightsUp",   100, 0, 100)
    histo_lum[2] = ROOT.TH1D("puWeightsDown", "puWeightsDown", 100, 0, 100)

    evaluator_lum = correctionlib._core.CorrectionSet.from_file("jsonpog-integration/POG/LUM/{0}/puWeights.json.gz".format(jsnFolder))

    for npu in range(100):

        syst = [0, 0, 0]
        syst[0] = evaluator_lum[listMethod].evaluate(float(npu), "nominal")
        syst[1] = evaluator_lum[listMethod].evaluate(float(npu), "up"     )
        syst[2] = evaluator_lum[listMethod].evaluate(float(npu), "down"   )

        histo_lum[0].SetBinContent(npu+1,syst[0])
        histo_lum[1].SetBinContent(npu+1,syst[1])
        histo_lum[2].SetBinContent(npu+1,syst[2])

    filePUName = "puWeights_UL_{0}.root".format(year)
    outFilePU = ROOT.TFile(filePUName,"recreate")
    outFilePU.cd()
    histo_lum[0].Write()
    histo_lum[1].Write()
    histo_lum[2].Write()
    outFilePU.Close()
