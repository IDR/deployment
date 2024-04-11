#!/bin/bash

cd ../ansible

# You must edit openstack-create-infrastructure.yml:
# - Add your SSH key and
# - Set parameters specific to your OpenStack cloud

ansible-galaxy install -r requirements.yml
ansible-playbook -i ../inventories/openstack-idr.py --diff openstack-create-infrastructure.yml

# Security risk, only enable this when you setup a server with a new SSH key
export ANSIBLE_HOST_KEY_CHECKING=False
export OS_PROXY_SSH_ARGS='-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
ansible-playbook -i ../inventories/openstack-idr.py --diff -u rokcy idr-00-preinstall.yml idr-01-install-idr.yml idr-03-postinstall.yml
