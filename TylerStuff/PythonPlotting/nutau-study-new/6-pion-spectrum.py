import uproot
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# Open the ROOT file with the correct path
# file = uproot.open("/lstr/sahara/dune/tlabree/analysis/srcs/duneana/duneana/CERNWorkshop/Analysis/gen1_tau_cc_1000_events_new.root")
file = uproot.open("/lstr/sahara/dune/tlabree/analysis/srcs/duneana/duneana/CERNWorkshop/Analysis/gen1_mu_cc_1000_events_new.root")

# Access the tree
tree = file["ana/gen1"]

# Get arrays from the tree
sim_generation = tree["simGeneration"].array()
sim = tree["sim"].array()
sim_pdg_code = tree["simPdgCode"].array()
sim_energy = tree["simEnergy"].array()

# Filter for 1st generation negative pions (simGeneration==1, sim==1, simPdgCode==-211)
mask_neg_pions = (sim_generation == 1) & (sim == 1) & (sim_pdg_code == -211)
neg_pion_energies = ak.flatten(sim_energy[mask_neg_pions])

# Filter for 1st generation positive pions (simGeneration==1, sim==1, simPdgCode==211)
mask_pos_pions = (sim_generation == 1) & (sim == 1) & (sim_pdg_code == 211)
pos_pion_energies = ak.flatten(sim_energy[mask_pos_pions])

# Convert to numpy arrays for easier handling
neg_pion_energies_np = ak.to_numpy(neg_pion_energies)
pos_pion_energies_np = ak.to_numpy(pos_pion_energies)

# Print some statistics about the results
print(f"Found {len(neg_pion_energies_np)} negative pions")
if len(neg_pion_energies_np) > 0:
    print(f"Negative pion energy range: {np.min(neg_pion_energies_np):.2f} to {np.max(neg_pion_energies_np):.2f} GeV")
else:
    print("No negative pions found")

print(f"Found {len(pos_pion_energies_np)} positive pions")
if len(pos_pion_energies_np) > 0:
    print(f"Positive pion energy range: {np.min(pos_pion_energies_np):.2f} to {np.max(pos_pion_energies_np):.2f} GeV")
else:
    print("No positive pions found")

# Create a figure with two subplots side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Determine a suitable number of bins based on the data
# Using Sturges' rule: k = log2(n) + 1
bins_neg = max(100, int(np.log2(len(neg_pion_energies_np)) + 1)) if len(neg_pion_energies_np) > 0 else 10
bins_pos = max(100, int(np.log2(len(pos_pion_energies_np)) + 1)) if len(pos_pion_energies_np) > 0 else 10

# Plot negative pion energies
if len(neg_pion_energies_np) > 0:
    ax1.hist(neg_pion_energies_np, bins=bins_neg, alpha=0.7, color='red', edgecolor='black')
else:
    ax1.text(0.5, 0.5, "No negative pions found", ha='center', va='center', transform=ax1.transAxes)

ax1.set_title("First-Generation Negative Pions ($\pi^-$)")
ax1.set_xlabel("Energy (GeV)")
ax1.set_ylabel("Count")
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_minor_locator(AutoMinorLocator())
ax1.yaxis.set_minor_locator(AutoMinorLocator())

# Plot positive pion energies
if len(pos_pion_energies_np) > 0:
    ax2.hist(pos_pion_energies_np, bins=bins_pos, alpha=0.7, color='blue', edgecolor='black')
else:
    ax2.text(0.5, 0.5, "No positive pions found", ha='center', va='center', transform=ax2.transAxes)

ax2.set_title("First-Generation Positive Pions ($\pi^+$)")
ax2.set_xlabel("Energy (GeV)")
ax2.set_ylabel("Count")
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_minor_locator(AutoMinorLocator())
ax2.yaxis.set_minor_locator(AutoMinorLocator())

# Add overall title
fig.suptitle("Energy Distribution of First-Generation Pions", fontsize=16)
plt.tight_layout()

# Save the figure
plt.savefig("pion_energy_distributions_mu.png", dpi=300)

# Show the plot
