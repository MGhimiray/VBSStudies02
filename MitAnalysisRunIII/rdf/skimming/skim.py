import ROOT
import os, sys, getopt, json, time, subprocess, socket
import fnmatch
import math

ROOT.ROOT.EnableImplicitMT(2)

ROOT.gInterpreter.ProcessLine('#include "functions_skim.h"')

selectionJsonPath = "config/selection.json"
if(not os.path.exists(selectionJsonPath)):
    selectionJsonPath = "selection.json"

with open(selectionJsonPath) as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

overallTriggers = jsonObject['triggers']

JSON = "isGoodRunLS(isSkimData, run, luminosityBlock)"

def buildcommand(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = p.communicate()
    print("command {0}, out {1}, error{2}, returncode {3}".format(command,out,error,p.returncode))
    return p.returncode

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

# split fIns files in groups of group files
def groupFiles(fIns, group):

    ret = [fIns[x:x+group] for x in range(0, len(fIns), group)]

    return ret

def getTriggerFromJson(overall, type, year ):

    for trigger in overall:
        if(trigger['name'] == type and trigger['year'] == year): return trigger['definition']

if __name__ == "__main__":

    copyFilesToFS = True
    #            1l     2l     3l     met    pho
    doSkimSel = [True, True, True, True, False]

    outputDir = "root://submit50.mit.edu//store/user/ceballos/nanoaod/skims_submit/"
    inputSamplesCfg = "skim_input_samples.cfg"
    inputFilesCfg = "skim_input_files.cfg"
    whichSample = 1
    whichJob = -1
    group = 10

    valid = ['outputDir=', "inputSamplesCfg=", "inputFilesCfg=", "whichSample=", "whichJob=", "group=", 'help']
    usage  =  "Usage: ana.py --outputDir=<{0}>\n".format(outputDir)
    usage +=  "              --inputSamplesCfg=<{0}>\n".format(inputSamplesCfg)
    usage +=  "              --inputFilesCfg=<{0}>\n".format(inputFilesCfg)
    usage +=  "              --whichSample=<{0}>\n".format(whichSample)
    usage +=  "              --whichJob=<{0}>\n".format(whichJob)
    usage +=  "              --group=<{0}>".format(group)
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
        if opt == "--outputDir":
            outputDir = str(arg)
        if opt == "--inputSamplesCfg":
            inputSamplesCfg = str(arg)
        if opt == "--inputFilesCfg":
            inputFilesCfg = str(arg)
        if opt == "--whichSample":
            whichSample = int(arg)
        if opt == "--whichJob":
            whichJob = int(arg)
        if opt == "--group":
            group = int(arg)

    theHost = socket.gethostname()
    msgCPInput  = "xrdcp --force"
    msgCPOutput = "xrdcp --force"
    isLocal = False
    if(("t3deskxxx" in theHost) or ("t3btchxxx" in theHost)):
        outputDir = outputDir.replace("root://t3serv017.mit.edu/","/mnt/hadoop")
        msgCPOutput = "cp"
        isLocal = True
        print("T3 node ({0}), outputDir = {1} / msgCPOutput = {2}".format(theHost,outputDir,msgCPOutput))

    elif("submit" in theHost):
        outputDir = outputDir.replace("root://submit50.mit.edu/","/ceph/submit/data/group/cms")
        msgCPOutput = "cp"
        isLocal = True
        print("submit node ({0}), outputDir = {1} / msgCPOutput = {2}".format(theHost,outputDir,msgCPOutput))

    # Reading which sample we want to skim
    inputSamplesFile = open(inputSamplesCfg, 'r')
    linesSamplesFile = inputSamplesFile.readlines()
    if(whichSample < 0 or whichSample >= len(linesSamplesFile)):
        print("Incorrect whichSample: {0}".format(whichSample))
        sys.exit(1)
    sampleToSkim = linesSamplesFile[whichSample].strip()
    print("Sample to skim: {0}".format(sampleToSkim))

    year = -1
    isSkimData = -1
    if("Run2018" in sampleToSkim):
        year = 2018
        isSkimData = 1
    elif("Run2022" in sampleToSkim):
        year = 2022
        isSkimData = 1
    elif("Run2023" in sampleToSkim):
        year = 2023
        isSkimData = 1
    elif("Run2024" in sampleToSkim):
        year = 2024
        isSkimData = 1
    elif("RunIISummer20UL18" in sampleToSkim):
        year = 2018
        isSkimData = 0
    elif("Run3Summer22" in sampleToSkim):
        year = 2022
        isSkimData = 0
    elif("Run3Summer23" in sampleToSkim):
        year = 2023
        isSkimData = 0
    elif("2024Summer24" in sampleToSkim):
        year = 2024
        isSkimData = 0

    if(year == -1 or isSkimData == -1):
        print("Incorrect year/isSkimData: {0} / {1}".format(year, isSkimData))
        sys.exit(1)

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
        jsnName = "Collisions23_13p6TeV_DCSOnly_TkPx.json"
    elif(year == 2024):
        jsnName = "Collisions24_13p6TeV_DCSOnly_TkPx.json"

    if os.path.exists(os.path.join("jsns",jsnName)):
        loadJSON(os.path.join("jsns",jsnName))
    else:
        loadJSON(jsnName)

    TRIGGERMUEG = getTriggerFromJson(overallTriggers, "TRIGGERMUEG", year)
    TRIGGERDMU  = getTriggerFromJson(overallTriggers, "TRIGGERDMU", year)
    TRIGGERSMU  = getTriggerFromJson(overallTriggers, "TRIGGERSMU", year)
    TRIGGERDEL  = getTriggerFromJson(overallTriggers, "TRIGGERDEL", year)
    TRIGGERSEL  = getTriggerFromJson(overallTriggers, "TRIGGERSEL", year)

    TRIGGERLEP = "{0} or {1} or {2} or {3} or {4}".format(TRIGGERSEL,TRIGGERDEL,TRIGGERSMU,TRIGGERDMU,TRIGGERMUEG)

    TRIGGERFAKEMU = getTriggerFromJson(overallTriggers, "TRIGGERFAKEMU", year)
    TRIGGERFAKEEL = getTriggerFromJson(overallTriggers, "TRIGGERFAKEEL", year)

    TRIGGERFAKE = "{0} or {1}".format(TRIGGERFAKEMU,TRIGGERFAKEEL)

    TRIGGERMET = getTriggerFromJson(overallTriggers, "TRIGGERMET", year)
    TRIGGERPHO = getTriggerFromJson(overallTriggers, "TRIGGERPHOINC", year)

    print(inputFilesCfg)
    rootFiles = ROOT.vector('string')()
    inputFilesFile = open(inputFilesCfg, 'r')
    #trick to deal with official samples
    sampleToFilter = [sampleToSkim, sampleToSkim, sampleToSkim]
    if("NANOAODSIM" in sampleToSkim):
        sampleToFilter[0] = "/"+sampleToSkim.split("+")[0]+"/"
        sampleToFilter[1] = sampleToSkim.split("+")[1].split("-")[0]
        sampleToFilter[2] = sampleToSkim.split("+")[1].split("-")[1]
    elif("NANOAOD" in sampleToSkim):
        sampleToFilter[0] = "/"+sampleToSkim.split("+")[0]+"/"
        sampleToFilter[1] = sampleToSkim.split("+")[1].split("-")[0]
        sampleToFilter[2] = sampleToSkim.split("+")[1].split("-")[1]
    while True:
        line = inputFilesFile.readline().strip()
        if not line:
            break
        if(sampleToFilter[0] not in line):
            continue
        if(sampleToFilter[1] not in line):
            continue
        if(sampleToFilter[2] not in line):
            continue
        rootFiles.push_back(line)

    groupedFiles = groupFiles(rootFiles, group)
    finalOutputDir1 = os.path.join(outputDir, "1l", sampleToSkim)
    finalOutputDir2 = os.path.join(outputDir, "2l", sampleToSkim)
    finalOutputDir3 = os.path.join(outputDir, "3l", sampleToSkim)
    finalOutputDir4 = os.path.join(outputDir, "met",sampleToSkim)
    finalOutputDir5 = os.path.join(outputDir, "pho",sampleToSkim)
    print("Files to skim/jobs: {0}/{1} / outputDir: {2}".format(len(rootFiles),len(groupedFiles),outputDir))

    TRIGGERLEP    = "{0} or {1} or {2} or {3} or {4}".format(TRIGGERSEL,TRIGGERDEL,TRIGGERSMU,TRIGGERDMU,TRIGGERMUEG)
    TRIGGERALLLEP = "{0} or {1} or {2} or {3} or {4}".format(TRIGGERSEL,TRIGGERDEL,TRIGGERSMU,TRIGGERDMU,TRIGGERMUEG)

    print("TRIGGERLEP: {0}".format(TRIGGERLEP))

    print("TRIGGERFAKE: {0}".format(TRIGGERFAKE))

    for i, groupedFile in enumerate(groupedFiles):
        passJob = whichJob == -1 or whichJob == i
        if(passJob == False): continue
        try:
            atLeastOneFile = [False, False, False, False, False]

            fOutName1 = "output_1l_%d_%d.root" % (whichSample,i)
            fOutName2 = "output_2l_%d_%d.root" % (whichSample,i)
            fOutName3 = "output_3l_%d_%d.root" % (whichSample,i)
            fOutName4 = "output_met_%d_%d.root"% (whichSample,i)
            fOutName5 = "output_pho_%d_%d.root"% (whichSample,i)

            print("Create {0} / {1} / {2} / {3} / {4}".format(fOutName1,fOutName2,fOutName3,fOutName4,fOutName5))

            msgMerge1 = "python3 haddnanoaod.py %s" % (fOutName1)
            msgMerge2 = "python3 haddnanoaod.py %s" % (fOutName2)
            msgMerge3 = "python3 haddnanoaod.py %s" % (fOutName3)
            msgMerge4 = "python3 haddnanoaod.py %s" % (fOutName4)
            msgMerge5 = "python3 haddnanoaod.py %s" % (fOutName5)
            msgRm = "rm -f"

            isJobFailure = False

            for nf in range(len(groupedFile)):
                fOutIndivName1 = "output_1l_{0}_{1}_{2}.root".format(whichSample,i,nf)
                fOutIndivName2 = "output_2l_{0}_{1}_{2}.root".format(whichSample,i,nf)
                fOutIndivName3 = "output_3l_{0}_{1}_{2}.root".format(whichSample,i,nf)
                fOutIndivName4 = "output_met_{0}_{1}_{2}.root".format(whichSample,i,nf)
                fOutIndivName5 = "output_pho_{0}_{1}_{2}.root".format(whichSample,i,nf)

                msgRm = msgRm + " " + fOutIndivName1
                msgRm = msgRm + " " + fOutIndivName2
                msgRm = msgRm + " " + fOutIndivName3
                msgRm = msgRm + " " + fOutIndivName4
                msgRm = msgRm + " " + fOutIndivName5

                inputSingleFile = groupedFile[nf]
                inputSingleFileBase = os.path.basename(inputSingleFile)
                copycommand = "%s %s %s" % (msgCPInput,inputSingleFile, inputSingleFileBase)

                copy_result = False
                n_retries = 0
                while n_retries < 5 and copy_result is False:
                    returncode = buildcommand(copycommand)
                    if os.path.exists(inputSingleFileBase) and returncode == 0:
                        copy_result = True
                    else:
                        print("Copying file {0} failed ({1}), retrying".format(inputSingleFileBase,returncode))
                        n_retries+=1
                        time.sleep(0.1)

                if(copy_result == False):
                    print("Copying file {0} failed completely, exiting the loop".format(inputSingleFileBase))
                    isJobFailure = True
                    break

                rdf = ROOT.RDataFrame("Events", inputSingleFileBase)\
                            .Define("isSkimData","{}".format(isSkimData))\
                            .Define("applyDataJson","{}".format(JSON)).Filter("applyDataJson","pass JSON")

                print("Processing({0}): {1} / {2}".format(nf,inputSingleFile,rdf.Count().GetValue()))
                nonZeroEvents = True
                if(rdf.Count().GetValue() == 0):
                    nonZeroEvents = False

                if((doSkimSel[1] == True or doSkimSel[2] == True) and nonZeroEvents == True):
                    rdf_ll = rdf.Define("skim_mu", "abs(Muon_eta) < 2.4 && Muon_pt > 10 && Muon_looseId == true")\
                                .Define("skim_el", "abs(Electron_eta) < 2.5 && Electron_pt > 10 && Electron_cutBased >= 1")\
                                .Filter("Sum(skim_mu)+Sum(skim_el) >= 2","At least two loose leptons")\
                                .Define("skimmu_pt",    "Muon_pt[skim_mu]")\
                                .Define("skimmu_eta",   "Muon_eta[skim_mu]")\
                                .Define("skimmu_phi",   "Muon_phi[skim_mu]")\
                                .Define("skimmu_mass",  "Muon_mass[skim_mu]")\
                                .Define("skimmu_charge","Muon_charge[skim_mu]")\
                                .Define("skimel_pt",    "Electron_pt[skim_el]")\
                                .Define("skimel_eta",   "Electron_eta[skim_el]")\
                                .Define("skimel_phi",   "Electron_phi[skim_el]")\
                                .Define("skimel_mass",  "Electron_mass[skim_el]")\
                                .Define("skimel_charge","Electron_charge[skim_el]")\
                                .Define("skim_lep_charge","Sum(skimmu_charge)+Sum(skimel_charge)")\
                                .Define("skim","applySkim(skimmu_pt, skimmu_eta, skimmu_phi, skimmu_mass, skimel_pt, skimel_eta, skimel_phi, skimel_mass, skim_lep_charge, PuppiMET_pt)")

                    rdf_2l = rdf_ll.Define("trigger2l","({0}) or ({1})".format(TRIGGERLEP,TRIGGERFAKE))\
                                   .Filter("trigger2l > 0","Passed trigger2l")\
                                   .Filter("skim >= 2","Two loose leptons with mll > 10 GeV")\
                                   .Snapshot("Events", fOutIndivName2)

                    rdf_3l = rdf_ll.Define("trigger2l","{0}".format(TRIGGERLEP))\
                                   .Filter("trigger2l > 0","Passed trigger2l")\
                                   .Filter("skim == 1 || skim == 2 || skim == 3",">=3, q(l1+l2)!=0, met>50/ptll>50")\
                                   .Snapshot("Events", fOutIndivName3)

                if(doSkimSel[0] == True and nonZeroEvents == True):
                    rdf_1l = rdf.Define("trigger1l","{0}".format(TRIGGERFAKE))\
                                .Filter("trigger1l > 0","Passed trigger1l")\
                                .Define("skim_fake_mu", "abs(Muon_eta) < 2.4 && Muon_pt > 10 && Muon_looseId == true")\
                                .Define("skim_fake_el", "abs(Electron_eta) < 2.5 && Electron_pt > 10 && Electron_cutBased >= 1")\
                                .Filter("Sum(skim_fake_mu)+Sum(skim_fake_el) == 1","One fake lepton")\
                                .Snapshot("Events", fOutIndivName1)

                if(doSkimSel[3] == True and nonZeroEvents == True):
                    rdf_met= rdf_ll.Define("triggermet","{0}".format(TRIGGERMET))\
                                   .Filter("triggermet > 0","Passed triggermet")\
                                   .Filter("skim >= 1","Two or more loose leptons")\
                                   .Snapshot("Events", fOutIndivName4)

                if(doSkimSel[4] == True and nonZeroEvents == True):
                    rdf_pho = rdf.Define("triggerlep","{0}".format(TRIGGERALLLEP))\
                                 .Define("triggerpho","{0}".format(TRIGGERPHO))\
                                 .Filter("triggerlep > 0 or triggerpho > 0","Passed trigger")\
                                 .Define("skim_el", "abs(Electron_eta) < 2.5 && Electron_pt > 10 && Electron_cutBased >= 1")\
                                 .Define("photon_mask", "cleaningMask(Electron_photonIdx[skim_el],nPhoton)")\
                                 .Define("skim_photon", "Photon_pt > 20 && abs(Photon_eta) < 2.5 && photon_mask && Photon_pfRelIso03_chg*Photon_pt < 10 && cleaningBitmap(Photon_vidNestedWPBitmap,4,2) && cleaningBitmap(Photon_vidNestedWPBitmap,10,2) && cleaningBitmap(Photon_vidNestedWPBitmap,12,2)")\
                                 .Filter("Sum(skim_photon) >= 1","One loose photon")\
                                 .Snapshot("Events", fOutIndivName5)

                eventCounts = [0, 0, 0, 0, 0]
                try:
                    eventCounts[0] = rdf_1l.Count().GetValue()
                    del rdf_1l
                except Exception as e:
                    print("No selected events in {0}".format(fOutIndivName1))
                try:
                    eventCounts[1] = rdf_2l.Count().GetValue()
                    del rdf_2l
                except Exception as e:
                    print("No selected events in {0}".format(fOutIndivName2))
                try:
                    eventCounts[2] = rdf_3l.Count().GetValue()
                    del rdf_3l
                except Exception as e:
                    print("No selected events in {0}".format(fOutIndivName3))
                try:
                    eventCounts[3] = rdf_met.Count().GetValue()
                    del rdf_met
                except Exception as e:
                    print("No selected events in {0}".format(fOutIndivName4))
                try:
                    eventCounts[4] = rdf_pho.Count().GetValue()
                    del rdf_pho
                except Exception as e:
                    print("No selected events in {0}".format(fOutIndivName5))

                try:
                    del rdf, rdf_ll
                except Exception as e:
                    print("Delete exception {0}".format(e))

                runTree = ROOT.TChain("Runs")
                runTree.AddFile(inputSingleFileBase)
                lumiTree = ROOT.TChain("LuminosityBlocks")
                if(isSkimData == 1):
                    lumiTree.AddFile(inputSingleFileBase)

                fOut1 = ROOT.TFile(fOutIndivName1,"UPDATE")
                fOut1.cd()
                runTreeCopy1 = runTree.CopyTree("");
                runTreeCopy1.Write()
                if(isSkimData == 1):
                    lumiTreeCopy1 = lumiTree.CopyTree("");
                    lumiTreeCopy1.Write()
                fOut1.Close()
                if(eventCounts[0] > 0 or isSkimData == 1):
                    atLeastOneFile[0] = True
                    msgMerge1 = msgMerge1 + " " + fOutIndivName1

                fOut2 = ROOT.TFile(fOutIndivName2,"UPDATE")
                fOut2.cd()
                runTreeCopy2 = runTree.CopyTree("");
                runTreeCopy2.Write()
                if(isSkimData == 1):
                    lumiTreeCopy2 = lumiTree.CopyTree("");
                    lumiTreeCopy2.Write()
                fOut2.Close()
                if(eventCounts[1] > 0 or isSkimData == 1):
                    atLeastOneFile[1] = True
                    msgMerge2 = msgMerge2 + " " + fOutIndivName2

                fOut3 = ROOT.TFile(fOutIndivName3,"UPDATE")
                fOut3.cd()
                runTreeCopy3 = runTree.CopyTree("");
                runTreeCopy3.Write()
                if(isSkimData == 1):
                    lumiTreeCopy3 = lumiTree.CopyTree("");
                    lumiTreeCopy3.Write()
                fOut3.Close()
                if(eventCounts[2] > 0 or isSkimData == 1):
                    atLeastOneFile[2] = True
                    msgMerge3 = msgMerge3 + " " + fOutIndivName3

                fOut4 = ROOT.TFile(fOutIndivName4,"UPDATE")
                fOut4.cd()
                runTreeCopy4 = runTree.CopyTree("");
                runTreeCopy4.Write()
                if(isSkimData == 1):
                    lumiTreeCopy4 = lumiTree.CopyTree("");
                    lumiTreeCopy4.Write()
                fOut4.Close()
                if(eventCounts[3] > 0 or isSkimData == 1):
                    atLeastOneFile[3] = True
                    msgMerge4 = msgMerge4 + " " + fOutIndivName4

                fOut5 = ROOT.TFile(fOutIndivName5,"UPDATE")
                fOut5.cd()
                runTreeCopy5 = runTree.CopyTree("");
                runTreeCopy5.Write()
                if(isSkimData == 1):
                    lumiTreeCopy5 = lumiTree.CopyTree("");
                    lumiTreeCopy5.Write()
                fOut5.Close()
                if(eventCounts[4] > 0 or isSkimData == 1):
                    atLeastOneFile[4] = True
                    msgMerge5 = msgMerge5 + " " + fOutIndivName5

                os.remove(inputSingleFileBase)

            if(isJobFailure == True):
                print("Job ({0}/{1}) failed completely".format(outputDir,i))
                continue

            # haddnanoaod1
            copy_result = False
            n_retries = 0
            if(doSkimSel[0] == False): copy_result = True
            while n_retries < 5 and copy_result is False:
                returncode = 0
                if(atLeastOneFile[0] == True):
                    returncode = buildcommand(msgMerge1)
                else:
                    fOutName1 = "output_1l_%d_%d.txt" % (whichSample,i)
                    returntestcode = buildcommand("touch {0}".format(fOutName1))
                if returncode == 0:
                    copy_result = True
                    if(isSkimData == 0):
                        try:
                            dftest = ROOT.RDataFrame("Events", fOutName1)
                            nevents = dftest.Count().GetValue()
                            del dftest
                        except Exception as e:
                            os.remove(fOutName1)
                            fOutName1 = "output_1l_%d_%d.txt" % (whichSample,i)
                            returntestcode = buildcommand("touch {0}".format(fOutName1))
                else:
                    print("haddnanoaod output file1 {0} failed ({1}), retrying".format(fOutName1,returncode))
                    n_retries+=1
                    time.sleep(0.1)
            if(copy_result == False):
                print("haddnanoaod output file1 {0} failed completely, exiting the loop".format(fOutName1))
                os.remove(fOutName1)

            # haddnanoaod2
            copy_result = False
            n_retries = 0
            if(doSkimSel[1] == False): copy_result = True
            while n_retries < 5 and copy_result is False:
                returncode = 0
                if(atLeastOneFile[1] == True):
                    returncode = buildcommand(msgMerge2)
                else:
                    fOutName2 = "output_2l_%d_%d.txt" % (whichSample,i)
                    returntestcode = buildcommand("touch {0}".format(fOutName2))
                if returncode == 0:
                    copy_result = True
                    if(isSkimData == 0):
                        try:
                            dftest = ROOT.RDataFrame("Events", fOutName2)
                            nevents = dftest.Count().GetValue()
                            del dftest
                        except Exception as e:
                            os.remove(fOutName2)
                            fOutName2 = "output_2l_%d_%d.txt" % (whichSample,i)
                            returntestcode = buildcommand("touch {0}".format(fOutName2))
                else:
                    print("haddnanoaod output file2 {0} failed ({1}), retrying".format(fOutName2,returncode))
                    n_retries+=1
                    time.sleep(0.1)
            if(copy_result == False):
                print("haddnanoaod output file2 {0} failed completely, exiting the loop".format(fOutName2))
                os.remove(fOutName2)

            # haddnanoaod3
            copy_result = False
            n_retries = 0
            if(doSkimSel[2] == False): copy_result = True
            while n_retries < 5 and copy_result is False:
                returncode = 0
                if(atLeastOneFile[2] == True):
                    returncode = buildcommand(msgMerge3)
                else:
                    fOutName3 = "output_3l_%d_%d.txt" % (whichSample,i)
                    returntestcode = buildcommand("touch {0}".format(fOutName3))
                if returncode == 0:
                    copy_result = True
                    if(isSkimData == 0):
                        try:
                            dftest = ROOT.RDataFrame("Events", fOutName3)
                            nevents = dftest.Count().GetValue()
                            del dftest
                        except Exception as e:
                            os.remove(fOutName3)
                            fOutName3 = "output_3l_%d_%d.txt" % (whichSample,i)
                            returntestcode = buildcommand("touch {0}".format(fOutName3))
                else:
                    print("haddnanoaod output file3 {0} failed ({1}), retrying".format(fOutName3,returncode))
                    n_retries+=1
                    time.sleep(0.1)
            if(copy_result == False):
                print("haddnanoaod output file3 {0} failed completely, exiting the loop".format(fOutName3))
                os.remove(fOutName3)

            # haddnanoaod4
            copy_result = False
            n_retries = 0
            if(doSkimSel[3] == False): copy_result = True
            while n_retries < 5 and copy_result is False:
                returncode = 0
                if(atLeastOneFile[3] == True):
                    returncode = buildcommand(msgMerge4)
                else:
                    fOutName4 = "output_met_%d_%d.txt" % (whichSample,i)
                    returntestcode = buildcommand("touch {0}".format(fOutName4))
                if returncode == 0:
                    copy_result = True
                    if(isSkimData == 0):
                        try:
                            dftest = ROOT.RDataFrame("Events", fOutName4)
                            nevents = dftest.Count().GetValue()
                            del dftest
                        except Exception as e:
                            os.remove(fOutName4)
                            fOutName4 = "output_met_%d_%d.txt" % (whichSample,i)
                            returntestcode = buildcommand("touch {0}".format(fOutName4))
                else:
                    print("haddnanoaod output file4 {0} failed ({1}), retrying".format(fOutName4,returncode))
                    n_retries+=1
                    time.sleep(0.1)
            if(copy_result == False):
                print("haddnanoaod output file4 {0} failed completely, exiting the loop".format(fOutName4))
                os.remove(fOutName4)


            # haddnanoaod5
            copy_result = False
            n_retries = 0
            if(doSkimSel[4] == False): copy_result = True
            while n_retries < 5 and copy_result is False:
                returncode = 0
                if(atLeastOneFile[4] == True):
                    returncode = buildcommand(msgMerge5)
                else:
                    fOutName5 = "output_pho_%d_%d.txt" % (whichSample,i)
                    returntestcode = buildcommand("touch {0}".format(fOutName5))
                if returncode == 0:
                    copy_result = True
                    if(isSkimData == 0):
                        try:
                            dftest = ROOT.RDataFrame("Events", fOutName5)
                            nevents = dftest.Count().GetValue()
                            del dftest
                        except Exception as e:
                            os.remove(fOutName5)
                            fOutName5 = "output_pho_%d_%d.txt" % (whichSample,i)
                            returntestcode = buildcommand("touch {0}".format(fOutName5))
                else:
                    print("haddnanoaod output file5 {0} failed ({1}), retrying".format(fOutName5,returncode))
                    n_retries+=1
                    time.sleep(0.1)
            if(copy_result == False):
                print("haddnanoaod output file5 {0} failed completely, exiting the loop".format(fOutName5))
                os.remove(fOutName5)

            if(copyFilesToFS == True):
                # copying output file1
                copycommand = "%s %s %s/%s" % (msgCPOutput,fOutName1,finalOutputDir1,fOutName1)
                if(isLocal == True and (not os.path.exists(finalOutputDir1))):
                    os.makedirs(finalOutputDir1)

                copy_result = False
                n_retries = 0
                if(doSkimSel[0] == False): copy_result = True
                while n_retries < 5 and copy_result is False:
                    returncode = buildcommand(copycommand)
                    if returncode == 0:
                        copy_result = True
                    else:
                        print("Copying output file1 {0} failed ({1}), retrying".format(fOutName1,returncode))
                        n_retries+=1
                        time.sleep(0.1)
                if(copy_result == False):
                    print("Copying output file1 {0} failed completely, exiting the loop".format(fOutName1))

                if os.path.exists(fOutName1):
                    os.remove(fOutName1)

                # copying output file2
                copycommand = "%s %s %s/%s" % (msgCPOutput,fOutName2,finalOutputDir2,fOutName2)
                if(isLocal == True and (not os.path.exists(finalOutputDir2))):
                    os.makedirs(finalOutputDir2)

                copy_result = False
                n_retries = 0
                if(doSkimSel[1] == False): copy_result = True
                while n_retries < 5 and copy_result is False:
                    returncode = buildcommand(copycommand)
                    if returncode == 0:
                        copy_result = True
                    else:
                        print("Copying output file2 {0} failed ({1}), retrying".format(fOutName2,returncode))
                        n_retries+=1
                        time.sleep(0.1)
                if(copy_result == False):
                    print("Copying output file2 {0} failed completely, exiting the loop".format(fOutName2))

                if os.path.exists(fOutName2):
                    os.remove(fOutName2)

                # copying output file3
                copycommand = "%s %s %s/%s" % (msgCPOutput,fOutName3,finalOutputDir3,fOutName3)
                if(isLocal == True and (not os.path.exists(finalOutputDir3))):
                    os.makedirs(finalOutputDir3)

                copy_result = False
                n_retries = 0
                if(doSkimSel[2] == False): copy_result = True
                while n_retries < 5 and copy_result is False:
                    returncode = buildcommand(copycommand)
                    if returncode == 0:
                        copy_result = True
                    else:
                        print("Copying output file3 {0} failed ({1}), retrying".format(fOutName3,returncode))
                        n_retries+=1
                        time.sleep(0.1)
                if(copy_result == False):
                    print("Copying output file3 {0} failed completely, exiting the loop".format(fOutName3))

                if os.path.exists(fOutName3):
                    os.remove(fOutName3)

                # copying output file4
                copycommand = "%s %s %s/%s" % (msgCPOutput,fOutName4,finalOutputDir4,fOutName4)
                if(isLocal == True and (not os.path.exists(finalOutputDir4))):
                    os.makedirs(finalOutputDir4)

                copy_result = False
                n_retries = 0
                if(doSkimSel[3] == False): copy_result = True
                while n_retries < 5 and copy_result is False:
                    returncode = buildcommand(copycommand)
                    if returncode == 0:
                        copy_result = True
                    else:
                        print("Copying output file4 {0} failed ({1}), retrying".format(fOutName4,returncode))
                        n_retries+=1
                        time.sleep(0.1)
                if(copy_result == False):
                    print("Copying output file4 {0} failed completely, exiting the loop".format(fOutName4))

                if os.path.exists(fOutName4):
                    os.remove(fOutName4)

                # copying output file5
                copycommand = "%s %s %s/%s" % (msgCPOutput,fOutName5,finalOutputDir5,fOutName5)
                if(isLocal == True and (not os.path.exists(finalOutputDir5))):
                    os.makedirs(finalOutputDir5)

                copy_result = False
                n_retries = 0
                if(doSkimSel[4] == False): copy_result = True
                while n_retries < 5 and copy_result is False:
                    returncode = buildcommand(copycommand)
                    if returncode == 0:
                        copy_result = True
                    else:
                        print("Copying output file4 {0} failed ({1}), retrying".format(fOutName5,returncode))
                        n_retries+=1
                        time.sleep(0.1)
                if(copy_result == False):
                    print("Copying output file5 {0} failed completely, exiting the loop".format(fOutName5))

                if os.path.exists(fOutName5):
                    os.remove(fOutName5)

            # Delete used files
            print(msgRm)
            os.system(msgRm)

        except Exception as e:
            print("PROBLEM {0} / {1} / {2}".format(outputDir,i,e))
