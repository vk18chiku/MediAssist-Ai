# backend/auth/routes.py
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import jwt
import os
import enum
from backend.email_service import send_real_email

from backend.database.connection import get_db
from backend.database.models import User, Patient, Doctor, PasswordReset, SignupOTP

# Setup Authentication Details
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# pwd_context removed
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ── Pydantic Schemas ──
class RoleEnum(str, enum.Enum):
    patient = "patient"
    doctor = "doctor"
    admin = "admin"

class SendSignupOTPRequest(BaseModel):
    email: EmailStr

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.patient
    specialization: Optional[str] = None
    otp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str

# ── Helper Functions ──
def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password, hashed_password):
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ── API Routes ──
@router.post("/signup-send-otp")
def signup_send_otp(data: SendSignupOTPRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    otp = str(random.randint(100000, 999999))
    expires_at = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
    
    db.query(SignupOTP).filter(SignupOTP.email == data.email).delete()
    
    otp_record = SignupOTP(email=data.email, otp=otp, expires_at=expires_at)
    db.add(otp_record)
    db.commit()
    
    subject = "Verify your email - MediAssist AI"
    body = f"Hello,\n\nYour OTP to verify your email and create an account is: {otp}\n\nThis OTP is valid for 15 minutes."
    send_real_email(data.email, subject, body)
    
    return {"msg": "OTP sent successfully"}

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    otp_record = db.query(SignupOTP).filter(SignupOTP.email == data.email, SignupOTP.otp == data.otp).first()
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    if datetime.fromisoformat(otp_record.expires_at) < datetime.utcnow():
        db.delete(otp_record)
        db.commit()
        raise HTTPException(status_code=400, detail="OTP has expired")
        
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=data.role.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create Patient or Doctor profile
    if data.role == RoleEnum.patient:
        db.add(Patient(user_id=user.id))
    elif data.role == RoleEnum.doctor:
        spec = data.specialization if data.specialization else "General Physician"
        db.add(Doctor(user_id=user.id, specialization=spec))
    db.commit()
    
    db.delete(otp_record)
    db.commit()

    # Send welcome email
    subject = "Welcome to MediAssist AI! 🏥"
    body = f"Hello {user.name},\n\nYour account as a '{user.role.capitalize()}' has been successfully created.\n\nThank you for choosing MediAssist AI for your healthcare needs!"
    send_real_email(user.email, subject, body)

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    return TokenResponse(access_token=token, token_type="bearer", role=user.role, name=user.name)

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    return TokenResponse(access_token=token, token_type="bearer", role=user.role, name=user.name)

import random

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"msg": "If the email is registered, an OTP has been sent."}
    
    otp = str(random.randint(100000, 999999))
    expires_at = (datetime.utcnow() + timedelta(minutes=15)).isoformat()
    
    db.query(PasswordReset).filter(PasswordReset.email == data.email).delete()
    
    reset_record = PasswordReset(email=data.email, otp=otp, expires_at=expires_at)
    db.add(reset_record)
    db.commit()
    
    subject = "Password Reset OTP - MediAssist AI"
    body = f"Hello {user.name},\n\nYour OTP for resetting your password is: {otp}\n\nThis OTP is valid for 15 minutes."
    send_real_email(user.email, subject, body)
    
    return {"msg": "If the email is registered, an OTP has been sent."}

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_record = db.query(PasswordReset).filter(PasswordReset.email == data.email, PasswordReset.otp == data.otp).first()
    
    if not reset_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    if datetime.fromisoformat(reset_record.expires_at) < datetime.utcnow():
        db.delete(reset_record)
        db.commit()
        raise HTTPException(status_code=400, detail="OTP has expired")
        
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
        
    user.hashed_password = get_password_hash(data.new_password)
    db.delete(reset_record)
    db.commit()
    
    return {"msg": "Password has been reset successfully."}