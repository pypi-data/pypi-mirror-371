"""
Main DocumentExtractor class for document extraction.
"""

import os
from typing import Dict, List, Any, Optional

from .exceptions import (
    ExtractionError, UnsupportedFileError, APIError, ModelError
)
from .utils import (
    OutputType, FileType, validate_output_type, 
    validate_model, detect_file_type, format_specified_fields
)
from .processors.cloud_processor import CloudProcessor


class DocumentExtractor:
    """
    Main class for document extraction.
    
    Provides a simple interface for extracting data from any document.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the DocumentExtractor.
        
        Args:
            api_key: Optional API key for unlimited access. If not provided, 
                    uses free tier with rate limits. Get your free API key from:
                    https://app.nanonets.com/#/keys
            model: Optional AI model ("gemini" or "openai")
            **kwargs: Additional arguments
        """
        self.api_key = api_key or "free-to-use"
        self.model = validate_model(model).value if model else None
        self.kwargs = kwargs
        
        # Initialize the processor
        self._processor = CloudProcessor(api_key=self.api_key, model=self.model, **self.kwargs)
    
    def extract(
        self,
        file_path: str,
        output_type: str = "flat-json",
        specified_fields: Optional[List[str]] = None,
        json_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract data from a document.
        
        Args:
            file_path: Path to the document file
            output_type: Type of output ("markdown", "flat-json", "specified-fields", "specified-json")
            specified_fields: List of field names to extract (for "specified-fields" output)
            json_schema: Custom JSON schema (for "specified-json" output)
            
        Returns:
            Dictionary containing extracted data
            
        Raises:
            ExtractionError: If extraction fails
            UnsupportedFileError: If file type is not supported
            ValueError: If parameters are invalid
        """
        # Validate parameters
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        output_type_enum = validate_output_type(output_type)
        
        # Detect file type
        try:
            file_type = detect_file_type(file_path)
        except UnsupportedFileError as e:
            raise UnsupportedFileError(
                f"Unsupported file type for {file_path}. "
                f"Supported types: PDF, images (PNG, JPG, TIFF, BMP), "
                f"documents (DOCX, DOC), spreadsheets (XLSX, XLS, CSV), "
                f"text files (TXT, RTF). Error: {e}"
            )
        
        # Prepare extraction parameters
        extraction_params = {
            "file_path": file_path,
            "file_type": file_type,
            "output_type": output_type_enum,
        }
        
        # Add mode-specific parameters
        if output_type_enum == OutputType.SPECIFIED_FIELDS:
            if not specified_fields:
                raise ValueError("specified_fields is required for 'specified-fields' output type")
            extraction_params["specified_fields"] = specified_fields
        
        elif output_type_enum == OutputType.SPECIFIED_JSON:
            if not json_schema:
                raise ValueError("json_schema is required for 'specified-json' output type")
            extraction_params["json_schema"] = json_schema
        
        # Perform extraction
        try:
            result = self._processor.extract(**extraction_params)
            return result
        except Exception as e:
            if isinstance(e, (ExtractionError, APIError, ModelError)):
                raise
            else:
                raise ExtractionError(f"Extraction failed: {str(e)}")
    
    def extract_batch(
        self,
        file_paths: List[str],
        output_type: str = "flat-json",
        specified_fields: Optional[List[str]] = None,
        json_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract data from multiple documents.
        
        Args:
            file_paths: List of file paths to process
            output_type: Type of output
            specified_fields: List of field names to extract
            json_schema: Custom JSON schema
            
        Returns:
            Dictionary mapping file paths to extraction results
        """
        results = {}
        
        for file_path in file_paths:
            try:
                result = self.extract(
                    file_path=file_path,
                    output_type=output_type,
                    specified_fields=specified_fields,
                    json_schema=json_schema
                )
                results[file_path] = result
            except Exception as e:
                results[file_path] = {"error": str(e)}
        
        return results
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return [
            ".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif",
            ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".rtf"
        ]
    
    def get_processing_info(self) -> Dict[str, Any]:
        """Get information about the current processing setup."""
        info = {
            "mode": "cloud", # Simplified mode
            "supported_formats": self.get_supported_formats(),
            "output_types": [ot.value for ot in OutputType],
            "api_key_configured": bool(self.api_key)
        }
        
        return info 