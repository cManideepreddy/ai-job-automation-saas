import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_ats_feedback(resume_text, job_description):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an ATS expert."},
                {"role": "user", "content": f"""
Analyze this resume vs job description.

Resume:
{resume_text}

Job:
{job_description}

Return:
- pros
- cons
- suggestions
- summary
"""}
            ]
        )

        content = response.choices[0].message.content

        return {
            "pros": [],
            "cons": [],
            "suggestions": [],
            "summary": content
        }

    except Exception as e:
        return {
            "pros": [],
            "cons": [],
            "suggestions": [],
            "summary": f"AI error: {str(e)}"
        }