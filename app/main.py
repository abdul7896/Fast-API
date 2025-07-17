import os
import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# ===== Configuration from environment variables =====
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

# # ===== Local Stack Clients  =====

# USE_LOCALSTACK = os.getenv("USE_LOCALSTACK", "false").lower() == "true"
# LOCALSTACK_URL = os.getenv("LOCALSTACK_URL", "http://localhost:4566")  # default LocalStack endpoint

# def get_s3_client():
#     kwargs = {"region_name": "us-east-1"}
#     if USE_LOCALSTACK:
#         kwargs.update({
#             "endpoint_url": LOCALSTACK_URL,
#             "aws_access_key_id": "test",
#             "aws_secret_access_key": "test",
#         })
#     return boto3.client("s3", **kwargs)

# def get_dynamodb_resource():
#     kwargs = {"region_name": "us-east-1"}
#     if USE_LOCALSTACK:
#         kwargs.update({
#             "endpoint_url": LOCALSTACK_URL,
#             "aws_access_key_id": "test",
#             "aws_secret_access_key": "test",
#         })
#     return boto3.resource("dynamodb", **kwargs)

# ===== AWS Clients  =====
def get_s3_client():
    return boto3.client("s3", region_name="us-east-1")


def get_dynamodb_resource():
    return boto3.resource("dynamodb", region_name="us-east-1")


# ===== Core Functions =====
def get_presigned_url(email: str):
    s3 = get_s3_client()
    try:
        url = s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": f"avatars/{email}.jpg"},
            ExpiresIn=3600,
        )
        return url
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
        response = table.scan()
        return response.get("Items", [])
    except ClientError:
        raise Exception("DynamoDB scan error")


# ===== FastAPI App Setup =====
app = FastAPI()


# Health Check
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Prometheus Metrics
try:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app)
except ImportError:

    @app.get("/metrics")
    async def metrics():
        return {"status": "error", "message": "Prometheus metrics are not enabled"}

def test_metrics_fallback():
    response = client.get("/metrics")
    assert response.status_code in [200, 500]
    assert "message" in response.json() or "status" in response.json()


@app.post("/user", response_model=UserResponse)
async def create_user(user: UserCreate):
    try:
        url = get_presigned_url(user.email)
        save_user_to_dynamo(user.name, user.email, url)
        return {"name": user.name, "email": user.email, "avatar_url": url}
    except ClientError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving user",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get("/users")
async def get_users():
    try:
        return get_all_users()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch users")

