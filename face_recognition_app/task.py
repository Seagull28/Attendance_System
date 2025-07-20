from celery import shared_task
from datetime import datetime, timedelta

@shared_task
def scan_classroom():
    # Initialize face recognition view and perform scan
    face_recognition_view = FaceRecognitionView()
    face_recognition_view.post(None)