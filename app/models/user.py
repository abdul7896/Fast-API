"""
Shared models for the Prima API
"""
from typing import List
import re
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from fastapi import Form


class UserForm(BaseModel):
    """Form data model for user creation with validation"""
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
        BLOCKED_DOMAINS = {
            'tempmail.com',
            'mailinator.com',
            'throwawaymail.com',
            'fakeinbox.com'
        }
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

    model_config = ConfigDict(from_attributes=True)