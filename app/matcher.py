import re
from typing import Any

# Canonical skills and common resume variants. Keep this list editable as the
# project grows; extraction is rule-based, not a trained language model.
SKILL_ALIASES = {
    "python": ["python", "python3"],
    "sql": ["sql", "structured query language"],
    "excel": ["excel", "microsoft excel", "ms excel"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "machine learning": ["machine learning", "ml"],
    "data analysis": ["data analysis", "data analytics", "data analyst"],
    "statistics": ["statistics", "statistical analysis"],
    "communication": ["communication", "stakeholder communication"],
    "project management": ["project management", "project coordination"],
    "fastapi": ["fastapi", "fast api"],
    "flask": ["flask"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "javascript": ["javascript", "js"],
    "react": ["react", "reactjs", "react.js"],
    "chemical engineering": ["chemical engineering"],
    "process simulation": ["process simulation", "process modelling", "process modeling"],
    "mass transfer": ["mass transfer"],
    "heat transfer": ["heat transfer"],
    "fluid mechanics": ["fluid mechanics", "fluid flow"],
    "matlab": ["matlab"],
    "autocad": ["autocad", "auto cad"],
}

STOP_WORDS = {
    "the", "and", "for", "with", "from", "that", "this", "you", "your",
    "are", "our", "will", "have", "has", "into", "about", "their", "they",
    "job", "role", "work", "team", "using", "use", "ability", "skills",
    "who", "what", "when", "where", "how", "all", "can", "not", "but",
}


def _contains_phrase(text: str, phrase: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(phrase.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text.lower()) is not None


def extract_skills(text: str) -> set[str]:
    """Return canonical skills found using phrase-boundary alias matching."""
    normalized = text.lower()
    found = set()
    for canonical, aliases in SKILL_ALIASES.items():
        if any(_contains_phrase(normalized, alias) for alias in aliases):
            found.add(canonical)
    return found


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*", text.lower())
    return {word for word in words if len(word) > 2 and word not in STOP_WORDS}


def _percentage(value: float) -> float:
    return round(max(0.0, min(value, 1.0)) * 100, 2)


def rank_jobs(resume_text: str, jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank jobs with explainable required/preferred skill and keyword scores."""
    resume_skills = extract_skills(resume_text)
    resume_terms = tokenize(resume_text)
    results = []

    for job in jobs:
        required = {str(skill).lower() for skill in job.get("required_skills", [])}
        preferred = {str(skill).lower() for skill in job.get("preferred_skills", [])}
        matched_required = sorted(resume_skills & required)
        missing_required = sorted(required - resume_skills)
        matched_preferred = sorted(resume_skills & preferred)

        required_score = len(matched_required) / len(required) if required else 1.0
        preferred_score = len(matched_preferred) / len(preferred) if preferred else required_score
        skill_score = (0.80 * required_score) + (0.20 * preferred_score)

        job_terms = tokenize(job.get("title", "") + " " + job.get("description", ""))
        keyword_score = len(resume_terms & job_terms) / len(job_terms) if job_terms else 0.0
        overall = (0.75 * skill_score) + (0.25 * keyword_score)

        if overall >= 0.75:
            match_level = "Strong match"
        elif overall >= 0.45:
            match_level = "Potential match"
        else:
            match_level = "Low match"

        results.append({
            **job,
            "match_score": _percentage(overall),
            "skill_score": _percentage(skill_score),
            "required_skill_score": _percentage(required_score),
            "preferred_skill_score": _percentage(preferred_score),
            "keyword_score": _percentage(keyword_score),
            "match_level": match_level,
            "matched_skills": matched_required,
            "missing_skills": missing_required,
            "matched_preferred_skills": matched_preferred,
        })

    return sorted(results, key=lambda item: (-item["match_score"], item.get("title", "").lower()))
