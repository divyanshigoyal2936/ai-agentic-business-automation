from fastapi import FastAPI, Header, HTTPException,Depends
from core.database import audit_logs_collection  
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents import orchestrator
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.database import users_collection
import bcrypt
import jwt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im1hbmFnZXJAY29tcGFueS5jb20iLCJyb2xlIjoibWFuYWdlciIsImV4cCI6MTc5MDY2MDMxNH0.LOvSn8_-hSCPHDZkJyKzEtngYoRDG5HG5XPU9Q_SwW8

def create_token(email, role):
    payload = {
        "email": email,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/health")
def check_health():
    return {"status": "ok"}


class ChatRequest(BaseModel):
    message: str


class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/chat")
def chat(request: ChatRequest, user=Depends(verify_token)):
    response = orchestrator(request.message, user["role"], user["email"])
    return {"response": response}

@app.get("/audit-logs")
def get_audit_logs(user=Depends(verify_token)):
    if user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Only managers can view audit logs")

    logs = list(audit_logs_collection.find().sort("timestamp", -1))

    for log in logs:
        log["_id"] = str(log["_id"])
        log["timestamp"] = str(log["timestamp"])

    return {"logs": logs}

@app.post("/login")
def login(request: LoginRequest):
    user = users_collection.find_one({"email": request.email})

    if not user:
        return {"error": "Invalid email or password"}

    password_matches = bcrypt.checkpw(
        request.password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    )

    if not password_matches:
        return {"error": "Invalid email or password"}

    token = create_token(user["email"], user["role"])

    return {"message": "Login successful", "role": user["role"], "token": token}