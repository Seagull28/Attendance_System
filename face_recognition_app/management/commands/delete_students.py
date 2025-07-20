from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from face_recognition_app.models import Student
from django.db import transaction

class Command(BaseCommand):
    help = 'Delete students with roll numbers in specified range'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Delete regular students (001-062)
                for i in range(1, 63):
                    roll_number = f'2451-23-748-{i:03d}'
                    student = Student.objects.filter(roll_number=roll_number).first()
                    if student:
                        user = student.user
                        student.delete()
                        user.delete()
                        self.stdout.write(f'Deleted student with roll number {roll_number}')

                # Delete lateral students (301-310)
                for i in range(301, 311):
                    roll_number = f'2451-23-748-{i}'
                    student = Student.objects.filter(roll_number=roll_number).first()
                    if student:
                        user = student.user
                        student.delete()
                        user.delete()
                        self.stdout.write(f'Deleted student with roll number {roll_number}')

            self.stdout.write(self.style.SUCCESS('Successfully deleted all specified students'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))