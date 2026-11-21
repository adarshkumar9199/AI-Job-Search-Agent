# AI Job Search Assistant

A resume-based job matching API built with Python and FastAPI. Upload a PDF resume, optionally select a role and location, and receive a ranked list of matching jobs with matched and missing skills.

> **Project status:** Initial MVP using a small local demo job dataset. It does not fetch live vacancies. Matching is based on skill overlap and keyword similarity, not a trained AI model or semantic embeddings.

## Features

- Extract text from PDF resumes using pypdf.
- Identify skills from a configurable skill list.
- Rank demo job listings using a transparent weighted score.
- Show matched and missing skills for each result.
- Filter by role and location.
- Explore API endpoints through FastAPI Swagger docs.

## How matching works

For each job:
- Skill score = matched required skills / total required skills.
- Keyword score = overlap between resume terms and job-description terms.
- Overall score = 70% skill score + 30% keyword score.

This is a simple baseline recommender. Scores are indicative and should not be treated as a hiring decision.

## Tech stack

- Python
- FastAPI
- Uvicorn
- pypdf

## Project structure

```text
AI-Job-Search-Agent/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── matcher.py
├── data/
│   └── jobs.json
├── .gitignore
├── requirements.txt
└── README.md
```

## Run locally (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to try the API.

## API

- `GET /` — service information
- `GET /health` — health check
- `GET /api/jobs` — list demo jobs
- `POST /api/jobs/search` — upload a PDF resume and get ranked matches

For `POST /api/jobs/search`, use multipart form data:
- `resume` (required): PDF file
- `role` (optional): role keyword, e.g. Data Analyst
- `location` (optional): location keyword, default is Remote
- `limit` (optional): number of results, default is 5

## Limitations and next steps

- The bundled job listings are sample data, not current vacancies.
- Scanned/image-only PDFs may not yield extractable text.
- Skill extraction uses a fixed vocabulary and can miss synonyms or context.
- Keyword overlap is not true semantic understanding.
- Future work: connect a permitted live job data provider, add tests, improve skill taxonomy, and evaluate ranking on a human-reviewed dataset.

## Attribution

This repository is an independent learning implementation based on the general idea of resume-based job discovery. It is not a fork and does not contain copied source files from [Software566/ai-job-search-agent](https://github.com/Software566/ai-job-search-agent). The referenced project provided inspiration for the problem statement; all code in this repository is newly written for this MVP.

## Privacy

Use sample resumes while testing. Do not upload sensitive personal information to an untrusted deployment. This local MVP does not persist uploaded resume files.
