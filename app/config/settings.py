"""
Application settings and configuration management
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings using Pydantic Settings"""
    
    # API Settings
    app_name: str = "Prima API"
    app_version: str = "1.0.0"
    app_description: str = "User management service with avatar upload capabilities"
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development").lower()
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API Authentication
    api_key: Optional[str] = os.getenv("API_KEY")
    
    # AWS Configuration
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    s3_bucket: Optional[str] = os.getenv("S3_BUCKET")
    dynamodb_table: str = os.getenv("DYNAMODB_TABLE", "users")
    
    # CORS Configuration
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "http://localhost,http://localhost:3000,http://127.0.0.1,http://127.0.0.1:3000")
    allowed_hosts: str = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,[::1],prima-api")
    
    # File Upload Settings
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "102400"))  # 100KB in bytes
    allowed_file_types: str = os.getenv("ALLOWED_FILE_TYPES", "image/jpeg,image/jpg")
    
    # AWS Client Configuration
    aws_connect_timeout: int = int(os.getenv("AWS_CONNECT_TIMEOUT", "3"))
    aws_read_timeout: int = int(os.getenv("AWS_READ_TIMEOUT", "3"))
    aws_max_retries: int = int(os.getenv("AWS_MAX_RETRIES", "1"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


# Create a global settings instance
settings = get_settings()