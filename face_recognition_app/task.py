from celery import shared_task
from datetime import datetime, timedelta
from face_recognition_app.views import FaceRecognitionView

@shared_task
def scan_classroom():
    face_recognition_view = FaceRecognitionView()
    face_recognition_view.post(None)
