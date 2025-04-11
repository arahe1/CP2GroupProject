void mu_v_pi2() {
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
// Uncomment this block for the scatter plot of muons and pions
tree->Draw("trackdEdx:trackResRange",
           "trackdEdx<15 && trackResRange<130 && abs(truePdgCodes)==13 && trackScores>0.5",
           "goff");
int nMuon = tree->GetSelectedRows();
TGraph* gMuon = new TGraph(nMuon, tree->GetV2(), tree->GetV1());
gMuon->SetMarkerStyle(20);
gMuon->SetMarkerColor(kRed);
gMuon->SetMarkerSize(0.8);

tree->Draw("trackdEdx:trackResRange",
           "trackdEdx<15 && trackResRange<130 && abs(truePdgCodes)==211 && trackScores>0.5",
           "goff");
int nPion = tree->GetSelectedRows();
TGraph* gPion = new TGraph(nPion, tree->GetV2(), tree->GetV1());
gPion->SetMarkerStyle(20);
gPion->SetMarkerColor(kBlue);
gPion->SetMarkerSize(0.8);

TCanvas* c_scatter = new TCanvas("c_scatter", "dE/dx vs. Residual Range (Scatter)", 800, 600);
gMuon->Draw("AP");
gPion->Draw("P same");
gMuon->GetXaxis()->SetTitle("Residual Range [cm]");
gMuon->GetYaxis()->SetTitle("dE/dx [MeV/cm]");

TLegend* legend_scatter = new TLegend(0.65, 0.75, 0.88, 0.88);
legend_scatter->AddEntry(gMuon, "Muons (PDG +/-13)", "p");
legend_scatter->AddEntry(gPion, "Pions (PDG +/-211)", "p");
legend_scatter->Draw();

c_scatter->Update();
c_scatter->SaveAs("./data/plots-new/dEdx_ResRange_Scatter.png");  // Save the plot here with a sensible name

}

