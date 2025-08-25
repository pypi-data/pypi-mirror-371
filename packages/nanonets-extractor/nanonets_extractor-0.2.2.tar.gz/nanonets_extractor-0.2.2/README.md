# This Project has been moved to
## https://github.com/NanoNets/docstrange

# Try live demo
## https://docstrange.nanonets.com


# Nanonets Document Extractor

[![PyPI version](https://badge.fury.io/py/nanonets-extractor.svg)](https://badge.fury.io/py/nanonets-extractor)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/nanonets-extractor)](https://pypi.org/project/nanonets-extractor/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nanonets-extractor)](https://pypi.org/project/nanonets-extractor/)
[![PyPI - License](https://img.shields.io/pypi/l/nanonets-extractor)](https://github.com/NanoNets/document-extractor/blob/main/LICENSE)

A Python library for extracting data from any document using AI.

> **🚀 Try it instantly!** Visit [extraction-api.nanonets.com](https://extraction-api.nanonets.com) to access our hosted document extractors with a user-friendly interface.

## Quick Start

### Installation

```bash
pip install nanonets-extractor
```

### Basic Usage

```python
from nanonets_extractor import DocumentExtractor

# Initialize extractor
extractor = DocumentExtractor()

# Extract data from any document
result = extractor.extract(
    file_path="invoice.pdf",
    output_type="flat-json"
)

print(result)
```

## Initialization Parameters

### DocumentExtractor()

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `api_key` | str | No | API key for unlimited access (optional - uses free tier if not provided) |
| `model` | str | No | AI model: `"gemini"` or `"openai"` (optional) |

### Examples

```python
# Free tier (with rate limits)
extractor = DocumentExtractor()

# Unlimited access with API key
extractor = DocumentExtractor(api_key="your_api_key")

# Specify a particular model with API key
extractor = DocumentExtractor(api_key="your_api_key", model="openai")
```

**💡 Getting Your API Key**: If you hit rate limits, get your **FREE** API key from [https://app.nanonets.com/#/keys](https://app.nanonets.com/#/keys) for unlimited access.

## Extract Method

### extractor.extract()

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | str | Yes | Path to your document |
| `output_type` | str | No | Output format (default: "flat-json") |
| `specified_fields` | list | No | Extract only specific fields |
| `json_schema` | dict | No | Custom JSON schema for output |

### Output Types

| Type | Description | Parameters Required |
|------|-------------|-------------------|
| `"markdown"` | Clean markdown formatting | None |
| `"html"` | Semantic HTML structure | None |
| `"fields"` | Auto-detected key-value pairs | None |
| `"tables"` | Structured table data | None |
| `"csv"` | Tabular data and CSV format | None |
| `"flat-json"` | Flat key-value JSON | None |
| `"specified-fields"` | Custom field extraction | `specified_fields` |
| `"specified-json"` | Custom schema extraction | `json_schema` |

## Supported Document Types

Works with **any document type**:
- 📄 **PDFs** - Invoices, contracts, reports
- 🖼️ **Images** - Screenshots, photos, scans  
- 📊 **Spreadsheets** - Excel, CSV files
- 📝 **Text Documents** - Word docs, text files
- 🆔 **ID Documents** - Passports, licenses, certificates
- 🧾 **Receipts** - Any receipt or bill

## Examples

### Basic Extraction
```python
from nanonets_extractor import DocumentExtractor

extractor = DocumentExtractor()

# Extract all data as key-value pairs
result = extractor.extract("document.pdf", output_type="fields")
print(result)
```

### Different Output Formats
```python
# Get clean markdown formatting
result = extractor.extract("document.pdf", output_type="markdown")
print(result)

# Get semantic HTML structure
result = extractor.extract("document.pdf", output_type="html")
print(result)

# Extract structured table data
result = extractor.extract("document.pdf", output_type="tables")
print(result)

# Get CSV format for tabular data
result = extractor.extract("document.pdf", output_type="csv")
print(result)
```

### Extract Specific Fields
```python
# Extract only specific fields
result = extractor.extract(
    file_path="invoice.pdf",
    output_type="specified-fields", 
    specified_fields=["invoice_number", "total", "customer_name"]
)
```

### Custom JSON Schema
```python
# Use custom schema
schema = {
    "invoice_number": "string",
    "line_items": [
        {
            "description": "string",
            "amount": "number"
        }
    ]
}

result = extractor.extract(
    file_path="invoice.pdf",
    output_type="specified-json",
    json_schema=schema
)
```

### Batch Processing
```python
# Process multiple files
files = ["doc1.pdf", "doc2.jpg", "doc3.docx"]
results = extractor.extract_batch(
    file_paths=files,
    output_type="fields"
)

for file_path, result in results.items():
    print(f"{file_path}: {result}")
```

## Command Line Interface

```bash
# Free tier (with rate limits)
nanonets-extractor document.pdf

# With API key for unlimited access
nanonets-extractor document.pdf --api-key your_api_key

# Specify output format with API key
nanonets-extractor document.pdf --api-key your_api_key --output-type markdown

# Extract specific fields
nanonets-extractor invoice.pdf --output-type specified-fields --fields "invoice_number,total,date"

# Save to file
nanonets-extractor document.pdf --output result.json

# Process multiple files
nanonets-extractor *.pdf --output-dir results/
```

## Error Handling

```python
from nanonets_extractor import DocumentExtractor
from nanonets_extractor.exceptions import ExtractionError, UnsupportedFileError

extractor = DocumentExtractor()

try:
    result = extractor.extract("document.pdf")
    print(result)
except UnsupportedFileError as e:
    print(f"File type not supported: {e}")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Supported File Formats

- **PDFs**: `.pdf`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.gif`
- **Documents**: `.docx`, `.doc`
- **Spreadsheets**: `.xlsx`, `.xls`, `.csv`
- **Text**: `.txt`, `.rtf`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 