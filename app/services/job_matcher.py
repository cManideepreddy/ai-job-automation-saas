from app.services.text_analyzer import extract_skills, flatten_skills, detect_domain
from app.services.job_fetcher import fetch_remoteok_jobs


# -----------------------------------------
# CALCULATE MATCH BETWEEN RESUME & JOB
# -----------------------------------------
def calculate_job_match(resume_skills, resume_domain, job):
    job_skills = job.get("skills", [])
    job_domain = job.get("domain", "general")

    # Safety check
    if not job_skills:
        return None

    # Skill matching
    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))

    # Base score
    base_score = int((len(matched) / max(len(job_skills), 1)) * 100)

    # -----------------------------------------
    # RELAXED DOMAIN LOGIC (VERY IMPORTANT)
    # -----------------------------------------
    if resume_domain == job_domain:
        boost = 1.2
    elif job_domain == "general":
        boost = 1.0
    else:
        boost = 0.8  # do NOT reject, only reduce slightly

    final_score = int(base_score * boost)

    # Always ensure minimum score (so UI never shows empty)
    final_score = max(final_score, 10)

    return {
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "link": job.get("link", ""),
        "match_score": final_score,
        "job_domain": job_domain,
        "matched_skills": matched,
        "missing_skills": missing,
        "relevance": (
            "High" if final_score > 60
            else "Medium" if final_score > 30
            else "Low"
        )
    }


# -----------------------------------------
# MAIN FUNCTION TO GET TOP JOBS
# -----------------------------------------
def get_top_job_matches(resume_text, top_n=10):

    # Extract resume data
    resume_skills = flatten_skills(extract_skills(resume_text))
    resume_domain = detect_domain(resume_text)

    # -----------------------------------------
    # FETCH LIVE JOBS
    # -----------------------------------------
    try:
        jobs = fetch_remoteok_jobs()
        print("Fetched jobs:", len(jobs))
    except Exception as e:
        print("Job fetch failed:", e)
        jobs = []

    # -----------------------------------------
    # FALLBACK (VERY IMPORTANT)
    # ALWAYS RETURNS JOBS
    # -----------------------------------------
    if not jobs:
        jobs = [
            {
                "title": "Software Engineer",
                "company": "Infosys",
                "skills": ["python", "java", "api"],
                "domain": "software",
                "link": "https://www.linkedin.com/jobs/search/?keywords=software%20engineer"
            },
            {
                "title": "Data Analyst",
                "company": "TCS",
                "skills": ["python", "sql", "excel"],
                "domain": "data",
                "link": "https://www.linkedin.com/jobs/search/?keywords=data%20analyst"
            },
            {
                "title": "Civil Engineer",
                "company": "L&T",
                "skills": ["autocad", "construction", "site"],
                "domain": "civil",
                "link": "https://www.naukri.com/civil-engineer-jobs"
            },
            {
                "title": "Mechanical Engineer",
                "company": "Tata Motors",
                "skills": ["cad", "design", "manufacturing"],
                "domain": "mechanical",
                "link": "https://www.indeed.com/jobs?q=mechanical+engineer"
            },
            {
                "title": "DevOps Engineer",
                "company": "Wipro",
                "skills": ["docker", "kubernetes", "aws"],
                "domain": "devops",
                "link": "https://www.linkedin.com/jobs/search/?keywords=devops"
            }
        ]

    # -----------------------------------------
    # MATCHING LOGIC
    # -----------------------------------------
    results = []

    for job in jobs:
        match = calculate_job_match(resume_skills, resume_domain, job)

        if match:  # 🔥 NO FILTERING (important)
            results.append(match)

    # Sort by score
    results.sort(key=lambda x: x["match_score"], reverse=True)

    # -----------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------
    return {
        "resume_domain": resume_domain,
        "resume_skills": resume_skills,
        "total_jobs_scanned": len(jobs),
        "top_matches": results[:top_n]
    }