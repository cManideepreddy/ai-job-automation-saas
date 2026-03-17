import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form
from app.config import UPLOAD_DIR
from app.services.resume_parser import extract_resume_text
from app.services.ats_engine import compute_ats_score
from app.services.llm_service import get_ai_ats_feedback

router = APIRouter()

@router.get("/")
def home():
    return {"message": "Backend Running"}

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

@router.post("/analyze-ats")
async def analyze_ats(
        resume_text: str = Form(...),
        job_description: str = Form(...)
):
    try:
        basic = compute_ats_score(resume_text, job_description)
        ai = get_ai_ats_feedback(resume_text, job_description)

        return {
            "basic_analysis": basic,
            "ai_analysis": ai
        }

    except Exception as e:
        return {
            "basic_analysis": {
                "ats_score": 0,
                "matched_keywords": [],
                "missing_keywords": [],
                "suggestions": ["Error occurred"],
                "summary": "Failed"
            },
            "ai_analysis": {
                "raw_response": str(e)
            }
        }