from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    name: str
    email: EmailStr
    avatar_url: str