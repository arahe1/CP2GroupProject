#!/bin/bash

# Usage check
if [ "$#" -ne 5 ]; then
    echo "Usage: ./submit_job.sh <script_path> <command> <run_number> <event_type> <macro_name>"
    echo "Example: ./submit_job.sh my_root.sh 'artToRoot.C(\"../data/input/\",\"../data/output/output.root\")' 01 nu_e_cc artToRoot"
    exit 1
fi

# Save inputs
script_path="$1"
command="$2"
run_number=$(printf "%02d" $3)  # Ensures the run number is two digits (01, 02, etc.)
event_type="$4"
macro_name="$5"

# Main directory for job scripts and logs, organized by run number
job_dir="./jobs/run-$run_number"

# Subdirectories for scripts and logs
scripts_dir="$job_dir/scripts"
logs_dir="$job_dir/logs"

# Create directories if they do not exist
mkdir -p "$scripts_dir"
mkdir -p "$logs_dir"

# Naming convention for files
file_name="${macro_name}-${event_type}"

# Filename for PBS script
pbs_script="$scripts_dir/$file_name.pbs"

# Job name
job_name="${macro_name}_${event_type}_run${run_number}"

# Create a PBS script with dynamic content
cat <<EOF >"$pbs_script"
#!/bin/bash
#PBS -N $job_name
#PBS -j oe
#PBS -o $logs_dir/$file_name-output.log
#PBS -e $logs_dir/$file_name-error.log
#PBS -l select=1:ncpus=1:mem=32gb
#PBS -l walltime=01:00:00

# Change to the specified directory
cd /lstr/sahara/dune/tlabree/nutau-study-new
# Execute the script with the command
"$script_path" '$command'
EOF

# Submit the generated PBS script
qsub "$pbs_script"

