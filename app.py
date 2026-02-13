import streamlit as st

# ---------- Page Setup ----------
st.set_page_config(page_title="Docker Image Security Auditor", layout="wide")

# ---------- Premium Styling ----------
st.markdown("""
<style>

/* Hide Streamlit default menu */
header {visibility: hidden;}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

.block-container {
    padding-top: 1rem;
}

/* Cyber Background */
.stApp {
    background:
    linear-gradient(to bottom, rgba(0,0,0,0.5), rgba(0,0,0,0.85)),
    url("https://images.unsplash.com/photo-1518770660439-4636190af475");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Force White Text */
html, body, [class*="css"]  {
    color: white !important;
}

/* Glass Container */
.glass {
    background: rgba(20,20,20,0.75);
    padding: 40px;
    border-radius: 20px;
    backdrop-filter: blur(8px);
    box-shadow: 0 0 25px rgba(0,255,255,0.3);
}

/* Animated Gradient Title */
.title {
    font-size: 52px;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg, #00ffff, #00ff99, #00ffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glow 3s infinite alternate;
}

@keyframes glow {
    from {text-shadow: 0 0 10px #00ffff;}
    to {text-shadow: 0 0 25px #00ffcc;}
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 20px;
    margin-bottom: 30px;
}

</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="title">🐳 Docker Image Security Auditor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Automated Dockerfile Static Security Scanner Dashboard</div>', unsafe_allow_html=True)

st.markdown('<div class="glass">', unsafe_allow_html=True)

# ---------- Upload ----------
uploaded_file = st.file_uploader("📤 Upload Dockerfile", type=["txt", "Dockerfile"])

dockerfile_content = ""

if uploaded_file:
    dockerfile_content = uploaded_file.read().decode("utf-8")
    st.subheader("📄 Uploaded Dockerfile")
    st.code(dockerfile_content, language="dockerfile")

# ---------- Risk Descriptions ----------
risk_description = {
    "Base image defined": "Dockerfile must define a secure base image.",
    "Avoid using latest tag": "Using latest tag may introduce unknown vulnerabilities.",
    "Non-root user configured": "Running container as root increases attack impact.",
    "Healthcheck present": "Healthcheck ensures container reliability.",
    "COPY preferred over ADD": "ADD may introduce unintended files.",
    "Port exposure limited": "Exposed ports increase attack surface.",
    "Startup command defined": "Container must define CMD or ENTRYPOINT.",
    "Secrets in ENV": "Secrets in ENV can leak sensitive data.",
    "RUN layers optimized": "Too many RUN layers increase image size.",
    "APT cache cleaned": "APT cache must be cleaned."
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

        st.subheader("📊 Risk Overview")
        st.markdown(f"### 🔐 Overall Risk Score: {risk_percent}%")
        st.progress(risk_percent / 100)

        # Pie Chart
        status_counts = {
            "PASS": sum(1 for _, s in results if s == "PASS"),
            "WARNING": sum(1 for _, s in results if s == "WARNING"),
            "CRITICAL": sum(1 for _, s in results if s == "CRITICAL"),
        }

        fig, ax = plt.subplots()
        ax.pie(status_counts.values(),
               labels=status_counts.keys(),
               autopct='%1.1f%%')
        ax.axis('equal')
        st.pyplot(fig)

        st.divider()
        st.subheader("📋 Detailed Findings")

        for check, status in results:
            if status == "PASS":
                st.success(f"🟢 {check}")
            elif status == "WARNING":
                st.warning(f"🟡 {check}\n\n👉 {risk_description[check]}")
            else:
                st.error(f"🔴 {check}\n\n👉 {risk_description[check]}")

        st.caption("Docker Image Security Auditor | DevSecOps Tool")

st.markdown('</div>', unsafe_allow_html=True)
