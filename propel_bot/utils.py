import json

import boto3
import botocore
from botocore.exceptions import ClientError
from settings import S3_BUCKET_NAME


def _get_s3_file_object(file_name):
    s3 = boto3.resource(
        "s3",
        config=botocore.config.Config(connect_timeout=5, read_timeout=1)
    )
    return s3.Object(S3_BUCKET_NAME, file_name)


def load_s3_data(file_name):
    s3_file_object = _get_s3_file_object(file_name)
    try:
        return json.loads(s3_file_object.get()["Body"].read())
    except ClientError:
        return {}
    return


def save_s3_data(file_name, data):
    s3_file_object = _get_s3_file_object(file_name)
    s3_file_object.put(Body=json.dumps(data))
