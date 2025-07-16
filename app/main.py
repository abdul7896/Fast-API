import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from app.schemas import UserCreate, UserResponse
from app.aws_client import get_s3_client, get_dynamodb_resource
from prometheus_client import Counter
from botocore.exceptions import ClientError

# Initialize FastAPI once
app = FastAPI(title="Prima Tech Challenge API")

# Metrics
REQUEST_COUNT = Counter('request_count', 'App Request Count')

# Middleware
@app.middleware("http")
async def count_requests(request, call_next):
    REQUEST_COUNT.inc()
    response = await call_next(request)
    return response

# CORS (configure properly for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# AWS Resources
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE_NAME")
s3_client = get_s3_client()
dynamodb = get_dynamodb_resource()
table = dynamodb.Table(DYNAMODB_TABLE)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/users", response_model=list[UserResponse])
def list_users():
    try:
        response = table.scan()
        return response.get("Items", [])
    except ClientError as e:
        raise HTTPException(500, f"DynamoDB error: {e.response['Error']['Message']}")
    except Exception as e:
        raise HTTPException(500, f"Unexpected error: {str(e)}")

@app.post("/user")
def create_user(user: UserCreate):
    try:
        avatar_key = f"avatars/{uuid.uuid4()}.png"
        presigned_post = s3_client.generate_presigned_post(
            Bucket=S3_BUCKET,
            Key=avatar_key,
            Fields={"acl": "public-read", "Content-Type": "image/png"},
            Conditions=[{"acl": "public-read"}, {"Content-Type": "image/png"}],
            ExpiresIn=3600,
        )
        
        item = {
            "email": user.email,
            "name": user.name,
            "avatar_url": f"https://{S3_BUCKET}.s3.amazonaws.com/{avatar_key}",
        }
        
        table.put_item(Item=item)
        return {"presigned_post": presigned_post, "user": item}
        
    except ClientError as e:
        raise HTTPException(500, f"AWS error: {e.response['Error']['Message']}")
    except ValidationError as e:
        raise HTTPException(422, detail=e.errors())
    except Exception as e:
        raise HTTPException(500, f"Unexpected error: {str(e)}")

from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

# Create Prometheus metrics
REQUEST_COUNT = Counter(
    'app_requests_total', 'Total HTTP requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds', 'Request latency',
    ['method', 'endpoint']
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    request_latency = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        http_status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(request_latency)
    
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# import os
# import uuid
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from pydantic import ValidationError
# from app.schemas import UserCreate, UserResponse
# from app.aws_client import get_s3_client, get_dynamodb_resource
# from fastapi import FastAPI
# from prometheus_client import start_http_server, Counter
# from fastapi import FastAPI

# REQUEST_COUNT = Counter('request_count', 'App Request Count')

# app = FastAPI()

# @app.middleware("http")
# async def count_requests(request, call_next):
#     REQUEST_COUNT.inc()
#     response = await call_next(request)
#     return response

# # Start Prometheus metrics server on a different port (e.g. 8001)
# import threading
# threading.Thread(target=start_http_server, args=(8001,), daemon=True).start()

# app = FastAPI()

# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}

# app = FastAPI(title="Prima Tech Challenge API")



# # Enable CORS for testing from any frontend origin (adjust in prod)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# S3_BUCKET = os.getenv("S3_BUCKET_NAME")
# DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE_NAME")

# s3_client = get_s3_client()
# dynamodb = get_dynamodb_resource()
# table = dynamodb.Table(DYNAMODB_TABLE)

# @app.get("/users", response_model=list[UserResponse])
# def list_users():
#     try:
#         response = table.scan()
#         items = response.get("Items", [])
#         return items
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

# @app.post("/user")
# def create_user(user: UserCreate):
#     try:
#         # Generate unique key for avatar image
#         avatar_key = f"avatars/{uuid.uuid4()}.png"
#         # Generate presigned POST URL for avatar upload
#         presigned_post = s3_client.generate_presigned_post(
#             Bucket=S3_BUCKET,
#             Key=avatar_key,
#             Fields={"acl": "public-read", "Content-Type": "image/png"},
#             Conditions=[
#                 {"acl": "public-read"},
#                 {"Content-Type": "image/png"}
#             ],
#             ExpiresIn=3600,
#         )
#         # Stores user metadata with avatar_url (to be uploaded by client)
#         item = {
#             "email": user.email,
#             "name": user.name,
#             "avatar_url": f"https://{S3_BUCKET}.s3.amazonaws.com/{avatar_key}",
#         }
#         table.put_item(Item=item)
#         return {"presigned_post": presigned_post, "user": item}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
