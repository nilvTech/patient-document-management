from sqlalchemy import Boolean, Integer, BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PatientDocumentData(Base):
    __tablename__ = "patient_document_data"

    patient_document_data_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    patient_document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    field_name: Mapped[str] = mapped_column(String(250), nullable=False)
    field_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reference_range: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_abnormal: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    display_order: Mapped[int | None] = mapped_column(Integer, nullable=True)

    document: Mapped["Document"] = relationship(back_populates="extracted_data")
