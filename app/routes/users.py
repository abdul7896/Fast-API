import os

import boto3
from dotenv import load_dotenv
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.models import UserCreate, UserResponse

load_dotenv()

router = APIRouter()


dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION"))
s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))


@router.post("/user", response_model=UserResponse)
async def create_user(user: UserCreate, avatar: UploadFile = File(...)):
    try:
        # Upload to S3
        s3.upload_fileobj(avatar.file, os.getenv("S3_BUCKET"), f"avatars/{user.email}")

        # Save to DynamoDB
        table_name = os.getenv("DYNAMODB_TABLE")
        dynamodb.Table(table_name).put_item(
            Item={
                "name": user.name,
                "email": user.email,
                "avatar_url": f"https://{os.getenv('S3_BUCKET')}.s3.amazonaws.com/avatars/{user.email}",
            }
        )

        return {
            "name": user.name,
            "email": user.email,
            "avatar_url": f"https://{os.getenv('S3_BUCKET')}.s3.amazonaws.com/avatars/{user.email}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
