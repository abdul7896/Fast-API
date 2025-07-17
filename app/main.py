from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# ===== Configuration from environment variables =====
import os

DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "users")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "default-bucket")

# ===== Pydantic Models =====
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr


class UserResponse(BaseModel):
    name: str
    email: str
    avatar_url: str


# ===== AWS Clients =====
import boto3
from botocore.exceptions import ClientError

def get_s3_client():
    return boto3.client("s3", region_name="us-east-1")


def get_dynamodb_resource():
    return boto3.resource("dynamodb", region_name="us-east-1")


# ===== Core Functions =====
def get_presigned_url(email: str):
    s3 = get_s3_client()
    try:
        return s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": f"avatars/{email}.jpg"},
            ExpiresIn=3600,
        )
    except ClientError as e:
        raise Exception(f"S3 error: {e}")


def save_user_to_dynamo(name: str, email: str, avatar_url: str):
    table = get_dynamodb_resource().Table(DYNAMODB_TABLE_NAME)
    try:
        table.put_item(Item={"email": email, "name": name, "avatar_url": avatar_url})
    except ClientError:
        raise Exception("DynamoDB error: Unable to put item")


def get_all_users():
    table = get_dynamodb_resource().Table(DYNAMODB_TABLE_NAME)
    try:
        return table.scan().get("Items", [])
    except ClientError:
        raise Exception("DynamoDB scan error")

# ===== API Routes =====
@app.post("/user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    try:
        url = get_presigned_url(user.email)
        save_user_to_dynamo(user.name, user.email, url)
        return {"name": user.name, "email": user.email, "avatar_url": url}
    except ClientError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error saving user")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/users")
async def get_users():
    try:
        return {"users": get_all_users()}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch users")