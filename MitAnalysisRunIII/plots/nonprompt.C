// overlay_dd_mm.C — run with: root overlay_dd_mm.C
// DD (filled purple) vs MM (black line) with statistical error bars (E1) for both.
// Saves PNG, PDF, EPS. CMS + lumi stamp. Larger axis fonts.

#include <TFile.h>
#include <TH1.h>
#include <TCanvas.h>
#include <TLegend.h>
#include <TStyle.h>
#include <TSystem.h>
#include <TROOT.h>
#include <TColor.h>
#include <TAxis.h>
#include <TLatex.h>

#include <vector>
#include <string>
#include <algorithm>
#include <iostream>

// ----------------- knobs you can tweak -----------------
static const int    kAnaId        = 1001;
static const int    kYear         = 2027;
static const bool   kNormalize    = false;   // keep OFF
static const int    kRebin        = 1;
static const double kHeadroom     = 2.0;     // y-max = headroom * peak
static const int    kYDivisions   = 505;     // fewer Y ticks (primary=5, minor=5)
static const bool   kLogY         = false;   // set true if you want log-y
static const char*  kOutDir       = "DDMM_plots_2027";
// -------------------------------------------------------

static TH1* GetTH1FromFile(const char* path, const char* key) {
  TFile* f = TFile::Open(path, "READ");
  if (!f || f->IsZombie()) {
    std::cerr << "[ERROR] Cannot open: " << path << "\n";
    if (f) f->Close();
    return nullptr;
  }
  TH1* h = nullptr;
  f->GetObject(key, h);
  if (!h) {
    std::cerr << "[ERROR] Key \"" << key << "\" not found in " << path << "\n";
    f->GetListOfKeys()->Print();
    f->Close();
    return nullptr;
  }
  TH1* c = (TH1*)h->Clone();
  c->SetDirectory(nullptr);
  c->Sumw2();
  f->Close();
  return c;
}

static void StyleDD(TH1* h) {
  if (!h) return;
  const int purpleFill = TColor::GetColor("#7B3294");
  const int purpleLine = TColor::GetColor("#4E196C");
  h->SetFillColor(purpleFill);
  h->SetFillStyle(1001);
  h->SetLineColor(purpleLine);
  h->SetLineWidth(2);
}

static void StyleMM(TH1* h) {
  if (!h) return;
  h->SetFillStyle(0);
  h->SetLineColor(kBlack);
  h->SetLineWidth(3);
}

static void DrawCMSLumi(const char* lumiText = "Run 3, 171 fb^{-1} (13.6 TeV)",
                        double cmsX=0.14, double cmsY=0.92,
                        double lumiX=0.95, double lumiY=0.92,
                        double cmsSize=0.072, double lumiSize=0.060)
{
  TLatex cms;  cms.SetNDC(); cms.SetTextFont(62); cms.SetTextSize(cmsSize);
  cms.DrawLatex(cmsX, cmsY, "CMS");
  TLatex lumi; lumi.SetNDC(); lumi.SetTextFont(42); lumi.SetTextSize(lumiSize); lumi.SetTextAlign(31);
  lumi.DrawLatex(lumiX, lumiY, lumiText);
}

static void OverlayAndSave(TH1* hDD, TH1* hMM,
                           const char* xaxisTitle,
                           const char* outBase,
                           bool /*normalizeShape*/,
                           int rebin)
{
  if (!hDD || !hMM) return;
  if (rebin > 1) { hDD->Rebin(rebin); hMM->Rebin(rebin); }

  hDD->SetName(std::string(std::string(hDD->GetName()) + "_DD").c_str());
  hMM->SetName(std::string(std::string(hMM->GetName()) + "_MM").c_str());

  StyleDD(hDD);
  StyleMM(hMM);

  hDD->GetXaxis()->SetTitle(xaxisTitle);
  hMM->GetXaxis()->SetTitle(xaxisTitle);
  const char* yTitle = "Events / bin";
  hDD->GetYaxis()->SetTitle(yTitle);
  hMM->GetYaxis()->SetTitle(yTitle);

  hDD->GetXaxis()->SetTitleSize(0.060);
  hDD->GetXaxis()->SetLabelSize(0.048);
  hDD->GetYaxis()->SetTitleSize(0.060);
  hDD->GetYaxis()->SetLabelSize(0.048);
  hDD->GetYaxis()->SetTitleOffset(0.8);
  hDD->GetYaxis()->SetNdivisions(kYDivisions);

  hDD->SetTitle("");
  hMM->SetTitle("");

  // --- Stat error bars setup (E1) for both ---
  gStyle->SetErrorX(0);       // no horizontal caps (pure vertical)
  gStyle->SetEndErrorSize(3); // cap size in pixels

  TH1* hDDerr = (TH1*)hDD->Clone((std::string(hDD->GetName())+"_err").c_str());
  hDDerr->SetDirectory(nullptr);
  hDDerr->SetMarkerStyle(20);
  hDDerr->SetMarkerSize(0.7);
  hDDerr->SetLineColor(hDD->GetLineColor());
  hDDerr->SetLineWidth(1);

  TH1* hMMerr = (TH1*)hMM->Clone((std::string(hMM->GetName())+"_err").c_str());
  hMMerr->SetDirectory(nullptr);
  hMMerr->SetMarkerStyle(20);
  hMMerr->SetMarkerSize(0.7);
  hMMerr->SetLineColor(kBlack);
  hMMerr->SetLineWidth(1);

  // Y range with headroom
  double maxy = std::max(hDD->GetMaximum(), hMM->GetMaximum());

  TCanvas c("c", "", 900, 700);
  c.SetLeftMargin(0.12);
  c.SetRightMargin(0.05);
  c.SetBottomMargin(0.12);
  c.SetTopMargin(0.12);
  gStyle->SetOptStat(0);
  c.SetLogy(kLogY);

  if (kLogY) {
    double minPos = 1e30;
    for (int b=1; b<=hDD->GetNbinsX(); ++b) { double v=hDD->GetBinContent(b); if (v>0 && v<minPos) minPos=v; }
    for (int b=1; b<=hMM->GetNbinsX(); ++b) { double v=hMM->GetBinContent(b); if (v>0 && v<minPos) minPos=v; }
    if (!(minPos>0)) minPos = 0.5;
    hDD->SetMinimum(minPos*0.5);
    hDD->SetMaximum(maxy*5.0);
  } else {
    hDD->SetMinimum(0.0);
    hDD->SetMaximum(kHeadroom * maxy);
  }

  // Draw order: histograms then both sets of error bars
  hDD->Draw("HIST");
  hMM->Draw("HIST SAME");
  hDDerr->Draw("E1 SAME");
  hMMerr->Draw("E1 SAME");

  TLegend leg(0.62, 0.68, 0.90, 0.84);
  leg.SetBorderSize(0);
  leg.SetFillStyle(0);
  leg.AddEntry(hDD, "Fakerate method", "f");
  leg.AddEntry(hMM, "Matrix method", "l");
  leg.Draw();
  // Legend
//  TLegend leg(0.62, 0.62, 0.92, 0.88);
//  leg.SetBorderSize(0);
//  leg.SetFillStyle(0);
//  leg.AddEntry(hDD,    "Fakerate method", "f");
//  leg.AddEntry(hMM,    "Matrix method",   "l");
//  leg.AddEntry(hDDerr, "DD stat. unc.",   "lep");
//  leg.AddEntry(hMMerr, "MM stat. unc.",   "lep");
  leg.Draw();

  DrawCMSLumi("Run 3, 171 fb^{-1} (13.6 TeV)", 0.14, 0.90, 0.93, 0.90, 0.072, 0.060);

  TString png = TString::Format("%s.png", outBase);
  TString pdf = TString::Format("%s.pdf", outBase);
  TString eps = TString::Format("%s.eps", outBase);
  c.SaveAs(png);
  c.SaveAs(pdf);
  c.SaveAs(eps);

  delete hDDerr;
  delete hMMerr;
}

// ---------- named macro entrypoint (no args) ----------
void nonprompt()
{
  gSystem->mkdir(kOutDir, kTRUE);

  const char* ddDir = "/mnt/home/mghimiray/VBSStudies/Outputs_VBS/DataDriven/1001/merge3";
  const char* mmDir = "/mnt/home/mghimiray/VBSStudies/Outputs_VBS/OriginalTT/1001/merge3";

  struct Item { int code; const char* outname; const char* xaxis; };
  std::vector<Item> items = {
    {17, "sswwbvbs_ptmiss",         "E_{T}^{miss} [GeV]"},
    {19, "sswwbvbssel_ltype",       "Lepton type"},
    {21, "sswwbvbssel_njets",       "N_{jets}"},
    {23, "sswwbvbssel_mjj",         "m_{jj} [GeV]"},
    {25, "sswwbvbssel_detajj",      "|#Delta#eta_{jj}|"},
    {27, "sswwbvbssel_dphijj",      "|#Delta#phi_{jj}|"},
    {31, "sswwbvbssel_bdt_vbfincl", "BDT (VBF incl.)"},
    {33, "sswwbvbssel_ptj1",        "p_{T}^{j1} [GeV]"},
    {35, "sswwbvbssel_ptj2",        "p_{T}^{j2} [GeV]"},
    {37, "sswwbvbssel_etaj1",       "#eta^{j1}"},
    {39, "sswwbvbssel_etaj2",       "#eta^{j2}"}
  };

  for (const auto& it : items) {
    TString ddPath = TString::Format("%s/fillhisto_sswwAnalysis%d_%d_%d.root", ddDir, kAnaId, kYear, it.code);
    TString mmPath = TString::Format("%s/fillhisto_sswwAnalysis%d_%d_%d.root", mmDir, kAnaId, kYear, it.code);

    TH1* hDD = GetTH1FromFile(ddPath.Data(), "histo11");
    TH1* hMM = GetTH1FromFile(mmPath.Data(), "histo11");

    if (!hDD || !hMM) {
      std::cerr << "[WARN] Skipping " << it.outname << " (missing hist)\n";
      if (hDD) delete hDD;
      if (hMM) delete hMM;
      continue;
    }

    hDD->SetName(it.outname);
    hMM->SetName(it.outname);

    TString outBase  = TString::Format("%s/%s", kOutDir, it.outname);
    OverlayAndSave(hDD, hMM, it.xaxis, outBase.Data(), kNormalize, kRebin);

    delete hDD;
    delete hMM;
  }

  std::cout << "[OK] Plots written in: " << kOutDir << "\n";
}
