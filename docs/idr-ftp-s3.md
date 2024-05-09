# IDR upload server

The IDR upload VM includes a FTP service for handling data submissions especially
in the early stage where sample data requires some testing.


## IDR FTP service

The IDR FTP service runs in Docker, and only allows [passive anonymous write-only uploads](https://github.com/ome/ansible-role-anonymous-ftp/).
The server listens on port `21`, with data connections on ports `32022-32222`.
Incoming uploads will appear on the server under `/data/idrftp-incoming/`.
