# tests/conftest.py
import os

import boto3
import pytest
from moto import mock_aws
from app.main import app
from fastapi.testclient import TestClient

TABLE = os.getenv("DYNAMODB_TABLE_NAME", "users")
S3_BUCKET = os.getenv("S3_BUCKET", "default-bucket")
client = TestClient(app) 


@pytest.fixture(autouse=True)
def aws_mocks():
    with mock_aws():
        ddb = boto3.resource("dynamodb", region_name="us-east-1")
        ddb.create_table(
            TableName=TABLE,
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=S3_BUCKET)
        yield
