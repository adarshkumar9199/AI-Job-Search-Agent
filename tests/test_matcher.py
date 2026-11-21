import unittest

from app.matcher import extract_skills, rank_jobs


class SkillExtractionTests(unittest.TestCase):
    def test_detects_aliases_as_canonical_skills(self):
        skills = extract_skills("Built dashboards in PowerBI and analysed data with Python3.")
        self.assertIn("power bi", skills)
        self.assertIn("data analysis", skills)
        self.assertIn("python", skills)

    def test_does_not_match_partial_words(self):
        self.assertNotIn("sql", extract_skills("NoSQL databases"))


class RankingTests(unittest.TestCase):
    def test_ranks_better_skill_fit_first(self):
        jobs = [
            {"title": "Role A", "required_skills": ["python", "sql"], "description": "Python SQL reporting"},
            {"title": "Role B", "required_skills": ["react", "css"], "description": "Frontend interface"},
        ]
        ranked = rank_jobs("Python and SQL reporting experience", jobs)
        self.assertEqual(ranked[0]["title"], "Role A")
        self.assertGreaterEqual(ranked[0]["match_score"], ranked[1]["match_score"])

    def test_returns_explanation_fields(self):
        jobs = [{"title": "Analyst", "required_skills": ["sql", "excel"], "preferred_skills": ["tableau"], "description": "Reports"}]
        result = rank_jobs("SQL and Excel", jobs)[0]
        self.assertEqual(result["matched_skills"], ["excel", "sql"])
        self.assertEqual(result["missing_skills"], [])
        self.assertEqual(result["matched_preferred_skills"], [])
        self.assertIn("match_level", result)
        self.assertIn("required_skill_score", result)

    def test_empty_resume_has_zero_match(self):
        result = rank_jobs("", [{"title": "Analyst", "required_skills": ["sql"], "description": ""}])[0]
        self.assertEqual(result["match_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
