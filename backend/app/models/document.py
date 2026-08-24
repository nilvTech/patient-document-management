# from datetime import datetime

# from sqlalchemy import DateTime, ForeignKey, LargeBinary, String
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.database import Base


# class Document(Base):
#     __tablename__ = "documents"

#     id: Mapped[int] = mapped_column(primary_key=True, index=True)

#     patient_id: Mapped[int] = mapped_column(
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     file_name: Mapped[str] = mapped_column( 
#         String(255),
#         nullable=False,
#     )

#     file_type: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#     )

#     file_size: Mapped[int] = mapped_column(
#         nullable=False,
#     )

#     file_data: Mapped[bytes] = mapped_column(
#         LargeBinary,
#         nullable=False,
#     )

#     uploaded_at: Mapped[datetime] = mapped_column(
#         DateTime,
#         default=datetime.utcnow,
#         nullable=False,
#     )

#     patient: Mapped["User"] = relationship(
#         back_populates="documents",
#     )

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)
    file_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Extraction pipeline state. "pending" is the pre-save default; because
    # extraction runs synchronously in this design it moves straight to
    # "processing" and then "completed"/"failed" within the same request.
    extraction_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    extraction_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    patient: Mapped["User"] = relationship(back_populates="documents")

    extracted_data: Mapped[list["PatientDocumentData"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )