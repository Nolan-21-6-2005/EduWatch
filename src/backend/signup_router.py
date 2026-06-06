import hashlib
from auth import signin
from fastapi import APIRouter
from pydantic import BaseModel
from auth import signup
from fastapi import APIRouter

router = APIRouter()

class LoginData(BaseModel):
    username: str
    password: str
    email: str
    gender: str
    phone: str
    date: str
    role: str
    
@router.post("/signup")
def login(data: LoginData):
    try:
        
        user = signup(
            data.username,
            data.password,
            data.email,
            data.gender,
            data.phone,
            data.date,
            data.role
        )
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        
