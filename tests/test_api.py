import unittest
from io import BytesIO
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.datastructures import UploadFile

from app.main import app, read_resume


class FakePage:
    def extract_text(self):
        return "Python SQL data analysis Excel communication project management"


class FakePdf:
    is_encrypted = False
    pages = [FakePage()]


class ResumeValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_non_pdf_filename(self):
        upload = UploadFile(filename="resume.docx", file=BytesIO(b"not a pdf"))
        with self.assertRaises(HTTPException) as ctx:
            await read_resume(upload)
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_rejects_file_over_size_limit_before_parsing(self):
        upload = UploadFile(filename="resume.pdf", file=BytesIO(b"x" * (5 * 1024 * 1024 + 1)))
        with self.assertRaises(HTTPException) as ctx:
            await read_resume(upload)
        self.assertEqual(ctx.exception.status_code, 413)

    async def test_rejects_malformed_pdf(self):
        upload = UploadFile(filename="resume.pdf", file=BytesIO(b"not a valid pdf"))
        with self.assertRaises(HTTPException) as ctx:
            await read_resume(upload)
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_rejects_pdf_without_extractable_text(self):
        class EmptyPage:
            def extract_text(self):
                return ""

        class EmptyPdf:
            is_encrypted = False
            pages = [EmptyPage()]

        upload = UploadFile(filename="resume.pdf", file=BytesIO(b"placeholder"))
        with patch("app.main.PdfReader", return_value=EmptyPdf()):
            with self.assertRaises(HTTPException) as ctx:
                await read_resume(upload)
        self.assertEqual(ctx.exception.status_code, 422)

    async def test_extracts_text_from_pdf_reader(self):
        upload = UploadFile(filename="resume.pdf", file=BytesIO(b"placeholder"))
        with patch("app.main.PdfReader", return_value=FakePdf()):
            result = await read_resume(upload)
        self.assertIn("Python SQL", result)


class ApiIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_home_and_health_endpoints(self):
        home = self.client.get("/")
        health = self.client.get("/health")
        self.assertEqual(home.status_code, 200)
        self.assertEqual(home.json()["version"], app.version)
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json(), {"status": "ok"})

    def test_jobs_endpoint_returns_sample_jobs(self):
        response = self.client.get("/api/jobs")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], len(payload["jobs"]))
        self.assertGreater(payload["count"], 0)

    @patch("app.main.PdfReader", return_value=FakePdf())
    def test_resume_skills_endpoint(self, _pdf_reader):
        response = self.client.post(
            "/api/resume/skills",
            files={"resume": ("resume.pdf", b"placeholder", "application/pdf")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("python", response.json()["detected_skills"])
        self.assertIn("sql", response.json()["detected_skills"])

    @patch("app.main.PdfReader", return_value=FakePdf())
    def test_job_search_endpoint_returns_ranked_explanations(self, _pdf_reader):
        response = self.client.post(
            "/api/jobs/search",
            files={"resume": ("resume.pdf", b"placeholder", "application/pdf")},
            data={"role": "Data Analyst", "location": "Remote", "limit": "5"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreater(payload["total_jobs_considered"], 0)
        self.assertGreater(len(payload["results"]), 0)
        self.assertIn("match_score", payload["results"][0])
        self.assertIn("matched_skills", payload["results"][0])
        self.assertIn("missing_required_skills", payload["results"][0])

    def test_job_search_rejects_invalid_limit(self):
        response = self.client.post(
            "/api/jobs/search",
            files={"resume": ("resume.pdf", b"placeholder", "application/pdf")},
            data={"limit": "25"},
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
