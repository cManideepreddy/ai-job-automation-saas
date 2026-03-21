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

st.set_page_config(
    page_title="ApplyPilot AI",
    page_icon="🚀",
    layout="wide"
)

# -------------------------
# CUSTOM STYLING
# -------------------------
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .hero {
        padding: 1.2rem 1.4rem;
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
        color: white;
        border-radius: 18px;
        margin-bottom: 1rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 2rem;
    }
    .hero p {
        margin: 0.4rem 0 0 0;
        color: #dbeafe;
        font-size: 1rem;
    }
    .section-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1rem 1rem 0.8rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
    }
    .small-muted {
        color: #64748b;
        font-size: 0.9rem;
    }
    .pill {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        margin: 0.15rem 0.2rem 0.15rem 0;
        border-radius: 999px;
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        font-size: 0.85rem;
    }
    .pill-warn {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        margin: 0.15rem 0.2rem 0.15rem 0;
        border-radius: 999px;
        background: #fff7ed;
        color: #c2410c;
        border: 1px solid #fed7aa;
        font-size: 0.85rem;
    }
    .job-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
    }
    .score-good {
        color: #047857;
        font-weight: 700;
    }
    .score-mid {
        color: #b45309;
        font-weight: 700;
    }
    .score-low {
        color: #b91c1c;
        font-weight: 700;
    }
    .subtle-line {
        border-top: 1px solid #e2e8f0;
        margin: 0.7rem 0 0.4rem 0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------
# SESSION STATE
# -------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "email" not in st.session_state:
    st.session_state.email = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "last_ats_result" not in st.session_state:
    st.session_state.last_ats_result = None
if "last_job_matches" not in st.session_state:
    st.session_state.last_job_matches = []

# -------------------------
# HELPERS
# -------------------------
def safe_post(url: str, **kwargs):
    try:
        return requests.post(url, timeout=120, **kwargs)
    except Exception as e:
        st.error(f"API request failed: {str(e)}")
        return None

def render_pills(items, warn=False):
    if not items:
        st.write("—")
        return
    class_name = "pill-warn" if warn else "pill"
    html = "".join([f'<span class="{class_name}">{item}</span>' for item in items])
    st.markdown(html, unsafe_allow_html=True)

def render_list_block(title, items, empty_text="No items available."):
    st.markdown(f"**{title}**")
    if items:
        for item in items:
            st.write(f"• {item}")
    else:
        st.write(empty_text)

def score_class(score: int):
    if score >= 75:
        return "score-good"
    if score >= 45:
        return "score-mid"
    return "score-low"

# -------------------------
# SIDEBAR AUTH
# -------------------------
st.sidebar.title("ApplyPilot AI")
st.sidebar.caption("Smart ATS + Job Matching")

menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Account", menu)

if choice == "Signup" and not st.session_state.user_id:
    st.sidebar.subheader("Create account")
    signup_email = st.sidebar.text_input("Email", key="signup_email")
    signup_password = st.sidebar.text_input("Password", type="password", key="signup_password")

    if st.sidebar.button("Signup"):
        res = safe_post(
            f"{BACKEND_URL}/signup",
            json={"email": signup_email, "password": signup_password}
        )
        if res is not None:
            data = res.json()
            if data.get("status") == "success":
                st.sidebar.success("Account created. Please login.")
            else:
                st.sidebar.error(data.get("message", "Signup failed."))

elif choice == "Login" and not st.session_state.user_id:
    st.sidebar.subheader("Login")
    login_email = st.sidebar.text_input("Email", key="login_email")
    login_password = st.sidebar.text_input("Password", type="password", key="login_password")

    if st.sidebar.button("Login"):
        res = safe_post(
            f"{BACKEND_URL}/login",
            json={"email": login_email, "password": login_password}
        )
        if res is not None:
            data = res.json()
            if data.get("status") == "success":
                st.session_state.user_id = data.get("user_id")
                st.session_state.email = data.get("email")
                st.sidebar.success("Login successful.")
                st.rerun()
            else:
                st.sidebar.error(data.get("message", "Login failed."))

if st.session_state.user_id:
    st.sidebar.success(f"Logged in as\n\n**{st.session_state.email}**")
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.email = None
        st.session_state.resume_text = ""
        st.session_state.last_ats_result = None
        st.session_state.last_job_matches = []
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Tips**")
st.sidebar.write("Use a targeted job description for the most accurate ATS score.")
st.sidebar.write("Upload PDF or DOCX resumes for best results.")

# -------------------------
# HERO
# -------------------------
st.markdown("""
<div class="hero">
    <h1>🚀 ApplyPilot AI</h1>
    <p>Upload once. Match smarter. Get hired faster.</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="small-muted">A guided resume analysis and job matching experience designed to feel like a real SaaS product.</div>',
    unsafe_allow_html=True
)

st.markdown("")

# -------------------------
# REQUIRE LOGIN
# -------------------------
if not st.session_state.user_id:
    st.info("Please login or create an account from the sidebar to continue.")
    st.stop()

# -------------------------
# STEP 1 - UPLOAD RESUME
# -------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("1. Upload Resume")
uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])

if uploaded_file:
    with st.spinner("Uploading and parsing your resume..."):
        res = safe_post(
            f"{BACKEND_URL}/upload-resume",
            files={"file": (uploaded_file.name, uploaded_file.getvalue())}
        )

    if res is not None and res.status_code == 200:
        data = res.json()
        if data.get("error"):
            st.error(data["error"])
        else:
            st.session_state.resume_text = data.get("resume_text", "")
            st.success("Resume uploaded successfully.")
            st.text_area("Resume Preview", st.session_state.resume_text, height=180)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# STEP 2 - JOB DESCRIPTION
# -------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("2. Paste Job Description")
job_description = st.text_area(
    "Paste the target job description",
    height=220,
    placeholder="Paste the full job description here to get a more accurate ATS score and tailored recommendations..."
)

col_a, col_b = st.columns([1, 1])
with col_a:
    analyze_clicked = st.button("Analyze Resume")
with col_b:
    match_clicked = st.button("Find Matching Jobs")
st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# ATS ANALYSIS
# -------------------------
if analyze_clicked:
    if not st.session_state.resume_text:
        st.warning("Please upload a resume first.")
    elif not job_description.strip():
        st.warning("Please paste a job description first.")
    else:
        with st.spinner("Analyzing ATS fit and extracting insights..."):
            res = safe_post(
                f"{BACKEND_URL}/analyze-ats",
                data={
                    "resume_text": st.session_state.resume_text,
                    "job_description": job_description,
                    "email": st.session_state.email
                }
            )

        if res is not None and res.status_code == 200:
            st.session_state.last_ats_result = res.json()
        else:
            st.error("ATS analysis failed.")

# -------------------------
# JOB MATCHING
# -------------------------
if match_clicked:
    if not st.session_state.resume_text:
        st.warning("Please upload a resume first.")
    else:
        with st.spinner("Finding the best matching roles..."):
            res = safe_post(
                f"{BACKEND_URL}/match-jobs",
                data={"resume_text": st.session_state.resume_text}
            )

        if res is not None and res.status_code == 200:
            data = res.json()
            st.session_state.last_job_matches = data.get("top_matches", [])
        else:
            st.error("Job matching failed.")

# -------------------------
# ATS RESULT UI
# -------------------------
if st.session_state.last_ats_result:
    result = st.session_state.last_ats_result
    basic = result.get("basic_analysis", {})
    ai = result.get("ai_analysis", {})

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("3. ATS Score & Insights")

    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        st.metric("ATS Score", f"{basic.get('ats_score', 0)}/100")
    with c2:
        st.metric("Resume Domain", basic.get("resume_domain", "unknown"))
    with c3:
        st.metric("Job Domain", basic.get("job_domain", "unknown"))

    st.markdown('<div class="subtle-line"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Strengths")
        strengths = basic.get("pros", []) + ai.get("pros", [])
        render_list_block("What looks good", strengths, "No strengths generated yet.")

    with col2:
        st.markdown("### Weaknesses")
        weaknesses = basic.get("cons", []) + ai.get("cons", [])
        render_list_block("What needs attention", weaknesses, "No weaknesses generated yet.")

    st.markdown("### Missing Skills")
    missing_required = basic.get("missing_required_skills", []) or basic.get("missing_keywords", [])
    render_pills(missing_required, warn=True)

    st.markdown("### Suggestions")
    suggestions = basic.get("suggestions", []) + ai.get("suggestions", [])
    render_list_block("Recommended improvements", suggestions, "No suggestions generated yet.")

    st.markdown("### Summary")
    st.write(ai.get("summary") or basic.get("summary") or "No summary available.")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# JOB MATCH RESULT UI
# -------------------------
if st.session_state.last_job_matches:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("4. Matching Jobs")
    st.markdown('<div class="small-muted">Recommended roles based on your uploaded resume.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    for idx, job in enumerate(st.session_state.last_job_matches, start=1):
        score = int(job.get("match_score", 0))
        klass = score_class(score)

        st.markdown('<div class="job-card">', unsafe_allow_html=True)
        st.markdown(f"### {idx}. {job.get('title', 'N/A')} — {job.get('company', 'N/A')}")
        st.markdown(f'<div class="{klass}">Match Score: {score}%</div>', unsafe_allow_html=True)
        st.write(f"**Relevance:** {job.get('relevance', 'N/A')}")
        st.write(f"**Job Domain:** {job.get('job_domain', 'unknown')}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Matched Skills**")
            render_pills(job.get("matched_skills", []))
        with col2:
            st.markdown("**Missing Skills**")
            render_pills(job.get("missing_skills", []), warn=True)

        st.markdown("**Apply Options**")
        c1, c2, c3 = st.columns(3)

        title = job.get("title", "").strip()
        linkedin = job.get("linkedin") or f"https://www.linkedin.com/jobs/search/?keywords={title.replace(' ', '%20')}"
        indeed = job.get("indeed") or f"https://www.indeed.com/jobs?q={title.replace(' ', '+')}"
        naukri = job.get("naukri") or f"https://www.naukri.com/{title.replace(' ', '-')}-jobs"

        with c1:
            st.markdown(f"[LinkedIn]({linkedin})")
        with c2:
            st.markdown(f"[Indeed]({indeed})")
        with c3:
            st.markdown(f"[Naukri]({naukri})")

        if job.get("link"):
            st.markdown(f"👉 [Apply Direct]({job.get('link')})")

        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# OPTIONAL EMAIL ALERTS
# -------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("5. Email Alerts")
alert_email = st.text_input("Send matching jobs to email", value=st.session_state.email or "")

if st.button("Send Job Alerts"):
    if not st.session_state.resume_text:
        st.warning("Please upload a resume first.")
    elif not alert_email.strip():
        st.warning("Please enter an email address.")
    else:
        with st.spinner("Sending email alerts..."):
            res = safe_post(
                f"{BACKEND_URL}/send-job-alerts",
                data={
                    "email": alert_email,
                    "resume_text": st.session_state.resume_text
                }
            )

        if res is not None and res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                st.success(f"Email sent successfully. Jobs sent: {data.get('jobs_sent', 0)}")
            else:
                st.error(data.get("message", "Email sending failed."))
        else:
            st.error("Failed to send email alerts.")
st.markdown('</div>', unsafe_allow_html=True)