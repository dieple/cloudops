## Introduction

As a Devops engineer contractor I tend to move quite often with the client contracts.
To overcome the tedious task of setting up new development environments everytime; I setup this repos to make life easier for me. Hope you'll find useful.

* Docker image/build development environment includes:
* Python3
* Flask --> microframework 
* python-terraform --> provides a wrapper of `terraform` command line tool
* python-terrascript --> generates terraform scripts using python.
* Terraform binary (defaults to v0.11.7 but can be overidden)
* Ansible  (defaults to v2.5.0 but can be overidden)
* AWS CLI
* AWS Vault --> Profiles, MFA and roles switching capability

The packages are build using pip install if possible, further addons can be included during docker image build stage.

## Installation

```bash
    git clone directory...
    cd directory
    python3 run.py -h
usage: run.py [-h] [-p PROFILE] [-i IMAGENAME] [-t TERRAFORMVERSION]
              [-a ANSIBLEVERSION] [--dockerAppUser DOCKERAPPUSER]
              [--installAnsible [INSTALLANSIBLE]]
              [--installTerraform [INSTALLTERRAFORM]]

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        Profile to use with aws-vault
  -i IMAGENAME, --imageName IMAGENAME
                        Docker image name
  -t TERRAFORMVERSION, --terraformVersion TERRAFORMVERSION
                        Terraform version
  -a ANSIBLEVERSION, --ansibleVersion ANSIBLEVERSION
                        Ansible version
  --dockerAppUser DOCKERAPPUSER
                        Docker OS App user
  --installAnsible [INSTALLANSIBLE]
                        Install ansible?
  --installTerraform [INSTALLTERRAFORM]
                        Install Terraform?

    python3 run.py  --dockerAppUser=devops --profile=dev
    ... snippep
Successfully built 4f84992ea3d1
Successfully tagged cloudops:latest
2019-02-20 16:58:52,107 - root - INFO - run_command: docker run --interactive --tty -u devops --rm --volume "$HOME/.aws:/home/devops/.aws" --volume "$HOME/repos:/repos" cloudops /bin/bash
Enter Access Key ID: YourAccessKeyId
Enter Secret Access Key: YourAcccessKeySecrets
Enter passphrase to unlock /home/devops/.awsvault/keys/:
Added credentials to profile "dev" in vault
Enter passphrase to unlock /home/devops/.awsvault/keys/:
Enter token for arn:aws:iam:::aws-account-numbermfa/dieple: 995559
Enter passphrase to unlock /home/devops/.awsvault/keys/:
devops@67fb998d20da:/repos$

Voila I've a same dev environment within a few minutes no matter where!

Note that $HOME/repos is where I checked out the git repos and can be seen in /repos in the docker image, where you can run terraform plan, etc. 
```    
