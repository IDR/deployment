#!/usr/bin/env python
# Assign an existing floating IP to an instance
# The target server must already have a (different) floating IP assigned
# The target floating IP can be specified as a domain name
#
# Examples:
#
#     os-idr-swapip.py idr-proxy 10.0.0.1
#     os-idr-swapip.py idr-proxy idr.openmicroscopy.org
#
# 1. Release the IP on the target server
# 2. If the target IP is assigned to another server release it
# 3. Assign the target IP to the target server
# 4. If the target IP was previously assigned to another server then assign
#    target's previous IP to that server (i.e. swap the IPs)

from builtins import input
import shade
import socket
import sys


class DetachFloatingIP(object):
    def __init__(self, cloud, floatingips, server):
        self.cloud = cloud
        fip = floatingips[server.accessIPv4]
        self.kwargs = dict(server_id=server.id, floating_ip_id=fip.id)
        self.description = 'Detaching IP {0} from {1} ({2})'.format(
            fip.floating_ip_address, server.name, fip.fixed_ip_address)

    def __call__(self):
        cloud.detach_ip_from_server(**self.kwargs)

    def __str__(self):
        return self.description


class AttachFloatingIP(object):
    def __init__(self, cloud, floatingips, server, targetip):
        self.cloud = cloud
        fip = floatingips[server.accessIPv4]
        if targetip not in floatingips:
            raise ValueError(
                '{0} is not an existing floating IP'.format(targetip))
        self.kwargs = dict(
            server=server,
            ips=targetip,
            wait=True,
            fixed_address=fip.fixed_ip_address,
        )
        self.description = 'Attaching IP {0} to {1} ({2})'.format(
            targetip, server.name, fip.fixed_ip_address)

    def __call__(self):
        cloud.add_ip_list(**self.kwargs)

    def __str__(self):
        return self.description


def swapip(cloud, targetname, targetdns):
    targetip = socket.gethostbyname(targetdns)
    servers = cloud.list_servers()
    floatingips = dict((fip.floating_ip_address, fip)
                       for fip in cloud.list_floating_ips())

    target = None
    current = None

    for s in servers:
        if s.name == targetname:
            if target:
                raise Exception(
                    'Multiple instances found {0}'.format(targetname))
            if not s.accessIPv4:
                raise Exception(
                    'No floating IP found for {0}'.format(targetname))
            if s.accessIPv4 == targetip:
                raise Exception('{0} already has floating IP {1}'.format(
                    targetname, targetip))
            target = s
            oldfloatingip = floatingips[s.accessIPv4].floating_ip_address

    if not target:
        raise Exception('Failed to find target server {0}'.format(targetname))

    for s in servers:
        if s.accessIPv4 == targetip:
            current = s
            break

    commands = []
    commands.append(DetachFloatingIP(cloud, floatingips, target))
    if current:
        commands.append(DetachFloatingIP(cloud, floatingips, current))

    commands.append(AttachFloatingIP(cloud, floatingips, target, targetip))
    if current:
        commands.append(AttachFloatingIP(
            cloud, floatingips, current, oldfloatingip))

    return commands


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 2:
        raise ValueError('Required parameters: server-name target-ip-or-dns')
    cloud = shade.openstack_cloud()
    commands = swapip(cloud, args[0], args[1])
    for c in commands:
        print(c)
    r = input('Enter "yes" to continue with these changes\n'
              '  (have you snapshotted the instances and volumes?): ')
    if r == 'yes':
        for c in commands:
            print(c)
            c()
    else:
        print('Aborting')
        sys.exit(1)
