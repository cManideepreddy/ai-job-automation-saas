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
        BACKEND_URL = "https://applypilot-backend.onrender.com"  # 🔥 YOUR RENDER URL

st.set_page_config(page_title="ApplyPilot AI", layout="centered")

st.write("Using backend:", BACKEND_URL)

# -------------------------
# SESSION INIT
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
        return requests.post(url, timeout=60, **kwargs)
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# -------------------------
# TITLE
# -------------------------
st.title("🚀 ApplyPilot AI")
st.caption("ATS Analysis • Job Matching • Smart Apply")

# -------------------------
# LOGIN / SIGNUP
# -------------------------
menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Menu", menu)

# -------------------------
# SIGNUP
# -------------------------
if choice == "Signup" and not st.session_state.user_id:
    st.subheader("Create Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):
        res = safe_post(
            f"{BACKEND_URL}/signup",
            json={"email": email, "password": password}
        )

        if res:
            data = res.json()
            if data.get("status") == "success":
                st.success("Signup successful! Please login.")
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
        res = safe_post(
            f"{BACKEND_URL}/login",
            json={"email": email, "password": password}
        )

        if res:
            data = res.json()
            if data.get("status") == "success":
                st.session_state.user_id = data["user_id"]
                st.session_state.email = data["email"]
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
        st.session_state.user_id = None
        st.session_state.email = None
        st.session_state.resume_text = ""
        st.session_state.last_job_matches = []
        st.rerun()

    st.divider()

    # -------------------------
    # UPLOAD RESUME
    # -------------------------
    st.header("1. Upload Resume")

    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

    if uploaded_file:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}

        res = safe_post(f"{BACKEND_URL}/upload-resume", files=files)

        if res and res.status_code == 200:
            data = res.json()

            if "resume_text" in data:
                st.session_state.resume_text = data["resume_text"]
                st.success("Resume uploaded successfully")

                st.text_area("Resume Preview", data["resume_text"], height=200)

    st.divider()

    # -------------------------
    # FIND JOBS
    # -------------------------
    st.header("2. Find Jobs")

    if st.button("Find Jobs"):

        if not st.session_state.resume_text:
            st.warning("Upload resume first")
        else:
            res = safe_post(
                f"{BACKEND_URL}/match-jobs",
                data={"resume_text": st.session_state.resume_text}
            )

            if res and res.status_code == 200:
                data = res.json()

                jobs = data.get("top_matches", [])
                st.session_state.last_job_matches = jobs

                if jobs:
                    st.success(f"{len(jobs)} jobs found")

                    for idx, job in enumerate(jobs, start=1):

                        st.markdown(f"### {idx}. {job['title']} - {job['company']}")

                        st.write(f"**Score:** {job['match_score']}%")
                        st.write(f"**Relevance:** {job['relevance']}")
                        st.write(f"**Domain:** {job['job_domain']}")

                        st.write("Matched Skills:", job["matched_skills"])
                        st.write("Missing Skills:", job["missing_skills"])

                        # 🔥 APPLY LINKS
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(
                                f"[LinkedIn](https://www.linkedin.com/jobs/search/?keywords={job['title']})"
                            )

                        with col2:
                            st.markdown(
                                f"[Indeed](https://www.indeed.com/jobs?q={job['title']})"
                            )

                        with col3:
                            st.markdown(
                                f"[Naukri](https://www.naukri.com/{job['title'].replace(' ', '-')}-jobs)"
                            )

                        if job.get("link"):
                            st.markdown(f"👉 [Apply Direct]({job['link']})")

                        st.divider()

                else:
                    st.warning("No jobs found")

            else:
                st.error("API failed")

else:
    st.info("Please login to continue")