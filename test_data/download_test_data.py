#!/usr/bin/env python
import boto3
import botocore

BUCKET_NAME = 'marburg' # replace with your bucket name
KEYS = [ '0040_20190515_222433_ASVBEN.kmall',
        '0003_20191011_0206_sentry_engineering.kmall' ]

s3 = boto3.resource('s3', endpoint_url = 'https://s3.us-west-1.wasabisys.com' )

for key in KEYS:
    try:
        s3key = "kmall_test_data/" + key
        s3.Bucket(BUCKET_NAME).download_file( s3key, key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
