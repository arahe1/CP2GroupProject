#!/bin/bash

# Define the apptainer command
APPTAINER_CMD="/cvmfs/oasis.opensciencegrid.org/mis/apptainer/current/bin/apptainer"

# Define the container path
CONTAINER_PATH="/cvmfs/singularity.opensciencegrid.org/fermilab/fnal-dev-sl7:latest"

# Define the bind paths
BIND_PATHS="/cvmfs,/lstr/sahara/,/home,/opt,/run/user,/etc/hostname,/etc/hosts,/etc/krb5.conf"

# Concatenate all arguments into a single command for ROOT
ROOT_COMMAND="$*"

# Properly escape and quote the entire ROOT command to ensure it's interpreted correctly
ESCAPED_ROOT_COMMAND=$(echo "$ROOT_COMMAND" | sed 's/"/\\"/g')

# Execute the command inside the apptainer container
$APPTAINER_CMD exec -B $BIND_PATHS --ipc --pid $CONTAINER_PATH bash -c " \
    source /cvmfs/dune.opensciencegrid.org/products/dune/setup_dune.sh; \
    setup dunesw v09_78_03d01 -q e20:prof; \
    root \"$ESCAPED_ROOT_COMMAND\" \
"

