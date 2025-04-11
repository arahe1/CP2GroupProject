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

In a separate terminal, connect to vmlab. Replace 8080 with the port give form the command above. Replace $USER with your username.

ssh -L 8080:localhost:8080 $USER@vmlab.niu.edu

Copy and paste the URL from the first terminal window in a browser to open the jupyter lab session.

Git Basics:

git branch name_of_branch will create an alternate copy of everything in a new area called name_of_branch that can be safely changed so that you don't mess up the main code. As far as I can tell this is purely virtual in nature and will not give you a new repo/directory. 

git status tells you which files need added or committed from your local repo or if you are in line with the GitHub repo. Will also tell you which branch you are on.

git add <file> means that changes to that file are readied for a commit

git commit <file> -m "explain the changes" means you are committed to the changes to that file and can now be pushed to GitHub repo. Whatever is in quotes gives a hint as to what these changes are.

git push takes your local changes and changes the GitHub repo so that it is the same as your local. Can sometimes cause problems if there are other changes pushed from someone else.

git pull takes the GitHub repo and adds any changes to your local repo. Opposite of git push basically.

You also can (and i think need) to do all of these commands for each branch if you are working on a branch instead of the main

