# AI Job Search Assistant

A resume-based job matching API built with Python and FastAPI. Upload a PDF resume, inspect extracted skills, and receive ranked sample jobs with a transparent explanation of each score.

> **Project status:** Learning MVP. It uses a local sample-job dataset and rule-based matching. It does not fetch live vacancies, use a trained language model, or predict hiring outcomes.

## Features

- Extract selectable text from PDF resumes with pypdf.
- Detect canonical skills using a small alias dictionary (for example, PowerBI → Power BI).
- Preview extracted skills before job matching.
- Rank jobs using required skills, preferred skills, and job-description keyword overlap.
- Explain each result with matched/missing skills, score breakdown, and match category.
- Filter sample jobs by role and location.
- Validate file type, file size, page count, encrypted PDFs, and empty/scanned PDFs.
- Run automated unit tests for extraction and ranking logic.

## Matching approach

This is an explainable baseline, not semantic AI.

1. **Required skill coverage** = matched required skills / total required skills.
2. **Preferred skill coverage** = matched preferred skills / total preferred skills.
3. **Skill score** = 80% required coverage + 20% preferred coverage.
4. **Keyword score** = overlap between resume terms and job title/description terms, divided by job terms.
5. **Overall match score** = 75% skill score + 25% keyword score.

The API also returns matched and missing required skills, matched preferred skills, and a simple match category. A score is a heuristic ranking signal, not a probability of getting hired.

## Tech stack

- Python
- FastAPI and Uvicorn
- pypdf
- unittest (Python standard library)

## Project structure

```text
AI-Job-Search-Agent/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── matcher.py
├── data/
│   └── jobs.json
├── tests/
│   └── test_matcher.py
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

Open http://127.0.0.1:8000/docs for interactive API documentation.

## Run tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

## API endpoints

- `GET /` — service information and version
- `GET /health` — health check
- `GET /api/jobs` — list sample jobs
- `POST /api/resume/skills` — upload a PDF and preview detected skills
- `POST /api/jobs/search` — upload a PDF and retrieve ranked sample jobs

For the search endpoint, send multipart form data:
- `resume` (required): PDF file
- `role` (optional): title filter, e.g. Data Analyst
- `location` (optional): location filter; Remote listings remain eligible
- `limit` (optional): 1–20, default 5

## Limitations and next steps

- The five bundled job records are illustrative sample data, not current vacancies.
- Skill extraction uses a manually maintained vocabulary and can miss context, synonyms, and equivalent experience.
- Keyword overlap is not semantic understanding.
- Scanned PDFs require OCR, which is not included.
- No persistent database, authentication, live job provider, or deployment pipeline is included.
- Next: add a larger reviewed dataset, evaluate ranking with Precision@K/Recall@K, expand tests, and integrate a permitted live job source.

## Attribution

This is an independent learning implementation of a resume-to-job matching idea. It is not a fork and does not contain copied source files from [Software566/ai-job-search-agent](https://github.com/Software566/ai-job-search-agent). The referenced repository inspired the problem statement.

## Privacy

The API processes the uploaded resume in memory and does not save it to disk. Use sample resumes while testing and avoid deploying with real personal data until appropriate security controls are added.

## Author

**Adarsh Kumar**  
Email: [adarsh.kumar919976@gmail.com](mailto:adarsh.kumar919976@gmail.com)

*Developed as a learning project with AI assistance. The author should review, run, test, and understand the implementation before presenting it as their own work.*
