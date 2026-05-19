from fastapi import APIRouter, Request, HTTPException, Depends, status, Header
from .auth_manager import AuthManager
import re
from datetime import datetime, timedelta
import traceback
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr

from config import settings
from logger import logger

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])

def get_auth_manager():
    return AuthManager()

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    token = authorization.split(" ")[1]
    auth_manager = get_auth_manager()
    user = auth_manager.validate_session(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user

@auth_router.post("/register")
async def register(data: RegisterRequest):
    auth_manager = get_auth_manager()
    try:
        user = auth_manager.create_user(
            data.username, data.email, data.password, 
            data.first_name, data.last_name
        )
        if user:
            token = auth_manager.create_session(user['id'])
            return {
                "message": "Registration successful",
                "user": user,
                "token": token
            }
        raise HTTPException(status_code=400, detail="Registration failed")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("registration_error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@auth_router.post("/login")
async def login(data: LoginRequest):
    auth_manager = get_auth_manager()
    user = auth_manager.authenticate_user(data.username_or_email, data.password)
    if user:
        token = auth_manager.create_session(user['id'])
        return {
            "message": "Login successful",
            "user": user,
            "token": token
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@auth_router.get("/me")
async def get_me(user: Dict = Depends(get_current_user)):
    return {"user": user}

@auth_router.post("/logout")
async def logout(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    get_auth_manager().delete_session(token)
    return {"message": "Logged out"}