import streamlit as st
from groq import Groq

# ---------- API Setup ----------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ---------- Page Setup ----------
st.set_page_config(page_title="Docker Image Security Auditor", layout="wide")

# ---------- Custom Styling ----------
st.markdown("""
<style>
header, footer, #MainMenu {visibility: hidden;}
.block-container {padding-top: 1.5rem;}

.stApp {
    background:
    linear-gradient(to bottom, rgba(0,0,0,0.75), rgba(0,0,0,0.9)),
    url("https://images.unsplash.com/photo-1518770660439-4636190af475");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.title {
    font-size: 50px;
    font-weight: 900;
    text-align: center;
    color: #00ffff;
    text-shadow: 0 0 12px rgba(0,255,255,0.8);
}

.subtitle {
    text-align: center;
    font-size: 20px;
    color: #e0e0e0;
    margin-bottom: 35px;
}

h2, h3, h4 {
    color: #ffffff !important;
}

pre {
    background: #0d1117 !important;
    color: #ffffff !important;
    border-radius: 12px;
}

.stSuccess {
    background-color: rgba(0, 150, 0, 0.25) !important;
    color: #eaffea !important;
}

.stWarning {
    background-color: rgba(255, 165, 0, 0.25) !important;
    color: #fff4d6 !important;
}

.stError {
    background-color: rgba(255, 0, 0, 0.25) !important;
    color: #ffe6e6 !important;
}

.stProgress > div > div {
    background-color: #00ffff !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="title">🐳 Docker Image Security Auditor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Static + AI Powered Dockerfile Security Scanner</div>', unsafe_allow_html=True)

# ---------- Upload ----------
uploaded_file = st.file_uploader("📤 Upload Dockerfile", type=["txt", "Dockerfile"])

dockerfile_content = ""

if uploaded_file:
    dockerfile_content = uploaded_file.read().decode("utf-8")
    st.subheader("📄 Uploaded Dockerfile")
    st.code(dockerfile_content, language="dockerfile")

# ---------- Static Audit ----------
def audit_dockerfile(dockerfile):
    return [
        ("Base image defined", "PASS" if "FROM" in dockerfile else "CRITICAL"),
        ("Avoid using latest tag", "PASS" if ":latest" not in dockerfile else "WARNING"),
        ("Non-root user configured", "PASS" if "USER root" not in dockerfile else "CRITICAL"),
        ("Healthcheck present", "PASS" if "HEALTHCHECK" in dockerfile else "WARNING"),
        ("Secrets in ENV", "PASS" if "SECRET" not in dockerfile else "CRITICAL"),
    ]

# ---------- AI Analysis ----------
def ai_security_analysis(dockerfile):

    prompt = f"""
You are a senior DevSecOps engineer.

Analyze this Dockerfile and provide:

1. Security Risks (with severity: LOW/MEDIUM/HIGH)
2. Configuration Errors
3. Recommended Fix for each issue
4. Separate explanation of each issue
5. Best practice improvements

Dockerfile:
{dockerfile}
"""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a Docker security expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content

# ---------- Scan ----------
if st.button("🔍 Run Full Security Scan"):

    if not dockerfile_content.strip():
        st.warning("⚠ Please upload Dockerfile first")
    else:

        # ----- Static Scan -----
        st.subheader("📊 Static Security Analysis")
        results = audit_dockerfile(dockerfile_content)

        score_map = {"PASS": 0, "WARNING": 5, "CRITICAL": 10}
        risk_score = sum(score_map[s] for _, s in results)
        risk_percent = min(100, risk_score)

        st.markdown(f"### 🔐 Overall Risk Level: **{risk_percent}%**")
        st.progress(risk_percent / 100)

        if risk_percent < 30:
            st.success("🟢 LOW RISK")
        elif risk_percent < 60:
            st.warning("🟡 MEDIUM RISK")
        else:
            st.error("🔴 HIGH RISK")

        for check, status in results:
            if status == "PASS":
                st.success(f"🟢 {check}")
            elif status == "WARNING":
                st.warning(f"🟡 {check}")
            else:
                st.error(f"🔴 {check}")

        st.divider()

        # ----- AI Scan -----
        st.subheader("🤖 AI Security Expert Analysis")

        with st.spinner("AI analyzing Dockerfile using Groq..."):
            ai_report = ai_security_analysis(dockerfile_content)

        st.markdown(ai_report)

        st.divider()
        st.caption("Docker Image Security Auditor | AI Powered by Groq")
