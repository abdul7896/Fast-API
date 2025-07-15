import os
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

# Read bucket name from environment variable
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
if not S3_BUCKET_NAME:
    raise RuntimeError("S3_BUCKET_NAME environment variable is not set")

@app.get("/users")
def get_users():
    # Your logic to get users from DynamoDB
    return {"message": "This will list users"}

@app.post("/user")
async def create_user(name: str, email: str, avatar: UploadFile = File(...)):
    # Use S3_BUCKET_NAME here to upload avatar
    # Your upload logic here...

    return {"message": f"User created and avatar uploaded to bucket {S3_BUCKET_NAME}"}
