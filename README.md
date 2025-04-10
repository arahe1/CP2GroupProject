# CP2GroupProject
Conda Environment Setup

conda create -n columnar_env
conda activate columnar_env
conda install jupyterlab
pip install awkward uproot

After the initial Setup, future sign-ins just need to run the following:

conda activate columnar_env

Jupyter Lab Start

Start a jupyter lab session. Use port 8080. It will likely give you a different port to be used in the ssh part.

jupyter lab --no-browser --port 8080

In a separate terminal, connect to vmlab with the port given from command above. Replace $USER with your username.

ssh -L 8080:localhost:8080 $USER@vmlab.niu.edu

Copy and paste the URL from the first terminal window in a browser to open the jupyter lab session.
