# Provisioning the IDR

## Overview of the architecture

The IDR contains two main groups of servers:

The production (public-facing) IDR (3 servers):
- Database
- OMERO.server
- Nginx gateway

The virtual analysis environment (VAE) IDR (3 servers):
- Database
- OMERO.server
- Docker Manager


## Ansible prerequisites

Almost all of the provisioning and deployment in the IDR is done using Ansible 2.1.
All ansible commands should be run from a shell in the [`ansible`](../ansible) directory.

You must first install the required galaxy roles:

    ansible-galaxy install -r requirements.yml

The [`ansible.cfg`](../ansible/ansible.cfg) configuration file will install the roles into the [`vendor`](../ansible/vendor) directory.


## OpenStack

The IDR is currently hosted on OpenStack, and we have an [example Ansible playbook](../ansible/openstack-create-infrastructure.yml) for provisioning compute, storage and networking.
The Ansible openstack modules require the `shade` python module.

This playbook will create two networks `idr` and `idr-a` for the production and analysis servers, and multiple instances and storage volumes.


### Production IDR
Network: `idr`

Instances:
- `idr-database`: PostgreSQL database server.
- `idr-omero`: OMERO.server, including OMERO.web.
- `idr-proxy`: Nginx gateway with custom caching configuration.

Volumes:
- `idr-database-db`: PostgreSQL data directory.
- `idr-omero-data`: OMERO data directory.
- `idr-proxy-nginxcache`: Nginx cache directory.


### Analysis IDR
Network: `idr-a`

Instances:
- `idr-a-database`: PostgreSQL database server.
- `idr-a-omero`: OMERO.server.
- `idr-a-dockermanager`: A Docker server for running VAEs.

Volumes:
- `idr-a-database-db`: PostgreSQL data directory.
- `idr-a-omero-data`: OMERO data directory.
- `idr-a-dockermanager-jupyter`: Files created by the VAE.

Note `idr-proxy` is also connected to the `idr-a` network to provide access to the analysis platform.

Separate networks are used to provide segregation between the restricted public-facing IDR, and the internal analysis IDR.


### Additional resources
- `idr-management`: An instance running Munin for monitoring the production IDR platform (attached to `idr` and `idr-a` networks).
- Security rules to restrict external access.
- Ansible hostgroup metadata is set on each instance to ensure the playbooks automatically run against the correct hosts.
- One floating IP attached to `idr-proxy`.
  All other instances will only be accessible by using this node as a proxy.


### Ansible provisioning example

You will need to customize the variables at the top of [`openstack-create-infrastructure.yml`](../ansible/openstack-create-infrastructure.yml) to fit with your OpenStack cloud.
In particular, you must define a list of SSH public key(s), for example:

    - idr_keypair_keys: ["ssh-rsa SSH_PUBLIC_KEY"]

You must have a [CentOS 7 cloud image](https://cloud.centos.org/centos/7/images/) (or equivalent) available.

Ensure you can login to OpenStack from the command line using [an OpenStack RC file](http://docs.openstack.org/user-guide/common/cli-set-environment-variables-using-openstack-rc.html) or equivalent, and run:

    ansible-playbook -i localhost, --diff openstack-create-infrastructure.yml

Ensure this playbook successfully runs to completion before [deploying the IDR](deployment.md).

Warning: At present the `nova` command may be used to [attach additional network interfaces to instances](https://github.com/IDR/ansible-role-openstack-idr-instance-network).
`nova` does not support [`clouds.yaml`](http://docs.openstack.org/developer/os-client-config/).
This will be fixed when the `openstack` command-line client supports this feature.


## Other platforms

You should be able to install the IDR on other clouds or physical hardware by provisioning the resources yourself.
All servers must be running CentOS 7.
An example static inventory is included in [`inventories/ansible-hosts`](../inventories/ansible-hosts).

For a minimal install you must have one host in each of:
- `idr-database-hosts`
- `idr-omero-hosts`
- `idr-proxy-hosts`

The other groups can be empty.

Once you have set up your servers you can [deploy the IDR](deployment.md).
