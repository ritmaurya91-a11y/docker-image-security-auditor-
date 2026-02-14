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

/* Hide Streamlit default */
#MainMenu, header, footer {visibility: hidden;}

/* Background */
.stApp {
    background:
    linear-gradient(rgba(0,0,0,0.90), rgba(0,0,0,0.95)),
    url("https://images.unsplash.com/photo-1518770660439-4636190af475");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Force text white */
html, body, p, span, div, li, ul, ol,
h1, h2, h3, h4, h5, h6 {
    color: white !important;
}

/* ==============================
   ANIMATED DROPZONE
============================== */
div[data-testid="stFileUploaderDropzone"] {
    background: rgba(25,25,25,0.95) !important;
    border: 2px dashed #00ffff !important;
    border-radius: 20px !important;
    padding: 45px !important;
    transition: all 0.3s ease-in-out;
    animation: glowPulse 3s infinite alternate;
}

/* Glow animation */
@keyframes glowPulse {
    0% { box-shadow: 0 0 10px #00ffff; }
    100% { box-shadow: 0 0 25px #00ff99; }
}

/* Hover lift */
div[data-testid="stFileUploaderDropzone"]:hover {
    transform: scale(1.02);
    border-color: #00ff99 !important;
}

/* Drag text */
div[data-testid="stFileUploaderDropzone"] p {
    color: white !important;
    font-weight: 600 !important;
    font-size: 18px !important;
}

/* ==============================
   ANIMATED BROWSE BUTTON
============================== */
div[data-testid="stFileUploaderDropzone"] button {
    background: linear-gradient(90deg, #8e2de2, #ff0080) !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 14px !important;
    padding: 10px 25px !important;
    border: none !important;
    position: relative;
    overflow: hidden;
    animation: browseGlow 2s infinite alternate;
    transition: all 0.3s ease-in-out;
}

/* Button glow */
@keyframes browseGlow {
    0% { box-shadow: 0 0 8px #8e2de2; }
    100% { box-shadow: 0 0 25px #ff0080; }
}

/* Hover zoom */
div[data-testid="stFileUploaderDropzone"] button:hover {
    transform: scale(1.08);
    box-shadow: 0 0 35px #ff0080 !important;
}

/* Shine sweep */
div[data-testid="stFileUploaderDropzone"] button::after {
    content: "";
    position: absolute;
    top: 0;
    left: -75%;
    width: 50%;
    height: 100%;
    background: rgba(255,255,255,0.4);
    transform: skewX(-25deg);
    transition: 0.75s;
}

div[data-testid="stFileUploaderDropzone"] button:hover::after {
    left: 125%;
}

/* Run scan button */
.stButton > button {
    background: linear-gradient(90deg, #00ffff, #00ff99) !important;
    color: black !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    padding: 10px 25px !important;
    animation: glowPulse 2s infinite alternate;
}

/* Code blocks */
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
