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

This role requires the distribution Docker package (you must install it yourself).
Using the upstream package is currently not supported.


Role Variables
--------------

Required:
- `kubernetes_role`: Either `master` or `worker`, currently only a single master is supported

Optional:
- `kubernetes_token`: The token for initialising/joining a cluster
- `kubernetes_advertise_address`: The address for connecting to the Kubernetes master
- `kubernetes_install_docker`: Whether to automatically install the distribution docker (Kubernetes will probably fail if you try to use the upstream package)


Example Playbooks
-----------------


Author Information
------------------

ome-devel@lists.openmicroscopy.org.uk
