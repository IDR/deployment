#!/usr/bin/env bash
# Convert a volume snapshot to an image
# Argument: the volume snapshot name or ID

set -e
set -u

SNAPSHOT="$1"
SIZE=$(openstack volume snapshot show "$SNAPSHOT" -f json | jq -r ".size")
TODAY=$(date +%Y%m%d)

# Snapshot -> Volume
DESCRIPTION="Created $TODAY from Snapshot $SNAPSHOT"
if openstack volume show "$SNAPSHOT"; then
    echo "Volume $SNAPSHOT already exists, skipping"
else
    echo "Creating volume $SNAPSHOT ($SIZE GB)"
    time openstack volume create --snapshot "$SNAPSHOT" "$SNAPSHOT" \
        --size "$SIZE" --description "$DESCRIPTION"

    while [ $(openstack volume show "$SNAPSHOT" -f json | jq -r ".status") != "available" ]; do
        echo -n .
        sleep 10
    done
    echo
    echo "Created volume $SNAPSHOT"
fi

# Volume -> Image
DESCRIPTION="Created $TODAY from Volume $SNAPSHOT"
if openstack image show "$SNAPSHOT"; then
    echo "Image $SNAPSHOT already exists, skipping"
else
    echo "Creating image $SNAPSHOT"
    time openstack image create --volume "$SNAPSHOT" "$SNAPSHOT"

    while [ $(openstack image show "$SNAPSHOT" -f json | jq -r ".status") != "active" ]; do
        echo -n .
        sleep 10
    done
    echo
    echo "Created image $SNAPSHOT"
fi

echo "You can download this image by running"
echo openstack image save --file "$SNAPSHOT" "$SNAPSHOT"
