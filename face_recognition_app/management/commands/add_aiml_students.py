from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from face_recognition_app.models import Student, Department, Section
from django.db import transaction

class Command(BaseCommand):
    help = 'Add students to department with code 102 (CSE-AIML)'

    def handle(self, *args, **options):
        try:
            # Fetch department by code only
            try:
                department = Department.objects.get(code=102)
            except Department.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    "❌ Department with code 102 does not exist. Please create it first."
                ))
                return

            # Fetch section A for Year 1
            try:
                section_a = Section.objects.get(
                    name='A',
                    department=department,
                    year=2023
                )
            except Section.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    "❌ Section 'A' for Year 2023 in the specified department does not exist. Please create it first."
                ))
                return

            self.stdout.write(self.style.SUCCESS(
                f"✅ Using department: code={department.code}, name={department.name}"
            ))
            self.stdout.write(self.style.SUCCESS(
                f"✅ Using section: name={section_a.name}, year={section_a.year}"
            ))

            # Add regular students (001-062)
            for i in range(1, 63):
                roll_number = f'2451-23-748-{i:03d}'
                username = roll_number.lower()
                with transaction.atomic():
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': f'{username}@example.com',
                        }
                    )
                    if created:
                        user.set_password('defaultpassword')
                        user.save()
                    if not Student.objects.filter(roll_number=roll_number).exists():
                        Student.objects.create(
                            user=user,
                            roll_number=roll_number,
                            department=department,
                            year=2023,
                            section=section_a
                        )

            # Add lateral students (301-310)
            for i in range(301, 311):
                roll_number = f'2451-23-748-{i}'
                username = roll_number.lower()
                with transaction.atomic():
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': f'{username}@example.com',
                        }
                    )
                    if created:
                        user.set_password('defaultpassword')
                        user.save()
                    if not Student.objects.filter(roll_number=roll_number).exists():
                        Student.objects.create(
                            user=user,
                            roll_number=roll_number,
                            department=department,
                            year=2023,
                            section=section_a
                        )

            self.stdout.write(self.style.SUCCESS('🎉 Successfully added all students.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
