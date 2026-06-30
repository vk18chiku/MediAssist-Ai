# frontend/streamlit/app.py
import streamlit as st
import requests
import os
import base64
import platform
import time

st.set_page_config(page_title="MediAssist AI", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# --- API Configuration ---
BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

if BASE_URL.endswith("/"):
    BASE_URL = BASE_URL[:-1]

# --- Session State Init ---
defaults = {
    "token": None, "user_name": None, "user_email": None, "role": None,
    "messages": [], "forgot_password_mode": False, "otp_sent": False,
    "reset_email": "", "signup_otp_sent": False, "current_session_id": None,
    "theme": "light",
}

from streamlit_cookies_controller import CookieController
import time
cookie_controller = CookieController()

cookie_token = None
cookie_user = None
cookie_email = None
cookie_role = None
cookie_theme = None

# Native Streamlit cookies (1.38+) read instantly from HTTP headers without JS delay
if hasattr(st, "context") and hasattr(st.context, "cookies"):
    _cookies = st.context.cookies
    cookie_token = _cookies.get('auth_token')
    cookie_user = _cookies.get('auth_user')
    cookie_email = _cookies.get('auth_email')
    cookie_role = _cookies.get('auth_role')
    cookie_theme = _cookies.get('ui_theme')

# Fallback to JS controller for older Streamlit versions (like localhost 1.35)
if not cookie_token:
    cookie_token = cookie_controller.get('auth_token')
if not cookie_user:
    cookie_user = cookie_controller.get('auth_user')
if not cookie_email:
    cookie_email = cookie_controller.get('auth_email')
if not cookie_role:
    cookie_role = cookie_controller.get('auth_role')
if not cookie_theme:
    cookie_theme = cookie_controller.get('ui_theme')

for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

if "theme_initialized" not in st.session_state:
    st.session_state.theme_initialized = True
    if cookie_theme:
        st.session_state.theme = cookie_theme

if cookie_theme != st.session_state.theme and cookie_theme is not None:
    cookie_controller.set('ui_theme', st.session_state.theme)

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
if not st.session_state.token and cookie_token:
    if cookie_email:
        st.session_state.token = cookie_token
        st.session_state.user_name = cookie_user
        st.session_state.user_email = cookie_email
        st.session_state.role = cookie_role


# ════════════════════════════════════════════════════════════════
# ULTRA-PREMIUM CSS — Advanced AI Platform UI
# ════════════════════════════════════════════════════════════════

if st.session_state.theme == "dark":
    css_vars = """
    --bg-void: #09090b;
    --bg-deep: #18181b;
    --bg-surface: #27272a;
    --chat-bg: #ffffff;
    --chat-text: #0f172a;
    --bg-elevated: #3f3f46;
    --bg-card: rgba(39, 39, 42, 0.9);
    --bg-card-hover: rgba(63, 63, 70, 1);
    --border-dim: rgba(255, 255, 255, 0.05);
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-glow: rgba(14, 165, 233, 0.3);
    --cyan: #00d1b2;
    --cyan-dim: #00e6c3;
    --cyan-glow: rgba(0, 209, 178, 0.15);
    --cyan-deep-glow: rgba(0, 209, 178, 0.05);
    --violet: #8b5cf6;
    --violet-dim: #a78bfa;
    --violet-glow: rgba(139, 92, 246, 0.15);
    --emerald: #10b981;
    --emerald-glow: rgba(16, 185, 129, 0.15);
    --amber: #f59e0b;
    --rose: #ef4444;
    --text-white: #f8fafc;
    --text-secondary: #a1a1aa;
    --text-muted: #71717a;
    --gradient-hero: linear-gradient(135deg, #00d1b2 0%, #00b89c 100%);
    --gradient-btn: linear-gradient(135deg, #00d1b2 0%, #00b89c 100%);
    --gradient-card: linear-gradient(160deg, #18181b 0%, #09090b 100%);
    """
else:
    css_vars = """
    --bg-void: #f8fafc;
    --bg-deep: #f1f5f9;
    --bg-surface: #ffffff;
    --chat-bg: #27272a;
    --chat-text: #f8fafc;
    --bg-elevated: #ffffff;
    --bg-card: rgba(255, 255, 255, 0.9);
    --bg-card-hover: rgba(255, 255, 255, 1);
    --border-dim: rgba(15, 23, 42, 0.05);
    --border-subtle: rgba(15, 23, 42, 0.08);
    --border-glow: rgba(14, 165, 233, 0.3);
    --cyan: #00d1b2;
    --cyan-dim: #00e6c3;
    --cyan-glow: rgba(0, 209, 178, 0.15);
    --cyan-deep-glow: rgba(0, 209, 178, 0.05);
    --violet: #8b5cf6;
    --violet-dim: #a78bfa;
    --violet-glow: rgba(139, 92, 246, 0.15);
    --emerald: #10b981;
    --emerald-glow: rgba(16, 185, 129, 0.15);
    --amber: #f59e0b;
    --rose: #ef4444;
    --text-white: #0f172a;
    --text-secondary: #475569;
    --text-muted: #64748b;
    --gradient-hero: linear-gradient(135deg, #00d1b2 0%, #00b89c 100%);
    --gradient-btn: linear-gradient(135deg, #00d1b2 0%, #00b89c 100%);
    --gradient-card: linear-gradient(160deg, #ffffff 0%, #f8fafc 100%);
    """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {{
    {css_vars}
}}
""" + """

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    color: var(--text-white) !important;
    transition: background-color 0.3s ease, color 0.3s ease !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(15, 23, 42, 0.1); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(15, 23, 42, 0.2); }

/* ── Main Background with Mesh ── */
.stApp {
    background: var(--bg-void) !important;
    background-image: 
        radial-gradient(ellipse 80% 50% at 20% 20%, rgba(14, 165, 233, 0.05) 0%, transparent 50%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 50%) !important;
    min-height: 100vh;
    transition: background 0.4s ease !important;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border-dim) !important;
    box-shadow: 2px 0 10px rgba(0,0,0,0.02) !important;
}
[data-testid="stSidebar"] * { color: var(--text-secondary); }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--text-white) !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextInput div[data-baseweb="input"], .stTextInput div[data-baseweb="base-input"],
.stTextArea textarea, .stTextArea div[data-baseweb="textarea"], .stTextArea div[data-baseweb="base-input"],
.stNumberInput input, .stNumberInput div[data-baseweb="input"], .stNumberInput div[data-baseweb="base-input"],
.stSelectbox div[data-baseweb="select"], .stSelectbox div[data-baseweb="select"] > div {
    background: var(--bg-surface) !important;
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    color: var(--text-white) !important;
    transition: all 0.25s ease !important;
    font-size: 15px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
}

::placeholder {
    color: var(--text-muted) !important;
    opacity: 0.7 !important;
}

/* Password Eye Icon and Suffix blocks */
.stTextInput [data-baseweb="input"] > div, .stTextInput [data-baseweb="input"] button {
    background: transparent !important;
    background-color: transparent !important;
    color: var(--text-white) !important;
}

/* Dropdown popover list */
[data-baseweb="menu"] {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
}
[data-baseweb="menu"] * {
    color: var(--text-white) !important;
}

.stTextInput input:focus, .stTextInput div[data-baseweb="input"]:focus-within,
.stTextArea textarea:focus, .stTextArea div[data-baseweb="textarea"]:focus-within {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px var(--cyan-glow) !important;
}
.stTextInput label, .stTextArea label, .stNumberInput label,
.stSelectbox label, .stFileUploader label {
    color: var(--text-muted) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

/* ── Buttons ── */
.stButton > button, .stFormSubmitButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    border: none !important;
    padding: 0.6rem 1.4rem !important;
}
.stButton > button[kind="primary"], .stFormSubmitButton > button {
    background: var(--gradient-btn) !important;
    color: white !important;
    box-shadow: 0 4px 10px rgba(14, 165, 233, 0.2) !important;
}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 15px rgba(14, 165, 233, 0.3) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--bg-surface) !important;
    color: var(--text-white) !important;
    border: 1px solid var(--border-subtle) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--bg-elevated) !important;
    border-color: var(--border-dim) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: var(--bg-surface) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border-subtle) !important;
}
[data-testid="stExpander"] details summary p, [data-testid="stExpander"] details summary svg {
    color: var(--text-white) !important;
    font-weight: 600 !important;
}

/* ── Containers (Cards) ── */
[data-testid="stVerticalBlockBorderWrapper"], 
[data-testid="stVerticalBlockBorderWrapper"] > div,
div[data-testid="stVerticalBlock"]:has(.custom-card-marker),
.st-emotion-cache-12w0qpk {
    background: var(--bg-surface) !important;
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    transition: background-color 0.3s ease, border-color 0.3s ease !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-deep) !important;
    border-radius: 14px !important;
    padding: 5px !important;
    gap: 4px !important;
    border: 1px solid var(--border-dim) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 11px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    color: var(--text-muted) !important;
    padding: 10px 24px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-surface) !important;
    color: var(--text-white) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    border: 1px solid var(--border-dim) !important;
}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    background: var(--chat-bg) !important;
    background-color: var(--chat-bg) !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: 18px !important;
    margin-bottom: 14px !important;
    padding: 18px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
}
[data-testid="stChatMessage"] * {
    color: var(--chat-text) !important;
}
[data-testid="stChatMessage"] .stMarkdown p {
    font-size: 15px !important;
    line-height: 1.75 !important;
}
[data-testid="stChatMessage"] div {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* ── Chat Input ── */
[data-testid="stChatInput"] > div {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px var(--cyan-glow) !important;
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
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 20px !important;
    padding: 2.5rem !important;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.05) !important;
}

/* ═══ Custom Components ═══ */

/* Auth Header */
.ai-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
    position: relative;
}
.ai-header h1 {
    font-size: 2.8rem;
    font-weight: 900;
    margin: 0;
    letter-spacing: -0.04em;
    color: var(--text-white);
}
.ai-header h1 .gradient-text {
    background: var(--gradient-hero);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.ai-header .subtitle {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-top: 10px;
    font-weight: 500;
}

/* Agent Badge */
.agent-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(14, 165, 233, 0.1);
    color: var(--cyan);
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border: 1px solid rgba(14, 165, 233, 0.2);
}
.agent-badge-violet {
    background: rgba(139, 92, 246, 0.1);
    color: var(--violet);
    border-color: rgba(139, 92, 246, 0.2);
}
.agent-badge-emerald {
    background: rgba(16, 185, 129, 0.1);
    color: var(--emerald);
    border-color: rgba(16, 185, 129, 0.2);
}
.agent-badge-amber {
    background: rgba(245, 158, 11, 0.1);
    color: var(--amber);
    border-color: rgba(245, 158, 11, 0.2);
}

/* Status Indicators */
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}
.status-online { background: var(--emerald); box-shadow: 0 0 8px var(--emerald-glow); }
.status-processing { background: var(--amber); }

/* Metric Cards (Welcome Screen) */
.metric-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}
.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.08);
    border-color: rgba(14, 165, 233, 0.3);
}
.metric-card .metric-icon {
    font-size: 2rem;
    margin-bottom: 14px;
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
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 28px;
    position: relative;
    box-shadow: 0 10px 30px -10px rgba(0,0,0,0.05);
}

/* Appointment Card */
.appt-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-left: 4px solid var(--cyan);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}

/* Doctor Card */
.doc-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* System Info Bar */
.system-info {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 12px;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

/* Pipeline Visualization */
.pipeline-flow {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin: 5px 0 5px 0;
    flex-wrap: wrap;
}
.pipeline-node {
    background: var(--bg-deep);
    border: 1px solid var(--border-dim);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-secondary);
}
.pipeline-node.active {
    background: rgba(14, 165, 233, 0.1);
    border-color: var(--cyan);
    color: var(--cyan);
}
.pipeline-arrow {
    color: var(--border-subtle);
    font-size: 12px;
}
hr { border-color: var(--border-dim) !important; }
.fade-in { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    background-color: var(--bg-surface) !important;
    border: 1px dashed var(--cyan) !important;
    border-radius: 12px !important;
    color: var(--text-white) !important;
}
[data-testid="stFileUploader"] > section, [data-testid="stFileUploaderDropzone"] {
    background-color: var(--bg-surface) !important;
}
[data-testid="stFileUploader"] * {
    color: var(--text-white) !important;
}
[data-testid="stFileUploader"] button {
    background: var(--gradient-btn) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

[data-testid="stChatInput"] {
    background-color: var(--bg-surface) !important;
}
[data-testid="stChatInput"] textarea {
    background-color: var(--bg-surface) !important;
    color: var(--text-white) !important;
}
[data-testid="stChatInput"] svg {
    color: var(--text-white) !important;
}

/* ── Bottom Chat Container ── */
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {
    background: var(--bg-void) !important;
}
[data-testid="stBottom"] > div {
    background: transparent !important;
}


.ai-header h1 {
    font-size: 3.5rem;
    font-weight: 900;
    margin: 0;
    letter-spacing: -0.05em;
    color: var(--text-white);
}


/* ── Reduce Streamlit Default Padding ── */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 95% !important;
}

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
                <span style="font-size:3.5rem; filter: drop-shadow(0 4px 10px rgba(14,165,233,0.15));">🧠</span>
            </div>
            <h1 style="font-weight: 900; font-size: 4rem;">Medi<span class="gradient-text" style="font-weight: 900;">Assist AI</span></h1>
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
                            if len(new_password_input) < 6:
                                st.error("Password must be at least 6 characters.")
                            else:
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
                                cookie_controller.set('auth_token', data["access_token"])
                                cookie_controller.set('auth_user', data["name"])
                                cookie_controller.set('auth_email', log_email)
                                cookie_controller.set('auth_role', data["role"])
                                st.success(f"Welcome back, {data['name']}!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                try: st.error(res.json().get("detail", "Invalid credentials."))
                                except: st.error(f"Server error: {res.status_code} - {res.text[:100]}")
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
                        if len(reg_password) < 6:
                            st.error("Password must be at least 6 characters.")
                        else:
                            with st.spinner("Sending OTP..."):
                                try:
                                    res = requests.post(f"{BASE_URL}/auth/signup-send-otp", json={"email": reg_email}, timeout=15)
                                    if res.status_code == 200:
                                        st.session_state.signup_otp_sent = True
                                        st.success("OTP sent!")
                                        st.rerun()
                                    else:
                                        try: st.error(res.json().get("detail", "Could not send OTP."))
                                        except: st.error(f"Server error: {res.status_code} - {res.text[:100]}")
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
                            cookie_controller.set('auth_token', data["access_token"])
                            cookie_controller.set('auth_user', data["name"])
                            cookie_controller.set('auth_email', reg_email)
                            cookie_controller.set('auth_role', data["role"])
                            st.session_state.signup_otp_sent = False
                            st.success(f"Welcome, {data['name']}!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            try: st.error(res.json().get("detail", "Signup failed."))
                            except: st.error(f"Server error: {res.status_code} - {res.text[:100]}")
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
    col1, col2, col3 = st.columns([7, 1, 1])
    with col1:
        safe_name = profile.get('name') or st.session_state.user_name or "Doctor"
        avatar_url = f"https://ui-avatars.com/api/?name={safe_name.replace(' ', '+')}&background=6366f1&color=fff&size=128&bold=true&format=svg"
        st.markdown(f"""
        <div class="profile-card fade-in">
            <div style="display:flex; gap:20px; align-items:flex-start;">
                <img src="{avatar_url}" style="border-radius:14px; width:80px; height:80px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                <div style="flex-grow:1;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <h2 style="margin:0 0 6px 0; color:var(--text-white); font-size:1.5rem; font-weight:800; letter-spacing:-0.02em;">
                                Dr. {safe_name}
                            </h2>
                            <span class="agent-badge" style="background:rgba(16,185,129,0.1); color:#10b981; border-color:rgba(16,185,129,0.2);">
                                {profile.get('specialization', 'Doctor')}
                            </span>
                        </div>
                        <div style="text-align:right;">
                            <div style="color:var(--text-white); font-weight:600; font-size:14px;">{profile.get('medical_name') or 'Clinic Not Set'}</div>
                            <div style="color:var(--text-secondary); font-size:12px; margin-top:3px;">📍 {profile.get('clinic_address') or 'N/A'}</div>
                            <div style="color:var(--text-secondary); font-size:12px; margin-top:2px;">📞 {profile.get('contact_number') or 'N/A'}</div>
                        </div>
                    </div>
                    <div style="margin-top:16px; color:var(--text-secondary); font-size:13px; line-height:1.6; background:var(--bg-void); padding:12px 16px; border-radius:10px; border:1px solid var(--border-subtle);">
                        {profile.get('bio') or '<em>No bio provided. Update your profile below.</em>'}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        theme_icon = "🌙 Dark" if st.session_state.theme == "light" else "☀️ Light"
        st.button(theme_icon, key="theme_toggle_doc", use_container_width=True, on_click=toggle_theme)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", type="secondary", use_container_width=True):
            for c in ['auth_token', 'auth_user', 'auth_email', 'auth_role']:
                try: cookie_controller.remove(c)
                except KeyError: pass
            st.session_state.token = None
            st.session_state.messages = []
            time.sleep(0.5)
            st.rerun()


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
                        <div class="appt-card" style="border-left-color: var(--emerald);">
                            <div style="color:var(--text-white); font-weight:600; font-size:13px; margin-bottom:4px;">{appt['patient_name']}</div>
                            <div style="color:var(--text-secondary); font-size:12px;">📅 {appt['date']} · ⏰ {appt['time']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No upcoming appointments.")
            else:
                st.error("Could not load.")

        st.markdown("<h3 style='color:var(--cyan); margin-bottom:15px; margin-top:0;'>⏳ Pending Requests</h3>", unsafe_allow_html=True)
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
                                <div style="color:var(--text-white); font-weight:600; font-size:13px;">{appt['patient_name']}</div>
                            </div>
                            <div>
                                <div style="color:var(--text-muted); font-size:10px; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:3px;">Email</div>
                                <div style="color:var(--text-secondary); font-size:12px;">{appt['patient_email']}</div>
                            </div>
                            <div>
                                <div style="color:var(--text-muted); font-size:10px; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:3px;">Date</div>
                                <div style="color:var(--cyan); font-weight:600; font-size:13px;">{appt['date']}</div>
                            </div>
                            <div>
                                <div style="color:var(--text-muted); font-size:10px; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:3px;">Time</div>
                                <div style="color:var(--cyan); font-weight:600; font-size:13px;">{appt['time']}</div>
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

# ════════════════════════════════════════════════════════════════
# PATIENT PROFILE
# ════════════════════════════════════════════════════════════════
def render_patient_profile(profile):
    st.markdown("<h3 style='color: white;'>⚙️ My Profile</h3>", unsafe_allow_html=True)
    st.markdown("<div style='color:var(--text-secondary); font-size:13px; margin-bottom:16px;'>Complete your medical profile for better AI assistance.</div>", unsafe_allow_html=True)
    
    with st.form("patient_profile_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.text_input("Age", value=profile.get("age") or "")
            blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"], index=0 if not profile.get("blood_group") else ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"].index(profile.get("blood_group", "Unknown")))
        with c2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0 if not profile.get("gender") else ["Male", "Female", "Other"].index(profile.get("gender", "Male")))
            height = st.text_input("Height (cm)", value=profile.get("height") or "")
        with c3:
            weight = st.text_input("Weight (kg)", value=profile.get("weight") or "")
            phone = st.text_input("Phone Number", value=profile.get("phone_number") or "")
            
        c4, c5 = st.columns(2)
        with c4:
            address = st.text_area("Address", value=profile.get("address") or "", height=80)
            allergies = st.text_area("Allergies (if any)", value=profile.get("allergies") or "", height=80)
        with c5:
            emergency = st.text_area("Emergency Contact", value=profile.get("emergency_contact") or "", height=80)
            diseases = st.text_area("Existing Diseases", value=profile.get("existing_diseases") or "", height=80)
            
        history = st.text_area("Medical History (Operations, major illnesses)", value=profile.get("medical_history") or "", height=100)
        
        if st.form_submit_button("Save Profile", type="primary"):
            payload = {
                "age": age, "gender": gender, "height": height, "weight": weight,
                "blood_group": blood, "phone_number": phone, "address": address,
                "emergency_contact": emergency, "allergies": allergies,
                "existing_diseases": diseases, "medical_history": history
            }
            r = requests.post(f"{BASE_URL}/patients/profile", params={"patient_email": st.session_state.user_email}, json=payload)
            if r.status_code == 200:
                st.success("Profile saved successfully!")
                st.rerun()
            else:
                st.error("Failed to save profile.")

# ════════════════════════════════════════════════════════════════
# PATIENT DASHBOARD (Main App)


# ════════════════════════════════════════════════════════════════
# PATIENT PROFILE
# ════════════════════════════════════════════════════════════════
def render_patient_profile(profile):
    st.markdown("<h3 style='color: white;'>⚙️ My Profile</h3>", unsafe_allow_html=True)
    st.markdown("<div style='color:var(--text-secondary); font-size:13px; margin-bottom:16px;'>Complete your medical profile for better AI assistance.</div>", unsafe_allow_html=True)
    
    with st.form("patient_profile_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.text_input("Age", value=profile.get("age") or "")
            blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"], index=0 if not profile.get("blood_group") else ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"].index(profile.get("blood_group", "Unknown")))
        with c2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0 if not profile.get("gender") else ["Male", "Female", "Other"].index(profile.get("gender", "Male")))
            height = st.text_input("Height (cm)", value=profile.get("height") or "")
        with c3:
            weight = st.text_input("Weight (kg)", value=profile.get("weight") or "")
            phone = st.text_input("Phone Number", value=profile.get("phone_number") or "")
            
        c4, c5 = st.columns(2)
        with c4:
            address = st.text_area("Address", value=profile.get("address") or "", height=80)
            allergies = st.text_area("Allergies (if any)", value=profile.get("allergies") or "", height=80)
        with c5:
            emergency = st.text_area("Emergency Contact", value=profile.get("emergency_contact") or "", height=80)
            diseases = st.text_area("Existing Diseases", value=profile.get("existing_diseases") or "", height=80)
            
        history = st.text_area("Medical History (Operations, major illnesses)", value=profile.get("medical_history") or "", height=100)
        
        if st.form_submit_button("Save Profile", type="primary"):
            payload = {
                "age": age, "gender": gender, "height": height, "weight": weight,
                "blood_group": blood, "phone_number": phone, "address": address,
                "emergency_contact": emergency, "allergies": allergies,
                "existing_diseases": diseases, "medical_history": history
            }
            r = requests.post(f"{BASE_URL}/patients/profile", params={"patient_email": st.session_state.user_email}, json=payload)
            if r.status_code == 200:
                st.toast("Profile saved successfully!")
                st.rerun()
            else:
                st.error("Failed to save profile.")

def main_app():
    res = requests.get(f"{BASE_URL}/patients/profile", params={"patient_email": st.session_state.user_email})
    profile = res.json() if res.status_code == 200 else {}
    profile_completed = profile.get("profile_completed", False)

    # System status bar with Agent Headers
    st.markdown('''
    <div class="system-info fade-in" style="display:flex; justify-content:space-between; align-items:center; padding: 18px 24px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <span class="status-dot status-online" style="width:10px; height:10px;"></span>
            <span style="font-size:24px; font-weight:900; color:var(--text-white); letter-spacing:-0.03em;">MediAssist AI</span>
        </div>
        <div style="display:flex; gap:35px; font-size:14px; font-weight:800; color:var(--text-white);">
            <span style="display:flex; align-items:center; gap:6px;">🔬 Symptom Check</span>
            <span style="display:flex; align-items:center; gap:6px;">💊 Medicine Info</span>
            <span style="display:flex; align-items:center; gap:6px;">📅 Appointments</span>
            <span style="display:flex; align-items:center; gap:6px;">📚 Medical Q&A</span>
        </div>
        <span style="font-size:13px; color:var(--text-muted); font-weight:600;">Multi-Agent System Active</span>
    </div>
    ''', unsafe_allow_html=True)

    # Top bar
    col1, col2, col3 = st.columns([7, 1, 1])
    with col1:
        safe_name = st.session_state.user_name or "User"
        avatar_url = f"https://ui-avatars.com/api/?name={safe_name.replace(' ', '+')}&background=6366f1&color=fff&size=128&bold=true&format=svg"
        st.markdown(f'''
        <div style="display:flex; align-items:center; gap:14px; padding:0px 0 10px 0; animation: fadeIn 0.4s ease-out;">
            <img src="{avatar_url}" style="border-radius:12px; width:48px; height:48px; border:2px solid var(--accent); box-shadow: 0 0 12px var(--accent-glow);">
            <div>
                <h2 style="margin:0; color:var(--text-white); font-size:1.3rem; font-weight:800; letter-spacing:-0.02em;">
                    {safe_name}
                </h2>
                <p style="margin:0; color:var(--text-secondary); font-size:12px;">Patient Dashboard</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        theme_icon = "🌙 Dark" if st.session_state.theme == "light" else "☀️ Light"
        st.button(theme_icon, key="theme_toggle_patient", use_container_width=True, on_click=toggle_theme)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", type="secondary", use_container_width=True):
            for c in ['auth_token', 'auth_user', 'auth_email', 'auth_role']:
                try: cookie_controller.remove(c)
                except KeyError: pass
            st.session_state.token = None
            st.session_state.messages = []
            st.session_state.current_session_id = None
            time.sleep(0.5)
            st.rerun()


    if not profile_completed:
        st.info("👋 Welcome! Please complete your Patient Profile to continue.")
        render_patient_profile(profile)
        return

    tab1, tab2 = st.tabs(["🏥 Dashboard", "⚙️ My Profile"])

    with tab1:
        # Action Header for Dashboard
        h_col1, h_col2, h_col3 = st.columns(3)
        
        with h_col1:
            with st.popover("💬 Previous Sessions", use_container_width=True):
                if st.button("＋ New Chat", type="primary", use_container_width=True):
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
                            if st.button(f"💬 {s['session_name'][:15]}...", key=f"session_{s['id']}", type=btn_style, use_container_width=True):
                                st.session_state.current_session_id = s["id"]
                                try:
                                    msgs_res = requests.get(f"{BASE_URL}/chat/sessions/{s['id']}/messages")
                                    if msgs_res.status_code == 200:
                                        st.session_state.messages = msgs_res.json()
                                except:
                                    st.session_state.messages = []
                                st.rerun()
                        with col_del:
                            if st.button("🗑", key=f"del_{s['id']}", type="secondary", use_container_width=True):
                                requests.delete(f"{BASE_URL}/chat/sessions/{s['id']}")
                                if st.session_state.current_session_id == s["id"]:
                                    st.session_state.current_session_id = None
                                    st.session_state.messages = []
                                st.rerun()
                else:
                    st.caption("No past sessions.")

        with h_col2:
            with st.popover("📅 My Appointments", use_container_width=True):
                try:
                    appt_res = requests.get(f"{BASE_URL}/appointments/patient", params={"patient_email": st.session_state.user_email})
                    if appt_res.status_code == 200:
                        my_appts = appt_res.json()
                        if my_appts:
                            for a in my_appts:
                                status_color = "var(--amber)" if a['status'] == 'pending' else ("var(--emerald)" if a['status'] == 'accepted' else "var(--rose)")
                                st.markdown(f'''
                                <div style="background:var(--bg-elevated); padding:10px; border-radius:8px; border-left:4px solid {status_color}; margin-bottom:8px; font-size:12px;">
                                    <div style="font-weight:bold; color:var(--text-white);">Dr. {a['doctor_name']}</div>
                                    <div style="color:var(--text-secondary);">{a['date']} | {a['time']}</div>
                                    <div style="color:{status_color}; font-weight:600; margin-top:4px;">{a['status'].upper()}</div>
                                </div>
                                ''', unsafe_allow_html=True)
                        else:
                            st.caption("No appointments booked yet.")
                except:
                    st.caption("Failed to load appointments.")
    
        with h_col3:
            with st.popover("🏥 Available Doctors", use_container_width=True):
                try:
                    res = requests.get(f"{BASE_URL}/doctors")
                    if res.status_code == 200:
                        docs = res.json()
                        if docs:
                            all_specs = sorted(list(set(d['specialization'] for d in docs)))
                            selected_spec = st.selectbox("Filter Specialty", ["All"] + all_specs, label_visibility="collapsed")
                            for i, d in enumerate(docs):
                                if selected_spec != "All" and d['specialization'] != selected_spec:
                                    continue
                                doc_avatar = f"https://ui-avatars.com/api/?name={d['name'].replace(' ', '+')}&background=6366f1&color=fff&size=64&bold=true&format=svg"
                                exp_text = f"{d.get('experience')} yrs" if d.get('experience') else "N/A"
                                
                                # Clean card styling
                                with st.container(border=True):
                                    st.markdown(f'''
                                    <span class="custom-card-marker" style="display:none;"></span>
                                    <div style="display:flex; gap:10px; align-items:center; margin-bottom:10px;">
                                        <img src="{doc_avatar}" style="border-radius:8px; width:48px; height:48px;">
                                        <div>
                                            <div style="color:var(--text-white); font-weight:700; font-size:14px;">Dr. {d['name']}</div>
                                            <div style="color:var(--cyan); font-size:12px; font-weight:600;">{d['specialization']}</div>
                                            <div style="color:var(--text-muted); font-size:11px;">{exp_text} exp | {d.get('medical_name') or 'Independent'}</div>
                                        </div>
                                    </div>
                                    ''', unsafe_allow_html=True)
                                    
                                    # Book Appointment logic
                                    with st.expander("📅 Book"):
                                        st.markdown(f"**Book with Dr. {d['name']}**")
                                        b_date = st.date_input("Date", key=f"date_{i}")
                                        b_time = st.time_input("Time", key=f"time_{i}")
                                        b_reason = st.text_input("Reason", placeholder="Brief symptom/reason", key=f"reason_{i}")
                                        if st.button("Confirm Booking", key=f"book_{i}", type="primary", use_container_width=True):
                                            payload = {
                                                "patient_name": st.session_state.user_name,
                                                "patient_email": st.session_state.user_email,
                                                "doctor_name": d['name'],
                                                "doctor_email": d['email'],
                                                "date": b_date.strftime("%Y-%m-%d"),
                                                "time": b_time.strftime("%H:%M")
                                            }
                                            breq = requests.post(f"{BASE_URL}/appointments/create", json=payload)
                                            if breq.status_code == 200:
                                                st.toast("Requested successfully!")
                                                st.rerun()
                                            else:
                                                st.error("Booking failed.")
                        else:
                            st.caption("No doctors available.")
                    else:
                        st.error("Failed to fetch.")
                except Exception as e:
                    st.error("Connection error.")

        st.markdown("<br>", unsafe_allow_html=True)
        col_chat, col_right = st.columns([7, 3], gap="medium")
    
        with col_chat:
            # ── Chat Messages ──
            chat_container = st.container(height=500)
            with chat_container:
                if not st.session_state.messages:
                    st.chat_message("assistant").markdown(f"Hello **{st.session_state.user_name}** 👋\n\nI'm your AI health assistant powered by a **multi-agent system**. The Supervisor will automatically route your query to the right specialist agent.\n\n💡 **Tip:** *You can book an appointment instantly by telling me the doctor's name, date, and time!* \n\nHow can I help you today?")
                
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        if "content" in message:
                            st.markdown(message["content"])
                        if "image" in message:
                            try: st.image(message["image"])
                            except: pass

        with col_right:
            st.markdown("<h3 style='color:var(--cyan); margin-bottom:15px; margin-top:0;'>📄 Report Analysis</h3>", unsafe_allow_html=True)
            report_file = st.file_uploader("Upload PDF or Image", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")
            if st.button("Analyze Report", type="primary", use_container_width=True) and report_file:
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

    # ── Chat Input ──
    if user_input := st.chat_input("Describe your symptoms, ask about medicines, or book an appointment..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Draw immediately inside the chat container so we don't need a full page rerun!
        with chat_container:
            st.chat_message("user").markdown(user_input)
            
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

    with tab2:
        render_patient_profile(profile)


# ════════════════════════════════════════════════════════════════
# ROUTING
# ════════════════════════════════════════════════════════════════
if not st.session_state.token:
    auth_screen()
elif st.session_state.role == "doctor":
    doctor_dashboard()
else:
    main_app()
