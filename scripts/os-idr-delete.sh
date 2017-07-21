#!/bin/sh
# Run this script to get a list of commands to delete all potential resources
# If you want to run it directly (not recommended):
#     bash <(./os-idr-delete.sh IDR_ENVIRONMENT)

set -eu

idr_environment=$1

for server in \
    proxy \
    omeroreadonly-1 \
    omeroreadonly-2 \
    omeroreadwrite \
    database \
    dockermanager \
    dockerworker-1 \
    dockerworker-2 \
    management \
    ; do
    echo openstack server delete ${idr_environment}-${server}
done
echo

for volume in \
    proxy-nginxcache \
    omeroreadwrite-data \
    database-db \
    dockermanager-data \
    ; do
    echo openstack volume delete ${idr_environment}-${volume}
done
echo

echo "for port in \$(openstack port list --router ${idr_environment}-router -f value | cut -d\  -f1); do"
echo "    openstack router remove port ${idr_environment}-router \$port"
echo "done"
echo

echo openstack router delete ${idr_environment}-router
echo

echo openstack network delete ${idr_environment}
echo

echo openstack server list -f yaml
echo openstack volume list -f yaml
echo openstack network list -f yaml
echo openstack router list -f yaml
