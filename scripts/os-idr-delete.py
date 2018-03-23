#!/usr/bin/env python
# Delete resources in an idr-environment

import argparse
from builtins import input
import shade
import sys


def is_in_idrenv(idrenv, obj):
    return (obj.name.startswith('%s-' % idrenv) or obj.name == idrenv)


class DeleteServers(object):
    def __init__(self, cloud, idrenv):
        self.cloud = cloud
        self.servers = [s for s in cloud.list_servers()
                        if is_in_idrenv(idrenv, s)]

        self.description = (
            ['Deleting Servers'] +
            ['  server {0} ({1})'.format(s.name, s.id)
             for s in self.servers]
        )

    def __call__(self):
        for s in self.servers:
            self.cloud.delete_server(s.id, wait=True)

    def __str__(self):
        return '\n'.join(self.description)


class DeleteVolumes(object):
    def __init__(self, cloud, idrenv):
        self.cloud = cloud
        self.volumes = [v for v in cloud.list_volumes()
                        if is_in_idrenv(idrenv, v)]
        volume_ids = set(v.id for v in self.volumes)
        self.volume_snapshots = [s for s in cloud.list_volume_snapshots()
                                 if s.volume_id in volume_ids]

        self.description = (
            ['Deleting Volumes'] +
            ['  volume-snapshot {0} ({1})'.format(s.name, s.id)
             for s in self.volume_snapshots] +
            ['  volume {0} ({1})'.format(v.name, v.id)
             for v in self.volumes]
        )

    def __call__(self):
        for s in self.volume_snapshots:
            cloud.delete_volume_snapshot(s.id, wait=True)
        for v in self.volumes:
            self.cloud.delete_volume(v.id, wait=True)

    def __str__(self):
        return '\n'.join(self.description)


class DeleteNetworks(object):
    def __init__(self, cloud, idrenv):
        self.cloud = cloud
        self.routers = [r for r in cloud.list_routers()
                        if is_in_idrenv(idrenv, r)]
        self.networks = [n for n in cloud.list_networks()
                         if is_in_idrenv(idrenv, n)]
        self.subnet_ids = []
        for n in self.networks:
            self.subnet_ids.extend(n.subnets)

        self.ports = {}
        self.router_map = dict((r.id, r) for r in self.routers)
        for n in self.networks:
            for p in cloud.list_ports({
                'device_owner': 'network:router_interface',
                'network_id': n.id
            }):
                if p.device_id in self.router_map:
                    try:
                        self.ports[p.device_id].add(p.id)
                    except KeyError:
                        self.ports[p.device_id] = set([p.id])

        # Fetch subnet metadata for display
        subnet_dict = dict((s.id, s) for s in cloud.list_subnets())

        self.description = (
            ['Deleting Networks'] +
            ['  ports {0}'.format(','.join(self.ports[router_id]))
             for router_id in self.ports] +
            ['  router {0} ({1})'.format(r.name, r.id)
             for r in self.routers] +
            ['  subnet {0} ({1})'.format(subnet_dict[s].name, s)
             for s in self.subnet_ids] +
            ['  network {0} ({1})'.format(n.name, n.id)
             for n in self.networks]
        )

    def __call__(self):
        for (router_id, port_ids) in self.ports.items():
            for p in port_ids:
                self.cloud.remove_router_interface(
                    self.router_map[router_id], port_id=p)
        for r in self.routers:
            self.cloud.delete_router(r.id)
        for s in self.subnet_ids:
            self.cloud.delete_subnet(s)
        for n in self.networks:
            self.cloud.delete_network(n.id)

    def __str__(self):
        return '\n'.join(self.description)


class DeleteSecurityGroups(object):
    def __init__(self, cloud, idrenv):
        self.cloud = cloud
        self.security_groups = [g for g in cloud.list_security_groups()
                                if is_in_idrenv(idrenv, g)]

        self.description = (
            ['Deleting Security-Groups'] +
            ['  security-group {0} ({1})'.format(g.name, g.id)
             for g in self.security_groups]
        )

    def __call__(self):
        for g in self.security_groups:
            self.cloud.delete_security_group(g.id)

    def __str__(self):
        return '\n'.join(self.description)


def delete(cloud, idrenv, resource_types):
    commands = []
    delete_all = 'all' in resource_types

    if delete_all or 'server' in resource_types:
        commands.append(DeleteServers(cloud, idrenv))
    if delete_all or 'volume' in resource_types:
        commands.append(DeleteVolumes(cloud, idrenv))
    if delete_all or 'network' in resource_types:
        commands.append(DeleteNetworks(cloud, idrenv))
    if delete_all or 'secgroup' in resource_types:
        commands.append(DeleteSecurityGroups(cloud, idrenv))

    return commands


def parse_args(args):
    def idrenv_validate(s):
        if len(s) < 1:
            raise argparse.ArgumentTypeError('Invalid idrenv')
        return s

    resource_types = (
        'server',
        'volume',
        'network',
        'secgroup',
        'all',
    )
    p = argparse.ArgumentParser(description='Delete OpenStack IDR resources')
    p.add_argument('idrenv', help='IDR Environment', type=idrenv_validate)
    p.add_argument(
        '--type', '-t', action='append', choices=resource_types,
        help='OpenStack resource type(s), use "all" to delete all')
    args = p.parse_args(args)
    if not args.type:
        raise argparse.ArgumentTypeError('Invalid resource type')
    return args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    if not args.idrenv.startswith('test'):
        p = input('This is not a test environment.\n'
                  'Enter the environment name to confirm deletion: ')
        if p != args.idrenv:
            print('Environment does not match, aborting')
            sys.exit(2)

    cloud = shade.openstack_cloud()
    commands = delete(cloud, args.idrenv, args.type)
    for c in commands:
        print(c)

    r = input('Enter "yes" to delete these resources: ')
    if r == 'yes':
        for c in commands:
            print(c.description[0])
            c()
    else:
        print('Aborting')
        sys.exit(1)
