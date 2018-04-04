#!/bin/bash
set -e

which ssh-agent || ( apt-get update -y && apt-get install openssh-client -y )
eval $(ssh-agent -s)
echo "$SSH_KEY" | tr -d '\r' | ssh-add - > /dev/null
mkdir ~/.ssh && chmod 700 ~/.ssh

git clone https://gitlab.com/paddatrapper/dotfiles ~/dotfiles
cd ~/dotfiles
stow ansible

git clone https://gitlab.com/zebra-crossing/ansible ~/ansible
cd ~/ansible

ansible-playbook site.yml
