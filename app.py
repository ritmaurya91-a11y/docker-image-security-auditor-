import streamlit as st

# ---------- Page Setup ----------
st.set_page_config(page_title="Docker Image Security Auditor", layout="wide")

# ---------- Custom Styling ----------
st.markdown("""
<style>

/* Remove Streamlit default header/footer */
header {visibility: hidden;}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

.block-container {
    padding-top: 1rem;
}

/* Background with smooth dark overlay */
.stApp {
    background:
    linear-gradient(to bottom, rgba(0,0,0,0.4), rgba(0,0,0,0.8)),
    url("https://images.unsplash.com/photo-1518770660439-4636190af475");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Glass effect container */
.glass {
    background: rgba(20, 20, 20, 0.75);
    padding: 40px;
    border-radius: 20px;
    backdrop-filter: blur(8px);
    box-shadow: 0 0 30px rgba(0,255,255,0.2);
}

/* Title styling */
.title {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    color: #00ffff;
    text-shadow: 2px 2px 10px black;
}

/* Subtitle styling */
.subtitle {
    text-align: center;
    font-size: 20px;
    color: white;
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

if uploaded_file is not None:
    dockerfile_content = uploaded_file.read().decode("utf-8")
    st.subheader("📄 Uploaded Dockerfile")
    st.code(dockerfile_content, language="dockerfile")

# ---------- Risk Description ----------
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
    "APT cache cleaned": "APT cache must be cleaned to avoid vulnerabilities."
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

    if dockerfile_content.strip() == "":
        st.warning("⚠ Please upload Dockerfile first")
    else:
        st.subheader("📊 One Page Security Audit Report")

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

        st.divider()

        st.subheader("📋 Detailed Security Findings")

        for check, status in results:
            if status == "PASS":
                st.success(f"🟢 {check} → Secure configuration detected")

            elif status == "WARNING":
                st.warning(
                    f"🟡 {check}\n\n"
                    f"👉 {risk_description.get(check)}"
                )

            else:
                st.error(
                    f"🔴 {check}\n\n"
                    f"👉 {risk_description.get(check)}"
                )

        st.divider()
        st.caption("Docker Image Security Auditor | Secure Your Containers")

st.markdown('</div>', unsafe_allow_html=True)
