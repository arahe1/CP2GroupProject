import uproot
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt
import particle
from particle import Particle
import os

def is_visible(pdg_code, energy):
    """
    Determine if a particle is visible in a LArTPC detector based on PDG code and energy.
    """
    # Check if it's a neutrino, neutral pion, or neutron
    if abs(pdg_code) in [12, 14, 16, 111, 2112]:
        return False
    
    # Check energy thresholds for different particle types
    if pdg_code in [211, -211]:  # Charged pions
        return energy > 0.1
    elif pdg_code == 2212:  # Protons
        return energy > 0.05
    elif pdg_code in [22, 11, -11, 13, -13]:  # Photons, Electrons, Muons
        return energy > 0.03
    else:
        return True  # Default case for other particles

def is_nuclear_code(pdg_code):
    """Check if the PDG code represents a nucleus."""
    return pdg_code > 1000000000

def display_event(file_path, event_index=0):
    """
    Display particle information for a specific event in a ROOT file.
    """
    # Extract filename from path
    filename = os.path.basename(file_path)
    
    # Open ROOT file and access tree
    file = uproot.open(file_path)
    tree = file["ana/gen1"]
    
    # Get total number of events
    n_events = tree.num_entries
    
    # Check if event_index is valid
    if event_index < 0 or event_index >= n_events:
        print(f"Invalid event index. Available range: 0 to {n_events-1}")
        return
    
    # Read data for the specific event
    event_data = tree.arrays(library="ak", entry_start=event_index, entry_stop=event_index+1)
    
    # Extract event ID
    event_id = event_data["eventID"][0]
    
    # Extract relevant arrays for this event
    sim_id = event_data["simID"][0]
    sim_pdg = event_data["simPdgCode"][0]
    sim_flag = event_data["sim"][0]
    reco_flag = event_data["reco"][0]
    sim_generation = event_data["simGeneration"][0]
    sim_energy = event_data["simEnergy"][0]
    
    # Count particles and duplicates
    total_particles = len(sim_id)
    unique_simids = set([sid for sid in sim_id if sid != -1])
    duplicate_count = sum([list(sim_id).count(sid) > 1 for sid in unique_simids])
    
    # Print event header as markdown
    print(f"\nFile: {filename}")
    print(f"Event ID: {event_id}  |  Total Particles: {total_particles}  |  Duplicate Particles: {duplicate_count}\n")
    
    # Print markdown table header with new column order
    print("| ID    | Particle    | Generation | Visible | Reconstructed | Energy (GeV) |")
    print("|-------|-------------|------------|---------|---------------|--------------|")
    
    # Print particle information as markdown table rows
    for i in range(total_particles):
        # Format particle ID
        id_str = f"{sim_id[i]}" if sim_id[i] != -1 else "-"
        
        # Get particle name from PDG code
        try:
            if sim_pdg[i] != 0:
                particle_name = Particle.from_pdgid(sim_pdg[i]).name
            else:
                particle_name = "Unknown"
        except:
            particle_name = f"PDG:{sim_pdg[i]}"
        
        # Format simulation and reconstruction flags
        reco_str = "✓" if reco_flag[i] == 1 else "✗"
        
        # Get generation value and energy
        generation = str(sim_generation[i])
        energy = sim_energy[i]
        
        # Determine if particle is visible with updated criteria
        visible = is_visible(sim_pdg[i], energy) and not is_nuclear_code(sim_pdg[i])
        vis_str = "✓" if visible else "✗"
        
        # Format energy with 3 decimal places
        energy_str = f"{energy:.3f}"
        
        # Format everything with consistent spacing
        id_formatted = id_str.ljust(5)
        particle_formatted = particle_name.ljust(11)
        gen_formatted = generation.center(10)
        vis_formatted = vis_str.center(7)
        reco_formatted = reco_str.center(13)
        energy_formatted = energy_str.ljust(12)
        
        # Print markdown table row with proper spacing and new column order
        print(f"| {id_formatted} | {particle_formatted} | {gen_formatted} | {vis_formatted} | {reco_formatted} | {energy_formatted} |")
    
    print(f"\nEvent {event_index+1} of {n_events}")
    
    return n_events

def interactive_pager():
    """
    Interactive pager to browse through events in ROOT files.
    """
    # Define file paths
    file_dir = "/lstr/sahara/dune/tlabree/analysis/srcs/duneana/duneana/CERNWorkshop/Analysis/"
    mu_file = os.path.join(file_dir, "gen1_mu_cc_100_events_new.root")
    tau_file = os.path.join(file_dir, "gen1_tau_cc_100_events_new.root")
    
    # Select file
    print("Available files:")
    print("1. gen1_mu_cc_100_events_new.root")
    print("2. gen1_tau_cc_100_events_new.root")
    
    file_choice = input("Select file (1 or 2): ")
    file_path = mu_file if file_choice == "1" else tau_file
    
    # Start with the first event
    current_event = 0
    n_events = display_event(file_path, current_event)
    
    # Interactive loop
    while True:
        command = input("\nCommands: [n]ext, [p]revious, [g]oto event #, [q]uit: ")
        
        if command.lower() == 'n':
            if current_event < n_events - 1:
                current_event += 1
                n_events = display_event(file_path, current_event)
            else:
                print("Already at the last event.")
        
        elif command.lower() == 'p':
            if current_event > 0:
                current_event -= 1
                n_events = display_event(file_path, current_event)
            else:
                print("Already at the first event.")
        
        elif command.lower().startswith('g'):
            try:
                goto_event = int(command.split()[1]) - 1  # Convert to 0-based index
                if 0 <= goto_event < n_events:
                    current_event = goto_event
                    n_events = display_event(file_path, current_event)
                else:
                    print(f"Event index out of range. Valid range: 1 to {n_events}")
            except:
                print("Invalid goto command. Format: g EVENT_NUMBER")
        
        elif command.lower() == 'q':
            print("Exiting pager.")
            break
        
        else:
            print("Invalid command.")

# Run the interactive pager
if __name__ == "__main__":
    interactive_pager()
