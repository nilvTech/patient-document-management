from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: int
    patient_id: int
    file_name: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    extraction_status: str
    extraction_error: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)










# from datetime import datetime

# from pydantic import BaseModel, ConfigDict

# class DocumentResponse(BaseModel):
#     id:int
#     patient_id:int
#     file_name:str
#     file_type:str
#     file_size:int
#     uploaded_at:datetime
    
#     model_config = ConfigDict(from_attributes=True)

    