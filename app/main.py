from fastapi import FastAPI, UploadFile, File, HTTPException
import boto3
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

app = FastAPI()

# Initialize AWS clients
dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv("AWS_REGION")
)
s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION")
)

@app.get("/users")
async def get_users():
    try:
        table = dynamodb.Table(os.getenv("DYNAMODB_TABLE"))
        return table.scan().get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user")
async def create_user(name: str, email: str, avatar: UploadFile = File(...)):
    try:
        # Upload to S3
        s3.upload_fileobj(
            avatar.file,
            os.getenv("S3_BUCKET"),
            f"avatars/{email}"
        )
        
        # Save to DynamoDB
        dynamodb.Table(os.getenv("DYNAMODB_TABLE")).put_item(
            Item={
                "name": name,
                "email": email,
                "avatar_url": f"https://{os.getenv('S3_BUCKET')}.s3.amazonaws.com/avatars/{email}"
            }
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))