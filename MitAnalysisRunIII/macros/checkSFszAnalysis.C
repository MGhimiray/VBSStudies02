void checkSFszAnalysis(int nsel, int year, int ana = 1001){
TFile *_file0 = TFile::Open(Form("anaZ/fillhisto_zAnalysis%d_%d_12.root",ana,year));
TFile *_file1 = TFile::Open(Form("anaZ/fillhisto_zAnalysis%d_%d_13.root",ana,year));
TFile *_file2 = TFile::Open(Form("anaZ/fillhisto_zAnalysis%d_%d_14.root",ana,year));
TFile *_file3 = TFile::Open(Form("anaZ/fillhisto_zAnalysis%d_%d_%d.root",ana,year,216+3*nsel));
TFile *_file4 = TFile::Open(Form("anaZ/fillhisto_zAnalysis%d_%d_%d.root",ana,year,217+3*nsel));
TFile *_file5 = TFile::Open(Form("anaZ/fillhisto_zAnalysis%d_%d_%d.root",ana,year,218+3*nsel));

TH1D *histo0 =  (TH1D*)_file0->Get(Form("histo5"));
TH1D *histo1 =  (TH1D*)_file1->Get(Form("histo5"));
TH1D *histo2 =  (TH1D*)_file2->Get(Form("histo5"));
TH1D *histo3 =  (TH1D*)_file3->Get(Form("histo5"));
TH1D *histo4 =  (TH1D*)_file4->Get(Form("histo5"));
TH1D *histo5 =  (TH1D*)_file5->Get(Form("histo5"));

TString nameSel[6]  = {"BTVSF", "PUxxx", "TrgSF", "Muoxx", "Elexx", "WSxxx"};

printf("%s %.3f %.3f %.3f\n",nameSel[nsel].Data(),histo0->GetSumOfWeights()/histo3->GetSumOfWeights(),histo1->GetSumOfWeights()/histo4->GetSumOfWeights(),histo2->GetSumOfWeights()/histo5->GetSumOfWeights());
}
