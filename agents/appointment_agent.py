# agents/appointment_agent.py
import os
from datetime import datetime
from PIL import Image, ImageDraw
from langchain_openai import ChatOpenAI
from backend.email_service import send_real_email
from backend.database.connection import engine
from backend.database.models import User, Appointment
from sqlalchemy.orm import sessionmaker

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Database Session Setup
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_doctor_email(doc_name):
    """Database se Doctor ka asli email nikalna"""
    db = SessionLocal()
    try:
        # Remove 'Dr.' or 'Dr ' prefix for better matching
        clean_name = doc_name.replace("Dr.", "").replace("Dr ", "").strip()
        doc = db.query(User).filter(User.name.ilike(f"%{clean_name}%"), User.role == "doctor").first()
        return doc.email if doc else None
    finally:
        db.close()

def generate_ticket(patient_name, doc_name, date, time):
    """Appointment Ticket (Image) create karna"""
    os.makedirs("./uploads", exist_ok=True)
    ticket_path = f"./uploads/ticket_{patient_name.replace(' ', '_')}_{time.replace(':','')}.png"
    
    img = Image.new('RGB', (450, 200), color=(30, 40, 50))
    d = ImageDraw.Draw(img)
    
    d.text((20, 20), "🏥 MEDIASSIST APPOINTMENT TICKET", fill=(255, 215, 0))
    d.text((20, 70), f"Patient Name: {patient_name}", fill=(255, 255, 255))
    d.text((20, 110), f"Doctor: {doc_name}", fill=(255, 255, 255))
    d.text((20, 150), f"Date: {date}  |  Time: {time}", fill=(255, 255, 255))
    
    img.save(ticket_path)
    return ticket_path

def save_appointment_to_db(patient_name, patient_email, doc_name, doc_email, date, time):
    """Appointment ko database mein directly save karna (status: pending)"""
    db = SessionLocal()
    try:
        appt = Appointment(
            patient_name=patient_name,
            patient_email=patient_email,
            doctor_name=doc_name,
            doctor_email=doc_email,
            date=date,
            time=time,
            status="pending",
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        db.add(appt)
        db.commit()
        db.refresh(appt)
        print(f"✅ Appointment saved to DB: ID={appt.id}, status=pending")
        return appt.id
    except Exception as e:
        print(f"❌ Error saving appointment to DB: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def book_appointment(state: dict):
    user_message = state["user_message"]
    
    # Patient ka Naam aur Email extract karna
    patient_name = "Patient"
    patient_email = None
    if "[Patient Name:" in user_message:
        try:
            patient_name = user_message.split("[Patient Name:")[1].split("]")[0].strip()
        except:
            pass
            
    if "[Patient Email:" in user_message:
        try:
            patient_email = user_message.split("[Patient Email:")[1].split("]")[0].strip()
        except:
            pass

    prompt = f"""
    You are an Appointment Booking Agent. Read the CONVERSATION HISTORY and extract:
    1. Doctor's Name
    2. Date
    3. Time

    If ANY are missing, ask politely. If ALL are present in the conversation, reply EXACTLY in this format:
    SUCCESS | [Doctor Name] | [Date] | [Time]

    {user_message}
    """
    
    response = llm.invoke(prompt).content
    print(f"\n[APPOINTMENT AGENT LLM RESPONSE]: {response}\n")

    if response.startswith("SUCCESS"):
        parts = response.split("|")
        doc_name = parts[1].strip()
        date = parts[2].strip()
        time = parts[3].strip()
        
        # 1. Doctor ka asli email nikalna
        doc_email = get_doctor_email(doc_name)
        
        # 2. Appointment ko DB mein save karna (status: pending)
        save_appointment_to_db(patient_name, patient_email or "", doc_name, doc_email, date, time)
        
        # 3. Patient ko "Request Sent" email bhejna
        if patient_email:
            send_real_email(
                patient_email,
                "📋 Appointment Request Sent - MediAssist AI",
                f"Hello {patient_name},\n\nYour appointment request has been sent to Dr. {doc_name}.\n\n"
                f"📅 Requested Date: {date}\n⏰ Requested Time: {time}\n\n"
                f"You will receive a confirmation email once the doctor reviews your request.\n\nRegards,\nMediAssist AI"
            )
        
        # 4. Doctor ko notification email bhejna
        if doc_email:
            send_real_email(
                doc_email,
                "🔔 New Appointment Request - MediAssist AI",
                f"Hello Dr. {doc_name},\n\nYou have a new appointment request.\n\n"
                f"👤 Patient: {patient_name}\n📅 Date: {date}\n⏰ Time: {time}\n\n"
                f"Please login to your MediAssist AI portal to Accept or Reject this request.\n\nRegards,\nMediAssist AI"
            )
        
        # 5. Image Ticket Generate karna
        ticket_path = generate_ticket(patient_name, doc_name, date, time)
        
        # Final Response UI ke liye
        final_msg = (
            f"✅ Your appointment **request** has been sent to **Dr. {doc_name}** for **{date}** at **{time}**!\n\n"
            f"📧 You will receive a confirmation email once the doctor accepts your request.\n\n"
            f"[TICKET_IMAGE:{ticket_path}]"
        )
        
        return {"response": final_msg}
    else:
        return {"response": response}