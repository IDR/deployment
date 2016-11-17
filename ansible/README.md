OME Ansible
===========

This contains a variety of Ansible playbooks and roles, including example files for provisioning an OpenStack VM from scratch with OMERO using Ansible.
Most of these scripts should also work on other platforms, providing the VM is brought up by some other method.

- Playbooks which start with `os` are OpenStack specific - the `os` stands for `OpenStack`.
- Playbooks which start with `idr` are for the Image Data Repository.
- Playbooks which start with `ci` are for OME continuous integration and build.

To get started with a minimal OMERO server, use the example playbook in the [README.md of roles/omero-server](/roles/omero-server/README.md).


Roles
-----
There are two roles directories.
- `roles`: These are roles which are considered ready for use. Breaking changes to these roles will be minimised.
- `roles-dev`: Roles which are still in development, or require special external configuration. These are not recommended for use.


OME OpenStack Ansible
----------------------

For the OpenStack specific README, see: [Getting started with OME OpenStack Ansible](README-os.md)

For the IDR specific OpenStack README, see: [IDR OpenStack](README-os-idr.md)


IDR Systems Infrastructure (`idrsystems-*`)
===========================================

These playbooks are for maintaining the bare-metal infrastructure for most of the IDR work.
This primarily involves maintaining the servers and storage underlying the virtualisation platforms used for development and running of the actual IDR, and is inevitably tied to the hardware configurations of these servers as well as the configuration of other services provided by the parent institution.

- `idrsystems-deployment.yml`: Use this playbook for checking and enforcing consistency of all existing IDR infrastructure.
  This includes deploying new roles to existing servers, or modifying configurations.
  If nothing has changed in the repository or inventory there should be no changes when this playbook is run.
- `idrsystems-provision.yml`: Use this playbook for ensuring all servers are provisioned and up to date.
  This includes provisioning new servers, running system upgrades, and everything in `idrsystems-deployment.yml`.
  Since this attempts to install updates there may be changes even if the repository or inventory are unchanged.


Dell Hardware (`hardware-dell`)
===============================

The playbooks in the `hardware-dell` directory can be used to help with installing Dell hardware maintenance, for instance DRAC and BIOS updates.
Given the nature of these updates these playbooks should only be run when required, and consideration given to running against one host at a time.
