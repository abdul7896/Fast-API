"""
Prima API - User Management Service with Avatar Upload
"""

# Standard Library Imports
import os
import uuid
import re
import logging
from typing import List

# Third-Party Imports
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .utils.middleware import TimingMiddleware
import boto3
from dotenv import load_dotenv
from .metrics import router as metrics_router
from .routes.users import router as users_router
from .config.settings import settings
from .utils.aws import aws_manager
from .security import get_api_key

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application with custom documentation endpoints
app = FastAPI(
    title="Prima API",
    description="User management service with avatar upload capabilities",
    docs_url="/docs",
    openapi_url="/openapi.json",
    version="1.0.0",
    # Set additional security-related configurations
    root_path=""  # Can be set via environment for reverse proxy scenarios
)

# Add security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware to prevent host header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts.split(",")
)

# Timing middleware for performance monitoring
app.add_middleware(TimingMiddleware)

# Include metrics router
app.include_router(metrics_router)
# Include users router
app.include_router(users_router)




# Blocked email domains for security
BLOCKED_DOMAINS = {
    'tempmail.com',
    'mailinator.com',
    'throwawaymail.com',
    'fakeinbox.com'
}

# DATA MODELS





# HEALTH CHECK ENDPOINTS

@app.get("/health", status_code=status.HTTP_200_OK, include_in_schema=False)
async def health_check():
    """
    Kubernetes liveness probe endpoint
    
    Returns:
        JSON: Application health status
    """
    logger.info("Health check endpoint called")
    return JSONResponse(content={"status": "healthy"})



@app.get("/ready", status_code=status.HTTP_200_OK, include_in_schema=False)
async def readiness_check():
    """Kubernetes readiness probe endpoint that checks service dependencies"""
    logger.info("Readiness check endpoint called")
    try:
        region = settings.aws_region
        if not region:
            logger.error("AWS_REGION is not configured")
            raise ValueError("AWS_REGION is not configured")

        # Configure boto3 with shorter timeouts specifically for health checks
        config = Config(
            connect_timeout=3,  # Shorter timeout for health checks
            read_timeout=3,
            retries={'max_attempts': 1}
        )

        # Check DynamoDB connectivity
        logger.debug("Checking DynamoDB connectivity")
        dynamodb = boto3.resource("dynamodb", region_name=region, config=config)
        table_name = settings.dynamodb_table
        try:
            dynamodb.meta.client.describe_table(TableName=table_name)
            logger.debug(f"DynamoDB table {table_name} is accessible")
        except Exception as e:
            logger.error(f"DynamoDB health check failed: {str(e)}")
            raise ValueError(f"DynamoDB health check failed: {str(e)}")

        # Check S3 connectivity
        logger.debug("Checking S3 connectivity")
        s3 = boto3.client("s3", region_name=region, config=config)
        bucket_name = settings.s3_bucket
        if not bucket_name:
            logger.error("S3_BUCKET is not configured")
            raise ValueError("S3_BUCKET is not configured")
        
        try:
            s3.head_bucket(Bucket=bucket_name)
            logger.debug(f"S3 bucket {bucket_name} is accessible")
        except Exception as e:
            logger.error(f"S3 health check failed: {str(e)}")
            raise ValueError(f"S3 health check failed: {str(e)}")

        logger.info("Readiness check completed successfully")
        return JSONResponse(
            content={"status": "ready", "dependencies": {"dynamodb": "ok", "s3": "ok"}}
        )

    except ValueError as e:
        # Log the actual error for debugging
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service dependencies unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in readiness check: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unexpected error during health check"
        )


