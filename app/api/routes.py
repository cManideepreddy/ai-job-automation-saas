import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from app.db.database_sqlite import cursor, conn

from app.config import UPLOAD_DIR
from app.services.resume_parser import extract_resume_text
from app.services.ats_engine import compute_ats_score
from app.services.llm_service import get_ai_ats_feedback
from app.services.job_matcher import get_top_job_matches
from app.services.email_service import send_job_alert_email

from app.db.database import get_db
from app.db.models import User, Resume, ATSResult, JobMatch
from app.db.schemas import UserSignup, UserLogin
from app.services.auth_service import hash_password, verify_password

router = APIRouter()

# -----------------------
# HEALTH CHECK
# -----------------------
@router.get("/")
def home():
    return {"message": "Backend Running"}

# -----------------------
# UPLOAD RESUME
# -----------------------
@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_resume_text(file_path)
        return {"resume_text": text[:5000]}
    except Exception as e:
        return {"error": str(e)}

# -----------------------
# ATS ANALYSIS
# -----------------------
@router.post("/analyze-ats")
async def analyze_ats(
        resume_text: str = Form(...),
        job_description: str = Form(...),
        email: str = Form(None)  # 👈 ADD THIS
):
    try:
        basic = compute_ats_score(resume_text, job_description)
        ai = get_ai_ats_feedback(resume_text, job_description)

        # 🔥 SAVE TO DATABASE
        if email:
            cursor.execute(
                "INSERT INTO user_activity (email, resume, ats_score) VALUES (?, ?, ?)",
                (email, resume_text[:1000], basic.get("ats_score", 0))
            )
            conn.commit()

        return {
            "basic_analysis": basic,
            "ai_analysis": ai
        }

    except Exception as e:
        return {
            "basic_analysis": {},
            "ai_analysis": {"error": str(e)}
        }

# -----------------------
# JOB MATCHING
# -----------------------
@router.post("/match-jobs")
async def match_jobs(resume_text: str = Form(...)):
    try:
        return get_top_job_matches(resume_text)
    except Exception as e:
        return {"error": str(e)}

# -----------------------
# EMAIL ALERTS
# -----------------------
@router.post("/send-job-alerts")
async def send_job_alerts(email: str = Form(...), resume_text: str = Form(...)):
    try:
        result = get_top_job_matches(resume_text)
        jobs = result.get("top_matches", [])

        success, message = send_job_alert_email(email, jobs)

        return {
            "status": "success" if success else "failed",
            "message": message,
            "jobs_sent": len(jobs)
        }

    except Exception as e:
        return {"status": "failed", "message": str(e)}

# -----------------------
# AUTH
# -----------------------
@router.post("/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    try:
        # 🔥 FIX ADDED HERE
        if len(user.password) > 72:
            return {"status": "failed", "message": "Password too long (max 72 chars)"}

        existing_user = db.query(User).filter(User.email == user.email).first()

        if existing_user:
            return {"status": "failed", "message": "Email already registered"}

        new_user = User(
            email=user.email,
            hashed_password=hash_password(user.password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "status": "success",
            "message": "User created successfully",
            "user_id": new_user.id
        }

    except Exception as e:
        return {"status": "failed", "message": str(e)}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()

        if not existing_user:
            return {"status": "failed", "message": "User not found"}

        if not verify_password(user.password, existing_user.hashed_password):
            return {"status": "failed", "message": "Invalid password"}

        return {
            "status": "success",
            "user_id": existing_user.id,
            "email": existing_user.email
        }

    except Exception as e:
        return {"status": "failed", "message": str(e)}

# -----------------------
# SAVE RESUME
# -----------------------
@router.post("/save-resume")
def save_resume(user_id: int = Form(...), filename: str = Form(...), resume_text: str = Form(...), db: Session = Depends(get_db)):
    try:
        resume = Resume(
            user_id=user_id,
            filename=filename,
            resume_text=resume_text
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        return {"status": "success", "resume_id": resume.id}

    except Exception as e:
        return {"status": "failed", "message": str(e)}

# -----------------------
# SAVE ATS RESULT
# -----------------------
@router.post("/save-ats-result")
def save_ats_result(
        user_id: int = Form(...),
        resume_id: int = Form(None),
        job_description: str = Form(...),
        ats_score: int = Form(...),
        matched_keywords: str = Form(""),
        missing_keywords: str = Form(""),
        ai_feedback: str = Form(""),
        db: Session = Depends(get_db)
):
    try:
        ats = ATSResult(
            user_id=user_id,
            resume_id=resume_id,
            job_description=job_description,
            ats_score=ats_score,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            ai_feedback=ai_feedback
        )

        db.add(ats)
        db.commit()
        db.refresh(ats)

        return {"status": "success", "ats_result_id": ats.id}

    except Exception as e:
        return {"status": "failed", "message": str(e)}

# -----------------------
# SAVE JOB MATCH
# -----------------------
@router.post("/save-job-match")
def save_job_match(
        user_id: int = Form(...),
        resume_id: int = Form(None),
        title: str = Form(...),
        company: str = Form(...),
        link: str = Form(""),
        match_score: int = Form(...),
        matched_skills: str = Form(""),
        missing_skills: str = Form(""),
        db: Session = Depends(get_db)
):
    try:
        job_match = JobMatch(
            user_id=user_id,
            resume_id=resume_id,
            title=title,
            company=company,
            link=link,
            match_score=match_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills
        )

        db.add(job_match)
        db.commit()
        db.refresh(job_match)

        return {"status": "success", "job_match_id": job_match.id}

    except Exception as e:
        return {"status": "failed", "message": str(e)}


@router.get("/get-users")
def get_users():
    cursor.execute("SELECT * FROM user_activity ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()

    return {
        "data": rows
    }