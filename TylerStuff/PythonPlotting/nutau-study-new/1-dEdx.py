import uproot
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt

file = uproot.open(
    "/lstr/sahara/dune/tlabree/analysis/srcs/duneana/duneana/CERNWorkshop/Analysis/output_10_events.root"
)
tree = file["ana/tree"]
data = tree.arrays(["hitdEdx", "hitResRange"], library="ak")

# Filter out indices where either value is NaN
valid_indices = [i for i, (x, y) in enumerate(zip(
    ak.flatten(data["hitResRange"], axis=None),
    ak.flatten(data["hitdEdx"], axis=None),
)) if not (np.isnan(x) or np.isnan(y))]

# Create lists using the valid indices
xs = [ak.flatten(data["hitResRange"], axis=None)[i] for i in valid_indices]
ys = [ak.flatten(data["hitdEdx"], axis=None)[i] for i in valid_indices]

# Plot
plt.figure(figsize=(8,6))
plt.hist2d(xs, ys, bins=[130, 150], range=[[0, 130], [0, 15]], cmap='viridis')
plt.xlabel("trackResRange [cm]")
plt.ylabel("trackdEdx [MeV/cm]")
plt.colorbar(label="Counts")
plt.xlim(0, 130)
plt.ylim(0, 15)
plt.savefig("data/plots-new/dEdx.svg")

