"""
API Gateway - Entry point for all API requests
"""

# Standard Library Imports
import os

# Third-Party Imports
from pydantic import BaseModel
from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    status
)
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application with custom documentation endpoints
app = FastAPI(
    title="API Gateway",
    description="Entry point for all API requests",
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

# Service URLs (loaded from environment)
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
AVATAR_SERVICE_URL = os.getenv("AVATAR_SERVICE_URL", "http://avatar-service:8000")

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
        # Check user service connectivity
        async with httpx.AsyncClient() as client:
            user_response = await client.get(f"{USER_SERVICE_URL}/health")
            if user_response.status_code != 200:
                raise ValueError("User service health check failed")
        
        # Check avatar service connectivity
        async with httpx.AsyncClient() as client:
            avatar_response = await client.get(f"{AVATAR_SERVICE_URL}/health")
            if avatar_response.status_code != 200:
                raise ValueError("Avatar service health check failed")

        return JSONResponse(
            content={"status": "ready", "dependencies": {"user-service": "ok", "avatar-service": "ok"}}
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

@app.get("/users")
async def get_users(api_key: str = Depends(get_api_key)):
    """
    Retrieve all registered users
    
    Returns:
        List of all users in the system
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{USER_SERVICE_URL}/users",
                headers={"X-API-Key": api_key}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Failed to retrieve users"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process user retrieval"
        )

@app.post("/user")
async def create_user(user_data: dict, api_key: str = Depends(get_api_key)):
    """
    Create new user
    
    Args:
        user_data: User information
    
    Returns:
        Created user data
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{USER_SERVICE_URL}/user",
                json=user_data,
                headers={"X-API-Key": api_key}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Failed to create user"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process user creation"
        )

@app.post("/avatar")
async def upload_avatar(avatar_data: dict, api_key: str = Depends(get_api_key)):
    """
    Upload avatar for a user
    
    Args:
        avatar_data: Avatar upload information
    
    Returns:
        Avatar URL
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AVATAR_SERVICE_URL}/avatar",
                json=avatar_data,
                headers={"X-API-Key": api_key}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Failed to upload avatar"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process avatar upload"
        )