# app/models/models.py
from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    name: str
    email: str
    avatar_url: str

    class Config:
        from_attributes = True  # if using Pydantic v2+