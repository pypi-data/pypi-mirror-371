"""
Utility classes and enums for the Nanonets Document Extractor package.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pathlib import Path


class OutputType(Enum):
    """Supported output types for document extraction."""
    MARKDOWN = "markdown"
    HTML = "html"
    FIELDS = "fields"
    TABLES = "tables"
    CSV = "csv"
    FLAT_JSON = "flat-json"
    SPECIFIED_FIELDS = "specified-fields"
    SPECIFIED_JSON = "specified-json"


class Model(Enum):
    """Supported AI models."""
    GEMINI = "gemini"
    OPENAI = "openai"


class FileType(Enum):
    """Supported file types."""
    PDF = "pdf"
    IMAGE = "image"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    TEXT = "text"


def detect_file_type(file_path: str) -> FileType:
    """Detect the type of file based on extension."""
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        return FileType.PDF
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
        return FileType.IMAGE
    elif ext in ['.docx', '.doc']:
        return FileType.DOCUMENT
    elif ext in ['.xlsx', '.xls', '.csv']:
        return FileType.SPREADSHEET
    elif ext in ['.txt', '.rtf']:
        return FileType.TEXT
    else:
        from .exceptions import UnsupportedFileError
        raise UnsupportedFileError(f"Unsupported file type: {ext}")


def validate_output_type(output_type: str) -> OutputType:
    """Validate and return output type enum."""
    try:
        return OutputType(output_type)
    except ValueError:
        raise ValueError(f"Invalid output type: {output_type}. "
                        f"Supported types: {[t.value for t in OutputType]}")


def validate_model(model: str) -> Model:
    """Validate and return model enum."""
    try:
        return Model(model)
    except ValueError:
        raise ValueError(f"Invalid model: {model}. "
                        f"Supported models: {[m.value for m in Model]}")


def format_specified_fields(fields: List[str]) -> str:
    """Format specified fields list as comma-separated string."""
    if not fields:
        return ""
    return ",".join(fields)


def parse_specified_fields(fields_str: str) -> List[str]:
    """Parse comma-separated fields string to list."""
    if not fields_str:
        return []
    return [field.strip() for field in fields_str.split(",") if field.strip()] 