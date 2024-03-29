#!/usr/bin/env python

# Copyright (c) 2012, Marco Vito Moscaritolo <marco@agavee.com>
# Copyright (c) 2013, Jesse Keating <jesse.keating@rackspace.com>
# Copyright (c) 2015, Hewlett-Packard Development Company, L.P.
# Copyright (c) 2016, Rackspace Australia
# Copyright (C) 2016, University of Dundee & Open Microscopy Environment
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

# The OpenStack Inventory module uses os-client-config for configuration.
# https://github.com/openstack/os-client-config
# This means it will either:
#  - Respect normal OS_* environment variables like other OpenStack tools
#  - Read values from a clouds.yaml file.
# If you want to configure via clouds.yaml, you can put the file in:
#  - Current directory
#  - ~/.config/openstack/clouds.yaml
#  - /etc/openstack/clouds.yaml
#  - /etc/ansible/openstack.yml
# The clouds.yaml file can contain entries for multiple clouds and multiple
# regions of those clouds. If it does, this inventory module will connect to
# all of them and present them as one contiguous inventory.
#
# See the adjacent openstack.yml file for an example config file
# There are two ansible inventory specific options that can be set in
# the inventory section.
# expand_hostvars controls whether or not the inventory will make extra API
#                 calls to fill out additional information about each server
# use_hostnames changes the behavior from registering every host with its UUID
#               and making a group of its hostname to only doing this if the
#               hostname in question has more than one server
# fail_on_errors causes the inventory to fail and return no hosts if one cloud
#                has failed (for example, bad credentials or being offline).
#                When set to False, the inventory will return hosts from
#                whichever other clouds it can contact. (Default: True)
#
# This dynamic inventory has been modified from the upstream version:
# - It always returns private IPs for servers.
# - If the server metadata contains `ssh_proxy_host` this will be used to
#   automatically find a SSH proxy server and sets a host-var
#   `ansible_ssh_common_args` on the server.
# - If the server metadata contains `network_order` these networks will be
#   searched for a private IP in that order.
#
# Environment variables:
# - OS_CLOUD: Set this to select a cloud
# - OS_PROXY_DISCOVER: Set to '0' to disable auto-configuration of ssh
#   proxy servers in the dynamic inventory.
# - OS_PROXY_SSH_ARGS: Additional SSH arguments to be set in the SSH
#   ProxyCommand. These must be double quoted.

import argparse
import collections
import os
import sys
import time
from packaging.version import Version

try:
    import json
except:
    import simplejson as json

import os_client_config
import shade
import shade.inventory

CONFIG_FILES = ['/etc/ansible/openstack.yaml', '/etc/ansible/openstack.yml']


def get_groups_from_server(server_vars, namegroup=True):
    groups = []

    region = server_vars['region']
    cloud = server_vars['cloud']
    metadata = server_vars.get('metadata', {})

    # Create a group for the cloud
    groups.append(cloud)

    # Create a group on region
    groups.append(region)

    # And one by cloud_region
    groups.append("%s_%s" % (cloud, region))

    # Check if group metadata key in servers' metadata
    if 'group' in metadata:
        groups.append(metadata['group'])

    for extra_group in metadata.get('groups', '').split(','):
        if extra_group:
            groups.append(extra_group.strip())
    # Metadata properties are limited to 255 characters, so add in groups from
    # a second property
    for extra_group in metadata.get('groups2', '').split(','):
        if extra_group:
            groups.append(extra_group.strip())

    groups.append('instance-%s' % server_vars['id'])
    if namegroup:
        groups.append(server_vars['name'])

    for key in ('flavor', 'image'):
        if 'name' in server_vars[key]:
            groups.append('%s-%s' % (key, server_vars[key]['name']))

    for key, value in iter(metadata.items()):
        groups.append('meta-%s_%s' % (key, value))

    az = server_vars.get('az', None)
    if az:
        # Make groups for az, region_az and cloud_region_az
        groups.append(az)
        groups.append('%s_%s' % (region, az))
        groups.append('%s_%s_%s' % (cloud, region, az))
    return groups


def get_host_groups(inventory, refresh=False):
    (cache_file, cache_expiration_time) = get_cache_settings()
    if is_cache_stale(cache_file, cache_expiration_time, refresh=refresh):
        groups = to_json(get_host_groups_from_cloud(inventory))
        open(cache_file, 'w').write(groups)
    else:
        groups = open(cache_file, 'r').read()
    return groups


def append_hostvars(hostvars, groups, key, server, namegroup=False):
    ansible_ssh_host = None

    # shade returns a dict of networks, but the order in which the networks
    # were assigned may be significant.
    # Check for a custom metadata property `network_order` that indicates
    # the order of networks
    try:
        network_order = server.metadata['network_order'].split(',')
        for network in network_order:
            for port in server['addresses'][network]:
                if port['OS-EXT-IPS:type'] == 'fixed':
                    ansible_ssh_host = port['addr']
                    break
            if ansible_ssh_host:
                break
    except KeyError:
        pass

    for network, ports in server['addresses'].items():
        if ansible_ssh_host:
            break
        for port in ports:
            if port['OS-EXT-IPS:type'] == 'fixed':
                ansible_ssh_host = port['addr']
                break
    if not ansible_ssh_host:
        ansible_ssh_host = server['interface_ip']

    hostvars[key] = dict(
        ansible_ssh_host=ansible_ssh_host,
        ansible_host=ansible_ssh_host,
        openstack=server)
    for group in get_groups_from_server(server, namegroup=namegroup):
        groups[group].append(key)


def is_ssh_proxy_host(server, network):
    """
    Checks whether this is an SSH proxy host by checking these criteria:
    - The metadata indicates this is an SSH proxy host
    - The server is attached to the specified network
    - The server has a floating IP on any of its attached networks

    Returns the IP of the proxy server if so
    """
    try:
        if server['openstack']['metadata']['ssh_proxy_host'] != 'proxy':
            return
    except KeyError:
        return

    networks = get_network_names(server)
    for net in networks:
        for port in server['openstack']['addresses'][net]:
            if port['OS-EXT-IPS:type'] == 'floating':
                return port['addr']


def is_ssh_proxy_host_required(server):
    # Checks the metadata to see if a SSH proxy host is required for access.
    # This dynamic inventory intentionally always returns the private IP of
    # a server, so effectively the proxy server must still connect via the
    # external proxy floating IP.
    try:
        proxy = server['openstack']['metadata']['ssh_proxy_host']
        if proxy in ('proxy', 'required'):
            return True
    except KeyError:
        pass
    return False


def get_network_names(server):
    # If the network_order metadata property is set try networks in
    # this order, since if the server hasn't been fully initialised only
    # the first NIC may be active
    # The metadata might be incorrect, so ignore unknown networks
    try:
        network_order = server['openstack']['metadata'][
            'network_order'].split(',')
    except Exception:
        network_order = []
    all_networks = set(server['openstack']['addresses'].keys())
    networks = [n for n in network_order if n in all_networks]
    networks += list(all_networks.difference(network_order))
    return networks


def update_ssh_proxy_host(hostvars):
    # If the server metadata has `ssh_proxy_host=required` then
    # look for a host in the same network which has property
    # `ssh_proxy_host=proxy` and set this as a SSH proxy in
    # ansible_ssh_common_args
    network_hosts = {}
    network_ssh_proxy = {}
    ssh_proxy_fmt = '-o ProxyCommand="ssh %s -W %%h:%%p -q %%r@%s"'
    ssh_proxy_ssh_args = os.getenv('OS_PROXY_SSH_ARGS', '')

    for (h, server) in hostvars.items():
        networks = get_network_names(server)
        for network in networks:
            try:
                network_hosts[network].append(server)
            except KeyError:
                network_hosts[network] = [server]

            # If there are multiple proxies just use the first
            if network not in network_ssh_proxy:
                ssh_ip = is_ssh_proxy_host(server, network)
                if ssh_ip:
                    network_ssh_proxy[network] = ssh_ip

    for (h, server) in hostvars.items():
        if not is_ssh_proxy_host_required(server):
            continue

        networks = get_network_names(server)
        for network in networks:
            if (network in network_ssh_proxy and
                    'ansible_ssh_common_args' not in server):
                server['ansible_ssh_common_args'] = (
                    ssh_proxy_fmt % (
                        ssh_proxy_ssh_args, network_ssh_proxy[network]))


def get_host_groups_from_cloud(inventory):
    groups = collections.defaultdict(list)
    firstpass = collections.defaultdict(list)
    hostvars = {}
    list_args = {}
    if hasattr(inventory, 'extra_config'):
        use_hostnames = inventory.extra_config['use_hostnames']
        list_args['expand'] = inventory.extra_config['expand_hostvars']
        if Version(shade.__version__) >= Version("1.6.0"):
            list_args['fail_on_cloud_config'] = \
                inventory.extra_config['fail_on_errors']
    else:
        use_hostnames = False

    for server in inventory.list_hosts(**list_args):

        if 'interface_ip' not in server:
            continue
        firstpass[server['name']].append(server)
    for name, servers in firstpass.items():
        if len(servers) == 1 and use_hostnames:
            append_hostvars(hostvars, groups, name, servers[0])
        else:
            server_ids = set()
            # Trap for duplicate results
            for server in servers:
                server_ids.add(server['id'])
            if len(server_ids) == 1 and use_hostnames:
                append_hostvars(hostvars, groups, name, servers[0])
            else:
                for server in servers:
                    append_hostvars(
                        hostvars, groups, server['id'], server,
                        namegroup=True)

    auto_proxy = os.getenv('OS_PROXY_DISCOVER')
    # Default to using proxy auto-discovery
    #if auto_proxy and auto_proxy != '0':
    if not auto_proxy or auto_proxy != '0':
        update_ssh_proxy_host(hostvars)
    groups['_meta'] = {'hostvars': hostvars}
    return groups


def is_cache_stale(cache_file, cache_expiration_time, refresh=False):
    ''' Determines if cache file has expired, or if it is still valid '''
    if refresh:
        return True
    if os.path.isfile(cache_file) and os.path.getsize(cache_file) > 0:
        mod_time = os.path.getmtime(cache_file)
        current_time = time.time()
        if (mod_time + cache_expiration_time) > current_time:
            return False
    return True


def get_cache_settings():
    config = os_client_config.config.OpenStackConfig(
        config_files=os_client_config.config.CONFIG_FILES + CONFIG_FILES)
    # For inventory-wide caching
    cache_expiration_time = config.get_cache_expiration_time()
    cache_path = config.get_cache_path()
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    cache_file = os.path.join(cache_path, 'ansible-inventory.cache')
    return (cache_file, cache_expiration_time)


def to_json(in_dict):
    return json.dumps(in_dict, sort_keys=True, indent=2)


def parse_args():
    parser = argparse.ArgumentParser(description='OpenStack Inventory Module')
    parser.add_argument('--refresh', action='store_true',
                        help='Refresh cached information')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Enable debug output')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true',
                       help='List active servers')
    group.add_argument('--host', help='List details about the specific host')

    return parser.parse_args()


def main():
    args = parse_args()
    try:
        config_files = os_client_config.config.CONFIG_FILES + CONFIG_FILES
        shade.simple_logging(debug=args.debug)
        inventory_args = dict(
            refresh=args.refresh,
            config_files=config_files,
            private=True,
        )
        if hasattr(shade.inventory.OpenStackInventory, 'extra_config'):
            inventory_args.update(dict(
                config_key='ansible',
                config_defaults={
                    'use_hostnames': False,
                    'expand_hostvars': True,
                    'fail_on_errors': True,
                }
            ))
        # shade.inventory ignores OS_CLOUD
        # http://git.openstack.org/cgit/openstack-infra/shade/tree/shade/inventory.py?h=1.12.1#n38
        cloud = os.getenv('OS_CLOUD')
        if cloud:
            inventory_args['cloud'] = cloud

        inventory = shade.inventory.OpenStackInventory(**inventory_args)

        if args.list:
            output = get_host_groups(inventory, refresh=args.refresh)
        elif args.host:
            output = to_json(inventory.get_host(args.host))
        print(output)
    except shade.OpenStackCloudException as e:
        sys.stderr.write('%s\n' % e.message)
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
