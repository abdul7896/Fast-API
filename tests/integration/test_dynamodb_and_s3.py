# tests/integration/test_dynamodb_and_s3.py

import os
import boto3
import pytest
from moto import mock_aws

S3_BUCKET = os.getenv("S3_BUCKET", "default-bucket")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "users")


@mock_aws
def test_s3_upload_and_list():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=S3_BUCKET)
    s3.put_object(Bucket=S3_BUCKET, Key="test.png", Body=b"dummy content")
    response = s3.list_objects_v2(Bucket=S3_BUCKET)
    keys = [obj["Key"] for obj in response.get("Contents", [])]
    assert "test.png" in keys


@mock_aws
def test_dynamodb_put_and_get_item():
    ddb = boto3.client("dynamodb", region_name="us-east-1")

    # Only create table if it doesn't exist
    existing_tables = ddb.list_tables()["TableNames"]
    if DYNAMODB_TABLE_NAME not in existing_tables:
        ddb.create_table(
            TableName=DYNAMODB_TABLE_NAME,
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )

    # Wait for table to be ready
    waiter = ddb.get_waiter("table_exists")
    waiter.wait(TableName=DYNAMODB_TABLE_NAME)

    # Now perform operations
    ddb.put_item(
        TableName=DYNAMODB_TABLE_NAME,
        Item={"email": {"S": "user@example.com"}, "name": {"S": "Test User"}}
    )
    
    result = ddb.get_item(
        TableName=DYNAMODB_TABLE_NAME,
        Key={"email": {"S": "user@example.com"}}
    )
    
    assert result["Item"]["name"]["S"] == "Test User"