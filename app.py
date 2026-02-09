import streamlit as st

# ---------- Page Setup ----------
st.set_page_config(page_title="Docker Image Security Auditor", layout="wide")

st.title("🐳 Docker Image Security Auditor Dashboard")
st.write("Upload a Dockerfile to perform automated security audit analysis.")

# ---------- Upload Dockerfile ----------
uploaded_file = st.file_uploader("📤 Upload Dockerfile", type=["txt", "Dockerfile"])

dockerfile_content = ""

if uploaded_file is not None:
    dockerfile_content = uploaded_file.read().decode("utf-8")

    st.subheader("📄 Uploaded Dockerfile")
    st.code(dockerfile_content, language="dockerfile")

# ---------- Risk Description Dictionary ----------
risk_description = {
    "Base image defined": "Missing base image makes Dockerfile invalid and insecure.",
    "Avoid using latest tag": "Using latest tag can introduce unknown vulnerabilities.",
    "Non-root user configured": "Running container as root increases attack impact.",
    "Healthcheck present": "Without healthcheck, container failure may go undetected.",
    "COPY preferred over ADD": "ADD can unintentionally pull external or unwanted files.",
    "Port exposure limited": "Exposing ports increases external attack surface.",
    "Startup command defined": "Missing CMD or ENTRYPOINT can break container runtime.",
    "Secrets in ENV": "Secrets stored in ENV can be extracted from image layers.",
    "RUN layers optimized": "Too many RUN layers increase attack surface and image size.",
    "APT cache cleaned": "Uncleaned cache may contain outdated vulnerable packages."
}

# ---------- Audit Function ----------
def audit_dockerfile(dockerfile):
    results = [
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
    return results

# ---------- Scan Button ----------
if st.button("🔍 Scan Dockerfile"):

    if dockerfile_content.strip() == "":
        st.warning("⚠ Please upload Dockerfile first")
    else:
        st.subheader("📊 One Page Security Audit Report")

        results = audit_dockerfile(dockerfile_content)

        # ---------- Risk Score ----------
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

        # ---------- Detailed 10-Line Report ----------
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
        st.caption("Docker Image Security Auditor Report")