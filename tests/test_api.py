import unittest
from io import BytesIO
from unittest.mock import patch

from fastapi import HTTPException
from starlette.datastructures import UploadFile

from app.main import read_resume


class ResumeValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_non_pdf_filename(self):
        upload = UploadFile(filename='resume.docx', file=BytesIO(b'not a pdf'))
        with self.assertRaises(HTTPException) as ctx:
            await read_resume(upload)
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_rejects_file_over_size_limit_before_parsing(self):
        upload = UploadFile(filename='resume.pdf', file=BytesIO(b'x' * (5 * 1024 * 1024 + 1)))
        with self.assertRaises(HTTPException) as ctx:
            await read_resume(upload)
        self.assertEqual(ctx.exception.status_code, 413)

    async def test_rejects_malformed_pdf(self):
        upload = UploadFile(filename='resume.pdf', file=BytesIO(b'not a valid pdf'))
        with self.assertRaises(HTTPException) as ctx:
            await read_resume(upload)
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_rejects_pdf_without_extractable_text(self):
        class EmptyPage:
            def extract_text(self): return ''
        class EmptyPdf:
            is_encrypted = False
            pages = [EmptyPage()]
        upload = UploadFile(filename='resume.pdf', file=BytesIO(b'placeholder'))
        with patch('app.main.PdfReader', return_value=EmptyPdf()):
            with self.assertRaises(HTTPException) as ctx:
                await read_resume(upload)
        self.assertEqual(ctx.exception.status_code, 422)

    async def test_extracts_text_from_pdf_reader(self):
        class TextPage:
            def extract_text(self): return 'Python SQL data analysis'
        class TextPdf:
            is_encrypted = False
            pages = [TextPage()]
        upload = UploadFile(filename='resume.pdf', file=BytesIO(b'placeholder'))
        with patch('app.main.PdfReader', return_value=TextPdf()):
            result = await read_resume(upload)
        self.assertEqual(result, 'Python SQL data analysis')


if __name__ == '__main__':
    unittest.main()
