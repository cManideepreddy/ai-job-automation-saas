import os
import streamlit as st
import requests

# -------------------------
# CONFIG
# -------------------------
BACKEND_URL = os.getenv("BACKEND_URL")

if not BACKEND_URL:
    try:
        BACKEND_URL = st.secrets["BACKEND_URL"]
    except Exception:
        BACKEND_URL = "https://applypilot-backend.onrender.com"

st.set_page_config(page_title="ApplyPilot AI", layout="centered")

st.title("🚀 ApplyPilot AI")
st.caption("ATS Analysis • Smart Job Matching • Email Alerts")

st.write("Using backend:", BACKEND_URL)

# -------------------------
# SESSION STATE
# -------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "email" not in st.session_state:
    st.session_state.email = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "last_job_matches" not in st.session_state:
    st.session_state.last_job_matches = []

# -------------------------
# HELPERS
# -------------------------
def safe_post(url, **kwargs):
    try:
        return requests.post(url, timeout=300, **kwargs)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# -------------------------
# MENU
# -------------------------
menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Menu", menu)

# -------------------------
# SIGNUP
# -------------------------
if choice == "Signup" and not st.session_state.user_id:
    st.subheader("Signup")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):
        res = safe_post(f"{BACKEND_URL}/signup", json={"email": email, "password": password})

        if res:
            data = res.json()
            if data.get("status") == "success":
                st.success("Account created")
            else:
                st.error(data.get("message"))

# -------------------------
# LOGIN
# -------------------------
elif choice == "Login" and not st.session_state.user_id:
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = safe_post(f"{BACKEND_URL}/login", json={"email": email, "password": password})

        if res:
            data = res.json()
            if data.get("status") == "success":
                st.session_state.user_id = data.get("user_id")
                st.session_state.email = data.get("email")
                st.success("Login successful")
                st.rerun()
            else:
                st.error(data.get("message"))

# -------------------------
# MAIN APP
# -------------------------
if st.session_state.user_id:

    st.success(f"Logged in as {st.session_state.email}")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.divider()

    # -------------------------
    # 1. UPLOAD RESUME
    # -------------------------
    st.header("1. Upload Resume")

    file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

    if file:
        with st.spinner("Processing resume..."):
            res = safe_post(
                f"{BACKEND_URL}/upload-resume",
                files={"file": (file.name, file.getvalue())}
            )

        if res:
            data = res.json()
            st.session_state.resume_text = data.get("resume_text", "")

            st.success("Resume uploaded")
            st.text_area("Resume Text", st.session_state.resume_text, height=200)

    st.divider()

    # -------------------------
    # 2. ATS ANALYSIS
    # -------------------------
    st.header("2. ATS Analysis")

    jd = st.text_area("Paste Job Description")

    if st.button("Analyze ATS"):
        with st.spinner("Analyzing..."):
            res = safe_post(
                f"{BACKEND_URL}/analyze-ats",
                data={
                    "resume_text": st.session_state.resume_text,
                    "job_description": jd,
                    "email": st.session_state.email
                }
            )

        if res:
            data = res.json()
            basic = data.get("basic_analysis", {})
            ai = data.get("ai_analysis", {})

            st.metric("ATS Score", basic.get("ats_score", 0))

            st.write("Matched:", basic.get("matched_keywords", []))
            st.write("Missing:", basic.get("missing_keywords", []))

            st.write("AI Summary:", ai.get("summary", ""))

    st.divider()

    # -------------------------
    # 3. JOB MATCHING
    # -------------------------
    st.header("3. Find Jobs")

    min_score = st.slider("Minimum Score", 0, 100, 40)

    if st.button("Find Jobs"):
        with st.spinner("Fetching jobs..."):
            res = safe_post(
                f"{BACKEND_URL}/match-jobs",
                data={"resume_text": st.session_state.resume_text}
            )

        if res:
            data = res.json()
            jobs = data.get("top_matches", [])

            jobs = [j for j in jobs if j["match_score"] >= min_score]

            if not jobs:
                st.warning("No jobs found")

            for job in jobs:
                st.subheader(f"{job['title']} - {job['company']}")

                st.write(f"Score: {job['match_score']}%")

                # Match indicator
                if job["match_score"] > 70:
                    st.success("🔥 Strong Match")
                elif job["match_score"] > 40:
                    st.warning("⚡ Medium Match")
                else:
                    st.error("❌ Low Match")

                st.write("Skills:", job["matched_skills"])

                st.write("### Apply Links")

                col1, col2, col3 = st.columns(3)

                if job.get("linkedin"):
                    col1.markdown(f"[LinkedIn]({job['linkedin']})")

                if job.get("indeed"):
                    col2.markdown(f"[Indeed]({job['indeed']})")

                if job.get("naukri"):
                    col3.markdown(f"[Naukri]({job['naukri']})")

                if job.get("link"):
                    st.markdown(f"👉 [Apply Direct]({job['link']})")

                st.divider()

    st.divider()

    # -------------------------
    # EMAIL ALERT
    # -------------------------
    st.header("4. Email Alerts")

    email = st.text_input("Email", value=st.session_state.email)

    if st.button("Send Alerts"):
        res = safe_post(
            f"{BACKEND_URL}/send-job-alerts",
            data={
                "email": email,
                "resume_text": st.session_state.resume_text
            }
        )

        if res:
            st.success("Email sent!")

else:
    st.info("Please login to continue")