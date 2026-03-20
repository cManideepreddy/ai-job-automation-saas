import requests
from app.services.text_analyzer import extract_skills, flatten_skills, detect_domain


def fetch_remoteok_jobs():
    try:
        res = requests.get(
            "https://remoteok.com/api",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )
        data = res.json()

        jobs = []
        if not isinstance(data, list) or len(data) <= 1:
            return []

        for j in data[1:]:
            title = j.get("position", "") or ""
            description = j.get("description", "") or ""
            company = j.get("company", "") or ""
            link = j.get("url", "") or ""

            text = f"{title} {description}"
            skills = flatten_skills(extract_skills(text))
            domain = detect_domain(text)

            jobs.append({
                "id": j.get("id"),
                "title": title,
                "company": company,
                "skills": skills,
                "description": description,
                "link": link,
                "domain": domain
            })

        return jobs

    except Exception as e:
        print("fetch_remoteok_jobs error:", e)
        return []