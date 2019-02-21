#!/usr/bin/env python

# Use the passed arguments to build and run the cloudops docker image for local development environment
# This is also included aws-vault
import sys
import os
import subprocess
import argparse
import logging
import stat

LOGLEVEL = os.getenv('LOG_LEVEL', 'INFO').strip()
logger = logging.getLogger()
logger.setLevel(LOGLEVEL.upper())
log_handler = logging.StreamHandler()
log_handler.setLevel(LOGLEVEL.upper())
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

output_dockerfile = "Dockerfile"
input_dockerfile = "templates/Dockerfile.template"
docker_entry_file = "entry.sh"
input_pip_packages_file = "templates/pip_packages.template"
output_pip_packages_file = "pip_packages"
terraform_text = "###INSTALL_TERRAFORM###"
aws_vault_text = "###INSTALL_AWS_VAULT###"


def process_arguments():
    parser = argparse.ArgumentParser()
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('Required arguments')
    #required.add_argument('-p', '--profile', help='Profile to use with aws-vault', required=True)
    optional.add_argument('-p', '--profile', help='Profile to use with aws-vault')
    optional.add_argument('-i', '--imageName', help='Docker image name', default='cloudops')
    optional.add_argument('-t', '--terraformVersion', help='Terraform version', default='0.11.7')
    optional.add_argument('-a', '--ansibleVersion', help='Ansible version', default='2.5.0')
    optional.add_argument('--dockerAppUser', help='Docker OS App user', default='cloudops')
    optional.add_argument("--installAnsible", type=str2bool, nargs='?', const=True, default=True, help="Install ansible?")
    optional.add_argument("--installTerraform", type=str2bool, nargs='?', const=True, default=True, help="Install Terraform?")
    parser._action_groups.append(optional)
    #logger.info("args {0}".format(parser.parse_args()))
    return parser.parse_args()


def str2bool(val):
    if val.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif val.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)


def create_docker_entry_file(entry_filename, profile):
    with open(entry_filename, 'w') as f:
        vault_add = "aws-vault add {0}\n".format(profile)
        vault_exec = "aws-vault exec --assume-role-ttl=1h --session-ttl=12h  {0} -- bash\n".format(profile)
        f.write('#!/bin/sh\n\n')
        f.write(vault_add)
        f.write(vault_exec)
        f.write("aws s3api list-buckets\n\n")

    # make the entrypoint executable so that the docker image can run on startup
    make_executable(entry_filename)


def create_pip_packages_file(args, input_pip_packages_file, output_pip_packages_file):
    # required development packages to install during docker build image
    with open(input_pip_packages_file) as f:
        with open(output_pip_packages_file, "w") as f1:
            for line in f:
                f1.write(line)

    # add ansible==${version}
    if args.installAnsible == True:
        with open(output_pip_packages_file, "a") as f:
            f.write("ansible=={0}\n".format(args.ansibleVersion))



def create_dockerfile_from_template(args, dockerfile_template, output_dockerfile):

    with open(dockerfile_template) as fin:
        with open(output_dockerfile, "w") as fout:
            for line in fin:
                if (args.installTerraform):
                    # terraform is required
                    if (line.startswith(terraform_text)):
                        lout = line.replace(terraform_text, '')
                        fout.write(lout)
                    # is also aws-vault required too
                    elif args.profile is not None:
                        # aws-vault is required
                        if (line.startswith(aws_vault_text)):
                            lout = line.replace(aws_vault_text, '')
                            fout.write(lout)
                        else:
                            fout.write(line)
                    else:
                        fout.write(line)

                elif args.profile is not None:
                    # aws-vault is required
                    if (line.startswith(aws_vault_text)):
                        lout = line.replace(aws_vault_text, '')
                        fout.write(lout)
                    else:
                        fout.write(line)
                else:
                    fout.write(line)


def build_docker_image(args, dockerfile):
    #you need to use os.system module to execute shell command
    build_command = 'docker build --build-arg profile={0} --build-arg terraformVersion={1} --build-arg dockerAppUser={2} --build-arg sshKey="$(cat ~/.ssh/id_rsa)"  --rm -f {3} -t {4}:latest .'.format(args.profile, args.terraformVersion, args.dockerAppUser, dockerfile, args.imageName)

    logger.info("build_command: {0}".format(build_command))
    os.system(build_command)

    #if you want to save the output for later use, you need to use subprocess module
    #child = subprocess.Popen(build_command, stdout=subprocess.PIPE, shell=True)
    #output = child.communicate()[0]
    #logger.info("build output: {0}".format(output))


def run_docker_image(args, dockerfile):
    # docker run --interactive --tty -u cloudops --rm --volume "$HOME/.aws:/home/cloudops/.aws" --volume "$HOME/repos:/repos" cloudops /bin/bash
    run_command = 'docker run --interactive --tty -u {0} --rm --volume "$HOME/.aws:/home/{0}/.aws" --volume "$HOME/repos:/repos" {1} /bin/bash'.format(args.dockerAppUser, args.imageName)

    logger.info("run_command: {0}".format(run_command))
    os.system(run_command)



def main():
    args = process_arguments()
    #image_name = args.imageName if args.imageName is not None else "cloudoups"

    if args.profile is not None:
        # create entry.sh for docker entrypoint (to use with aws-vault)
        create_docker_entry_file("entry.sh", args.profile)

    create_pip_packages_file(args, input_pip_packages_file, output_pip_packages_file)
    create_dockerfile_from_template(args, input_dockerfile, output_dockerfile)
    build_docker_image(args, output_dockerfile)
    run_docker_image(args, output_dockerfile)


if __name__ == '__main__':
    main()
