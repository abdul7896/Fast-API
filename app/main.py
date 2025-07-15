from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.get("/users")
def get_users():
    return {"message": "This will list users"}

@app.post("/user")
def create_user(name: str, email: str, avatar: UploadFile = File(...)):
    return {"message": "User created"}