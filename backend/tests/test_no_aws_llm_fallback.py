import io
import os
import tempfile
import unittest

from PIL import Image

from app.jobs.extract_llm import DocumentLLMService


class NoAWSFallbackTests(unittest.TestCase):
    def test_external_llm_is_disabled_by_default(self):
        from unittest.mock import patch
        with patch.dict(os.environ, {"EXTERNAL_LLM_ENABLED": "false"}):
            service = DocumentLLMService()
            self.assertFalse(service.use_external_llm)

    def test_form_extract_llm_returns_local_fallback_without_aws(self):
        service = DocumentLLMService()

        image = Image.new("RGB", (50, 50), color=(255, 255, 255))
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")

        response, input_tokens, output_tokens = service.form_extract_llm(
            image_bytes.getvalue(),
            None,
            1,
        )

        self.assertIsInstance(response, dict)
        self.assertIn("form", response)
        self.assertIsInstance(response["form"], dict)
        self.assertIsNone(input_tokens)
        self.assertIsNone(output_tokens)


if __name__ == "__main__":
    unittest.main()
