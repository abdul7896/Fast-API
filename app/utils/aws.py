"""
AWS connection management utilities
"""
import boto3
from botocore.config import Config
from functools import lru_cache
from typing import Optional

from ..config.settings import settings


class AWSClientManager:
    """
    Manages AWS service clients with connection pooling and configuration
    """
    
    def __init__(self):
        self._s3_client = None
        self._dynamodb_resource = None
    
    @property
    def s3_client(self):
        """Get S3 client with proper configuration"""
        if self._s3_client is None:
            self._s3_client = boto3.client(
                "s3",
                region_name=settings.aws_region,
                config=Config(
                    connect_timeout=settings.aws_connect_timeout,
                    read_timeout=settings.aws_read_timeout,
                    retries={'max_attempts': settings.aws_max_retries},
                    max_pool_connections=50  # Increase connection pool
                )
            )
        return self._s3_client
    
    @property
    def dynamodb_resource(self):
        """Get DynamoDB resource with proper configuration"""
        if self._dynamodb_resource is None:
            self._dynamodb_resource = boto3.resource(
                "dynamodb",
                region_name=settings.aws_region,
                config=Config(
                    connect_timeout=settings.aws_connect_timeout,
                    read_timeout=settings.aws_read_timeout,
                    retries={'max_attempts': settings.aws_max_retries},
                    max_pool_connections=20  # Connection pool for DynamoDB
                )
            )
        return self._dynamodb_resource


# Create a global instance of the manager
aws_manager = AWSClientManager()


@lru_cache(maxsize=128)
def get_cached_user(email: str) -> Optional[dict]:
    """
    Cache user lookups to improve performance for repeated requests
    This is a basic implementation - in production, consider using Redis
    """
    try:
        table = aws_manager.dynamodb_resource.Table(settings.dynamodb_table)
        response = table.get_item(Key={'email': email})
        return response.get('Item')
    except Exception:
        return None