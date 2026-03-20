from app.services.text_analyzer import extract_skills, flatten_skills, detect_domain
from app.services.job_fetcher import fetch_remoteok_jobs
from app.data.sample_jobs import SAMPLE_JOBS

# ---------------------------
# DOMAIN FILTER
# ---------------------------
def domain_match(resume_domain, job_domain):
    return resume_domain == job_domain


# ---------------------------
# SCORE CALCULATION
# ---------------------------
def calculate_job_match(resume_skills, resume_domain, job):
    job_skills = job.get("skills", [])
    job_domain = job.get("domain", "general")

    if not job_skills:
        return None

    # Domain penalty
    penalty = 1.0 if domain_match(resume_domain, job_domain) else 0.3

    matched = list(set(resume_skills) & set(job_skills))
    missing = list(set(job_skills) - set(resume_skills))

    base_score = int((len(matched) / max(len(job_skills), 1)) * 100)
    final_score = int(base_score * penalty)

    return {
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "link": job.get("link", ""),
        "linkedin": job.get("linkedin", ""),
        "indeed": job.get("indeed", ""),
        "naukri": job.get("naukri", ""),
        "match_score": final_score,
        "job_domain": job_domain,
        "matched_skills": matched,
        "missing_skills": missing,
        "relevance": "High" if final_score > 70 else "Medium" if final_score > 40 else "Low"
    }


# ---------------------------
# MAIN MATCH FUNCTION
# ---------------------------
def get_top_job_matches(resume_text, top_n=5):

    resume_skills = flatten_skills(extract_skills(resume_text))
    resume_domain = detect_domain(resume_text)

    try:
        jobs = fetch_remoteok_jobs()
    except Exception as e:
        print("Live fetch failed:", e)
        jobs = []

    # fallback
    if not jobs:
        jobs = SAMPLE_JOBS

    results = []

    for job in jobs:
        match = calculate_job_match(resume_skills, resume_domain, job)

        if match and match["match_score"] > 10:  # filter weak jobs
            results.append(match)

    results.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "resume_domain": resume_domain,
        "resume_skills": resume_skills,
        "total_jobs_scanned": len(jobs),
        "top_matches": results[:top_n]
    }