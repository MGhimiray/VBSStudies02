import os, sys, getopt, time

if __name__ == "__main__":

    outputDir = "/ceph/submit/data/group/cms/store/user/ceballos/nanoaod/skims_submit"
    outputForCondorCfg = "skim_input_condor_jobs_fromDAS.cfg"
    missingFilesCfg = "skim_input_condor_missing_jobs_fromDAS.cfg"
    debug = 0
    type = 0
    deleteFiles = 0

    valid = ['outputDir=', "outputForCondorCfg=", "missingFilesCfg=", "debug=", "type=", "delete=", "help"]
    usage  =  "Usage: ana.py --outputDir=<{0}>\n".format(outputDir)
    usage +=  "              --outputForCondorCfg=<{0}>\n".format(outputForCondorCfg)
    usage +=  "              --missingFilesCfg=<{0}>\n".format(missingFilesCfg)
    usage +=  "              --debug=<{0}>\n".format(debug)
    usage +=  "              --type=<{0}>\n".format(type)
    usage +=  "              --delete=<{0}>".format(deleteFiles)
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
        if opt == "--outputForCondorCfg":
            outputForCondorCfg = str(arg)
        if opt == "--missingFilesCfg":
            missingFilesCfg = str(arg)
        if opt == "--type":
            type = int(arg)
        if opt == "--debug":
            debug = int(arg)
        if opt == "--delete":
            deleteFiles = int(arg)

    missingFile = open(missingFilesCfg, 'w')

    countMissingFiles = [0, 0, 0, 0, 0, 0]
    outputFile = open(outputForCondorCfg, 'r')
    while True:
        lineRaw = outputFile.readline()
        line = lineRaw.strip().split(None, 4)
        if not line:
            break

        #isMissingFile = [True, True, True, True, True]
        isMissingFile = [True, True, True, True, False]
        # 1l
        fileNameA = os.path.join(outputDir, "1l", line[3], "output_1l_{0}.root".format(line[1]))
        fileNameB = os.path.join(outputDir, "1l", line[3], "output_1l_{0}_{1}.root".format(line[0],line[1]))
        fileNameC = os.path.join(outputDir, "1l", line[3], "output_1l_{0}_{1}.txt".format(line[0],line[1]))

        if((os.path.exists(fileNameA) and os.path.getsize(fileNameA) > 1000) or
           (os.path.exists(fileNameB) and os.path.getsize(fileNameB) > 1000) or
            os.path.exists(fileNameC)):
            isMissingFile[0] = False
        else:
            countMissingFiles[0] += 1
            if(debug == 1): print(fileNameB)

        # 2l
        fileNameA = os.path.join(outputDir, "2l", line[3], "output_2l_{0}.root".format(line[1]))
        fileNameB = os.path.join(outputDir, "2l", line[3], "output_2l_{0}_{1}.root".format(line[0],line[1]))
        fileNameC = os.path.join(outputDir, "2l", line[3], "output_2l_{0}_{1}.txt".format(line[0],line[1]))

        if((os.path.exists(fileNameA) and os.path.getsize(fileNameA) > 1000) or
           (os.path.exists(fileNameB) and os.path.getsize(fileNameB) > 1000) or
            os.path.exists(fileNameC)):
            isMissingFile[1] = False
        else:
            countMissingFiles[1] += 1
            if(debug == 1): print(fileNameB)

        # 3l
        fileNameA = os.path.join(outputDir, "3l", line[3], "output_3l_{0}.root".format(line[1]))
        fileNameB = os.path.join(outputDir, "3l", line[3], "output_3l_{0}_{1}.root".format(line[0],line[1]))
        fileNameC = os.path.join(outputDir, "3l", line[3], "output_3l_{0}_{1}.txt".format(line[0],line[1]))

        if((os.path.exists(fileNameA) and os.path.getsize(fileNameA) > 1000) or
           (os.path.exists(fileNameB) and os.path.getsize(fileNameB) > 1000) or
            os.path.exists(fileNameC)):
            isMissingFile[2] = False
        else:
            countMissingFiles[2] += 1
            if(debug == 1): print(fileNameB)

        # met
        fileNameA = os.path.join(outputDir, "met", line[3], "output_met_{0}.root".format(line[1]))
        fileNameB = os.path.join(outputDir, "met", line[3], "output_met_{0}_{1}.root".format(line[0],line[1]))
        fileNameC = os.path.join(outputDir, "met", line[3], "output_met_{0}_{1}.txt".format(line[0],line[1]))

        if((os.path.exists(fileNameA) and os.path.getsize(fileNameA) > 1000) or
           (os.path.exists(fileNameB) and os.path.getsize(fileNameB) > 1000) or
            os.path.exists(fileNameC)):
            isMissingFile[3] = False
        else:
            countMissingFiles[3] += 1
            if(debug == 1): print(fileNameB)

        # pho
        fileNameA = os.path.join(outputDir, "pho", line[3], "output_pho_{0}.root".format(line[1]))
        fileNameB = os.path.join(outputDir, "pho", line[3], "output_pho_{0}_{1}.root".format(line[0],line[1]))
        fileNameC = os.path.join(outputDir, "pho", line[3], "output_pho_{0}_{1}.txt".format(line[0],line[1]))

        if((os.path.exists(fileNameA) and os.path.getsize(fileNameA) > 1000) or
           (os.path.exists(fileNameB) and os.path.getsize(fileNameB) > 1000) or
            os.path.exists(fileNameC)):
            isMissingFile[4] = False
        else:
            countMissingFiles[4] += 1
            if(debug == 1): print(fileNameB)

        # summary
        if((type == 0 and (isMissingFile[0] == True or isMissingFile[1] == True or isMissingFile[2] == True or isMissingFile[3] == True or isMissingFile[4] == True)) or
           (type == 1 and (isMissingFile[1] == True or isMissingFile[2] == True or isMissingFile[3] == True or isMissingFile[4] == True)) or
           (type == 2 and (isMissingFile[4] == True))
          ):
            missingFile.writelines(lineRaw)
            countMissingFiles[5] += 1
            if(deleteFiles == 1):
                fileNameDelete = os.path.join(outputDir, "*", line[3], "output_*_{0}_{1}.*".format(line[0],line[1]))
                print("rm -f {0}".format(fileNameDelete))
                os.system("rm -f {0}".format(fileNameDelete))

    missingFile.close()

    print("missingFiles: {0} / {1} / {2} / {3} / {4} / {5}".format(countMissingFiles[0],countMissingFiles[1],countMissingFiles[2],countMissingFiles[3],countMissingFiles[4],countMissingFiles[5]))
    os.system("wc {0};wc {1}".format(outputForCondorCfg,missingFilesCfg))
