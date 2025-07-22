from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    name: str
    email: str
    avatar_url: str

    class Config:
        from_attributes = True  # if using Pydantic v2+
