Network
=======

Set up custom network interface configurations for a server.

Role Variables
--------------

- `networkifaces`: A list of dictionaries, one per network device, of network parameters which will be substituted into `templates/etc-sysconfig-network-scripts-ifcfg.j2`.
- `networkifaces[].device`: The device name. All other fields are optional, see the template for details.
- `networkifaces[].bondmaster`: If specified this NIC will be part of a bonded interface. If the `device` name matches `bondmaster` it will be set as the master, otherwise it will be a slave of `bondmaster`.


Example Playbook
----------------

    # Simple network
    - hosts: localhost
      roles:
      - role: network
        networkifaces:
        - device: eth0
          ip: 192.168.1.1
          netmask: 255.255.255.0
          type: ethernet
          gateway: 192.168.1.254
          dns1: 8.8.4.4
          dns2: 8.8.8.8

    # Bonded network combining eth0 and eth1
    - hosts: localhost
      roles:
      - role: network
        networkifaces:
        - device: bond0
          ip: 192.168.1.1
          prefix: 24
          gateway: 192.168.1.254
          dns1: 8.8.4.4
          dns2: 8.8.8.8
          bondmaster: bond0
        - device: eth0
          bondmaster: bond0
        - device: eth1
          bondmaster: bond0


Author Information
------------------

ome-devel@lists.openmicroscopy.org.uk
