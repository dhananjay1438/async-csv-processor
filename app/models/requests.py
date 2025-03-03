from pydantic import BaseModel


class UploadResponse(BaseModel):
    request_id: str
