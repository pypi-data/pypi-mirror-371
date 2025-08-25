# Installation Guide

This guide will help you install and set up the Nanonets Document Extractor package.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

Install the package with minimal dependencies:

```bash
pip install nanonets-extractor
```

That's it! The package only requires `requests` as a dependency and works out of the box.

## Development Installation

For development and testing:

```bash
git clone https://github.com/nanonets/document-extractor.git
cd document-extractor
pip install -e .[dev]
```

## Verification

After installation, verify that everything is working:

```python
from nanonets_extractor import DocumentExtractor

# Test basic functionality
extractor = DocumentExtractor()
print("✅ Installation successful!")
print("Processing info:", extractor.get_processing_info())
```

## Usage

```python
from nanonets_extractor import DocumentExtractor

# Initialize extractor (no API key needed!)
extractor = DocumentExtractor()

# Extract data from any document
result = extractor.extract("document.pdf")
print(result)
```

## Troubleshooting

### Common Issues

1. **Import errors**
   - Make sure you're using Python 3.8 or higher
   - Verify the package is installed: `pip list | grep nanonets`

2. **Network connectivity**
   - The package requires internet access for cloud processing
   - Check your network connection if extraction fails

### Getting Help

- Check the [documentation](https://docs.nanonets.com)
- Visit the [GitHub repository](https://github.com/nanonets/document-extractor)
- Report issues on [GitHub Issues](https://github.com/nanonets/document-extractor/issues)

## Next Steps

After installation, check out the examples in the `examples/` directory:

- `examples/basic_usage.py` - Basic usage examples
- `examples/batch_processing.py` - Batch processing examples

Or try the command-line interface:

```bash
nanonets-extractor --help
``` 