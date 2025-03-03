from celery import Celery
from app.config import REDIS_PASSWORD, REDIS_DB, REDIS_PORT, REDIS_HOST

if REDIS_PASSWORD:
    REDIS_URL = f'redis://{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

else:
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

celery_app = Celery(
    "background_csv_image_processor",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['app.services.csv_handler']
)

celery_app.conf.update(task_track_started=True)
