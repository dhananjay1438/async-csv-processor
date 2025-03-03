from pydantic import BaseModel, HttpUrl, Field
from typing import List


class CSVRowSchema(BaseModel):

    serial_number: int
    product_name: str
    image_urls: List[HttpUrl]
