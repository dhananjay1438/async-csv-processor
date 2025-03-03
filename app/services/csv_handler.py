import asyncio
import csv
import os
import uuid
from http.client import responses
from os import write
from unicodedata import lookup

from PIL import Image
import requests
import io
from celery.utils.log import get_task_logger
from typing import List, Dict, Any

from msgpack.fallback import BytesIO

from app.config import WEBHOOK_URL
from app.firebase_config import bucket, db
from app.models.process_csv_response import ErrorRowSchema
from app.redis import update_task_status
from app.workers.celery_worker import celery_app

logger = get_task_logger(__name__)


@celery_app.task()
def process_csv(file_content: str, request_id: str) -> None:
    try:
        csv_file = io.StringIO(file_content)
        reader = csv.DictReader(csv_file)
        validated_rows: List = []
        error_rows: List[ErrorRowSchema] = []

        seen_serial_numbers = set()
        for i, row in enumerate(reader, start=1):
            validated_row = {
                'serial_number': row['Serial Number'],
                'product_name': row['Product Name'],
                'image_urls': [url.strip() for url in row['Input Image Urls'].split(',')]
            }

            if validated_row.get('serial_number') in seen_serial_numbers:
                error_rows.append(ErrorRowSchema(
                    row_number=i,
                    error='Duplicate serial number',
                    row_data=row
                ))
                logger.warning(f'Duplicate serial number found at row: {i}')
                continue

            validated_rows.append(validated_row)
            seen_serial_numbers.add(validated_row.get('serial_number'))

        # If all rows failed validation
        if not validated_rows:
            update_task_status(request_id, 'status', "failed")
            return

        update_task_status(request_id, 'status', "in progress")
        process_images.apply_async(args=[validated_rows, request_id])
    except Exception as e:
        logger.error(e)

        update_task_status(request_id, 'status', "failed")

@celery_app.task()
def process_images(validated_rows: List[dict], request_id: str) -> None:
    try:
        output_image_urls = []
        for row in validated_rows:
            product_name = row['product_name']
            output_urls = []
            input_urls = row['image_urls']
            for image_url in input_urls:
                try:
                    response = requests.get(image_url)
                    response.raise_for_status()
                    img = Image.open(BytesIO(response.content))

                    output_buffer = BytesIO()
                    img.save(output_buffer, format='JPEG', quality=50)
                    output_buffer.seek(0)

                    file_name = f'{uuid.uuid4()}.jpg'
                    blob = bucket.blob(f'/compressed_images/{file_name}')
                    blob.upload_from_file(output_buffer, content_type='image/jpeg')
                    blob.make_public()

                    output_url = blob.public_url
                    output_urls.append(output_url)

                    db.collection('processed-images').add({
                        'request_id': request_id,
                        'product_name': product_name,
                        'input_url': image_url,
                        'output_url': output_url
                    })

                except Exception as e:
                    logger.error(f'Error processing image for {product_name}: {e}')

                output_image_urls.append({
                    'serial_number': row['serial_number'],
                    'product_name': product_name,
                    'input_urls': ','.join(input_urls),
                    'output_urls': ','.join(output_urls)
                })

        loop = asyncio.get_event_loop()
        csv_url = loop.run_until_complete(generate_and_upload_csv(output_image_urls, request_id))

        update_task_status(request_id, 'status', 'completed')
        update_task_status(request_id, 'csv_url', csv_url)

        trigger_webhook(request_id, csv_url)

    except Exception as e:
        logger.error(f'Following error was caused while processing images: {e}')
        update_task_status(request_id, 'status', 'failed')


async def generate_and_upload_csv(data: List[dict], request_id: str) -> str:

    file_name = f'processed_results_{request_id}.csv'
    file_path = f'/tmp/{file_name}'

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Serial Number', 'Product Name', 'Input Image Urls', 'Output Image Urls'])

        for row in data:
            writer.writerow([row['serial_number'], row['product_name'], row['input_urls'], row['output_urls']])

    blob = bucket.blob(f'processed_csvs/{file_name}')
    await asyncio.to_thread(blob.upload_from_filename, file_path, content_type='text/csv')

    blob.make_public()

    os.remove(file_path)

    return blob.public_url


def trigger_webhook(request_id, csv_url):
    webhook_url = WEBHOOK_URL

    payload = {
        "request_id": request_id,
        "status": "completed",
        "csv_url": csv_url,
    }

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()

    except Exception as e:
        logger.error(f'Error when calling webhook url: {e}')



