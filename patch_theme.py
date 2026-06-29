import re

with open("frontend/streamlit/app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update defaults to include theme
content = content.replace(
    '"reset_email": "", "signup_otp_sent": False, "current_session_id": None,',
    '"reset_email": "", "signup_otp_sent": False, "current_session_id": None,\n    "theme": "light",'
)

# 2. Get cookie theme and set it
cookie_logic = """cookie_role = cookie_controller.get('auth_role')
cookie_theme = cookie_controller.get('ui_theme')

for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default

if cookie_theme and st.session_state.theme != cookie_theme:
    st.session_state.theme = cookie_theme"""

content = content.replace(
"""cookie_role = cookie_controller.get('auth_role')

for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default""",
cookie_logic
)


# 3. Replace static CSS block with dynamic python variable
old_css_start = """st.markdown(\"\"\"
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {"""

new_css_start = """
if st.session_state.theme == "dark":
    css_vars = \"\"\"
    --bg-void: #09090b;
    --bg-deep: #18181b;
    --bg-surface: #27272a;
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
    \"\"\"
else:
    css_vars = \"\"\"
    --bg-void: #f8fafc;
    --bg-deep: #f1f5f9;
    --bg-surface: #ffffff;
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
    \"\"\"

st.markdown(f\"\"\"
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {{
    {css_vars}"""

content = content.replace(old_css_start, new_css_start)

# Clean up the end of the root block
content = content.replace("""    --gradient-btn: linear-gradient(135deg, #00d1b2 0%, #00b89c 100%);
    --gradient-card: linear-gradient(160deg, #ffffff 0%, #f8fafc 100%);
}""", "}")


with open("frontend/streamlit/app.py", "w", encoding="utf-8") as f:
    f.write(content)
