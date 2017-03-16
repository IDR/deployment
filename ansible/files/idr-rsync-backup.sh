The directories contained in this directory are
dumps of the IDR database produced using:

 $ pg_dump -Fd -j 8 -f ./$DATE ...

which allows restoring the database in parallel:

 $ pg_restore -Fd -j 8 -d idr ./$DATE
[centos@demo32-omero omero-sql]$ cat backup.sh
#!//usr/bin/env bash

set -e
set -u

HOST=$(omero config get omero.db.host)
DATE=$(date +"%Y-%m-%d")
test -e $DATE && {
  echo $DATE already exists
  exit 1
}
sudo time pg_dump -h $HOST -U omero idr -j 8 -Fd -f $DATE \
    --exclude-table-data password \
    --exclude-table-data eventlog
sudo chmod -R a+rX $DATE
rm latest
ln -s $DATE latest
