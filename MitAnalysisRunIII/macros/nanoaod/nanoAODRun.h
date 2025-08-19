//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Fri May  1 13:29:12 2020 by ROOT version 6.12/07
// from TTree Runs/Runs
// found on file: /afs/cern.ch/work/c/ceballos/public/samples/nanoaod/WpWpJJ_EWK_TuneCP5_13TeV-madgraph-pythia8.root
//////////////////////////////////////////////////////////

#ifndef nanoAODRun_h
#define nanoAODRun_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.

class nanoAODRun {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

// Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   UInt_t          run;
   Long64_t        genEventCount;
   Double_t        genEventSumw;
   Double_t        genEventSumw2;
   UInt_t          nLHEScaleSumw;
   Double_t        LHEScaleSumw[9];   //[nLHEScaleSumw]
   UInt_t          nLHEPdfSumw;
   Double_t        LHEPdfSumw[33];   //[nLHEPdfSumw]

   // List of branches
   TBranch        *b_run;   //!
   TBranch        *b_genEventCount;   //!
   TBranch        *b_genEventSumw;   //!
   TBranch        *b_genEventSumw2;   //!
   TBranch        *b_nLHEScaleSumw;   //!
   TBranch        *b_LHEScaleSumw;   //!
   TBranch        *b_nLHEPdfSumw;   //!
   TBranch        *b_LHEPdfSumw;   //!

   nanoAODRun(TTree *tree=0);
   virtual ~nanoAODRun();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif

#ifdef nanoAODRun_cxx
nanoAODRun::nanoAODRun(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("/afs/cern.ch/work/c/ceballos/public/samples/nanoaod/WpWpJJ_EWK_TuneCP5_13TeV-madgraph-pythia8.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("/afs/cern.ch/work/c/ceballos/public/samples/nanoaod/WpWpJJ_EWK_TuneCP5_13TeV-madgraph-pythia8.root");
      }
      f->GetObject("Runs",tree);

   }
   Init(tree);
}

nanoAODRun::~nanoAODRun()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t nanoAODRun::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t nanoAODRun::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
   if (!fChain) return -5;
   Long64_t centry = fChain->LoadTree(entry);
   if (centry < 0) return centry;
   if (fChain->GetTreeNumber() != fCurrent) {
      fCurrent = fChain->GetTreeNumber();
      Notify();
   }
   return centry;
}

void nanoAODRun::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("run", &run, &b_run);
   fChain->SetBranchAddress("genEventCount", &genEventCount, &b_genEventCount);
   fChain->SetBranchAddress("genEventSumw", &genEventSumw, &b_genEventSumw);
   fChain->SetBranchAddress("genEventSumw2", &genEventSumw2, &b_genEventSumw2);
   fChain->SetBranchAddress("nLHEScaleSumw", &nLHEScaleSumw, &b_nLHEScaleSumw);
   fChain->SetBranchAddress("LHEScaleSumw", LHEScaleSumw, &b_LHEScaleSumw);
   fChain->SetBranchAddress("nLHEPdfSumw", &nLHEPdfSumw, &b_nLHEPdfSumw);
   fChain->SetBranchAddress("LHEPdfSumw", LHEPdfSumw, &b_LHEPdfSumw);
   Notify();
}

Bool_t nanoAODRun::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void nanoAODRun::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t nanoAODRun::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef nanoAODRun_cxx
