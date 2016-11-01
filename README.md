# gitGC

gitGC is a light-weight GatedCheckin system implemented for (self)educational purposes.

## Setup

### Prepare build server
The server needs to be exposed to the Internet through port 8080. The server software itself is written in python, but relies on some UNIX-specifics such as bash. It needs the following packages installed:
* git
* python2.7
* python-virtualenv
* mongodb-server

You also need a bitbucket or github repository, and an ssh public key that can access the repository.

### Install and run the build server software
On the server, run the following commands:
* git clone https://github.com/89erik/gitGC.git
* cd gitGC
* ./init "git@bitbucket.org:(your repository).git"
* ./start_server.py

Write your commands for building your project into build.sh (a sample file is created by the init script). This script will run during each GC as the build step. This is initially set up as a bash script, but it can be changed to something else by editing the shebang (#!/bin/bash) at the first line of the script. Enter the commands for deploying your code in deploy.sh, this file can assume that the repository contains a fresh build.

### Configure your repository
The following line must be included in a gitconfig on the developers' machines. (the name can be whatever you want).
[alias] pushtomaster = !git push origin HEAD:GC_$(date +%F_%H%M.%S.%N)

There are several ways to do this, but the best is perhaps to add it to a file .gitconfig on the root of your repository, and then having all the developers run the following command the first time they clone it.
git config --local include.path ../.gitconfig

You should also set up your bitbucket/github repository not to allow anyone to push to your official branch (e.g main), except for the user running on the build server.

The final step is to add a webhook on your bitbucket/github repo:
* Open your repo on bitbucket/github
* Go to settings -> Webhooks
* Click Add webhook
    * URL/Payload URL: http://(build server url):8080/pull
    * Status (bitbucket): checked
    * SSL/TLS (bitbucket): uncheked
    * Secret (github): empty
    * Triggers: Repository push/Just the push event
* Save

## How it works
The developer makes a couple of commits on his local machine either directly on master or another branch and then merges to master. When he wishes to push it to bitbucket's master, he types the git alias as configured above, git pushtomaster. Instead of pushing directly to master, this will push to a temporary "candidate" branch on bitbucket. The webhook configured on bitbucket will then be triggered, and call the build server with the name of the branch that was just pushed. The build server will then do a git fetch from bitbucket into its working folder and checkout the new staging branch. It will then call build.sh, which (if you have configured it to) should build the code in the staging branch. If this doesn't fail, then it will merge the staging branch into its local master and then push this to bitbucket's master. Finally, it will delete the temporary branch. If either the merging or building fails in some way, the process will be aborted and the temporary branch will be rejected.


