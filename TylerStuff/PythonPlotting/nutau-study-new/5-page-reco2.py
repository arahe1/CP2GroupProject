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

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def analyze_event_simids(event_data, sim_mask, reco_mask):
    """Analyze particles sharing the same simID in an event"""
    # Get simIDs for this event
    sim_ids = event_data["simID"][sim_mask]
    flat_sim_ids = ak.flatten(sim_ids).to_numpy()
    
    # Count occurrences of each simID
    sim_id_counts = Counter(flat_sim_ids)
    
    # Get reconstructed particles
    reco_ids = event_data["simID"][sim_mask & reco_mask]
    flat_reco_ids = ak.flatten(reco_ids).to_numpy()
    reco_id_counts = Counter(flat_reco_ids)
    
    # Count simIDs with multiple particles
    multi_ids = {id: count for id, count in sim_id_counts.items() if count > 1}
    
    # Results
    stats = {
        "unique_simids": len(sim_id_counts),
        "multi_simids": len(multi_ids),
        "particles_per_id": list(sim_id_counts.values()),
        "sim_id_counts": sim_id_counts,
        "reco_id_counts": reco_id_counts,
        "multi_ids": multi_ids
    }
    
    return stats

def print_simid_analysis(stats):
    """Print simID analysis results"""
    print("\nSimID Analysis:")
    print(f"Unique simIDs: {stats['unique_simids']}")
    print(f"SimIDs with multiple particles: {stats['multi_simids']}")
    
    if stats['multi_ids']:
        print("\nTop simIDs with multiple particles:")
        print(f"{'SimID':<10} {'Sim Count':<10} {'Reco Count':<10} {'Reco %':<10}")
        print("-" * 50)
        
        for sim_id, count in sorted(stats['multi_ids'].items(), key=lambda x: x[1], reverse=True)[:5]:
            reco_count = stats['reco_id_counts'].get(sim_id, 0)
            reco_percent = f"{reco_count/count:.1%}" if count > 0 else "N/A"
            print(f"{sim_id:<10} {count:<10} {reco_count:<10} {reco_percent:<10}")

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
    
    # Display simID statistics if they were collected
    if "unique_simids" in stats and stats["unique_simids"]:
        print("\nSimID Statistics:")
        print(f"Average unique simIDs per event: {np.mean(stats['unique_simids']):.1f}")
        print(f"Average multi-particle simIDs per event: {np.mean(stats['multi_simids']):.1f}")
        
        # Distribution of particles per simID
        if "particles_per_id" in stats and stats["particles_per_id"]:
            all_counts = [count for event_counts in stats["particles_per_id"] for count in event_counts]
            multi_counts = [count for count in all_counts if count > 1]
            
            if multi_counts:
                bins = min(10, max(multi_counts))
                hist, edges = np.histogram(multi_counts, bins=bins)
                
                print("\nDistribution of particles per multi-particle simID:")
                for i in range(len(hist)):
                    bin_start = int(edges[i])
                    bin_end = int(edges[i+1])
                    bin_label = f"{bin_start}" if bin_start == bin_end else f"{bin_start}-{bin_end}"
                    bar_length = int(20 * hist[i] / max(hist)) if max(hist) > 0 else 0
                    print(f"  {bin_label:>5} particles: {'#' * bar_length} ({hist[i]})")

def compare_files(file1, file2):
    """Compare particle statistics between two files"""
    print(f"Loading file 1: {file1}")
    f1 = uproot.open(file1)
    data1 = f1["ana/gen1"].arrays(library="ak")
    
    print(f"Loading file 2: {file2}")
    f2 = uproot.open(file2)
    data2 = f2["ana/gen1"].arrays(library="ak")
    
    # Basic file info
    events1 = len(data1["eventID"])
    events2 = len(data2["eventID"])
    
    # Check if simID exists in both files
    has_sim_id = "simID" in data1 and "simID" in data2
    
    # Count particles
    sim1 = data1["sim"] == 1
    reco1 = data1["reco"] == 1
    sim2 = data2["sim"] == 1
    reco2 = data2["reco"] == 1
    
    # Count simulated and reconstructed particles
    sim_pdg1 = ak.flatten(data1["simPdgCode"][sim1]).to_numpy()
    reco_pdg1 = ak.flatten(data1["simPdgCode"][sim1 & reco1]).to_numpy()
    sim_pdg2 = ak.flatten(data2["simPdgCode"][sim2]).to_numpy()
    reco_pdg2 = ak.flatten(data2["simPdgCode"][sim2 & reco2]).to_numpy()
    
    # Get total counts
    total_sim1 = len(sim_pdg1)
    total_reco1 = len(reco_pdg1)
    total_sim2 = len(sim_pdg2)
    total_reco2 = len(reco_pdg2)
    
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
    
    # Compare by particle types
    sim_counts1 = Counter(sim_pdg1)
    sim_counts2 = Counter(sim_pdg2)
    
    # Get top 10 particles
    all_pdgs = sorted(
        set(sim_counts1) | set(sim_counts2),
        key=lambda p: (sim_counts1.get(p, 0) + sim_counts2.get(p, 0)),
        reverse=True
    )[:10]
    
    print("\nTop 10 Particles Comparison (avg per event):")
    print(f"{'Particle':<25} {'PDG':<8} {'File 1':<8} {'File 2':<8} {'Diff':<8} {'Ratio':<8}")
    print("-" * 70)
    
    for pdg in all_pdgs:
        sim1_count = sim_counts1.get(pdg, 0) / events1
        sim2_count = sim_counts2.get(pdg, 0) / events2
        diff = sim2_count - sim1_count
        ratio = sim2_count / max(0.001, sim1_count)
        
        name = get_particle_name(pdg)
        print(f"{name[:24]:<25} {pdg:<8} {sim1_count:<8.2f} {sim2_count:<8.2f} {diff:<+8.2f} {ratio:<8.2f}")
    
    # SimID comparison if available
    if has_sim_id:
        print("\nSimID Analysis:")
        
        # Process simID data for file 1
        sim_ids1 = ak.flatten(data1["simID"][sim1]).to_numpy()
        sim_id_counts1 = Counter(sim_ids1)
        multi_ids1 = sum(1 for count in sim_id_counts1.values() if count > 1)
        avg_per_id1 = sum(sim_id_counts1.values()) / len(sim_id_counts1) if sim_id_counts1 else 0
        
        # Process simID data for file 2
        sim_ids2 = ak.flatten(data2["simID"][sim2]).to_numpy()
        sim_id_counts2 = Counter(sim_ids2)
        multi_ids2 = sum(1 for count in sim_id_counts2.values() if count > 1)
        avg_per_id2 = sum(sim_id_counts2.values()) / len(sim_id_counts2) if sim_id_counts2 else 0
        
        print(f"{'Unique simIDs':20} {len(sim_id_counts1):>15} {len(sim_id_counts2):>15} {len(sim_id_counts2)-len(sim_id_counts1):>15}")
        print(f"{'Multi-particle simIDs':20} {multi_ids1:>15} {multi_ids2:>15} {multi_ids2-multi_ids1:>15}")
        print(f"{'Avg particles per simID':20} {avg_per_id1:>15.2f} {avg_per_id2:>15.2f} {avg_per_id2-avg_per_id1:>15.2f}")
        
        # Histogram of particles per simID for both files
        counts1 = [count for count in sim_id_counts1.values() if count > 1]
        counts2 = [count for count in sim_id_counts2.values() if count > 1]
        
        if counts1 and counts2:
            max_count = max(max(counts1), max(counts2))
            bins = min(10, max_count)
            
            hist1, edges = np.histogram(counts1, bins=bins)
            hist2, _ = np.histogram(counts2, bins=edges)
            
            print("\nDistribution of particles per simID:")
            print(f"{'Particles':>10} {'File 1':>15} {'File 2':>15} {'Diff':>10}")
            for i in range(len(hist1)):
                bin_start = int(edges[i])
                bin_end = int(edges[i+1])
                bin_label = f"{bin_start}" if bin_start == bin_end else f"{bin_start}-{bin_end}"
                print(f"{bin_label:>10} {hist1[i]:>15} {hist2[i]:>15} {hist2[i]-hist1[i]:>+10}")

def browse_events(file_path):
    """Browser for event-by-event particle information"""
    print(f"Loading file: {file_path}")
    file = uproot.open(file_path)
    tree = file["ana/gen1"]
    data = tree.arrays(library="ak")
    
    total_events = len(data["eventID"])
    print(f"Loaded {total_events} events from {file_path}")
    
    # Check if file has simID information
    has_sim_id = "simID" in data
    
    current_event = 0
    event_stats = defaultdict(list)
    
    while True:
        # Extract event data for current event
        if current_event >= total_events:
            print("End of file reached.")
            current_event = total_events - 1
            
        # Get event mask - all entries with this event ID
        event_id = data["eventID"][current_event]
        event_mask = data["eventID"] == event_id
        
        # Extract the data for just this event
        event_data = data[event_mask]
        
        # Get sim and reco masks for this event
        sim_mask = event_data["sim"] == 1
        reco_mask = event_data["reco"] == 1
        
        # Count simulated particles
        sim_pdg = event_data["simPdgCode"][sim_mask]
        sim_flat = ak.flatten(sim_pdg).to_numpy()
        sim_counts = Counter(sim_flat)
        
        # Count reconstructed particles
        reco_pdg = event_data["simPdgCode"][sim_mask & reco_mask]
        reco_flat = ak.flatten(reco_pdg).to_numpy()
        reco_counts = Counter(reco_flat)
        
        # Calculate reconstructable particles
        reconstructable_sim = [p for p in sim_flat if abs(p) not in NON_RECONSTRUCTABLE]
        reconstructable_reco = [p for p in reco_flat if abs(p) not in NON_RECONSTRUCTABLE]
        
        # Get neutrino info if available
        nu_pdg = event_data["nuPdgCode"][0] if "nuPdgCode" in event_data else None
        
        # Clear screen and show event info
        clear_screen()
        print("="*70)
        print(f"Event {current_event+1}/{total_events} (ID: {event_id})")
        
        if nu_pdg is not None:
            nu_name = get_particle_name(nu_pdg)
            print(f"Neutrino type: {nu_name} (PDG: {nu_pdg})")
        
        print("="*70)
        
        # Display event summary
        print(f"Total simulated particles: {len(sim_flat)}")
        print(f"Total reconstructed particles: {len(reco_flat)}")
        
        if len(reconstructable_sim) > 0:
            recon_eff = len(reconstructable_reco)/len(reconstructable_sim)
            print(f"Reconstructable particles: {len(reconstructable_sim)}")
            print(f"Reconstruction efficiency: {recon_eff:.1%}")
            
            # Store basic event statistics
            event_stats["total_sim"].append(len(sim_flat))
            event_stats["total_reco"].append(len(reco_flat))
            event_stats["reconstructable"].append(len(reconstructable_sim))
            event_stats["efficiency"].append(recon_eff)
        
        # Analyze simID statistics if available
        if has_sim_id:
            simid_stats = analyze_event_simids(event_data, sim_mask, reco_mask)
            print_simid_analysis(simid_stats)
            
            # Store simID statistics
            event_stats["unique_simids"].append(simid_stats["unique_simids"])
            event_stats["multi_simids"].append(simid_stats["multi_simids"])
            event_stats["particles_per_id"].append(simid_stats["particles_per_id"])
        
        # Display detailed particle breakdown
        print("\nParticle Counts:")
        print(f"{'Particle':<25} {'PDG':<8} {'Sim':<5} {'Reco':<5} {'Efficiency':<10}")
        print("-"*70)
        
        # Get all PDG codes sorted by count
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Event-by-event particle browser")
    parser.add_argument("file_path", help="Path to ROOT file")
    args = parser.parse_args()
    
    browse_events(args.file_path)
