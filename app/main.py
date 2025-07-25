"""
Prima API - User Management Service with Avatar Upload
"""

# Standard Library Imports
import os
import uuid
import re
from typing import List

# Third-Party Imports
from pydantic import BaseModel, EmailStr, validator
from fastapi import (
    FastAPI,
    File,
    Form,
    UploadFile,
    HTTPException,
    Depends,
    status
)
from botocore.config import Config
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
import boto3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application with custom documentation endpoints
app = FastAPI(
    title="Prima API",
    description="User management service with avatar upload capabilities",
    docs_url="/docs",
    openapi_url="/openapi.json",
    version="1.0.0"
)


# SECURITY CONFIGURATION


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

class UserForm(BaseModel):
    """Form data model for user creation with validation"""
    name: str
    email: EmailStr

    @validator('name')
    def validate_name(cls, value):
        """Ensure name contains only letters, spaces, and hyphens"""
        if not re.match(r'^[a-zA-Z\s-]+$', value):
            raise ValueError('Name can only contain letters and spaces')
        return value.strip()

    @validator('email')
    def validate_email_domain(cls, value):
        """Block disposable email domains and validate email structure"""
        domain = value.split('@')[-1].lower()
        if domain in BLOCKED_DOMAINS:
            raise ValueError('Disposable email domains are not allowed')
        if '..' in value:
            raise ValueError('Invalid email format')
        return value.lower().strip()

    @classmethod
    def as_form(cls, name: str = Form(...), email: str = Form(...)):
        """Special classmethod to handle form data parsing"""
        return cls(name=name, email=email)

class UserResponse(BaseModel):
    """Response model for user data output"""
    name: str
    email: EmailStr
    avatar_url: str

    class Config:
        """Enable ORM mode for compatibility with database models"""
        from_attributes = True

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
    try:
        region = os.getenv("AWS_REGION")
        if not region:
            raise ValueError("AWS_REGION is not set")

        config = Config(connect_timeout=2, read_timeout=2)

        # Check DynamoDB
        dynamodb = boto3.resource("dynamodb", region_name=region, config=config)
        table_name = os.getenv("DYNAMODB_TABLE", "users")
        dynamodb.meta.client.describe_table(TableName=table_name)

        # Check S3
        s3 = boto3.client("s3", region_name=region, config=config)
        s3.head_bucket(Bucket=os.getenv("S3_BUCKET"))

        return {"status": "ready"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service dependencies unavailable: {str(e)}"
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
def create_user(
    api_key: str = Depends(get_api_key),
    form_data: UserForm = Depends(UserForm.as_form),
    avatar: UploadFile = File(...),
):
    """
    Create new user with avatar upload
    
    Args:
        form_data: Validated user information
        avatar: JPEG image file (100KB max)
    
    Returns:
        UserResponse: Created user data with avatar URL
    """
    try:
        # Validate uploaded file
        if avatar.content_type not in ["image/jpeg", "image/jpg"]:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Only JPEG images are accepted"
            )
        
        # Process and upload avatar
        safe_email = form_data.email.replace(" ", "_").replace('"', "")
        file_key = f"avatars/{safe_email}/{uuid.uuid4()}.jpg"
        
        s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
        s3.upload_fileobj(
            avatar.file,
            os.getenv("S3_BUCKET"),
            file_key,
            ExtraArgs={"ContentType": "image/jpeg"}
        )
        
        avatar_url = f"https://{os.getenv('S3_BUCKET')}.s3.amazonaws.com/{file_key}"

        # Store user data
        dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
        table = dynamodb.Table(os.getenv("DYNAMODB_TABLE"))
        table.put_item(Item={
            "name": form_data.name,
            "email": form_data.email,
            "avatar_url": avatar_url
        })

        return UserResponse(**{
            "name": form_data.name,
            "email": form_data.email,
            "avatar_url": avatar_url
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process user creation"
        )