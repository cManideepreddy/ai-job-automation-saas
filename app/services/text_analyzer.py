import re
from app.data.skill_catalog import SKILL_CATALOG, DOMAIN_HINTS

def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower()).strip()

def extract_skills(text):
    text = normalize_text(text)
    found = {}

    for domain, skills in SKILL_CATALOG.items():
        found[domain] = [s for s in skills if s in text]

    return found

def flatten_skills(skill_map):
    skills = []
    for v in skill_map.values():
        skills.extend(v)
    return list(set(skills))

def detect_domain(text):
    text = normalize_text(text)
    scores = {}

    for domain, hints in DOMAIN_HINTS.items():
        score = 0
        for h in hints:
            if h in text:
                score += 3
        for s in SKILL_CATALOG.get(domain, []):
            if s in text:
                score += 1
        scores[domain] = score

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        best = "general"

    return best