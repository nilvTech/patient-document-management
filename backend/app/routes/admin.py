from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document, User
from app.schemas.document import DocumentResponse

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.get("/patients")
def get_patients(
    db: Session = Depends(get_db),
):
    patients = db.query(User).filter(User.role == "patient").all()

    return patients


@router.get(
    "/patient/{patient_id}/documents",
    response_model=list[DocumentResponse],
)
def get_patient_documents_for_admin(
    patient_id: int,
    db: Session = Depends(get_db),
):
    patient = (
        db.query(User)
        .filter(
            User.id == patient_id,
            User.role == "patient",
        )
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    documents = (
        db.query(Document)
        .filter(Document.patient_id == patient_id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    return documents