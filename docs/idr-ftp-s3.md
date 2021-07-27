# IDR upload server

The IDR upload VM includes FTP and S3 services for handling data submissions.


## IDR FTP server

The IDR FTP server runs in Docker, and only allows [passive anonymous write-only uploads](https://github.com/ome/ansible-role-anonymous-ftp/).
The server listens on port `21`, with data connections on ports `32022-32222`.
Incoming uploads will appear on the server under `/data/idrftp-incoming/`.


## IDR S3 upload server

The IDR S3 submission server is co-located with the IDR FTP server.
The IDR S3 server is actually a proxy through to the backend S3 filestore provided by EBI, and uses Minio's support for proxying S3 whilst overlaying its own authentication.

Details of how this works are in the [`ome.minio-s3-gateway` Ansible role](https://github.com/ome/ansible-role-minio-s3-gateway).

Users are created and removed using the `/usr/bin/minio-user.sh` script.
For example, to add a new user `user-test`:

    sudo minio-user.sh add user-test

The S3 access and secret key will be printed to stdout, and can be passed to the submitter who will be able to write and read to `https://idr-ftp.openmicroscopy.org/idr-upload/user-test/` using an S3 client.

To remove a user run:

    sudo minio-user.sh remove user-test

This only deletes the user credentials, it does not delete any data.

Run the script without arguments for full help.
