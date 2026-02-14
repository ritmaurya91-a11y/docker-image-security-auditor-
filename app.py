import streamlit as st
from groq import Groq
import logging
import time
from datetime import datetime

# ==============================
# CONFIGURATION
# ==============================
st.set_page_config(
    page_title="Docker Security Auditor",
    layout="wide",
    page_icon="🐳"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ GROQ_API_KEY not found in secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ==============================
# GLOBAL PROFESSIONAL STYLING
# ==============================
st.markdown("""
<style>

/* Hide default */
#MainMenu, footer {visibility: hidden;}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}

/* FORCE ALL TEXT WHITE */
html, body, div, span, p, label, li,
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
}

/* Headings Accent */
h1, h2, h3, h4 {
    color: #00ffff !important;
}

/* File Uploader Styling */
div[data-testid="stFileUploaderDropzone"] {
    background: rgba(0, 0, 0, 0.6) !important;
    border: 2px dashed #00ffff !important;
    border-radius: 15px !important;
    padding: 40px !important;
    animation: borderGlow 3s infinite alternate;
}

@keyframes borderGlow {
    0% { box-shadow: 0 0 10px #00ffff; }
    100% { box-shadow: 0 0 25px #00ff99; }
}

div[data-testid="stFileUploaderDropzone"] p {
    color: #ffffff !important;
    font-weight: bold !important;
    font-size: 18px !important;
}

/* Animated Main Buttons */
.stButton > button {
    background: linear-gradient(90deg, #8e2de2, #ff0080) !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    padding: 10px 25px !important;
    border: none !important;
    animation: glow 2s infinite alternate;
    transition: all 0.3s ease-in-out;
}

@keyframes glow {
    0% { box-shadow: 0 0 10px #8e2de2; }
    100% { box-shadow: 0 0 30px #ff0080; }
}

.stButton > button:hover {
    transform: scale(1.07);
}

/* Download Button */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(90deg, #00ffff, #00ff99) !important;
    color: black !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    animation: glow 2s infinite alternate;
}

/* Code Block */
pre {
    background: #0d1117 !important;
    color: white !important;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# HEADER
# ==============================
st.title("🐳 Docker Image Security Auditor")
st.caption("Enterprise-Grade Static + AI Powered Dockerfile Scanner")

# ==============================
# FILE UPLOAD
# ==============================
uploaded_file = st.file_uploader("📤 Upload Dockerfile", type=["txt", "Dockerfile"])
dockerfile_content = ""

if uploaded_file:
    try:
        dockerfile_content = uploaded_file.read().decode("utf-8")
        st.code(dockerfile_content, language="dockerfile")
    except Exception as e:
        logging.error(str(e))
        st.error("Invalid file format.")
        st.stop()

# ==============================
# STATIC SCANNER
# ==============================
def static_scan(dockerfile: str):
    checks = []
    checks.append(("Base Image Defined", "PASS" if "FROM" in dockerfile else "CRITICAL"))
    checks.append(("Avoid latest tag", "WARNING" if ":latest" in dockerfile else "PASS"))
    checks.append(("Running as root", "CRITICAL" if "USER root" in dockerfile else "PASS"))
    checks.append(("HEALTHCHECK Present", "PASS" if "HEALTHCHECK" in dockerfile else "WARNING"))
    checks.append(("Uses COPY instead of ADD", "WARNING" if "ADD " in dockerfile else "PASS"))
    checks.append(("Exposes unnecessary ports", "WARNING" if "EXPOSE 22" in dockerfile else "PASS"))
    return checks

def calculate_risk(results):
    score_map = {"PASS": 0, "WARNING": 5, "CRITICAL": 15}
    total_score = sum(score_map[r[1]] for r in results)
    return min(100, total_score)

# ==============================
# AI ANALYSIS
# ==============================
def ai_analysis(dockerfile: str):
    dockerfile = dockerfile[:3500]

    prompt = """
You are a Senior DevSecOps Engineer.

Analyze the Dockerfile and provide:
1. Risk Percentage (numeric)
2. Security Risks
3. Explanation
4. Recommendations
5. Best Practices
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a Docker security expert."},
                {"role": "user", "content": prompt + dockerfile}
            ],
            temperature=0.2,
            max_tokens=1000
        )
        return response.choices[0].message.content

    except Exception as e:
        logging.error(str(e))
        return "⚠ AI analysis failed. Please try again later."

# ==============================
# RUN SCAN
# ==============================
if st.button("🔍 Run Security Scan"):

    if not dockerfile_content.strip():
        st.warning("Upload a Dockerfile first.")
        st.stop()

    with st.spinner("Running Static Analysis..."):
        static_results = static_scan(dockerfile_content)
        risk_percent = calculate_risk(static_results)
        time.sleep(1)

    st.subheader("📊 Static Results")
    st.progress(risk_percent / 100)
    st.write(f"Overall Risk Score: {risk_percent}%")

    for check, status in static_results:
        if status == "PASS":
            st.success(check)
        elif status == "WARNING":
            st.warning(check)
        else:
            st.error(check)

    st.divider()

    st.subheader("🤖 AI Expert Review")
    with st.spinner("AI analyzing..."):
        ai_text = ai_analysis(dockerfile_content)
    st.markdown(ai_text)

# ==============================
# FOOTER
# ==============================
st.caption("Enterprise Docker Security Auditor | Production Ready | DevSecOps Tool")
