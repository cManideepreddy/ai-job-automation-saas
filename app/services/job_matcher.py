from app.services.text_analyzer import extract_skills, flatten_skills, detect_domain
from app.services.job_fetcher import fetch_remoteok_jobs


def calculate_job_match(resume_skills, resume_domain, job):
    job_skills = job.get("skills", [])
    job_domain = job.get("domain", "general")

    if not job_skills:
        return None

    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))

    base_score = int((len(matched) / max(len(job_skills), 1)) * 100)

    # 🔥 Relaxed domain logic
    if resume_domain == job_domain:
        boost = 1.2
    elif job_domain == "general":
        boost = 1.0
    else:
        boost = 0.8

    final_score = int(base_score * boost)

    return {
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "link": job.get("link", ""),
        "match_score": max(final_score, 10),  # always show something
        "job_domain": job_domain,
        "matched_skills": matched,
        "missing_skills": missing,
        "relevance": "High" if final_score > 60 else "Medium" if final_score > 30 else "Low"
    }


def get_top_job_matches(resume_text, top_n=10):

    resume_skills = flatten_skills(extract_skills(resume_text))
    resume_domain = detect_domain(resume_text)

    try:
        jobs = fetch_remoteok_jobs()
        print("Fetched jobs:", len(jobs))
    except Exception:
        jobs = []

    # 🔥 fallback (ALWAYS RETURNS JOBS)
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
                "skills": ["autocad", "construction"],
                "domain": "civil",
                "link": "https://www.naukri.com/civil-engineer-jobs"
            }
        ]

    results = []

    for job in jobs:
        match = calculate_job_match(resume_skills, resume_domain, job)
        if match:
            results.append(match)

    results.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "resume_domain": resume_domain,
        "resume_skills": resume_skills,
        "total_jobs_scanned": len(jobs),
        "top_matches": results[:top_n]
    }