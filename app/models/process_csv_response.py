from pydantic import BaseModel
from typing import List, Optional, Literal

from app.models.csv_row import CSVRowSchema


class ErrorRowSchema(BaseModel):
    row_number: int
    error: str
    row_data: CSVRowSchema

class ProcessCSVResponseSchema(BaseModel):
    status: str = Literal['success', 'failed', 'partial_success']
    processed_rows: int
    errors: List[ErrorRowSchema]
    message: Optional[str] = None
