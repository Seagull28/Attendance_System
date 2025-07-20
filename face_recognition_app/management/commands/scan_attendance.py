from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import IntegrityError
import face_recognition
import cv2
import numpy as np
import os
from datetime import timedelta,datetime
from face_recognition_app.models import Student, Subject, TimeTable, Attendance, AttendanceReport

class Command(BaseCommand):
    help = 'Scan faces and mark attendance'

    def handle(self, *args, **options):
        now = timezone.localtime()
        weekday =  now.weekday()+1  
        self.stdout.write(f"🔕 Today is {now.strftime('%A')}, current time: {now.strftime('%H:%M:%S')}")

        classes_today = TimeTable.objects.filter(day_of_week=weekday)
        if not classes_today:
            self.stdout.write("⚠️ No classes found for today in TimeTable.")
            return

        self.stdout.write(f"📘 Found {classes_today.count()} class(es) scheduled for today.")

        class_found = False
        for entry in classes_today:
            start_window = timezone.make_aware(datetime.combine(now.date(), entry.start_time))
            end_window = start_window + timedelta(minutes=10)

            self.stdout.write(f"🔍 Checking class {entry.subject.code} - {entry.subject.name} from {entry.start_time} to {entry.end_time}")

            if start_window <= now <= end_window:
                class_found = True
                self.capture_attendance(entry.subject)
                break

        if not class_found:
            self.stdout.write("⛔ No class scheduled within the 10-minute window for attendance.")

    def capture_attendance(self, subject):
        self.stdout.write("📷 Starting webcam to capture frames...")

        known_encodings = []
        known_students = []

        for student in Student.objects.all():
            if student.face_encoding:
                known_encodings.append(np.frombuffer(student.face_encoding))
                known_students.append(student)

        cap = cv2.VideoCapture(0)
        marked_students = set()
        start_time = timezone.now()

        while (timezone.now() - start_time).seconds < 60:
            ret, frame = cap.read()
            if not ret:
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame,model='hog')
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                """matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
                if True in matches:
                    match_index = matches.index(True)
                    student = known_students[match_index]
                    if student not in marked_students:
                        self.mark_attendance(student, subject)
                        marked_students.add(student)
                        top, right, bottom, left = face_location
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.putText(frame, student.roll_number, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)"""
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                if face_distances[best_match_index] < 0.45:  # Adjust threshold if needed
                    student = known_students[best_match_index]
                    if student not in marked_students:
                        self.mark_attendance(student, subject)
                        marked_students.add(student)
                        top, right, bottom, left = face_location
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.putText(frame, student.roll_number, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                else:
                     # Optional: draw box for unknown face
                    top, right, bottom, left = face_location
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(frame, "Unknown", (left, top - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imshow('Attendance Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        self.mark_absentees(subject, marked_students)

    def mark_attendance(self, student, subject):
        today = timezone.localdate()
        now = timezone.localtime().time()

        _, created = Attendance.objects.get_or_create(
            student=student,
            subject=subject,
            date=today,
            defaults={
                'time': now,
                'present': True
            }
        )

        if created:
            self.stdout.write(f"✅ Marked Present: {student.roll_number} for {subject.code}")
        else:
            self.stdout.write(f"ℹ️ Already marked: {student.roll_number} for {subject.code}")

        self.update_attendance_report(student, subject)

    def mark_absentees(self, subject, present_students):
        today = timezone.localdate()
        all_students = Student.objects.all()

        for student in all_students:
            # Only mark if attendance does not exist yet
            if not Attendance.objects.filter(student=student, subject=subject, date=today).exists():
                Attendance.objects.create(
                    student=student,
                    subject=subject,
                    date=today,
                    time=timezone.localtime().time(),
                    present=False
                )
                self.stdout.write(f"❌ Marked Absent: {student.roll_number} for {subject.code}")

            self.update_attendance_report(student, subject)

    def update_attendance_report(self, student, subject):
        today = timezone.localdate()
        month = today.month
        year = today.year

        report, _ = AttendanceReport.objects.get_or_create(
            student=student,
            subject=subject,
            month=month,
            year=year,
            defaults={
                'total_classes': 0,
                'classes_attended': 0,
            }
        )

        total = Attendance.objects.filter(student=student, subject=subject, date__month=month, date__year=year).count()
        attended = Attendance.objects.filter(student=student, subject=subject, date__month=month,
                                             date__year=year, present=True).count()

        report.total_classes = total
        report.classes_attended = attended
        report.save()
        
        self.stdout.write(f"📊 Updated report: {student.roll_number} | {subject.code} | {report.classes_attended}/{report.total_classes}")
