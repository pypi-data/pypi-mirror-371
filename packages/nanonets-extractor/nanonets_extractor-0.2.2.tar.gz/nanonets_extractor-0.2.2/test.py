from nanonets_extractor import DocumentExtractor

# Initialize with cloud processing (requires API key)
extractor = DocumentExtractor()

# Extract data from a document
result = extractor.extract(
    file_path="1.png",
    output_type="flat-json"
)

print("================ flat-json ================")
print(result)


result = extractor.extract(
    file_path="1.png",
    output_type="specified-fields",
    specified_fields=[
        "name",
        "address",
        "phone",
        "email",
        "website", 
        "total experience"
    ]
)

print("================ specified-fields ================")
print(result)


result = extractor.extract(
    file_path="1.png",
    output_type="specified-json",
    specified_json={
        "name": "string",
        "years of experience": [{
            "company": "string",
            "years": "number"
        }]
    }
)

print("================ specified-json ================")
print(result)