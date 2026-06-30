# backend/main.py
import os
import shutil
from datetime import datetime, timedelta
from fastapi import FastAPI, UploadFile, File, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from backend.database.connection import engine, Base, get_db
from backend.database import models
from backend.database.models import Appointment, ChatSession, ChatMessage
from backend.auth.routes import router as auth_router
from backend.email_service import send_real_email
from graph.workflow import app as langgraph_app

# Agents
from agents.report_summarizer_agent import summarize_report


# Create all tables (including new Appointment table)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MediAssist AI",
    description="AI-powered Hospital Assistant",
    version="1.0.0"
)

app.include_router(auth_router)

# ── REQUEST SCHEMAS ──
class ChatRequest(BaseModel):
    message: str
    user_name: str = "Patient"
    user_email: str = "patient@example.com"
    chat_history: list = []
    session_id: Optional[int] = None

class AppointmentCreateRequest(BaseModel):
    patient_name: str
    patient_email: str
    doctor_name: str
    doctor_email: Optional[str] = None
    date: str
    time: str

class RejectRequest(BaseModel):
    reason: str

class DoctorProfileUpdate(BaseModel):
    experience: Optional[int] = None
    medical_name: Optional[str] = None
    clinic_address: Optional[str] = None
    contact_number: Optional[str] = None
    bio: Optional[str] = None

class PatientProfileUpdate(BaseModel):
    age: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    blood_group: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    existing_diseases: Optional[str] = None

# ── ROOT ──
@app.get("/")
def read_root():
    return {"message": "Welcome to MediAssist AI API!"}

@app.get("/chat/sessions")
def get_chat_sessions(patient_email: str, db: Session = Depends(get_db)):
    sessions = db.query(models.ChatSession).filter(models.ChatSession.patient_email == patient_email).order_by(models.ChatSession.updated_at.desc()).all()
    return [{"id": s.id, "session_name": s.session_name, "updated_at": s.updated_at} for s in sessions]

@app.get("/chat/sessions/{session_id}/messages")
def get_chat_messages(session_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.id).all()
    return [{"role": m.role, "content": m.content, "timestamp": m.timestamp} for m in messages]

@app.delete("/chat/sessions/{session_id}")
def delete_chat_session(session_id: int, db: Session = Depends(get_db)):
    db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).delete()
    db.query(models.ChatSession).filter(models.ChatSession.id == session_id).delete()
    db.commit()
    return {"status": "success"}

# ── CHAT ENDPOINT ──
@app.post("/chat")
def chat_with_ai(req: ChatRequest, db: Session = Depends(get_db)):
    now_str = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    
    session_id = req.session_id
    if not session_id:
        session_name = req.message[:30] + "..." if len(req.message) > 30 else req.message
        new_session = models.ChatSession(
            patient_email=req.user_email,
            session_name=session_name,
            created_at=now_str,
            updated_at=now_str
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        session_id = new_session.id
    else:
        session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
        if session:
            session.updated_at = now_str
            db.commit()

    user_msg = models.ChatMessage(session_id=session_id, role="user", content=req.message, timestamp=now_str)
    db.add(user_msg)
    db.commit()

    history_str = ""
    for m in req.chat_history[-10:]:
        content = m.get('content', '')
        if "[TICKET_IMAGE:" in content:
            content = content.split("[TICKET_IMAGE:")[0].strip()
        history_str += f"{m['role'].capitalize()}: {content}\n"

    msg_with_details = f"[Patient Name: {req.user_name}]\n[Patient Email: {req.user_email}]\n\n--- CONVERSATION HISTORY ---\n{history_str}"
    result = langgraph_app.invoke({"user_message": msg_with_details, "current_message": req.message})
    
    ai_response = result["response"]
    
    ai_msg = models.ChatMessage(session_id=session_id, role="assistant", content=ai_response, timestamp=(datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"))
    db.add(ai_msg)
    db.commit()

    return {
        "session_id": session_id,
        "agent": result["agent_type"],
        "response": ai_response
    }

# ── APPOINTMENT ENDPOINTS ──

@app.post("/appointments/create")
def create_appointment(req: AppointmentCreateRequest, db: Session = Depends(get_db)):
    """Called by appointment_agent when a booking is detected."""
    appt = models.Appointment(
        patient_name=req.patient_name,
        patient_email=req.patient_email,
        doctor_name=req.doctor_name,
        doctor_email=req.doctor_email,
        date=req.date,
        time=req.time,
        status="pending",
        created_at=(datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M")
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    
    if appt.doctor_email:
        send_real_email(
            appt.doctor_email,
            "🛎️ New Appointment Request - MediAssist AI",
            f"Hello Dr. {appt.doctor_name},\n\nYou have received a new appointment request from {appt.patient_name}.\n\n"
            f"📅 Date: {appt.date}\n⏰ Time: {appt.time}\n\n"
            f"Please log in to your MediAssist dashboard to Accept or Reject this request.\n\nRegards,\nMediAssist AI"
        )
        
    return {"id": appt.id, "status": "pending"}

def cleanup_past_appointments(db: Session):
    """Deletes appointments where the date and time have already passed."""
    now = (datetime.utcnow() + timedelta(hours=5, minutes=30))
    appts = db.query(models.Appointment).all()
    deleted = False
    for a in appts:
        try:
            appt_dt = datetime.strptime(f"{a.date} {a.time}", "%Y-%m-%d %H:%M")
            if appt_dt < now:
                db.delete(a)
                deleted = True
        except ValueError:
            pass
    if deleted:
        db.commit()

@app.get("/appointments/pending")
def get_pending_appointments(doctor_email: str, db: Session = Depends(get_db)):
    """Fetch all pending appointment requests for a specific doctor."""
    cleanup_past_appointments(db)
    appts = db.query(models.Appointment).filter(
        models.Appointment.doctor_email == doctor_email,
        models.Appointment.status == "pending"
    ).all()
    return [
        {
            "id": a.id,
            "patient_name": a.patient_name,
            "patient_email": a.patient_email,
            "doctor_name": a.doctor_name,
            "date": a.date,
            "time": a.time,
            "created_at": a.created_at
        }
        for a in appts
    ]

@app.get("/appointments/accepted")
def get_accepted_appointments(doctor_email: str, db: Session = Depends(get_db)):
    """Fetch all accepted upcoming appointments for a specific doctor."""
    cleanup_past_appointments(db)
    appts = db.query(models.Appointment).filter(
        models.Appointment.doctor_email == doctor_email,
        models.Appointment.status == "accepted"
    ).all()
    
    return [
        {
            "id": a.id,
            "patient_name": a.patient_name,
            "patient_email": a.patient_email,
            "date": a.date,
            "time": a.time,
        }
        for a in appts
    ]

@app.post("/appointments/{appointment_id}/accept")
def accept_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Doctor accepts an appointment — emails sent to BOTH patient and doctor."""
    appt = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appt:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt.status = "accepted"
    db.commit()

    # 1. Email to PATIENT — confirmation
    send_real_email(
        appt.patient_email,
        "✅ Appointment Confirmed! - MediAssist AI",
        f"Hello {appt.patient_name},\n\nGreat news! Dr. {appt.doctor_name} has CONFIRMED your appointment.\n\n"
        f"📅 Date: {appt.date}\n⏰ Time: {appt.time}\n\nPlease arrive 10 minutes early.\n\nRegards,\nMediAssist AI"
    )

    # 2. Email to DOCTOR — reminder of the confirmed slot
    if appt.doctor_email:
        send_real_email(
            appt.doctor_email,
            "📅 Appointment Confirmed in Your Schedule - MediAssist AI",
            f"Hello Dr. {appt.doctor_name},\n\nYou have confirmed a new appointment.\n\n"
            f"👤 Patient: {appt.patient_name}\n📅 Date: {appt.date}\n⏰ Time: {appt.time}\n\nThis slot is now locked in your schedule.\n\nRegards,\nMediAssist AI"
        )

    return {"status": "accepted", "message": f"Appointment accepted. Emails sent to patient and doctor."}

@app.post("/appointments/{appointment_id}/reject")
def reject_appointment(appointment_id: int, req: RejectRequest, db: Session = Depends(get_db)):
    """Doctor rejects an appointment — rejection email sent ONLY to patient."""
    appt = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appt:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt.status = "rejected"
    appt.rejection_reason = req.reason
    db.commit()

    # Email ONLY to PATIENT with rejection reason
    send_real_email(
        appt.patient_email,
        "❌ Appointment Request Update - MediAssist AI",
        f"Hello {appt.patient_name},\n\nWe regret to inform you that Dr. {appt.doctor_name} is unable to accept your appointment request.\n\n"
        f"📅 Requested Date: {appt.date}\n⏰ Requested Time: {appt.time}\n\n"
        f"📝 Reason from Doctor: {req.reason}\n\n"
        f"Please use MediAssist AI to book a new appointment at a different time or with a different doctor.\n\nRegards,\nMediAssist AI"
    )

    return {"status": "rejected", "message": f"Appointment rejected. Email sent to patient only."}

# ── UPLOAD REPORT ENDPOINT ──
@app.post("/reports/upload")
def upload_report(file: UploadFile = File(...)):
    os.makedirs("./uploads", exist_ok=True)
    file_path = f"./uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    summary = summarize_report(file_path)
    return {"summary": summary}



# ── DOCTORS LIST ENDPOINT ──
@app.get("/doctors")
def get_all_doctors(db: Session = Depends(get_db)):
    doctors = db.query(models.User.name, models.User.email, models.Doctor.specialization, models.Doctor.experience, models.Doctor.medical_name, models.Doctor.clinic_address, models.Doctor.contact_number, models.Doctor.bio)\
                .join(models.Doctor, models.User.id == models.Doctor.user_id).all()
    return [{
        "name": doc.name, 
        "email": doc.email,
        "specialization": doc.specialization,
        "experience": doc.experience,
        "medical_name": doc.medical_name,
        "clinic_address": doc.clinic_address,
        "contact_number": doc.contact_number,
        "bio": doc.bio
    } for doc in doctors]

# ── DOCTOR PROFILE ENDPOINTS ──
@app.get("/doctors/profile")
def get_doctor_profile(doctor_email: str, db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor, models.User.name, models.User.email)\
               .join(models.User, models.Doctor.user_id == models.User.id)\
               .filter(models.User.email == doctor_email).first()
    if not doctor:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return {
        "name": doctor.name,
        "email": doctor.email,
        "specialization": doctor[0].specialization,
        "experience": doctor[0].experience,
        "medical_name": doctor[0].medical_name,
        "clinic_address": doctor[0].clinic_address,
        "contact_number": doctor[0].contact_number,
        "bio": doctor[0].bio
    }

@app.post("/doctors/profile")
def update_doctor_profile(doctor_email: str, req: DoctorProfileUpdate, db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor)\
               .join(models.User, models.Doctor.user_id == models.User.id)\
               .filter(models.User.email == doctor_email).first()
    if not doctor:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    if req.experience is not None:
        doctor.experience = req.experience
    if req.medical_name is not None:
        doctor.medical_name = req.medical_name
    if req.clinic_address is not None:
        doctor.clinic_address = req.clinic_address
    if req.contact_number is not None:
        doctor.contact_number = req.contact_number
    if req.bio is not None:
        doctor.bio = req.bio
        
    db.commit()
    return {"message": "Profile updated successfully"}

# ── PATIENT PROFILE ENDPOINTS ──
@app.get("/patients/profile")
def get_patient_profile(patient_email: str, db: Session = Depends(get_db)):
    patient = db.query(models.Patient, models.User.name, models.User.email)\
               .join(models.User, models.Patient.user_id == models.User.id)\
               .filter(models.User.email == patient_email).first()
    if not patient:
        user = db.query(models.User).filter(models.User.email == patient_email).first()
        if user and user.role == "patient":
            new_patient = models.Patient(user_id=user.id)
            db.add(new_patient)
            db.commit()
            db.refresh(new_patient)
            return {
                "name": user.name, "email": user.email, "profile_completed": False,
                "age": None, "gender": None, "height": None, "weight": None, "blood_group": None,
                "phone_number": None, "address": None, "emergency_contact": None,
                "medical_history": None, "allergies": None, "existing_diseases": None
            }
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return {
        "name": patient.name,
        "email": patient.email,
        "profile_completed": bool(patient[0].profile_completed),
        "age": patient[0].age,
        "gender": patient[0].gender,
        "height": patient[0].height,
        "weight": patient[0].weight,
        "blood_group": patient[0].blood_group,
        "phone_number": patient[0].phone_number,
        "address": patient[0].address,
        "emergency_contact": patient[0].emergency_contact,
        "medical_history": patient[0].medical_history,
        "allergies": patient[0].allergies,
        "existing_diseases": patient[0].existing_diseases
    }

@app.post("/patients/profile")
def update_patient_profile(patient_email: str, req: PatientProfileUpdate, db: Session = Depends(get_db)):
    patient = db.query(models.Patient)\
               .join(models.User, models.Patient.user_id == models.User.id)\
               .filter(models.User.email == patient_email).first()
    if not patient:
        user = db.query(models.User).filter(models.User.email == patient_email).first()
        if user and user.role == "patient":
            patient = models.Patient(user_id=user.id)
            db.add(patient)
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Patient not found")
    
    if req.age is not None: patient.age = req.age
    if req.gender is not None: patient.gender = req.gender
    if req.height is not None: patient.height = req.height
    if req.weight is not None: patient.weight = req.weight
    if req.blood_group is not None: patient.blood_group = req.blood_group
    if req.phone_number is not None: patient.phone_number = req.phone_number
    if req.address is not None: patient.address = req.address
    if req.emergency_contact is not None: patient.emergency_contact = req.emergency_contact
    if req.medical_history is not None: patient.medical_history = req.medical_history
    if req.allergies is not None: patient.allergies = req.allergies
    if req.existing_diseases is not None: patient.existing_diseases = req.existing_diseases
    
    patient.profile_completed = 1
    db.commit()
    return {"message": "Patient Profile updated successfully"}

@app.get("/appointments/patient")
def get_patient_appointments(patient_email: str, db: Session = Depends(get_db)):
    cleanup_past_appointments(db)
    appts = db.query(models.Appointment).filter(
        models.Appointment.patient_email == patient_email
    ).order_by(models.Appointment.id.desc()).all()
    
    return [
        {
            "id": a.id,
            "doctor_name": a.doctor_name,
            "date": a.date,
            "time": a.time,
            "status": a.status,
            "rejection_reason": a.rejection_reason,
            "created_at": a.created_at
        }
        for a in appts
    ]
