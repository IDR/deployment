Kubernetes
==========

Deploy a Kubernetes cluster with a single master using `kubeadm`.

This role is still in development, and is based on https://kubernetes.io/docs/setup/independent/create-cluster-kubeadm/

There are several other Ansible playbooks and roles for installing a simple Kubernetes cluster, but I couldn't get them to work.

To check whether the cluster has been successfully deployed try on a master node try:

    kubectl --kubeconfig /etc/kubernetes/admin.conf get pods --all-namespaces
    kubectl --kubeconfig /etc/kubernetes/admin.conf get nodes


Dependencies
------------



Role Variables
--------------



Example Playbooks
-----------------



Author Information
------------------

ome-devel@lists.openmicroscopy.org.uk
