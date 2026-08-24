from pathlib import Path

from app.services.llm_extraction import extract_medical_fields_from_pdf


pdf_path = Path("test_report.pdf")

result = extract_medical_fields_from_pdf(
    file_bytes=pdf_path.read_bytes(),
    file_name=pdf_path.name,
)

print("\nEXTRACTION RESULT")
print("=================")

for field in result.fields:
    print(field.model_dump())