from pydantic import BaseModel, EmailStr, HttpUrl

class UserCreate(BaseModel):
    email: EmailStr
    name: str

class UserResponse(BaseModel):
    email: EmailStr
    name: str
    avatar_url: HttpUrl
