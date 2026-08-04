import unittest
from unittest.mock import MagicMock
from app.jobs.jobs_access import JobDocumentService

class MethodValidationTests(unittest.TestCase):
    def test_get_method_from_id_with_invalid_uuid(self):
        db_mock = MagicMock()
        # "string" is not a valid UUID, should return (None, None) and not call the database
        display_name, internal_name = JobDocumentService.get_method_from_id(db_mock, "string")
        self.assertIsNone(display_name)
        self.assertIsNone(internal_name)
        db_mock.query.assert_not_called()

    def test_get_method_from_id_with_valid_but_non_existent_uuid(self):
        db_mock = MagicMock()
        query_mock = db_mock.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = None
        
        display_name, internal_name = JobDocumentService.get_method_from_id(db_mock, "00000000-0000-0000-0000-000000000000")
        self.assertIsNone(display_name)
        self.assertIsNone(internal_name)
        db_mock.query.assert_called_once()

    def test_get_method_from_id_with_valid_exist_uuid(self):
        db_mock = MagicMock()
        mock_method = MagicMock()
        mock_method.display_name = "LLM Extraction"
        mock_method.internal_name = "llm"
        query_mock = db_mock.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = mock_method
        
        display_name, internal_name = JobDocumentService.get_method_from_id(db_mock, "11111111-2222-3333-4444-555555555555")
        self.assertEqual(display_name, "LLM Extraction")
        self.assertEqual(internal_name, "llm")
        db_mock.query.assert_called_once()

if __name__ == "__main__":
    unittest.main()
