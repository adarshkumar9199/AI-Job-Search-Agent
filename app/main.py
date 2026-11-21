import json
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pypdf import PdfReader

from app.matcher import rank_jobs

BASE_DIR = Path(__file__).resolve().parent.parent
JOBS_FILE = BASE_DIR / "data" / "jobs.json"

app = FastAPI(
    title="AI Job Search Assistant",
    description="A resume-based job matching MVP using skill overlap and keyword similarity.",
    version="1.0.0",
)


def load_jobs() -> list[dict]:
    with JOBS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/")
def home():
    return {
        "message": "AI Job Search Assistant API",
        "docs": "/docs",
        "note": "Uses sample job listings; no live job feed is connected."
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/jobs")
def get_jobs():
    return load_jobs()


@app.post("/api/jobs/search")
async def search_jobs(
    resume: UploadFile = File(...),
    role: str = Form(""),
    location: str = Form("Remote"),
    limit: int = Form(5),
):
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")

    if limit < 1 or limit > 20:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 20.")

    try:
        content = await resume.read()
        from io import BytesIO
        reader = PdfReader(BytesIO(content))
        resume_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read this PDF file.") from exc

    if not resume_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No selectable text found. Scanned PDFs need OCR before matching."
        )

    jobs = load_jobs()
    if role.strip():
        jobs = [job for job in jobs if role.lower() in job["title"].lower()]
    if location.strip() and location.lower() != "remote":
        jobs = [
            job for job in jobs
            if location.lower() in job.get("location", "").lower()
            or job.get("location", "").lower() == "remote"
        ]

    ranked = rank_jobs(resume_text, jobs)
    return {
        "total_jobs_considered": len(ranked),
        "results": ranked[:limit],
        "matching_method": "70% skill overlap + 30% keyword overlap",
        "disclaimer": "Demo recommendations only; not live vacancies or hiring advice."
    }
