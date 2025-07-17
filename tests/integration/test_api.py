# tests/integration/test_api.py

import os
import boto3
from fastapi.testclient import TestClient
from app.main import app
from botocore.exceptions import ClientError
import pytest
from moto import mock_aws

# Set environment variables before importing app
os.environ["DYNAMODB_TABLE_NAME"] = "users"
os.environ["S3_BUCKET_NAME"] = "default-bucket"

client = TestClient(app)

@pytest.fixture(scope="function")
def aws_mocks():
    with mock_aws():
        # Setup DynamoDB
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="users",
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        waiter = table.meta.client.get_waiter("table_exists")
        waiter.wait(TableName="users")

        # Setup S3
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="default-bucket")

        yield


def test_get_users_success(aws_mocks):
    # Add user directly via boto3
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table("users")
    table.put_item(Item={"email": "user@example.com", "name": "Test User"})

    response = client.get("/users")
    assert response.status_code == 200
    assert response.json()[0]["email"] == "user@example.com"




def test_get_users_dynamodb_error(mocker, aws_mocks):
    # Mock boto3.resource via get_dynamodb_resource
    mock_dynamo = mocker.patch("app.main.get_dynamodb_resource")
    mock_table = mock_dynamo.return_value.Table.return_value
    mock_table.scan.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "Service Unavailable"}}, "Scan"
    )

    response = client.get("/users")
    assert response.status_code == 500
    assert "Failed to fetch users" in response.text


def test_create_user_success(aws_mocks):
    test_user = {"email": "new@example.com", "name": "New User"}
    response = client.post("/user", json=test_user)

    assert response.status_code == 200  # Or 201 if your API returns that
    data = response.json()
    assert data["email"] == test_user["email"]
    assert "avatar_url" in data


def test_create_user_dynamodb_error(mocker, aws_mocks):
    mock_dynamo = mocker.patch("app.main.get_dynamodb_resource")
    mock_table = mock_dynamo.return_value.Table.return_value
    mock_table.put_item.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "PutItem failed"}}, "PutItem"
    )

    response = client.post("/user", json={"email": "fail@example.com", "name": "Fail User"})
    assert response.status_code == 500
    assert "An error occurred" in response.text  


    