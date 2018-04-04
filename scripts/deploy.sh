#!/bin/bash
set -e

echo $ANSIBLE_VAULT_PASSWORD > ~/ansible_vault_password.txt
mkdir ~/.ssh/
chmod 700 ~/.ssh
echo $SSH_KEY > ~/.ssh/id_rsa

git clone https://gitlab.com/paddatrapper/dotfiles ~/dotfiles
cd ~/dotfiles
stow ansible

cd ~/
git clone https://gitlab.com/paddatrapper/ansible
cd ~/ansible

ansible-playbook --vault-password-file=~/ansible_vault_password.txt

rm ~/ansible_vault_password.txt
