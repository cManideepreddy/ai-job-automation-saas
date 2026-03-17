from app.data.sample_jobs import SAMPLE_JOBS
from app.services.job_fetcher import fetch_remoteok_jobs

# 🔹 Master skill dictionary (can expand later)
SKILL_KEYWORDS = [
    "python",
    "sql",
    "java",
    "aws",
    "gcp",
    "azure",
    "spark",
    "hadoop",
    "docker",
    "kubernetes",
    "etl",
    "airflow",
    "api",
    "git",
    "linux",
    "excel",
    "fastapi",
    "pandas"
]


# 🔹 Step 1: Extract skills from resume
def extract_skills_from_resume(resume_text: str) -> list[str]:
    if not resume_text:
        return []

    text = resume_text.lower()
    found_skills = [skill for skill in SKILL_KEYWORDS if skill in text]

    return sorted(list(set(found_skills)))


# 🔹 Step 2: Match resume skills with job skills
def calculate_job_match(resume_skills: list[str], job: dict) -> dict:
    job_skills = [skill.lower() for skill in job.get("skills", [])]

    # 🛑 Skip invalid jobs
    if not job_skills:
        return None

    matched_skills = sorted(list(set(resume_skills) & set(job_skills)))
    missing_skills = sorted(list(set(job_skills) - set(resume_skills)))

    # 🔥 Improved scoring (weighted)
    match_score = int((len(matched_skills) * 1.5 / len(job_skills)) * 100)
    match_score = min(match_score, 100)

    # 🔹 Relevance label
    if match_score >= 80:
        relevance = "Strong match"
    elif match_score >= 50:
        relevance = "Moderate match"
    else:
        relevance = "Low match"

    return {
        "id": job.get("id"),
        "title": job.get("title"),
        "company": job.get("company"),
        "description": job.get("description"),
        "link": job.get("link"),
        "required_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": match_score,
        "relevance": relevance
    }


# 🔹 Step 3: Main function to get top matches
def get_top_job_matches(resume_text: str, top_n: int = 5) -> dict:
    """
    Extract skills → Fetch real jobs → Match → Return top N
    """

    resume_skills = extract_skills_from_resume(resume_text)

    # 🔥 Try fetching real-time jobs
    try:
        jobs = fetch_remoteok_jobs()
        print(f"Fetched {len(jobs)} real jobs")
    except Exception as e:
        print("Error fetching jobs:", e)
        jobs = []

    # 🔁 Fallback if API fails
    if not jobs:
        print("⚠️ Using fallback SAMPLE_JOBS")
        jobs = SAMPLE_JOBS

    matched_jobs = []

    for job in jobs:
        result = calculate_job_match(resume_skills, job)

        # 🛑 Skip invalid results
        if result:
            matched_jobs.append(result)

    # 🔥 Sort by best score
    matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "resume_skills": resume_skills,
        "total_jobs_scanned": len(jobs),
        "top_matches": matched_jobs[:top_n]
    }