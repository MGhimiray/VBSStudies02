#include <TROOT.h>
#include <TMVA/DataLoader.h>
#include <TMVA/Factory.h>
#include <TMVA/Types.h>
#include <TFile.h>
#include <TCut.h>
#include <TTree.h>
#include <TString.h>
#include <TStyle.h>

void ewkvbsMVA(
  TString inputFileName = "/work/submit/ceballos/mva_samples/ntupleWZAna_year2027.root",
  int nsel = 0,
  TString extraString="vbfinc_v0",
  bool moreMVAs = false,
  bool dodnn = false
) {
  gROOT->ProcessLine("TMVA::gConfig().GetVariablePlotting().fMaxNumOfAllowedVariablesForScatterPlots = 50");
  TFile *output_file;
  TMVA::Factory *factory;
  TString trainTreeEventSplitStr="(eventNum % 10)>=5";
  TString testTreeEventSplitStr="(eventNum % 10)<5";

  // Determine the input trees
  TFile *inputFile = TFile::Open(inputFileName,"READ");
  TTree *mvaTree = (TTree*)inputFile->Get("events");
  
  // Initialize the factory
  output_file=TFile::Open(Form("MVA_%s.root",extraString.Data()), "RECREATE");
  factory = new TMVA::Factory("bdt", output_file, "!V:!Silent:DrawProgressBar:Transformations=I;D;P;G,D:AnalysisType=Multiclass");
  TString factoryOptions="!V:!Silent:DrawProgressBar";
  //TString factoryOptions="!V:!Silent:!DrawProgressBar";
  if(nsel != 2)factoryOptions+=":AnalysisType=Classification";
  factory = new TMVA::Factory("bdt", output_file, factoryOptions);
  TMVA::DataLoader *dataloader=new TMVA::DataLoader("MitEWKVBSAnalysis");

  TCut cutTrainSignal = Form("%s && vbs_ptj1 > 50 && vbs_ptj2 > 50 && (theCat==%d||theCat==%d)",trainTreeEventSplitStr.Data(),8,8);
  TCut cutTrainBkg    = Form("%s && vbs_ptj1 > 50 && vbs_ptj2 > 50 && (theCat==%d||theCat==%d||theCat==%d)",trainTreeEventSplitStr.Data(),9,9,9);
  TCut cutTestSignal  = Form("%s && vbs_ptj1 > 50 && vbs_ptj2 > 50 && (theCat==%d||theCat==%d)",testTreeEventSplitStr.Data(), 8,8);
  TCut cutTestBkg     = Form("%s && vbs_ptj1 > 50 && vbs_ptj2 > 50 && (theCat==%d||theCat==%d||theCat==%d)",testTreeEventSplitStr.Data(), 9,9,9);
  if     (nsel == 1){
    cutTrainSignal = Form("%s && vbs_ptj1 > 50 && vbs_ptj2 > 50 && (theCat==%d||theCat==%d)",trainTreeEventSplitStr.Data(),6,8);
    cutTrainBkg    = Form("%s && vbs_ptj1 > 50 && vbs_ptj2 > 50 && (theCat==%d||theCat==%d||theCat==%d)",trainTreeEventSplitStr.Data(),3,7,9);
    cutTestSignal  = Form("%s && vbs_ptj1 > 50 && vbs_ptj2 > 50 && (theCat==%d||theCat==%d)",testTreeEventSplitStr.Data(), 6,8);
    cutTestBkg     = Form("%s && vbs_ptj1 > 50 && vbs_ptj2 > 50 && (theCat==%d||theCat==%d||theCat==%d)",testTreeEventSplitStr.Data(), 3,7,9);
  }
  else if(nsel == 2){
    cutTrainSignal = Form("%s && vbs_ptj1 > 50 && vbs_ptj2 > 50 && (theCat==%d||theCat==%d)",trainTreeEventSplitStr.Data(),8,8);
    cutTrainBkg    = Form("%s && vbs_ptj1 > 50 && vbs_ptj2 > 50 && (theCat==%d||theCat==%d||theCat==%d)",trainTreeEventSplitStr.Data(),6,6,6);
    cutTestSignal  = Form("%s && vbs_ptj1 > 50 && vbs_ptj2 > 50 && (theCat==%d||theCat==%d)",testTreeEventSplitStr.Data(), 8,8);
    cutTestBkg     = Form("%s && vbs_ptj1 > 50 && vbs_ptj2 > 50 && (theCat==%d||theCat==%d||theCat==%d)",testTreeEventSplitStr.Data(), 6,6,6);
  }
  dataloader->AddTree(mvaTree, "Signal"    , 1.0, cutTrainSignal, "train");
  dataloader->AddTree(mvaTree, "Background", 1.0, cutTrainBkg	, "train");
  dataloader->AddTree(mvaTree, "Signal"    , 1.0, cutTestSignal , "test");
  dataloader->AddTree(mvaTree, "Background", 1.0, cutTestBkg    , "test");
  //dataloader->SetWeightExpression("abs(weight)", "Signal");
  //dataloader->SetWeightExpression("abs(weight)", "Background");
  dataloader->SetWeightExpression("1.0", "Signal");
  dataloader->SetWeightExpression("1.0", "Background");
  
  if(nsel == 0 || nsel == 1 || nsel == 2){
    dataloader->AddVariable("ngood_jets","ngood_jets","",'F');
    dataloader->AddVariable("vbs_mjj"       ,"vbs_mjj"       ,"",'F');
    dataloader->AddVariable("vbs_ptjj"      ,"vbs_ptjj"      ,"",'F');
    dataloader->AddVariable("vbs_detajj"    ,"vbs_detajj"    ,"",'F');
    dataloader->AddVariable("vbs_dphijj"    ,"vbs_dphijj"    ,"",'F');
    dataloader->AddVariable("vbs_ptj1"      ,"vbs_ptj1"      ,"",'F');
    dataloader->AddVariable("vbs_ptj2"      ,"vbs_ptj2"      ,"",'F');
    dataloader->AddVariable("vbs_etaj1"     ,"vbs_etaj1"     ,"",'F');
    dataloader->AddVariable("vbs_etaj2"     ,"vbs_etaj2"     ,"",'F');
    dataloader->AddVariable("vbs_zepvv"     ,"vbs_zepvv"     ,"",'F');
    //dataloader->AddVariable("vbs_zepmax"    ,"vbs_zepmax"    ,"",'F');
    dataloader->AddVariable("vbs_sumHT"     ,"vbs_sumHT"     ,"",'F');
    //dataloader->AddVariable("vbs_ptvv"      ,"vbs_ptvv"      ,"",'F');
    dataloader->AddVariable("vbs_pttot"     ,"vbs_pttot"     ,"",'F');
    dataloader->AddVariable("vbs_detavvj1"  ,"vbs_detavvj1"  ,"",'F');
    dataloader->AddVariable("vbs_detavvj2"  ,"vbs_detavvj2"  ,"",'F');
    dataloader->AddVariable("vbs_ptbalance" ,"vbs_ptbalance" ,"",'F');
  }

  TString prepareOptions="NormMode=None";
    prepareOptions+=":SplitMode=Block"; // use e.g. all events selected by trainTreeEventSplitStr for training
    prepareOptions+=":MixMode=Random";
  dataloader->PrepareTrainingAndTestTree("", prepareOptions);

  TString hyperparameters;

  hyperparameters=
  "!H:!V:NTrees=1000:BoostType=Grad:MinNodeSize=10%:NegWeightTreatment=IgnoreNegWeightsInTraining:Shrinkage=0.10:UseBaggedBoost:GradBaggingFraction=0.3:nCuts=1000:MaxDepth=3";
  factory->BookMethod(dataloader, TMVA::Types::kBDT, Form("BDTG_%s",extraString.Data()), hyperparameters);

  TString layoutString ("Layout=TANH|100,TANH|50,TANH|10,LINEAR");

  TString training0 ("LearningRate=1e-1,Momentum=0.0,Repetitions=1,ConvergenceSteps=300,BatchSize=20,TestRepetitions=15,WeightDecay=0.001,Regularization=NONE,DropConfig=0.0+0.5+0.5+0.5,DropRepetitions=1,Multithreading=True");
  TString training1 ("LearningRate=1e-2,Momentum=0.5,Repetitions=1,ConvergenceSteps=300,BatchSize=30,TestRepetitions=7,WeightDecay=0.001,Regularization=L2,Multithreading=True,DropConfig=0.0+0.1+0.1+0.1,DropRepetitions=1");
  TString training2 ("LearningRate=1e-2,Momentum=0.3,Repetitions=1,ConvergenceSteps=300,BatchSize=40,TestRepetitions=7,WeightDecay=0.0001,Regularization=L2,Multithreading=True");
  TString training3 ("LearningRate=1e-3,Momentum=0.1,Repetitions=1,ConvergenceSteps=200,BatchSize=70,TestRepetitions=7,WeightDecay=0.0001,Regularization=NONE,Multithreading=True");
  
  TString trainingStrategyString ("TrainingStrategy=");
  //trainingStrategyString += training0 + "|" + training1 + "|" + training2 + "|" + training3;
  trainingStrategyString += training0 + "|" + training1 + "|" + training2;

  // General Options.
  TString dnnOptions ("!H:V:ErrorStrategy=CROSSENTROPY:VarTransform=N:"
		      "WeightInitialization=XAVIERUNIFORM");
  dnnOptions.Append (":"); dnnOptions.Append (layoutString);
  dnnOptions.Append (":"); dnnOptions.Append (trainingStrategyString);
  
  // Standard implementation, no dependencies.
  TString stdOptions = dnnOptions + ":Architecture=CPU";
  if(dodnn)
    factory->BookMethod(dataloader, TMVA::Types::kDNN, "DNN", stdOptions);

  if(moreMVAs){
  hyperparameters=
  "!H:!V:BoostType=AdaBoost:MinNodeSize=10%:NegWeightTreatment=IgnoreNegWeightsInTraining:SeparationType=MisClassificationError:NTrees=1000:MaxDepth=3:AdaBoostBeta=0.12:nCuts=10000";
  factory->BookMethod(dataloader, TMVA::Types::kBDT, Form("BDTA_%s",extraString.Data()), hyperparameters);

  hyperparameters=
  "!H:!V:VarTransform=None";
  factory->BookMethod(dataloader, TMVA::Types::kHMatrix, Form("HMatrix_%s",extraString.Data()), hyperparameters);

  hyperparameters=
  "!H:!V:!TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmooth=5:NAvEvtPerBin=70:VarTransform=PCA";
  factory->BookMethod(dataloader, TMVA::Types::kLikelihood, Form("LikelihoodPCA_%s",extraString.Data()), hyperparameters);

  hyperparameters=
  "!H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmoothBkg[1]=10:NSmooth=1:NAvEvtPerBin=70";
  factory->BookMethod(dataloader, TMVA::Types::kLikelihood, Form("Likelihood_%s",extraString.Data()), hyperparameters);

  hyperparameters=
  "!H:!V:Fisher:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=40:NsmoothMVAPdf=10";
  factory->BookMethod(dataloader, TMVA::Types::kFisher, Form("Fisher_%s",extraString.Data()), hyperparameters);

  hyperparameters=
  "!H:!V:!TransformOutput:PDFInterpol=KDE:KDEtype=Gauss:KDEiter=Adaptive:KDEFineFactor=0.3:KDEborder=None:NAvEvtPerBin=70";
  factory->BookMethod(dataloader, TMVA::Types::kLikelihood, Form("LikelihoodKDE_%s",extraString.Data()), hyperparameters);

  hyperparameters=
  "H:!V:Boost_Num=30:Boost_Transform=log:Boost_Type=AdaBoost:Boost_AdaBoostBeta=0.3:!Boost_DetailedMonitoring";
  factory->BookMethod(dataloader, TMVA::Types::kFisher, Form("BoostedFisher_%s",extraString.Data()), hyperparameters);

   hyperparameters=
  "!H:!V:NeuronType=tanh:VarTransform=N:NCycles=1000:HiddenLayers=N+3:TestRate=5:!UseRegulator";
  factory->BookMethod(dataloader, TMVA::Types::kMLP, Form("MLP_%s",extraString.Data()), hyperparameters);
  }

  factory->TrainAllMethods();
  factory->TestAllMethods();
  factory->EvaluateAllMethods();
  output_file->Close();
}
