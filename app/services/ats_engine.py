from app.services.text_analyzer import extract_skills, flatten_skills, detect_domain

def compute_ats_score(resume_text, jd_text):
    resume_skills = set(flatten_skills(extract_skills(resume_text)))
    jd_skills = set(flatten_skills(extract_skills(jd_text)))

    resume_domain = detect_domain(resume_text)
    job_domain = detect_domain(jd_text)

    # Skill score
    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills

    skill_score = int((len(matched) / max(len(jd_skills), 1)) * 100)

    # Domain score
    domain_score = 100 if resume_domain == job_domain else 20

    final_score = int(skill_score * 0.7 + domain_score * 0.3)

    pros = []
    cons = []
    suggestions = []

    if matched:
        pros.append(f"Matched skills: {', '.join(list(matched)[:5])}")

    if missing:
        cons.append(f"Missing skills: {', '.join(list(missing)[:5])}")
        suggestions.append(f"Add these skills if applicable: {', '.join(list(missing)[:5])}")

    if resume_domain != job_domain:
        cons.append(f"Domain mismatch: Resume={resume_domain}, Job={job_domain}")
        suggestions.append("Apply for domain-relevant jobs or modify resume")

    summary = "Strong match" if final_score > 70 else "Needs improvement"

    return {
        "ats_score": final_score,
        "resume_domain": resume_domain,
        "job_domain": job_domain,
        "matched_keywords": list(matched),
        "missing_keywords": list(missing),
        "matched_required_skills": list(matched),
        "missing_required_skills": list(missing),
        "pros": pros,
        "cons": cons,
        "suggestions": suggestions,
        "summary": summary
    }