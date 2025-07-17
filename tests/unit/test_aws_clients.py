# tests/unit/test_aws_clients.py

import os
import boto3
import pytest
from moto import mock_aws  # Unified mock for all AWS services

# Load from environment or default values
TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "users")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "default-bucket")

@pytest.fixture(scope="function")
def aws_mocks():
    with mock_aws():  # Mocks all AWS services
        # Setup DynamoDB
        ddb = boto3.resource("dynamodb", region_name="us-east-1")
        ddb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        # Setup S3
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=S3_BUCKET)

        yield

def test_dynamodb_put_and_scan(aws_mocks):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(Item={"email": "a@b.com", "name": "Test"})
    response = table.scan()
    assert response["Items"] == [{"email": "a@b.com", "name": "Test"}]

def test_s3_upload_and_list(aws_mocks):
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.put_object(Bucket=S3_BUCKET, Key="test.png", Body=b"dummy content")

    response = s3.list_objects_v2(Bucket=S3_BUCKET)
    keys = [obj["Key"] for obj in response.get("Contents", [])]
    assert "test.png" in keys

def test_dynamodb_put_and_get_item(aws_mocks):
    dynamodb = boto3.client("dynamodb", region_name="us-east-1")
    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            "email": {"S": "user@example.com"},
            "name": {"S": "Test User"}
        }
    )

    result = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={"email": {"S": "user@example.com"}}
    )
    assert result["Item"]["name"]["S"] == "Test User"