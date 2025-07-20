# app/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List
import boto3
import os
import uuid
from dotenv import load_dotenv

# Load environment
load_dotenv()

# FastAPI App
app = FastAPI(docs_url="/docs", openapi_url="/openapi.json")

# Security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

# AWS Setup
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))

# Environment Vars
BUCKET_NAME = os.getenv("S3_BUCKET")
TABLE_NAME = os.getenv("DYNAMODB_TABLE")
EXPECTED_API_KEY = os.getenv("API_KEY", "your-secret-api-key")

# Pydantic Models
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    name: str
    email: str
    avatar_url: str

    class Config:
        from_attributes = True

# Dependency: API Key
async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# GET /users
@app.get("/users", response_model=List[UserResponse])
def get_users(api_key: str = Depends(get_api_key)):
    try:
        table = dynamodb.Table(TABLE_NAME)
        return table.scan().get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST /user
@app.post("/user", response_model=UserResponse)
def create_user(
    api_key: str = Depends(get_api_key),
    name: str = Form(...),
    email: str = Form(...),
    avatar: UploadFile = File(...),
):
    try:
        # Validate file type
        if avatar.content_type not in ["image/jpeg", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Only JPG images are allowed")

        # Sanitize email
        safe_email = email.strip().replace(" ", "_").replace('"', "")

        # Get file extension
        file_extension = os.path.splitext(avatar.filename)[1]
        if file_extension.lower() not in [".jpg", ".jpeg"]:
            raise HTTPException(status_code=400, detail="Only .jpg or .jpeg files allowed")

        # Generate unique file name
        file_key = f"avatars/{safe_email}/{uuid.uuid4()}{file_extension}"

        # Upload to S3
        s3.upload_fileobj(avatar.file, BUCKET_NAME, file_key)

        # Save to DynamoDB
        avatar_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_key}"
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(
            Item={
                "name": name,
                "email": email,
                "avatar_url": avatar_url
            }
        )

        return {
            "name": name,
            "email": email,
            "avatar_url": avatar_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))