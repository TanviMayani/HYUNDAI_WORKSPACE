import os
import tempfile
import unittest

from app.jobs.job_helpers import document_processing_service


class LocalUploadTests(unittest.TestCase):
    def test_save_uploaded_bytes_creates_local_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            old_cwd = os.getcwd()
            os.chdir(tmp_dir)
            try:
                file_path = document_processing_service.save_uploaded_bytes(
                    "invoice.pdf",
                    b"%PDF-1.4 test",
                    "job-123",
                )
                self.assertTrue(os.path.exists(file_path))
                self.assertTrue(file_path.endswith("invoice.pdf"))
                with open(file_path, "rb") as fh:
                    self.assertEqual(fh.read(), b"%PDF-1.4 test")
            finally:
                os.chdir(old_cwd)

    def test_generate_presigned_url_local_path(self):
        local_path = r"D:\Hyundai-IDP\uploads\job-123\invoice.pdf"
        url = document_processing_service.generate_presigned_url(local_path)
        self.assertTrue(url.startswith("http"))
        self.assertIn("/uploads/job-123/invoice.pdf", url)


if __name__ == "__main__":
    unittest.main()
