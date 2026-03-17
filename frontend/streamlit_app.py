import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.title("🚀 AI Resume ATS + Job Match MVP")

# ---------------------------
# Upload Resume
# ---------------------------
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

resume_text = ""

if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    res = requests.post(f"{BACKEND_URL}/upload-resume", files=files)

    if res.status_code == 200:
        data = res.json()
        resume_text = data.get("resume_text", "")
        st.success("✅ Resume uploaded")
        st.text_area("Resume Text", resume_text, height=200)
    else:
        st.error("❌ Upload failed")

# ---------------------------
# ATS Analysis
# ---------------------------
jd = st.text_area("Paste Job Description")

if st.button("Analyze ATS"):
    if not resume_text or not jd:
        st.warning("Upload resume and paste JD")
    else:
        response = requests.post(
            f"{BACKEND_URL}/analyze-ats",
            data={"resume_text": resume_text, "job_description": jd}
        )

        if response.status_code == 200:
            result = response.json()

            basic = result.get("basic_analysis", {})
            ai = result.get("ai_analysis", {})

            st.subheader("📊 ATS Score")
            st.metric("Score", f'{basic.get("ats_score", 0)}/100')

            st.write("✅ Matched:", basic.get("matched_keywords", []))
            st.write("❌ Missing:", basic.get("missing_keywords", []))

            st.write("💡 Suggestions:")
            for s in basic.get("suggestions", []):
                st.write("-", s)

            st.subheader("🤖 AI Feedback")
            st.write(ai.get("raw_response", "No response"))

        else:
            st.error("Analysis failed")

# ---------------------------
# JOB MATCHING (NEW SECTION)
# ---------------------------
st.subheader("🔍 Find Matching Jobs")

jobs_data = None

if st.button("Find Jobs"):
    if not resume_text:
        st.warning("Upload resume first")
    else:
        res = requests.post(
            f"{BACKEND_URL}/match-jobs",
            data={"resume_text": resume_text}
        )

        if res.status_code == 200:
            jobs_data = res.json()

            st.success(f"Found {jobs_data.get('total_jobs_scanned', 0)} jobs")

            for job in jobs_data.get("top_matches", []):
                st.markdown(f"### {job['title']} - {job['company']}")
                st.write(f"📊 Score: {job['match_score']}% ({job['relevance']})")
                st.write("✅ Matched:", job["matched_skills"])
                st.write("❌ Missing:", job["missing_skills"])
                st.write(f"🔗 [Apply Here]({job['link']})")
                st.divider()

        else:
            st.error("Job matching failed")

# ---------------------------
# EMAIL ALERTS
# ---------------------------
st.subheader("📩 Get Job Alerts")

email = st.text_input("Enter your email")

if st.button("Send Job Alerts"):
    if not resume_text:
        st.warning("Please upload a resume first.")
    elif not email.strip():
        st.warning("Please enter an email address.")
    else:
        response = requests.post(
            f"{BACKEND_URL}/send-job-alerts",  # ✅ FIXED
            data={"email": email, "resume_text": resume_text}
        )

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == "success":
                st.success(f"📩 Email sent! Jobs sent: {data.get('jobs_sent', 0)}")
            else:
                st.error(f"Email failed: {data.get('message')}")
        else:
            st.error("Failed to call email alert API")