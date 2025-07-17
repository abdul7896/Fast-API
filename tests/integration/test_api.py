import os
import pytest
from fastapi.testclient import TestClient
from app.main import app, DYNAMODB_TABLE_NAME, get_dynamodb_resource, get_s3_client
from moto import mock_aws

# Set environment variables
os.environ["DYNAMODB_TABLE_NAME"] = "users"
os.environ["S3_BUCKET_NAME"] = "prima-tech-user-avatars"

# TestClient
client = TestClient(app)

@pytest.fixture
def aws_mocks():
    with mock_aws():
        # Setup DynamoDB
        dynamodb = get_dynamodb_resource()
        table = dynamodb.create_table(
            TableName="users",
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.meta.client.get_waiter("table_exists").wait(TableName="users")

        # Setup S3
        s3 = get_s3_client()
        s3.create_bucket(Bucket="prima-tech-user-avatars")

        yield

def add_user(email, name, avatar_url=None):
    table = get_dynamodb_resource().Table(DYNAMODB_TABLE_NAME)
    avatar_url = avatar_url or f"https://default-bucket.s3.amazonaws.com/avatars/{email}.jpg"
    table.put_item(Item={"email": email, "name": name, "avatar_url": avatar_url})

def test_get_users_success(aws_mocks):
    test_email = "user@example.com"
    test_name = "Test User"
    avatar_url = f"https://default-bucket.s3.amazonaws.com/avatars/{test_email}.jpg"

    add_user(test_email, test_name, avatar_url)

    response = client.get("/users")
    assert response.status_code == 200

    data = response.json()
    assert "users" in data
    users = data["users"]
    assert users
    assert users[0]["email"] == test_email
    assert users[0]["name"] == test_name
    assert users[0]["avatar_url"] == avatar_url

def test_get_users_dynamodb_error(mocker, aws_mocks):
    mock_table = mocker.patch("app.main.get_dynamodb_resource").return_value.Table.return_value
    mock_table.scan.side_effect = Exception("DynamoDB scan error")

    response = client.get("/users")
    assert response.status_code == 500
    assert "Failed to fetch users" in response.text

def test_create_user_success(aws_mocks):
    test_user = {"email": "new@example.com", "name": "New User"}
    response = client.post("/user", json=test_user)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user["email"]
    assert "avatar_url" in data