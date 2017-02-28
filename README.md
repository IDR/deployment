# IDR systems documentation

The [Image Data Resource (IDR)](https://idr-demo.openmicroscopy.org/) is an online, public data repository that seeks to store, integrate and serve image datasets from published scientific studies.
The IDR is also a platform that is entirely built with open-source components and tools, and these documents describe how to build and manage your own version of the IDR.

The IDR is currently hosted on [OpenStack](https://www.openstack.org/) at [EMBL-EBI](http://www.ebi.ac.uk/).
At present OpenStack is the recommended platform for all deployments.
It should be possible to deploy the IDR on other cloud platforms or physical hardware, but changes will be required, particularly with respect to network interfaces.
[Ansible](https://www.ansible.com/) (an open-source configuration management system) is used extensively for managing the IDR.


## Prerequisites

The IDR provisioning and deployment instructions are aimed at experienced system administrators familiar with using Ansible playbooks and roles for managing multiple servers.
If you are deploying the IDR platform on OpenStack you should have a good working knowledge of instances, volumes and networking.

All documents assume extensive knowledge of [OMERO](https://www.openmicroscopy.org/site/support/omero5/sysadmins/).


## Documents

[Provisioning](docs/provisioning.md): Guidelines for provisioning compute, storage and network resources for hosting the IDR, on virtual or physical hardware.

[Deployment](docs/deployment.md): Instructions on how to install the IDR using Ansible.

[idr-ansible.sh](docs/idr-ansible.sh): An example script to provision and deploy the IDR on OpenStack.

[Operating procedures](docs/operating-procedures.md): Administration of the IDR
