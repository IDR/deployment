#!/usr/bin/env bash
# Snapshot IDR OpenStack volumes and instances

# Attempt to continue on error
#set -e
set -u

if [ $# -ne 1 ]; then
    echo "USAGE: $(basename "$0") vm_prefix"
    exit 1
fi

vm_prefix="$1"
today=$(date +%Y%m%d)
vm_errors=0
vol_errors=0

for vm in \
        database \
        omero \
        proxy \
        a-dockermanager \
        management \
        ; do
    server="$vm_prefix-$vm"
    echo "Snapshotting server $server"
    openstack server image create --name "$server-$today" "$server" -f yaml
    [ $? -eq 0 ] || let vm_errors++
    echo
done

for vol in \
        database-db \
        omero-data \
        proxy-nginxcache \
        a-dockermanager-data \
        ; do
    volume="$vm_prefix-$vol"
    echo "Snapshotting volume $volume"
    openstack snapshot create --force --name "$volume-$today" "$volume" -f yaml
    [ $? -eq 0 ] || let vol_errors++
    echo
done

let errors=($vm_errors + $vol_errors)
if [ $vm_errors -ne 0 ]; then
    echo "ERROR: $vm_errors server snapshots failed"
fi
if [ $vol_errors -ne 0 ]; then
    echo "ERROR: $vol_errors volume snapshots failed"
fi
exit $errors
