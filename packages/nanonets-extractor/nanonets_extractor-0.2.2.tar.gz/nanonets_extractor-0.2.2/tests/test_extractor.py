"""
Unit tests for the DocumentExtractor class.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch

from nanonets_extractor import DocumentExtractor
from nanonets_extractor.exceptions import ExtractionError, UnsupportedFileError
from nanonets_extractor.utils import OutputType


class TestDocumentExtractor(unittest.TestCase):
    """Test cases for DocumentExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary test file
        self.test_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        self.test_file.write(b"dummy content")
        self.test_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)
    
    def test_extractor_initialization(self):
        """Test DocumentExtractor initialization."""
        # Default initialization (free tier)
        extractor = DocumentExtractor()
        self.assertEqual(extractor.api_key, "free-to-use")
        self.assertIsNone(extractor.model)
        
        # With API key
        extractor = DocumentExtractor(api_key="custom_key")
        self.assertEqual(extractor.api_key, "custom_key")
        
        # With model
        extractor = DocumentExtractor(model="openai")
        self.assertEqual(extractor.model, "openai")
        
        # With both API key and model
        extractor = DocumentExtractor(api_key="custom_key", model="gemini")
        self.assertEqual(extractor.api_key, "custom_key")
        self.assertEqual(extractor.model, "gemini")
    
    def test_invalid_model(self):
        """Test initialization with invalid model."""
        with self.assertRaises(ValueError):
            DocumentExtractor(model="invalid_model")
    
    @patch('nanonets_extractor.extractor.CloudProcessor')
    def test_basic_extraction(self, mock_cloud_processor):
        """Test basic extraction."""
        # Mock the processor
        mock_processor = Mock()
        mock_processor.extract.return_value = {"text": "extracted content"}
        mock_cloud_processor.return_value = mock_processor
        
        extractor = DocumentExtractor()
        result = extractor.extract(self.test_file.name, output_type="flat-json")
        
        self.assertEqual(result, {"text": "extracted content"})
        mock_processor.extract.assert_called_once()
    
    def test_file_not_found(self):
        """Test extraction with non-existent file."""
        extractor = DocumentExtractor()
        
        with self.assertRaises(FileNotFoundError):
            extractor.extract("non_existent_file.pdf")
    
    def test_invalid_output_type(self):
        """Test extraction with invalid output type."""
        extractor = DocumentExtractor()
        
        with self.assertRaises(ValueError):
            extractor.extract(self.test_file.name, output_type="invalid")
    
    def test_specified_fields_without_fields(self):
        """Test specified-fields output type without fields."""
        extractor = DocumentExtractor()
        
        with self.assertRaises(ValueError):
            extractor.extract(self.test_file.name, output_type="specified-fields")
    
    def test_specified_json_without_schema(self):
        """Test specified-json output type without schema."""
        extractor = DocumentExtractor()
        
        with self.assertRaises(ValueError):
            extractor.extract(self.test_file.name, output_type="specified-json")
    
    @patch('nanonets_extractor.extractor.CloudProcessor')
    def test_batch_extraction(self, mock_cloud_processor):
        """Test batch extraction."""
        # Mock the processor
        mock_processor = Mock()
        mock_processor.extract.return_value = {"text": "extracted content"}
        mock_cloud_processor.return_value = mock_processor
        
        extractor = DocumentExtractor()
        results = extractor.extract_batch([self.test_file.name], output_type="flat-json")
        
        self.assertIn(self.test_file.name, results)
        self.assertEqual(results[self.test_file.name], {"text": "extracted content"})
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        extractor = DocumentExtractor()
        formats = extractor.get_supported_formats()
        
        self.assertIsInstance(formats, list)
        self.assertIn(".pdf", formats)
        self.assertIn(".jpg", formats)
        self.assertIn(".docx", formats)
    
    def test_get_processing_info(self):
        """Test getting processing info."""
        extractor = DocumentExtractor()
        info = extractor.get_processing_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn("mode", info)
        self.assertIn("supported_formats", info)
        self.assertIn("output_types", info)
        self.assertIn("api_key_configured", info)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_validate_output_type(self):
        """Test output type validation."""
        from nanonets_extractor.utils import validate_output_type
        
        # Valid types
        self.assertEqual(validate_output_type("markdown"), OutputType.MARKDOWN)
        self.assertEqual(validate_output_type("html"), OutputType.HTML)
        self.assertEqual(validate_output_type("fields"), OutputType.FIELDS)
        self.assertEqual(validate_output_type("tables"), OutputType.TABLES)
        self.assertEqual(validate_output_type("csv"), OutputType.CSV)
        self.assertEqual(validate_output_type("flat-json"), OutputType.FLAT_JSON)
        self.assertEqual(validate_output_type("specified-fields"), OutputType.SPECIFIED_FIELDS)
        self.assertEqual(validate_output_type("specified-json"), OutputType.SPECIFIED_JSON)
        
        # Invalid type
        with self.assertRaises(ValueError):
            validate_output_type("invalid")
    
    def test_validate_model(self):
        """Test model validation."""
        from nanonets_extractor.utils import validate_model, Model
        
        # Valid models
        self.assertEqual(validate_model("gemini"), Model.GEMINI)
        self.assertEqual(validate_model("openai"), Model.OPENAI)
        
        # Invalid model
        with self.assertRaises(ValueError):
            validate_model("invalid")
    
    def test_detect_file_type(self):
        """Test file type detection."""
        from nanonets_extractor.utils import detect_file_type, FileType
        
        # Valid file types
        self.assertEqual(detect_file_type("test.pdf"), FileType.PDF)
        self.assertEqual(detect_file_type("test.jpg"), FileType.IMAGE)
        self.assertEqual(detect_file_type("test.docx"), FileType.DOCUMENT)
        self.assertEqual(detect_file_type("test.xlsx"), FileType.SPREADSHEET)
        self.assertEqual(detect_file_type("test.txt"), FileType.TEXT)
        
        # Invalid file type
        with self.assertRaises(UnsupportedFileError):
            detect_file_type("test.xyz")
    

if __name__ == '__main__':
    unittest.main() 