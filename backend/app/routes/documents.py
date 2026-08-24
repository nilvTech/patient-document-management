from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.models.patient_document_data import PatientDocumentData
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.schemas.patient_document_data import PatientDocumentDataResponse
from app.services.llm_extraction import ExtractionError, extract_medical_fields_from_pdf
from app.services.validation import validate_and_normalize

from pathlib import Path

router = APIRouter(
    prefix="/patient",
    tags=["Patient Documents"],
)

# ALLOWED_CONTENT_TYPES = {"application/pdf"}
# ALLOWED_EXTENSIONS = {".pdf"}
ALLOWED_CONTENT_TYPES = {
    # PDF
    "application/pdf",
    # Microsoft Word
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    # Microsoft Excel
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    # Microsoft PowerPoint
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    # Images
    "image/jpeg",
    "image/png",
    "image/webp",
    # Text / data
    "text/plain",
    "text/csv",
    "text/html",
    "text/xml",
    "application/xml",
    "application/json",
    "application/rtf",
    "text/rtf",
}

ALLOWED_EXTENSIONS = {
    # PDF
    ".pdf",
    # Word
    ".doc",
    ".docx",
    # Excel
    ".xls",
    ".xlsx",
    # PowerPoint
    ".ppt",
    ".pptx",
    # Images
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    # Text / data
    ".txt",
    ".csv",
    ".html",
    ".htm",
    ".xml",
    ".json",
    ".rtf",
}


# def _is_allowed_file(filename: str, content_type: str | None) -> bool:
#     ext_ok = any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
#     # Some browsers send generic "application/octet-stream" for PDFs, so we
#     # accept the file if EITHER the content-type OR the extension checks out,
#     # rather than requiring both — but always require the extension.
#     type_ok = content_type in ALLOWED_CONTENT_TYPES or content_type in (
#         None,
#         "application/octet-stream",
#     )
#     return ext_ok and type_ok
def _is_allowed_file(
    filename: str,
    content_type: str | None,
) -> bool:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return False

    if content_type in ALLOWED_CONTENT_TYPES:
        return True

    if content_type in (
        None,
        "",
        "application/octet-stream",
    ):
        return True

    return False


def _run_extraction_pipeline(document: Document, db: Session) -> None:
    """Synchronous: extract -> validate -> persist -> update status."""
    document.extraction_status = "processing"
    db.commit()

    try:
        raw_extraction = extract_medical_fields_from_pdf(
            document.file_data, document.file_name
        )
    except ExtractionError as exc:
        document.extraction_status = "failed"
        document.extraction_error = str(exc)
        db.commit()
        return

    result = validate_and_normalize(raw_extraction)

    for f in result.valid_fields:
        db.add(
            PatientDocumentData(
                patient_document_id=document.id,
                field_name=f.fieldName,
                field_value=f.fieldValue,
                unit=f.unit,
                reference_range=f.referenceRange,
                is_abnormal=f.isAbnormal,
                display_order=f.displayOrder,
            )
        )

    document.extraction_status = "completed"
    document.extraction_error = "; ".join(result.warnings) if result.warnings else None
    db.commit()


@router.post(
    "/{patient_id}/documents",
    response_model=list[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_documents(
    patient_id: int,
    files: Annotated[
        list[UploadFile], File(description="Select one or more PDF documents")
    ],
    db: Session = Depends(get_db),
):
    patient = (
        db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    )
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    # Reject the whole batch up front if any file isn't a PDF, so the
    # frontend can show one clear message rather than partial success.
    invalid_names = [
        f.filename
        for f in files
        if not _is_allowed_file(f.filename or "", f.content_type)
    ]
    if invalid_names:
        raise HTTPException(
            status_code=400,
            # detail=(
            #     "Unsupported file format for: "
            #     f"{', '.join(invalid_names)}. Please upload a valid file format (PDF only)."
            # ),
            detail=(
                "Unsupported file format for: "
                f"{', '.join(invalid_names)}. "
                "Please upload a supported document format."
            ),
        )

    uploaded_documents: list[Document] = []

    for file in files:
        file_data = await file.read()
        if not file_data:
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' is empty",
            )

        document = Document(
            patient_id=patient_id,
            file_name=file.filename or "unknown",
            file_type=file.content_type or "application/pdf",
            file_size=len(file_data),
            file_data=file_data,
            extraction_status="pending",
        )
        db.add(document)
        uploaded_documents.append(document)

    db.commit()
    for document in uploaded_documents:
        db.refresh(document)

    # Synchronous extraction, one document at a time.
    for document in uploaded_documents:
        _run_extraction_pipeline(document, db)
        db.refresh(document)

    return uploaded_documents


@router.get("/{patient_id}/documents", response_model=list[DocumentResponse])
def get_patient_documents(patient_id: int, db: Session = Depends(get_db)):
    patient = (
        db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    )
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    documents = (
        db.query(Document)
        .filter(Document.patient_id == patient_id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )
    return documents


@router.get("/{patient_id}/documents/{document_id}/file")
def get_document_file(patient_id: int, document_id: int, db: Session = Depends(get_db)):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.patient_id == patient_id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return Response(
        content=document.file_data,
        media_type=document.file_type,
        headers={"Content-Disposition": f'inline; filename="{document.file_name}"'},
    )


@router.get(
    "/{patient_id}/documents/{document_id}/extracted-data",
    response_model=list[PatientDocumentDataResponse],
)
def get_extracted_data(
    patient_id: int, document_id: int, db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.patient_id == patient_id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    data = (
        db.query(PatientDocumentData)
        .filter(PatientDocumentData.patient_document_id == document_id)
        .order_by(PatientDocumentData.display_order.asc().nulls_last())
        .all()
    )
    return data


# from typing import Annotated

# from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

# from fastapi.responses import Response

# from sqlalchemy.orm import Session

# from app.database import get_db
# from app.models.document import Document
# from app.models.user import User
# from app.schemas.document import DocumentResponse

# router = APIRouter(
#     prefix="/patient",
#     tags=["Patient Documents"],
# )


# # Upload document endpoint
# @router.post(
#     "/{patient_id}/documents",
#     response_model=list[DocumentResponse],
#     status_code=status.HTTP_201_CREATED,
# )
# async def upload_documents(
#     patient_id: int,
#     files: Annotated[
#         list[UploadFile],
#         File(description="Select one or more documents"),
#     ],
#     db: Session = Depends(get_db),
# ):
#     # Check whether patient exists
#     patient = (
#         db.query(User)
#         .filter(
#             User.id == patient_id,
#             User.role == "patient",
#         )
#         .first()
#     )

#     if not patient:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Patient not found",
#         )

#     if not files:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="No files provided",
#         )

#     uploaded_documents = []

#     for file in files:
#         file_data = await file.read()

#         if not file_data:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"File '{file.filename}' is empty",
#             )

#         document = Document(
#             patient_id=patient_id,
#             file_name=file.filename or "unknown",
#             file_type=file.content_type or "application/octet-stream",
#             file_size=len(file_data),
#             file_data=file_data,
#         )

#         db.add(document)
#         uploaded_documents.append(document)

#     db.commit()

#     for document in uploaded_documents:
#         db.refresh(document)

#     return uploaded_documents


# # Get All documents
# @router.get("/{patient_id}/documents", response_model=list[DocumentResponse])
# def get_patient_documents(patient_id: int, db: Session = Depends(get_db)):
#     # Check wheather patient exists
#     patient = (
#         db.query(User).filter(User.id == patient_id, User.role == "patient").first()
#     )

#     if not patient:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
#         )

#     documents = (
#         db.query(Document)
#         .filter(Document.patient_id == patient_id)
#         .order_by(Document.uploaded_at.desc())
#         .all()
#     )
#     return documents


# # get documents as View/Download
# @router.get("/{patient_id}/documents/{document_id}/file")
# def get_document_file(patient_id: int, document_id: int, db: Session = Depends(get_db)):
#     document = (
#         db.query(Document)
#         .filter(Document.id == document_id, Document.patient_id == patient_id)
#         .first()
#     )

#     if not document:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
#         )

#     return Response(
#         content=document.file_data,
#         media_type=document.file_type,
#         headers={"Content-Disposition": f'inline; filename="{document.file_name}"'},
#     )
