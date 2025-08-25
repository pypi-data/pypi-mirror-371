"""
Batch processing example for Nanonets Document Extractor.
"""

import os
import json
from pathlib import Path
from nanonets_extractor import DocumentExtractor


def process_directory(directory_path: str, output_dir: str = "extracted_data"):
    """
    Process all documents in a directory.
    
    Args:
        directory_path: Path to directory containing documents
        output_dir: Directory to save extraction results
    """
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Initialize extractor
    extractor = DocumentExtractor()
    
    # Supported file extensions
    supported_extensions = extractor.get_supported_formats()
    
    # Find all supported files
    files_to_process = []
    for ext in supported_extensions:
        pattern = f"*{ext}"
        files_to_process.extend(Path(directory_path).glob(pattern))
    
    if not files_to_process:
        print(f"No supported files found in {directory_path}")
        return
    
    print(f"Found {len(files_to_process)} files to process")
    
    # Process files in batches
    batch_size = 10
    for i in range(0, len(files_to_process), batch_size):
        batch = files_to_process[i:i+batch_size]
        batch_paths = [str(f) for f in batch]
        
        print(f"Processing batch {i//batch_size + 1}...")
        
        try:
            # Extract data from batch
            results = extractor.extract_batch(
                file_paths=batch_paths,
                output_type="flat-json"
            )
            
            # Save results
            for file_path, result in results.items():
                filename = Path(file_path).stem
                output_file = Path(output_dir) / f"{filename}_extracted.json"
                
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                
                if "error" in result:
                    print(f"  ❌ {filename}: {result['error']}")
                else:
                    print(f"  ✅ {filename}: Extracted successfully")
                    
        except Exception as e:
            print(f"  ❌ Batch processing failed: {e}")


def process_different_output_types():
    """Demonstrate different output types."""
    extractor = DocumentExtractor()
    
    # Sample file (replace with actual file)
    sample_file = "sample_invoice.pdf"
    
    if not os.path.exists(sample_file):
        print(f"Sample file {sample_file} not found. Please provide a valid file.")
        return
    
    print("=== Different Output Types ===")
    
    # 1. Auto-detected fields
    print("\n1. Auto-detected fields:")
    try:
        result = extractor.extract(sample_file, output_type="fields")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    # 2. Markdown output
    print("\n2. Markdown output:")
    try:
        result = extractor.extract(sample_file, output_type="markdown")
        print(result.get("markdown", "No markdown content"))
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. HTML output
    print("\n3. HTML output:")
    try:
        result = extractor.extract(sample_file, output_type="html")
        print(result.get("html", "No HTML content"))
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. Table extraction
    print("\n4. Table extraction:")
    try:
        result = extractor.extract(sample_file, output_type="tables")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    # 5. CSV format
    print("\n5. CSV format:")
    try:
        result = extractor.extract(sample_file, output_type="csv")
        print(result.get("csv", "No CSV content"))
    except Exception as e:
        print(f"Error: {e}")
    
    # 6. Specified fields
    print("\n6. Specified fields:")
    try:
        result = extractor.extract(
            sample_file, 
            output_type="specified-fields",
            specified_fields=["invoice_number", "total", "date"]
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main function demonstrating batch processing."""
    
    # Example 1: Process a directory
    print("=== Batch Processing Example ===")
    process_directory("./sample_documents", "./results")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Different output types
    process_different_output_types()
    
    # Example 3: Manual file list processing
    print("\n=== Manual File List Processing ===")
    
    extractor = DocumentExtractor()
    
    # List of files to process
    files = [
        "invoice1.pdf",
        "receipt1.jpg", 
        "contract1.docx"
    ]
    
    # Filter existing files
    existing_files = [f for f in files if os.path.exists(f)]
    
    if existing_files:
        try:
            results = extractor.extract_batch(
                file_paths=existing_files,
                output_type="flat-json"
            )
            
            print("Processing results:")
            for file_path, result in results.items():
                print(f"\n{file_path}:")
                if "error" in result:
                    print(f"  Error: {result['error']}")
                else:
                    print(f"  Success: {len(result)} fields extracted")
                    
        except Exception as e:
            print(f"Batch processing failed: {e}")
    else:
        print("No files found to process. Please provide valid file paths.")


if __name__ == "__main__":
    main() 