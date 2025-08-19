#include<vector>

#if !defined (__CINT__) || defined (__MAKECINT__)
#include "THStack.h"
#include "TGaxis.h"
#include "TH1F.h"
#include "TLatex.h"
#include "TPad.h"
#include "TCanvas.h"
#include "TAxis.h"
#include "TLegend.h"
#include "TFrame.h"
#include "TExec.h"
#include <iostream>
#include "TPaveText.h"
#endif

Bool_t isBSMOverlaid = true;

//float xPos[nPlotCategories] = {0.70,0.70,0.70,0.70,0.70,0.70,0.70,0.40,0.40,0.40,0.40,0.40,0.40,0.40,0.40};
float xPos[nPlotCategories] = {0.67,0.67,0.67,0.67,0.67,0.67,0.67,0.43,0.43,0.43,0.43,0.43,0.43,0.43,0.43};
float yOff[nPlotCategories] = {   0,	1,   2,   3,   4,  5,   6,   0,   1,   2,   3,   4,   5,   6,   7};

const Float_t _tsize   = 0.050;
const Float_t _xoffset = 0.200;
const Float_t _yoffset = 0.051;

const double SFBinWidth = 1;

//------------------------------------------------------------------------------
// GetMaximumIncludingErrors
//------------------------------------------------------------------------------
Float_t GetMaximumIncludingErrors(TH1F* h, bool doApplyBinWidth)
{
    Float_t maxWithErrors = 0;

    for (Int_t i=1; i<=h->GetNbinsX(); i++) {

        Float_t binHeight = h->GetBinContent(i) + h->GetBinError(i);

        if(doApplyBinWidth) binHeight = binHeight/h->GetBinWidth(i)*SFBinWidth;

        if (binHeight > maxWithErrors) maxWithErrors = binHeight;
    }

    return maxWithErrors;
}

//------------------------------------------------------------------------------
// GetMinimumIncludingErrors
//------------------------------------------------------------------------------
Float_t GetMinimumIncludingErrors(TH1F* h, bool doApplyBinWidth)
{
    Float_t minWithErrors = 100000000;

    for (Int_t i=1; i<=h->GetNbinsX(); i++) {

        Float_t binHeight = h->GetBinContent(i) + h->GetBinError(i);

        if(doApplyBinWidth) binHeight = binHeight/h->GetBinWidth(i)*SFBinWidth;

        if (binHeight < minWithErrors) minWithErrors = binHeight;
    }

    return minWithErrors;
}


//------------------------------------------------------------------------------
// AxisFonts
//------------------------------------------------------------------------------
void AxisFonts(TAxis*  axis,
        TString coordinate,
        TString title,
	bool doApplyBinWidth)
{
    axis->SetLabelFont  (   42);
    axis->SetLabelOffset(0.010);
    axis->SetLabelSize  (0.045);
    axis->SetNdivisions (  505);
    axis->SetTitleFont  (   42);
    axis->SetTitleOffset(  0.9);
    axis->SetTitleSize  (0.050);

    if      (coordinate == "y" && doApplyBinWidth == true) axis->SetTitleOffset(0.9);
    else if (coordinate == "y")                            axis->SetTitleOffset(0.9);

    axis->SetTitle(title);
}

//------------------------------------------------------------------------------
// THStackAxisFonts
//------------------------------------------------------------------------------
void THStackAxisFonts(THStack* h,
        TString  coordinate,
        TString  title,
	bool doApplyBinWidth)
{
    TAxis* axis = NULL;

    if (coordinate.Contains("x")) axis = h->GetHistogram()->GetXaxis();
    if (coordinate.Contains("y")) axis = h->GetHistogram()->GetYaxis();

    AxisFonts(axis, coordinate, title, doApplyBinWidth);
}

//------------------------------------------------------------------------------
// DrawLegend
//------------------------------------------------------------------------------
void DrawLegend(Float_t x1,
        Float_t y1,
        TH1F*   hist,
        TString label,
        TString option)
{
    TLegend* legend = new TLegend(x1,
            y1,
            x1 + _xoffset,
            y1 + _yoffset);

    legend->SetBorderSize  (     0);
    legend->SetFillColor   (     0);
    legend->SetTextAlign   (    12);
    legend->SetTextFont    (    62);
    legend->SetTextSize    (_tsize);
    legend->SetShadowColor(      0);

    legend->AddEntry(hist, label.Data(), option.Data());

    legend->Draw();
}

void DrawLegendTG(Float_t x1,
        Float_t y1,
        TGraph  *hist,
        TString label,
        TString option)
{
    TLegend* legend = new TLegend(x1,
            y1,
            x1 + _xoffset,
            y1 + _yoffset);

    legend->SetBorderSize(     0);
    legend->SetFillColor (     0);
    legend->SetTextAlign (    12);
    legend->SetTextFont  (    62);
    legend->SetTextSize  (_tsize);

    legend->AddEntry(hist, label.Data(), option.Data());

    legend->Draw();
}

class StandardPlot {

    public: 
        StandardPlot() { _doApplyBinWidth = false; _hist.resize(nPlotCategories,0); _hist[kPlotData] = 0; _breakdown = false; _HiggsLabel = ""; _Higgs2Label = "";_labelEM = " Nonprompt";_labelVVV = " VVV";}
        void setMCHist   (int s, TH1F * h)  { _hist[s] = h;} 
        void setAllHist  (TH1F * h)         { _hist_total = h;} 
        void setOverlaid  (bool b)   { isBSMOverlaid = b;   }
        void setLabelEM   (TString s){ _labelEM  = s.Data();}
        void setLabelVVV  (TString s){ _labelVVV = s.Data();}

  TH1F* getDataHist() { return _hist[kPlotData]; }

        void setHiggsLabel  (TString s) {_HiggsLabel =s;}
        void setHiggs2Label (TString s) {_Higgs2Label=s;}

        TH1* DrawAndRebinTo(const int &rebinTo) {

            if(rebinTo == 0) return Draw();
            int rebin = 0, nbins = 0;
            for (int i=0; i<nPlotCategories; i++) {

                // in case the user doesn't set it
                if( !_hist[i] ) continue;

                nbins = _hist[i]->GetNbinsX();
            }
            if (nbins == 0) return Draw();

            rebin = nbins / rebinTo;
            while(nbins % rebin != 0) rebin--;
            return Draw(rebin);

        }

        TH1* Draw(const int &rebin=1) {

            THStack* hstack = new THStack();
	    TH1D* hSum = 0;
	    for(int ic=0; ic<nPlotCategories; ic++) if(_hist[ic]) {hSum = (TH1D*)_hist[ic]->Clone(); break;}
	    hSum->Rebin(rebin);
	    hSum->Scale(0.0);
            //for (int ic=0; ic<nPlotCategories; ic++) {
            for (int ic=nPlotCategories-1; ic>=0; ic--) {

                // in case the user doesn't set it
                if( !_hist[ic] || ic == kPlotData) continue;
                _hist[ic]->Rebin(rebin);
                _hist[ic]->SetLineColor(plotColors[ic]);
	       //for(int i=1; i<=_hist[ic]->GetNbinsX(); i++) if(_hist[ic]->GetBinContent(i)<0) _hist[ic]->SetBinContent(i,0);

                if(_doApplyBinWidth == true){
                  _hist[ic]->Scale(1,"width");
                }

                // signal gets overlaid
                if (ic == kPlotBSM && isBSMOverlaid == false) continue;
                if (ic == kPlotSignal0 && isBSMOverlaid == false) continue;
                if (ic == kPlotSignal1 && isBSMOverlaid == false) continue;
                if (ic == kPlotSignal2 && isBSMOverlaid == false) continue;
                if (ic == kPlotSignal3 && isBSMOverlaid == false) continue;

                _hist[ic]->SetFillColor(plotColors[ic]);
                _hist[ic]->SetFillStyle(1001);

                hstack->Add(_hist[ic]);
		hSum  ->Add(_hist[ic]);
            }
            if(_hist_total) for(int i=1; i<=_hist_total->GetNbinsX(); i++) {hSum->SetBinError(i,_hist_total->GetBinError(i));}

            if(_hist[kPlotBSM]    ) _hist[kPlotBSM    ]->SetLineWidth(4);
            if(_hist[kPlotSignal0]) _hist[kPlotSignal0]->SetLineWidth(4);
            if(_hist[kPlotSignal1]) _hist[kPlotSignal1]->SetLineWidth(4);
            if(_hist[kPlotSignal2]) _hist[kPlotSignal2]->SetLineWidth(4);
            if(_hist[kPlotSignal3]) _hist[kPlotSignal3]->SetLineWidth(4);

            if(_hist[kPlotBSM]    ) _hist[kPlotBSM    ]->SetFillColor(0);
            if(_hist[kPlotSignal0]) _hist[kPlotSignal0]->SetFillColor(0);
            if(_hist[kPlotSignal1]) _hist[kPlotSignal1]->SetFillColor(0);
            if(_hist[kPlotSignal2]) _hist[kPlotSignal2]->SetFillColor(0);
            if(_hist[kPlotSignal3]) _hist[kPlotSignal3]->SetFillColor(0);

            if(_hist[kPlotBSM]    ) _hist[kPlotBSM    ]->SetFillStyle(3001);
            if(_hist[kPlotSignal0]) _hist[kPlotSignal0]->SetFillStyle(3002);
            if(_hist[kPlotSignal1]) _hist[kPlotSignal1]->SetFillStyle(3002);
            if(_hist[kPlotSignal2]) _hist[kPlotSignal2]->SetFillStyle(3002);
            if(_hist[kPlotSignal3]) _hist[kPlotSignal3]->SetFillStyle(3002);

            if(_hist[kPlotData]) _hist[kPlotData]->Rebin(rebin);
            if(_hist[kPlotData]) _hist[kPlotData]->SetLineColor  (kBlack);
            if(_hist[kPlotData]) _hist[kPlotData]->SetMarkerSize(0.8);
            if(_hist[kPlotData]) _hist[kPlotData]->SetMarkerStyle(kFullCircle);

            //_hist[kPlotData]->SetBinContent(5,_hist[kPlotData]->GetBinContent(5)-1);
            //_hist[kPlotData]->SetBinContent(6,_hist[kPlotData]->GetBinContent(6)-1);
            //_hist[kPlotData]->SetBinContent(4,_hist[kPlotData]->GetBinContent(4)-5);
	    hstack->Draw("hist");

  	    TGraphAsymmErrors * gsyst = new TGraphAsymmErrors(hSum);
	    bool plotSystErrorBars = true;
	    if(plotSystErrorBars == true) {
              for (int i = 0; i < gsyst->GetN(); ++i) {
                double systBck = 0;
		//if(_hist[iWW	]) systBck = systBck + 1.000*TMath::Power(0.100*_hist[iWW    ]->GetBinContent(i+1),2);
                double total = hSum->GetBinContent(i+1);
                if(total > 0) systBck = sqrt(systBck)/total; else systBck=0.0; 
		systBck=0.0;
                gsyst->SetPointEYlow (i, sqrt(hSum->GetBinError(i+1)*hSum->GetBinError(i+1)+hSum->GetBinContent(i+1)*hSum->GetBinContent(i+1)*systBck*systBck));
                gsyst->SetPointEYhigh(i, sqrt(hSum->GetBinError(i+1)*hSum->GetBinError(i+1)+hSum->GetBinContent(i+1)*hSum->GetBinContent(i+1)*systBck*systBck));
	      }
              gsyst->SetFillColor(12);
              gsyst->SetFillStyle(3345);
              gsyst->SetMarkerSize(0);
              gsyst->SetLineWidth(0);
              gsyst->SetLineColor(kWhite);
	      gsyst->Draw("E2same");
              //TExec *setex1 = new TExec("setex1","gStyle->SetErrorX(0)");
              //setex1->Draw();
	    }

            if(_hist[kPlotBSM    ] && isBSMOverlaid == false) _hist[kPlotBSM    ]->Draw("hist,same");
            if(_hist[kPlotSignal0] && isBSMOverlaid == false) _hist[kPlotSignal0]->Draw("hist,same");
            if(_hist[kPlotSignal1] && isBSMOverlaid == false) _hist[kPlotSignal1]->Draw("hist,same");
            if(_hist[kPlotSignal2] && isBSMOverlaid == false) _hist[kPlotSignal2]->Draw("hist,same");
            if(_hist[kPlotSignal3] && isBSMOverlaid == false) _hist[kPlotSignal3]->Draw("hist,same");

            if(_hist[kPlotData]) {
	      bool plotCorrectErrorBars = true;
	      if(plotCorrectErrorBars == true) {
  		TGraphAsymmErrors * gc = new TGraphAsymmErrors(_hist[kPlotData]);
  		for (int j = 0; j < gc->GetN(); ++j) {
		TGraphAsymmErrors *g = (TGraphAsymmErrors*)gc->Clone();
		g->SetLineColor(kBlack);
  		for (int i = 0; i < g->GetN(); ++i) {
                  double N = g->GetY()[i];
                  double alpha=(1-0.6827);
                  double L = (N==0) ? 0 : (ROOT::Math::gamma_quantile(alpha/2,N,1.));
                  double U = ROOT::Math::gamma_quantile_c(alpha/2,N+1,1);
                  g->SetPointEYlow(i,double(N)-L);
                  g->SetPointEYhigh(i, U-double(N));

                  g->SetPointEXlow (i, 0);//g->SetPointEXlow (i, _hist[kPlotData]->GetBinWidth(i+1)/2.);
                  g->SetPointEXhigh(i, 0);//g->SetPointEXhigh(i, _hist[kPlotData]->GetBinWidth(i+1)/2.);

                  if(N==0 && j!=i) g->SetPoint(i, g->GetX()[i], -0.1);
                  if(N==0 && j==i) g->SetMarkerSize(0);

                  //if(N==0) {
                  //  g->SetPoint(i, g->GetX()[i], -0.1);
                  //  g->SetPointEYhigh(i, U-double(N)+0.1);
                  //}
  		}
		if(_doApplyBinWidth == true){
 		  for (int i = 0; i < g->GetN(); ++i) {
                    g->SetPointEYlow (i, g->GetErrorYlow(i) /_hist[kPlotData]->GetBinWidth(i+1)*SFBinWidth);
                    g->SetPointEYhigh(i, g->GetErrorYhigh(i)/_hist[kPlotData]->GetBinWidth(i+1)*SFBinWidth);
                    g->SetPoint      (i, g->GetX()[i], g->GetY()[i]/_hist[kPlotData]->GetBinWidth(i+1)*SFBinWidth);
  		  }
		}
  		for (int i = 0; i < gc->GetN(); ++i) {
                  double x,y;
                  g->GetPoint(i, x, y);
                  _hist[kPlotData]->SetBinContent(i+1,y);
                  _hist[kPlotData]->SetBinError(i+1,TMath::Sqrt(y));
                }
		g->Draw("P,z");
  		}
	      }
	      else {
                if(_doApplyBinWidth == true){
                  for(int nb=1; nb<=_hist[kPlotData]->GetNbinsX(); nb++){
		    _hist[kPlotData]->SetBinContent(nb, _hist[kPlotData]->GetBinContent(nb)/_hist[kPlotData]->GetBinWidth(nb)*SFBinWidth);
		    _hist[kPlotData]->SetBinError  (nb, _hist[kPlotData]->GetBinError(nb)  /_hist[kPlotData]->GetBinWidth(nb)*SFBinWidth);
                  }
                }
	        _hist[kPlotData]->Draw("ep,same");
	      }
            }
	    
            hstack->SetTitle("");
            //hstack->SetTitle("CMS");

   	    //TPaveText *pt = new TPaveText(0.61,0.8337762,0.9408059,0.8862238,"blNDC");
   	    //pt->SetName("title");
   	    //pt->SetBorderSize(0);
   	    //pt->SetFillColor(10);
   	    //pt->SetTextFont(42);
   	    //pt->SetTextSize(_tsize);
   	    //pt->AddText("CMS preliminary");
   	    //pt->Draw();
   
            Float_t theMax = hstack->GetMaximum();
            Float_t theMin = hstack->GetMinimum();

            if (_hist[kPlotBSM]) {
                if (_hist[kPlotBSM]->GetMaximum() > theMax) theMax = _hist[kPlotBSM]->GetMaximum();
                if (_hist[kPlotBSM]->GetMinimum() < theMin) theMin = _hist[kPlotBSM]->GetMinimum();
            }
            if (_hist[kPlotSignal0]) {
                if (_hist[kPlotSignal0]->GetMaximum() > theMax) theMax = _hist[kPlotSignal0]->GetMaximum();
                if (_hist[kPlotSignal0]->GetMinimum() < theMin) theMin = _hist[kPlotSignal0]->GetMinimum();
            }
            if (_hist[kPlotSignal1]) {
                if (_hist[kPlotSignal1]->GetMaximum() > theMax) theMax = _hist[kPlotSignal1]->GetMaximum();
                if (_hist[kPlotSignal1]->GetMinimum() < theMin) theMin = _hist[kPlotSignal1]->GetMinimum();
            }
            if (_hist[kPlotSignal2]) {
                if (_hist[kPlotSignal2]->GetMaximum() > theMax) theMax = _hist[kPlotSignal2]->GetMaximum();
                if (_hist[kPlotSignal2]->GetMinimum() < theMin) theMin = _hist[kPlotSignal2]->GetMinimum();
            }
            if (_hist[kPlotSignal3]) {
                if (_hist[kPlotSignal3]->GetMaximum() > theMax) theMax = _hist[kPlotSignal3]->GetMaximum();
                if (_hist[kPlotSignal3]->GetMinimum() < theMin) theMin = _hist[kPlotSignal3]->GetMinimum();
            }

            if (_hist[kPlotData]) {

                Float_t dataMax = GetMaximumIncludingErrors(_hist[kPlotData],_doApplyBinWidth);
                if (dataMax > theMax) theMax = dataMax;

                Float_t dataMin = GetMinimumIncludingErrors(_hist[kPlotData],_doApplyBinWidth);
                if (dataMin < theMin) theMin = dataMin;
            }

            if (gPad->GetLogy()) {
                hstack->SetMaximum(100 * theMax);
                hstack->SetMinimum(TMath::Max(0.9 * theMin,0.001));
            } else {
              hstack->SetMaximum(2.0 * theMax);
            }

            if(_breakdown) {
                THStackAxisFonts(hstack, "y", "Events / bin", _doApplyBinWidth);
                hstack->GetHistogram()->LabelsOption("v");
            } else {
                if(_units.Sizeof() == 1) {
                    THStackAxisFonts(hstack, "x", _xLabel.Data(), _doApplyBinWidth);
                    if     (_doApplyBinWidth == true && SFBinWidth == 1) THStackAxisFonts(hstack, "y", "Events / GeV", _doApplyBinWidth);
                    else if(_doApplyBinWidth == true)                    THStackAxisFonts(hstack, "y", Form("Events / %.2f",SFBinWidth), _doApplyBinWidth);
                    else                                                 THStackAxisFonts(hstack, "y", "Events / bin", _doApplyBinWidth);
                } else {
		    if(_units.EndsWith("BIN") == false){
                      THStackAxisFonts(hstack, "x", TString::Format("%s [%s]",_xLabel.Data(),_units.Data()), _doApplyBinWidth);
                      if(hSum->GetBinWidth(0) < 1) THStackAxisFonts(hstack, "y", TString::Format("Events / %.1f %s",hSum->GetBinWidth(0),_units.Data()), _doApplyBinWidth);
		      else                         THStackAxisFonts(hstack, "y", TString::Format("Events / %.0f %s",hSum->GetBinWidth(0),_units.Data()), _doApplyBinWidth);
                    }
		    else {
		      _units = _units.ReplaceAll("BIN","");
 		      if(strcmp(_units.Data(),"")==0) THStackAxisFonts(hstack, "x", TString::Format("%s",_xLabel.Data()), _doApplyBinWidth);
                      else                            THStackAxisFonts(hstack, "x", TString::Format("%s [%s]",_xLabel.Data(),_units.Data()), _doApplyBinWidth);
                      if     (_doApplyBinWidth == true && SFBinWidth == 1) THStackAxisFonts(hstack, "y", "Events / GeV", _doApplyBinWidth);
                      else if(_doApplyBinWidth == true)                    THStackAxisFonts(hstack, "y", Form("Events / %.2f",SFBinWidth), _doApplyBinWidth);
                      else                                                 THStackAxisFonts(hstack, "y", "Events / bin", _doApplyBinWidth);
		    }
                }
            }

            size_t j=0;
            TString higgsLabel  = Form("%s",_HiggsLabel.Data());
            TString higgs2Label = Form("%s",_Higgs2Label.Data());
            bool isThereSignal = false;

            for (int ic=0; ic<nPlotCategories; ic++) {
	      if     (ic==kPlotData){
	        if(_hist[ic] && _hist[ic]->GetSumOfWeights() > 0) { DrawLegend(xPos[j], 0.84 - yOff[j]*_yoffset, _hist[ic], plotNames[ic].Data(), "ep"); j++;}
                if(plotSystErrorBars == true) {DrawLegendTG(xPos[j], 0.84 - yOff[j]*_yoffset,gsyst, "Total unc.",  "f" ); j++;isThereSignal = true;}
              }
	      else if(ic == kPlotBSM){
	        double furtherXOffSet = 0.0;
		if(higgsLabel.Contains("m_{H},m_{a}")) furtherXOffSet = -0.05;
		if(higgsLabel.Contains("Z(ll)h_{125}")) furtherXOffSet = -0.05;
                if     (_hist[ic] && isBSMOverlaid) { DrawLegend(xPos[j]+furtherXOffSet, 0.84 - yOff[j]*_yoffset, _hist[ic], higgsLabel, "f" ); j++; }
                else if(_hist[ic])		    { DrawLegend(xPos[j]+furtherXOffSet, 0.84 - yOff[j]*_yoffset, _hist[ic], higgsLabel, "l" ); j++; }
	      }
	      else if(ic == kPlotSignal0){
	        double furtherXOffSet = 0.0;
		if(higgs2Label.Contains("ADD")) furtherXOffSet = -0.05;
                if     (_hist[ic] && isBSMOverlaid) { DrawLegend(xPos[j]+furtherXOffSet, 0.84 - yOff[j]*_yoffset*1.15, _hist[ic], higgs2Label, "f" ); j++; }
                else if(_hist[ic])		    { DrawLegend(xPos[j]+furtherXOffSet, 0.84 - yOff[j]*_yoffset*1.15, _hist[ic], higgs2Label, "l" ); j++; }
	      }
	      else if(ic == kPlotSignal1 || ic == kPlotSignal2 || ic == kPlotSignal3){
                if     (_hist[ic] && isBSMOverlaid) { DrawLegend(xPos[j], 0.84 - yOff[j]*_yoffset*1.09, _hist[ic], plotNames[ic].Data(), "f" ); j++; }
                else if(_hist[ic])		    { DrawLegend(xPos[j], 0.84 - yOff[j]*_yoffset*1.09, _hist[ic], plotNames[ic].Data(), "l" ); j++; }
	      }
	      else {
	        if(_hist[ic] && _hist[ic]->GetSumOfWeights() > 0) { DrawLegend(xPos[j], 0.84 - yOff[j]*_yoffset, _hist[ic], plotNames[ic].Data(), "f"); j++;}
	      }
	    }

            if(plotSystErrorBars == true && isThereSignal == false) {DrawLegendTG(xPos[j], 0.84 - yOff[j]*_yoffset,gsyst, "Total unc.",  "f" ); j++;}

            //TLatex* luminosity = new TLatex(0.9, 0.8, TString::Format("L = %.1f fb^{-1}",_lumi));
            //luminosity->SetNDC();
            //luminosity->SetTextAlign(32);
            //luminosity->SetTextFont(42);
            //luminosity->SetTextSize(_tsize);
            //luminosity->Draw("same");
            if(_extraLabel) _extraLabel->Draw("same");

            return hstack->GetHistogram();
        }
        void setDoApplyBinWidth(const bool &b) {_doApplyBinWidth = b; }
        void setLumi(const float &l) { _lumi = l; }
        void setLabel(const TString &s) { _xLabel = s; }
        void setUnits(const TString &s) { _units = s; }
        void setBreakdown(const bool &b = true) { _breakdown = b; }
        void addLabel(const std::string &s) {
            _extraLabel = new TLatex(0.216, 0.70, TString(s));
            _extraLabel->SetNDC();
            _extraLabel->SetTextAlign(13);
            _extraLabel->SetTextFont(62);
            _extraLabel->SetTextSize(0.055);
        }

    private: 
        std::vector<TH1F*> _hist;
        TH1F* _hist_total;

        //MWL
        float    _lumi;
        TString  _xLabel;
        TString  _units;
        TLatex * _extraLabel;
        bool     _breakdown;
        TString  _HiggsLabel;
        TString  _Higgs2Label;
        TString  _labelEM;
        TString  _labelVVV;
	bool     _doApplyBinWidth;

};
