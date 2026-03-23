import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def rewrite_resume(resume_text, job_description):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume writer."
                },
                {
                    "role": "user",
                    "content": f"""
Rewrite this resume to match the job description.

Make it:
- ATS optimized
- Professional
- Strong bullet points
- Keyword rich

Resume:
{resume_text}

Job:
{job_description}

Return clean improved resume text.
"""
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"