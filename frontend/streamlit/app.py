# frontend/streamlit/app.py
import streamlit as st
import requests
from streamlit_mic_recorder import mic_recorder
import os
import base64

st.set_page_config(page_title="MediAssist AI", page_icon="🏥", layout="wide")

import platform
# Smart URL: agar Windows pe run ho raha hai (local), toh localhost use kare.
# Agar Linux (Docker) pe hai, toh mediassist_backend use kare.
if platform.system() == "Windows":
    BASE_URL = "http://localhost:8000"
else:
    BASE_URL = os.environ.get("BACKEND_URL", "http://mediassist_backend:8000")

def img_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

STATIC = "/app/frontend/streamlit/static"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(circle at top, #151a28 0%, #0b0f19 100%) !important; min-height: 100vh; }
#MainMenu, footer, header { visibility: hidden; }

[data-testid="stSidebar"] {
    background: #11151e !important;
    border-right: 1px solid rgba(30, 42, 58, 0.8) !important;
}
[data-testid="stSidebar"] * { color: #c9d1d9; }

.stButton > button {
    border-radius: 8px !important; font-weight: 600 !important;
    font-size: 14px !important; transition: all 0.2s ease !important; border: none !important;
}
.stButton > button[kind="primary"] { background: #2563eb !important; color: white !important; }
.stButton > button[kind="primary"]:hover { background: #1d4ed8 !important; transform: translateY(-1px) !important; }
.stButton > button[kind="secondary"] { background: #1e2a3a !important; color: #94a3b8 !important; border: 1px solid #2d3748 !important; }
.stButton > button[kind="secondary"]:hover { background: #263444 !important; }

.stFormSubmitButton > button {
    background: #2563eb !important; color: white !important;
    border-radius: 8px !important; font-weight: 600 !important;
    border: none !important; transition: all 0.2s ease !important;
}
.stFormSubmitButton > button:hover { background: #1d4ed8 !important; transform: translateY(-1px) !important; }

.stTabs [data-baseweb="tab-list"] {
    background: rgba(15, 17, 23, 0.8) !important; border-radius: 12px !important;
    padding: 6px !important; gap: 8px !important; border: 1px solid rgba(30, 42, 58, 0.8) !important;
    box-shadow: inset 0 2px 6px rgba(0,0,0,0.3) !important;
}
.stTabs [data-baseweb="tab"] { 
    border-radius: 8px !important; font-weight: 600 !important; 
    color: #94a3b8 !important; padding: 10px 24px !important; transition: all 0.3s ease !important;
}
.stTabs [aria-selected="true"] { 
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important; 
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    color: white !important; 
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(22, 27, 39, 0.6) !important; border: 1px solid rgba(45, 55, 72, 0.5) !important;
    backdrop-filter: blur(8px) !important;
    border-radius: 8px !important; color: #e2e8f0 !important; transition: all 0.2s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #2563eb !important; box-shadow: 0 0 0 2px rgba(37,99,235,0.15) !important;
}
.stTextInput label, .stTextArea label, .stNumberInput label,
.stSelectbox label, .stFileUploader label {
    color: #94a3b8 !important; font-size: 13px !important; font-weight: 500 !important;
}
[data-testid="stChatMessage"] {
    background: rgba(22, 27, 39, 0.7) !important; border: 1px solid rgba(45, 55, 72, 0.4) !important;
    backdrop-filter: blur(8px) !important; box-shadow: 0 4px 10px -2px rgba(0,0,0,0.1) !important;
    border-radius: 12px !important; margin-bottom: 12px !important; padding: 6px !important;
}
[data-testid="stChatInputTextArea"] {
    background: #161b27 !important; border: 1px solid #2d3748 !important;
    border-radius: 10px !important; color: #e2e8f0 !important;
}
hr { border-color: #1e2a3a !important; }
.stAlert { border-radius: 8px !important; }
.streamlit-expanderHeader {
    background: #161b27 !important; border-radius: 8px !important;
    color: #94a3b8 !important; font-weight: 600 !important; border: 1px solid #1e2a3a !important;
}
[data-testid="stFileUploader"] {
    background: #161b27 !important; border: 1px dashed #2d3748 !important; border-radius: 8px !important;
}
[data-baseweb="select"] > div {
    background: #161b27 !important; border: 1px solid #2d3748 !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #e2e8f0 !important; font-weight: 600 !important; }
.stSpinner > div { border-top-color: #2563eb !important; }
.stNumberInput button { background: #1e2a3a !important; border-radius: 6px !important; }

[data-testid="stForm"] {
    background: linear-gradient(145deg, rgba(22, 27, 39, 0.95), rgba(15, 17, 23, 0.98)) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(37, 99, 235, 0.2) !important;
    border-radius: 16px !important;
    box-shadow: 0 0 40px -10px rgba(37, 99, 235, 0.15), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    padding: 2rem !important;
}

.card {
    background: linear-gradient(145deg, rgba(22, 27, 39, 0.9), rgba(15, 17, 23, 0.95));
    backdrop-filter: blur(10px);
    border: 1px solid rgba(30, 42, 58, 0.6);
    border-radius: 12px; padding: 18px 20px; margin-bottom: 12px;
    box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px -2px rgba(0, 0, 0, 0.3);
}
.badge {
    display: inline-block; background: #1e3a8a; color: #93c5fd;
    padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

for key, default in [("token", None), ("user_name", None), ("user_email", None), ("role", None), ("messages", []), ("forgot_password_mode", False), ("otp_sent", False), ("reset_email", ""), ("signup_otp_sent", False), ("current_session_id", None)]:
    if key not in st.session_state:
        st.session_state[key] = default


def auth_screen():
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 1.6, 1])
    with col_m:
        st.markdown("""
        <div style="text-align:center; margin-bottom:2rem;">
            <img src="https://cdn-icons-png.flaticon.com/512/2966/2966327.png" style="margin-bottom:16px; filter: drop-shadow(0 0 15px rgba(37,99,235,0.4));" width="100" height="100">
            <h1 style="margin:0; color:#e2e8f0; font-size:2.4rem; font-weight:800; letter-spacing:-0.5px;">MediAssist <span style="color:#38bdf8;">AI</span></h1>
            <p style="color:#94a3b8; font-size:1.05rem; margin-top:8px; font-weight:400;">Your Intelligent Healthcare Companion</p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.forgot_password_mode:
            st.markdown("### Reset Your Password")
            
            if not st.session_state.otp_sent:
                with st.form("forgot_password_form"):
                    st.info("Enter your registered email. We will send you a 6-digit OTP.")
                    reset_email_input = st.text_input("Email", placeholder="you@example.com")
                    if st.form_submit_button("Send OTP", type="primary", use_container_width=True):
                        if reset_email_input:
                            with st.spinner("Sending OTP..."):
                                res = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": reset_email_input})
                            if res.status_code == 200:
                                st.session_state.otp_sent = True
                                st.session_state.reset_email = reset_email_input
                                st.success("OTP sent! Please check your email.")
                                st.rerun()
                            else:
                                st.error("Failed to send OTP.")
                        else:
                            st.error("Please enter your email.")
            else:
                with st.form("reset_password_form"):
                    st.info(f"Enter the OTP sent to {st.session_state.reset_email} and your new password.")
                    otp_input = st.text_input("6-digit OTP")
                    new_password_input = st.text_input("New Password", type="password")
                    if st.form_submit_button("Reset Password", type="primary", use_container_width=True):
                        if otp_input and new_password_input:
                            with st.spinner("Resetting password..."):
                                res = requests.post(f"{BASE_URL}/auth/reset-password", json={
                                    "email": st.session_state.reset_email,
                                    "otp": otp_input,
                                    "new_password": new_password_input
                                })
                            if res.status_code == 200:
                                st.success("Password has been reset successfully! You can now login.")
                                st.session_state.forgot_password_mode = False
                                st.session_state.otp_sent = False
                                st.rerun()
                            else:
                                try: st.error(res.json().get("detail", "Failed to reset password."))
                                except: st.error("Server error.")
                        else:
                            st.error("Please fill in all fields.")
                            
            if st.button("Back to Login", use_container_width=True):
                st.session_state.forgot_password_mode = False
                st.session_state.otp_sent = False
                st.rerun()
            
            return

        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            with st.form("login_form"):
                log_email    = st.text_input("Email", placeholder="you@example.com")
                log_password = st.text_input("Password", type="password", placeholder="Enter your password")
                st.markdown("<br>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("Login", use_container_width=True)
                if submit_login:
                    with st.spinner("Authenticating..."):
                        res = requests.post(f"{BASE_URL}/auth/login", json={"email": log_email, "password": log_password})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.token      = data["access_token"]
                        st.session_state.user_name  = data["name"]
                        st.session_state.user_email = log_email
                        st.session_state.role       = data["role"]
                        st.success(f"Welcome back, {data['name']}!")
                        st.rerun()
                    else:
                        try: st.error(res.json().get("detail", "Invalid credentials."))
                        except: st.error("Server error. Please try again.")
            
            if st.button("Forgot Password?", use_container_width=True):
                st.session_state.forgot_password_mode = True
                st.session_state.otp_sent = False
                st.rerun()

        with tab2:
            reg_name     = st.text_input("Full Name", key="reg_name", placeholder="John Doe", disabled=st.session_state.signup_otp_sent)
            reg_email    = st.text_input("Email", key="reg_email", placeholder="you@example.com", disabled=st.session_state.signup_otp_sent)
            reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Min 6 characters", disabled=st.session_state.signup_otp_sent)
            reg_role     = st.selectbox("I am a:", ["patient", "doctor"], key="reg_role", disabled=st.session_state.signup_otp_sent)
            reg_spec = None
            if reg_role == "doctor":
                reg_spec = st.selectbox("Specialization:", [
                    "General Physician", "Neurologist", "Cardiologist",
                    "Dermatologist", "Pediatrician", "Orthopedic"
                ], key="reg_spec", disabled=st.session_state.signup_otp_sent)
            st.markdown("<br>", unsafe_allow_html=True)
            
            if not st.session_state.signup_otp_sent:
                submit_signup = st.button("Send OTP to Email", type="primary", use_container_width=True)
                if submit_signup:
                    if reg_name and reg_email and reg_password:
                        with st.spinner("Sending OTP..."):
                            res = requests.post(f"{BASE_URL}/auth/signup-send-otp", json={"email": reg_email})
                        if res.status_code == 200:
                            st.session_state.signup_otp_sent = True
                            st.success("OTP sent to your email!")
                            st.rerun()
                        else:
                            try: st.error(res.json().get("detail", "Could not send OTP."))
                            except: st.error("Server error.")
                    else:
                        st.error("Please fill all required fields before sending OTP.")
            else:
                st.info(f"An OTP has been sent to {reg_email}")
                signup_otp = st.text_input("Enter 6-digit OTP", key="signup_otp")
                verify_signup = st.button("Verify & Create Account", type="primary", use_container_width=True)
                if verify_signup:
                    if signup_otp:
                        payload = {"name": reg_name, "email": reg_email, "password": reg_password, "role": reg_role, "specialization": reg_spec, "otp": signup_otp}
                        with st.spinner("Creating your account..."):
                            res = requests.post(f"{BASE_URL}/auth/signup", json=payload)
                        if res.status_code == 201:
                            data = res.json()
                            st.session_state.token      = data["access_token"]
                            st.session_state.user_name  = data["name"]
                            st.session_state.user_email = reg_email
                            st.session_state.role       = data["role"]
                            st.session_state.signup_otp_sent = False
                            st.success(f"Account created! Welcome, {data['name']}.")
                            st.rerun()
                        else:
                            try: st.error(res.json().get("detail", "Signup failed."))
                            except: st.error("Server error.")
                    else:
                        st.error("Please enter the OTP.")
                        
                if st.button("Change Email (Go Back)", use_container_width=True):
                    st.session_state.signup_otp_sent = False
                    st.rerun()


def process_chat_response(full_res):
    if "[TICKET_IMAGE:" in full_res:
        text_part = full_res.split("[TICKET_IMAGE:")[0].strip()
        img_path  = full_res.split("[TICKET_IMAGE:")[1].split("]")[0]
        st.chat_message("assistant").markdown(text_part)
        try: st.image(img_path)
        except: pass
        st.session_state.messages.append({"role": "assistant", "content": text_part, "image": img_path})
    else:
        st.chat_message("assistant").markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})


def doctor_dashboard():
    # Fetch profile details for the header
    res = requests.get(f"{BASE_URL}/doctors/profile", params={"doctor_email": st.session_state.user_email})
    profile = res.json() if res.status_code == 200 else {}

    col1, col2 = st.columns([8, 1])
    with col1:
        avatar_url = f"https://ui-avatars.com/api/?name={profile.get('name', st.session_state.user_name).replace(' ', '+')}&background=2563eb&color=fff&size=128&bold=true"
        st.markdown(f"""
        <div class="card" style="border-top: 4px solid #2563eb; margin-bottom: 20px; padding: 20px;">
            <div style="display: flex; gap: 20px; align-items: flex-start;">
                <img src="{avatar_url}" style="border-radius: 12px; width: 80px; height: 80px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="flex-grow: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h2 style="margin:0 0 6px 0; color:#e2e8f0; font-size:1.8rem; font-weight:700;">
                                Dr. {profile.get('name', st.session_state.user_name)}
                            </h2>
                            <span class="badge" style="background:#2563eb; color:white; font-size: 13px; padding: 6px 12px;">{profile.get('specialization', 'Doctor')}</span>
                        </div>
                        <div style="text-align: right;">
                            <div style="color:#e2e8f0; font-weight:600; font-size:16px;">{profile.get('medical_name') or 'Clinic / Hospital Not Set'}</div>
                            <div style="color:#94a3b8; font-size:13px; margin-top:2px;">📍 {profile.get('clinic_address') or 'Address not provided'}</div>
                            <div style="color:#64748b; font-size:12px; margin-top:4px;">📞 {profile.get('contact_number') or 'Contact not provided'}</div>
                        </div>
                    </div>
                    <div style="margin-top:20px; color:#94a3b8; font-size:14px; line-height:1.6; background:#0f1117; padding:12px; border-radius:8px;">
                        {profile.get('bio') or '<i>No bio provided yet. Update your profile below to add one.</i>'}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", type="secondary"):
            st.session_state.token = None
            st.session_state.messages = []
            st.rerun()

    st.divider()
    tab1, tab2 = st.tabs(["Dashboard", "My Profile"])

    with tab1:
        with st.sidebar:
            st.markdown("### Upcoming Appointments")
            if st.button("Refresh", key="refresh_accepted", use_container_width=True):
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            res = requests.get(f"{BASE_URL}/appointments/accepted",
                               params={"doctor_email": st.session_state.user_email})
            if res.status_code == 200:
                accepted = res.json()
                if accepted:
                    for appt in accepted:
                        st.markdown(f"""
                        <div class="card" style="padding:14px;">
                            <div style="color:#e2e8f0; font-weight:600; font-size:14px; margin-bottom:6px;">{appt['patient_name']}</div>
                            <div style="color:#64748b; font-size:13px;">&#x1F4C5; {appt['date']}</div>
                            <div style="color:#64748b; font-size:13px;">&#x23F0; {appt['time']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No upcoming appointments.")
            else:
                st.error("Could not load appointments.")

        st.markdown("### Pending Appointment Requests")
        res = requests.get(f"{BASE_URL}/appointments/pending",
                           params={"doctor_email": st.session_state.user_email})
        if res.status_code == 200:
            pending = res.json()
            if not pending:
                st.success("All caught up! No pending requests.")
            else:
                st.info(f"{len(pending)} request(s) awaiting your response.")
                for appt in pending:
                    appt_id = appt['id']
                    st.markdown(f"""
                    <div class="card">
                        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:14px;">
                            <div>
                                <div style="color:#64748b; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Patient</div>
                                <div style="color:#e2e8f0; font-weight:600; font-size:14px;">{appt['patient_name']}</div>
                            </div>
                            <div>
                                <div style="color:#64748b; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Email</div>
                                <div style="color:#94a3b8; font-size:13px;">{appt['patient_email']}</div>
                            </div>
                            <div>
                                <div style="color:#64748b; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Date</div>
                                <div style="color:#60a5fa; font-weight:600; font-size:14px;">{appt['date']}</div>
                            </div>
                            <div>
                                <div style="color:#64748b; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Time</div>
                                <div style="color:#60a5fa; font-weight:600; font-size:14px;">{appt['time']}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    col_acc, col_rej = st.columns([1, 2])
                    with col_acc:
                        if st.button("Accept", key=f"accept_{appt_id}", type="primary", use_container_width=True):
                            r = requests.post(f"{BASE_URL}/appointments/{appt_id}/accept")
                            if r.status_code == 200:
                                st.success(f"Accepted! Email sent to {appt['patient_email']}.")
                                st.rerun()
                            else:
                                st.error("Failed to accept.")
                    with col_rej:
                        rejection_reason = st.selectbox("Reason:", [
                            "Not available at this time", "On leave / Holiday",
                            "Slot already booked", "Emergency / Personal reason",
                            "Please reschedule", "Other"
                        ], key=f"reason_{appt_id}")
                        if st.button("Reject", key=f"reject_{appt_id}", use_container_width=True):
                            r = requests.post(f"{BASE_URL}/appointments/{appt_id}/reject",
                                              json={"reason": rejection_reason})
                            if r.status_code == 200:
                                st.warning(f"Rejected. Email sent to {appt['patient_email']}.")
                                st.rerun()
                            else:
                                st.error("Failed to reject.")
        else:
            st.error("Could not connect to the server.")

    with tab2:
        st.markdown("### Update Profile Details")
        st.markdown("<div style='color:#94a3b8; font-size:14px; margin-bottom:20px;'>Fill out the details below to update your public profile visible to patients.</div>", unsafe_allow_html=True)
        
        with st.form("profile_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                exp    = st.number_input("Experience (years)", value=profile.get("experience") or 0, min_value=0)
                med_name = st.text_input("Hospital / Clinic Name", value=profile.get("medical_name") or "", placeholder="e.g. City Hospital")
            with col_b:
                clinic = st.text_input("Full Address (Street, City, Zip)", value=profile.get("clinic_address") or "", placeholder="e.g. 123 Main St, New York")
                contact = st.text_input("Contact Number", value=profile.get("contact_number") or "", placeholder="e.g. +1 234 567 8900")
            bio = st.text_area("Bio / Description", value=profile.get("bio") or "",
                               placeholder="Tell patients about your expertise, degrees, and treatments offered...", height=100)
            if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                payload = {"experience": exp, "medical_name": med_name, "clinic_address": clinic, "contact_number": contact, "bio": bio}
                r = requests.post(f"{BASE_URL}/doctors/profile",
                                  params={"doctor_email": st.session_state.user_email}, json=payload)
                if r.status_code == 200:
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update profile.")


def main_app():
    # Top bar
    col1, col2 = st.columns([8, 1])
    with col1:
        avatar_url = f"https://ui-avatars.com/api/?name={st.session_state.user_name.replace(' ', '+')}&background=0ea5e9&color=fff&size=128&bold=true"
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 16px; padding: 12px 0 20px 0;">
            <img src="{avatar_url}" style="border-radius: 50%; width: 50px; height: 50px; border: 2px solid #0ea5e9;">
            <div>
                <h2 style="margin:0; color:#e2e8f0; font-size:1.5rem; font-weight:700;">
                    Welcome, {st.session_state.user_name}
                </h2>
                <p style="margin:2px 0 0 0; color:#64748b; font-size:13px;">How can MediAssist help you today?</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Logout", type="secondary"):
            st.session_state.token = None
            st.session_state.messages = []
            st.session_state.current_session_id = None
            st.rerun()

    st.divider()

    with st.sidebar:
        st.markdown("### Chat History")
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            st.session_state.current_session_id = None
            st.session_state.messages = []
            st.rerun()
            
        try:
            sessions_res = requests.get(f"{BASE_URL}/chat/sessions", params={"patient_email": st.session_state.user_email})
            chat_sessions = sessions_res.json() if sessions_res.status_code == 200 else []
        except:
            chat_sessions = []
            
        if chat_sessions:
            st.markdown("<div style='max-height: 250px; overflow-y: auto; padding-right: 4px;'>", unsafe_allow_html=True)
            for s in chat_sessions:
                col_btn, col_del = st.columns([8, 2])
                with col_btn:
                    btn_style = "primary" if st.session_state.current_session_id == s["id"] else "secondary"
                    if st.button(f"💬 {s['session_name']}", key=f"session_{s['id']}", use_container_width=True, type=btn_style):
                        st.session_state.current_session_id = s["id"]
                        try:
                            msgs_res = requests.get(f"{BASE_URL}/chat/sessions/{s['id']}/messages")
                            if msgs_res.status_code == 200:
                                st.session_state.messages = msgs_res.json()
                        except:
                            st.session_state.messages = []
                        st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"del_{s['id']}", use_container_width=True, type="secondary"):
                        requests.delete(f"{BASE_URL}/chat/sessions/{s['id']}")
                        if st.session_state.current_session_id == s["id"]:
                            st.session_state.current_session_id = None
                            st.session_state.messages = []
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.caption("No past chats.")
            
        st.divider()
        st.markdown("### Doctors")
        show_docs = st.toggle("Show Doctor Directory")
        if show_docs:
            res = requests.get(f"{BASE_URL}/doctors")
            if res.status_code == 200:
                docs = res.json()
                if docs:
                    # Extract unique specializations for the dropdown
                    all_specs = sorted(list(set(d['specialization'] for d in docs)))
                    selected_spec = st.selectbox("Filter by Specialization", ["All"] + all_specs)
                    
                    # Group doctors by specialization
                    grouped_docs = {}
                    for d in docs:
                        spec = d['specialization']
                        if selected_spec != "All" and spec != selected_spec:
                            continue
                        if spec not in grouped_docs:
                            grouped_docs[spec] = []
                        grouped_docs[spec].append(d)
                    
                    if not grouped_docs:
                        st.caption("No doctors found for this specialization.")
                    
                    for spec, d_list in grouped_docs.items():
                        st.markdown(f"<div style='color:#e2e8f0; font-size:13px; font-weight:600; margin:14px 0 8px 0; border-bottom:1px solid #1e2a3a; padding-bottom:4px;'>🩺 {spec}</div>", unsafe_allow_html=True)
                        for d in d_list:
                            exp_text = f"{d.get('experience')} yrs" if d.get('experience') else "N/A"
                            doc_avatar = f"https://ui-avatars.com/api/?name={d['name'].replace(' ', '+')}&background=2563eb&color=fff&size=64&bold=true"
                            st.markdown(f"""
                            <div class="card" style="padding:12px; margin-bottom:8px; display: flex; gap: 12px; align-items: flex-start;">
                                <img src="{doc_avatar}" style="border-radius: 8px; width: 44px; height: 44px; border: 1px solid #1e2a3a;">
                                <div style="flex-grow: 1;">
                                    <div style="color:#e2e8f0; font-weight:600; font-size:14px;">Dr. {d['name']}</div>
                                    <div style="color:#2563eb; font-size:11px; font-weight:600; margin-bottom:6px;">{d.get('medical_name') or 'Independent Clinic'}</div>
                                    <div style="color:#64748b; font-size:12px;">{exp_text} &nbsp;|&nbsp; {d.get('contact_number') or 'N/A'}</div>
                                    <div style="color:#64748b; font-size:11px; margin-top:3px; line-height:1.4;">{d.get('clinic_address') or 'N/A'}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.caption("No doctors available.")
            else:
                st.error("Failed to fetch doctors.")

        st.divider()
        st.markdown("### Medical Report")
        report_file = st.file_uploader("Upload PDF or Image", type=["pdf", "jpg", "jpeg", "png"],
                                       label_visibility="collapsed")
        if st.button("Summarize Report", use_container_width=True) and report_file:
            with st.spinner("Analyzing report..."):
                files = {"file": (report_file.name, report_file, report_file.type)}
                res = requests.post(f"{BASE_URL}/reports/upload", files=files)
            if res.status_code == 200:
                summary = res.json()["summary"]
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"*(OCR Agent)*\n\n**Report Summary:**\n{summary}"
                })
                st.rerun()
            else:
                st.error("Error summarizing report.")

    if not st.session_state.messages:
        cols = st.columns(4)
        cards = [
            ("Symptom Check", "Describe your symptoms"),
            ("Medicines",     "Drug information"),
            ("Appointments",  "Book a doctor"),
            ("Reports",       "Upload & analyze"),
        ]
        icons = ["&#x1FA7A;", "&#x1F48A;", "&#x1F4C5;", "&#x1F4CB;"]
        for col, icon, (title, desc) in zip(cols, icons, cards):
            col.markdown(f"""
            <div class="card" style="text-align:center; padding:20px 14px;">
                <div style="font-size:1.8rem; margin-bottom:8px;">{icon}</div>
                <div style="color:#e2e8f0; font-weight:600; font-size:14px;">{title}</div>
                <div style="color:#64748b; font-size:12px; margin-top:4px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Hello **{st.session_state.user_name}**!\n\nI'm your AI health assistant. How can I help you today?\n\n- Describe your symptoms for AI diagnosis\n- Ask about medicines or treatments\n- Book a doctor appointment\n- Upload a medical report for analysis\n- Use voice assistant from the sidebar"
        })

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "content" in message:
                st.markdown(message["content"])
            if "image" in message:
                try: st.image(message["image"])
                except: pass

    if user_input := st.chat_input("Ask me anything about your health..."):
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            res = requests.post(f"{BASE_URL}/chat", json={
                "message": user_input,
                "user_name": st.session_state.user_name,
                "user_email": st.session_state.user_email,
                "chat_history": st.session_state.messages,
                "session_id": st.session_state.current_session_id
            })
        if res.status_code == 200:
            data = res.json()
            st.session_state.current_session_id = data.get("session_id")
            full_res = f"*(Answered by: {data['agent'].upper()} AGENT)*\n\n{data['response']}"
            process_chat_response(full_res)
        else:
            st.error("Error connecting to Chat Agent.")

    # --- CHATGPT STYLE INPUT & MIC ---
    if "mic_key" not in st.session_state:
        st.session_state["mic_key"] = "mic_0"

    st.markdown("""
    <style>
    /* ChatGPT Style Chat Input */
    [data-testid="stChatInput"] {
        padding-bottom: 24px !important;
    }
    [data-testid="stChatInput"] > div {
        background-color: #2f2f2f !important;
        border-radius: 30px !important;
        border: none !important;
        padding-right: 50px !important;
        padding-left: 10px !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: white !important;
    }
    
    /* Make the submit arrow look like ChatGPT (White circle) */
    [data-testid="stChatInput"] button {
        background-color: white !important;
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        margin-right: 5px !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }
    [data-testid="stChatInput"] button svg {
        fill: black !important;
        color: black !important;
    }
    </style>
    
    <script>
    // Robust JS to find the mic recorder and float it next to the chat input arrow
    const setMicPos = () => {
        try {
            const iframes = window.parent.document.querySelectorAll('iframe');
            let micContainer = null;
            for (let i = 0; i < iframes.length; i++) {
                if (iframes[i].src && iframes[i].src.includes('mic_recorder')) {
                    micContainer = iframes[i].closest('div[data-testid="stElementContainer"]');
                    break;
                }
            }
            if (micContainer) {
                micContainer.style.setProperty('position', 'fixed', 'important');
                micContainer.style.setProperty('bottom', '37px', 'important');
                micContainer.style.setProperty('z-index', '999999', 'important');
                micContainer.style.setProperty('width', '45px', 'important');
                micContainer.style.setProperty('height', '45px', 'important');
                micContainer.style.setProperty('background', 'transparent', 'important');
                
                if (window.parent.innerWidth >= 750) {
                    micContainer.style.setProperty('left', '50%', 'important');
                    micContainer.style.setProperty('margin-left', '295px', 'important');
                } else {
                    micContainer.style.setProperty('right', '60px', 'important');
                    micContainer.style.setProperty('left', 'auto', 'important');
                }
            }
        } catch(e) {}
    };
    setInterval(setMicPos, 500);
    window.parent.addEventListener('resize', setMicPos);
    </script>
    """, unsafe_allow_html=True)
    
    audio_data = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", just_once=True, key=st.session_state["mic_key"])
    
    if audio_data and 'bytes' in audio_data:
        with st.spinner("Processing audio..."):
            files = {"file": ("voice_note.wav", audio_data['bytes'], "audio/wav")}
            try:
                res = requests.post(f"{BASE_URL}/voice/upload", files=files, timeout=15)
                if res.status_code == 200:
                    text_result = res.json()["text"]
                    st.session_state.messages.append({"role": "user", "content": f"🎤 Voice: {text_result}"})
                    
                    with st.spinner("Thinking..."):
                        chat_res = requests.post(f"{BASE_URL}/chat", json={
                            "message": text_result,
                            "user_name": st.session_state.user_name,
                            "user_email": st.session_state.user_email,
                            "chat_history": st.session_state.messages,
                            "session_id": st.session_state.current_session_id
                        }, timeout=30)
                    
                    if chat_res.status_code == 200:
                        data = chat_res.json()
                        st.session_state.current_session_id = data.get("session_id")
                        full_res = f"*(Answered by: {data['agent'].upper()} AGENT)*\n\n{data['response']}"
                        process_chat_response(full_res)
                    else:
                        st.error("Error getting response from Chat Agent.")
                else:
                    st.error("Error processing audio.")
            except Exception as e:
                st.error("Connection timed out or failed. Please try again.")
            
            # Reset mic state to prevent infinite loop
            import time
            st.session_state["mic_key"] = f"mic_{int(time.time())}"
            st.rerun()

if not st.session_state.token:
    auth_screen()
elif st.session_state.role == "doctor":
    doctor_dashboard()
else:
    main_app()