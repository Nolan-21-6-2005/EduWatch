import hashlib
from pydantic import BaseModel
from src.database_query.auth import signin
from fastapi import APIRouter

router = APIRouter()

class LoginData(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(data: LoginData):
    try:
        input_hash = hashlib.sha256(
            data.password.encode()
        ).hexdigest()
        
        user = signin(data.email)
        if not user:
            return {
            "success": False,
            "message": "User not found"
        }
        
        stored_hash = user[2]
        if input_hash == stored_hash:
            return {
                "success": True,
                "email": user[1],
                "role": user[3]
            }
        else:
            return {
                "success": False,
                "message": "Wrong password"
            }
    except Exception as e:
        return {
            "success": False,
            "message": "Internal server error"
        }

