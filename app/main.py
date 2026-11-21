import json
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pypdf import PdfReader

from app.matcher import extract_skills, rank_jobs

BASE_DIR = Path(__file__).resolve().parent.parent
JOBS_FILE = BASE_DIR / "data" / "jobs.json"
MAX_RESUME_BYTES = 5 * 1024 * 1024

app = FastAPI(
    title="AI Job Search Assistant",
    description="An explainable resume-to-job matching MVP using rule-based skills and keyword overlap.",
    version="1.1.0",
)


def load_jobs() -> list[dict]:
    with JOBS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/")
def home():
    return {
        "message": "AI Job Search Assistant API",
        "docs": "/docs",
        "version": app.version,
        "note": "Uses sample job listings; no live job feed is connected."
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/jobs")
def get_jobs():
    return {"count": len(load_jobs()), "jobs": load_jobs()}


@app.post("/api/resume/skills")
async def preview_resume_skills(resume: UploadFile = File(...)):
    """Extract selectable PDF text and return the skills detected in it."""
    resume_text = await read_resume(resume)
    return {
        "detected_skills": sorted(extract_skills(resume_text)),
        "note": "Rule-based extraction; review results because synonyms and context may be missed."
    }


async def read_resume(resume: UploadFile) -> str:
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")

    content = await resume.read()
    if len(content) > MAX_RESUME_BYTES:
        raise HTTPException(status_code=413, detail="Resume PDF must be 5 MB or smaller.")

    try:
        reader = PdfReader(BytesIO(content))
        if reader.is_encrypted:
            raise HTTPException(status_code=400, detail="Password-protected PDFs are not supported.")
        if len(reader.pages) > 30:
            raise HTTPException(status_code=413, detail="Resume PDF must contain 30 pages or fewer.")
        resume_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read this PDF file.") from exc

    if not resume_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No selectable text found. Scanned PDFs need OCR before matching."
        )
    return resume_text


@app.post("/api/jobs/search")
async def search_jobs(
    resume: UploadFile = File(...),
    role: str = Form(""),
    location: str = Form("Remote"),
    limit: int = Form(5),
):
    if limit < 1 or limit > 20:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 20.")

    resume_text = await read_resume(resume)
    jobs = load_jobs()

    if role.strip():
        jobs = [job for job in jobs if role.strip().lower() in job["title"].lower()]
    if location.strip() and location.strip().lower() != "remote":
        jobs = [
            job for job in jobs
            if location.strip().lower() in job.get("location", "").lower()
            or job.get("location", "").lower() == "remote"
        ]

    ranked = rank_jobs(resume_text, jobs)
    return {
        "total_jobs_considered": len(ranked),
        "resume_skills_detected": sorted(extract_skills(resume_text)),
        "results": ranked[:limit],
        "scoring_method": {
            "overall": "75% skill score + 25% keyword overlap",
            "skill_score": "80% required-skill coverage + 20% preferred-skill coverage",
            "note": "Scores are heuristic indicators, not probabilities of getting hired."
        },
        "disclaimer": "Demo recommendations only; listings are sample data, not live vacancies."
    }
