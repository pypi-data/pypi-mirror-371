#!/usr/bin/env python3
"""
Command line interface for Nanonets Document Extractor.
"""

import sys
import os
import argparse
import json
import glob
from typing import List, Dict, Any

from .extractor import DocumentExtractor
from .exceptions import ExtractionError, UnsupportedFileError
from .utils import validate_output_type


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Extract data from documents using Nanonets Document Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic extraction with auto-detected fields (free tier)
  nanonets-extractor document.pdf --output-type fields

  # With API key for unlimited access
  nanonets-extractor document.pdf --api-key your_api_key --output-type fields

  # Get clean markdown formatting
  nanonets-extractor document.pdf --output-type markdown

  # Extract structured table data with API key
  nanonets-extractor document.pdf --api-key your_api_key --output-type tables

  # Extract specific fields
  nanonets-extractor invoice.pdf --output-type specified-fields --fields invoice_number,customer_name,total_amount

  # Save output to file
  nanonets-extractor document.pdf --output result.json

  # Batch processing
  nanonets-extractor *.pdf --output-dir results/
        """
    )
    
    # File input
    parser.add_argument(
        'files',
        nargs='+',
        help='Document files to process (supports glob patterns)'
    )
    
    # Model selection
    parser.add_argument(
        '--model',
        choices=['gemini', 'openai'],
        help='AI model to use for processing'
    )
    
    # API key (optional)
    parser.add_argument(
        '--api-key',
        help='API key for unlimited access (optional - uses free tier if not provided). Get yours from: https://app.nanonets.com/#/keys'
    )
    
    # Output type
    parser.add_argument(
        '--output-type',
        choices=['markdown', 'html', 'fields', 'tables', 'csv', 'flat-json', 'specified-fields', 'specified-json'],
        default='flat-json',
        help='Output format (default: flat-json)'
    )
    
    # Specified fields
    parser.add_argument(
        '--fields',
        help='Comma-separated list of fields to extract (for specified-fields output)'
    )
    
    # JSON schema
    parser.add_argument(
        '--schema',
        help='Path to JSON schema file (for specified-json output)'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: stdout)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for batch processing'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode'
    )
    
    return parser


def run_extraction(args):
    """Run the extraction based on command line arguments."""
    # Initialize extractor
    try:
        extractor = DocumentExtractor(
            api_key=args.api_key,
            model=args.model
        )
    except Exception as e:
        print(f"Initialization error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Parse specified fields
    specified_fields = None
    if args.fields:
        specified_fields = [field.strip() for field in args.fields.split(',')]
    
    # Load JSON schema
    json_schema = None
    if args.schema:
        try:
            with open(args.schema, 'r') as f:
                json_schema = json.load(f)
        except Exception as e:
            print(f"Error loading schema file: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Expand file patterns
    files = expand_file_patterns(args.files)
    
    if not files:
        print("No files found matching the specified patterns.", file=sys.stderr)
        sys.exit(1)
    
    # Process files
    if len(files) == 1:
        # Single file processing
        process_single_file(
            extractor, files[0], args.output_type, specified_fields, 
            json_schema, args.output, args.verbose, args.quiet
        )
    else:
        # Batch processing
        process_batch_files(
            extractor, files, args.output_type, specified_fields,
            json_schema, args.output_dir, args.verbose, args.quiet
        )


def expand_file_patterns(patterns: List[str]) -> List[str]:
    """Expand glob patterns to actual file paths."""
    files = []
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            files.extend(matches)
        else:
            # If no glob matches, treat as literal file path
            if os.path.exists(pattern):
                files.append(pattern)
    
    return files


def process_single_file(
    extractor: DocumentExtractor,
    file_path: str, 
    output_type: str,
    specified_fields: List[str],
    json_schema: Dict[str, Any],
    output_file: str,
    verbose: bool,
    quiet: bool
):
    """Process a single file."""
    try:
        if verbose and not quiet:
            print(f"Processing: {file_path}")
        
        result = extractor.extract(
            file_path=file_path,
            output_type=output_type,
            specified_fields=specified_fields,
            json_schema=json_schema
        )
        
        if output_file:
            with open(output_file, 'w') as f:
                if output_type in ["markdown", "html", "csv"]:
                    # For text-based outputs, save the content directly
                    content = result.get(output_type, "")
                    f.write(content)
                else:
                    # For JSON-based outputs
                    json.dump(result, f, indent=2)
            
            if not quiet:
                print(f"Results saved to: {output_file}")
        else:
            if output_type == "markdown":
                print(result.get("markdown", ""))
            elif output_type == "html":
                print(result.get("html", ""))
            elif output_type == "csv":
                print(result.get("csv", ""))
            else:
                print(json.dumps(result, indent=2))
                
    except (ExtractionError, UnsupportedFileError) as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error processing {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def process_batch_files(
    extractor: DocumentExtractor,
    file_paths: List[str],
    output_type: str,
    specified_fields: List[str],
    json_schema: Dict[str, Any],
    output_dir: str,
    verbose: bool,
    quiet: bool
):
    """Process multiple files."""
    if not quiet:
        print(f"Processing {len(file_paths)} files...")
    
    results = extractor.extract_batch(
        file_paths=file_paths,
        output_type=output_type,
        specified_fields=specified_fields,
        json_schema=json_schema
    )
    
    if output_dir:
        # Save individual files
        os.makedirs(output_dir, exist_ok=True)
        
        for file_path, result in results.items():
            filename = os.path.splitext(os.path.basename(file_path))[0]
            output_file = os.path.join(output_dir, f"{filename}_extracted.json")
            
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            if verbose and not quiet:
                if "error" in result:
                    print(f"  ❌ {filename}: {result['error']}")
                else:
                    print(f"  ✅ {filename}: Extracted successfully")
        
        if not quiet:
            print(f"Results saved to directory: {output_dir}")
    else:
        # Print all results
        print(json.dumps(results, indent=2))


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        run_extraction(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 