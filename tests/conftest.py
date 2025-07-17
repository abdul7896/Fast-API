import pytest
from moto import mock_aws
import boto3
import os

@pytest.fixture(scope="module")  # Changed to module scope for better performance
def aws_mocks():
    # Ensure clean environment
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    
    with mock_aws():
        # Setup DynamoDB
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="users",
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.meta.client.get_waiter("table_exists").wait(TableName="users")

        # Setup S3
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="prima-tech-user-avatars")

        yield

        # Cleanup (optional but recommended)
        table.delete()
        s3.delete_bucket(Bucket="prima-tech-user-avatars")

@pytest.fixture(autouse=True)
def aws_environment(aws_mocks):
    """Ensure all tests use mocked AWS"""
    # Set environment variables for all tests
    os.environ["DYNAMODB_TABLE_NAME"] = "users"
    os.environ["S3_BUCKET_NAME"] = "prima-tech-user-avatars"
    yield