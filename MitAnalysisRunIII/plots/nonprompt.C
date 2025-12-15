// overlay_dd_mm.C — run with: root -l -b -q overlay_dd_mm.C
// DD (filled purple) vs MM (black line) with optional normalization,
// and a bottom ratio panel: (Fake-rate / Matrix). Saves PNG, PDF, EPS.

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
#include <TPad.h>
#include <TLine.h>

#include <vector>
#include <string>
#include <algorithm>
#include <iostream>

// ----------------- knobs you can tweak -----------------
static const int    kAnaId        = 1001;
static const int    kYear         = 2027;
static const bool   kNormalize    = true;    // normalize both histos to unit area (with bin-width)
static const int    kRebin        = 1;
static const double kHeadroom     = 2.0;     // y-max = headroom * peak (for linear y)
static const int    kYDivisions   = 505;     // fewer Y ticks (primary=5, minor=5)
static const bool   kLogY         = false;   // log scale for top panel
static const char*  kOutDir       = "DDMM_plots_2027";

// Ratio panel controls
static const bool   kShowRatio    = true;
static const double kRatioYmin    = 0.5;
static const double kRatioYmax    = 1.5;
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
                           bool normalizeShape,
                           int rebin)
{
  if (!hDD || !hMM) return;

  if (rebin > 1) { hDD->Rebin(rebin); hMM->Rebin(rebin); }

  hDD->SetName(std::string(std::string(hDD->GetName()) + "_DD").c_str());
  hMM->SetName(std::string(std::string(hMM->GetName()) + "_MM").c_str());

  StyleDD(hDD);
  StyleMM(hMM);

  // Axis titles (top panel will hide X, ratio will carry X)
  const char* yTitle = "Events / bin";
  hDD->GetXaxis()->SetTitle(xaxisTitle);
  hMM->GetXaxis()->SetTitle(xaxisTitle);
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

  // --- Normalize to unit area with bin-width if requested ---
  if (normalizeShape) {
    const int nbx = hDD->GetNbinsX();
    double intDD = hDD->Integral(1, nbx, "width");
    double intMM = hMM->Integral(1, nbx, "width");
    if (intDD > 0) hDD->Scale(1.0 / intDD, "width");
    if (intMM > 0) hMM->Scale(1.0 / intMM, "width");
  }

  // Stat error bar styling (if you choose to draw E1)
  gStyle->SetErrorX(0);
  gStyle->SetEndErrorSize(3);

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

  // Y-range headroom (for top)
  double maxy = std::max(hDD->GetMaximum(), hMM->GetMaximum());

  // ------------ Canvas with ratio pad ------------
  TCanvas c("c", "", 900, 700);
  gStyle->SetOptStat(0);

  // Pads: top (pad1) and bottom (pad2)
  TPad* pad1 = new TPad("pad1","pad1", 0.0, kShowRatio ? 0.30 : 0.0, 1.0, 1.0);
  TPad* pad2 = nullptr;
  pad1->SetLeftMargin(0.12);
  pad1->SetRightMargin(0.05);
  pad1->SetTopMargin(0.12);
  pad1->SetBottomMargin(kShowRatio ? 0.02 : 0.12);
  pad1->SetTicks(1,1);
  pad1->SetLogy(kLogY);
  pad1->Draw();

  if (kShowRatio) {
    pad2 = new TPad("pad2","pad2", 0.0, 0.0, 1.0, 0.30);
    pad2->SetLeftMargin(0.12);
    pad2->SetRightMargin(0.05);
    pad2->SetTopMargin(0.02);
    pad2->SetBottomMargin(0.38);
    pad2->SetGridy(true);
    pad2->SetTicks(1,1);
    pad2->Draw();
  }

  // ------------ Top pad (main histograms) ------------
  pad1->cd();

  if (kLogY) {
    double minPos = 1e30;
    for (int b=1; b<=hDD->GetNbinsX(); ++b) { double v=hDD->GetBinContent(b); if (v>0 && v<minPos) minPos=v; }
    for (int b=1; b<=hMM->GetNbinsX(); ++b) { double v=hMM->GetBinContent(b); if (v>0 && v<minPos) minPos=v; }
    if (!(minPos>0)) minPos = 5e-4;
    hDD->SetMinimum(minPos*0.5);
    hDD->SetMaximum(maxy*5.0);
  } else {
    hDD->SetMinimum(0.0);
    hDD->SetMaximum(kHeadroom * maxy);
  }

  // Hide X on top; ratio will carry it
  hDD->GetXaxis()->SetLabelSize(kShowRatio ? 0.0 : 0.048);
  hDD->GetXaxis()->SetTitleSize(kShowRatio ? 0.0 : 0.060);

  // Draw order
  hDD->Draw("HIST");
  hMM->Draw("HIST SAME");
  // Uncomment if you want error bars on top:
  // hDDerr->Draw("E1 SAME");
  // hMMerr->Draw("E1 SAME");

  // Legend
  TLegend leg(0.62, 0.68, 0.90, 0.84);
  leg.SetBorderSize(0);
  leg.SetFillStyle(0);
  leg.AddEntry(hDD, "Fake-rate method", "f");
  leg.AddEntry(hMM, "Matrix method", "l");
  leg.Draw();

  DrawCMSLumi("Run 3, 171 fb^{-1} (13.6 TeV)", 0.14, 0.90, 0.93, 0.90, 0.072, 0.060);

  // ------------ Bottom pad (ratio) ------------
  TH1* hRatio = nullptr;
  if (kShowRatio) {
    pad2->cd();
    hRatio = (TH1*)hDD->Clone((std::string(hDD->GetName())+"_ratio").c_str());
    hRatio->SetDirectory(nullptr);
    // Protect against division by zero
    for (int b=1; b<=hRatio->GetNbinsX(); ++b) {
      double denom = hMM->GetBinContent(b);
      if (denom == 0.0) {
        hRatio->SetBinContent(b, 0.0);
        hRatio->SetBinError(b, 0.0);
      }
    }
    hRatio->Divide(hMM);

    // Style
    hRatio->SetTitle("");
    hRatio->SetLineColor(kBlack);
    hRatio->SetLineWidth(1);
    hRatio->SetMarkerStyle(20);
    hRatio->SetMarkerSize(0.8);
    hRatio->SetMarkerColor(kBlack);

    // Axes
    hRatio->GetYaxis()->SetTitle("Fake-rate / Matrix");
    hRatio->GetYaxis()->SetNdivisions(505);
    hRatio->GetYaxis()->SetTitleSize(0.11);
    hRatio->GetYaxis()->SetTitleOffset(0.5);
    hRatio->GetYaxis()->SetLabelSize(0.10);

    hRatio->GetXaxis()->SetTitle(xaxisTitle);
    hRatio->GetXaxis()->SetTitleSize(0.12);
    hRatio->GetXaxis()->SetLabelSize(0.11);
    hRatio->GetXaxis()->SetTickLength(0.06);

    hRatio->SetMinimum(kRatioYmin);
    hRatio->SetMaximum(kRatioYmax);

    hRatio->Draw("E1");

    // Unity line
    double xmin = hRatio->GetXaxis()->GetXmin();
    double xmax = hRatio->GetXaxis()->GetXmax();
    TLine line(xmin, 1.0, xmax, 1.0);
    line.SetLineStyle(2);
    line.SetLineWidth(2);
    line.Draw("SAME");
  }

  // ------------ Save ------------
  c.cd();
  TString png = TString::Format("%s.png", outBase);
  TString pdf = TString::Format("%s.pdf", outBase);
  TString eps = TString::Format("%s.eps", outBase);
  c.SaveAs(png);
  c.SaveAs(pdf);
  c.SaveAs(eps);

  delete hDDerr;
  delete hMMerr;
  if (hRatio) delete hRatio;
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
