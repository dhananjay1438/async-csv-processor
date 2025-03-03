from app.api import upload
from fastapi import FastAPI

from app.api import webhook

app = FastAPI(title='CSV image processing API', version='1.0')

app.include_router(router=upload.router, prefix='/upload')
app.include_router(router=webhook.router, prefix='/webhook')

@app.get('/', summary="root api call", description="Home API call, returns hello world")
async def root():
    return {"message": "hello world"}
