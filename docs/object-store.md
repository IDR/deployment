# IDR object store

IDR makes use of object storage to export images and plates from published
studies into a rich cloud-aware representation following the
[OME-NGFF specification](https://ngff.openmicroscopy.org/latest/).

## Set-up

The Embassy Cloud Version 4 includes an S3 compatible Object Storage backend. To use the object store, it is required to have a local installation of the AWS CLI as well as AWS access and secret keys.

Full instructions are given in https://docs.embassy.ebi.ac.uk/userguide/Embassyv4.html#s3-object-store.


## Public bucket creation

The following examples use `idr0000` as the study name.

First, create a bucket named after a study e.g. `idr0000`

    aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 mb s3://idr0000

To list all available buckets:

    aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 ls


### Policy

There are two ways to make keys in a bucket publicly readable, either via object ACL or via bucket policy. S3 ACLs is a [legacy access control mechanism ](https://aws.amazon.com/blogs/security/iam-policies-and-bucket-policies-and-acls-oh-my-controlling-access-to-s3-resources/) and can to be set
either when copying objects e.g. via `aws s3 cp` by passing the appropriate
ACL e.g. `--acl public-read`. 

To let the world list the keys of a bucket and read all keys, create a
`policy.json` that grants the actions to anyone:

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
            "arn:aws:s3:::idr0066/*",
            "arn:aws:s3:::idr0066"]
        }
      ]
    }

Set the bucket policy using `s3api put-bucket-policy`:

    aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3api put-bucket-policy --bucket idr0000 --policy file://policy.json

Optionally, inspect the bucket policy using `s3api get-bucket-policy`::

    aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3api get-bucket-policy --bucket idr0000 --output text


### CORS

For browser access like vizarr, the CORS headers needs to be configured to
allow GET and HEAD data access. Create a `cors.json` file:

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

Set the bucket CORS configuration using `s3api put-bucket-cors`:

    aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3api put-bucket-cors --bucket idr0066  --cors-configuration file://cors.json

Optionally, inspect the bucketCORS configuration using `s3api put-bucket-cors`:

    aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3api get-bucket-cors --bucket idr0066

## Copy and list objects

To copy objects to the a bucket use `s3 cp` with the `--recursive` flag:

    aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 cp --recursive /data/1.zarr s3://idr0000/1.zarr/

Objects can be inspected using `s3 ls`:

    aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 ls s3://idr0000/
