import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.schemas import UserCreate, UserResponse
from app.aws_client import get_s3_client, get_dynamodb_resource

app = FastAPI(title="Prima Tech Challenge API")

# Enable CORS for testing from any frontend origin (adjust in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE_NAME")

s3_client = get_s3_client()
dynamodb = get_dynamodb_resource()
table = dynamodb.Table(DYNAMODB_TABLE)

@app.get("/users", response_model=list[UserResponse])
def list_users():
    try:
        response = table.scan()
        items = response.get("Items", [])
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@app.post("/user")
def create_user(user: UserCreate):
    try:
        # Generate unique key for avatar image
        avatar_key = f"avatars/{uuid.uuid4()}.png"
        # Generate presigned POST URL for avatar upload
        presigned_post = s3_client.generate_presigned_post(
            Bucket=S3_BUCKET,
            Key=avatar_key,
            Fields={"acl": "public-read", "Content-Type": "image/png"},
            Conditions=[
                {"acl": "public-read"},
                {"Content-Type": "image/png"}
            ],
            ExpiresIn=3600,
        )
        # Stores user metadata with avatar_url (to be uploaded by client)
        item = {
            "email": user.email,
            "name": user.name,
            "avatar_url": f"https://{S3_BUCKET}.s3.amazonaws.com/{avatar_key}",
        }
        table.put_item(Item=item)
        return {"presigned_post": presigned_post, "user": item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
