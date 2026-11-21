import re
from typing import Any

SKILLS = {
    "python", "sql", "excel", "power bi", "tableau", "machine learning",
    "data analysis", "statistics", "communication", "project management",
    "fastapi", "flask", "html", "css", "javascript", "react",
    "chemical engineering", "process simulation", "mass transfer",
    "heat transfer", "fluid mechanics", "matlab", "autocad"
}

STOP_WORDS = {
    "the", "and", "for", "with", "from", "that", "this", "you", "your",
    "are", "our", "will", "have", "has", "into", "about", "their", "they",
    "job", "role", "work", "team", "using", "use", "ability", "skills"
}


def extract_skills(text: str) -> set[str]:
    normalized = text.lower()
    found = set()
    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, normalized):
            found.add(skill)
    return found


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*", text.lower())
    return {word for word in words if len(word) > 2 and word not in STOP_WORDS}


def rank_jobs(resume_text: str, jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    resume_skills = extract_skills(resume_text)
    resume_terms = tokenize(resume_text)
    results = []

    for job in jobs:
        required = {skill.lower() for skill in job.get("required_skills", [])}
        matched = sorted(resume_skills & required)
        missing = sorted(required - resume_skills)
        skill_score = len(matched) / len(required) if required else 0.0

        job_terms = tokenize(job.get("title", "") + " " + job.get("description", ""))
        keyword_score = len(resume_terms & job_terms) / len(job_terms) if job_terms else 0.0

        overall = (0.70 * skill_score) + (0.30 * keyword_score)
        results.append({
            **job,
            "match_score": round(overall * 100, 2),
            "skill_score": round(skill_score * 100, 2),
            "keyword_score": round(keyword_score * 100, 2),
            "matched_skills": matched,
            "missing_skills": missing,
        })

    return sorted(results, key=lambda item: item["match_score"], reverse=True)
