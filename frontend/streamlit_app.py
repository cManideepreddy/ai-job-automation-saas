import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.title("AI Resume ATS + Job Match MVP")

# Upload Resume
uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

resume_text = ""

if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
    res = requests.post(f"{BACKEND_URL}/upload-resume", files=files)

    if res.status_code == 200:
        data = res.json()
        resume_text = data.get("resume_text", "")
        st.success("Resume uploaded")
        st.text_area("Resume Text", resume_text, height=200)
    else:
        st.error("Upload failed")

# Job Description
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

            st.subheader("ATS Score")
            st.metric("Score", f'{basic.get("ats_score", 0)}/100')

            st.write("Matched:", basic.get("matched_keywords", []))
            st.write("Missing:", basic.get("missing_keywords", []))

            st.write("Suggestions:")
            for s in basic.get("suggestions", []):
                st.write("-", s)

            st.subheader("AI Feedback")
            st.write(ai.get("raw_response", "No response"))

        else:
            st.error("Analysis failed")