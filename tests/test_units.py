from fastapi import FastAPI, UploadFile, Form, HTTPException
from typing import List

app = FastAPI()

# Temporary in-memory storage for testing
users_db = []

@app.post("/user")
async def create_user(
    name: str = Form(...),
    email: str = Form(...),
    avatar: UploadFile = None
):
    """Create a user with avatar"""
    if not email.endswith("@example.com"):
        raise HTTPException(status_code=422, detail="Invalid email format")
    
    user = {"name": name, "email": email}
    users_db.append(user)
    return {"user_id": len(users_db)}

@app.get("/users")
async def get_users():
    """Get all users"""
    return users_db