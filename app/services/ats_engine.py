import re
from collections import Counter


COMMON_SKILLS = [
    "python", "sql", "java", "aws", "gcp", "azure", "spark", "hadoop",
    "fastapi", "docker", "kubernetes", "etl", "airflow", "linux",
    "machine learning", "data engineering", "api", "git", "pandas"
]


def extract_keywords(text: str) -> list[str]:
    text_lower = text.lower()
    found = []

    for skill in COMMON_SKILLS:
        if skill in text_lower:
            found.append(skill)

    return sorted(list(set(found)))


def compute_ats_score(resume_text: str, job_description: str) -> dict:
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_description)

    matched = [kw for kw in jd_keywords if kw in resume_keywords]
    missing = [kw for kw in jd_keywords if kw not in resume_keywords]

    if not jd_keywords:
        score = 50
    else:
        score = int((len(matched) / len(jd_keywords)) * 100)

    score = max(0, min(score, 100))

    suggestions = []
    if missing:
        suggestions.append(f"Add or highlight these missing keywords: {', '.join(missing)}")
    if score < 60:
        suggestions.append("Your resume needs better alignment with the job description.")
    if score >= 60:
        suggestions.append("Your resume has decent alignment, but can still be improved for stronger ATS performance.")

    summary = (
        f"Resume matched {len(matched)} out of {len(jd_keywords)} important job keywords."
        if jd_keywords else
        "No standard keywords detected in the job description, so score is estimated."
    )

    return {
        "ats_score": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "suggestions": suggestions,
        "summary": summary
    }