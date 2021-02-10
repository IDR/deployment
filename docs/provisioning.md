# Provisioning the IDR

## Overview of the architecture

The IDR contains two main groups of servers:

The production (public-facing) IDR (3 servers):
- Database
- OMERO.servers
- Nginx gateway

## Ansible prerequisites

Almost all of the provisioning and deployment in the IDR is done using Ansible 2.1.
All ansible commands should be run from a shell in the [`ansible`](../ansible) directory.

    cd ../ansible

You must first install the required galaxy roles:

    ansible-galaxy install -r requirements.yml

The [`ansible.cfg`](../ansible/ansible.cfg) configuration file will install the roles into the [`vendor`](../ansible/vendor) directory.


## OpenStack

The IDR is currently hosted on OpenStack, see below for an example Ansible playbook for provisioning compute, storage and networking.
The Ansible openstack modules require the `shade` python module.


### Production IDR
Network: `idr`

Instances:
- `idr-database`: PostgreSQL database server
- `idr-omeroreadwrite`: Read-write OMERO.server including OMERO.web
- `idr-omeroreadonly*`: Read-only OMERO.servers including OMERO.web
- `idr-proxy`: Nginx gateway with custom caching configuration

Volumes:
- `idr-database-db`: PostgreSQL data directory
- `idr-omeroreadwrite-data`: OMERO data directory
- `idr-proxy-nginxcache`: Nginx cache directory


### Additional resources
- `idr-management`: An instance running Munin for monitoring the production IDR platform
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

This playbook will create a set of VMs on the OpenStack cloud. You must
associate the proxy host to a floating IP either using the OpenStack UI or via
the `openstack` command-line interface:

    $ openstack floating ip list
    $ openstack server add floating ip <proxy_server_name> <ip>

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
