import uproot
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import particle

# Open the file with your specified path
file = uproot.open("/lstr/sahara/dune/tlabree/analysis/srcs/duneana/duneana/CERNWorkshop/Analysis/gen1_1000_events.root")
tree = file["ana/gen1"]
data = tree.arrays(library="ak")

# Define which particles should be reconstructable
def is_reconstructable(pdg_code):
    # Particles that are not reconstructable (neutral particles)
    non_reconstructable = [
        2112,   # neutron
        22,     # photon/gamma
        111,    # pi0
        310,    # K0_S
        130,    # K0_L
        3122,   # Lambda
        2000000001,  # Nuclear fragments often have special codes
        # Add more as needed
    ]
    
    # Check if this is a neutral particle
    if pdg_code in non_reconstructable:
        return False
    
    # Check if it's a neutrino (PDG codes 12, 14, 16 and their antiparticles)
    if abs(pdg_code) in [12, 14, 16]:
        return False
        
    # Otherwise, it should be reconstructable
    return True

# Function to analyze both reconstructed and unreconstructed particles
def analyze_particles():
    # Create masks for different categories
    sim_mask = data["sim"] == 1
    reco_mask = data["reco"] == 1
    
    # Particles that are simulated but not reconstructed (sim==1, reco==0)
    unreco_mask = sim_mask & (data["reco"] == 0)
    
    # Particles that are both simulated and reconstructed (sim==1, reco==1)
    reco_mask = sim_mask & (data["reco"] == 1)
    
    # Extract PDG codes for both categories
    unreco_pdg_codes = data["simPdgCode"][unreco_mask]
    reco_pdg_codes = data["simPdgCode"][reco_mask]
    
    # Flatten and count
    flat_unreco_pdg = ak.flatten(unreco_pdg_codes).to_numpy()
    flat_reco_pdg = ak.flatten(reco_pdg_codes).to_numpy()
    
    unreco_counts = Counter(flat_unreco_pdg)
    reco_counts = Counter(flat_reco_pdg)
    
    return unreco_counts, reco_counts

# Get counts for both categories
unreco_counts, reco_counts = analyze_particles()

# Combine both counters to get the set of all PDG codes
all_pdg_codes = set(unreco_counts.keys()) | set(reco_counts.keys())

# Sort PDG codes by total count (unreco + reco)
sorted_pdg_codes = sorted(all_pdg_codes, 
                          key=lambda x: (unreco_counts.get(x, 0) + reco_counts.get(x, 0)),
                          reverse=True)


sorted_pdg_codes = [pdg for pdg in sorted_pdg_codes if is_reconstructable(pdg)]

# Limit to top N for better readability
top_n = min(15, len(sorted_pdg_codes))
top_pdg_codes = sorted_pdg_codes[:top_n]

# Get counts for each category
unreco_values = [unreco_counts.get(pdg, 0) for pdg in top_pdg_codes]
reco_values = [reco_counts.get(pdg, 0) for pdg in top_pdg_codes]

# Use particle package to get proper names
def get_particle_name(pdg_code):
    try:
        return particle.Particle.from_pdgid(pdg_code).name
    except:
        return f"PDG {pdg_code}"

# Get particle names for the plot
names = [get_particle_name(code) for code in top_pdg_codes]

# Set up the plot
fig, ax = plt.figure(figsize=(14, 10)), plt.axes()

# Width of each bar
width = 0.35

# Positions for bars
x = np.arange(len(names))

# Create bars
unreco_bars = ax.bar(x - width/2, unreco_values, width, label='Unreconstructed', color='#ff7f0e')
reco_bars = ax.bar(x + width/2, reco_values, width, label='Reconstructed', color='#1f77b4')

# Add labels and title
ax.set_xlabel('Particle Type', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.set_title('Comparison of Reconstructed vs. Unreconstructed Particles', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(names, rotation=45, ha='right', fontsize=10)
ax.legend()

# Add grid for better readability
ax.grid(axis='y', linestyle='--', alpha=0.3)

# Add values on top of bars for both categories
def add_labels(bars, values):
    for bar, value in zip(bars, values):
        if value > 0:  # Only add label if the value is greater than 0
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(value)}', ha='center', va='bottom', fontsize=9)

add_labels(unreco_bars, unreco_values)
add_labels(reco_bars, reco_values)

# Calculate and display reconstruction efficiency for each particle type
for i, pdg in enumerate(top_pdg_codes):
    total = unreco_values[i] + reco_values[i]
    if total > 0:
        efficiency = (reco_values[i] / total) * 100
        ax.text(i, max(unreco_values[i], reco_values[i]) + 5, 
                f"{efficiency:.1f}%", ha='center', va='bottom', 
                fontsize=8, color='green')

plt.tight_layout()
plt.savefig('particle_reconstruction_comparison.png')
plt.show()

# Print statistics
print("Particle Reconstruction Statistics:")
print(f"{'Particle':<20} {'Unreco':<10} {'Reco':<10} {'Total':<10} {'Efficiency':<10}")
print("-" * 60)

for i, pdg in enumerate(top_pdg_codes):
    name = names[i]
    unreco = unreco_values[i]
    reco = reco_values[i]
    total = unreco + reco
    
    if total > 0:
        efficiency = (reco / total) * 100
        efficiency_str = f"{efficiency:.1f}%"
    else:
        efficiency_str = "N/A"
    
    print(f"{name:<20} {unreco:<10} {reco:<10} {total:<10} {efficiency_str:<10}")
