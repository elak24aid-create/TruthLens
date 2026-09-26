import os
import json
import uuid
import hashlib
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel
from typing import Optional
from backend.app.config import BASE_DIR

router = APIRouter(prefix="/auth", tags=["Auth"])

USERS_FILE = BASE_DIR / "data" / "users.json"

class AuthRequest(BaseModel):
    email: str
    password: str
    
class AuthResponse(BaseModel):
    token: str
    email: str
    
def _load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def _save_users(users):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/register", response_model=AuthResponse)
def register(req: AuthRequest):
    users = _load_users()
    if req.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    token = str(uuid.uuid4())
    users[req.email] = {
        "password_hash": _hash_password(req.password),
        "token": token
    }
    _save_users(users)
    return AuthResponse(token=token, email=req.email)

@router.post("/login", response_model=AuthResponse)
def login(req: AuthRequest):
    users = _load_users()
    user = users.get(req.email)
    if not user or user["password_hash"] != _hash_password(req.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    # Generate new token on login
    token = str(uuid.uuid4())
    users[req.email]["token"] = token
    _save_users(users)
    return AuthResponse(token=token, email=req.email)

@router.get("/me")
def get_profile(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    
    users = _load_users()
    for email, data in users.items():
        if data.get("token") == token:
            return {"email": email}
            
    raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"status": "success"}
    token = authorization.split(" ")[1]
    
    users = _load_users()
    for email, data in users.items():
        if data.get("token") == token:
            data["token"] = None
            _save_users(users)
            return {"status": "success"}
    return {"status": "success"}
