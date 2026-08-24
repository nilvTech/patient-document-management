"""
Extract medical fields from a PDF using Google Gemini.

Gemini receives the PDF directly and returns structured data
validated against the existing ExtractedMedicalFields Pydantic model.
"""

import mimetypes

import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from app.schemas.patient_document_data import ExtractedMedicalFields
from app.services.canonical_fields import CANONICAL_FIELDS

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

        _client = genai.Client(api_key=api_key)

    return _client


class ExtractionError(Exception):
    """Raised when the LLM call fails or returns invalid data."""


def _build_prompt() -> str:
    canonical_list = "\n".join(f"- {name}" for name in CANONICAL_FIELDS)

    return f"""
You are a medical report data extraction engine.

You will be given a patient's laboratory or medical report as a PDF.

Extract every discrete test result, measurement, or vital sign that
is EXPLICITLY PRESENT in the document.

STRICT RULES:

1. Only extract values that literally appear in the document.
   Never invent, estimate, calculate, or infer a value.

2. For each field, map its name to the closest matching entry in
   this canonical field list, using medical knowledge of synonyms
   and abbreviations.

   Examples:
   Hb, HGB, Haemoglobin -> Hemoglobin

   Canonical field list:
{canonical_list}

   If a result genuinely does not correspond to any entry in the
   canonical list, extract it using the report's own label verbatim.

3. If a field's value, unit, or reference range is not present,
   set that property to null.

4. Set isAbnormal to true or false ONLY if the document explicitly
   indicates that the value is abnormal.

   Examples:
   - High/Low flags
   - H/L markers
   - Asterisks
   - Explicit abnormal indicators
   - Out-of-range styling

   If the document provides no such signal, set isAbnormal to null.

   Do NOT calculate abnormality yourself from the reference range.

5. displayOrder must reflect the order in which fields appear
   in the document, starting at 1.

6. Extract fields from every page and every table in the document.

7. If the document contains no extractable medical data,
   return an empty fields array.

Return the structured data according to the provided schema.
Do not include commentary.
"""


def extract_medical_fields_from_pdf(
    file_bytes: bytes,
    file_name: str,
) -> ExtractedMedicalFields:

    if not file_bytes:
        raise ExtractionError("The supplied PDF is empty.")

    client = _get_client()

    uploaded_file = None
    temp_pdf_path = None

    try:
        # ---------------------------------------------------------
        # 1. Write the incoming PDF bytes to a temporary file.
        # ---------------------------------------------------------
        suffix = Path(file_name).suffix or ".pdf"

        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_pdf_path = temp_file.name

        # ---------------------------------------------------------
        # 2. Upload the temporary PDF to Gemini.
        # ---------------------------------------------------------

        mime_type, _ = mimetypes.guess_type(temp_pdf_path)

        uploaded_file = client.files.upload(
            file=temp_pdf_path,
            config={
                "mime_type": mime_type or "application/octet-stream",
            },
        )

        # ---------------------------------------------------------
        # 3. Ask Gemini to extract structured medical data.
        # ---------------------------------------------------------
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                uploaded_file,
                _build_prompt(),
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": ExtractedMedicalFields,
            },
        )

    except Exception as exc:
        raise ExtractionError(f"Gemini extraction request failed: {exc}") from exc

    finally:
        # ---------------------------------------------------------
        # 4. Delete Gemini's uploaded file.
        # ---------------------------------------------------------
        if uploaded_file is not None:
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception:
                pass

        # ---------------------------------------------------------
        # 5. Delete our local temporary file.
        # ---------------------------------------------------------
        if temp_pdf_path is not None:
            try:
                os.unlink(temp_pdf_path)
            except Exception:
                pass

    # -------------------------------------------------------------
    # 6. Validate Gemini's structured response using Pydantic.
    # -------------------------------------------------------------
    try:
        if not response.text:
            raise ExtractionError("Gemini returned an empty response.")

        return ExtractedMedicalFields.model_validate_json(response.text)

    except Exception as exc:
        raise ExtractionError(
            f"Gemini returned invalid structured data: {exc}"
        ) from exc


# """
# Sends an uploaded PDF report directly to the OpenAI Responses API and gets
# back strictly-structured JSON (validated against ExtractedMedicalFields).

# Requires an OpenAI SDK version that supports:
#   - client.files.create(..., purpose="user_data")
#   - client.responses.parse(..., text_format=<pydantic model>)

# The currently pinned openai==3.3.1 has been verified locally to support both
# of these interfaces.
# """

# import os

# from dotenv import load_dotenv
# from openai import OpenAI

# from app.schemas.patient_document_data import ExtractedMedicalFields
# from app.services.canonical_fields import CANONICAL_FIELDS

# load_dotenv()

# OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

# _client: OpenAI | None = None


# def _get_client() -> OpenAI:
#     global _client
#     if _client is None:
#         _client = OpenAI()  # reads OPENAI_API_KEY from env
#     return _client


# class ExtractionError(Exception):
#     """Raised when the LLM call fails or returns something we can't trust."""


# def _build_prompt() -> str:
#     canonical_list = "\n".join(f"- {name}" for name in CANONICAL_FIELDS)

#     return f"""You are a medical report data extraction engine. You will be given a
# patient's lab/medical report as a PDF. Extract every discrete test result,
# measurement, or vital sign that is EXPLICITLY PRESENT in the document.

# STRICT RULES:
# 1. Only extract values that literally appear in the document. Never invent,
#    estimate, or infer a value that is not written in the report.
# 2. For each field, map its name to the closest matching entry in this
#    canonical field list, using your medical knowledge of synonyms and
#    abbreviations (e.g. "Hb", "HGB", "Haemoglobin" all map to "Hemoglobin"):
# {canonical_list}
#    If a result genuinely does not correspond to any entry in that list,
#    extract it anyway using the report's own label, verbatim.
# 3. If a field's value, unit, or reference range is not present in the
#    document, set it to null. Do not guess units or ranges.
# 4. Set isAbnormal to true/false only if the document explicitly marks the
#    value as high/low/abnormal (flags, asterisks, "H"/"L" markers, out-of-range
#    styling, or an explicit statement). If the document gives no such signal,
#    set isAbnormal to null — do not compute it yourself from the reference
#    range.
# 5. displayOrder should reflect the order fields appear in the document,
#    starting at 1.
# 6. If the document spans multiple pages or contains multiple tables, extract
#    fields from all of them.
# 7. If the document contains no extractable medical data at all, return an
#    empty fields array — do not fabricate placeholder entries.

# Return only the structured data. Do not include commentary."""


# def extract_medical_fields_from_pdf(
#     file_bytes: bytes,
#     file_name: str,
# ) -> ExtractedMedicalFields:
#     client = _get_client()

#     try:
#         uploaded_file = client.files.create(
#             file=(file_name, file_bytes, "application/pdf"),
#             purpose="user_data",
#         )
#     except Exception as exc:
#         raise ExtractionError(f"Failed to upload file to LLM provider: {exc}") from exc

#     try:
#         response = client.responses.parse(
#             model=OPENAI_MODEL,
#             input=[
#                 {
#                     "role": "user",
#                     "content": [
#                         {"type": "input_file", "file_id": uploaded_file.id},
#                         {"type": "input_text", "text": _build_prompt()},
#                     ],
#                 }
#             ],
#             text_format=ExtractedMedicalFields,
#         )
#     except Exception as exc:
#         raise ExtractionError(f"LLM extraction request failed: {exc}") from exc
#     finally:
#         try:
#             client.files.delete(uploaded_file.id)
#         except Exception:
#             pass  # best-effort cleanup; not fatal to the extraction itself

#     parsed = response.output_parsed
#     if parsed is None:
#         raise ExtractionError("LLM did not return a parseable structured response.")

#     return parsed
