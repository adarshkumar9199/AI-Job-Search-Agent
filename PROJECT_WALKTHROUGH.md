# Project walkthrough and interview preparation

## 30-second explanation

I built a resume-based job matching API using Python and FastAPI. A user uploads a text-based PDF resume, the application extracts its text, identifies skills using a rule-based alias dictionary, and ranks a small local set of sample jobs. Each result includes a score breakdown and matched or missing skills, so the recommendation is explainable.

## Problem and solution

**Problem:** A candidate may spend time reading many job descriptions without quickly knowing which requirements match their resume.

**Solution:** This MVP compares resume skills with each sample job's required and preferred skills, adds a keyword-overlap score, and returns ranked results with explanations.

## How it works

1. The user uploads a PDF resume.
2. pypdf extracts selectable text. The API rejects unsupported file types, oversized files, password-protected files, files over the page limit, malformed PDFs, and PDFs with no extractable text.
3. extract_skills() searches for known skill names and aliases with phrase boundaries.
4. rank_jobs() compares detected skills with each job's required and preferred skills.
5. The API combines the skill and keyword scores, sorts the jobs, and returns the explanation.

## Scoring formula

- Required coverage = matched required skills / total required skills.
- Preferred coverage = matched preferred skills / total preferred skills.
- Skill score = 80% required coverage + 20% preferred coverage.
- Keyword score = resume/job-description token overlap divided by the number of job-description tokens.
- Overall score = 75% skill score + 25% keyword score.

These are manually chosen heuristic weights. They have not been validated against recruiter decisions or hiring outcomes. The score is not a probability of selection.

## Honest limitations

- The bundled five jobs are illustrative sample records, not live vacancies.
- Skill extraction is dictionary-based; it does not understand context like a trained NLP model.
- Scanned PDFs need OCR, which is not implemented.
- Keyword overlap can reward common words and is not semantic similarity.
- There is no database, login, deployment, or live job-board integration.
- No measured accuracy or ranking-performance metric is available yet.

## Run and verify on macOS

```bash
git clone https://github.com/adarshkumar9199/AI-Job-Search-Agent.git
cd AI-Job-Search-Agent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m unittest discover -s tests -v
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs and try GET /health, GET /api/jobs, POST /api/resume/skills, and POST /api/jobs/search with a selectable-text PDF.

## Resume bullet (do not add a metric until measured)

Developed a resume-based job matching API using Python and FastAPI, implementing PDF text extraction, rule-based skill detection, weighted job ranking, and explainable match breakdowns.

## Likely interview questions

**Is it really AI?**
It is an explainable rule-based matching MVP, not a trained AI/ML model. The project name is AI Job Search Assistant, but the current matching engine uses rules and keyword overlap.

**How is the score calculated?**
The overall score is 75% skill score and 25% keyword overlap. The skill score gives 80% weight to required skills and 20% to preferred skills.

**Why show missing skills?**
It helps candidates see which listed requirements are not detected in their resume and makes the ranking easier to understand.

**Does it fetch current jobs?**
No. It currently uses five illustrative records stored in data/jobs.json.

**What are the limitations?**
It can miss synonyms and context, scanned PDFs need OCR, and keyword overlap is not semantic understanding. The score has not been validated against real hiring outcomes.

**What would you improve next?**
I would use a larger, verified job dataset, collect human relevance labels, evaluate Precision@5 and Recall@5, and only then compare the baseline with semantic search.

## Before presenting it

- Run the app and tests yourself.
- Open the API docs and test both resume endpoints.
- Read and understand app/main.py, app/matcher.py, and the scoring formula.
- Do not claim live job integration, machine-learning model training, measured accuracy, or performance improvements unless you implement and verify them.
