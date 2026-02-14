import streamlit as st
from groq import Groq
import logging
import os
import time
from datetime import datetime
from io import BytesIO

# ==============================
# CONFIGURATION
# ==============================
st.set_page_config(
    page_title="Docker Security Auditor",
    layout="wide",
    page_icon="🐳"
)

# Logging setup (Production style)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Secure API Key Load
if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ GROQ_API_KEY not found in secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ==============================
# STYLING (Clean Professional)
# ==============================
st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
.stApp { background-color: #0e1117; }
h1, h2, h3, h4 { color: #00ffff; }
div[data-testid="stFileUploaderDropzone"] {
    background: #1c1f26;
    border: 2px dashed #00ffff;
    border-radius: 12px;
    padding: 35px;
}
div[data-testid="stFileUploaderDropzone"] p {
    color: white !important;
    font-weight: 600;
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
uploaded_file = st.file_uploader("Upload Dockerfile", type=["txt", "Dockerfile"])

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
# STATIC SCANNER (Improved)
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

# ==============================
# RISK CALCULATION
# ==============================
def calculate_risk(results):
    score_map = {"PASS": 0, "WARNING": 5, "CRITICAL": 15}
    total_score = sum(score_map[r[1]] for r in results)
    return min(100, total_score)

# ==============================
# AI ANALYSIS (Protected)
# ==============================
def ai_analysis(dockerfile: str):

    dockerfile = dockerfile[:3500]

    prompt = f"""
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
            max_tokens=1000,
            timeout=30
        )

        return response.choices[0].message.content

    except Exception as e:
        logging.error(str(e))
        return "⚠ AI analysis failed. Please try again later."

# ==============================
# AUTO FIX
# ==============================
def generate_secure_dockerfile(dockerfile: str):

    prompt = f"""
Fix all security issues in this Dockerfile.
Return ONLY the improved Dockerfile.

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
            temperature=0.2,
            max_tokens=1000,
            timeout=30
        )

        return response.choices[0].message.content

    except Exception as e:
        logging.error(str(e))
        return None

# ==============================
# DOWNLOAD REPORT
# ==============================
def generate_report(dockerfile, static_results, ai_text, risk_percent):
    report = f"""
DOCKER SECURITY AUDIT REPORT
Generated: {datetime.now()}

Overall Risk: {risk_percent}%

STATIC ANALYSIS:
"""
    for check, status in static_results:
        report += f"- {check}: {status}\n"

    report += "\nAI ANALYSIS:\n"
    report += ai_text

    return report

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

    st.subheader("📊 Static Results")
    st.progress(risk_percent / 100)
    st.write(f"Overall Risk Score: {risk_percent}%")

    for check, status in static_results:
        if status == "PASS":
            st.success(f"{check}")
        elif status == "WARNING":
            st.warning(f"{check}")
        else:
            st.error(f"{check}")

    st.divider()

    st.subheader("🤖 AI Expert Review")
    with st.spinner("AI analyzing..."):
        ai_text = ai_analysis(dockerfile_content)
    st.markdown(ai_text)

    st.divider()

    # AUTO FIX
    st.subheader("🛠 Auto-Fix")
    if st.button("Generate Secure Dockerfile"):
        with st.spinner("Generating..."):
            secure_file = generate_secure_dockerfile(dockerfile_content)

        if secure_file:
            st.code(secure_file, language="dockerfile")

            st.download_button(
                label="⬇ Download Secure Dockerfile",
                data=secure_file,
                file_name="secure_Dockerfile",
                mime="text/plain"
            )

    st.divider()

    # DOWNLOAD REPORT
    report_text = generate_report(dockerfile_content, static_results, ai_text, risk_percent)

    st.download_button(
        label="📄 Download Security Report",
        data=report_text,
        file_name="security_report.txt",
        mime="text/plain"
    )

# ==============================
# FOOTER
# ==============================
st.caption("Enterprise Docker Security Auditor | Production Ready | DevSecOps Tool")
