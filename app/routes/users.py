"""
User routes module for Prima API
Separated from main.py for better code organization
"""
import os
import uuid
import re
import logging
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
import boto3
from dotenv import load_dotenv
from botocore.config import Config

from fastapi import Depends
from ..config.settings import settings
from ..utils.aws import aws_manager
from ..models import UserForm, UserResponse
from ..security import get_api_key

# Set up logging
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter()

# Blocked email domains for security (duplicated here for self-contained routes module)
BLOCKED_DOMAINS = {
    'tempmail.com',
    'mailinator.com',
    'throwawaymail.com',
    'fakeinbox.com'
}


@router.post("/user", response_model=UserResponse)
async def create_user(
    form_data: UserForm = Depends(UserForm.as_form),
    avatar: UploadFile = File(...),
    api_key: str = Depends(get_api_key)  # Authentication dependency
):
    """
    Create new user with avatar upload (moved from main.py for better modularity)
    
    Args:
        form_data: Validated user information
        avatar: JPEG image file (100KB max)
        api_key: Validated API key for authentication
    
    Returns:
        UserResponse: Created user data with avatar URL
    """
    logger.info(f"Creating new user: {form_data.name} with email: {form_data.email}")
    
    try:
        # Validate uploaded file
        if avatar.content_type not in ["image/jpeg", "image/jpg"]:
            logger.warning(f"Invalid file type uploaded: {avatar.content_type}")
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Only JPEG images are accepted"
            )
        
        # Read file content for thorough validation
        contents = await avatar.read()
        
        # Check file size against settings
        max_size = settings.max_file_size
        if len(contents) > max_size:  # Use configured max file size
            logger.warning(f"File size too large: {len(contents)} bytes, max: {max_size}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size must be less than {max_size} bytes"
            )
        
        # Additional security: verify it's actually a JPEG (magic bytes check)
        if not contents.startswith((b'\xff\xd8\xff\xe0', b'\xff\xd8\xff\xe1', b'\xff\xd8\xff\xe2', 
                                   b'\xff\xd8\xff\xe3', b'\xff\xd8\xff\xe4', b'\xff\xd8\xff\xe5',
                                   b'\xff\xd8\xff\xe6', b'\xff\xd8\xff\xe7', b'\xff\xd8\xff\xe8',
                                   b'\xff\xd8\xff\xe9', b'\xff\xd8\xff\xea', b'\xff\xd8\xff\xeb',
                                   b'\xff\xd8\xff\xec', b'\xff\xd8\xff\xed', b'\xff\xd8\xff\xee',
                                   b'\xff\xd8\xff\xef')):
            logger.warning("File does not have valid JPEG magic bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File does not appear to be a valid JPEG image"
            )
        
        logger.debug("File validation passed, proceeding with upload")
        
        # Reset file pointer to beginning for upload
        avatar.file.seek(0)
        
        # Process and upload avatar
        safe_email = form_data.email.replace(" ", "_").replace('"', "").replace("'", "")
        file_key = f"avatars/{safe_email}/{uuid.uuid4()}.jpg"
        
        logger.debug(f"Uploading avatar to S3 with key: {file_key}")
        s3 = aws_manager.s3_client
        s3.upload_fileobj(
            avatar.file,
            settings.s3_bucket,
            file_key,
            ExtraArgs={"ContentType": "image/jpeg"}
        )
        
        avatar_url = f"https://{settings.s3_bucket}.s3.amazonaws.com/{file_key}"
        logger.info(f"Avatar uploaded successfully: {avatar_url}")

        # Store user data
        logger.debug(f"Storing user data in DynamoDB table: {settings.dynamodb_table}")
        dynamodb = aws_manager.dynamodb_resource
        table = dynamodb.Table(settings.dynamodb_table)
        table.put_item(Item={
            "name": form_data.name,
            "email": form_data.email,
            "avatar_url": avatar_url
        })
        
        logger.info(f"User {form_data.name} ({form_data.email}) created successfully")

        return UserResponse(
            name=form_data.name,
            email=form_data.email,
            avatar_url=avatar_url
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process user creation"
        )


@router.get("/users", response_model=List[UserResponse])
def get_users(api_key: str = Depends(get_api_key)):
    """
    Retrieve all registered users (moved from main.py for better modularity)
    
    Args:
        api_key: Validated API key for authentication
    
    Returns:
        List[UserResponse]: List of all users in the system
    """
    logger.info("Retrieving all users")
    try:
        dynamodb = aws_manager.dynamodb_resource
        table = dynamodb.Table(settings.dynamodb_table)
        response = table.scan()
        items = response.get("Items", [])
        
        logger.info(f"Retrieved {len(items)} users from database")
        
        # Convert DynamoDB items to UserResponse models
        users = []
        for item in items:
            user = UserResponse(
                name=item.get("name", ""),
                email=item.get("email", ""),
                avatar_url=item.get("avatar_url", "")
            )
            users.append(user)
        
        return users
    except Exception as e:
        logger.error(f"Failed to retrieve users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )
