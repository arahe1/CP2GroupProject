import uproot
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import particle

# Particles that can't be reconstructed (neutral or unstable)
NON_RECONSTRUCTABLE = {2112, 22, 111, 310, 130, 3122, 2000000001, 1000180400, 311, -311} | {abs(nu) for nu in [12, 14, 16]}

def analyze_particle_reconstruction(file_path="/lstr/sahara/dune/tlabree/analysis/srcs/duneana/duneana/CERNWorkshop/Analysis/gen1_1000_events.root", 
                           neutrino_type="muon", interaction="CC", events=1000, 
                           save_name=None):
    # Load data and extract particle counts
    data = uproot.open(file_path)["ana/gen1"].arrays(library="ak")
    sim, reco = data["sim"] == 1, data["reco"] == 1
    
    unreco = Counter(ak.flatten(data["simPdgCode"][sim & ~reco]).to_numpy())
    reco = Counter(ak.flatten(data["simPdgCode"][sim & reco]).to_numpy())
    
    # Get top reconstructable particles sorted by total count
    pdgs = sorted([p for p in set(unreco) | set(reco) if abs(p) not in NON_RECONSTRUCTABLE],
                  key=lambda p: unreco.get(p, 0) + reco.get(p, 0), reverse=True)[:10]
    
    # Prepare plotting data with particle names
    def get_name(p):
        try:
            return particle.Particle.from_pdgid(p).name
        except:
            return f"PDG {p}"
    names = [get_name(p) for p in pdgs]
    unreco_vals = [unreco.get(p, 0) for p in pdgs]
    reco_vals = [reco.get(p, 0) for p in pdgs]
    efficiency = [f"{(100*r/(u+r)):.1f}%" if u+r > 0 else "N/A" for u, r in zip(unreco_vals, reco_vals)]
    
    # Create plot
    fig, ax = plt.figure(figsize=(8, 6)), plt.axes()
    x, w = np.arange(len(names)), 0.35
    
    # Add bars for unreconstructed and reconstructed counts
    unreco_bars = ax.bar(x - w/2, unreco_vals, w, label='Unreconstructed', color='#ff7f0e')
    reco_bars = ax.bar(x + w/2, reco_vals, w, label='Reconstructed', color='#1f77b4')
    
    # Configure plot appearance
    title = f'Particle Reconstruction - {events:,} {neutrino_type} neutrino {interaction} events'
    ax.set(xlabel='Particle Type', ylabel='Count', title=title,
           xticks=x, xticklabels=[n[:19] for n in names])
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Add bar value labels
    [ax.text(bar.get_x() + w/2, val + 0.1, str(int(val)), ha='center', va='bottom')
     for bars, vals in [(unreco_bars, unreco_vals), (reco_bars, reco_vals)]
     for bar, val in zip(bars, vals) if val > 0]
    
    # Save and display the plot
    output_file = save_name or f'./data/plots-new/particle_reconstruction_{neutrino_type}_{interaction}_{events}.png'
    plt.tight_layout()
    plt.savefig(output_file)
    
    # Print statistics table
    print(f"Results saved to: {output_file}")
    print("Particle Reconstruction Statistics:")
    print(f"{'Particle':<20} {'Unreco':<10} {'Reco':<10} {'Total':<10} {'Efficiency':<10}")
    print("-" * 60)
    [print(f"{n[:19]:<20} {u:<10} {r:<10} {u+r:<10} {e:<10}")
     for n, u, r, e in zip(names, unreco_vals, reco_vals, efficiency)]
    
    return names, unreco_vals, reco_vals

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Example usage with command-line arguments:
        # python script.py path/to/file.root muon CC 10000
        file_path = sys.argv[1] if len(sys.argv) > 1 else None
        nu_type = sys.argv[2] if len(sys.argv) > 2 else "muon"
        interaction = sys.argv[3] if len(sys.argv) > 3 else "CC" 
        events = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
        
        analyze_particle_reconstruction(
            file_path=file_path,
            neutrino_type=nu_type,
            interaction=interaction,
            events=events
        )
    else:
        analyze_particle_reconstruction()
