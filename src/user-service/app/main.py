"""
User Service - Manages user data and operations
"""

# Standard Library Imports
import os
import re
from typing import List

# Third-Party Imports
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    status
)
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
import boto3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application with custom documentation endpoints
app = FastAPI(
    title="User Service",
    description="User management service",
    docs_url="/docs",
    openapi_url="/openapi.json",
    version="1.0.0"
)

# API Key Authentication Header
api_key_header = APIKeyHeader(
    name="X-API-Key",
    description="Enter your API key",
    auto_error=True
)

# Expected API Key (loaded from environment)
EXPECTED_API_KEY = os.getenv("API_KEY", "default-secret-key")

# Blocked email domains for security
BLOCKED_DOMAINS = {
    'tempmail.com',
    'mailinator.com',
    'throwawaymail.com',
    'fakeinbox.com'
}

# DATA MODELS

class UserCreate(BaseModel):
    """Request model for user creation with validation"""
    name: str
    email: EmailStr

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Ensure name contains only letters, spaces, and hyphens"""
        if not isinstance(value, str):
            raise ValueError('Name must be a string')
        if not re.match(r'^[a-zA-Z\s-]+$', value):
            raise ValueError('Name can only contain letters, spaces, and hyphens')
        if len(value.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return value.strip()

    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, value: str) -> str:
        """Block disposable email domains and validate email structure"""
        if not isinstance(value, str):
            raise ValueError('Email must be a string')
        domain = value.split('@')[-1].lower()
        if domain in BLOCKED_DOMAINS:
            raise ValueError('Disposable email domains are not allowed')
        if '..' in value:
            raise ValueError('Invalid email format')
        return value.lower().strip()

class UserResponse(BaseModel):
    """Response model for user data output"""
    name: str
    email: EmailStr
    avatar_url: str

    model_config = ConfigDict(from_attributes=True)

# DEPENDENCY FUNCTIONS

async def get_api_key(api_key: str = Depends(api_key_header)):
    """Validate API keys in incoming requests"""
    if api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API credentials"
        )
    return api_key

# HEALTH CHECK ENDPOINTS

@app.get("/health", status_code=status.HTTP_200_OK, include_in_schema=False)
async def health_check():
    """
    Kubernetes liveness probe endpoint
    
    Returns:
        JSON: Application health status
    """
    return JSONResponse(content={"status": "healthy"})

@app.get("/ready", status_code=status.HTTP_200_OK, include_in_schema=False)
async def readiness_check():
    """Kubernetes readiness probe endpoint that checks service dependencies"""
    try:
        region = os.getenv("AWS_REGION")
        if not region:
            raise ValueError("AWS_REGION environment variable is not set")

        # Check DynamoDB connectivity
        dynamodb = boto3.resource("dynamodb", region_name=region)
        table_name = os.getenv("DYNAMODB_TABLE", "users")
        try:
            dynamodb.meta.client.describe_table(TableName=table_name)
        except Exception as e:
            raise ValueError(f"DynamoDB health check failed: {str(e)}")

        return JSONResponse(
            content={"status": "ready", "dependencies": {"dynamodb": "ok"}}
        )

    except ValueError as e:
        # Log the actual error for debugging
        print(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service dependencies unavailable: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error in readiness check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unexpected error during health check"
        )

# BUSINESS LOGIC ENDPOINTS

@app.get("/users", response_model=List[UserResponse])
def get_users(api_key: str = Depends(get_api_key)):
    """
    Retrieve all registered users
    
    Returns:
        List[UserResponse]: List of all users in the system
    """
    try:
        dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
        table = dynamodb.Table(os.getenv("DYNAMODB_TABLE"))
        return table.scan().get("Items", [])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )

@app.post("/user", response_model=UserResponse)
def create_user(user_data: UserCreate, api_key: str = Depends(get_api_key)):
    """
    Create new user
    
    Args:
        user_data: Validated user information
    
    Returns:
        UserResponse: Created user data
    """
    try:
        # Store user data
        dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
        table = dynamodb.Table(os.getenv("DYNAMODB_TABLE"))
        table.put_item(Item={
            "name": user_data.name,
            "email": user_data.email,
            "avatar_url": ""  # Will be updated by avatar service
        })

        return UserResponse(**{
            "name": user_data.name,
            "email": user_data.email,
            "avatar_url": ""
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process user creation"
        )