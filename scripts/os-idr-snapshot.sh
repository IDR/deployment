#!/usr/bin/env bash
# Snapshot IDR OpenStack volumes

# Attempt to continue on error
#set -e
set -u

if [ $# -ne 1 ]; then
    echo "USAGE: $(basename "$0") vm_prefix"
    exit 1
fi

vm_prefix="$1"
today=$(date +%Y%m%d)
vol_errors=0

for vol in \
        database-db \
        omeroreadwrite-data \
        proxy-nginxcache \
        ; do
    volume="$vm_prefix-$vol"
    echo "Snapshotting volume $volume"
    openstack volume snapshot create --force --volume "$volume" "$volume-$today" -f yaml
    [ $? -eq 0 ] || let vol_errors++
    echo
done

if [ $vol_errors -ne 0 ]; then
    echo "ERROR: $vol_errors volume snapshots failed"
    exit $vol_errors
fi
