import firebase_admin
from firebase_admin import credentials, storage, firestore
from app.config import FIREBASE_CREDENTIALS, FIREBASE_STORAGE_BUCKET

cred = credentials.Certificate(FIREBASE_CREDENTIALS)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'storageBucket': FIREBASE_STORAGE_BUCKET
    })

db = firestore.client()

bucket = storage.bucket()
