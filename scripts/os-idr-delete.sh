#!/bin/sh
# Run this script to get a list of commands to delete all potential resources
# If you want to run it directly (not recommended):
#     bash <(./os-idr-delete.sh IDR_ENVIRONMENT)

set -eu

idr_environment=$1
for server in proxy omero database management; do
    echo openstack server delete ${idr_environment}-${server}
done
echo

for server in omero database dockermanager dockerworker; do
    echo openstack server delete ${idr_environment}-a-${server}
done
echo

for volume in proxy-nginxcache omero-data database-db; do
    echo openstack volume delete ${idr_environment}-${volume}
done
echo

for volume in omero-data database-db dockermanager-data; do
    echo openstack volume delete ${idr_environment}-a-${volume}
done
echo

for router in ${idr_environment}-router ${idr_environment}-a-router; do
    echo "for port in \$(openstack port list --router ${router} -f value | cut -d\  -f1); do"
    echo "    openstack router remove port ${router} \$port"
    echo "done"
    echo
done
echo

for router in ${idr_environment}-router ${idr_environment}-a-router; do
    echo openstack router delete ${router}
done
echo

for network in ${idr_environment} ${idr_environment}-a; do
    echo openstack network delete ${network}
done
echo

echo openstack server list -f yaml
echo openstack volume list -f yaml
echo openstack network list -f yaml
echo openstack router list -f yaml
