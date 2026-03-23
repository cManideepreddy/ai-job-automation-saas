import os
import requests
import streamlit as st

# -------------------------
# CONFIG
# -------------------------
BACKEND_URL = os.getenv("BACKEND_URL")

if not BACKEND_URL:
    try:
        BACKEND_URL = st.secrets["BACKEND_URL"]
    except Exception:
        BACKEND_URL = "https://applypilot-backend.onrender.com"

st.set_page_config(page_title="ApplyPilot AI", page_icon="🚀", layout="wide")

# -------------------------
# STYLING
# -------------------------
st.markdown("""
<style>
.hero {
    padding: 20px;
    background: linear-gradient(135deg, #1d4ed8, #0f172a);
    color: white;
    border-radius: 15px;
}
.card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    margin-bottom: 15px;
}
.pill {
    display:inline-block;
    padding:5px 10px;
    margin:3px;
    border-radius:20px;
    background:#eff6ff;
    color:#1d4ed8;
}
.pill-warn {
    display:inline-block;
    padding:5px 10px;
    margin:3px;
    border-radius:20px;
    background:#fff7ed;
    color:#c2410c;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# SESSION
# -------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "email" not in st.session_state:
    st.session_state.email = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "ats" not in st.session_state:
    st.session_state.ats = None
if "jobs" not in st.session_state:
    st.session_state.jobs = []

# -------------------------
# HELPERS
# -------------------------
def safe_post(url, **kwargs):
    try:
        return requests.post(url, timeout=120, **kwargs)
    except Exception as e:
        st.error(str(e))
        return None

def pills(items, warn=False):
    if not items:
        st.write("—")
        return
    cls = "pill-warn" if warn else "pill"
    html = "".join([f'<span class="{cls}">{i}</span>' for i in items])
    st.markdown(html, unsafe_allow_html=True)

# -------------------------
# SIDEBAR LOGIN
# -------------------------
st.sidebar.title("ApplyPilot AI")

menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Account", menu)

if choice == "Signup" and not st.session_state.user_id:
    email = st.sidebar.text_input("Email")
    pwd = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Signup"):
        res = safe_post(f"{BACKEND_URL}/signup", json={"email": email, "password": pwd})
        if res:
            st.sidebar.success(res.json().get("message"))

elif choice == "Login" and not st.session_state.user_id:
    email = st.sidebar.text_input("Email")
    pwd = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        res = safe_post(f"{BACKEND_URL}/login", json={"email": email, "password": pwd})
        if res:
            data = res.json()
            if data.get("status") == "success":
                st.session_state.user_id = data["user_id"]
                st.session_state.email = data["email"]
                st.rerun()
            else:
                st.sidebar.error(data["message"])

if st.session_state.user_id:
    st.sidebar.success(f"Logged in\n{st.session_state.email}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

# -------------------------
# HERO
# -------------------------
st.markdown("""
<div class="hero">
<h2>🚀 ApplyPilot AI</h2>
<p>Upload once. Match smarter. Get hired faster.</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.user_id:
    st.info("Login to continue")
    st.stop()

# -------------------------
# STEP 1 UPLOAD
# -------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("1. Upload Resume")

file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

if file:
    res = safe_post(f"{BACKEND_URL}/upload-resume",
                    files={"file": (file.name, file.getvalue())})
    if res:
        data = res.json()
        st.session_state.resume_text = data.get("resume_text", "")
        st.success("Uploaded successfully")
        st.text_area("Preview", st.session_state.resume_text, height=150)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# STEP 2 JOB DESC
# -------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("2. Job Description")

jd = st.text_area("Paste Job Description")

col1, col2 = st.columns(2)
analyze = col1.button("🔍 Analyze Resume")
match = col2.button("🎯 Find Jobs")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# ATS
# -------------------------
if analyze:
    if not st.session_state.resume_text:
        st.warning("Upload resume first")
    else:
        res = safe_post(f"{BACKEND_URL}/analyze-ats",
                        data={"resume_text": st.session_state.resume_text,
                              "job_description": jd,
                              "email": st.session_state.email})
        if res:
            st.session_state.ats = res.json()

if st.session_state.ats:
    basic = st.session_state.ats.get("basic_analysis", {})
    ai = st.session_state.ats.get("ai_analysis", {})

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("3. ATS Analysis")

    score = basic.get("ats_score", 0)
    st.metric("ATS Score", f"{score}/100")

    if score < 50:
        st.error("Low score")
    elif score < 75:
        st.warning("Average score")
    else:
        st.success("Excellent score")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Strengths")
        for i in basic.get("pros", []) + ai.get("pros", []):
            st.write("•", i)

    with col2:
        st.write("### Weaknesses")
        for i in basic.get("cons", []) + ai.get("cons", []):
            st.write("•", i)

    st.write("### Missing Skills")
    pills(basic.get("missing_keywords", []), True)

    st.write("### Suggestions")
    for i in basic.get("suggestions", []) + ai.get("suggestions", []):
        st.write("•", i)

    st.write("### Summary")
    st.write(ai.get("summary", ""))

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# JOB MATCH
# -------------------------
if match:
    res = safe_post(f"{BACKEND_URL}/match-jobs",
                    data={"resume_text": st.session_state.resume_text})
    if res:
        st.session_state.jobs = res.json().get("top_matches", [])

if st.session_state.jobs:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("4. Matching Jobs")
    st.markdown('</div>', unsafe_allow_html=True)

    for job in st.session_state.jobs:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.write(f"### {job['title']} - {job['company']}")
        st.write("Score:", job["match_score"])

        pills(job.get("matched_skills", []))
        pills(job.get("missing_skills", []), True)

        title = job["title"]

        st.markdown(f"[LinkedIn](https://www.linkedin.com/jobs/search/?keywords={title})")
        st.markdown(f"[Indeed](https://www.indeed.com/jobs?q={title})")
        st.markdown(f"[Naukri](https://www.naukri.com/{title}-jobs)")

        if job.get("link"):
            st.markdown(f"👉 [Apply Direct]({job['link']})")

        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# RESUME IMPROVE
# -------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("5. Improve Resume")

if st.button("🚀 Improve Resume"):
    res = safe_post(f"{BACKEND_URL}/rewrite-resume",
                    data={"resume_text": st.session_state.resume_text,
                          "job_description": jd})
    if res:
        st.text_area("Improved Resume", res.json().get("improved_resume", ""), height=300)

st.markdown('</div>', unsafe_allow_html=True)