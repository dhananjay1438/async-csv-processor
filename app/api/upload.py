import uuid
from typing import Dict

from fastapi import APIRouter, UploadFile, File
from app.models.requests import UploadResponse
from app.redis import update_task_status, get_task_status
from app.services.csv_handler import process_csv

router = APIRouter()


@router.post("/", summary="Use to upload CSV file to process it",
             description="Adds the request to upload CSV file and get the compressed images back",
             response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)) -> UploadResponse:

    file_content: bytes = await file.read()
    decoded_content: str = file_content.decode('utf-8')
    request_id = str(uuid.uuid4())
    update_task_status(request_id, 'status', "started")

    process_csv.apply_async(args=[decoded_content, request_id])
    return UploadResponse(request_id=request_id)


@router.get('/status/{request_id}')
async def get_status(request_id: str) -> Dict:
    return get_task_status(request_id)
