import redis
from redis import Redis
from typing import Dict

from app.config import REDIS_PASSWORD, REDIS_DB, REDIS_PORT, REDIS_HOST

redis_client: Redis = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def update_task_status(request_id: str, key, value: str) -> None:
    redis_client.hset(request_id, key, value)

def get_task_status(request_id: str) -> Dict:

    status = redis_client.hget(request_id, "status") or ""
    csv_url = redis_client.hget(request_id, 'csv_url') or ""

    return {
        'request_id': request_id,
        'status': status,
        'csv_url': csv_url
    }

def delete_task_status(request_id: str) -> None:
    redis_client.delete(request_id)



