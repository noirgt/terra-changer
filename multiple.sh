#!/bin/sh
export GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
git clone git@gitlab.com:noirgt-proxmox/terra-infra.git
git config --global --add safe.directory /changer/terra-infra
git config --global user.email 'noirgt@mail.ru' \
        && git config --global user.name 'TOKAMIRO NETWORK'

python3 main.py $@
