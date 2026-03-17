import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import SMTP_EMAIL, SMTP_APP_PASSWORD


def send_job_alert_email(to_email: str, jobs: list):
    try:
        if not SMTP_EMAIL or not SMTP_APP_PASSWORD:
            raise ValueError("SMTP credentials are missing in .env")

        msg = MIMEMultipart()
        msg["From"] = SMTP_EMAIL
        msg["To"] = to_email
        msg["Subject"] = "Your Daily Job Matches"

        if not jobs:
            body = "No matching jobs were found today."
        else:
            body = "Here are your top matching jobs:\n\n"

            for idx, job in enumerate(jobs, start=1):
                body += (
                    f"{idx}. {job.get('title', 'N/A')} - {job.get('company', 'N/A')}\n"
                    f"Match Score: {job.get('match_score', 0)}%\n"
                    f"Matched Skills: {', '.join(job.get('matched_skills', []))}\n"
                    f"Missing Skills: {', '.join(job.get('missing_skills', []))}\n"
                    f"Link: {job.get('link', 'N/A')}\n"
                    f"Relevance: {job.get('relevance', 'N/A')}\n"
                    "----------------------------------\n"
                )

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        return True, "Email sent successfully"

    except Exception as e:
        return False, str(e)