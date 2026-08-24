import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

print("API key loaded:", bool(api_key))
print("Model:", model)

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set")

pdf_path = Path("test_report.pdf")

if not pdf_path.exists():
    raise FileNotFoundError(f"PDF not found: {pdf_path}")

pdf_bytes = pdf_path.read_bytes()

print("PDF size:", len(pdf_bytes), "bytes")

client = genai.Client(api_key=api_key)

# Upload PDF
uploaded_file = client.files.upload(
    file=pdf_path,
)

print("PDF uploaded successfully")
print("File name:", uploaded_file.name)

prompt = """
You are a medical report data extraction engine.

Read the uploaded PDF and extract every discrete test result,
measurement, or vital sign explicitly present in the document.

For each result, return:

- fieldName
- fieldValue
- unit
- referenceRange
- isAbnormal
- displayOrder

Rules:
1. Only extract information explicitly present in the PDF.
2. Never invent or calculate values.
3. If unit is not present, return null.
4. If reference range is not present, return null.
5. If the report explicitly marks a result as high, low, abnormal,
   etc., set isAbnormal accordingly.
6. Otherwise set isAbnormal to null.
7. displayOrder should follow the order in which results appear.
8. Extract results from all pages.
"""

response = client.models.generate_content(
    model=model,
    contents=[
        uploaded_file,
        prompt,
    ],
)

print("\nGEMINI RESPONSE")
print("================")
print(response.text)