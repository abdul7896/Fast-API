import os
import uuid
from typing import List

import boto3
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

load_dotenv()
app = FastAPI(docs_url="/docs", openapi_url="/openapi.json")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)
EXPECTED_API_KEY = os.getenv("API_KEY", "your-secret-api-key")


class UserResponse(BaseModel):
    name: str
    email: str
    avatar_url: str

    class Config:
        from_attributes = True


async def get_api_key(api_key: str = Depends(api_key_header)):
    expected = os.getenv("API_KEY", "your-secret-api-key")  # moved here
    if api_key != expected:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key


@app.get("/users", response_model=List[UserResponse])
def get_users(api_key: str = Depends(get_api_key)):
    try:
        dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
        table = dynamodb.Table(os.getenv("DYNAMODB_TABLE"))
        return table.scan().get("Items", [])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/user", response_model=UserResponse)
def create_user(
    api_key: str = Depends(get_api_key),
    name: str = Form(...),
    email: str = Form(...),
    avatar: UploadFile = File(...),
):
    try:
        if avatar.content_type not in ["image/jpeg", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Only JPG images are allowed")

        safe_email = email.strip().replace(" ", "_").replace('"', "")
        file_extension = os.path.splitext(avatar.filename)[1]
        if file_extension.lower() not in [".jpg", ".jpeg"]:
            raise HTTPException(
                status_code=400, detail="Only .jpg or .jpeg files allowed"
            )

        file_key = f"avatars/{safe_email}/{uuid.uuid4()}{file_extension}"
        s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
        s3.upload_fileobj(avatar.file, os.getenv("S3_BUCKET"), file_key)

        avatar_url = f"https://{os.getenv('S3_BUCKET')}.s3.amazonaws.com/{file_key}"
        dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
        table = dynamodb.Table(os.getenv("DYNAMODB_TABLE"))
        table.put_item(Item={"name": name, "email": email, "avatar_url": avatar_url})

        return {"name": name, "email": email, "avatar_url": avatar_url}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[create_user] Unexpected error: {e}", flush=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
