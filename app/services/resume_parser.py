import os
import pdfplumber
from docx import Document
from app.utils.text_cleaner import clean_text


def extract_text_from_pdf(file_path: str) -> str:
    text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return clean_text(" ".join(text))


def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    text = [para.text for para in doc.paragraphs if para.text.strip()]
    return clean_text(" ".join(text))


def extract_resume_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Please upload PDF or DOCX.")