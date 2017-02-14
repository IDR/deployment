# Deploying the IDR

The IDR runs on CentOS 7 64 bit servers only.


## Overview of the playbooks

The deployment steps are separated into multiple playbooks.
Several top-level playbooks are provided which should be suitable for the majority of cases, the most important being `idr-01-install-idr.yml`.
You should not need to run any other playbooks individually.

### [`idr-00-preinstall.yml`](../ansible/idr-00-preinstall.yml)
This handles the initialisation of storage volumes which have already been attached to the server but have not been formatted or mounted, and also configures multiple network interfaces if necessary.
If you provisioned your servers on OpenStack with the example playbook you must run this.

### [`idr-01-install-idr.yml`](../ansible/idr-01-install-idr.yml)
This is the main playbook that does almost all the work involved in setting up the IDR, including installing and setting up PostgreSQL, OMERO.server, OMERO.web, and the front-end caching Nginx proxy.

### [`idr-03-postinstall.yml`](../ansible/idr-03-postinstall.yml)
This is an optional playbook to setup some OMERO users, including setting the OMERO `root` user password to a random string (stored in `/root/idr-root-ice.config`) and creating a public user for OMERO.web.
This playbook is *not* idempotent.

### [`idr-09-monitoring.yml`](../ansible/idr-09-monitoring.yml)
This is an optional playbook to setup monitoring of the IDR and OMERO.server.
This includes configuring all servers with Munin, and enabling Slack notifications for OMERO.server errors.
You will need to provide a secret Slack token for Slack notifications.


## Ansible inventory

You have three options for setting up an Ansible inventory to use with the IDR deployment playbooks, depending on how you [provisioned the servers](provisioning.md).

### OpenStack dynamic private inventory
This is the recommended method if you provisioned the servers using the supplied OpenStack playbook and are familiar with [Ansible dynamic inventories](http://docs.ansible.com/ansible/intro_dynamic_inventory.html), and is the methods we use internally for managing the production IDR servers.

[inventories/openstack-idr.py](../inventories/openstack-idr.py) is a modified version of the [default Ansible OpenStack dynamic inventory](https://raw.githubusercontent.com/ansible/ansible/devel/contrib/inventory/openstack.py) to make it easier to use an [Ansible SSH gateway/jump host](http://docs.ansible.com/ansible/faq.html#how-do-i-configure-a-jump-host-to-access-servers-that-i-have-no-direct-access-to), and to configure multiple networks.
The main changes are:
- automatic setting of SSH ProxyCommand
- ordering of network interfaces

This inventory will attempt to automatically route all SSH access via `idr-proxy`, using metadata attached to the servers in the [IDR openstack-idr-instance](https://github.com/IDR/ansible-role-openstack-idr-instance) role.

### Static inventory
This is recommended if you have provisioned the servers yourself, or if you are unfamiliar with setting up an Ansible dynamic inventory.
Modify the hosts section in the [example static inventory](../inventories/ansible-hosts).


## Ansible deployment example

You must run Ansible from the [`ansible`](../ansible) directory.

If you are using a static inventory run:

    ansible-playbook -i ../inventories/ansible-hosts --diff -e idr_environment=idr idr-01-install-idr.yml idr-03-postinstall.yml

If you provisioned your servers using the OpenStack playbook and are using the IDR dynamic inventory run:

    ansible-playbook -i ../inventories/openstack-idr.py --diff -u centos -e idr_environment=idr idr-00-preinstall.yml idr-01-install-idr.yml idr-03-postinstall.yml

If this completes successfully you should be able to access a public OMERO.web at the IP of the `idr-proxy` server.


### Advanced deployment options
The `idr_environment` variable can be used to run multiple copies of the IDR alongside each other for testing purposes, and to minimise downtime between releases.
See the `hosts` section of each playbook for examples of how this is used.

You should always set `idr_environment=idr` unless you know exactly what you are doing.
