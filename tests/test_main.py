"""
Tests for Prima API
"""
import os
import pytest
from fastapi.testclient import TestClient
from moto import mock_dynamodb, mock_s3
import boto3
from unittest.mock import patch

# Set test environment
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["S3_BUCKET"] = "test-bucket"
os.environ["DYNAMODB_TABLE"] = "test-table"
os.environ["API_KEY"] = "test-api-key"
os.environ["ALLOWED_HOSTS"] = "testserver,localhost,127.0.0.1"

from app.main import app
from app.models import UserForm

client = TestClient(app, base_url="http://testserver")


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
@mock_s3
@mock_dynamodb
def aws_setup(aws_credentials):
    """Set up mock AWS services."""
    # Create S3 bucket
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")
    
    # Create DynamoDB table
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.create_table(
        TableName="test-table",
        KeySchema=[
            {"AttributeName": "email", "KeyType": "HASH"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "email", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST"
    )
    table.wait_until_exists()
    
    yield
    

class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    @mock_dynamodb
    @mock_s3
    def test_readiness_check_success(self, aws_credentials):
        """Test readiness check with mocked AWS services."""
        # Setup mocked AWS services
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="test-table",
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "dependencies" in data


class TestAPIAuthentication:
    """Test API key authentication."""
    
    def test_missing_api_key(self):
        """Test request without API key."""
        response = client.get("/users")
        assert response.status_code == 403  # Forbidden
    
    def test_invalid_api_key(self):
        """Test request with invalid API key."""
        headers = {"X-API-Key": "invalid-key"}
        response = client.get("/users", headers=headers)
        assert response.status_code == 403
        assert response.json()["detail"] == "Invalid API credentials"
    
    @mock_dynamodb
    def test_valid_api_key(self, aws_credentials):
        """Test request with valid API key."""
        # Setup DynamoDB
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="test-table",
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        
        headers = {"X-API-Key": "test-api-key"}
        response = client.get("/users", headers=headers)
        assert response.status_code == 200


class TestUserEndpoints:
    """Test user management endpoints."""
    
    @mock_dynamodb
    def test_get_users_empty(self, aws_credentials):
        """Test getting users when table is empty."""
        # Setup DynamoDB
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="test-table",
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        
        headers = {"X-API-Key": "test-api-key"}
        response = client.get("/users", headers=headers)
        assert response.status_code == 200
        assert response.json() == []
    
    @mock_s3
    @mock_dynamodb
    def test_create_user_success(self, aws_credentials):
        """Test successful user creation."""
        # Setup AWS services
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="test-table",
            KeySchema=[{"AttributeName": "email", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "email", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        
        # Create proper JPEG content with JPEG magic bytes
        test_image_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'  # Minimal JPEG header
        
        headers = {"X-API-Key": "test-api-key"}
        files = {"avatar": ("test.jpg", test_image_content, "image/jpeg")}
        data = {
            "name": "Test User",
            "email": "test@example.com"
        }
        
        response = client.post("/user", headers=headers, files=files, data=data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["name"] == "Test User"
        assert response_data["email"] == "test@example.com"
        assert "avatar_url" in response_data
    
    def test_create_user_invalid_file_type(self):
        """Test user creation with invalid file type."""
        test_content = b"fake_png_content"
        
        headers = {"X-API-Key": "test-api-key"}
        files = {"avatar": ("test.png", test_content, "image/png")}
        data = {
            "name": "Test User",
            "email": "test@example.com"
        }
        
        response = client.post("/user", headers=headers, files=files, data=data)
        assert response.status_code == 400
        assert "Only JPEG images are accepted" in response.json()["detail"]
    
    def test_create_user_invalid_email(self):
        """Test user creation with invalid email."""
        # Create proper JPEG content with JPEG magic bytes
        test_image_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'  # Minimal JPEG header
        
        headers = {"X-API-Key": "test-api-key"}
        files = {"avatar": ("test.jpg", test_image_content, "image/jpeg")}
        data = {
            "name": "Test User",
            "email": "invalid-email"
        }
        
        response = client.post("/user", headers=headers, files=files, data=data)
        assert response.status_code == 422  # Validation error
    
    def test_create_user_blocked_domain(self):
        """Test user creation with blocked email domain."""
        # Create proper JPEG content with JPEG magic bytes
        test_image_content = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00'  # Minimal JPEG header
        
        headers = {"X-API-Key": "test-api-key"}
        files = {"avatar": ("test.jpg", test_image_content, "image/jpeg")}
        data = {
            "name": "Test User",
            "email": "test@tempmail.com"  # Blocked domain
        }
        
        response = client.post("/user", headers=headers, files=files, data=data)
        assert response.status_code == 422  # Validation error


class TestMetrics:
    """Test metrics endpoint."""
    
    def test_metrics_endpoint(self):
        """Test that metrics endpoint is accessible."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "prima_api_requests_total" in response.text
        assert "prima_api_uptime_seconds" in response.text


class TestValidation:
    """Test input validation."""
    
    def test_name_validation_too_short(self):
        """Test name validation with too short name."""
        
        with pytest.raises(ValueError, match="Name must be at least 2 characters long"):
            UserForm(name="A", email="test@example.com")
    
    def test_name_validation_invalid_characters(self):
        """Test name validation with invalid characters."""
        
        with pytest.raises(ValueError, match="Name can only contain letters, spaces, and hyphens"):
            UserForm(name="Test123", email="test@example.com")
    
    def test_email_validation_invalid_format(self):
        """Test email validation with invalid format."""
        
        with pytest.raises(Exception):  # Pydantic raises ValidationError, not ValueError
            UserForm(name="Test User", email="test..user@example.com")


if __name__ == "__main__":
    pytest.main([__file__])
