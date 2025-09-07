"""
Avatar Service - Manages user avatars and image operations
"""

# Standard Library Imports
import os
import uuid

# Third-Party Imports
from pydantic import BaseModel, EmailStr, ConfigDict
from fastapi import (
    FastAPI,
    File,
    UploadFile,
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
    title="Avatar Service",
    description="User avatar management service",
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

# DATA MODELS

class AvatarUploadRequest(BaseModel):
    """Request model for avatar upload"""
    email: EmailStr

class AvatarResponse(BaseModel):
    """Response model for avatar data"""
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

        # Check S3 connectivity
        s3 = boto3.client("s3", region_name=region)
        bucket_name = os.getenv("S3_BUCKET")
        if not bucket_name:
            raise ValueError("S3_BUCKET environment variable is not set")
        
        try:
            s3.head_bucket(Bucket=bucket_name)
        except Exception as e:
            raise ValueError(f"S3 health check failed: {str(e)}")

        return JSONResponse(
            content={"status": "ready", "dependencies": {"s3": "ok"}}
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

@app.post("/avatar", response_model=AvatarResponse)
def upload_avatar(
    avatar_request: AvatarUploadRequest,
    avatar: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    """
    Upload avatar for a user
    
    Args:
        avatar_request: User email for avatar association
        avatar: JPEG image file (100KB max)
    
    Returns:
        AvatarResponse: Avatar URL
    """
    try:
        # Validate uploaded file
        if avatar.content_type not in ["image/jpeg", "image/jpg"]:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Only JPEG images are accepted"
            )
        
        # Process and upload avatar
        safe_email = avatar_request.email.replace(" ", "_").replace('"', "")
        file_key = f"avatars/{safe_email}/{uuid.uuid4()}.jpg"
        
        s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
        s3.upload_fileobj(
            avatar.file,
            os.getenv("S3_BUCKET"),
            file_key,
            ExtraArgs={"ContentType": "image/jpeg"}
        )
        
        avatar_url = f"https://{os.getenv('S3_BUCKET')}.s3.amazonaws.com/{file_key}"

        # Update user data with avatar URL
        dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
        table = dynamodb.Table(os.getenv("DYNAMODB_TABLE"))
        table.update_item(
            Key={"email": avatar_request.email},
            UpdateExpression="SET avatar_url = :avatar_url",
            ExpressionAttributeValues={":avatar_url": avatar_url}
        )

        return AvatarResponse(
            email=avatar_request.email,
            avatar_url=avatar_url
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process avatar upload"
        )