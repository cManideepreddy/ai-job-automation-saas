import requests
from app.services.text_analyzer import extract_skills, flatten_skills, detect_domain

def fetch_remoteok_jobs():
    try:
        res = requests.get(
            "https://remoteok.com/api",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )
        print("RemoteOK status:", res.status_code)

        data = res.json()
        jobs = []

        for j in data[1:]:
            text = (j.get("position", "") + " " + j.get("description", ""))
            skills = flatten_skills(extract_skills(text))
            domain = detect_domain(text)

            jobs.append({
                "id": j.get("id"),
                "title": j.get("position"),
                "company": j.get("company"),
                "skills": skills,
                "description": j.get("description"),
                "link": j.get("url"),
                "domain": domain
            })

        print("Fetched jobs count:", len(jobs))
        return jobs

    except Exception as e:
        print("fetch_remoteok_jobs error:", e)
        return []