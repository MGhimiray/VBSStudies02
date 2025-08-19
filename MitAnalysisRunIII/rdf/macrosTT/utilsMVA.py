import ROOT
import os, json

def redefineMVAVariables(df,tmva_helper,varString,mvaSel):

    dftag = df

    if(mvaSel == 1):
        dftag =(dftag.Redefine("ngood_jets"   ,"ngood_jets{0}".format(varString))
                     .Redefine("vbs_mjj"      ,"vbs_mjj{0}".format(varString))
                     .Redefine("vbs_ptjj"     ,"vbs_ptjj{0}".format(varString))
                     .Redefine("vbs_detajj"   ,"vbs_detajj{0}".format(varString))
                     .Redefine("vbs_dphijj"   ,"vbs_dphijj{0}".format(varString))
                     .Redefine("vbs_ptj1"     ,"vbs_ptj1{0}".format(varString))
                     .Redefine("vbs_ptj2"     ,"vbs_ptj2{0}".format(varString))
                     .Redefine("vbs_etaj1"    ,"vbs_etaj1{0}".format(varString))
                     .Redefine("vbs_etaj2"    ,"vbs_etaj2{0}".format(varString))
                     .Redefine("vbs_zepvv"    ,"vbs_zepvv{0}".format(varString))
                     .Redefine("vbs_zepmax"   ,"vbs_zepmax{0}".format(varString))
                     .Redefine("vbs_sumHT"    ,"vbs_sumHT{0}".format(varString))
                     .Redefine("vbs_ptvv"     ,"vbs_ptvv{0}".format(varString))
                     .Redefine("vbs_pttot"    ,"vbs_pttot{0}".format(varString))
                     .Redefine("vbs_detavvj1" ,"vbs_detavvj1{0}".format(varString))
                     .Redefine("vbs_detavvj2" ,"vbs_detavvj2{0}".format(varString))
                     .Redefine("vbs_ptbalance","vbs_ptbalance{0}".format(varString))
                     )
        dftag = tmva_helper.run_inference(dftag,"bdt_vbfinc{0}".format(varString),1)

    else:
        print("Wrong selection: {0}".format(mvaSel))

    return dftag
