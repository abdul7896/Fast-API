"""
Security utilities for the Prima API
"""
import os
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from ..config.settings import settings

# API Key Authentication Header
api_key_header = APIKeyHeader(
    name="X-API-Key",
    description="Enter your API key",
    auto_error=True
)

logger = logging.getLogger(__name__)

async def get_api_key(api_key: str = Depends(api_key_header)):
    """Validate API keys in incoming requests"""
    logger.debug(f"Validating API key for request")
    if not settings.api_key:
        logger.error("API_KEY is not configured, access denied for security")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: API_KEY not set"
        )
    
    if api_key != settings.api_key:
        logger.warning(f"Invalid API key provided: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API credentials"
        )
    
    logger.info("API key validation successful")
    return api_key