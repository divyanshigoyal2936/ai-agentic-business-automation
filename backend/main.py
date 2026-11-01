from fastapi import FastAPI, Header, HTTPException, Depends
from core.database import audit_logs_collection, pending_approvals_collection, users_collection
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents import orchestrator, log_action
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from tools.order_tools import process_refund
from bson import ObjectId
import bcrypt
import jwt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()

frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# ---------------- Human-in-the-loop approvals ----------------

def require_manager(user):
    if user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Only managers can handle approvals")


def to_object_id(approval_id):
    try:
        return ObjectId(approval_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid approval id")


@app.get("/approvals")
def get_pending_approvals(user=Depends(verify_token)):
    require_manager(user)

    items = list(pending_approvals_collection.find({"status": "pending"}).sort("created_at", -1))

    for item in items:
        item["_id"] = str(item["_id"])
        item["created_at"] = str(item["created_at"])

    return {"approvals": items}


@app.post("/approvals/{approval_id}/approve")
def approve_request(approval_id: str, user=Depends(verify_token)):
    require_manager(user)
    oid = to_object_id(approval_id)

    # Atomic claim: only a "pending" request can become "approved".
    # A second approve click returns None here, so no double refund.
    approval = pending_approvals_collection.find_one_and_update(
        {"_id": oid, "status": "pending"},
        {"$set": {
            "status": "approved",
            "decided_by": user["email"],
            "decided_at": datetime.datetime.now()
        }}
    )

    if not approval:
        raise HTTPException(status_code=409, detail="Request not found or already decided")

    result = process_refund(approval["order_id"])

    log_action(user["email"], user["role"], "process_refund",
               {"order_id": approval["order_id"]}, result, True)

    return {"message": "Refund approved and processed", "result": result}


@app.post("/approvals/{approval_id}/reject")
def reject_request(approval_id: str, user=Depends(verify_token)):
    require_manager(user)
    oid = to_object_id(approval_id)

    approval = pending_approvals_collection.find_one_and_update(
        {"_id": oid, "status": "pending"},
        {"$set": {
            "status": "rejected",
            "decided_by": user["email"],
            "decided_at": datetime.datetime.now()
        }}
    )

    if not approval:
        raise HTTPException(status_code=409, detail="Request not found or already decided")

    result = {"error": "Refund request rejected by manager"}

    log_action(user["email"], user["role"], "process_refund",
               {"order_id": approval["order_id"]}, result, False)

    return {"message": "Refund request rejected", "result": result}