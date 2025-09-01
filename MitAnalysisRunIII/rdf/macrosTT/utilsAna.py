import ROOT
import os, json, sys
from utilsCategory import plotCategory
from subprocess import call,check_output
#from correctionlib import _core
import correctionlib
correctionlib.register_pyroot_binding()
#ROOT.gInterpreter.Declare('#include "mysf.h"')
#ROOT.gInterpreter.Load("mysf.so")

useXROOTD = False

def getLumi(year):
    lumi = [36.1, 41.5, 60.0, 8.1, 26.7, 18.1, 9.7, 107.0]

    lumiBit = -999
    if(year == 2016): lumiBit = 0
    elif(year == 2017): lumiBit = 1
    elif(year == 2018): lumiBit = 2
    elif(year == 20220): lumiBit = 3
    elif(year == 20221): lumiBit = 4
    elif(year == 20230): lumiBit = 5
    elif(year == 20231): lumiBit = 6
    elif(year == 20240): lumiBit = 7

    print("lumi({0}/{1}) = {2}".format(year,lumiBit,lumi[lumiBit]))

    return lumi[lumiBit]

#if "/functions.so" not in ROOT.gSystem.GetLibraries():
#    ROOT.gSystem.CompileMacro("functions.cc","k")
ROOT.gInterpreter.ProcessLine('#include "functions.h"')

#def loadCorrectionSet(year):
#    ROOT.gInterpreter.Load("mysf.so")
#    ROOT.gInterpreter.Declare('#include "mysf.h"')
#    ROOT.gInterpreter.ProcessLine('auto corr_sf = MyCorrections(%d);' % (year))

def loadJSON(fIn):

    if not os.path.isfile(fIn):
        print("JSON file %s does not exist" % fIn)
        return

    if not hasattr(ROOT, "jsonMap"):
        print("jsonMap not found in ROOT dict")
        return

    info = json.load(open(fIn))
    print("JSON file %s loaded" % fIn)
    for k,v in info.items():

        vec = ROOT.std.vector["std::pair<unsigned int, unsigned int>"]()
        for combo in v:
            pair = ROOT.std.pair["unsigned int", "unsigned int"](*[int(c) for c in combo])
            vec.push_back(pair)
            ROOT.jsonMap[int(k)] = vec

def getTriggerFromJson(overall, type, year):

    if(year > 10000): year = year // 10

    for trigger in overall:
        if(trigger['name'] == type and trigger['year'] == year): return trigger['definition']

def getLeptomSelFromJson(overall, type, year, debug = 0):

    if(year > 10000): year = year // 10
    version = 12
    if(year >= 2024): version = 15

    for leptonSel in overall:
        if(leptonSel['name'] == type and leptonSel['version'] == version):
            if(debug == 1):
                print("{0}({1}): {2}".format(leptonSel['name'],leptonSel['version'],leptonSel['definition']))
            return leptonSel['definition']

def getMesonFromJson(overall, type, cat ):

    for meson in overall:
        if meson['name'] == type and meson['type'] == cat: return meson['definition']

def findDataset(name):

    DASclient = "dasgoclient -query '%(query)s'"
    cmd= DASclient%{'query':'file dataset=%s'%name}
    print(cmd)
    check_output(cmd,shell=True)
    fileList=[ 'root://xrootd-cms.infn.it//'+x for x in check_output(cmd,shell=True).split() ]

    files_ROOT = ROOT.vector('string')()
    for f in fileList: files_ROOT.push_back(f)

    return files_ROOT

def findDIR(directory):

    print(directory)

    maxFiles = 1000000000
    if("/1l/" in directory and "NANOAODSIM" in directory and
       "TTto4Q" not in directory and "WWto4Q" not in directory):
        maxFiles = 200

    # HACK!
    #if("/2l/" in directory and "NANOAODSIM" in directory and
    #   ("DY" in directory or "TT" in directory)):
    #    maxFiles = 100

    counter = 0
    rootFiles = ROOT.vector('string')()

    if(useXROOTD == True and "/ceph/submit/data/group/cms" in directory):
        xrd = "root://submit50.mit.edu/"
        xrdpath = directory.replace("/ceph/submit/data/group/cms","")
        f = check_output(['xrdfs', f'{xrd}', 'ls', xrdpath]).decode(sys.stdout.encoding)
        stringFiles = f.split()
        for e in range(len(stringFiles)):
            filePath = xrd + stringFiles[e]
            if "failed/" in filePath: continue
            if "log/" in filePath: continue
            if ".txt" in filePath: continue
            counter+=1
            if(counter > maxFiles): break
            rootFiles.push_back(filePath)

    else:
        for root, directories, filenames in os.walk(directory):
            for f in filenames:

                isBadFile = False
                filePath = os.path.join(os.path.abspath(root), f)
                if "failed/" in filePath: continue
                if "log/" in filePath: continue
                if ".txt" in filePath: continue
                if(("XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX" in filePath) or

                   ("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" in filePath)
                   ): isBadFile = True

                if(isBadFile == True):
                    print("Bad file: {0}".format(filePath))
                    continue
                counter+=1
                if(counter > maxFiles): break
                rootFiles.push_back(filePath)

    #print(rootFiles)
    return rootFiles

def findMany(basedir, regex):

    if basedir[-1] == "/": basedir = basedir[:-1]
    regex = basedir + "/" + regex

    rootFiles = ROOT.vector('string')()
    for root, directories, filenames in os.walk(basedir):

        for f in filenames:

            filePath = os.path.join(os.path.abspath(root), f)
            if "failed/" in filePath: continue
            if "log/" in filePath: continue
            if fnmatch.fnmatch(filePath, regex): rootFiles.push_back(filePath)

    return rootFiles

# split fIns files in group files
def groupFiles(fIns, group):

    ret =  [fIns[i::group] for i in range(group)]

    return ret

def concatenate(result, tmp1):
    for f in tmp1:
        result.push_back(f)

def getMClist(sampleNOW, skimType):

    files = findDIR("{}".format(SwitchSample(sampleNOW, skimType)[0]))
    return files

def getDATAlist(type, year, skimType):

    if(year > 10000): year = year // 10

    #dirT2 = "/mnt/T2_US_MIT/hadoop/cms/store/user/paus/nanohr/D00/"
    #dirT2 = "/mnt/T3_US_MIT/hadoop/scratch/ceballos/nanoaod/skims_submit/" + skimType
    dirT2 = "/mnt/home/mghimiray/VBSStudies/DATA/DAS"
    dirTest = "/ceph/submit/data/group/cms/store/user/ceballos/test/test/"

    jsnName = ""
    if(year == 2016):
        jsnName = "Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt"
    elif(year == 2017):
        jsnName = "Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt"
    elif(year == 2018):
        jsnName = "Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"
    elif(year == 2022):
        jsnName = "Cert_Collisions2022_355100_362760_Golden.json"
    elif(year == 2023):
        jsnName = "Cert_Collisions2023_366442_370790_Golden.json"
    elif(year == 2024):
        jsnName = "Cert_Collisions2024_378981_386951_Golden.json"

    if os.path.exists(os.path.join("jsns",jsnName)):
        loadJSON(os.path.join("jsns",jsnName))
    else:
        loadJSON(jsnName)

    filesL = []
    ##### 2018 ####
    if(year == 2018 and type == 1000):
        filesL = findDIR("{0}/{1}/{2}/SingleMuon+Run2018A-UL2018_MiniAODv2-v2+MINIAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1001):
        filesL = findDIR("{0}/{1}/{2}/SingleMuon+Run2018B-UL2018_MiniAODv2-v2+MINIAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1002):
        filesL = findDIR("{0}/{1}/{2}/SingleMuon+Run2018C-UL2018_MiniAODv2-v2+MINIAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1003):
        filesL = findDIR("{0}/{1}/{2}/SingleMuon+Run2018D-UL2018_MiniAODv2-v3+MINIAOD".format(dirT2, year, skimType))

    elif(year == 2018 and type == 1010):
        filesL = findDIR("{0}/{1}/{2}/DoubleMuon+Run2018A-UL2018_MiniAODv2-v1+MINIAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1011):
        filesL = findDIR("{0}/{1}/{2}/DoubleMuon+Run2018B-UL2018_MiniAODv2-v1+MINIAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1012):
        filesL = findDIR("{0}/{1}/{2}/DoubleMuon+Run2018C-UL2018_MiniAODv2-v1+MINIAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1013):
        filesL = findDIR("{0}/{1}/{2}/DoubleMuon+Run2018D-UL2018_MiniAODv2-v1+MINIAOD".format(dirT2, year, skimType))

    elif(year == 2018 and type == 1020):
        filesL = findDIR("{0}/{1}/{2}/MuonEG+Run2018A-UL2018_MiniAODv2-v1+MINIAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1021):
        filesL = findDIR("{0}/{1}/{2}/MuonEG+Run2018B-UL2018_MiniAODv2-v1+MINIAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1022):
        filesL = findDIR("{0}/{1}/{2}/MuonEG+Run2018C-UL2018_MiniAODv2-v1+MINIAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1023):
        filesL = findDIR("{0}/{1}/{2}/MuonEG+Run2018D-UL2018_MiniAODv2-v1+MINIAOD".format(dirT2, year, skimType))

    elif(year == 2018 and type == 1030):
        filesL = findDIR("{0}/{1}/{2}/EGamma+Run2018A-UL2018_MiniAODv2-v1+MINIAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1031):
        filesL = findDIR("{0}/{1}/{2}/EGamma+Run2018B-UL2018_MiniAODv2-v1+MINIAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1032):
        filesL = findDIR("{0}/{1}/{2}/EGamma+Run2018C-UL2018_MiniAODv2-v1+MINIAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1033):
        filesL = findDIR("{0}/{1}/{2}/EGamma+Run2018D-UL2018_MiniAODv2-v2+MINIAOD".format(dirT2, year, skimType))

    elif(year == 2018 and type == 1050):
        filesL = findDIR("{0}/{1}/{2}/MET+Run2018A-UL2018_MiniAODv2_NanoAODv9-v2+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1051):
        filesL = findDIR("{0}/{1}/{2}/MET+Run2018B-UL2018_MiniAODv2_NanoAODv9-v2+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1052):
        filesL = findDIR("{0}/{1}/{2}/MET+Run2018C-UL2018_MiniAODv2_NanoAODv9-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2018 and type == 1053):
        filesL = findDIR("{0}/{1}/{2}/MET+Run2018D-UL2018_MiniAODv2_NanoAODv9-v1+NANOAOD".format(dirT2, year, skimType))

    ##### 2022 ####
    elif(year == 2022 and type == 1001):
        filesL = findDIR("{0}/{1}/{2}/SingleMuon+Run2022B-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1002):
        filesL = findDIR("{0}/{1}/{2}/SingleMuon+Run2022C-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))

    elif(year == 2022 and type == 1011):
        filesL = findDIR("{0}/{1}/{2}/DoubleMuon+Run2022B-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1012):
        filesL = findDIR("{0}/{1}/{2}/DoubleMuon+Run2022C-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))

    elif(year == 2022 and type == 1021):
        filesL = findDIR("{0}/{1}/{2}/MuonEG+Run2022B-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1022):
        filesL = findDIR("{0}/{1}/{2}/MuonEG+Run2022C-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1023):
        filesL = findDIR("{0}/{1}/{2}/MuonEG+Run2022D-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1024):
        filesL = findDIR("{0}/{1}/{2}/MuonEG+Run2022E-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1025):
        filesL = findDIR("{0}/{1}/{2}/MuonEG+Run2022F-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1026):
        filesL = findDIR("{0}/{1}/{2}/MuonEG+Run2022G-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))

    elif(year == 2022 and type == 1031):
        filesL = findDIR("{0}/{1}/{2}/EGamma+Run2022B-22Sep2023-v2+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1032):
        filesL = findDIR("{0}/{1}/{2}/EGamma+Run2022C-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1033):
        filesL = findDIR("{0}/{1}/{2}/EGamma+Run2022D-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1034):
        filesL = findDIR("{0}/{1}/{2}/EGamma+Run2022E-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1035):
        filesL = findDIR("{0}/{1}/{2}/EGamma+Run2022F-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1036):
        filesL = findDIR("{0}/{1}/{2}/EGamma+Run2022G-22Sep2023-v2+NANOAOD".format(dirT2, year, skimType))

    elif(year == 2022 and type == 1042):
        filesL = findDIR("{0}/{1}/{2}/Muon+Run2022C-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1043):
        filesL = findDIR("{0}/{1}/{2}/Muon+Run2022D-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1044):
        filesL = findDIR("{0}/{1}/{2}/Muon+Run2022E-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1045):
        filesL = findDIR("{0}/{1}/{2}/Muon+Run2022F-22Sep2023-v2+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1046):
        filesL = findDIR("{0}/{1}/{2}/Muon+Run2022G-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))

    elif(year == 2022 and type == 1051):
        filesL = findDIR("{0}/{1}/{2}/MET+Run2022B-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1052):
        filesL = findDIR("{0}/{1}/{2}/MET+Run2022C-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/JetMET+Run2022C-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2022 and type == 1053):
        filesL = findDIR("{0}/{1}/{2}/JetMET+Run2022D-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1054):
        filesL = findDIR("{0}/{1}/{2}/JetMET+Run2022E-22Sep2023-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1055):
        filesL = findDIR("{0}/{1}/{2}/JetMET+Run2022F-22Sep2023-v2+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2022 and type == 1056):
        filesL = findDIR("{0}/{1}/{2}/JetMET+Run2022G-22Sep2023-v2+NANOAOD".format(dirT2, year, skimType))

##### 2023 ####

    elif(year == 2023 and type == 1022):
        filesL = findDIR("{0}/{1}/{2}/MuonEG+Run2023C-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/MuonEG+Run2023C-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/MuonEG+Run2023C-22Sep2023_v3-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/MuonEG+Run2023C-22Sep2023_v4-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2023 and type == 1023):
        filesL = findDIR("{0}/{1}/{2}/MuonEG+Run2023D-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/MuonEG+Run2023D-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)

    elif(year == 2023 and type == 1032):
        filesL   = findDIR("{0}/{1}/{2}/EGamma0+Run2023C-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/EGamma0+Run2023C-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/EGamma0+Run2023C-22Sep2023_v3-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/EGamma0+Run2023C-22Sep2023_v4-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2023C-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2023C-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2023C-22Sep2023_v3-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2023C-22Sep2023_v4-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2023 and type == 1033):
        filesL   = findDIR("{0}/{1}/{2}/EGamma0+Run2023D-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/EGamma0+Run2023D-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2023D-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2023D-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)

    elif(year == 2023 and type == 1042):
        filesL   = findDIR("{0}/{1}/{2}/Muon0+Run2023C-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/Muon0+Run2023C-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/Muon0+Run2023C-22Sep2023_v3-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/Muon0+Run2023C-22Sep2023_v4-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2023C-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2023C-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2023C-22Sep2023_v3-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2023C-22Sep2023_v4-v2+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2023 and type == 1043):
        filesL   = findDIR("{0}/{1}/{2}/Muon0+Run2023D-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/Muon0+Run2023D-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2023D-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2023D-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)


    elif(year == 2023 and type == 1052):
        filesL   = findDIR("{0}/{1}/{2}/JetMET0+Run2023C-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/JetMET0+Run2023C-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/JetMET0+Run2023C-22Sep2023_v3-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/JetMET0+Run2023C-22Sep2023_v4-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2023C-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2023C-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2023C-22Sep2023_v3-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2023C-22Sep2023_v4-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2023 and type == 1053):
        filesL   = findDIR("{0}/{1}/{2}/JetMET0+Run2023D-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/JetMET0+Run2023D-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2023D-22Sep2023_v1-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2023D-22Sep2023_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)

    ##### 2024 ####
    elif(year == 2024 and type == 1022):
        filesL   = findDIR("{0}/{1}/{2}/MuonEG+Run2024C-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2024 and type == 1023):
        filesL   = findDIR("{0}/{1}/{2}/MuonEG+Run2024D-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2024 and type == 1024):
        filesL   = findDIR("{0}/{1}/{2}/MuonEG+Run2024E-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2024 and type == 1025):
        filesL   = findDIR("{0}/{1}/{2}/MuonEG+Run2024F-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2024 and type == 1026):
        filesL   = findDIR("{0}/{1}/{2}/MuonEG+Run2024G-MINIv6NANOv15-v3+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2024 and type == 1027):
        filesL   = findDIR("{0}/{1}/{2}/MuonEG+Run2024H-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
    elif(year == 2024 and type == 1028):
        filesL   = findDIR("{0}/{1}/{2}/MuonEG+Run2024I-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/MuonEG+Run2024I-MINIv6NANOv15_v2-v2+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)

    elif(year == 2024 and type == 1032):
        filesL   = findDIR("{0}/{1}/{2}/EGamma0+Run2024C-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2024C-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1033):
        filesL   = findDIR("{0}/{1}/{2}/EGamma0+Run2024D-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2024D-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1034):
        filesL   = findDIR("{0}/{1}/{2}/EGamma0+Run2024E-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2024E-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1035):
        filesL   = findDIR("{0}/{1}/{2}/EGamma0+Run2024F-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2024F-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1036):
        filesL   = findDIR("{0}/{1}/{2}/EGamma0+Run2024G-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2024G-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1037):
        filesL   = findDIR("{0}/{1}/{2}/EGamma0+Run2024H-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2024H-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1038):
        filesL   = findDIR("{0}/{1}/{2}/EGamma0+Run2024I-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2024I-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/EGamma0+Run2024I-MINIv6NANOv15_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/EGamma1+Run2024I-MINIv6NANOv15_v2-v2+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)

    elif(year == 2024 and type == 1042):
        filesL   = findDIR("{0}/{1}/{2}/Muon0+Run2024C-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2024C-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1043):
        filesL   = findDIR("{0}/{1}/{2}/Muon0+Run2024D-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2024D-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1044):
        filesL   = findDIR("{0}/{1}/{2}/Muon0+Run2024E-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2024E-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1045):
        filesL   = findDIR("{0}/{1}/{2}/Muon0+Run2024F-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2024F-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1046):
        filesL   = findDIR("{0}/{1}/{2}/Muon0+Run2024G-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2024G-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1047):
        filesL   = findDIR("{0}/{1}/{2}/Muon0+Run2024H-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2024H-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1048):
        filesL   = findDIR("{0}/{1}/{2}/Muon0+Run2024I-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2024I-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/Muon0+Run2024I-MINIv6NANOv15_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/Muon1+Run2024I-MINIv6NANOv15_v2-v2+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)

    elif(year == 2024 and type == 1052):
        filesL   = findDIR("{0}/{1}/{2}/JetMET0+Run2024C-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2024C-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1053):
        filesL   = findDIR("{0}/{1}/{2}/JetMET0+Run2024D-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2024D-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1054):
        filesL   = findDIR("{0}/{1}/{2}/JetMET0+Run2024E-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2024E-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1055):
        filesL   = findDIR("{0}/{1}/{2}/JetMET0+Run2024F-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2024F-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1056):
        filesL   = findDIR("{0}/{1}/{2}/JetMET0+Run2024G-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2024G-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1057):
        filesL   = findDIR("{0}/{1}/{2}/JetMET0+Run2024H-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2024H-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
    elif(year == 2024 and type == 1058):
        filesL   = findDIR("{0}/{1}/{2}/JetMET0+Run2024I-MINIv6NANOv15-v2+NANOAOD".format(dirT2, year, skimType))
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2024I-MINIv6NANOv15-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/JetMET0+Run2024I-MINIv6NANOv15_v2-v1+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)
        filesAux = findDIR("{0}/{1}/{2}/JetMET1+Run2024I-MINIv6NANOv15_v2-v2+NANOAOD".format(dirT2, year, skimType))
        for x in filesAux:
            filesL.push_back(x)

    elif(year == 2022 and type == 9999):
        filesL = findDIR("{0}".format(dirTest))

    files = ROOT.vector('string')()
    concatenate(files, filesL)

    return files

def SwitchSample(argument, skimType):

    #dirT2 = "/scratch/submit/cms/ceballos/nanoaod/skims_submit/" + skimType
    dirT2 = "/mnt/home/mghimiray/VBSStudies/DATA/Monte_Carlo/"
    dirLocal = "/work/submit/mariadlf/Hrare/D01"

    ggWWXS_LO_MCFM = 0.0496265/(0.1086*0.1086)
    ggWWXS_LO_MADGRAPH = 3.51313
    ggWWXS_kFactor = 1.4

    switch = {
       100: (dirT2+"2022/DYto2L-2Jets_MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",19982.5*1000,plotCategory("kPlotDY")),
       101: (dirT2+"2022/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",6345.99*1000,plotCategory("kPlotDY")),
       102: (dirT2+"2022/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",(118.7*1.06-ggWWXS_LO_MCFM)*0.1086*0.1086*9*1000,plotCategory("kPlotqqWW")),
       103: (dirT2+"2022/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",4.924*1.08*1000,plotCategory("kPlotWZ")),
       104: (dirT2+"2022/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",7.568*1.08*1000,plotCategory("kPlotWZ")),
       105: (dirT2+"2022/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",6.788*1.19*1000,plotCategory("kPlotZZ")),
       106: (dirT2+"2022/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",1.031*1.16*1000,plotCategory("kPlotZZ")),
       107: (dirT2+"2022/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",1.390*1.19*1000,plotCategory("kPlotZZ")),
       108: (dirT2+"2022/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.950*923.6*0.1086*0.1086*9*1000,plotCategory("kPlotTT")),
       109: (dirT2+"2022/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.950*923.6*0.1086*3*(1-0.1086*3)*2*1000,plotCategory("kPlotTT")),
       110: (dirT2+"2022/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5_ext1-v2+NANOAODSIM",1000000*0.950*923.6*(1-0.1086*3)*(1-0.1086*3)*1000,plotCategory("kPlotNonPrompt")),
       111: (dirT2+"2022/TbarWplusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",4.67*1000,plotCategory("kPlotTW")),
       112: (dirT2+"2022/TWminusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",4.67*1000,plotCategory("kPlotTW")),
       113: (dirT2+"2022/WtoLNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",64481.58*1000,plotCategory("kPlotOther")),
       114: (dirT2+"2022/WWW_4F_TuneCP5_13p6TeV_amcatnlo-madspin-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.23280*1000,plotCategory("kPlotVVV")),
       115: (dirT2+"2022/WWZ_4F_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.18510*1000,plotCategory("kPlotVVV")),
       116: (dirT2+"2022/WZZ_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.06206*1000,plotCategory("kPlotVVV")),
       117: (dirT2+"2022/ZZZ_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.01591*1000,plotCategory("kPlotVVV")),
       118: (dirT2+"2022/WZGtoLNuZG_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.08425*1000,plotCategory("kPlotVVV")),
       119: (dirT2+"2022/TTWW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.0081651*1000,plotCategory("kPlotTVX")),
       120: (dirT2+"2022/TTZZ_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.0015617*1000,plotCategory("kPlotTVX")),
       121: (dirT2+"2022/GluGluHtoZZto4L_M-125_TuneCP5_13p6TeV_powheg2-JHUGenV752-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",52.230*0.02619*0.101*0.101*1000,plotCategory("kPlotHiggs")),
       122: (dirT2+"2022/VBFHto2Zto4L_M125_TuneCP5_13p6TeV_powheg-jhugenv752-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",4.0780*0.02619*0.101*0.101*1000,plotCategory("kPlotHiggs")),
       123: (dirT2+"2022/TTLL_MLL-4to50_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.03949*1000,plotCategory("kPlotTVX")),
       124: (dirT2+"2022/TTLL_MLL-50_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.08646*1000,plotCategory("kPlotTVX")),
       125: (dirT2+"2022/ggWWto2L2Nu_OS_PolarizationLL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.24053*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       126: (dirT2+"2022/ggWWto2L2Nu_OS_PolarizationLT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.08268*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       127: (dirT2+"2022/ggWWto2L2Nu_OS_PolarizationTL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.08268*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       128: (dirT2+"2022/ggWWto2L2Nu_OS_PolarizationTT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",3.10724*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       129: (dirT2+"2022/DYGto2LG-1Jets_MLL-50_PTG-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",124.18762*1000,plotCategory("kPlotVG")),
       130: (dirT2+"2022/DYGto2LG-1Jets_MLL-50_PTG-50to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v3+NANOAODSIM",2.08977*1000,plotCategory("kPlotVG")),
       131: (dirT2+"2022/DYGto2LG-1Jets_MLL-50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.34767*1000,plotCategory("kPlotVG")),
       132: (dirT2+"2022/DYGto2LG-1Jets_MLL-50_PTG-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.04734*1000,plotCategory("kPlotVG")),
       133: (dirT2+"2022/WGtoLNuG-1Jets_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",668.91538*1000,plotCategory("kPlotVG")),
       134: (dirT2+"2022/WGtoLNuG-1Jets_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",2.22141*1000,plotCategory("kPlotVG")),
       135: (dirT2+"2022/WGtoLNuG-1Jets_PTG-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v1+NANOAODSIM",0.291367*1000,plotCategory("kPlotVG")),
       136: (dirT2+"2022/WWto4Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",1000000*(118.7*1.06-ggWWXS_LO_MCFM)*(1-0.1086*3)*(1-0.1086*3)*1000,plotCategory("kPlotNonPrompt")),
       137: (dirT2+"2022/GluGluHto2Tau_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",52.230*0.06272*1000,plotCategory("kPlotHiggs")),
       138: (dirT2+"2022/VBFHToTauTau_M125_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",4.0780*0.06272*1000,plotCategory("kPlotHiggs")),
       139: (dirT2+"2022/DYGto2LG-1Jets_MLL-4to50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",87.73210*1000,plotCategory("kPlotVG")),
       140: (dirT2+"2022/DYGto2LG-1Jets_MLL-4to50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.24095*1000,plotCategory("kPlotVG")),
       141: (dirT2+"2022/DYGto2LG-1Jets_MLL-4to50_PTG-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.02228*1000,plotCategory("kPlotVG")),
       142: (dirT2+"2022/TbarWplus_DR_AtLeastOneLepton_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",23.97*1000,plotCategory("kPlotTW")),
       143: (dirT2+"2022/TWminus_DR_AtLeastOneLepton_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",23.97*1000,plotCategory("kPlotTW")),
       144: (dirT2+"2022/VH_HtoNonbb_M-125_TuneCP5_13p6TeV_amcatnloFXFX-madspin-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v1+NANOAODSIM",(0.9439+1.4570)*(1-0.577)*1000,plotCategory("kPlotHiggs")),
       145: (dirT2+"2022/DYto2L-2Jets_MLL-50_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",5034.65*1000,plotCategory("kPlotDY")),
       146: (dirT2+"2022/DYto2L-2Jets_MLL-50_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",952.29*1000,plotCategory("kPlotDY")),
       147: (dirT2+"2022/DYto2L-2Jets_MLL-50_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",359.05*1000,plotCategory("kPlotDY")),
       148: (dirT2+"2022/TTLNu-1Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v1+NANOAODSIM",0.2502*1000,plotCategory("kPlotTVX")),
       149: (dirT2+"2022/TZQB-Zto2L-4FS_MLL-30_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.07968*0.70*1000,plotCategory("kPlotTVX")),
       150: (dirT2+"2022/VBS-SSWW_PolarizationLL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v1+NANOAODSIM",0.002190*1000,plotCategory("kPlotEWKSSWW")),
       151: (dirT2+"2022/VBS-SSWW_PolarizationTL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v3+NANOAODSIM",0.011700*1000,plotCategory("kPlotEWKSSWW")),
       152: (dirT2+"2022/VBS-SSWW_PolarizationTT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v1+NANOAODSIM",0.017635*1000,plotCategory("kPlotEWKSSWW")),
       153: (dirT2+"2022/GluGluHto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-jhugen752-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",52.230*0.2137*0.1086*0.1086*9*1000,plotCategory("kPlotHiggs")),
       154: (dirT2+"2022/VBFHto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-jhugen752-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",4.0780*0.2137*0.1086*0.1086*9*1000,plotCategory("kPlotHiggs")),
       155: (dirT2+"2022/TTHtoNon2B_M-125_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v4+NANOAODSIM",0.5700*(1-0.577)*1000,plotCategory("kPlotHiggs")),
       156: (dirT2+"2022/WGtoLNuG-1Jets_PTG-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v1+NANOAODSIM",0.022322*1000,plotCategory("kPlotVG")),
       157: (dirT2+"2022/WGtoLNuG-1Jets_PTG-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v3+NANOAODSIM",0.004918*1000,plotCategory("kPlotVG")),
       158: (dirT2+"2022/WW_DoubleScattering_TuneCP5_13p6TeV_pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",2.14891*1000,plotCategory("kPlotOther")),
       159: (dirT2+"2022/GluGlutoContinto2Zto4E_TuneCP5_13p6TeV_mcfm-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       160: (dirT2+"2022/GluGlutoContinto2Zto4Mu_TuneCP5_13p6TeV_mcfm-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       161: (dirT2+"2022/GluGlutoContinto2Zto4Tau_TuneCP5_13p6TeV_mcfm-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       162: (dirT2+"2022/GluGluToContinto2Zto2E2Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.0061150*1000,plotCategory("kPlotZZ")),
       163: (dirT2+"2022/GluGluToContinto2Zto2Mu2Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",0.0061150*1000,plotCategory("kPlotZZ")),
       164: (dirT2+"2022/GluGlutoContinto2Zto2E2Mu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v1+NANOAODSIM",0.0061150*1000,plotCategory("kPlotZZ")),
       165: (dirT2+"2022/GluGlutoContintoWWtoENuENu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       166: (dirT2+"2022/GluGlutoContintoWWtoENuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       167: (dirT2+"2022/GluGlutoContintoWWtoENuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       168: (dirT2+"2022/GluGlutoContintoWWtoMuNuENu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       169: (dirT2+"2022/GluGlutoContintoWWtoMuNuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       170: (dirT2+"2022/GluGlutoContintoWWtoMuNuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       171: (dirT2+"2022/GluGlutoContintoWWtoTauNuENu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       172: (dirT2+"2022/GluGlutoContintoWWtoTauNuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       173: (dirT2+"2022/GluGlutoContintoWWtoTauNuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       174: (dirT2+"2022/WWto2L2Nu-2Jets_OS_noTop_EW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM", 0.3301419*1000,plotCategory("kPlotqqWW")),
       175: (dirT2+"2022/WWto2L2Nu-2Jets_OS_noTop_QCD_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",2.6758028*1000,plotCategory("kPlotqqWW")),
       176: (dirT2+"2022/WWto2L2Nu-2Jets_SS_noTop_EW_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v3+NANOAODSIM",         0.0295255*1000,plotCategory("kPlotEWKSSWW")),
       177: (dirT2+"2022/WWto2L2Nu-2Jets_SS_noTop_QCD_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",        0.0279662*1000,plotCategory("kPlotQCDSSWW")),
       178: (dirT2+"2022/WZto3LNu-2Jets_EW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",           0.0429366*1000,plotCategory("kPlotEWKWZ")),
       179: (dirT2+"2022/WZto3LNu-2Jets_QCD_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",          0.4958618*1000*0.70,plotCategory("kPlotWZ")),
       180: (dirT2+"2022/ZZto2L2Nu-2Jets_EW_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",                  0.0051721*1000,plotCategory("kPlotZZ")),
       181: (dirT2+"2022/ZZto2L2Nu-2Jets_QCD_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",                 0.0912313*1000*1.40,plotCategory("kPlotZZ")),
       182: (dirT2+"2022/ZZto4L-2Jets_EW_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIM",                     0.0011422*1000,plotCategory("kPlotZZ")),
       183: (dirT2+"2022/ZZto4L-2Jets_QCD_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v3+NANOAODSIM",                    0.0202984*1000*1.40,plotCategory("kPlotZZ")),

       200: (dirT2+"2022EE/DYto2L-2Jets_MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",19982.5*1000,plotCategory("kPlotDY")),
       201: (dirT2+"2022EE/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",6345.99*1000,plotCategory("kPlotDY")),
       202: (dirT2+"2022EE/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",(118.7*1.06-ggWWXS_LO_MCFM)*0.1086*0.1086*9*1000,plotCategory("kPlotqqWW")),
       203: (dirT2+"2022EE/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",4.924*1.08*1000,plotCategory("kPlotWZ")),
       204: (dirT2+"2022EE/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",7.568*1.08*1000,plotCategory("kPlotWZ")),
       205: (dirT2+"2022EE/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",6.788*1.19*1000,plotCategory("kPlotZZ")),
       206: (dirT2+"2022EE/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",1.031*1.16*1000,plotCategory("kPlotZZ")),
       207: (dirT2+"2022EE/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",1.390*1.19*1000,plotCategory("kPlotZZ")),
       208: (dirT2+"2022EE/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.950*923.6*0.1086*0.1086*9*1000,plotCategory("kPlotTT")),
       209: (dirT2+"2022EE/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.950*923.6*0.1086*3*(1-0.1086*3)*2*1000,plotCategory("kPlotTT")),
       210: (dirT2+"2022EE/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",1000000*0.950*923.6*(1-0.1086*3)*(1-0.1086*3)*1000,plotCategory("kPlotNonPrompt")),
       211: (dirT2+"2022EE/TbarWplusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",4.67*1000,plotCategory("kPlotTW")),
       212: (dirT2+"2022EE/TWminusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",4.67*1000,plotCategory("kPlotTW")),
       213: (dirT2+"2022EE/WtoLNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",64481.58*1000,plotCategory("kPlotOther")),
       214: (dirT2+"2022EE/WWW_4F_TuneCP5_13p6TeV_amcatnlo-madspin-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.23280*1000,plotCategory("kPlotVVV")),
       215: (dirT2+"2022EE/WWZ_4F_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.18510*1000,plotCategory("kPlotVVV")),
       216: (dirT2+"2022EE/WZZ_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.06206*1000,plotCategory("kPlotVVV")),
       217: (dirT2+"2022EE/ZZZ_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.01591*1000,plotCategory("kPlotVVV")),
       218: (dirT2+"2022EE/WZGtoLNuZG_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.08425*1000,plotCategory("kPlotVVV")),
       219: (dirT2+"2022EE/TTWW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.0081651*1000,plotCategory("kPlotTVX")),
       220: (dirT2+"2022EE/TTZZ_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v3+NANOAODSIM",0.0015617*1000,plotCategory("kPlotTVX")),
       221: (dirT2+"2022EE/GluGluHtoZZto4L_M-125_TuneCP5_13p6TeV_powheg2-JHUGenV752-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",52.230*0.02619*0.101*0.101*1000,plotCategory("kPlotHiggs")),
       222: (dirT2+"2022EE/VBFHto2Zto4L_M125_TuneCP5_13p6TeV_powheg-jhugenv752-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",4.0780*0.02619*0.101*0.101*1000,plotCategory("kPlotHiggs")),
       223: (dirT2+"2022EE/TTLL_MLL-4to50_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.03949*1000,plotCategory("kPlotTVX")),
       224: (dirT2+"2022EE/TTLL_MLL-50_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.08646*1000,plotCategory("kPlotTVX")),
       225: (dirT2+"2022EE/ggWWto2L2Nu_OS_PolarizationLL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.24053*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       226: (dirT2+"2022EE/ggWWto2L2Nu_OS_PolarizationLT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.08268*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       227: (dirT2+"2022EE/ggWWto2L2Nu_OS_PolarizationTL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.08268*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       228: (dirT2+"2022EE/ggWWto2L2Nu_OS_PolarizationTT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",3.10724*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       229: (dirT2+"2022EE/DYGto2LG-1Jets_MLL-50_PTG-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",124.18762*1000,plotCategory("kPlotVG")),
       230: (dirT2+"2022EE/DYGto2LG-1Jets_MLL-50_PTG-50to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v1+NANOAODSIM",2.08977*1000,plotCategory("kPlotVG")),
       231: (dirT2+"2022EE/DYGto2LG-1Jets_MLL-50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.34767*1000,plotCategory("kPlotVG")),
       232: (dirT2+"2022EE/DYGto2LG-1Jets_MLL-50_PTG-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v4+NANOAODSIM",0.04734*1000,plotCategory("kPlotVG")),
       233: (dirT2+"2022EE/WGtoLNuG-1Jets_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",668.91538*1000,plotCategory("kPlotVG")),
       234: (dirT2+"2022EE/WGtoLNuG-1Jets_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",2.22141*1000,plotCategory("kPlotVG")),
       235: (dirT2+"2022EE/WGtoLNuG-1Jets_PTG-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v3+NANOAODSIM",0.291367*1000,plotCategory("kPlotVG")),
       236: (dirT2+"2022EE/WWto4Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",1000000*(118.7*1.06-ggWWXS_LO_MCFM)*(1-0.1086*3)*(1-0.1086*3)*1000,plotCategory("kPlotNonPrompt")),
       237: (dirT2+"2022EE/GluGluHto2Tau_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",52.230*0.06272*1000,plotCategory("kPlotHiggs")),
       238: (dirT2+"2022EE/VBFHToTauTau_M125_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",4.0780*0.06272*1000,plotCategory("kPlotHiggs")),
       239: (dirT2+"2022EE/DYGto2LG-1Jets_MLL-4to50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",87.73210*1000,plotCategory("kPlotVG")),
       240: (dirT2+"2022EE/DYGto2LG-1Jets_MLL-4to50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.24095*1000,plotCategory("kPlotVG")),
       241: (dirT2+"2022EE/DYGto2LG-1Jets_MLL-4to50_PTG-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.02228*1000,plotCategory("kPlotVG")),
       242: (dirT2+"2022EE/TbarWplus_DR_AtLeastOneLepton_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",23.97*1000,plotCategory("kPlotTW")),
       243: (dirT2+"2022EE/TWminus_DR_AtLeastOneLepton_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",23.97*1000,plotCategory("kPlotTW")),
       244: (dirT2+"2022EE/VH_HtoNonbb_M-125_TuneCP5_13p6TeV_amcatnloFXFX-madspin-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v1+NANOAODSIM",(0.9439+1.4570)*(1-0.577)*1000,plotCategory("kPlotHiggs")),
       245: (dirT2+"2022EE/DYto2L-2Jets_MLL-50_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",5034.65*1000,plotCategory("kPlotDY")),
       246: (dirT2+"2022EE/DYto2L-2Jets_MLL-50_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",952.29*1000,plotCategory("kPlotDY")),
       247: (dirT2+"2022EE/DYto2L-2Jets_MLL-50_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",359.05*1000,plotCategory("kPlotDY")),
       248: (dirT2+"2022EE/TTLNu-1Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v4+NANOAODSIM",0.2502*1000,plotCategory("kPlotTVX")),
       249: (dirT2+"2022EE/TZQB-Zto2L-4FS_MLL-30_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.07968*0.70*1000,plotCategory("kPlotTVX")),
       250: (dirT2+"2022EE/VBS-SSWW_PolarizationLL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v3+NANOAODSIM",0.002190*1000,plotCategory("kPlotEWKSSWW")),
       251: (dirT2+"2022EE/VBS-SSWW_PolarizationTL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v1+NANOAODSIM",0.011700*1000,plotCategory("kPlotEWKSSWW")),
       252: (dirT2+"2022EE/VBS-SSWW_PolarizationTT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v3+NANOAODSIM",0.017635*1000,plotCategory("kPlotEWKSSWW")),
       253: (dirT2+"2022EE/GluGluHto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-jhugen752-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",52.230*0.2137*0.1086*0.1086*9*1000,plotCategory("kPlotHiggs")),
       254: (dirT2+"2022EE/VBFHto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-jhugen752-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",4.0780*0.2137*0.1086*0.1086*9*1000,plotCategory("kPlotHiggs")),
       255: (dirT2+"2022EE/TTHtoNon2B_M-125_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.5700*(1-0.577)*1000,plotCategory("kPlotHiggs")),
       256: (dirT2+"2022EE/WGtoLNuG-1Jets_PTG-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v3+NANOAODSIM",0.022322*1000,plotCategory("kPlotVG")),
       257: (dirT2+"2022EE/WGtoLNuG-1Jets_PTG-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v3+NANOAODSIM",0.004918*1000,plotCategory("kPlotVG")),
       258: (dirT2+"2022EE/WW_DoubleScattering_TuneCP5_13p6TeV_pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",2.14891*1000,plotCategory("kPlotOther")),
       259: (dirT2+"2022EE/GluGlutoContinto2Zto4E_TuneCP5_13p6TeV_mcfm-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       260: (dirT2+"2022EE/GluGlutoContinto2Zto4Mu_TuneCP5_13p6TeV_mcfm-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       261: (dirT2+"2022EE/GluGlutoContinto2Zto4Tau_TuneCP5_13p6TeV_mcfm-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       262: (dirT2+"2022EE/GluGluToContinto2Zto2E2Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v4+NANOAODSIM",0.0061150*1000,plotCategory("kPlotZZ")),
       263: (dirT2+"2022EE/GluGluToContinto2Zto2Mu2Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v4+NANOAODSIM",0.0061150*1000,plotCategory("kPlotZZ")),
       264: (dirT2+"2022EE/GluGluToContinto2Zto2E2Mu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",0.0061150*1000,plotCategory("kPlotZZ")),
       265: (dirT2+"2022EE/GluGlutoContintoWWtoENuENu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       266: (dirT2+"2022EE/GluGlutoContintoWWtoENuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       267: (dirT2+"2022EE/GluGlutoContintoWWtoENuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       268: (dirT2+"2022EE/GluGlutoContintoWWtoMuNuENu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       269: (dirT2+"2022EE/GluGlutoContintoWWtoMuNuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       270: (dirT2+"2022EE/GluGlutoContintoWWtoMuNuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       271: (dirT2+"2022EE/GluGlutoContintoWWtoTauNuENu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       272: (dirT2+"2022EE/GluGlutoContintoWWtoTauNuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       273: (dirT2+"2022EE/GluGlutoContintoWWtoTauNuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       274: (dirT2+"2022EE/WWto2L2Nu-2Jets_OS_noTop_EW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM", 0.3301419*1000,plotCategory("kPlotqqWW")),
       275: (dirT2+"2022EE/WWto2L2Nu-2Jets_OS_noTop_QCD_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",2.6758028*1000,plotCategory("kPlotqqWW")),
       276: (dirT2+"2022EE/WWto2L2Nu-2Jets_SS_noTop_EW_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",         0.0295255*1000,plotCategory("kPlotEWKSSWW")),
       277: (dirT2+"2022EE/WWto2L2Nu-2Jets_SS_noTop_QCD_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",        0.0279662*1000,plotCategory("kPlotQCDSSWW")),
       278: (dirT2+"2022EE/WZto3LNu-2Jets_EW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",           0.0429366*1000,plotCategory("kPlotEWKWZ")),
       279: (dirT2+"2022EE/WZto3LNu-2Jets_QCD_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",          0.4958618*1000*0.70,plotCategory("kPlotWZ")),
       280: (dirT2+"2022EE/ZZto2L2Nu-2Jets_EW_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",                  0.0051721*1000,plotCategory("kPlotZZ")),
       281: (dirT2+"2022EE/ZZto2L2Nu-2Jets_QCD_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",                 0.0912313*1000*1.40,plotCategory("kPlotZZ")),
       282: (dirT2+"2022EE/ZZto4L-2Jets_EW_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIM",                     0.0011422*1000,plotCategory("kPlotZZ")),
       283: (dirT2+"2022EE/ZZto4L-2Jets_QCD_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v3+NANOAODSIM",                    0.0202984*1000*1.40,plotCategory("kPlotZZ")),

# Era C 2023, 20230
       300: (dirT2+"2023/DYto2L-2Jets_MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14_ext1-v3+NANOAODSIM",19982.5*1000,plotCategory("kPlotDY")),
       301: (dirT2+"2023/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v1+NANOAODSIM",6345.99*1000,plotCategory("kPlotDY")),
       302: (dirT2+"2023/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v4+NANOAODSIM",(118.7*1.06-ggWWXS_LO_MCFM)*0.1086*0.1086*9*1000,plotCategory("kPlotqqWW")),
       303: (dirT2+"2023/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2+NANOAODSIM",4.924*1.08*1000,plotCategory("kPlotWZ")),
       304: (dirT2+"2023/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3+NANOAODSIM",7.568*1.08*1000,plotCategory("kPlotWZ")),
       305: (dirT2+"2023/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v1+NANOAODSIM",6.788*1.19*1000,plotCategory("kPlotZZ")),
       306: (dirT2+"2023/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v1+NANOAODSIM",1.031*1.16*1000,plotCategory("kPlotZZ")),
       307: (dirT2+"2023/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3+NANOAODSIM",1.390*1.19*1000,plotCategory("kPlotZZ")),
       308: (dirT2+"2023/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2+NANOAODSIM",0.950*923.6*0.1086*0.1086*9*1000,plotCategory("kPlotTT")),
       309: (dirT2+"2023/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2+NANOAODSIM",0.950*923.6*0.1086*3*(1-0.1086*3)*2*1000,plotCategory("kPlotTT")),
       310: (dirT2+"2023/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-JMENano12p5_132X_mcRun3_2023_realistic_v5-v1+NANOAODSIM",1000000*0.950*923.6*(1-0.1086*3)*(1-0.1086*3)*1000,plotCategory("kPlotNonPrompt")),
       311: (dirT2+"2023/TbarWplusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v4+NANOAODSIM",4.67*1000,plotCategory("kPlotTW")),
       312: (dirT2+"2023/TWminusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2+NANOAODSIM",4.67*1000,plotCategory("kPlotTW")),
       313: (dirT2+"2023/WtoLNu-4Jets_TuneCP5_13p6TeV_madgraphMLM-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3+NANOAODSIM",64481.58*1000,plotCategory("kPlotOther")),
       314: (dirT2+"2023/WWW_4F_TuneCP5_13p6TeV_amcatnlo-madspin-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2+NANOAODSIM",0.23280*1000,plotCategory("kPlotVVV")),
       315: (dirT2+"2023/WWZ_4F_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2+NANOAODSIM",0.18510*1000,plotCategory("kPlotVVV")),
       316: (dirT2+"2023/WZZ_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2+NANOAODSIM",0.06206*1000,plotCategory("kPlotVVV")),
       317: (dirT2+"2023/ZZZ_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2+NANOAODSIM",0.01591*1000,plotCategory("kPlotVVV")),
       318: (dirT2+"2023/WZGtoLNuZG_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",0.08425*1000,plotCategory("kPlotVVV")),
       319: (dirT2+"2023/TTWW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",0.0081651*1000,plotCategory("kPlotTVX")),
       320: (dirT2+"2023/TTZZ_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v4+NANOAODSIM",0.0015617*1000,plotCategory("kPlotTVX")),
       321: (dirT2+"2023/GluGluHtoZZto4L_M-125_TuneCP5_13p6TeV_powheg-jhugen-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v3+NANOAODSIM",52.230*0.02619*0.101*0.101*1000,plotCategory("kPlotHiggs")),
       322: (dirT2+"2023/VBFHto2Zto4L_M-125_TuneCP5_13p6TeV_powheg-jhugen-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v3+NANOAODSIM",4.0780*0.02619*0.101*0.101*1000,plotCategory("kPlotHiggs")),
       323: (dirT2+"2023/TTLL_MLL-4to50_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",0.03949*1000,plotCategory("kPlotTVX")),
       324: (dirT2+"2023/TTLL_MLL-50_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",0.08646*1000,plotCategory("kPlotTVX")),
       325: (dirT2+"2023/ggWWto2L2Nu_OS_PolarizationLL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIMFAKE",0.24053*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       326: (dirT2+"2023/ggWWto2L2Nu_OS_PolarizationLT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIMFAKE",0.08268*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       327: (dirT2+"2023/ggWWto2L2Nu_OS_PolarizationTL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIMFAKE",0.08268*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       328: (dirT2+"2023/ggWWto2L2Nu_OS_PolarizationTT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIMFAKE",3.10724*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       329: (dirT2+"2023/DYGto2LG-1Jets_MLL-50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v4+NANOAODSIM",126.469425988806051*1000,plotCategory("kPlotVG")),
       330: (dirT2+"2023/DYGto2LG-1Jets_MLL-50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v3+NANOAODSIM",0.347454856033058*1000,plotCategory("kPlotVG")),
       331: (dirT2+"2023/DYGto2LG-1Jets_MLL-50_PTG-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v4+NANOAODSIM",0.043623155782532*1000,plotCategory("kPlotVG")),
       332: (dirT2+"2023/DYGto2LG-1Jets_MLL-50_PTG-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v4+NANOAODSIM",0.003152651247494*1000,plotCategory("kPlotVG")),
       333: (dirT2+"2023/WGtoLNuG-1Jets_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",668.91538*1000,plotCategory("kPlotVG")),
       334: (dirT2+"2023/WGtoLNuG-1Jets_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",2.22141*1000,plotCategory("kPlotVG")),
       335: (dirT2+"2023/WGtoLNuG-1Jets_PTG-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3+NANOAODSIM",0.291367*1000,plotCategory("kPlotVG")),
       336: (dirT2+"2023/WWto4Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v4+NANOAODSIM",1000000*(118.7*1.06-ggWWXS_LO_MCFM)*(1-0.1086*3)*(1-0.1086*3)*1000,plotCategory("kPlotNonPrompt")),
       337: (dirT2+"2023/GluGluHto2Tau_M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",52.230*0.06272*1000,plotCategory("kPlotHiggs")),
       338: (dirT2+"2023/VBFHToTauTau_M125_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",4.0780*0.06272*1000,plotCategory("kPlotHiggs")),
       339: (dirT2+"2023/DYGto2LG-1Jets_MLL-4to50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIMFAKE",87.73210*1000,plotCategory("kPlotVG")),
       340: (dirT2+"2023/DYGto2LG-1Jets_MLL-4to50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIMFAKE",0.24095*1000,plotCategory("kPlotVG")),
       341: (dirT2+"2023/DYGto2LG-1Jets_MLL-4to50_PTG-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIMFAKE",0.02228*1000,plotCategory("kPlotVG")),
       342: (dirT2+"2023/TbarWplus_DR_AtLeastOneLepton_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIMFAKE",23.97*1000,plotCategory("kPlotTW")),
       343: (dirT2+"2023/TWminus_DR_AtLeastOneLepton_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2+NANOAODSIMFAKE",23.97*1000,plotCategory("kPlotTW")),
       344: (dirT2+"2023/VH_HtoNonbb_M-125_TuneCP5_13p6TeV_amcatnloFXFX-madspin-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",(0.9439+1.4570)*(1-0.577)*1000,plotCategory("kPlotHiggs")),
       345: (dirT2+"2023/DYto2L-2Jets_MLL-50_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3+NANOAODSIM",5034.65*1000,plotCategory("kPlotDY")),
       346: (dirT2+"2023/DYto2L-2Jets_MLL-50_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3+NANOAODSIM",952.29*1000,plotCategory("kPlotDY")),
       347: (dirT2+"2023/DYto2L-2Jets_MLL-50_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3+NANOAODSIM",359.05*1000,plotCategory("kPlotDY")),
       348: (dirT2+"2023/TTLNu-1Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",0.2502*1000,plotCategory("kPlotTVX")),
       349: (dirT2+"2023/TZQB-Zto2L-4FS_MLL-30_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",0.07968*1.00*1000,plotCategory("kPlotTVX")),
       350: (dirT2+"2023/VBS-SSWW_PolarizationLL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v3+NANOAODSIM",0.002190*1000,plotCategory("kPlotEWKSSWW")),
       351: (dirT2+"2023/VBS-SSWW_PolarizationTL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v3+NANOAODSIM",0.011700*1000,plotCategory("kPlotEWKSSWW")),
       352: (dirT2+"2023/VBS-SSWW_PolarizationTT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v3+NANOAODSIM",0.017635*1000,plotCategory("kPlotEWKSSWW")),
       353: (dirT2+"2023/GluGluHto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-jhugen752-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",52.230*0.2137*0.1086*0.1086*9*1000,plotCategory("kPlotHiggs")),
       354: (dirT2+"2023/VBFHto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-jhugen752-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",4.0780*0.2137*0.1086*0.1086*9*1000,plotCategory("kPlotHiggs")),
       355: (dirT2+"2023/TTHtoNon2B_M-125_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v2+NANOAODSIM",0.5700*(1-0.577)*1000,plotCategory("kPlotHiggs")),
       356: (dirT2+"2023/WGtoLNuG-1Jets_PTG-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3+NANOAODSIM",0.022322*1000,plotCategory("kPlotVG")),
       357: (dirT2+"2023/WGtoLNuG-1Jets_PTG-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v14-v3+NANOAODSIM",0.004918*1000,plotCategory("kPlotVG")),
       358: (dirT2+"2023/WW_DoubleScattering_TuneCP5_13p6TeV_pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",2.14891*1000,plotCategory("kPlotOther")),
       359: (dirT2+"2023/GluGlutoContinto2Zto4E_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v3+NANOAODSIM",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       360: (dirT2+"2023/GluGlutoContinto2Zto4Mu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v3+NANOAODSIM",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       361: (dirT2+"2023/GluGlutoContinto2Zto4Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v3+NANOAODSIM",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       362: (dirT2+"2023/GluGlutoContinto2Zto2E2Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v3+NANOAODSIM",0.0061150*1000,plotCategory("kPlotZZ")),
       363: (dirT2+"2023/GluGlutoContinto2Zto2Mu2Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v3+NANOAODSIM",0.0061150*1000,plotCategory("kPlotZZ")),
       364: (dirT2+"2023/GluGluToContinto2Zto2E2Mu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",0.0061150*1000,plotCategory("kPlotZZ")),
       365: (dirT2+"2023/GluGlutoContintoWWtoENuENu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       366: (dirT2+"2023/GluGlutoContintoWWtoENuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       367: (dirT2+"2023/GluGlutoContintoWWtoENuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       368: (dirT2+"2023/GluGlutoContintoWWtoMuNuENu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       369: (dirT2+"2023/GluGlutoContintoWWtoMuNuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       370: (dirT2+"2023/GluGlutoContintoWWtoMuNuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       371: (dirT2+"2023/GluGlutoContintoWWtoTauNuENu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       372: (dirT2+"2023/GluGlutoContintoWWtoTauNuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       373: (dirT2+"2023/GluGlutoContintoWWtoTauNuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       374: (dirT2+"2023/WWto2L2Nu-2Jets_OS_noTop_EW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM", 0.3301419*1000,plotCategory("kPlotqqWW")),
       375: (dirT2+"2023/WWto2L2Nu-2Jets_OS_noTop_QCD_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",2.6758028*1000,plotCategory("kPlotqqWW")),
       376: (dirT2+"2023/WWto2L2Nu-2Jets_SS_noTop_EW_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",         0.0295255*1000,plotCategory("kPlotEWKSSWW")),
       377: (dirT2+"2023/WWto2L2Nu-2Jets_SS_noTop_QCD_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",        0.0279662*1000,plotCategory("kPlotQCDSSWW")),
       378: (dirT2+"2023/WZto3LNu-2Jets_EW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",           0.0429366*1000,plotCategory("kPlotEWKWZ")),
       379: (dirT2+"2023/WZto3LNu-2Jets_QCD_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v1+NANOAODSIM",          0.4958618*1000*0.70,plotCategory("kPlotWZ")),
       380: (dirT2+"2023/ZZto2L2Nu-2Jets_EW_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",                  0.0051721*1000,plotCategory("kPlotZZ")),
       381: (dirT2+"2023/ZZto2L2Nu-2Jets_QCD_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",                 0.0912313*1000,plotCategory("kPlotZZ")),
       382: (dirT2+"2023/ZZto4L-2Jets_EW_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",                     0.0011422*1000,plotCategory("kPlotZZ")),
       383: (dirT2+"2023/ZZto4L-2Jets_QCD_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_v15-v2+NANOAODSIM",                    0.0202984*1000,plotCategory("kPlotZZ")),

       400: (dirT2+"2023/DYto2L-2Jets_MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2_ext1-v3+NANOAODSIM",19982.5*1000,plotCategory("kPlotDY")),
       401: (dirT2+"2023/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",6345.99*1000,plotCategory("kPlotDY")),
       402: (dirT2+"2023/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",(118.7*1.06-ggWWXS_LO_MCFM)*0.1086*0.1086*9*1000,plotCategory("kPlotqqWW")),
       403: (dirT2+"2023/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v2+NANOAODSIM",4.924*1.08*1000,plotCategory("kPlotWZ")),
       404: (dirT2+"2023/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v2+NANOAODSIM",7.568*1.08*1000,plotCategory("kPlotWZ")),
       405: (dirT2+"2023/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",6.788*1.19*1000,plotCategory("kPlotZZ")),
       406: (dirT2+"2023/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v1+NANOAODSIM",1.031*1.16*1000,plotCategory("kPlotZZ")),
       407: (dirT2+"2023/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",1.390*1.19*1000,plotCategory("kPlotZZ")),
       408: (dirT2+"2023/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",0.950*923.6*0.1086*0.1086*9*1000,plotCategory("kPlotTT")),
       409: (dirT2+"2023/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",0.950*923.6*0.1086*3*(1-0.1086*3)*2*1000,plotCategory("kPlotTT")),
       410: (dirT2+"2023/TTto4Q_TuneCP5Up_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",1000000*0.950*923.6*(1-0.1086*3)*(1-0.1086*3)*1000,plotCategory("kPlotNonPrompt")),
       411: (dirT2+"2023/TbarWplusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",4.67*1000,plotCategory("kPlotTW")),
       412: (dirT2+"2023/TWminusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",4.67*1000,plotCategory("kPlotTW")),
       413: (dirT2+"2023/WtoLNu-4Jets_TuneCP5_13p6TeV_madgraphMLM-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",64481.58*1000,plotCategory("kPlotOther")),
       414: (dirT2+"2023/WWW_4F_TuneCP5_13p6TeV_amcatnlo-madspin-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v2+NANOAODSIM",0.23280*1000,plotCategory("kPlotVVV")),
       415: (dirT2+"2023/WWZ_4F_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",0.18510*1000,plotCategory("kPlotVVV")),
       416: (dirT2+"2023/WZZ_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v2+NANOAODSIM",0.06206*1000,plotCategory("kPlotVVV")),
       417: (dirT2+"2023/ZZZ_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v2+NANOAODSIM",0.01591*1000,plotCategory("kPlotVVV")),
       418: (dirT2+"2023/WZGtoLNuZG_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.08425*1000,plotCategory("kPlotVVV")),
       419: (dirT2+"2023/TTWW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.0081651*1000,plotCategory("kPlotTVX")),
       420: (dirT2+"2023/TTZZ_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.0015617*1000,plotCategory("kPlotTVX")),
       421: (dirT2+"2023/GluGluHtoZZto4L_M-125_TuneCP5_13p6TeV_powheg-jhugen-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",52.230*0.02619*0.101*0.101*1000,plotCategory("kPlotHiggs")),
       422: (dirT2+"2023/VBFHto2Zto4L_M-125_TuneCP5_13p6TeV_powheg-jhugen-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",4.0780*0.02619*0.101*0.101*1000,plotCategory("kPlotHiggs")),
       423: (dirT2+"2023/TTLL_MLL-4to50_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.03949*1000,plotCategory("kPlotTVX")),
       424: (dirT2+"2023/TTLL_MLL-50_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.08646*1000,plotCategory("kPlotTVX")),
       425: (dirT2+"2023/ggWWto2L2Nu_OS_PolarizationLL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIMFAKE",0.24053*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       426: (dirT2+"2023/ggWWto2L2Nu_OS_PolarizationLT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIMFAKE",0.08268*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       427: (dirT2+"2023/ggWWto2L2Nu_OS_PolarizationTL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIMFAKE",0.08268*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       428: (dirT2+"2023/ggWWto2L2Nu_OS_PolarizationTT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIMFAKE",3.10724*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*1.4*1000,plotCategory("kPlotggWW")),
       429: (dirT2+"2023/DYGto2LG-1Jets_MLL-50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",126.469425988806051*1000,plotCategory("kPlotVG")),
       430: (dirT2+"2023/DYGto2LG-1Jets_MLL-50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v3+NANOAODSIM",0.347454856033058*1000,plotCategory("kPlotVG")),
       431: (dirT2+"2023/DYGto2LG-1Jets_MLL-50_PTG-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.043623155782532*1000,plotCategory("kPlotVG")),
       432: (dirT2+"2023/DYGto2LG-1Jets_MLL-50_PTG-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.003152651247494*1000,plotCategory("kPlotVG")),
       433: (dirT2+"2023/WGtoLNuG-1Jets_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",668.91538*1000,plotCategory("kPlotVG")),
       434: (dirT2+"2023/WGtoLNuG-1Jets_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",2.22141*1000,plotCategory("kPlotVG")),
       435: (dirT2+"2023/WGtoLNuG-1Jets_PTG-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",0.291367*1000,plotCategory("kPlotVG")),
       436: (dirT2+"2023/WWto4Q_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",1000000*(118.7*1.06-ggWWXS_LO_MCFM)*(1-0.1086*3)*(1-0.1086*3)*1000,plotCategory("kPlotNonPrompt")),
       437: (dirT2+"2023/GluGluHToTauTau_M-125_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v2+NANOAODSIM",52.230*0.06272*1000,plotCategory("kPlotHiggs")),
       438: (dirT2+"2023/VBFHToTauTau_M125_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",4.0780*0.06272*1000,plotCategory("kPlotHiggs")),
       439: (dirT2+"2023/DYGto2LG-1Jets_MLL-4to50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIMFAKE",87.73210*1000,plotCategory("kPlotVG")),
       440: (dirT2+"2023/DYGto2LG-1Jets_MLL-4to50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIMFAKE",0.24095*1000,plotCategory("kPlotVG")),
       441: (dirT2+"2023/DYGto2LG-1Jets_MLL-4to50_PTG-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIMFAKE",0.02228*1000,plotCategory("kPlotVG")),
       442: (dirT2+"2023/TbarWplus_DR_AtLeastOneLepton_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIMFAKE",23.97*1000,plotCategory("kPlotTW")),
       443: (dirT2+"2023/TWminus_DR_AtLeastOneLepton_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIMFAKE",23.97*1000,plotCategory("kPlotTW")),
       444: (dirT2+"2023/VH_HtoNonbb_M-125_TuneCP5_13p6TeV_amcatnloFXFX-madspin-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",(0.9439+1.4570)*(1-0.577)*1000,plotCategory("kPlotHiggs")),
       445: (dirT2+"2023/DYto2L-2Jets_MLL-50_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",5034.65*1000,plotCategory("kPlotDY")),
       446: (dirT2+"2023/DYto2L-2Jets_MLL-50_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",952.29*1000,plotCategory("kPlotDY")),
       447: (dirT2+"2023/DYto2L-2Jets_MLL-50_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",359.05*1000,plotCategory("kPlotDY")),
       448: (dirT2+"2023/TTLNu-1Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.2502*1000,plotCategory("kPlotTVX")),
       449: (dirT2+"2023/TZQB-Zto2L-4FS_MLL-30_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v3+NANOAODSIM",0.07968*1.00*1000,plotCategory("kPlotTVX")),
       450: (dirT2+"2023/VBS-SSWW_PolarizationLL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.002190*1000,plotCategory("kPlotEWKSSWW")),
       451: (dirT2+"2023/VBS-SSWW_PolarizationTL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.011700*1000,plotCategory("kPlotEWKSSWW")),
       452: (dirT2+"2023/VBS-SSWW_PolarizationTT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.017635*1000,plotCategory("kPlotEWKSSWW")),
       453: (dirT2+"2023/GluGluHto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-jhugen752-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",52.230*0.2137*0.1086*0.1086*9*1000,plotCategory("kPlotHiggs")),
       454: (dirT2+"2023/VBFHto2Wto2L2Nu_M-125_TuneCP5_13p6TeV_powheg-jhugen752-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",4.0780*0.2137*0.1086*0.1086*9*1000,plotCategory("kPlotHiggs")),
       455: (dirT2+"2023/TTHtoNon2B_M-125_TuneCP5_13p6TeV_powheg-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v2+NANOAODSIM",0.5700*(1-0.577)*1000,plotCategory("kPlotHiggs")),
       456: (dirT2+"2023/WGtoLNuG-1Jets_PTG-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",0.022322*1000,plotCategory("kPlotVG")),
       457: (dirT2+"2023/WGtoLNuG-1Jets_PTG-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIM",0.004918*1000,plotCategory("kPlotVG")),
       458: (dirT2+"2023/WW_DoubleScattering_TuneCP5_13p6TeV_pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",2.14891*1000,plotCategory("kPlotOther")),
       459: (dirT2+"2023/GluGlutoContinto2Zto4E_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       460: (dirT2+"2023/GluGlutoContinto2Zto4Mu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       461: (dirT2+"2023/GluGlutoContinto2Zto4Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       462: (dirT2+"2023/GluGlutoContinto2Zto2E2Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.0061150*1000,plotCategory("kPlotZZ")),
       463: (dirT2+"2023/GluGlutoContinto2Zto2Mu2Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.0061150*1000,plotCategory("kPlotZZ")),
       464: (dirT2+"2023/GluGluToContinto2Zto2E2Mu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",0.0061150*1000,plotCategory("kPlotZZ")),
       465: (dirT2+"2023/GluGlutoContintoWWtoENuENu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       466: (dirT2+"2023/GluGlutoContintoWWtoENuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       467: (dirT2+"2023/GluGlutoContintoWWtoENuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       468: (dirT2+"2023/GluGlutoContintoWWtoMuNuENu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       469: (dirT2+"2023/GluGlutoContintoWWtoMuNuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       470: (dirT2+"2023/GluGlutoContintoWWtoMuNuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       471: (dirT2+"2023/GluGlutoContintoWWtoTauNuENu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       472: (dirT2+"2023/GluGlutoContintoWWtoTauNuMuNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       473: (dirT2+"2023/GluGlutoContintoWWtoTauNuTauNu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       474: (dirT2+"2023/WWto2L2Nu-2Jets_OS_noTop_EW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v1+NANOAODSIM", 0.3301419*1000,plotCategory("kPlotqqWW")),
       475: (dirT2+"2023/WWto2L2Nu-2Jets_OS_noTop_QCD_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",2.6758028*1000,plotCategory("kPlotqqWW")),
       476: (dirT2+"2023/WWto2L2Nu-2Jets_SS_noTop_EW_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",         0.0295255*1000,plotCategory("kPlotEWKSSWW")),
       477: (dirT2+"2023/WWto2L2Nu-2Jets_SS_noTop_QCD_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",        0.0279662*1000,plotCategory("kPlotQCDSSWW")),
       478: (dirT2+"2023/WZto3LNu-2Jets_EW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",           0.0429366*1000,plotCategory("kPlotEWKWZ")),
       479: (dirT2+"2023/WZto3LNu-2Jets_QCD_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",          0.4958618*1000*0.70,plotCategory("kPlotWZ")),
       480: (dirT2+"2023/ZZto2L2Nu-2Jets_EW_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",                  0.0051721*1000,plotCategory("kPlotZZ")),
       481: (dirT2+"2023/ZZto2L2Nu-2Jets_QCD_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",                 0.0912313*1000,plotCategory("kPlotZZ")),
       482: (dirT2+"2023/ZZto4L-2Jets_EW_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",                     0.0011422*1000,plotCategory("kPlotZZ")),
       483: (dirT2+"2023/ZZto4L-2Jets_QCD_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIM",                    0.0202984*1000,plotCategory("kPlotZZ")),


       500: (dirT2+"2024/DYto2E_Bin-MLL-10to50_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",19982.5*1000/3.,plotCategory("kPlotDY")),
       501: (dirT2+"2024/DYto2E-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v4+NANOAODSIM",6345.99*1000/3.,plotCategory("kPlotDY")),
       502: (dirT2+"2024/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(118.7*1.06-ggWWXS_LO_MCFM)*0.1086*0.1086*9*1000,plotCategory("kPlotqqWW")),
       503: (dirT2+"2024/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",4.924*1.08*1000,plotCategory("kPlotWZ")),
       504: (dirT2+"2024/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",7.568*1.08*1000,plotCategory("kPlotWZ")),
       505: (dirT2+"2024/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",6.788*1.19*1000,plotCategory("kPlotZZ")),
       506: (dirT2+"2024/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",1.031*1.16*1000,plotCategory("kPlotZZ")),
       507: (dirT2+"2024/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",1.390*1.19*1000,plotCategory("kPlotZZ")),
       508: (dirT2+"2024/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3+NANOAODSIM",0.950*923.6*0.1086*0.1086*9*1000,plotCategory("kPlotTT")),
       509: (dirT2+"2024/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",0.950*923.6*0.1086*3*(1-0.1086*3)*2*1000,plotCategory("kPlotTT")),
       510: (dirT2+"2024/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",1000000*0.950*923.6*(1-0.1086*3)*(1-0.1086*3)*1000,plotCategory("kPlotNonPrompt")),
       511: (dirT2+"2024/TbarWplusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",4.67*1000,plotCategory("kPlotTW")),
       512: (dirT2+"2024/TWminusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",4.67*1000,plotCategory("kPlotTW")),
       513: (dirT2+"2024/WtoENu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3+NANOAODSIM",64481.58*1000/3.,plotCategory("kPlotOther")),
       514: (dirT2+"2024/WWW-4F_TuneCP5_13p6TeV_amcatnlo-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",0.23280*1000,plotCategory("kPlotVVV")),
       515: (dirT2+"2024/WWZ-4F_TuneCP5_13p6TeV_amcatnlo-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",0.18510*1000,plotCategory("kPlotVVV")),
       516: (dirT2+"2024/WZZ-5F_TuneCP5_13p6TeV_amcatnlo-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",0.06206*1000,plotCategory("kPlotVVV")),
       517: (dirT2+"2024/ZZZ-5F_TuneCP5_13p6TeV_amcatnlo-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",0.01591*1000,plotCategory("kPlotVVV")),
       518: (dirT2+"2024/WZGtoLNuZG_TuneCP5_13p6TeV_amcatnlo-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",0.08425*1000,plotCategory("kPlotVVV")),
       519: (dirT2+"2024/TTWW_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.0081651*1000,plotCategory("kPlotTVX")),
       520: (dirT2+"2024/TTZZ_TuneCP5_13p6TeV_madgraph-madspin-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.0015617*1000,plotCategory("kPlotTVX")),
       521: (dirT2+"2024/GluGluHto2Zto4L_Par-M-125_TuneCP5_13p6TeV_powhegMINNLO-jhugen-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",52.230*0.02619*0.101*0.101*1000,plotCategory("kPlotHiggs")),
       522: (dirT2+"2024/VBFH-Hto2Zto4L_Par-M-125_TuneCP5_13p6TeV_powheg-jhugen-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",4.0780*0.02619*0.101*0.101*1000,plotCategory("kPlotHiggs")),
       523: (dirT2+"2024/TTLL_MLL-4to50_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.03949*1000,plotCategory("kPlotTVX")),
       524: (dirT2+"2024/TTLL_MLL-50_TuneCP5_13p6TeV_amcatnlo-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.08646*1000,plotCategory("kPlotTVX")),
       525: (dirT2+"2024/DYto2Mu_Bin-MLL-10to50_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",19982.5*1000/3.,plotCategory("kPlotDY")),
       526: (dirT2+"2024/DYto2Mu-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v6+NANOAODSIM",6345.99*1000/3.,plotCategory("kPlotDY")),
       527: (dirT2+"2024/DYto2Tau_Bin-MLL-10to50_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",19982.5*1000/3.,plotCategory("kPlotDY")),
       528: (dirT2+"2024/DYto2Tau-2Jets_Bin-MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v5+NANOAODSIM",6345.99*1000/3.,plotCategory("kPlotDY")),
       529: (dirT2+"2024/DYGto2LG-1Jets_MLL-50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",126.469425988806051*1000,plotCategory("kPlotVG")),
       530: (dirT2+"2024/DYGto2LG-1Jets_MLL-50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v3+NANOAODSIMFAKE",0.347454856033058*1000,plotCategory("kPlotVG")),
       531: (dirT2+"2024/DYGto2LG-1Jets_MLL-50_PTG-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.043623155782532*1000,plotCategory("kPlotVG")),
       532: (dirT2+"2024/DYGto2LG-1Jets_MLL-50_PTG-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.003152651247494*1000,plotCategory("kPlotVG")),
       533: (dirT2+"2024/WGtoLNuG-1Jets_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",668.91538*1000,plotCategory("kPlotVG")),
       534: (dirT2+"2024/WGtoLNuG-1Jets_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",2.22141*1000,plotCategory("kPlotVG")),
       535: (dirT2+"2024/WGtoLNuG-1Jets_PTG-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIMFAKE",0.291367*1000,plotCategory("kPlotVG")),
       536: (dirT2+"2024/WWto4Q_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",1000000*(118.7*1.06-ggWWXS_LO_MCFM)*(1-0.1086*3)*(1-0.1086*3)*1000,plotCategory("kPlotNonPrompt")),
       537: (dirT2+"2024/GluGluH-HTo2Tau_Par-M-125_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",52.230*0.06272*1000,plotCategory("kPlotHiggs")),
       538: (dirT2+"2024/VBFH-HTo2Tau_Par-M-125_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",4.0780*0.06272*1000,plotCategory("kPlotHiggs")),
       539: (dirT2+"2024/DYGto2LG-1Jets_MLL-4to50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIMFAKE",87.73210*1000,plotCategory("kPlotVG")),
       540: (dirT2+"2024/DYGto2LG-1Jets_MLL-4to50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIMFAKE",0.24095*1000,plotCategory("kPlotVG")),
       541: (dirT2+"2024/DYGto2LG-1Jets_MLL-4to50_PTG-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_postEE_v6-v2+NANOAODSIMFAKE",0.02228*1000,plotCategory("kPlotVG")),
       542: (dirT2+"2024/WtoMuNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3+NANOAODSIM",64481.58*1000/3.,plotCategory("kPlotOther")),
       543: (dirT2+"2024/WtoTauNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v3+NANOAODSIM",64481.58*1000/3.,plotCategory("kPlotOther")),
       544: (dirT2+"2024/VH_HtoNonbb_M-125_TuneCP5_13p6TeV_amcatnloFXFX-madspin-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",(0.9439+1.4570)*(1-0.577)*1000,plotCategory("kPlotHiggs")),
       545: (dirT2+"2024/DYto2L-2Jets_MLL-50_0J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIMFAKE",5034.65*1000,plotCategory("kPlotDY")),
       546: (dirT2+"2024/DYto2L-2Jets_MLL-50_1J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIMFAKE",952.29*1000,plotCategory("kPlotDY")),
       547: (dirT2+"2024/DYto2L-2Jets_MLL-50_2J_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIMFAKE",359.05*1000,plotCategory("kPlotDY")),
       548: (dirT2+"2024/TTLNu-1Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.2502*1000,plotCategory("kPlotTVX")),
       549: (dirT2+"2024/TZQB-ZtoLL-TtoL-CPV_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.07968*0.70*1000,plotCategory("kPlotTVX")),
       550: (dirT2+"2024/VBS-SSWW_PolarizationLL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.002190*1000,plotCategory("kPlotEWKSSWW")),
       551: (dirT2+"2024/VBS-SSWW_PolarizationTL_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.011700*1000,plotCategory("kPlotEWKSSWW")),
       552: (dirT2+"2024/VBS-SSWW_PolarizationTT_TuneCP5_13p6TeV_madgraph-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.017635*1000,plotCategory("kPlotEWKSSWW")),
       553: (dirT2+"2024/GluGluHto2Wto2L2Nu_Par-M-125_TuneCP5_13p6TeV_powheg-jhugen-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",52.230*0.2137*0.1086*0.1086*9*1000,plotCategory("kPlotHiggs")),
       554: (dirT2+"2024/VBFHto2Wto2L2Nu_Par-M-125_TuneCP5_13p6TeV_powheg-jhugen-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",4.0780*0.2137*0.1086*0.1086*9*1000,plotCategory("kPlotHiggs")),
       555: (dirT2+"2024/TTH-HtoNon2B_Par-M-125_TuneCP5_13p6TeV_powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",0.5700*(1-0.577)*1000,plotCategory("kPlotHiggs")),
       556: (dirT2+"2024/WGtoLNuG-1Jets_PTG-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIMFAKE",0.022322*1000,plotCategory("kPlotVG")),
       557: (dirT2+"2024/WGtoLNuG-1Jets_PTG-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v2-v3+NANOAODSIMFAKE",0.004918*1000,plotCategory("kPlotVG")),
       558: (dirT2+"2024/WW-DPS_TuneCP5_13p6TeV_pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",2.14891*1000,plotCategory("kPlotOther")),
       559: (dirT2+"2024/GluGlutoContinto2Zto4E_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       560: (dirT2+"2024/GluGlutoContinto2Zto4Mu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       561: (dirT2+"2024/GluGlutoContinto2Zto4Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.5*0.0061150*1000,plotCategory("kPlotZZ")),
       562: (dirT2+"2024/GluGlutoContinto2Zto2E2Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.0061150*1000,plotCategory("kPlotZZ")),
       563: (dirT2+"2024/GluGlutoContinto2Zto2Mu2Tau_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.0061150*1000,plotCategory("kPlotZZ")),
       564: (dirT2+"2024/GluGluToContinto2Zto2E2Mu_TuneCP5_13p6TeV_mcfm701-pythia8+Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_postBPix_v6-v2+NANOAODSIMFAKE",0.0061150*1000,plotCategory("kPlotZZ")),
       565: (dirT2+"2024/GluGluWWto2E2Nu_TuneCP5_13p6TeV_mcfm-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       566: (dirT2+"2024/GluGluWWtoENuMuNu_TuneCP5_13p6TeV_mcfm-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       567: (dirT2+"2024/GluGluWWtoENuTauNu_TuneCP5_13p6TeV_mcfm-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       568: (dirT2+"2024/GluGluWWtoMuNuENu_TuneCP5_13p6TeV_mcfm-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       569: (dirT2+"2024/GluGluWWto2Mu2Nu_TuneCP5_13p6TeV_mcfm-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       570: (dirT2+"2024/GluGluWWtoMuNuTauNu_TuneCP5_13p6TeV_mcfm-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       571: (dirT2+"2024/GluGluWWtoTauNuENu_TuneCP5_13p6TeV_mcfm-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       572: (dirT2+"2024/GluGluWWtoTauNuMuNu_TuneCP5_13p6TeV_mcfm-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       573: (dirT2+"2024/GluGluWWto2Tau2Nu_TuneCP5_13p6TeV_mcfm-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(0.1086*0.1086)*ggWWXS_LO_MCFM*1.4*1000,plotCategory("kPlotggWW")),
       574: (dirT2+"2024/WWJJto2L2Nu-OS-noTop-EWK_TuneCP5_13p6TeV_madgraph-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",                         0.3301419*1000,plotCategory("kPlotqqWW")),
       575: (dirT2+"2024/WWJJto2L2Nu-OS-noTop-QCD_TuneCP5_13p6TeV_madgraph-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",                         2.6758028*1000,plotCategory("kPlotqqWW")),
       576: (dirT2+"2024/WWJJto2L2Nu-SS-noTop-EWK_TuneCP5_13p6TeV_madgraph-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",                         0.0295255*1000,plotCategory("kPlotEWKSSWW")),
       577: (dirT2+"2024/WWJJto2L2Nu-SS-noTop-QCD_TuneCP5_13p6TeV_madgraph-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",                         0.0279662*1000,plotCategory("kPlotQCDSSWW")),
       578: (dirT2+"2024/WZJJto3LNu-EWK_TuneCP5_13p6TeV_madgraph-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",                                   0.0429366*1000,plotCategory("kPlotEWKWZ")),
       579: (dirT2+"2024/WZJJto3LNu-QCD_TuneCP5_13p6TeV_madgraph-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",                                   0.4958618*1000*0.70,plotCategory("kPlotWZ")),
       580: (dirT2+"2024/ZZJJto2L2Nu-EWK_TuneCP5_13p6TeV_madgraph-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",                                  0.0051721*1000,plotCategory("kPlotZZ")),
       581: (dirT2+"2024/ZZJJto2L2Nu-QCD_TuneCP5_13p6TeV_madgraph-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",                                  0.0912313*1000*1.40,plotCategory("kPlotZZ")),
       582: (dirT2+"2024/ZZJJto4L-EWK_TuneCP5_13p6TeV_madgraph-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",                                     0.0011422*1000,plotCategory("kPlotZZ")),
       583: (dirT2+"2024/ZZJJto4L-QCD_TuneCP5_13p6TeV_madgraph-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",                                     0.0202984*1000*1.40,plotCategory("kPlotZZ")),
       584: (dirT2+"2024/WpWpJJ-EWK_TuneCP5_13p6TeV-powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",0.5*0.0295255*1000,plotCategory("kPlotEWKSSWW")),
       585: (dirT2+"2024/WmWmJJ-EWK_TuneCP5_13p6TeV-powheg-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",0.5*0.0295255*1000,plotCategory("kPlotEWKSSWW")),
       586: (dirT2+"2024/ZH-HtoNon2B_Par-M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(0.9439)*(1-0.577)*1000,plotCategory("kPlotHiggs")),
       587: (dirT2+"2024/WplusH-HtoNon2B_Par-M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(1.4570*0.608)*(1-0.577)*1000,plotCategory("kPlotHiggs")),
       588: (dirT2+"2024/WminusH-HtoNon2B_Par-M-125_TuneCP5_13p6TeV_amcatnloFXFX-pythia8+RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2-v2+NANOAODSIM",(1.4570*0.392)*(1-0.577)*1000,plotCategory("kPlotHiggs")),

       900:(dirLocal+"/2018/vbf-hrhogamma-powheg+NANOAOD_01",1.0*1000,plotCategory("kPlotBSM")),

       901:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/DY_MLM_2022_preEE",6345.99*1000,plotCategory("kPlotDY")),
       902:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/DY_2022_preEE",6345.99*1000,plotCategory("kPlotDY")),
       903:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/DY_2022_postEE",6345.99*1000,plotCategory("kPlotDY")),
       904:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/DY_2023_partA",6345.99*1000,plotCategory("kPlotDY")),
       905:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/DY_2023_partB",6345.99*1000,plotCategory("kPlotDY")),

       906:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/TTto2L2Nu_2022_postEE",0.950*923.6*0.1086*0.1086*9*1000,plotCategory("kPlotTT")),
       907:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/TWminusto2L2Nu_2022_postEE",23.97*1000*2.0,plotCategory("kPlotTW")),

       960:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/qqWW_2018",(118.7-3.974)*0.1086*0.1086*9*1000,plotCategory("kPlotqqWW")),

       961:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/qqWW_2022_postEE",(118.7*1.06-ggWWXS_LO_MCFM)*0.1086*0.1086*9*1000,plotCategory("kPlotqqWW")),

       962:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/GluGlutoContintoWWtoENuENu_postEE"    ,(0.1086*0.1086)*ggWWXS_LO_MCFM*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),
       963:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/GluGlutoContintoWWtoENuMuNu_postEE"   ,(0.1086*0.1086)*ggWWXS_LO_MCFM*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),
       964:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/GluGlutoContintoWWtoENuTauNu_postEE"  ,(0.1086*0.1086)*ggWWXS_LO_MCFM*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),
       965:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/GluGlutoContintoWWtoMuNuENu_postEE"   ,(0.1086*0.1086)*ggWWXS_LO_MCFM*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),
       966:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/GluGlutoContintoWWtoMuNuMuNu_postEE"  ,(0.1086*0.1086)*ggWWXS_LO_MCFM*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),
       967:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/GluGlutoContintoWWtoMuNuTauNu_postEE" ,(0.1086*0.1086)*ggWWXS_LO_MCFM*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),
       968:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/GluGlutoContintoWWtoTauNuENu_postEE"  ,(0.1086*0.1086)*ggWWXS_LO_MCFM*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),
       969:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/GluGlutoContintoWWtoTauNuMuNu_postEE" ,(0.1086*0.1086)*ggWWXS_LO_MCFM*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),
       970:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/GluGlutoContintoWWtoTauNuTauNu_postEE",(0.1086*0.1086)*ggWWXS_LO_MCFM*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),

       971:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/ggWWto2L2Nu_OS_PolarizationLL_postEE",0.24053*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),
       972:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/ggWWto2L2Nu_OS_PolarizationLT_postEE",0.08268*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),
       973:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/ggWWto2L2Nu_OS_PolarizationTL_postEE",0.08268*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),
       974:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/ggWWto2L2Nu_OS_PolarizationTT_postEE",3.10724*(ggWWXS_LO_MCFM/ggWWXS_LO_MADGRAPH)*ggWWXS_kFactor*1000,plotCategory("kPlotggWW")),

       975:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/WW_MINNLO_13p0TeV",(118.7-3.974)*0.1086*0.1086*9*1000,plotCategory("kPlotqqWW")),

       976:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/WW_MINNLO_13p6TeV",12.80173*1000,plotCategory("kPlotqqWW")),

       977:("/ceph/submit/data/group/cms/store/user/ceballos/test_samples/WZ3l_2022_postEE",4.924*1.08*1000,plotCategory("kPlotWZ")),

       978:("/ceph/submit/data/user/c/ceballos/test_samples/WpWpJJ-EWK_TuneCP5_13p6TeV-powheg-pythia8",0.5*0.0295255*1000,plotCategory("kPlotEWKSSWW")),
       979:("/ceph/submit/data/user/c/ceballos/test_samples/WmWmJJ-EWK_TuneCP5_13p6TeV-powheg-pythia8",0.5*0.0295255*1000,plotCategory("kPlotEWKSSWW")),

    }
    return switch.get(argument, "BKGdefault, xsecDefault, category")
