import uproot
import awkward as ak
import numpy as np
from collections import Counter, defaultdict
import particle
import argparse
import os

# Particles that can't be reconstructed
NON_RECONSTRUCTABLE = {2112, 22, 111, 310, 130, 3122, 2000000001, 1000180400, 311, -311} | {abs(nu) for nu in [12, 14, 16]}

def get_particle_name(pdg):
    """Get readable particle name from PDG code"""
    try:
        return particle.Particle.from_pdgid(pdg).name
    except:
        return f"PDG {pdg}"

def browse_events(file_path):
    """Browser for event-by-event particle information"""
    print(f"Loading file: {file_path}")
    file = uproot.open(file_path)
    tree = file["ana/gen1"]
    data = tree.arrays(library="ak")
    
    total_events = len(data["eventID"])
    print(f"Loaded {total_events} events from {file_path}")
    
    current_event = 0
    event_stats = defaultdict(list)
    
    while True:
        # Extract event data
        if current_event >= total_events:
            print("End of file reached.")
            current_event = total_events - 1
            
        # Get event mask - all entries with this event ID
        event_id = data["eventID"][current_event]
        event_mask = data["eventID"] == event_id
        
        # Get sim and reco status for particles in this event
        sim_mask = data["sim"][event_mask] == 1
        reco_mask = data["reco"][event_mask] == 1
        
        # Get PDG codes for particles in this event
        pdg_codes = data["simPdgCode"][event_mask]
        
        # Count simulated particles
        sim_pdg = pdg_codes[sim_mask]
        sim_flat = ak.flatten(sim_pdg).to_numpy()
        sim_counts = Counter(sim_flat)
        
        # Count reconstructed particles
        reco_pdg = pdg_codes[sim_mask & reco_mask]
        reco_flat = ak.flatten(reco_pdg).to_numpy()
        reco_counts = Counter(reco_flat)
        
        # Calculate reconstructable particles
        reconstructable_sim = [p for p in sim_flat if abs(p) not in NON_RECONSTRUCTABLE]
        reconstructable_reco = [p for p in reco_flat if abs(p) not in NON_RECONSTRUCTABLE]
        
        # Get neutrino info if available
        nu_pdg = data["nuPdgCode"][current_event] if "nuPdgCode" in data else None
        
        # Display event information
        clear_screen()
        print("="*70)
        print(f"Event {current_event+1}/{total_events} (ID: {event_id})")
        
        if nu_pdg is not None:
            nu_name = get_particle_name(nu_pdg)
            print(f"Neutrino type: {nu_name} (PDG: {nu_pdg})")
        
        print("="*70)
        
        # Display summary for this event
        print(f"Total simulated particles: {len(sim_flat)}")
        print(f"Total reconstructed particles: {len(reco_flat)}")
        
        if len(reconstructable_sim) > 0:
            recon_eff = len(reconstructable_reco)/len(reconstructable_sim)
            print(f"Reconstructable particles: {len(reconstructable_sim)}")
            print(f"Reconstruction efficiency: {recon_eff:.1%}")
            
            # Store event statistics
            event_stats["total_sim"].append(len(sim_flat))
            event_stats["total_reco"].append(len(reco_flat))
            event_stats["reconstructable"].append(len(reconstructable_sim))
            event_stats["efficiency"].append(recon_eff)
        
        # Display detailed breakdown
        print("\nParticle Counts:")
        print(f"{'Particle':<25} {'PDG':<8} {'Sim':<5} {'Reco':<5} {'Efficiency':<10}")
        print("-"*70)
        
        # Combine and sort particle counts
        all_pdgs = sorted(set(sim_counts) | set(reco_counts), 
                          key=lambda p: sim_counts.get(p, 0), 
                          reverse=True)
        
        for pdg in all_pdgs:
            sim_count = sim_counts.get(pdg, 0)
            reco_count = reco_counts.get(pdg, 0)
            eff = f"{reco_count/sim_count:.1%}" if sim_count > 0 else "N/A"
            name = get_particle_name(pdg)
            
            print(f"{name[:24]:<25} {pdg:<8} {sim_count:<5} {reco_count:<5} {eff:<10}")
        
        # Navigation options
        print("\nNavigation:")
        print("n = next, p = previous, j = jump, s = stats, c = compare files, q = quit")
        choice = input("Enter choice: ").strip().lower()
        
        if choice == 'n':
            current_event = min(current_event + 1, total_events - 1)
        elif choice == 'p':
            current_event = max(current_event - 1, 0)
        elif choice == 'j':
            try:
                target = int(input("Jump to event number: ").strip()) - 1
                current_event = max(0, min(target, total_events - 1))
            except ValueError:
                print("Invalid event number")
        elif choice == 's':
            display_statistics(event_stats)
            input("Press Enter to continue...")
        elif choice == 'c':
            other_file = input("Enter path to another ROOT file to compare: ").strip()
            if os.path.exists(other_file):
                compare_files(file_path, other_file)
                input("Press Enter to continue...")
            else:
                print(f"File not found: {other_file}")
                input("Press Enter to continue...")
        elif choice == 'q':
            break
        else:
            print("Invalid choice")

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_statistics(stats):
    """Display aggregate statistics from browsed events"""
    if not stats["total_sim"]:
        print("No statistics collected yet.")
        return
        
    total_events = len(stats["total_sim"])
    
    print("\n" + "="*50)
    print(f"Statistics Summary ({total_events} events)")
    print("="*50)
    
    print(f"Average simulated particles per event: {np.mean(stats['total_sim']):.1f}")
    print(f"Average reconstructed particles per event: {np.mean(stats['total_reco']):.1f}")
    print(f"Average reconstructable particles per event: {np.mean(stats['reconstructable']):.1f}")
    print(f"Average reconstruction efficiency: {np.mean(stats['efficiency']):.1%}")

def compare_files(file1, file2):
    """Compare particle statistics between two files"""
    # Load files
    f1 = uproot.open(file1)
    data1 = f1["ana/gen1"].arrays(library="ak")
    
    f2 = uproot.open(file2)
    data2 = f2["ana/gen1"].arrays(library="ak")
    
    # Basic file info
    events1 = len(data1["eventID"])
    events2 = len(data2["eventID"])
    
    # Get particle counts
    sim1 = data1["sim"] == 1
    reco1 = data1["reco"] == 1
    sim2 = data2["sim"] == 1
    reco2 = data2["reco"] == 1
    
    # Count total particles
    sim_counts1 = Counter(ak.flatten(data1["simPdgCode"][sim1]).to_numpy())
    reco_counts1 = Counter(ak.flatten(data1["simPdgCode"][sim1 & reco1]).to_numpy())
    sim_counts2 = Counter(ak.flatten(data2["simPdgCode"][sim2]).to_numpy())
    reco_counts2 = Counter(ak.flatten(data2["simPdgCode"][sim2 & reco2]).to_numpy())
    
    # Total particles
    total_sim1 = sum(sim_counts1.values())
    total_reco1 = sum(reco_counts1.values())
    total_sim2 = sum(sim_counts2.values())
    total_reco2 = sum(reco_counts2.values())
    
    # Display comparison
    print("\n" + "="*70)
    print(f"Comparison: {os.path.basename(file1)} vs {os.path.basename(file2)}")
    print("="*70)
    
    print(f"{'':20} {'File 1':>15} {'File 2':>15} {'Difference':>15}")
    print(f"{'Events':20} {events1:>15} {events2:>15} {events2-events1:>15}")
    print(f"{'Total sim particles':20} {total_sim1:>15} {total_sim2:>15} {total_sim2-total_sim1:>15}")
    print(f"{'Avg sim per event':20} {total_sim1/events1:>15.2f} {total_sim2/events2:>15.2f} {total_sim2/events2-total_sim1/events1:>15.2f}")
    print(f"{'Total reco particles':20} {total_reco1:>15} {total_reco2:>15} {total_reco2-total_reco1:>15}")
    print(f"{'Avg reco per event':20} {total_reco1/events1:>15.2f} {total_reco2/events2:>15.2f} {total_reco2/events2-total_reco1/events1:>15.2f}")
    
    # Compare top 10 most common particles
    all_pdgs = sorted(
        set(sim_counts1) | set(sim_counts2),
        key=lambda p: (sim_counts1.get(p, 0) + sim_counts2.get(p, 0)),
        reverse=True
    )[:10]
    
    print("\nTop 10 Particles Comparison:")
    print(f"{'Particle':<25} {'PDG':<8} {'Sim 1':<8} {'Sim 2':<8} {'Diff':<8} {'Ratio':<8}")
    print("-"*70)
    
    for pdg in all_pdgs:
        sim1_count = sim_counts1.get(pdg, 0) / events1
        sim2_count = sim_counts2.get(pdg, 0) / events2
        diff = sim2_count - sim1_count
        ratio = sim2_count / max(0.001, sim1_count)
        
        name = get_particle_name(pdg)
        print(f"{name[:24]:<25} {pdg:<8} {sim1_count:<8.2f} {sim2_count:<8.2f} {diff:<+8.2f} {ratio:<8.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Event-by-event particle browser")
    parser.add_argument("file_path", help="Path to ROOT file")
    args = parser.parse_args()
    
    browse_events(args.file_path)
