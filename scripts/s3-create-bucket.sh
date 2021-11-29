#!/usr/bin/env bash
# Create public bucket

set -u

if [ $# -ne 1 ]; then
    echo "USAGE: $(basename "$0") bucket_name [endpoint_url]"
    exit 1
fi

BUCKET_NAME=$1
ENDPOINT_URL=${2:-https://uk1s3.embassy.ebi.ac.uk}
POLICY=$(mktemp)
cat > $POLICY << EOL
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"PublicRead",
      "Effect":"Allow",
      "Principal": "*",
      "Action":[
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:ListBucket"],
      "Resource":[
        "arn:aws:s3:::$BUCKET_NAME/*",
        "arn:aws:s3:::$BUCKET_NAME"]
    }
  ]
}
EOL
cat $POLICY

CORS=$(mktemp)
cat > $CORS << EOL
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedHeaders": ["Authorization"],
      "AllowedMethods": ["GET", "HEAD"],
      "MaxAgeSeconds": 3000
    }
  ]
}
EOL
cat $CORS

aws --endpoint-url $ENDPOINT_URL s3 mb s3://$BUCKET_NAME

aws --endpoint-url $ENDPOINT_URL s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://$POLICY
aws --endpoint-url $ENDPOINT_URL s3api put-bucket-cors --bucket $BUCKET_NAME --cors-configuration file://$CORS
