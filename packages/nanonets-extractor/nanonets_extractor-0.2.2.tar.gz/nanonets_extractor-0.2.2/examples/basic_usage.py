"""
Basic usage example for Nanonets Document Extractor.
"""

from nanonets_extractor import DocumentExtractor


def main():
    """Demonstrate basic usage of the document extractor."""
    
    # Example 1: Free tier usage (with rate limits)
    print("=== Free Tier Usage ===")
    try:
        # Initialize extractor (free tier)
        extractor = DocumentExtractor()
        
        # Extract data from a document
        result = extractor.extract(
            file_path="sample_invoice.pdf",  # Replace with actual file path
            output_type="flat-json"
        )
        
        print("Free tier extraction result:")
        print(result)
        
    except Exception as e:
        print(f"Free tier extraction failed: {e}")
        if "Rate limit exceeded" in str(e):
            print("💡 Tip: Get unlimited access with a free API key!")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Unlimited access with API key
    print("=== Unlimited Access with API Key ===")
    try:
        # Initialize with API key for unlimited access
        # Get your free API key from: https://app.nanonets.com/#/keys
        extractor = DocumentExtractor(api_key="your_api_key_here")  # Replace with actual API key
        
        # Extract data from a document
        result = extractor.extract(
            file_path="sample_document.pdf",  # Replace with actual file path
            output_type="html"
        )
        
        print("Unlimited access result:")
        print(result)
        
    except Exception as e:
        print(f"API key extraction failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Auto-detected fields
    print("=== Auto-detected Fields ===")
    try:
        extractor = DocumentExtractor()
        
        result = extractor.extract(
            file_path="sample_document.pdf",  # Replace with actual file path
            output_type="fields"
        )
        
        print("Auto-detected fields:")
        print(result)
        
    except Exception as e:
        print(f"Fields extraction failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 4: Table extraction
    print("=== Table Extraction ===")
    try:
        extractor = DocumentExtractor()
        
        result = extractor.extract(
            file_path="sample_document.pdf",  # Replace with actual file path
            output_type="tables"
        )
        
        print("Table data:")
        print(result)
        
    except Exception as e:
        print(f"Table extraction failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 5: Extract specific fields
    print("=== Extract Specific Fields ===")
    try:
        extractor = DocumentExtractor()
        
        result = extractor.extract(
            file_path="invoice.pdf",  # Replace with actual file path
            output_type="specified-fields",
            specified_fields=["invoice_number", "total_amount", "date"]
        )
        
        print("Specific fields extraction:")
        print(result)
        
    except Exception as e:
        print(f"Specific fields extraction failed: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 6: Batch processing
    print("=== Batch Processing ===")
    try:
        extractor = DocumentExtractor()
        
        files = ["invoice1.pdf", "invoice2.pdf", "receipt1.jpg"]  # Replace with actual files
        results = extractor.extract_batch(
            file_paths=files,
            output_type="flat-json"
        )
        
        print("Batch processing results:")
        for file_path, result in results.items():
            print(f"\n{file_path}:")
            print(result)
        
    except Exception as e:
        print(f"Batch processing failed: {e}")


if __name__ == "__main__":
    main() 