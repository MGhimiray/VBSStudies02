import ROOT
import os, sys, getopt, json

ROOT.ROOT.EnableImplicitMT(4)
from utilsAna import getDATAlist
from lumitools import make_lumihelper, make_jsonhelper

def readDASample(sampleNOW,year,skimType,jsnName,lumiName):

    files = getDATAlist(sampleNOW, year, skimType)
    print("Total files: {0}".format(len(files)))

    if(len(files) == 0):
        print("Nothing to process, exit")
        return
    jsonhelper = make_jsonhelper(jsnName)
    lumihelper = make_lumihelper(lumiName)

    lumidf = ROOT.RDataFrame("LuminosityBlocks", files)
    lumidf = lumidf.Filter(jsonhelper, ["run", "luminosityBlock"], "jsonfilter")
    lumidf = lumidf.Define("lumival", lumihelper, ["run", "luminosityBlock"])
    lumisum = lumidf.Sum("lumival")

    report = lumidf.Report()
    report.Print()
    print("Total lumi({0:}): {1:6.3f}".format(sampleNOW,lumisum.GetValue()))

if __name__ == "__main__":

    group = 1

    skimType = "2l"
    year = 2022
    process = -1

    valid = ['year=', "process=",  'skimType=', 'help']
    usage  =  "Usage: ana.py --year=<{0}>\n".format(year)
    usage +=  "              --process=<{0}>\n".format(process)
    usage +=  "              --skimType=<{0}>".format(skimType)
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
        if opt == "--process":
            process = int(arg)
        if opt == "--skimType":
            skimType = arg

    jsnName = ""
    lumiName = ""
    if(year == 2016):
        jsnName = "jsns/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt"
    elif(year == 2017):
        jsnName = "jsns/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt"
    elif(year == 2018):
        jsnName = "jsns/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"
    elif(year == 2022):
        jsnName = "jsns/Cert_Collisions2022_355100_362760_Golden.json"
        lumiName = "jsns/lumi_2022.csv"
    elif(year == 2023):
        jsnName = "jsns/Cert_Collisions2023_366442_370790_Golden.json"
        lumiName = "jsns/lumi_2023.csv"
    elif(year == 2024):
        jsnName = "jsns/Cert_Collisions2024_378981_386951_Golden.json"
        lumiName = "jsns/lumi_2024.csv"

    readDASample(process,year,skimType,jsnName,lumiName)
