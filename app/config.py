import os
from dotenv import load_dotenv

load_dotenv()

environment = os.getenv('ENVIRONMENT')
env_file = '.env.local' if environment == 'local' else '.env.docker'

load_dotenv(env_file)

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_DB = os.getenv('REDIS_DB', 0)
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', "")


FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS')

FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')

WEBHOOK_URL = os.getenv('WEBHOOK_URL')

