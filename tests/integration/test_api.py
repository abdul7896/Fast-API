# tests/integration/test_api.py

import os

import boto3
import pytest
from botocore.exceptions import ClientError
from fastapi.testclient import TestClient
from moto import mock_aws

from app.main import app

# Set environment variables before importing app
os.environ["DYNAMODB_TABLE_NAME"] = "users"
os.environ["S3_BUCKET_NAME"] = "default-bucket"

client = TestClient(app)


@pytest.fixture(scope="function")
def aws_mocks():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="users",
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.meta.client.get_waiter("table_exists").wait(TableName="users")

        boto3.client("s3", region_name="us-east-1").create_bucket(
            Bucket="default-bucket"
        )
        yield


def add_user(email, name):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table("users")
    table.put_item(Item={"email": email, "name": name})


def test_get_users_success(aws_mocks):
    add_user("user@example.com", "Test User")
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json()[0]["email"] == "user@example.com"


def test_get_users_dynamodb_error(mocker, aws_mocks):
    mock_table = mocker.patch(
        "app.main.get_dynamodb_resource"
    ).return_value.Table.return_value
    mock_table.scan.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "Service Unavailable"}}, "Scan"
    )
    response = client.get("/users")
    assert response.status_code == 500
    assert "Failed to fetch users" in response.text


def test_create_user_success(aws_mocks):
    test_user = {"email": "new@example.com", "name": "New User"}
    response = client.post("/user", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert "avatar_url" in data


# def test_create_user_dynamodb_error(mocker, aws_mocks):
#     mock_table = mocker.patch(
#         "app.main.get_dynamodb_resource"
#     ).return_value.Table.return_value
#     mock_table.put_item.side_effect = ClientError(
#         {"Error": {"Code": "500", "Message": "PutItem failed"}}, "PutItem"
#     )

#     response = client.post(
#         "/user", json={"email": "fail@example.com", "name": "Fail User"}
#     )

#     assert response.status_code == 500
#     assert response.json()["detail"] == "DynamoDB error: Unable to put item"
