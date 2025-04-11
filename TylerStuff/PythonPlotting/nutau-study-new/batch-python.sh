#!/bin/bash

# Define the directory where this script resides
SCRIPT_DIR='/lstr/sahara/dune/tlabree/nutau-study'

# Define the path to the virtual environment relative to the script's location
VENV_PATH="$SCRIPT_DIR/venv/bin/activate"

# Concatenate all arguments into a single command for Python
PYTHON_COMMAND="$*"

# Check if the virtual environment activation script exists
if [ ! -f "$VENV_PATH" ]; then
    echo "Virtual environment activation script not found at $VENV_PATH"
    exit 1
fi

# Execute the Python command within the virtual environment
source "$VENV_PATH"
python $PYTHON_COMMAND
deactivate

