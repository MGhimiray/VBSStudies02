#include "TH1D.h"
#include "TH2D.h"

enum plotCategory {
  kPlotData      , // 0
  kPlotqqWW      , // 1
  kPlotggWW      , // 2
  kPlotTT        , // 3
  kPlotTW        , // 4
  kPlotDY        , // 5
  kPlotEWKSSWW   , // 6
  kPlotQCDSSWW   , // 7
  kPlotEWKWZ     , // 8
  kPlotWZ        , // 9
  kPlotZZ        , //10
  kPlotNonPrompt , //11
  kPlotVVV       , //12
  kPlotTVX       , //13
  kPlotVG        , //14
  kPlotHiggs     , //15
  kPlotWS        , //16
  kPlotOther     , //17
  kPlotEM        , //18
  kPlotBSM       , //19
  kPlotSignal0   , //20
  kPlotSignal1   , //21
  kPlotSignal2   , //22
  kPlotSignal3   , //23
  kPlotSignal4   , //24
  kPlotSignal5   , //25
  nPlotCategories
};

std::map<int, TString> plotBaseNames={
  { kPlotData	   , "Data" },
  { kPlotqqWW	   , "qqWW" },
  { kPlotggWW	   , "ggWW" },
  { kPlotTT	   , "TT" },
  { kPlotTW	   , "TW" },
  { kPlotDY	   , "DY" },
  { kPlotEWKSSWW   , "EWKSSWW" },
  { kPlotQCDSSWW   , "QCDSSWW" },
  { kPlotEWKWZ     , "EWKWZ" },
  { kPlotWZ	   , "WZ" },
  { kPlotZZ	   , "ZZ" },
  { kPlotNonPrompt , "NonPrompt" },
  { kPlotVVV	   , "VVV" },
  { kPlotTVX	   , "TVX" },
  { kPlotVG	   , "VG" },
  { kPlotHiggs     , "Higgs" },
  { kPlotWS	   , "WS" },
  { kPlotOther     , "Other" },
  { kPlotEM	   , "EM" },
  { kPlotBSM	   , "BSM" },
  { kPlotSignal0   , "Signal0" },
  { kPlotSignal1   , "Signal1" },
  { kPlotSignal2   , "Signal2" },
  { kPlotSignal3   , "Signal3" },
  { kPlotSignal4   , "Signal4" },
  { kPlotSignal5   , "Signal5" }
}; 

std::map<int, int> plotColors={
  { kPlotData	   , kBlack},
  { kPlotqqWW	   , kAzure-9},
  { kPlotggWW	   , 901},
  { kPlotTT	   , kYellow},
  { kPlotTW	   , kYellow-3},
  { kPlotDY	   , kAzure-2},
  { kPlotEWKSSWW   , TColor::GetColor(248,206,104)},
  { kPlotQCDSSWW   , TColor::GetColor(250,202,255)},
  { kPlotEWKWZ     , kCyan+3},
  { kPlotWZ	   , TColor::GetColor(222,90,106)},
  { kPlotZZ	   , kAzure-11},
  { kPlotNonPrompt , TColor::GetColor(155,152,204)},
  { kPlotVVV	   , 840},
  { kPlotTVX	   , kViolet+7},
  { kPlotVG	   , kGreen-8},
  { kPlotHiggs     , 841},
  { kPlotWS	   , kAzure+10},
  { kPlotOther     , kGreen-5},
  { kPlotEM	   , kGreen-5},
  { kPlotBSM	   , kGreen-4},
  { kPlotSignal0   , kBlue},
  { kPlotSignal1   , kMagenta+1},
  { kPlotSignal2   , kGreen-4},
  { kPlotSignal3   , kAzure-5},
  { kPlotSignal4   , kAzure-6},
  { kPlotSignal5   , kAzure-7}
}; 

std::map<int, TString> plotNames={
    { kPlotData      , "Data"},
    { kPlotqqWW      , "WW"},
    { kPlotggWW      , "gg #rightarrow WW"},
    { kPlotTT	     , "Top quark"},
    { kPlotTW	     , "tW"},
    { kPlotDY	     , "Drell-Yan"},
    { kPlotEWKSSWW   , "W^{#pm}W^{#pm}"},
    { kPlotQCDSSWW   , "QCD W^{#pm}W^{#pm}"},
    { kPlotEWKWZ     , "EWK WZ"},
    { kPlotWZ	     , "WZ"},
    { kPlotZZ	     , "ZZ"},
    { kPlotNonPrompt , "Nonprompt"},
    { kPlotVVV       , "VVV"},
    { kPlotTVX       , "tVx"},
    { kPlotVG	     , "V#gamma" },
    { kPlotHiggs     , "Higgs boson"},
    { kPlotWS	     , "Wrong sign"},
    { kPlotOther     , "Other bkg."},
    { kPlotEM	     , "Nonresonant"},
    { kPlotBSM       , "BSM"},
    { kPlotSignal0   , "Signal 0"},
    { kPlotSignal1   , "Signal 1"},
    { kPlotSignal2   , "Signal 2"},
    { kPlotSignal3   , "Signal 3"},
    { kPlotSignal4   , "Signal 4"},
    { kPlotSignal5   , "Signal 5"}
};
