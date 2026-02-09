# 🐳 Docker Image Security Auditor

A **Streamlit-based security auditing dashboard** that analyzes Dockerfiles and highlights common security risks and bad practices. This tool helps developers, students, and DevOps engineers quickly review Dockerfile configurations before building images.

---

## 🚀 Features

* 📤 Upload and analyze any Dockerfile
* 🔍 Automated security checks based on best practices
* 📊 One-page risk summary with percentage score
* 🟢🟡🔴 Clear risk levels: LOW, MEDIUM, HIGH
* 📋 Detailed explanation for each security finding
* 🐳 Docker-focused checks aligned with real-world issues

---

## 🛡️ Security Checks Performed

The auditor currently checks the following:

1. **Base Image Defined** – Ensures a `FROM` instruction exists
2. **Avoid Using `latest` Tag** – Prevents unpredictable image updates
3. **Non-Root User** – Warns if container runs as root
4. **Healthcheck Present** – Detects missing container health checks
5. **COPY vs ADD** – Recommends safer `COPY` usage
6. **Port Exposure** – Flags unnecessary exposed ports
7. **Startup Command** – Ensures `CMD` or `ENTRYPOINT` is defined
8. **Secrets in ENV** – Detects potential secret leakage
9. **RUN Layer Optimization** – Warns about too many RUN layers
10. **APT Cache Cleanup** – Checks for proper package cache cleanup

Each check is marked as:

* 🟢 **PASS** – Secure configuration
* 🟡 **WARNING** – Needs attention
* 🔴 **CRITICAL** – High security risk

---

## 📦 Project Structure

```
├── app.py              # Main Streamlit application
├── Dockerfile          # container setup
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
```

---

## 🧑‍💻 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone <repository-url>
cd docker-image-security-auditor
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Application

```bash
streamlit run app.py
```

The app will open automatically in your browser (usually at `http://localhost:8501`).

---

## 🧪 How to Use

1. Launch the Streamlit app
2. Upload a Dockerfile using the file uploader
3. Click **🔍 Scan Dockerfile**
4. View:

   * Overall risk percentage
   * Risk level (Low / Medium / High)
   * Detailed findings with explanations


Developed as a learning-focused Docker security auditing tool using **Python + Streamlit**.
