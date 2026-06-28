# backend/database/models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from backend.database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # Role ko String rakha gaya hai taaki SQLite bina error ke data save kar sake
    role = Column(String, default="patient")

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    # Future scaling ke liye: age, blood_group wagaira yahan add honge

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    specialization = Column(String, default="General Physician")
    medical_name = Column(String, nullable=True)
    experience = Column(Integer, nullable=True)
    clinic_address = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    bio = Column(String, nullable=True)

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String)
    patient_email = Column(String)
    doctor_name = Column(String)
    doctor_email = Column(String, nullable=True)
    date = Column(String)
    time = Column(String)
    # Status: pending / accepted / rejected
    status = Column(String, default="pending")
    rejection_reason = Column(String, nullable=True)
    created_at = Column(String)

class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    otp = Column(String)
    expires_at = Column(String)

class SignupOTP(Base):
    __tablename__ = "signup_otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    otp = Column(String)
    expires_at = Column(String)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_email = Column(String, index=True)
    session_name = Column(String)
    created_at = Column(String)
    updated_at = Column(String)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String) # 'user' or 'assistant'
    content = Column(String)
    timestamp = Column(String)
