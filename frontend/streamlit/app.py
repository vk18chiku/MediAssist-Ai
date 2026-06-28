# frontend/streamlit/app.py
import streamlit as st
import requests
import os
import base64
import platform
import time

st.set_page_config(page_title="MediAssist AI", page_icon="🧠", layout="wide")

# --- API Configuration ---
if platform.system() == "Windows":
    BASE_URL = "http://localhost:8000"
else:
    BASE_URL = os.environ.get("BACKEND_URL", "http://mediassist_backend:8000")

# --- Session State Init ---
defaults = {
    "token": None, "user_name": None, "user_email": None, "role": None,
    "messages": [], "forgot_password_mode": False, "otp_sent": False,
    "reset_email": "", "signup_otp_sent": False, "current_session_id": None,
}
for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ════════════════════════════════════════════════════════════════
# ULTRA-PREMIUM CSS — Advanced AI Platform UI
# ════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
    --bg-void: #05060b;
    --bg-deep: #0a0d14;
    --bg-surface: #0f1219;
    --bg-elevated: #151923;
    --bg-card: rgba(15, 18, 25, 0.80);
    --bg-card-hover: rgba(21, 25, 35, 0.95);
    --border-dim: rgba(255, 255, 255, 0.04);
    --border-subtle: rgba(255, 255, 255, 0.07);
    --border-glow: rgba(56, 189, 248, 0.4);
    --cyan: #38bdf8;
    --cyan-dim: #0ea5e9;
    --cyan-glow: rgba(56, 189, 248, 0.20);
    --cyan-deep-glow: rgba(56, 189, 248, 0.08);
    --violet: #a78bfa;
    --violet-dim: #8b5cf6;
    --violet-glow: rgba(167, 139, 250, 0.20);
    --emerald: #34d399;
    --emerald-glow: rgba(52, 211, 153, 0.25);
    --amber: #fbbf24;
    --rose: #fb7185;
    --text-white: #f0f4f8;
    --text-secondary: #7c8da6;
    --text-muted: #4a5568;
    --gradient-hero: linear-gradient(135deg, #38bdf8 0%, #818cf8 40%, #a78bfa 70%, #c084fc 100%);
    --gradient-btn: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #8b5cf6 100%);
    --gradient-card: linear-gradient(160deg, rgba(56,189,248,0.06) 0%, rgba(139,92,246,0.04) 100%);
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(56, 189, 248, 0.2); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(56, 189, 248, 0.35); }

/* ── Main Background with Mesh ── */
.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 20% 20%, rgba(56, 189, 248, 0.06) 0%, transparent 50%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 50%),
        radial-gradient(ellipse 50% 50% at 50% 0%, rgba(56, 189, 248, 0.03) 0%, transparent 40%),
        var(--bg-void) !important;
    min-height: 100vh;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-deep) 0%, var(--bg-void) 100%) !important;
    border-right: 1px solid var(--border-dim) !important;
    backdrop-filter: blur(20px) !important;
}
[data-testid="stSidebar"] * { color: var(--text-secondary); }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--text-white) !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    opacity: 0.8;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    color: var(--text-white) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px var(--cyan-glow), 0 0 20px var(--cyan-deep-glow) !important;
    background: rgba(56, 189, 248, 0.03) !important;
}
.stTextInput label, .stTextArea label, .stNumberInput label,
.stSelectbox label, .stFileUploader label {
    color: var(--text-muted) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* ── Buttons ── */
.stButton > button, .stFormSubmitButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: none !important;
    padding: 0.6rem 1.4rem !important;
    letter-spacing: 0.02em !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button[kind="primary"], .stFormSubmitButton > button {
    background: var(--gradient-btn) !important;
    background-size: 200% 200% !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(14, 165, 233, 0.25), 0 0 30px rgba(99, 102, 241, 0.1) !important;
}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(14, 165, 233, 0.35), 0 0 40px rgba(99, 102, 241, 0.15) !important;
    background-position: right center !important;
    filter: brightness(1.1) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.04) !important;
    color: var(--text-white) !important;
    border: 1px solid var(--border-subtle) !important;
    backdrop-filter: blur(10px) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: var(--cyan-glow) !important;
    box-shadow: 0 0 15px var(--cyan-deep-glow) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.02) !important;
    border-radius: 14px !important;
    padding: 5px !important;
    gap: 4px !important;
    border: 1px solid var(--border-dim) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 11px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: var(--text-muted) !important;
    padding: 10px 24px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--gradient-btn) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2) !important;
}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    background: var(--gradient-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 18px !important;
    margin-bottom: 14px !important;
    padding: 18px !important;
    backdrop-filter: blur(12px) !important;
    transition: border-color 0.3s ease !important;
}
[data-testid="stChatMessage"]:hover {
    border-color: rgba(56, 189, 248, 0.15) !important;
}
[data-testid="stChatMessage"] .stMarkdown p {
    font-size: 14px !important;
    line-height: 1.75 !important;
    color: var(--text-white) !important;
}

/* ── Chat Input ── */
[data-testid="stChatInput"] > div {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 16px !important;
    transition: border-color 0.3s ease !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 20px var(--cyan-deep-glow) !important;
}
[data-testid="stChatInput"] textarea {
    color: var(--text-white) !important;
}
[data-testid="stChatInput"] button {
    background: var(--gradient-btn) !important;
    border-radius: 10px !important;
}

/* ── Form ── */
[data-testid="stForm"] {
    background: linear-gradient(160deg, rgba(56,189,248,0.03) 0%, rgba(139,92,246,0.02) 100%) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 20px !important;
    padding: 2.5rem !important;
    backdrop-filter: blur(16px) !important;
    box-shadow: 0 20px 50px -20px rgba(0, 0, 0, 0.5) !important;
}

/* ═══ Custom Components ═══ */

/* Auth Header */
.ai-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
    position: relative;
}
.ai-header::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(56,189,248,0.08) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}
.ai-header h1 {
    font-size: 2.8rem;
    font-weight: 900;
    margin: 0;
    letter-spacing: -0.04em;
    position: relative; z-index: 1;
}
.ai-header h1 .gradient-text {
    background: var(--gradient-hero);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    background-size: 300% 300%;
    animation: gradientShift 4s ease infinite;
}
.ai-header .subtitle {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-top: 10px;
    font-weight: 400;
    letter-spacing: 0.02em;
    position: relative; z-index: 1;
}

/* Agent Badge */
.agent-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 189, 248, 0.08);
    color: var(--cyan);
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border: 1px solid rgba(56, 189, 248, 0.15);
    transition: all 0.3s ease;
}
.agent-badge:hover {
    background: rgba(56, 189, 248, 0.15);
    border-color: rgba(56, 189, 248, 0.3);
    box-shadow: 0 0 12px var(--cyan-deep-glow);
}
.agent-badge-violet {
    background: rgba(167, 139, 250, 0.08);
    color: var(--violet);
    border-color: rgba(167, 139, 250, 0.15);
}
.agent-badge-emerald {
    background: rgba(52, 211, 153, 0.08);
    color: var(--emerald);
    border-color: rgba(52, 211, 153, 0.15);
}
.agent-badge-amber {
    background: rgba(251, 191, 36, 0.08);
    color: var(--amber);
    border-color: rgba(251, 191, 36, 0.15);
}

/* Status Indicators */
.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
    animation: statusPulse 2s ease-in-out infinite;
}
.status-online { background: var(--emerald); box-shadow: 0 0 8px var(--emerald-glow); }
.status-processing { background: var(--amber); box-shadow: 0 0 8px rgba(251,191,36,0.3); }

/* Metric Cards (Welcome Screen) */
.metric-card {
    background: var(--gradient-card);
    border: 1px solid var(--border-subtle);
    border-radius: 18px;
    padding: 24px;
    text-align: center;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    cursor: default;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--gradient-hero);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.metric-card:hover {
    border-color: rgba(56, 189, 248, 0.2);
    transform: translateY(-4px);
    box-shadow: 0 16px 40px -12px rgba(56, 189, 248, 0.12);
}
.metric-card:hover::before { opacity: 1; }
.metric-card .metric-icon {
    font-size: 2rem;
    margin-bottom: 14px;
    filter: drop-shadow(0 0 12px var(--cyan-glow));
}
.metric-card .metric-title {
    font-size: 14px;
    font-weight: 700;
    color: var(--text-white);
    margin-bottom: 4px;
}
.metric-card .metric-desc {
    font-size: 11px;
    color: var(--text-secondary);
    line-height: 1.4;
}

/* Profile Card */
.profile-card {
    background: var(--gradient-card);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 28px;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
}
.profile-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--gradient-hero);
}

/* Appointment Card */
.appt-card {
    background: var(--gradient-card);
    border: 1px solid var(--border-subtle);
    border-left: 3px solid var(--cyan);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    transition: all 0.25s ease;
}
.appt-card:hover {
    border-left-color: var(--violet);
    transform: translateX(4px);
    box-shadow: 0 4px 20px rgba(56, 189, 248, 0.06);
}

/* Doctor Card */
.doc-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border-dim);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 8px;
    transition: all 0.25s ease;
}
.doc-card:hover {
    background: rgba(56, 189, 248, 0.04);
    border-color: rgba(56, 189, 248, 0.15);
}

/* System Info Bar */
.system-info {
    background: linear-gradient(135deg, rgba(56,189,248,0.06) 0%, rgba(139,92,246,0.04) 100%);
    border: 1px solid rgba(56, 189, 248, 0.12);
    border-radius: 14px;
    padding: 14px 20px;
    font-size: 12px;
    color: var(--text-secondary);
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 20px;
    backdrop-filter: blur(8px);
}

/* Pipeline Visualization */
.pipeline-flow {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin: 20px 0 10px 0;
    flex-wrap: wrap;
}
.pipeline-node {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 8px 16px;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-secondary);
    transition: all 0.3s ease;
}
.pipeline-node:hover {
    border-color: var(--cyan);
    color: var(--cyan);
    box-shadow: 0 0 15px var(--cyan-deep-glow);
}
.pipeline-node.active {
    border-color: var(--cyan);
    color: var(--cyan);
    background: rgba(56, 189, 248, 0.08);
}
.pipeline-arrow {
    color: var(--text-muted);
    font-size: 14px;
    padding: 0 6px;
    opacity: 0.5;
}

hr { border-color: var(--border-dim) !important; }

/* ── Animations ── */
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
@keyframes statusPulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.6; transform: scale(0.85); } }
@keyframes glowPulse { 0%, 100% { box-shadow: 0 0 5px var(--cyan-deep-glow); } 50% { box-shadow: 0 0 20px var(--cyan-glow); } }
.fade-in { animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# AUTH SCREEN
# ════════════════════════════════════════════════════════════════
def auth_screen():
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1.2, 1.6, 1.2])
    with col_m:
        st.markdown("""
        <div class="ai-header fade-in">
            <div style="margin-bottom:20px;">
                <span style="font-size:3.5rem; filter: drop-shadow(0 0 20px rgba(56,189,248,0.35));">🧠</span>
            </div>
            <h1>Medi<span class="gradient-text">Assist AI</span></h1>
            <p class="subtitle">Multi-Agent Healthcare Intelligence Platform</p>
            <div class="pipeline-flow" style="margin-top:20px;">
                <span class="pipeline-node active">🧠 Supervisor</span>
                <span class="pipeline-arrow">→</span>
                <span class="pipeline-node">🔬 Symptom</span>
                <span class="pipeline-arrow">|</span>
                <span class="pipeline-node">💊 Medicine</span>
                <span class="pipeline-arrow">|</span>
                <span class="pipeline-node">📚 RAG</span>
                <span class="pipeline-arrow">|</span>
                <span class="pipeline-node">📅 Booking</span>
            </div>
            <div style="margin-top:14px; display:flex; justify-content:center; gap:8px; flex-wrap:wrap;">
                <span class="agent-badge">🔬 Symptom Agent</span>
                <span class="agent-badge agent-badge-violet">💊 Medicine Agent</span>
                <span class="agent-badge agent-badge-emerald">📚 RAG Agent</span>
                <span class="agent-badge agent-badge-amber">📅 Appointment Agent</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.forgot_password_mode:
            st.markdown("#### 🔐 Reset Your Password")
            if not st.session_state.otp_sent:
                with st.form("forgot_password_form"):
                    st.info("Enter your registered email. We will send you a 6-digit OTP.")
                    reset_email_input = st.text_input("Email", placeholder="you@example.com")
                    if st.form_submit_button("Send OTP", type="primary"):
                        if reset_email_input:
                            with st.spinner("Sending OTP..."):
                                res = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": reset_email_input})
                            if res.status_code == 200:
                                st.session_state.otp_sent = True
                                st.session_state.reset_email = reset_email_input
                                st.success("OTP sent! Check your email.")
                                st.rerun()
                            else:
                                st.error("Failed to send OTP.")
                        else:
                            st.error("Please enter your email.")
            else:
                with st.form("reset_password_form"):
                    st.info(f"Enter the OTP sent to {st.session_state.reset_email}")
                    otp_input = st.text_input("6-digit OTP")
                    new_password_input = st.text_input("New Password", type="password")
                    if st.form_submit_button("Reset Password", type="primary"):
                        if otp_input and new_password_input:
                            with st.spinner("Resetting..."):
                                res = requests.post(f"{BASE_URL}/auth/reset-password", json={
                                    "email": st.session_state.reset_email,
                                    "otp": otp_input,
                                    "new_password": new_password_input
                                })
                            if res.status_code == 200:
                                st.success("Password reset! You can now login.")
                                st.session_state.forgot_password_mode = False
                                st.session_state.otp_sent = False
                                st.rerun()
                            else:
                                try: st.error(res.json().get("detail", "Failed to reset."))
                                except: st.error("Server error.")
                        else:
                            st.error("Please fill in all fields.")

            if st.button("← Back to Login"):
                st.session_state.forgot_password_mode = False
                st.session_state.otp_sent = False
                st.rerun()
            return

        tab1, tab2 = st.tabs(["Sign In", "Create Account"])

        with tab1:
            with st.form("login_form"):
                log_email = st.text_input("Email", placeholder="you@example.com")
                log_password = st.text_input("Password", type="password", placeholder="Enter your password")
                st.markdown("<br>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("Sign In", type="primary")
                if submit_login:
                    with st.spinner("Authenticating..."):
                        try:
                            res = requests.post(f"{BASE_URL}/auth/login", json={"email": log_email, "password": log_password})
                            if res.status_code == 200:
                                data = res.json()
                                st.session_state.token = data["access_token"]
                                st.session_state.user_name = data["name"]
                                st.session_state.user_email = log_email
                                st.session_state.role = data["role"]
                                st.success(f"Welcome back, {data['name']}!")
                                st.rerun()
                            else:
                                try: st.error(res.json().get("detail", "Invalid credentials."))
                                except: st.error("Server error. Please try again.")
                        except requests.exceptions.ConnectionError:
                            st.error("⚠️ Backend server is not running. Please start the backend first.")

            if st.button("Forgot Password?"):
                st.session_state.forgot_password_mode = True
                st.session_state.otp_sent = False
                st.rerun()

        with tab2:
            reg_name = st.text_input("Full Name", key="reg_name", placeholder="John Doe", disabled=st.session_state.signup_otp_sent)
            reg_email = st.text_input("Email", key="reg_email", placeholder="you@example.com", disabled=st.session_state.signup_otp_sent)
            reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Min 6 characters", disabled=st.session_state.signup_otp_sent)
            reg_role = st.selectbox("I am a:", ["patient", "doctor"], key="reg_role", disabled=st.session_state.signup_otp_sent)
            reg_spec = None
            if reg_role == "doctor":
                reg_spec = st.selectbox("Specialization:", [
                    "General Physician", "Neurologist", "Cardiologist",
                    "Dermatologist", "Pediatrician", "Orthopedic"
                ], key="reg_spec", disabled=st.session_state.signup_otp_sent)
            st.markdown("<br>", unsafe_allow_html=True)

            if not st.session_state.signup_otp_sent:
                submit_signup = st.button("Send OTP to Email", type="primary")
                if submit_signup:
                    if reg_name and reg_email and reg_password:
                        with st.spinner("Sending OTP..."):
                            try:
                                res = requests.post(f"{BASE_URL}/auth/signup-send-otp", json={"email": reg_email})
                                if res.status_code == 200:
                                    st.session_state.signup_otp_sent = True
                                    st.success("OTP sent!")
                                    st.rerun()
                                else:
                                    try: st.error(res.json().get("detail", "Could not send OTP."))
                                    except: st.error("Server error.")
                            except requests.exceptions.ConnectionError:
                                st.error("⚠️ Backend server is not running.")
                    else:
                        st.error("Please fill all fields.")
            else:
                st.info(f"OTP sent to {reg_email}")
                signup_otp = st.text_input("Enter 6-digit OTP", key="signup_otp")
                verify_signup = st.button("Verify & Create Account", type="primary")
                if verify_signup:
                    if signup_otp:
                        payload = {"name": reg_name, "email": reg_email, "password": reg_password, "role": reg_role, "specialization": reg_spec, "otp": signup_otp}
                        with st.spinner("Creating account..."):
                            res = requests.post(f"{BASE_URL}/auth/signup", json=payload)
                        if res.status_code == 201:
                            data = res.json()
                            st.session_state.token = data["access_token"]
                            st.session_state.user_name = data["name"]
                            st.session_state.user_email = reg_email
                            st.session_state.role = data["role"]
                            st.session_state.signup_otp_sent = False
                            st.success(f"Welcome, {data['name']}!")
                            st.rerun()
                        else:
                            try: st.error(res.json().get("detail", "Signup failed."))
                            except: st.error("Server error.")
                    else:
                        st.error("Please enter the OTP.")

                if st.button("← Change Email"):
                    st.session_state.signup_otp_sent = False
                    st.rerun()


# ════════════════════════════════════════════════════════════════
# CHAT RESPONSE HANDLER
# ════════════════════════════════════════════════════════════════
def process_chat_response(full_res):
    if "[TICKET_IMAGE:" in full_res:
        text_part = full_res.split("[TICKET_IMAGE:")[0].strip()
        img_path = full_res.split("[TICKET_IMAGE:")[1].split("]")[0]
        st.chat_message("assistant").markdown(text_part)
        try: st.image(img_path)
        except: pass
        st.session_state.messages.append({"role": "assistant", "content": text_part, "image": img_path})
    else:
        st.chat_message("assistant").markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})


# ════════════════════════════════════════════════════════════════
# DOCTOR DASHBOARD
# ════════════════════════════════════════════════════════════════
def doctor_dashboard():
    res = requests.get(f"{BASE_URL}/doctors/profile", params={"doctor_email": st.session_state.user_email})
    profile = res.json() if res.status_code == 200 else {}

    # Header
    col1, col2 = st.columns([8, 1])
    with col1:
        avatar_url = f"https://ui-avatars.com/api/?name={profile.get('name', st.session_state.user_name).replace(' ', '+')}&background=6366f1&color=fff&size=128&bold=true&format=svg"
        st.markdown(f"""
        <div class="profile-card fade-in">
            <div style="display:flex; gap:20px; align-items:flex-start;">
                <img src="{avatar_url}" style="border-radius:14px; width:80px; height:80px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                <div style="flex-grow:1;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <h2 style="margin:0 0 6px 0; color:var(--text-primary); font-size:1.5rem; font-weight:800; letter-spacing:-0.02em;">
                                Dr. {profile.get('name', st.session_state.user_name)}
                            </h2>
                            <span class="agent-badge" style="background:rgba(16,185,129,0.1); color:#10b981; border-color:rgba(16,185,129,0.2);">
                                {profile.get('specialization', 'Doctor')}
                            </span>
                        </div>
                        <div style="text-align:right;">
                            <div style="color:var(--text-primary); font-weight:600; font-size:14px;">{profile.get('medical_name') or 'Clinic Not Set'}</div>
                            <div style="color:var(--text-secondary); font-size:12px; margin-top:3px;">📍 {profile.get('clinic_address') or 'N/A'}</div>
                            <div style="color:var(--text-secondary); font-size:12px; margin-top:2px;">📞 {profile.get('contact_number') or 'N/A'}</div>
                        </div>
                    </div>
                    <div style="margin-top:16px; color:var(--text-secondary); font-size:13px; line-height:1.6; background:rgba(255,255,255,0.03); padding:12px 16px; border-radius:10px; border:1px solid var(--border-subtle);">
                        {profile.get('bio') or '<em>No bio provided. Update your profile below.</em>'}
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
    tab1, tab2 = st.tabs(["📋 Dashboard", "⚙️ My Profile"])

    with tab1:
        with st.sidebar:
            st.markdown("### ✅ Accepted")
            if st.button("↻ Refresh", key="refresh_accepted"):
                st.rerun()
            res = requests.get(f"{BASE_URL}/appointments/accepted",
                               params={"doctor_email": st.session_state.user_email})
            if res.status_code == 200:
                accepted = res.json()
                if accepted:
                    for appt in accepted:
                        st.markdown(f"""
                        <div class="appt-card" style="border-left-color: var(--accent-emerald);">
                            <div style="color:var(--text-primary); font-weight:600; font-size:13px; margin-bottom:4px;">{appt['patient_name']}</div>
                            <div style="color:var(--text-secondary); font-size:12px;">📅 {appt['date']} · ⏰ {appt['time']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No upcoming appointments.")
            else:
                st.error("Could not load.")

        st.markdown("### Pending Requests")
        res = requests.get(f"{BASE_URL}/appointments/pending",
                           params={"doctor_email": st.session_state.user_email})
        if res.status_code == 200:
            pending = res.json()
            if not pending:
                st.markdown("""
                <div class="system-info">
                    <span class="status-dot status-online"></span>
                    All caught up — no pending requests.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="system-info">
                    <span class="status-dot status-processing"></span>
                    {len(pending)} request(s) awaiting your response
                </div>
                """, unsafe_allow_html=True)
                for appt in pending:
                    appt_id = appt['id']
                    st.markdown(f"""
                    <div class="appt-card fade-in">
                        <div style="display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:12px;">
                            <div>
                                <div style="color:var(--text-muted); font-size:10px; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:3px;">Patient</div>
                                <div style="color:var(--text-primary); font-weight:600; font-size:13px;">{appt['patient_name']}</div>
                            </div>
                            <div>
                                <div style="color:var(--text-muted); font-size:10px; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:3px;">Email</div>
                                <div style="color:var(--text-secondary); font-size:12px;">{appt['patient_email']}</div>
                            </div>
                            <div>
                                <div style="color:var(--text-muted); font-size:10px; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:3px;">Date</div>
                                <div style="color:var(--accent-light); font-weight:600; font-size:13px;">{appt['date']}</div>
                            </div>
                            <div>
                                <div style="color:var(--text-muted); font-size:10px; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:3px;">Time</div>
                                <div style="color:var(--accent-light); font-weight:600; font-size:13px;">{appt['time']}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    col_acc, col_rej = st.columns([1, 2])
                    with col_acc:
                        if st.button("✓ Accept", key=f"accept_{appt_id}", type="primary"):
                            r = requests.post(f"{BASE_URL}/appointments/{appt_id}/accept")
                            if r.status_code == 200:
                                st.success(f"Accepted! Email sent to {appt['patient_email']}.")
                                st.rerun()
                            else:
                                st.error("Failed.")
                    with col_rej:
                        rejection_reason = st.selectbox("Reason:", [
                            "Not available at this time", "On leave / Holiday",
                            "Slot already booked", "Emergency / Personal reason",
                            "Please reschedule", "Other"
                        ], key=f"reason_{appt_id}")
                        if st.button("✗ Reject", key=f"reject_{appt_id}"):
                            r = requests.post(f"{BASE_URL}/appointments/{appt_id}/reject",
                                              json={"reason": rejection_reason})
                            if r.status_code == 200:
                                st.warning(f"Rejected. Email sent to {appt['patient_email']}.")
                                st.rerun()
                            else:
                                st.error("Failed.")
        else:
            st.error("Could not connect to server.")

    with tab2:
        st.markdown("### Update Profile")
        st.markdown("<div style='color:var(--text-secondary); font-size:13px; margin-bottom:16px;'>Your public profile visible to patients.</div>", unsafe_allow_html=True)

        with st.form("profile_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                exp = st.number_input("Experience (years)", value=profile.get("experience") or 0, min_value=0)
                med_name = st.text_input("Hospital / Clinic", value=profile.get("medical_name") or "", placeholder="e.g. City Hospital")
            with col_b:
                clinic = st.text_input("Address", value=profile.get("clinic_address") or "", placeholder="123 Main St, City")
                contact = st.text_input("Contact Number", value=profile.get("contact_number") or "", placeholder="+1 234 567 8900")
            bio = st.text_area("Bio / Description", value=profile.get("bio") or "",
                               placeholder="Your expertise, degrees, treatments...", height=100)
            if st.form_submit_button("Save Changes", type="primary"):
                payload = {"experience": exp, "medical_name": med_name, "clinic_address": clinic, "contact_number": contact, "bio": bio}
                r = requests.post(f"{BASE_URL}/doctors/profile",
                                  params={"doctor_email": st.session_state.user_email}, json=payload)
                if r.status_code == 200:
                    st.success("Profile updated!")
                    st.rerun()
                else:
                    st.error("Failed to update.")


# ════════════════════════════════════════════════════════════════
# PATIENT DASHBOARD (Main App)
# ════════════════════════════════════════════════════════════════
def main_app():
    # System status bar
    st.markdown("""
    <div class="system-info fade-in">
        <span class="status-dot status-online"></span>
        <span><strong>MediAssist AI</strong> — Multi-Agent System Active</span>
        <span style="margin-left:auto; font-size:11px; color:var(--text-muted);">LangGraph Supervisor • GPT-3.5 Turbo</span>
    </div>
    """, unsafe_allow_html=True)

    # Top bar
    col1, col2 = st.columns([8, 1])
    with col1:
        avatar_url = f"https://ui-avatars.com/api/?name={st.session_state.user_name.replace(' ', '+')}&background=6366f1&color=fff&size=128&bold=true&format=svg"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:14px; padding:8px 0 20px 0; animation: fadeIn 0.4s ease-out;">
            <img src="{avatar_url}" style="border-radius:12px; width:48px; height:48px; border:2px solid var(--accent); box-shadow: 0 0 12px var(--accent-glow);">
            <div>
                <h2 style="margin:0; color:var(--text-primary); font-size:1.3rem; font-weight:800; letter-spacing:-0.02em;">
                    {st.session_state.user_name}
                </h2>
                <p style="margin:0; color:var(--text-secondary); font-size:12px;">Patient Dashboard</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", type="secondary"):
            st.session_state.token = None
            st.session_state.messages = []
            st.session_state.current_session_id = None
            st.rerun()

    st.divider()

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("### 💬 Sessions")
        if st.button("＋ New Chat", type="primary"):
            st.session_state.current_session_id = None
            st.session_state.messages = []
            st.rerun()

        try:
            sessions_res = requests.get(f"{BASE_URL}/chat/sessions", params={"patient_email": st.session_state.user_email})
            chat_sessions = sessions_res.json() if sessions_res.status_code == 200 else []
        except:
            chat_sessions = []

        if chat_sessions:
            for s in chat_sessions:
                col_btn, col_del = st.columns([8, 2])
                with col_btn:
                    btn_style = "primary" if st.session_state.current_session_id == s["id"] else "secondary"
                    if st.button(f"💬 {s['session_name']}", key=f"session_{s['id']}", type=btn_style):
                        st.session_state.current_session_id = s["id"]
                        try:
                            msgs_res = requests.get(f"{BASE_URL}/chat/sessions/{s['id']}/messages")
                            if msgs_res.status_code == 200:
                                st.session_state.messages = msgs_res.json()
                        except:
                            st.session_state.messages = []
                        st.rerun()
                with col_del:
                    if st.button("🗑", key=f"del_{s['id']}", type="secondary"):
                        requests.delete(f"{BASE_URL}/chat/sessions/{s['id']}")
                        if st.session_state.current_session_id == s["id"]:
                            st.session_state.current_session_id = None
                            st.session_state.messages = []
                        st.rerun()
        else:
            st.caption("No past sessions.")

        st.divider()
        st.markdown("### 🏥 Doctors")
        show_docs = st.toggle("Show Directory")
        if show_docs:
            try:
                res = requests.get(f"{BASE_URL}/doctors")
                if res.status_code == 200:
                    docs = res.json()
                    if docs:
                        all_specs = sorted(list(set(d['specialization'] for d in docs)))
                        selected_spec = st.selectbox("Filter", ["All"] + all_specs)

                        for d in docs:
                            if selected_spec != "All" and d['specialization'] != selected_spec:
                                continue
                            doc_avatar = f"https://ui-avatars.com/api/?name={d['name'].replace(' ', '+')}&background=6366f1&color=fff&size=64&bold=true&format=svg"
                            exp_text = f"{d.get('experience')} yrs" if d.get('experience') else "N/A"
                            st.markdown(f"""
                            <div class="doc-card">
                                <div style="display:flex; gap:10px; align-items:center;">
                                    <img src="{doc_avatar}" style="border-radius:8px; width:36px; height:36px;">
                                    <div>
                                        <div style="color:var(--text-primary); font-weight:600; font-size:13px;">Dr. {d['name']}</div>
                                        <div style="color:var(--accent-light); font-size:11px; font-weight:600;">{d['specialization']}</div>
                                        <div style="color:var(--text-muted); font-size:11px;">{exp_text} · {d.get('medical_name') or 'Independent'}</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption("No doctors available.")
                else:
                    st.error("Failed to fetch.")
            except:
                st.error("Connection error.")

        st.divider()
        st.markdown("### 📄 Report Analysis")
        report_file = st.file_uploader("Upload PDF or Image", type=["pdf", "jpg", "jpeg", "png"],
                                       label_visibility="collapsed")
        if st.button("Analyze Report") and report_file:
            with st.spinner("🔬 OCR Agent processing..."):
                files = {"file": (report_file.name, report_file, report_file.type)}
                res = requests.post(f"{BASE_URL}/reports/upload", files=files)
            if res.status_code == 200:
                summary = res.json()["summary"]
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"*🔬 Processed by: OCR AGENT*\n\n**Report Summary:**\n{summary}"
                })
                st.rerun()
            else:
                st.error("Error analyzing report.")

    # ── Welcome Cards (when no messages) ──
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center; padding:2rem 0 0.5rem 0;" class="fade-in">
            <span style="font-size:2.8rem; filter: drop-shadow(0 0 16px rgba(56,189,248,0.3));">🧠</span>
            <h2 style="color:var(--text-white); font-weight:800; font-size:1.6rem; margin:14px 0 6px 0; letter-spacing:-0.03em;">What can I help you with?</h2>
            <p style="color:var(--text-secondary); font-size:12px; margin:0;">Powered by LangGraph Multi-Agent Supervisor Architecture</p>
            <div class="pipeline-flow">
                <span class="pipeline-node active">User Query</span>
                <span class="pipeline-arrow">→</span>
                <span class="pipeline-node active">🧠 Supervisor</span>
                <span class="pipeline-arrow">→</span>
                <span class="pipeline-node">Agent Execution</span>
                <span class="pipeline-arrow">→</span>
                <span class="pipeline-node">Response</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(4)
        cards = [
            ("🔬", "Symptom Check", "Describe symptoms for AI diagnosis", "Symptom Agent"),
            ("💊", "Medicine Info", "Drug interactions & suggestions", "Medicine Agent"),
            ("📅", "Appointments", "Book a doctor visit", "Appointment Agent"),
            ("📚", "Medical Q&A", "Ask from medical knowledge base", "RAG Agent"),
        ]
        for col, (icon, title, desc, agent) in zip(cols, cards):
            col.markdown(f"""
            <div class="metric-card fade-in">
                <div class="metric-icon">{icon}</div>
                <div class="metric-title">{title}</div>
                <div class="metric-desc">{desc}</div>
                <div style="margin-top:8px;"><span class="agent-badge" style="font-size:9px; padding:2px 8px;">{agent}</span></div>
            </div>
            """, unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Hello **{st.session_state.user_name}** 👋\n\nI'm your AI health assistant powered by a **multi-agent system**. The Supervisor will automatically route your query to the right specialist agent:\n\n- 🔬 **Symptom Agent** — Describe symptoms for AI-powered diagnosis\n- 💊 **Medicine Agent** — Drug information & OTC suggestions\n- 📅 **Appointment Agent** — Book a doctor appointment\n- 📚 **RAG Agent** — Medical knowledge from curated sources\n\nHow can I help you today?"
        })

    # ── Chat Messages ──
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "content" in message:
                st.markdown(message["content"])
            if "image" in message:
                try: st.image(message["image"])
                except: pass

    # ── Chat Input ──
    if user_input := st.chat_input("Describe your symptoms, ask about medicines, or book an appointment..."):
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("🧠 Supervisor routing to agent..."):
            try:
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
                    agent_name = data['agent'].upper()
                    full_res = f"*🤖 Routed to: **{agent_name} AGENT***\n\n{data['response']}"
                    process_chat_response(full_res)
                else:
                    st.error("Error from backend.")
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Backend server is not reachable.")


# ════════════════════════════════════════════════════════════════
# ROUTING
# ════════════════════════════════════════════════════════════════
if not st.session_state.token:
    auth_screen()
elif st.session_state.role == "doctor":
    doctor_dashboard()
else:
    main_app()
