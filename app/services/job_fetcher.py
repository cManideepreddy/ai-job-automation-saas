import requests


def fetch_remoteok_jobs():
    url = "https://remoteok.com/api"

    try:
        response = requests.get(url)
        data = response.json()

        jobs = []

        # skip first metadata element
        for item in data[1:]:
            job = {
                "id": item.get("id"),
                "title": item.get("position"),
                "company": item.get("company"),
                "skills": extract_skills_from_text(item.get("description", "")),
                "description": item.get("description", ""),
                "link": item.get("url")
            }
            jobs.append(job)

        return jobs

    except Exception as e:
        print("Error fetching jobs:", e)
        return []


def extract_skills_from_text(text):
    keywords = [
        "python", "sql", "aws", "gcp", "spark", "docker",
        "kubernetes", "api", "linux", "react", "node"
    ]

    text = text.lower()
    return [kw for kw in keywords if kw in text]