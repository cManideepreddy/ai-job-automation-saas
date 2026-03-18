import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="ApplyPilot AI", layout="centered")

# -------------------------
# SESSION INIT
# -------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "email" not in st.session_state:
    st.session_state.email = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "resume_filename" not in st.session_state:
    st.session_state.resume_filename = ""
if "last_ats_result" not in st.session_state:
    st.session_state.last_ats_result = None
if "last_job_matches" not in st.session_state:
    st.session_state.last_job_matches = []

# -------------------------
# HELPERS
# -------------------------
def render_list(title: str, items: list, icon: str = "-"):
    st.subheader(title)
    if items:
        for item in items:
            st.write(f"{icon} {item}")
    else:
        st.write("No items available.")


def safe_post(url: str, **kwargs):
    try:
        response = requests.post(url, timeout=60, **kwargs)
        return response
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None


# -------------------------
# TITLE
# -------------------------
st.title("🚀 ApplyPilot AI")
st.caption("ATS Analysis • Smart Job Matching • Email Alerts")

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

    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Signup"):
        if not signup_email or not signup_password:
            st.warning("Please fill all fields.")
        elif len(signup_password.encode("utf-8")) > 72:
            st.error("Password too long. Please keep it under 72 bytes.")
        else:
            res = safe_post(
                f"{BACKEND_URL}/signup",
                json={"email": signup_email, "password": signup_password}
            )

            if res is not None:
                data = res.json()
                if data.get("status") == "success":
                    st.success("Account created successfully. Please login.")
                else:
                    st.error(data.get("message", "Signup failed."))

# -------------------------
# LOGIN
# -------------------------
elif choice == "Login" and not st.session_state.user_id:
    st.subheader("Login")

    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if not login_email or not login_password:
            st.warning("Please fill all fields.")
        else:
            res = safe_post(
                f"{BACKEND_URL}/login",
                json={"email": login_email, "password": login_password}
            )

            if res is not None:
                data = res.json()
                if data.get("status") == "success":
                    st.session_state.user_id = data.get("user_id")
                    st.session_state.email = data.get("email")
                    st.success("Login successful.")
                    st.rerun()
                else:
                    st.error(data.get("message", "Login failed."))

# -------------------------
# MAIN APP AFTER LOGIN
# -------------------------
if st.session_state.user_id:
    st.success(f"Logged in as {st.session_state.email}")

    if st.button("Logout"):
        st.session_state.user_id = None
        st.session_state.email = None
        st.session_state.resume_text = ""
        st.session_state.resume_filename = ""
        st.session_state.last_ats_result = None
        st.session_state.last_job_matches = []
        st.rerun()

    st.divider()

    # -------------------------
    # RESUME UPLOAD
    # -------------------------
    st.header("1. Upload Resume")

    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

    if uploaded_file is not None:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        res = safe_post(f"{BACKEND_URL}/upload-resume", files=files)

        if res is not None and res.status_code == 200:
            data = res.json()

            if data.get("error"):
                st.error(data["error"])
            else:
                st.session_state.resume_text = data.get("resume_text", "")
                st.session_state.resume_filename = uploaded_file.name

                st.success("Resume uploaded and parsed successfully.")
                st.text_area("Extracted Resume Text", st.session_state.resume_text, height=200)

                save_resume_res = safe_post(
                    f"{BACKEND_URL}/save-resume",
                    data={
                        "user_id": st.session_state.user_id,
                        "filename": st.session_state.resume_filename,
                        "resume_text": st.session_state.resume_text
                    }
                )

                if save_resume_res is not None:
                    save_resume_data = save_resume_res.json()
                    if save_resume_data.get("status") == "success":
                        st.caption(f"Resume saved to database (Resume ID: {save_resume_data.get('resume_id')})")
                    else:
                        st.warning(f"Resume parsed but not saved: {save_resume_data.get('message', 'Unknown error')}")

    st.divider()

    # -------------------------
    # ATS ANALYSIS
    # -------------------------
    st.header("2. ATS Analysis")

    job_description = st.text_area("Paste Job Description", height=180)

    if st.button("Analyze ATS"):
        if not st.session_state.resume_text:
            st.warning("Please upload a resume first.")
        elif not job_description.strip():
            st.warning("Please paste a job description.")
        else:
            res = safe_post(
                f"{BACKEND_URL}/analyze-ats",
                data={
                    "resume_text": st.session_state.resume_text,
                    "job_description": job_description
                }
            )

            if res is not None and res.status_code == 200:
                result = res.json()
                st.session_state.last_ats_result = result

                basic = result.get("basic_analysis", {})
                ai = result.get("ai_analysis", {})

                st.subheader("ATS Score Overview")
                st.metric("ATS Score", f"{basic.get('ats_score', 0)}/100")

                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Resume Domain:**", basic.get("resume_domain", "unknown"))
                with col2:
                    st.write("**Job Domain:**", basic.get("job_domain", "unknown"))

                st.subheader("Keyword Analysis")
                st.write("**Matched Keywords:**", basic.get("matched_keywords", []))
                st.write("**Missing Keywords:**", basic.get("missing_keywords", []))
                st.write("**Matched Required Skills:**", basic.get("matched_required_skills", []))
                st.write("**Missing Required Skills:**", basic.get("missing_required_skills", []))

                basic_pros = basic.get("pros", [])
                ai_pros = ai.get("pros", [])
                basic_cons = basic.get("cons", [])
                ai_cons = ai.get("cons", [])
                basic_suggestions = basic.get("suggestions", [])
                ai_suggestions = ai.get("suggestions", [])

                render_list("Pros", basic_pros + ai_pros, "✅")
                render_list("Cons", basic_cons + ai_cons, "❌")
                render_list("Suggestions", basic_suggestions + ai_suggestions, "💡")

                st.subheader("Summary")
                st.write(ai.get("summary") or basic.get("summary") or "No summary available.")

                # Save ATS result
                ai_feedback_text = (
                    f"Pros: {ai_pros}\n"
                    f"Cons: {ai_cons}\n"
                    f"Suggestions: {ai_suggestions}\n"
                    f"Summary: {ai.get('summary', '')}"
                )

                save_ats_res = safe_post(
                    f"{BACKEND_URL}/save-ats-result",
                    data={
                        "user_id": st.session_state.user_id,
                        "job_description": job_description,
                        "ats_score": basic.get("ats_score", 0),
                        "matched_keywords": ", ".join(basic.get("matched_keywords", [])),
                        "missing_keywords": ", ".join(basic.get("missing_keywords", [])),
                        "ai_feedback": ai_feedback_text
                    }
                )

                if save_ats_res is not None:
                    save_ats_data = save_ats_res.json()
                    if save_ats_data.get("status") == "success":
                        st.caption(f"ATS result saved (ATS Result ID: {save_ats_data.get('ats_result_id')})")
                    else:
                        st.warning(f"ATS result displayed but not saved: {save_ats_data.get('message', 'Unknown error')}")
            else:
                st.error("ATS analysis failed.")

    st.divider()

    # -------------------------
    # JOB MATCHING
    # -------------------------
    st.header("3. Find Matching Jobs")

    if st.button("Find Jobs"):
        if not st.session_state.resume_text:
            st.warning("Please upload a resume first.")
        else:
            res = safe_post(
                f"{BACKEND_URL}/match-jobs",
                data={"resume_text": st.session_state.resume_text}
            )

            if res is not None and res.status_code == 200:
                data = res.json()
                st.session_state.last_job_matches = data.get("top_matches", [])

                st.subheader("Matching Summary")
                st.write("**Detected Resume Domain:**", data.get("resume_domain", "unknown"))
                st.write("**Resume Skills:**", data.get("resume_skills", []))
                st.write("**Total Jobs Scanned:**", data.get("total_jobs_scanned", 0))

                if st.session_state.last_job_matches:
                    for idx, job in enumerate(st.session_state.last_job_matches, start=1):
                        st.markdown(f"### {idx}. {job.get('title', 'N/A')} - {job.get('company', 'N/A')}")
                        st.write(f"**Match Score:** {job.get('match_score', 0)}%")
                        st.write(f"**Relevance:** {job.get('relevance', 'N/A')}")
                        st.write(f"**Job Domain:** {job.get('job_domain', 'unknown')}")
                        st.write(f"**Matched Skills:** {job.get('matched_skills', [])}")
                        st.write(f"**Missing Skills:** {job.get('missing_skills', [])}")

                        link = job.get("link")
                        if link:
                            st.markdown(f"[Apply Here]({link})")

                        st.divider()

                        # Save job match
                        safe_post(
                            f"{BACKEND_URL}/save-job-match",
                            data={
                                "user_id": st.session_state.user_id,
                                "title": job.get("title", ""),
                                "company": job.get("company", ""),
                                "link": job.get("link", ""),
                                "match_score": job.get("match_score", 0),
                                "matched_skills": ", ".join(job.get("matched_skills", [])),
                                "missing_skills": ", ".join(job.get("missing_skills", []))
                            }
                        )
                else:
                    st.info("No relevant jobs found for this resume.")
            else:
                st.error("Job matching failed.")

    st.divider()

    # -------------------------
    # EMAIL ALERTS
    # -------------------------
    st.header("4. Email Job Alerts")

    alert_email = st.text_input("Enter email for alerts", value=st.session_state.email or "")

    if st.button("Send Job Alerts"):
        if not st.session_state.resume_text:
            st.warning("Please upload a resume first.")
        elif not alert_email.strip():
            st.warning("Please enter an email address.")
        else:
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
                st.error("Failed to call email alert API.")

else:
    st.info("Please login or signup from the left menu to continue.")