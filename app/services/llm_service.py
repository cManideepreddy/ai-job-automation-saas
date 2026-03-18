import json
from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_ai_ats_feedback(resume_text, jd_text):
    try:
        prompt = f"""
Compare resume and job description.

Return JSON:
{{
"pros": [],
"cons": [],
"suggestions": [],
"summary": ""
}}

Resume:
{resume_text}

JD:
{jd_text}
"""

        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(res.choices[0].message.content)

    except Exception as e:
        return {"pros": [], "cons": [str(e)], "suggestions": [], "summary": "AI failed"}