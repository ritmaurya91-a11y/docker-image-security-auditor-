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

/* Background */
.stApp {
    background:
    linear-gradient(to bottom, rgba(0,0,0,0.85), rgba(0,0,0,0.95)),
    url("https://images.unsplash.com/photo-1518770660439-4636190af475");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Force ALL text white */
html, body, [class*="css"] {
    color: white !important;
}

/* Title */
.title {
    font-size: 50px;
    font-weight: 900;
    text-align: center;
    color: #00ffff !important;
    text-shadow: 0 0 15px rgba(0,255,255,0.8);
}

.subtitle {
    text-align: center;
    font-size: 20px;
    color: #ffffff !important;
    margin-bottom: 35px;
}

/* Upload box styling */
section[data-testid="stFileUploader"] > div {
    background-color: rgba(25,25,25,0.85) !important;
    border-radius: 15px;
    padding: 20px;
    color: white !important;
}

/* Upload label */
section[data-testid="stFileUploader"] label {
    color: white !important;
    font-weight: 600;
}

/* Uploaded filename */
span {
    color: white !important;
}

/* Code block */
pre {
    background: #0d1117 !important;
    color: #ffffff !important;
    border-radius: 12px;
}

/* Status boxes */
.stSuccess {background-color: rgba(0,150,0,0.25) !important;}
.stWarning {background-color: rgba(255,165,0,0.25) !important;}
.stError {background-color: rgba(255,0,0,0.25) !important;}

/* Progress bar */
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
        ("Running as non-root user", "PASS" if "USER root" not in dockerfile else "CRITICAL"),
        ("Healthcheck present", "PASS" if "HEALTHCHECK" in dockerfile else "WARNING"),
        ("Secrets in ENV", "PASS" if "SECRET" not in dockerfile else "CRITICAL"),
    ]

# ---------- AI Analysis ----------
def ai_security_analysis(dockerfile):

    dockerfile = dockerfile[:4000]

    prompt = f"""
You are a Senior DevSecOps Engineer.

Analyze this Dockerfile and provide:

1. Overall Risk Percentage (0-100%)
2. Security Risks (LOW/MEDIUM/HIGH)
3. Short description of each risk
4. Recommended Fix for each issue
5. Best practice improvements

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
            max_tokens=1500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ AI Error: {str(e)}"

# ---------- Scan ----------
if st.button("🔍 Run Full Security Scan"):

    if not dockerfile_content.strip():
        st.warning("⚠ Please upload Dockerfile first")
    else:

        # Static Scan
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

        # AI Scan
        st.subheader("🤖 AI Security Expert Analysis")

        with st.spinner("AI analyzing Dockerfile..."):
            ai_report = ai_security_analysis(dockerfile_content)

        st.markdown(ai_report)

        st.divider()
        st.caption("Docker Image Security Auditor | AI Powered by Groq")

