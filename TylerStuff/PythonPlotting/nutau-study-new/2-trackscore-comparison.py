import uproot
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt

file = uproot.open("/lstr/sahara/dune/tlabree/analysis/srcs/duneana/duneana/CERNWorkshop/Analysis/output_1000_events.root")
tree = file["ana/tree"]
data = tree.arrays(["trackScore", "truePdgCode"], library="ak")

muon_tracks = ak.flatten(data["trackScore"][abs(data["truePdgCode"]) == 13])
pion_tracks = ak.flatten(data["trackScore"][abs(data["truePdgCode"]) == 211])

plt.figure(figsize=(8,6))
plt.hist(muon_tracks, bins=50, range=[0, 1], histtype='step', label='Muons')
plt.hist(pion_tracks, bins=50, range=[0, 1], histtype='step', label='Pions')
plt.xlabel("Residual Range [cm]")
plt.ylabel("dE/dx [MeV/cm]")
plt.legend()
plt.xlim(0, 1)
plt.savefig("data/plots-new/track_score_comparison.svg")
plt.close()

