# CP2GroupProject
You should already have a Conda Environment Setup so while in the directory you want to use run:

conda activate columnar_env;

Then git clone this page.

If you don't have it setup already for some reason do the following:
Conda Environment Setup

conda create -n columnar_env

conda activate columnar_env

conda install jupyterlab

pip install awkward uproot

Jupyter Lab Start

Start a jupyter lab session. Use port 8080. It will likely give you a different port to be used in the ssh part.

jupyter lab --no-browser --port 8080

In a separate terminal, connect to vmlab (or Metis). Replace 8080 with the port give form the command above. Replace $USER with your username. You can also replace vmlab with Metis if you want to use Metis instead.

ssh -L 8080:localhost:8080 $USER@vmlab.niu.edu

Copy and paste the URL from the first terminal window in a browser to open the jupyter lab session.
