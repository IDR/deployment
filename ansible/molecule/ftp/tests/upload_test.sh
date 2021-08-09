#!/bin/sh
set -eu

cd /
ftp -p -n 127.0.0.1 << EOF
user anonymous allowed@example.org
cd incoming
put upload_test.sh
quit
EOF

# IDR FTP molecule test script
