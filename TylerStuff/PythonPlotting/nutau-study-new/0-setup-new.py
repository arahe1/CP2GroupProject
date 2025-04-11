import uproot
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt

# Open the ROOT file - replace with your actual file path
file = uproot.open("/lstr/sahara/dune/tlabree/analysis/srcs/duneana/duneana/CERNWorkshop/Analysis/output_test.root")

# Access the tree - the tree name appears to be "gen1" based on your paste
tree = file["ana/gen1"]

# List all branches to confirm what we're working with
branches = tree.keys()
print("Available branches:", branches)

# Read the data into awkward arrays
data = tree.arrays(library="ak")
