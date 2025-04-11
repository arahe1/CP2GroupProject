////////////////////////////////////////////////////////////////////////
// Class:       AnalyseEvents
// Plugin Type: analyzer (Unknown Unknown)
// File:        AnalyseEvents_module.cc
//
// Generated at Thu Mar 20 16:38:33 2025 by Tyler LaBree using cetskelgen
// from cetlib version 3.18.02.
////////////////////////////////////////////////////////////////////////

#include <optional>

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
        //Helper functions
        bool EventMatchesCriteria(const art::Event& e);
        std::tuple<int, int> GetNuSliceIDs(const art::Event& e);
        std::vector<art::Ptr<recob::PFParticle>> GetAllPFPs(const art::Event& e);
        std::vector<art::Ptr<recob::PFParticle>> GetDaughterPFPs(const art::Event& e);
        std::optional<art::Ptr<recob::Track>> GetTrack(art::Ptr<recob::PFParticle> pfp, const art::Event& e);
        float GetTrackScore(art::Ptr<recob::PFParticle> pfp, const art::Event& e);
        std::optional<art::Ptr<anab::Calorimetry>> GetCalorimetry(std::optional<art::Ptr<recob::Track>> track, const art::Event& e);
        int GetMCParticleID(art::Ptr<recob::PFParticle> pfp, const art::Event& e);
        std::optional<const simb::MCParticle*> GetMCParticle(int id);
        std::vector<const simb::MCParticle*> GetPrimaryMCParticles(const art::Event& e);
        std::vector<int> GetDaughterMCParticleIDs(const art::Event& e);
        std::vector<const simb::MCParticle*> GetDaughterMCParticles(const art::Event& e);

        // Input labels from fhicl file
        std::string fMCTruthLabel;
        std::string fMCParticleLabel;
        std::string fSliceLabel;
        std::string fPFParticleLabel;
        std::string fTrackLabel;
        std::string fCalorimetryLabel;
        std::string fCVNLabel;

        // Input variables from fhicl file
        int fInitialNeutrinoFlavor;
        int fIsChargedCurrent;

        // Output variables written to root file
        TTree *fReco;
        unsigned int fEventID;
        unsigned int fNPFParticles;
        unsigned int fNDaughters;
        std::vector<int> fTrackId;
        std::vector<float> fTrackLength;
        std::vector<float> fTrackScore;
        std::vector<std::vector<float>> fHitdEdx;
        std::vector<std::vector<float>> fHitResRange;
        std::vector<int> fTruePdgCode;
        std::vector<float> fTrueEnergy;

        TTree *fFail;
        std::vector<int> fTruePdgCodeFail;
        std::vector<float> fTrueEnergyFail;
};


test::AnalyseEvents::AnalyseEvents(fhicl::ParameterSet const& p)
    : EDAnalyzer{p},
    fMCTruthLabel(p.get<std::string>("MCTruthLabel")),
    fMCParticleLabel(p.get<std::string>("MCParticleLabel")),
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

bool test::AnalyseEvents::EventMatchesCriteria(const art::Event& e) {
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
    return eventMatchesCriteria;
}

std::tuple<int, int> test::AnalyseEvents::GetNuSliceIDs(const art::Event& e) {

    auto const& slices = e.getValidHandle<std::vector<recob::Slice>>(fSliceLabel);
    art::FindManyP<recob::PFParticle> slicePFPAssn(slices, e, fPFParticleLabel);

    int nuSliceID = -1;
    int nuID = -1;

    for (auto const& slice : *slices) {
        std::vector<art::Ptr<recob::PFParticle>> slicePFPs =
            slicePFPAssn.at(slice.ID());

        for (auto slicePFP : slicePFPs) {
            const bool isPrimary = slicePFP->IsPrimary();
            const bool isNeutrino = (std::abs(slicePFP->PdgCode()) == 12) ||
                                    (std::abs(slicePFP->PdgCode()) == 14);

            if (isPrimary && isNeutrino) {
                nuSliceID = slice.ID();
                nuID = slicePFP->Self();
                break;
            }
        }

        if (nuID >= 0) break;
    }

    return std::make_tuple(nuSliceID, nuID);
}


std::vector<art::Ptr<recob::PFParticle>> test::AnalyseEvents::GetAllPFPs(const art::Event& e) {

    auto [nuSliceID, nuID] = GetNuSliceIDs(e);
    if (nuID < 0)
        return {};

    auto const& slices = e.getValidHandle<std::vector<recob::Slice>>(fSliceLabel);
    art::FindManyP<recob::PFParticle> slicePFPAssn(slices, e, fPFParticleLabel);
    std::vector<art::Ptr<recob::PFParticle>> nuSlicePFPs = slicePFPAssn.at(nuSliceID);
    std::vector<art::Ptr<recob::PFParticle>> pfps;

    for (auto const& nuSlicePFP : nuSlicePFPs) {
        if (nuSlicePFP->Self() != static_cast<long unsigned int>(nuID))
            pfps.push_back(nuSlicePFP);
    }

    return pfps;
}


std::vector<art::Ptr<recob::PFParticle>> test::AnalyseEvents::GetDaughterPFPs(const art::Event& e) {
    auto [nuSliceID, nuID] = GetNuSliceIDs(e);
    std::vector<art::Ptr<recob::PFParticle>> pfps = GetAllPFPs(e);
    std::vector<art::Ptr<recob::PFParticle>> daughterPFPs;

    for (auto const& pfp : pfps) {
        if (pfp->Parent() == static_cast<long unsigned int>(nuID))
            daughterPFPs.push_back(pfp);
    }

    return daughterPFPs;
}


std::optional<art::Ptr<recob::Track>> test::AnalyseEvents::GetTrack(art::Ptr<recob::PFParticle> pfp, const art::Event& e) {
    auto const& pfpHandle = 
        e.getValidHandle<std::vector<recob::PFParticle>>(fPFParticleLabel);
    art::FindManyP<recob::Track> pfpTrackAssn(pfpHandle, e, fTrackLabel);
    std::vector<art::Ptr<recob::Track>> tracks = pfpTrackAssn.at(pfp->Self());

    if (tracks.size() != 1) {
        return std::nullopt;
    }
    return tracks.at(0);
}


float test::AnalyseEvents::GetTrackScore(art::Ptr<recob::PFParticle> pfp, const art::Event& e) {
    auto const& pfpHandle = 
        e.getValidHandle<std::vector<recob::PFParticle>>(fPFParticleLabel);
    art::FindManyP<larpandoraobj::PFParticleMetadata> pfpMetadataAssn(pfpHandle, e, fPFParticleLabel);

    std::vector<art::Ptr<larpandoraobj::PFParticleMetadata>> metadatas =
        pfpMetadataAssn.at(pfp->Self());

    if (metadatas.size() != 1)
        return NAN;

    /*
    const auto& metadata = metadatas[0];
    std::map<std::string, float> properties = metadata->GetPropertiesMap();
    return properties.at("TrackScore")
    */
    return metadatas[0]->GetPropertiesMap().at("TrackScore");
}


std::optional<art::Ptr<anab::Calorimetry>> test::AnalyseEvents::GetCalorimetry(std::optional<art::Ptr<recob::Track>> track, const art::Event& e) {
    if (!track)
        return std::nullopt;

    auto const& trackHandle = 
        e.getValidHandle<std::vector<recob::Track>>(fTrackLabel);
    art::FindManyP<anab::Calorimetry> trackCaloAssn(trackHandle, e, fCalorimetryLabel);

    std::vector<art::Ptr<anab::Calorimetry>> calos =
        trackCaloAssn.at(track.value()->ID());

    std::vector<art::Ptr<anab::Calorimetry>> plane2Calos;
    for (auto const& calo : calos) {
        if (calo->PlaneID().Plane == 2)
            plane2Calos.push_back(calo);
    }
    if (plane2Calos.size() == 1) {
        return plane2Calos[0];
    }
    return std::nullopt;
}


int test::AnalyseEvents::GetMCParticleID(art::Ptr<recob::PFParticle> pfp, const art::Event& e) {
    auto const& pfpHandle = 
        e.getValidHandle<std::vector<recob::PFParticle>>(fPFParticleLabel);
    auto const& clusterHandle =
        e.getValidHandle<std::vector<recob::Cluster>>(fPFParticleLabel);

    art::FindManyP<recob::Cluster> pfpClusterAssn(pfpHandle, e, fPFParticleLabel);
    art::FindManyP<recob::Hit> clusterHitAssn(clusterHandle, e, fPFParticleLabel);

    std::vector<art::Ptr<recob::Cluster>> clusters = pfpClusterAssn.at(pfp->Self());

    std::vector<art::Ptr<recob::Hit>> hitsAcc;
    for (const auto& cluster : clusters) {
        const std::vector<art::Ptr<recob::Hit>> hits = clusterHitAssn.at(cluster->ID());
        hitsAcc.insert(hitsAcc.end(), hits.begin(), hits.end());
    }

    auto const clockData
        = art::ServiceHandle<detinfo::DetectorClocksService>()->DataFor(e);

    return TruthMatchUtils::TrueParticleIDFromTotalRecoHits(clockData, hitsAcc, 1);
}


std::optional<const simb::MCParticle*> test::AnalyseEvents::GetMCParticle(int id) {
    if (id > 0) {
        return art::ServiceHandle<cheat::ParticleInventoryService>()->TrackIdToParticle_P(id);
    }
    return std::nullopt;
}

std::vector<const simb::MCParticle*> test::AnalyseEvents::GetPrimaryMCParticles(const art::Event& e) {
    auto const& mcParticles =
        e.getValidHandle<std::vector<simb::MCParticle>>(fMCParticleLabel);
    std::vector<const simb::MCParticle*> primaryMCParticles;
    for (const auto& mcParticle : *mcParticles) {
        if (mcParticle.Mother() == -1) {
            primaryMCParticles.push_back(&mcParticle);
        }
    }
    return primaryMCParticles;
}

std::vector<int> test::AnalyseEvents::GetDaughterMCParticleIDs(const art::Event& e) {
    std::vector<int> ids;

    std::vector<const simb::MCParticle*> primaryMCParticles = GetPrimaryMCParticles(e);
    for (const simb::MCParticle* primaryMCParticle : primaryMCParticles) {
        for (int i = 0; i < primaryMCParticle->NumberDaughters(); i++) {
            int newID = primaryMCParticle->Daughter(i);
            if (std::find(ids.begin(), ids.end(), newID) == ids.end()) {
                ids.push_back(newID);
            }
        }
    }
    std::cout << "Daughter IDs: ";
    for (int id : ids) std::cout << id << " ";
    std::cout << std::endl;
    return ids;
}

/* 
std::vector<const simb::MCParticle*> test::AnalyseEvents::GetDaughterMCParticles(const art::Event& e) {
    std::vector<const simb::MCParticle*> particles;

    auto const& mcParticles =
        e.getValidHandle<std::vector<simb::MCParticle>>(fMCParticleLabel);
    std::vector<int> ids = GetDaughterMCParticleIDs(e);

    for (const auto& mcParticle : *mcParticles) {
        if (std::find(ids.begin(), ids.end(), mcParticle.TrackId()) != ids.end()) {
            particles.push_back(&mcParticle);
        }
    }
    return particles;
}
*/

std::vector<const simb::MCParticle*> test::AnalyseEvents::GetDaughterMCParticles(const art::Event& e) {
    std::vector<const simb::MCParticle*> particles;
    auto const& mcParticles =
        e.getValidHandle<std::vector<simb::MCParticle>>(fMCParticleLabel);
    for (const auto& mcParticle : *mcParticles) {
        if (mcParticle.Mother() == 0) {
            particles.push_back(&mcParticle);
        }
    }
    return particles;
}

void test::AnalyseEvents::analyze(art::Event const& e)
{
    fEventID = e.id().event();

    fEventID = 0;
    fNPFParticles = 0;
    fNDaughters = 0;
    fTrackId.clear();
    fTrackLength.clear();
    fTrackScore.clear();
    fHitdEdx.clear();
    fHitResRange.clear();
    fTruePdgCode.clear();
    fTrueEnergy.clear();
    fTruePdgCodeFail.clear();
    fTrueEnergyFail.clear();

    if (!EventMatchesCriteria(e)) {
        return;
    }

    std::vector<art::Ptr<recob::PFParticle>> daughterPFPs = GetDaughterPFPs(e);
    fNPFParticles = GetAllPFPs(e).size();
    fNDaughters = daughterPFPs.size();
    std::vector<int> mcParticleFromPFParticleIDs;
    for (art::Ptr<recob::PFParticle> daughterPFP : daughterPFPs) {
        fTrackScore.push_back(GetTrackScore(daughterPFP, e));

        std::optional<art::Ptr<recob::Track>> track = GetTrack(daughterPFP, e);
        if (track) {
            fTrackLength.push_back(track.value()->Length());
        } else {
            fTrackLength.push_back(NAN);
        }

        std::optional<art::Ptr<anab::Calorimetry>> calo = GetCalorimetry(track, e);
        if (calo) {
            fHitdEdx.push_back(calo.value()->dEdx());
            fHitResRange.push_back(calo.value()->ResidualRange());
        } else {
            fHitdEdx.push_back({});
            fHitResRange.push_back({});
        }
        mcParticleFromPFParticleIDs.push_back(GetMCParticleID(daughterPFP, e));
        std::optional<const simb::MCParticle*> mcParticle = GetMCParticle(mcParticleFromPFParticleIDs.back());
        if (mcParticle) {
            fTrackId.push_back(mcParticle.value()->TrackId());
            fTruePdgCode.push_back(mcParticle.value()->PdgCode());
            fTrueEnergy.push_back(mcParticle.value()->E());
        } else {
            fTrackId.push_back(-1);
            fTruePdgCode.push_back(0);
            fTrueEnergy.push_back(NAN);
        }
    }

    fReco->Fill();

    std::vector<const simb::MCParticle*> mcParticles = GetDaughterMCParticles(e);
    for (const simb::MCParticle* mcParticle : mcParticles) {
        if (std::find(fTrackId.begin(), fTrackId.end(), mcParticle->TrackId()) != fTrackId.end()) {
            continue;
        }
        fTruePdgCodeFail.push_back(mcParticle->PdgCode());
        fTrueEnergyFail.push_back(mcParticle->E());
    }

    fFail->Fill();
}

void test::AnalyseEvents::beginJob()
{
    art::ServiceHandle<art::TFileService> tfs;

    fReco = tfs->make<TTree>("reco", "Reconstructed particles");
    fReco->Branch("eventID", &fEventID);
    fReco->Branch("nPFParticles", &fNPFParticles);
    fReco->Branch("nDaughters", &fNDaughters);
    fReco->Branch("trackId", &fTrackId);
    fReco->Branch("trackLength", &fTrackLength);
    fReco->Branch("trackScore", &fTrackScore);
    fReco->Branch("hitdEdx", &fHitdEdx);
    fReco->Branch("hitResRange", &fHitResRange);
    fReco->Branch("truePdgCode", &fTruePdgCode);
    fReco->Branch("trueEnergy", &fTrueEnergy);

    fFail = tfs->make<TTree>("fail", "Particles which failed to be reconstructed");
    fFail->Branch("truePdgCode", &fTruePdgCodeFail);
    fFail->Branch("trueEnergy", &fTrueEnergyFail);
}

void test::AnalyseEvents::endJob()
{
    // Implementation of optional member function here.
}

DEFINE_ART_MODULE(test::AnalyseEvents)
