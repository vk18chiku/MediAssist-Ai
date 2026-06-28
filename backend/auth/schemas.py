# backend/database/schemas.py
from pydantic import BaseModel, EmailStr

# Signup ke liye data structure
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "patient" # Default role patient hoga

# Login ke liye data structure
class UserLogin(BaseModel):
    email: EmailStr
    password: str