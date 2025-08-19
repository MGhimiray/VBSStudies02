import ROOT
from ROOT import TFile, TH1D, TH2D
import os, sys, getopt, glob
from utilsCategory import plotCategory

if __name__ == "__main__":
    path = "fillhisto_zAnalysis1001_sample203_year20221_job0.root"
    category = 9

    valid = ['path=', 'category=', 'help']
    usage  =  "Usage: ana.py --path=<{0}>\n".format(path)
    usage +=  "              --category=<{0}>".format(category)
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
        if opt == "--category":
            category = int(arg)

    nCat = plotCategory("kPlotCategories")

    fileLep = TFile("{0}".format(path))
    print(fileLep.GetName())
    if(not os.path.exists(path)):
        print("File {0} does not exist".format(fileLep.GetName()))
        exit(1)

    startH = 216
    numberOfSel = 11
    histoLep = [[0 for y in range(numberOfSel)] for x in range(2)]
    yields = [[0 for y in range(numberOfSel)] for x in range(2)]
    meaning = ["all ", "btag", "pu  ", "trig", "msel", "esel", "ws  ", "mcfk", "ewkc", "btv", "btvn"]

    for nlep in range(2):
        for nsel in range(numberOfSel):
            histoLep[nlep][nsel] = (fileLep.Get("histo_{0}_{1}".format(startH+nlep+2*nsel,category))).Clone()
            yields[nlep][nsel] = histoLep[nlep][nsel].GetSumOfWeights()

    msg = ""
    for nsel in range(1,numberOfSel):
        msg = msg + "  " + ("{0}").format(meaning[nsel])
    print(msg)

    for nlep in range(2):
        msg = ""
        for nsel in range(1,numberOfSel):
            yields[nlep][nsel] = yields[nlep][0] / yields[nlep][nsel]
            msg = msg + " " + ("{0:.3f}").format(yields[nlep][nsel])
        print(msg)
