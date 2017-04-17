#!//usr/bin/env bash

set -e
set -u

HOST=$(su omero -lc "/opt/omero/server/OMERO.server/bin/omero config get omero.db.host")
PASS=$(su omero -lc "/opt/omero/server/OMERO.server/bin/omero config get omero.db.pass")
DATE=$(date +"%Y-%m-%d")
test -e $DATE && {
  echo $DATE already exists
  exit 1
}
time pg_dump -h $HOST -U omero idr -j 8 -Fd -f $DATE \
    --exclude-table-data password \
    --exclude-table-data eventlog
chmod -R a+rX $DATE
rm -f latest
ln -s $DATE latest
