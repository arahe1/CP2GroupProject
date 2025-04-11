void mu_v_pi() {
    TFile* file = TFile::Open("analysisOutput2.root");
    if (!file || file->IsZombie()) {
        std::cerr << "Error: could not open file!" << std::endl;
        return;
    }

    TDirectory* dir = (TDirectory*)file->Get("ana");
    if (!dir) {
        std::cerr << "Error: could not find directory 'ana'" << std::endl;
        return;
    }

    dir->cd();
    TTree* tree = (TTree*)dir->Get("tree");
    if (!tree) {
        std::cerr << "Error: could not find TTree named 'tree'" << std::endl;
        return;
    }

    /*
    // Draw muons to a TGraph
    tree->Draw("trackdEdx:trackResRange",
               "trackdEdx<15 && trackResRange<130 && abs(truePdgCodes)==13 && trackScores>0.5",
               "goff");
    int nMuon = tree->GetSelectedRows();
    TGraph* gMuon = new TGraph(nMuon, tree->GetV2(), tree->GetV1()); // V2 = x, V1 = y
    hmuon->SetMarkerStyle(20);
    hmuon->SetMarkerColor(kRed);
    hmuon->SetMarkerSize(1.2);

    // Draw pions to a TGraph
    tree->Draw("trackdEdx:trackResRange",
               "trackdEdx<15 && trackResRange<130 && abs(truePdgCodes)==211 && trackScores>0.5",
               "goff");
    int nPion = tree->GetSelectedRows();
    TGraph* gPion = new TGraph(nPion, tree->GetV2(), tree->GetV1()); // V2 = x, V1 = y
    hpion->SetMarkerStyle(20);
    hpion->SetMarkerColor(kBlue);
    hpion->SetMarkerSize(1.2);

    // Draw both graphs
    TCanvas* c = new TCanvas("c", "dE/dx vs. Residual Range (Scatter)", 800, 600);
    hmuon->Draw("AP");         // A = axis, P = points
    hpion->Draw("P same");

    // Axes labels
    hmuon->GetXaxis()->SetTitle("Residual Range [cm]");
    hmuon->GetYaxis()->SetTitle("dE/dx [MeV/cm]");

    // Legend
    TLegend* legend = new TLegend(0.65, 0.75, 0.88, 0.88);
    legend->AddEntry(hmuon, "Muons (PDG +/-13)", "p");
    legend->AddEntry(hpion, "Pions (PDG +/-211)", "p");
    legend->Draw();

    c->Update();
    */

    /*
    tree->Draw("trackScores>>hmuon(50, 0, 1)",
               "abs(truePdgCodes)==13",
               "goff");
    TH1F* hmuon = (TH1F*)gDirectory->Get("hmuon");

    tree->Draw("trackScores>>hpion(50, 0, 1)",
               "abs(truePdgCodes)==211",
               "goff");
    TH1F* hpion = (TH1F*)gDirectory->Get("hpion");
    */

  tree->Draw("trackScores>>hpion(50, 0, 1)", "abs(truePdgCodes)==211", "goff");
  TH1F* hpion = (TH1F*)gDirectory->Get("hpion");

  tree->Draw("trackScores>>hmuon(50, 0, 1)", "abs(truePdgCodes)==13", "goff");
  TH1F* hmuon = (TH1F*)gDirectory->Get("hmuon");

  TCanvas* c = new TCanvas("c", "Track Score Comparison", 800, 600);

  hmuon->SetLineColor(kRed);
  hmuon->SetLineWidth(2);
  hmuon->SetStats(0);  // Hide default stats box
  hmuon->SetTitle("Track Score Comparison;Track Score;Entries");
  hmuon->Draw("hist");

  hpion->SetLineColor(kBlue);
  hpion->SetLineWidth(2);
  hpion->Draw("hist same");

  TLegend* legend = new TLegend(0.65, 0.75, 0.88, 0.88);
  legend->AddEntry(hmuon, "Muons (PDG ±13)", "l");
  legend->AddEntry(hpion, "Pions (PDG ±211)", "l");
  legend->Draw();

  c->Update();
}

