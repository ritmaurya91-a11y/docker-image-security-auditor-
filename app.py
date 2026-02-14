import streamlit as st
from groq import Groq
import time

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Docker Image Security Auditor", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ==============================
# FULL STYLING
# ==============================
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}

.stApp {
    background:
    linear-gradient(rgba(0,0,0,0.65), rgba(0,0,0,0.75)),
    url("https://images.unsplash.com/photo-1518770660439-4636190af475");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

html, body, p, span, div, li, ul, ol, h1, h2, h3, h4, h5, h6 {
    color: white !important;
}

h1 {
    font-size: 52px !important;
    font-weight: 900 !important;
    color: #00ffff !important;
    text-align: center !important;
    text-shadow:
        0 0 5px #00ffff,
        0 0 15px #00ffff,
        0 0 35px #00ffff;
    animation: titleGlow 2s infinite alternate;
}

@keyframes titleGlow {
    from { text-shadow: 0 0 10px #00ffff; }
    to { text-shadow: 0 0 40px #00ffcc; }
}

div[data-testid="stFileUploaderDropzone"] {
    background: rgba(25,25,25,0.85) !important;
    border: 2px dashed #00ffff !important;
    border-radius: 20px !important;
    padding: 45px !important;
}

div[data-testid="stFileUploaderDropzone"] div {
    color: #00ffff !important;
    text-shadow: 0 0 10px #00ffff;
}

div[data-testid="stFileUploaderDropzone"] button {
    box-shadow: 0 0 15px #ff00ff;
}

.stButton > button {
    background: linear-gradient(90deg, #00ffff, #00ff99) !important;
    color: black !important;
    font-weight: bold !important;
    border-radius: 12px !important;
}

pre {
    background: #0d1117 !important;
    color: white !important;
    border-radius: 12px;
}

code {
    background: #1f2937 !important;
    color: #00ff99 !important;
    padding: 3px 6px;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.markdown("<h1>🐳 Docker Image Security Auditor</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>Static + AI Powered Dockerfile Security Scanner</h4>", unsafe_allow_html=True)

# ==============================
# FILE UPLOAD
# ==============================
uploaded_file = st.file_uploader("📤 Upload Dockerfile", type=["txt", "Dockerfile"])

dockerfile_content = ""

if uploaded_file:
    dockerfile_content = uploaded_file.read().decode("utf-8")
    st.subheader("📄 Uploaded Dockerfile")
    st.code(dockerfile_content, language="dockerfile")

# ==============================
# STATIC CHECK
# ==============================
def static_scan(dockerfile):
    return [
        ("Base image defined", "PASS" if "FROM" in dockerfile else "CRITICAL"),
        ("Avoid latest tag", "WARNING" if ":latest" in dockerfile else "PASS"),
        ("Running as root user", "CRITICAL" if "USER root" in dockerfile else "PASS"),
        ("Healthcheck present", "PASS" if "HEALTHCHECK" in dockerfile else "WARNING"),
    ]

# ==============================
# AI ANALYSIS
# ==============================
def ai_analysis(dockerfile):
    dockerfile = dockerfile[:4000]

    prompt = f"""
You are a Senior DevSecOps Engineer.

Analyze this Dockerfile and provide:
1. Overall Risk Percentage
2. Security Risks
3. Explanation
4. Recommended Fixes
5. Best Practices

Dockerfile:
{dockerfile}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a Docker security expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI Error: {str(e)}"

# ==============================
# AUTO FIX FUNCTION
# ==============================
def auto_fix_dockerfile(dockerfile):

    fix_prompt = f"""
Fix all security issues in this Dockerfile.
Return ONLY the improved secure Dockerfile code.

Dockerfile:
{dockerfile}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a Docker security expert."},
                {"role": "user", "content": fix_prompt}
            ],
            temperature=0.2,
            max_tokens=1200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Auto-Fix Error: {str(e)}"

# ==============================
# RUN SCAN BUTTON
# ==============================

run_scan = st.button("🔍 Run Full Security Scan")

if run_scan:

    if not dockerfile_content.strip():
        st.warning("⚠ Please upload a Dockerfile first.")
    else:

        st.session_state["dockerfile"] = dockerfile_content

        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

        st.subheader("📊 Static Security Analysis")

        results = static_scan(dockerfile_content)

        score_map = {"PASS": 0, "WARNING": 5, "CRITICAL": 10}
        risk_score = sum(score_map[s] for _, s in results)
        risk_percent = min(100, risk_score)

        st.markdown(f"### 🔐 Overall Risk Level: {risk_percent}%")
        st.progress(risk_percent / 100)

        for check, status in results:
            if status == "PASS":
                st.success(f"🟢 {check}")
            elif status == "WARNING":
                st.warning(f"🟡 {check}")
            else:
                st.error(f"🔴 {check}")

        st.divider()

        st.subheader("🤖 AI Security Expert Analysis")
        with st.spinner("AI analyzing Dockerfile..."):
            ai_report = ai_analysis(dockerfile_content)

        st.markdown(ai_report)
        st.divider()

# ==============================
# AUTO FIX SECTION
# ==============================

if "dockerfile" in st.session_state:

    st.subheader("🛠 Auto-Fix Dockerfile")

    generate_fix = st.button("🚀 Generate Secure Dockerfile")

    if generate_fix:
        with st.spinner("Generating secure version..."):
            fixed_code = auto_fix_dockerfile(st.session_state["dockerfile"])

        st.success("✅ Secure Dockerfile Generated")
        st.code(fixed_code, language="dockerfile")

    st.divider()
    st.caption("Docker Image Security Auditor | AI Powered by Groq")
    
