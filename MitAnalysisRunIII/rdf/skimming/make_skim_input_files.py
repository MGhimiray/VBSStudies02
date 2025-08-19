import os, sys, getopt

if __name__ == "__main__":

    inputDir = "/home/tier3/cmsprod/catalog/t2mit/nanohr/D00/"
    inputCfg = "skim_input_samples.cfg"
    outputCfg = "skim_input_files.cfg"
    outputForCondorCfg = "skim_input_condor_jobs.cfg"
    group = 10

    valid = ['inputDir=', "inputCfg=", "outputCfg=", "outputForCondorCfg=", "group=", 'help']
    usage  =  "Usage: ana.py --inputDir=<{0}>\n".format(inputDir)
    usage +=  "              --inputCfg=<{0}>\n".format(inputCfg)
    usage +=  "              --outputCfg=<{0}>\n".format(outputCfg)
    usage +=  "              --outputForCondorCfg=<{0}>\n".format(outputForCondorCfg)
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
        if opt == "--inputDir":
            inputDir = str(arg)
        if opt == "--inputCfg":
            inputCfg = str(arg)
        if opt == "--outputCfg":
            outputCfg = str(arg)
        if opt == "--outputForCondorCfg":
            outputForCondorCfg = str(arg)
        if opt == "--group":
            group = str(arg)

    outputFile = open(outputCfg, 'w')
    outputForCondorFile = open(outputForCondorCfg, 'w')

    countSamples = 0
    inputFile = open(inputCfg, 'r')
    while True:
        line = inputFile.readline().strip()
        if not line:
            break
        countSamples += 1
        print(line)
        rawfile = os.path.join(inputDir, line, "RawFiles.00")
        if not os.path.isfile(rawfile):
            print("File %s does not exist!" % rawFile)

        countJobs = 0
        countFiles = 0
        inputRawFile = open(rawfile, 'r')
        while True:
            lineRaw = inputRawFile.readline().strip().split(None, 1)
            if not lineRaw:
                break

            if(countFiles%group == 0):
                lineForCondor = "{0} {1} {2} {3}\n".format(countSamples-1,countJobs,group,line)
                outputForCondorFile.writelines(lineForCondor)
                countJobs += 1

            countFiles += 1
            #outputFile.writelines(lineRaw[0].replace("root://xrootd.cmsaf.mit.edu//store","gsiftp://se01.cmsaf.mit.edu:2811/cms/store"))
            outputFile.writelines(lineRaw[0])
            outputFile.writelines("\n")

        print("Sample({0}): files/jobs: {1} / {2}".format(countSamples,countFiles,countJobs))

    print("Samples: {0}".format(countSamples))
