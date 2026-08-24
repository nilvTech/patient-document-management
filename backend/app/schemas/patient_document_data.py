from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExtractedMedicalField(BaseModel):
    """Structured-output contract the LLM must fill in for each field found."""
    fieldName: str = Field(min_length=1, max_length=250)
    fieldValue: Optional[str] = None
    unit: Optional[str] = Field(default=None, max_length=100)
    referenceRange: Optional[str] = Field(default=None, max_length=200)
    isAbnormal: Optional[bool] = None
    displayOrder: Optional[int] = None


class ExtractedMedicalFields(BaseModel):
    fields: list[ExtractedMedicalField]


class PatientDocumentDataResponse(BaseModel):
    """What the API returns to the frontend for persisted, validated rows."""
    patient_document_data_id: int
    patient_document_id: int
    field_name: str
    field_value: Optional[str]
    unit: Optional[str]
    reference_range: Optional[str]
    is_abnormal: Optional[bool]
    display_order: Optional[int]

    model_config = ConfigDict(from_attributes=True)