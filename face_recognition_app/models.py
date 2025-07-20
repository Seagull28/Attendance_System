from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Section(models.Model):
    name = models.CharField(max_length=1)  # A, B, etc.
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    capacity = models.IntegerField(default=60)
    year = models.IntegerField()

    class Meta:
        unique_together = ['department', 'name', 'year']

    def __str__(self):
        return f"{self.department.code} - Year {self.year} - Section {self.name}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)  # Add this line
    roll_number = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year = models.IntegerField()
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    face_encoding = models.BinaryField(null=True, blank=True)

    def get_section_from_roll(self):
        # Extract the student number from roll number (last 3 digits)
        student_number = int(self.roll_number.split('-')[-1])
        
        # Determine section based on roll number range
        if 1 <= student_number <= 62:  # Regular students - Section A
            return 'A'
        elif 63 <= student_number <= 124:  # Regular students - Section B
            return 'B'
        elif 301 <= student_number <= 310:  # Lateral students - Section A
            return 'A'
        elif 311 <= student_number <= 320:  # Lateral students - Section B
            return 'B'
        return 'A'  # Default section if number doesn't match any range

    def parse_roll_number(self):
        # Format: 2451-23-748-310
        parts = self.roll_number.split('-')
        if len(parts) == 4:
            return {
                'college_code': parts[0],
                'year': '20' + parts[1],  # Convert 23 to 2023
                'branch_code': parts[2],
                'student_id': parts[3]
            }
        return None

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            roll_info = self.parse_roll_number()
            if roll_info:
                self.year = int(roll_info['year'])
                # Map branch code to department
                branch_mapping = {
                    '748': '102',
                    # Add more branch codes as needed
                }
                branch_name_mapping = {
                    '748': 'CSE-AIML',
                }
                # Instead of setting department directly, get or create Department
                dept_code = branch_mapping.get(roll_info['branch_code'], 0)
                dept_name = branch_name_mapping.get(roll_info['branch_code'], 'Unknown')

                department, _ = Department.objects.get_or_create(
                    code=dept_code,
                    defaults={'name': dept_name}
                )
                self.department = department

                # Get or create Section
                section_name = self.get_section_from_roll()
                section, _ = Section.objects.get_or_create(
                    department=department,
                    name=section_name,
                    year=self.year,
                    defaults={'capacity': 60}
                )
                self.section = section

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.roll_number} (Section {self.section})"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year = models.IntegerField()
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    present = models.BooleanField(default=False)

    class Meta:
        unique_together = ['student', 'subject', 'date']

class TimeTable(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ['subject', 'day_of_week', 'start_time']

class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    total_classes = models.IntegerField(default=0)
    classes_attended = models.IntegerField(default=0)
    month = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        unique_together = ['student', 'subject', 'total_classes']
