import streamlit as st

# ---------- Page Setup ----------
st.set_page_config(page_title="Docker Image Security Auditor", layout="wide")

# ---------- Stylish Background ----------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(rgba(0,0,0,0.65), rgba(0,0,0,0.65)),
    url("https://images.unsplash.com/photo-1518770660439-4636190af475");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Remove top extra spacing */
.block-container {
    padding-top: 2rem;
}


/* Title */
.title {
    font-size: 48px;
    font-weight: 700;
    text-align: center;
    color: #00e5ff;
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 20px;
    color: #ffffff;
    margin-bottom: 30px;
}

/* Footer */
.footer {
    text-align: center;
    color: #cccccc;
    margin-top: 40px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


st.markdown('<div class="title">🐳 Docker Image Security Auditor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Automated Dockerfile Static Security Scanner Dashboard</div>', unsafe_allow_html=True)

st.divider()

# ---------- Upload ----------
uploaded_file = st.file_uploader("📤 Upload Dockerfile", type=["txt", "Dockerfile"])

dockerfile_content = ""

if uploaded_file:
    dockerfile_content = uploaded_file.read().decode("utf-8")
    st.subheader("📄 Uploaded Dockerfile")
    st.code(dockerfile_content, language="dockerfile")

# ---------- Risk Dictionary ----------
risk_description = {
    "Base image defined": "Missing base image makes Dockerfile invalid and insecure.",
    "Avoid using latest tag": "Using latest tag can introduce unknown vulnerabilities.",
    "Non-root user configured": "Running container as root increases attack impact.",
    "Healthcheck present": "Without healthcheck, container failure may go undetected.",
    "COPY preferred over ADD": "ADD can unintentionally pull external or unwanted files.",
    "Port exposure limited": "Exposing ports increases external attack surface.",
    "Startup command defined": "Missing CMD or ENTRYPOINT can break container runtime.",
    "Secrets in ENV": "Secrets stored in ENV can be extracted from image layers.",
    "RUN layers optimized": "Too many RUN layers increase attack surface.",
    "APT cache cleaned": "Uncleaned cache may contain outdated vulnerable packages."
}

# ---------- Audit Function ----------
def audit_dockerfile(dockerfile):
    return [
        ("Base image defined", "PASS" if "FROM" in dockerfile else "CRITICAL"),
        ("Avoid using latest tag", "PASS" if ":latest" not in dockerfile else "WARNING"),
        ("Non-root user configured", "PASS" if "USER root" not in dockerfile else "CRITICAL"),
        ("Healthcheck present", "PASS" if "HEALTHCHECK" in dockerfile else "WARNING"),
        ("COPY preferred over ADD", "PASS" if "ADD " not in dockerfile else "WARNING"),
        ("Port exposure limited", "PASS" if "EXPOSE" in dockerfile else "WARNING"),
        ("Startup command defined", "PASS" if ("CMD" in dockerfile or "ENTRYPOINT" in dockerfile) else "CRITICAL"),
        ("Secrets in ENV", "PASS" if "SECRET" not in dockerfile else "CRITICAL"),
        ("RUN layers optimized", "PASS" if dockerfile.count("RUN") <= 5 else "WARNING"),
        ("APT cache cleaned", "PASS" if "rm -rf /var/lib/apt/lists" in dockerfile else "CRITICAL"),
    ]

# ---------- Scan ----------
if st.button("🔍 Scan Dockerfile"):

    if not dockerfile_content.strip():
        st.warning("⚠ Please upload Dockerfile first")
    else:
        results = audit_dockerfile(dockerfile_content)

        score_map = {"PASS": 0, "WARNING": 5, "CRITICAL": 10}
        risk_percent = min(100, sum(score_map[s] for _, s in results))

        st.subheader("📊 Security Risk Overview")
        st.markdown(f"### 🔐 Overall Risk Score: {risk_percent}%")
        st.progress(risk_percent / 100)

        if risk_percent < 30:
            st.success("🟢 LOW RISK – Secure configuration detected.")
        elif risk_percent < 60:
            st.warning("🟡 MEDIUM RISK – Improvements recommended.")
        else:
            st.error("🔴 HIGH RISK – Critical misconfigurations found.")

        st.divider()
        st.subheader("📋 Detailed Findings")

        for check, status in results:
            if status == "PASS":
                st.success(f"🟢 {check}")
            elif status == "WARNING":
                st.warning(f"🟡 {check}\n\n👉 {risk_description[check]}")
            else:
                st.error(f"🔴 {check}\n\n👉 {risk_description[check]}")

        st.markdown('<div class="footer">Docker Image Security Auditor • DevSecOps Tool • Internship Project</div>', unsafe_allow_html=True)

# ---------- Glass End ----------
st.markdown('</div>', unsafe_allow_html=True)
