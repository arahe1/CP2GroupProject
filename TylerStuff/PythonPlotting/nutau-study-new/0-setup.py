import uproot
import awkward as ak

file = uproot.open("/lstr/sahara/dune/tlabree/analysis/srcs/duneana/duneana/CERNWorkshop/Analysis/output_10_events.root")
tree = file["ana/tree"]
data = tree.arrays(["eventID", "nDaughters", "nPFParticles", "trackLength", "trackScore", "hitdEdx", "hitResRange", "truePdgCode", "trueEnergy"], library="ak")

