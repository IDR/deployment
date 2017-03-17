The directories contained in this directory are
dumps of the IDR database produced using:

 $ pg_dump -Fd -j 8 -f ./$DATE ...

which allows restoring the database in parallel:

 $ pg_restore -Fd -j 8 -d idr ./$DATE
