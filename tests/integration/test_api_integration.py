import io
import os
import boto3
from fastapi.testclient import TestClient
from moto import mock_aws
import app.main as main_module

# Create a test client for FastAPI app
client = TestClient(main_module.app)


def setup_aws():
    """
    Setup mocked AWS environment:
    - Create S3 bucket for avatars
    - Create DynamoDB table for users with email as the partition key
    """
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=os.getenv("S3_BUCKET"))

    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName=os.getenv("DYNAMODB_TABLE"),
        KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


@mock_aws
def test_create_user_flow():
    """
    Test creating a user with avatar upload.
    - Setup AWS mocks
    - POST user data and avatar
    - Verify response status and returned data
    """
    setup_aws()

    files = {"avatar": ("avatar.jpg", io.BytesIO(b"data"), "image/jpeg")}
    data = {"name": "John Doe", "email": "john@example.com"}
    headers = {"X-API-Key": os.getenv("API_KEY")}

    response = client.post("/user", headers=headers, data=data, files=files)

    print("Response:", response.status_code, response.text)
    assert response.status_code == 200

    resp = response.json()
    assert resp["email"] == "john@example.com"
    assert resp["name"] == "John Doe"
    assert "avatar_url" in resp


@mock_aws
def test_get_users_flow():
    """
    Test retrieving list of users.
    - Setup AWS mocks
    - Create a user first
    - GET users list
    - Assert the created user exists in the response
    """
    setup_aws()

    client.post(
        "/user",
        headers={"X-API-Key": os.getenv("API_KEY")},
        data={"name": "Alice", "email": "alice@example.com"},
        files={"avatar": ("avatar.jpg", io.BytesIO(b"d"), "image/jpeg")},
    )

    response = client.get("/users", headers={"X-API-Key": os.getenv("API_KEY")})

    assert response.status_code == 200

    users = response.json()
    assert any(u["email"] == "alice@example.com" for u in users)
