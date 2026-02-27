import streamlit as st
from groq import Groq
import time
import re

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Docker Security Auditor", layout="wide")

# ==============================
# GROQ CLIENT
# ==============================
if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ GROQ_API_KEY not found in secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ==============================
# DARK UI FIX
# ==============================
st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}

.stApp {
    background:
    linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)),
    url("https://images.unsplash.com/photo-1518770660439-4636190af475");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

html, body, p, span, div, label, li, ul, ol, h1, h2, h3, h4 {
    color: #ffffff !important;
}

pre, code {
    background-color: #111111 !important;
    color: #00ff99 !important;
    border-radius: 12px !important;
}

div[data-testid="stFileUploaderDropzone"] {
    background: #111111 !important;
    border: 2px dashed #00ffff !important;
    border-radius: 20px !important;
    padding: 40px !important;
}

div[data-testid="stFileUploaderDropzone"] * {
    color: #ffffff !important;
}

.stButton > button {
    background: linear-gradient(90deg, #00ffff, #00ff99) !important;
    color: black !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    padding: 10px 25px !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# ==============================
# ==============================
# HEADER (Animated - No Text Change)
# ==============================
st.markdown("""
<style>
@keyframes glow {
    0% { text-shadow: 0 0 5px #00ffff; }
    50% { text-shadow: 0 0 25px #00ffff, 0 0 40px #00ff99; }
    100% { text-shadow: 0 0 5px #00ffff; }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animated-h1 {
    text-align:center;
    color:#00ffff;
    animation: glow 2s infinite ease-in-out, fadeIn 1.5s ease-in-out;
}

.animated-h4 {
    text-align:center;
    animation: fadeIn 2s ease-in-out;
}
</style>

<h1 class="animated-h1">🐳 Docker Image Security Auditor</h1>
<h4 class="animated-h4">Static + AI Powered Dockerfile Scanner</h4>
""", unsafe_allow_html=True)
# ==============================
# FILE UPLOAD
# ==============================
uploaded_file = st.file_uploader("📤 Upload Dockerfile", type=["txt", "Dockerfile"])

dockerfile_content = ""

if uploaded_file:
    dockerfile_content = uploaded_file.read().decode("utf-8")
    st.session_state["dockerfile"] = dockerfile_content
    st.subheader("📄 Uploaded Dockerfile")
    st.code(dockerfile_content, language="dockerfile")

# ==============================
# STATIC SCAN
# ==============================
def static_scan(dockerfile):

    checks = []

    checks.append(("Base image defined", "PASS" if "FROM" in dockerfile else "CRITICAL"))

    if ":latest" in dockerfile:
        checks.append(("Using latest tag", "CRITICAL"))
    else:
        checks.append(("No latest tag", "PASS"))

    if "USER" not in dockerfile:
        checks.append(("No non-root user", "CRITICAL"))
    else:
        checks.append(("Non-root user defined", "PASS"))

    if re.search(r"ENV\s+.*(PASSWORD|SECRET|KEY)", dockerfile, re.IGNORECASE):
        checks.append(("Hardcoded secrets detected", "CRITICAL"))
    else:
        checks.append(("No hardcoded secrets", "PASS"))

    if "curl" in dockerfile and "| bash" in dockerfile:
        checks.append(("Remote script execution (curl | bash)", "CRITICAL"))
    else:
        checks.append(("No remote script execution", "PASS"))

    if "ADD " in dockerfile:
        checks.append(("Using ADD instead of COPY", "WARNING"))
    else:
        checks.append(("Using COPY safely", "PASS"))

    if re.search(r"EXPOSE\s+(22|21|23)", dockerfile):
        checks.append(("Sensitive ports exposed", "WARNING"))
    else:
        checks.append(("No sensitive ports exposed", "PASS"))

    if "HEALTHCHECK" not in dockerfile:
        checks.append(("Missing HEALTHCHECK", "WARNING"))
    else:
        checks.append(("HEALTHCHECK present", "PASS"))

    return checks


# ==============================
# AI ANALYSIS
# ==============================
def ai_analysis(dockerfile):

    prompt = f"""
You are a Senior DevSecOps Engineer.

Analyze this Dockerfile and provide:
1. Overall Risk Percentage
2. Security Risks
3. Explanation
4. Recommended Fixes
5. Best Practices

Dockerfile:
{dockerfile[:4000]}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a Docker security expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
            timeout=30
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ AI Analysis Failed: {str(e)}"


# ==============================
# AUTO FIX
# ==============================
def auto_fix(dockerfile):

    prompt = f"""
Fix ALL security issues in this Dockerfile.
Return ONLY the improved secure Dockerfile code.
Do not add explanation.

Dockerfile:
{dockerfile[:4000]}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a Docker security expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500,
            timeout=30
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ AutoFix Failed: {str(e)}"


# ==============================
# RUN SCAN
# ==============================
if st.button("🔍 Run Full Security Scan"):

    if not dockerfile_content.strip():
        st.warning("⚠ Upload Dockerfile first")
    else:

        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.005)
            progress.progress(i + 1)

        results = static_scan(dockerfile_content)

        score_map = {"PASS": 0, "WARNING": 10, "CRITICAL": 30}
        risk_score = sum(score_map[s] for _, s in results)
        risk_percent = min(100, risk_score)

        st.subheader("📊 Static Analysis")
        st.markdown(f"### 🔥 Overall Risk: {risk_percent}%")
        st.progress(risk_percent / 100)

        for check, status in results:
            if status == "PASS":
                st.success(f"🟢 {check}")
            elif status == "WARNING":
                st.warning(f"🟡 {check}")
            else:
                st.error(f"🔴 {check}")

        st.divider()

        st.subheader("🤖 AI Security Expert Review")
        with st.spinner("Analyzing with Groq AI..."):
            ai_text = ai_analysis(dockerfile_content)

        st.markdown(ai_text)


# ==============================
# AUTO FIX SECTION
# ==============================
if "dockerfile" in st.session_state:

    st.subheader("🛠 Auto-Fix Dockerfile")

    if st.button("🚀 Generate Secure Dockerfile"):
        with st.spinner("Generating secure version..."):
            secure = auto_fix(st.session_state["dockerfile"])

        if secure.startswith("❌"):
            st.error(secure)
        else:
            st.success("✅ Secure Dockerfile Generated")
            st.code(secure, language="dockerfile")

    st.divider()
    st.caption("Enterprise Docker Security Auditor | Powered by Groq AI")
