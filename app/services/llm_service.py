from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def get_ai_ats_feedback(resume_text: str, job_description: str) -> dict:
    prompt = f"""
You are an expert ATS resume reviewer and career coach.

Analyze the following resume against the job description.

Return output in this exact JSON format:
{{
  "summary": "short summary",
  "improvement_suggestions": [
    "suggestion 1",
    "suggestion 2",
    "suggestion 3"
  ],
  "strong_points": [
    "point 1",
    "point 2"
  ],
  "missing_areas": [
    "missing 1",
    "missing 2"
  ]
}}

Resume:
{resume_text}

Job Description:
{job_description}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a precise ATS analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content
    return {"raw_response": content}