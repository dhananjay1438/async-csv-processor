from fastapi import APIRouter, Request

router = APIRouter()

@router.post('/')
async def webhook_handler(request: Request):
    data = await request.json()
    print("We have received the webhook callback")
    print(data)
