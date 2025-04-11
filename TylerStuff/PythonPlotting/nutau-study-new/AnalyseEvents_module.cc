////////////////////////////////////////////////////////////////////////
// Class:       AnalyseEvents
// Plugin Type: analyzer (Unknown Unknown)
// File:        AnalyseEvents_module.cc
//
// Generated at Thu Mar 20 16:38:33 2025 by Tyler LaBree using cetskelgen
// from cetlib version 3.18.02.
////////////////////////////////////////////////////////////////////////

#include "art/Framework/Core/EDAnalyzer.h"
#include "art/Framework/Core/ModuleMacros.h"
#include "art/Framework/Principal/Event.h"
#include "art/Framework/Principal/Handle.h"
#include "art/Framework/Principal/Run.h"
#include "art/Framework/Principal/SubRun.h"
#include "canvas/Utilities/InputTag.h"
#include "fhiclcpp/ParameterSet.h"
#include "messagefacility/MessageLogger/MessageLogger.h"

#include "art_root_io/TFileService.h"
#include <TTree.h>

#include "canvas/Persistency/Common/FindManyP.h"

#include "nusimdata/SimulationBase/MCTruth.h"
#include "lardataobj/RecoBase/Slice.h"
#include "lardataobj/RecoBase/PFParticle.h"
#include "lardataobj/RecoBase/Track.h"
#include "lardataobj/RecoBase/Cluster.h"
#include "lardataobj/RecoBase/Hit.h"
#include "lardataobj/RecoBase/PFParticleMetadata.h"
#include "lardataobj/AnalysisBase/Calorimetry.h"

#include "larsim/Utils/TruthMatchUtils.h"
#include "dunereco/AnaUtils/DUNEAnaPFParticleUtils.h"
#include "lardata/DetectorInfoServices/DetectorClocksService.h"
#include "larsim/MCCheater/ParticleInventoryService.h"
#include "nusimdata/SimulationBase/MCParticle.h"

namespace test {
    class AnalyseEvents;
}


class test::AnalyseEvents : public art::EDAnalyzer {
    public:
        explicit AnalyseEvents(fhicl::ParameterSet const& p);
        // The compiler-generated destructor is fine for non-base
        // classes without bare pointers or other resource use.

        // Plugins should not be copied or assigned.
        AnalyseEvents(AnalyseEvents const&) = delete;
        AnalyseEvents(AnalyseEvents&&) = delete;
        AnalyseEvents& operator=(AnalyseEvents const&) = delete;
        AnalyseEvents& operator=(AnalyseEvents&&) = delete;

        // Required functions.
        void analyze(art::Event const& e) override;

        // Selected optional functions.
        void beginJob() override;
        void endJob() override;

    private:
        // Input labels from fhicl file
        std::string fMCTruthLabel;
        std::string fSliceLabel;
        std::string fPFParticleLabel;
        std::string fTrackLabel;
        std::string fCalorimetryLabel;
        std::string fCVNLabel;

        // Input variables from fhicl file
        int fInitialNeutrinoFlavor;
        int fIsChargedCurrent;

        // Output variables written to root file
        TTree *fTree;
        unsigned int fEventID;
        unsigned int fNPFParticles;
        unsigned int fNPrimaryChildren;
        std::vector<float> fTrackLengths;
        std::vector<float> fTrackScores;
        std::vector<std::vector<float>> fTrackdEdx;
        std::vector<std::vector<float>> fTrackResRange;
        std::vector<int> fTruePdgCodes;
        std::vector<float> fTrueEnergies;
};


test::AnalyseEvents::AnalyseEvents(fhicl::ParameterSet const& p)
    : EDAnalyzer{p},
    fMCTruthLabel(p.get<std::string>("MCTruthLabel")),
    fSliceLabel(p.get<std::string>("SliceLabel")),
    fPFParticleLabel(p.get<std::string>("PFParticleLabel")),
    fTrackLabel(p.get<std::string>("TrackLabel")),
    fCalorimetryLabel(p.get<std::string>("CalorimetryLabel")),
    fCVNLabel(p.get<std::string>("CVNLabel")),
    fInitialNeutrinoFlavor(p.get<int>("InitialNeutrinoFlavor")),
    fIsChargedCurrent(p.get<int>("IsChargedCurrent"))
{
    // Call appropriate consumes<>() for any products to be retrieved by this module.
}

void test::AnalyseEvents::analyze(art::Event const& e)
{
    fEventID = e.id().event();

    fEventID = 0;
    fNPFParticles = 0;
    fNPrimaryChildren = 0;
    fTrackLengths.clear();
    fTrackScores.clear();
    fTrackdEdx.clear();
    fTrackResRange.clear();
    fTruePdgCodes.clear();
    fTrueEnergies.clear();

    auto const& mctruths =
        e.getValidHandle<std::vector<simb::MCTruth>>(fMCTruthLabel);

    bool eventMatchesCriteria = true;
    for (auto const& mctruth : *mctruths) {
        if (fInitialNeutrinoFlavor != mctruth.GetNeutrino().Nu().PdgCode()
                || fIsChargedCurrent != !mctruth.GetNeutrino().CCNC()) {
            eventMatchesCriteria = false;
            break;
        }
    }
    if (!eventMatchesCriteria) {
        return;
    }

    auto const& slices = 
        e.getValidHandle<std::vector<recob::Slice>>(fSliceLabel);
    art::FindManyP<recob::PFParticle> slicePFPAssn(slices, e, fPFParticleLabel);

    int nuSliceID = -1; int nuID = -1;

    for (auto const& slice : *slices) {
        std::vector<art::Ptr<recob::PFParticle>> slicePFPs =
            slicePFPAssn.at(slice.ID());
        for (auto slicePFP : slicePFPs) {
            const bool isPrimary(slicePFP->IsPrimary());
            const bool isNeutrino(
                    (std::abs(slicePFP->PdgCode()) == 12)
                    || (std::abs(slicePFP->PdgCode()) == 14));
            if (!(isPrimary && isNeutrino))
                continue;
            nuSliceID = slice.ID();
            nuID = slicePFP->Self();
            fNPFParticles = slicePFPs.size() - 1;
            fNPrimaryChildren = slicePFP->NumDaughters();
            break;
        }
    }
    if (nuID < 0)
        return;

    auto const& pfps = 
        e.getValidHandle<std::vector<recob::PFParticle>>(fPFParticleLabel);
    art::FindManyP<recob::Track> pfpTrackAssn(pfps, e, fTrackLabel);
    art::FindManyP<larpandoraobj::PFParticleMetadata> pfpMetadataAssn(pfps, e, fPFParticleLabel);
    art::FindManyP<recob::Cluster> pfpClusterAssn(pfps, e, fPFParticleLabel);

    auto const& clusterHandle =
        e.getValidHandle<std::vector<recob::Cluster>>(fPFParticleLabel);
    art::FindManyP<recob::Hit> clusterHitAssn(clusterHandle, e, fPFParticleLabel);

    auto const& tracks = 
        e.getValidHandle<std::vector<recob::Track>>(fTrackLabel);
    art::FindManyP<anab::Calorimetry> trackCaloAssn(tracks, e, fCalorimetryLabel);

    std::vector<art::Ptr<recob::PFParticle>> nuSlicePFPs =
        slicePFPAssn.at(nuSliceID);
    for (auto const& nuSlicePFP : nuSlicePFPs) {
        if (nuSlicePFP->Parent() != static_cast<long unsigned int>(nuID))
            continue;
        std::vector<art::Ptr<recob::Track>> tracks =
            pfpTrackAssn.at(nuSlicePFP->Self());
        if (tracks.size() != 1)
            continue;
        art::Ptr<recob::Track> track = tracks.at(0);
        fTrackLengths.push_back(track->Length());

        std::vector<art::Ptr<anab::Calorimetry>> calos =
            trackCaloAssn.at(track.key());
        for (auto const& calo : calos) {
            const int plane = calo->PlaneID().Plane;
            if (plane != 2)
                continue;
            fTrackdEdx.push_back(calo->dEdx());
            fTrackResRange.push_back(calo->ResidualRange());
        }

        std::vector<art::Ptr<larpandoraobj::PFParticleMetadata>> metadatas =
            pfpMetadataAssn.at(nuSlicePFP->Self());
        for (auto const& metadata : metadatas) {
            std::map<std::string, float> properties = metadata->GetPropertiesMap();
            fTrackScores.push_back(properties.at("TrackScore"));
        }

        std::vector<art::Ptr<recob::Hit>> hitsAcc;
        std::vector<art::Ptr<recob::Cluster>> clusters =
            pfpClusterAssn.at(nuSlicePFP->Self());
        for (const auto& cluster : clusters) {
            std::vector<art::Ptr<recob::Hit>> hits
                = clusterHitAssn.at(cluster->ID());
            hitsAcc.insert(hitsAcc.end(), hits.begin(), hits.end());
        }

        auto const clockData
            = art::ServiceHandle<detinfo::DetectorClocksService>()->DataFor(e);

        int g4id 
            = TruthMatchUtils::TrueParticleIDFromTotalRecoHits(clockData, hitsAcc, 1);
        //std::cout << "pfpid: " << nuSlicePFP->Self() << "\tg4id: " << g4id << std::endl;
        const simb::MCParticle* mcParticle 
            = art::ServiceHandle<cheat::ParticleInventoryService>()->TrackIdToParticle_P(g4id);
        fTruePdgCodes.push_back(mcParticle->PdgCode());
        fTrueEnergies.push_back(mcParticle->E());
    }

    fTree->Fill();
}

void test::AnalyseEvents::beginJob()
{
    art::ServiceHandle<art::TFileService> tfs;
    fTree = tfs->make<TTree>("tree", "Output TTree");

    fTree->Branch("eventID", &fEventID);
    fTree->Branch("nPFParticles", &fNPFParticles);
    fTree->Branch("nPrimaryChildren", &fNPrimaryChildren);
    fTree->Branch("trackLengths", &fTrackLengths);
    fTree->Branch("trackScores", &fTrackScores);
    fTree->Branch("trackdEdx", &fTrackdEdx);
    fTree->Branch("trackResRange", &fTrackResRange);
    fTree->Branch("truePdgCodes", &fTruePdgCodes);
    fTree->Branch("trueEnergies", &fTrueEnergies);
}

void test::AnalyseEvents::endJob()
{
    // Implementation of optional member function here.
}

DEFINE_ART_MODULE(test::AnalyseEvents)
