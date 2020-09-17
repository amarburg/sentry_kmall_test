#!/usr/bin/env python
import boto3
import botocore
from botocore import UNSIGNED
from botocore.client import Config

import os

BUCKET_NAME = 'kmall-py-test-data' # replace with your bucket name

## UNSIGNED lets us download anonymously
s3 = boto3.resource('s3', endpoint_url = 'https://s3.us-west-1.wasabisys.com',
                     config=Config(signature_version=UNSIGNED) )
bucket = s3.Bucket(BUCKET_NAME)

## Download all files from S3 bucket
for file in bucket.objects.all():

    if os.path.isfile( file.key ):
        continue

    try:
        s3.Bucket(BUCKET_NAME).download_file( file.key, file.key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
