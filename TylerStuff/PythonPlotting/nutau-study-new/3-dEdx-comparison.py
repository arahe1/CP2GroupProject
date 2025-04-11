import uproot
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt

file = uproot.open("/lstr/sahara/dune/tlabree/analysis/srcs/duneana/duneana/CERNWorkshop/Analysis/output_1000_events.root")
tree = file["ana/tree"]
data = tree.arrays(["hitdEdx", "hitResRange", "truePdgCode"], library="ak")

muon_mask = abs(data["truePdgCode"]) == 13
pion_mask = abs(data["truePdgCode"]) == 211

muon_resrange = data["hitResRange"][muon_mask]
muon_dedx = data["hitdEdx"][muon_mask]

pion_resrange = data["hitResRange"][pion_mask]
pion_dedx = data["hitdEdx"][pion_mask]

plt.figure(figsize=(8, 6))

plt.scatter(ak.ravel(muon_resrange), ak.ravel(muon_dedx), label="Muons", alpha=0.05)
plt.scatter(ak.ravel(pion_resrange), ak.ravel(pion_dedx), label="Pions", alpha=0.05)

plt.xlabel("Residual Range [cm]")
plt.ylabel("dE/dx [MeV/cm]")
plt.legend()
plt.xlim(0, 130)
plt.ylim(0, 15)
plt.savefig("data/plots-new/dEdx_scatter.png")

