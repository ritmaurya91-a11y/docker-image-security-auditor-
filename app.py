import streamlit as st
from groq import Groq
import time

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Docker Image Security Auditor", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ==============================
# FULL CSS FIX (INCLUDING DRAG TEXT)
# ==============================
st.markdown("""
<style>

/* Background stays */
.stApp {
    background:
    linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.92)),
    url("https://images.unsplash.com/photo-1518770660439-4636190af475");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* ================================
   ANIMATED DROPZONE DESIGN
================================ */

div[data-testid="stFileUploaderDropzone"] {
    background: rgba(25,25,25,0.95) !important;
    border: 2px solid transparent !important;
    border-radius: 20px !important;
    padding: 50px !important;
    position: relative;
    transition: all 0.3s ease-in-out;
    animation: glowPulse 3s infinite alternate;
}

/* Gradient glowing border */
div[data-testid="stFileUploaderDropzone"]::before {
    content: "";
    position: absolute;
    inset: -2px;
    border-radius: 22px;
    background: linear-gradient(45deg, #00ffff, #00ff99, #00ffff);
    z-index: -1;
    filter: blur(12px);
    opacity: 0.6;
}

/* Hover animation */
div[data-testid="stFileUploaderDropzone"]:hover {
    transform: scale(1.02);
    box-shadow: 0 0 30px #00ff99;
}

/* Pulse glow animation */
@keyframes glowPulse {
    0% {
        box-shadow: 0 0 10px #00ffff;
    }
    100% {
        box-shadow: 0 0 25px #00ff99;
    }
}

/* Drag text styling */
div[data-testid="stFileUploaderDropzone"] p {
    color: white !important;
    font-weight: 600 !important;
    font-size: 18px !important;
}

/* Browse button styling */
div[data-testid="stFileUploaderDropzone"] button {
    background: linear-gradient(90deg, #00ffff, #00ff99) !important;
    color: black !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    transition: 0.3s ease;
}

div[data-testid="stFileUploaderDropzone"] button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 15px #00ff99;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.markdown("<h1 style='text-align:center;color:#00ffff;'>🐳 Docker Image Security Auditor</h1>", unsafe_allow_html=True)
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
            model="llama-3.3-70b-versatile",
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
# RUN SCAN
# ==============================
if st.button("🔍 Run Full Security Scan"):

    if not dockerfile_content.strip():
        st.warning("⚠ Please upload a Dockerfile first.")
    else:

        # Scanning animation
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
        st.caption("Docker Image Security Auditor | AI Powered by Groq")
