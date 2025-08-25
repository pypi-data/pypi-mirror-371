"""
Nanonets Document Extractor

A Python library for extracting data from any document using AI.
"""

__version__ = "0.2.2"

from .extractor import DocumentExtractor
from .utils import OutputType
from .exceptions import (
    ExtractionError, 
    UnsupportedFileError, 
    APIError, 
    ModelError
)

__all__ = [
    "DocumentExtractor",
    "OutputType",
    "ExtractionError",
    "UnsupportedFileError", 
    "APIError",
    "ModelError",
] 