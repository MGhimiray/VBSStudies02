import ROOT
import os, sys, getopt

ROOT.ROOT.EnableImplicitMT(4)
from utilsCategory import plotCategory
from utilsAna import getMClist, getDATAlist
from utilsAna import SwitchSample

def readMCSample(sampleNOW, year, PDType, skimType):

    files = getMClist(sampleNOW, skimType)
    print(len(files))

    for f in range(len(files)):
        try:
            df = ROOT.RDataFrame("Events", files[f])
            nevents = df.Count().GetValue()
            del df
        except Exception as e:
            print("{0} {1}".format(files[f].replace("root://t3serv017.mit.edu/","/mnt/T3_US_MIT/hadoop"),e))

def readDASample(sampleNOW, year, PDType, skimType):

    files = getDATAlist(sampleNOW, year, PDType, skimType)
    print(len(files))

    for f in range(len(files)):
        try:
            df = ROOT.RDataFrame("Events", files[f])
            nevents = df.Count().GetValue()
            del df
        except Exception as e:
            print("{0} {1}".format(files[f].replace("root://t3serv017.mit.edu/","/mnt/T3_US_MIT/hadoop"),e))

if __name__ == "__main__":

    year = 2022
    skimType = "1l"
    process = 0

    valid = ["year=", "skimType=", "process=", 'help']
    usage  =  "Usage: ana.py --year=<{0}>\n".format(year)
    usage +=  "              --skimType=<{0}>\n".format(skimType)
    usage +=  "              --process=<{0}>".format(process)
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
        if opt == "--skimType":
            skimType = str(arg)
        if opt == "--process":
            process = int(arg)

    if(process == 1):
        readMCSample(1,2018,"All",skimType)
    elif(process == 101):
        readDASample(process,2018,"SingleMuon",skimType)
    elif(process == 102):
        readDASample(process,2018,"DoubleMuon",skimType)
    elif(process == 102):
        readDASample(process,2018,"MuonEG",skimType)
    elif(process == 104):
        readDASample(process,2018,"Egamma",skimType)
