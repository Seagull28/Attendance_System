import json
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from .models import Student, Attendance, AttendanceReport, Subject, TimeTable
import face_recognition
import numpy as np
import cv2
import base64
import io
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from face_recognition_app.models import Student, Attendance, Subject, AttendanceReport
from collections import defaultdict
import json
from datetime import timedelta
from reportlab.pdfgen import canvas
from collections import OrderedDict,defaultdict
from calendar import monthrange

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'student_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = Student.objects.get(user=self.request.user)
        subjects = Subject.objects.filter(department=student.department, year=student.year)

        attendance_data = []        
        for subject in subjects:
            total_classes = Attendance.objects.filter(subject=subject).values('date').distinct().count()
            attended_classes = Attendance.objects.filter(
                #student=student,
                subject=subject,
                present=True
            ).count()
            
            attendance_data.append({
                'subject': subject,
                'Classes Held': total_classes,
                'classes Attended': attended_classes,
                'classes Absent': total_classes - attended_classes, 
                'Absent Dates': [attendance.date.strftime('%Y-%m-%d') for attendance in Attendance.objects.filter(student=student, subject=subject, present=False)],
                'Attendance %': (attended_classes / total_classes * 100) if total_classes > 0 else 0
            })
        
        context['attendance_reports'] = attendance_data
        overall = sum([entry['Attendance %'] for entry in attendance_data])
        context['overall_percentage'] = round(overall / len(attendance_data), 1) if attendance_data else 0

        return context

class FaceCaptureView(UserPassesTestMixin, TemplateView):
    template_name = 'admin/face_capture.html'

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request):
        image_data = request.POST.get('image')
        roll_number = request.POST.get('roll_number')
        
        try:
            student = Student.objects.get(roll_number=roll_number)
            
            # Check if student already has a face encoding
            if student.face_encoding:
                return JsonResponse({
                    'success': False, 
                    'error': 'Student already has a face encoding. Please contact admin to update.'
                })
            
            image_data = base64.b64decode(image_data.split(',')[1])
            image = face_recognition.load_image_file(io.BytesIO(image_data))
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                return JsonResponse({
                    'success': False, 
                    'error': 'No face detected in image'
                })
                
            if len(face_encodings) > 1:
                return JsonResponse({
                    'success': False, 
                    'error': 'Multiple faces detected. Please ensure only one face is in the frame'
                })
            
            student.face_encoding = face_encodings[0].tobytes()
            student.save()
            return JsonResponse({'success': True})
            
        except Student.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Student not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            })

class FaceRecognitionView(View):
    def get(self, request):
        if not request.user.is_staff:
            return HttpResponseForbidden()
        return render(request, 'face_recognition.html')

    def post(self, request):
        video_capture = cv2.VideoCapture(0)
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True
        face_count = 0

        while True:
            ret, frame = video_capture.read()
            if process_this_frame and face_count < 5:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]
                
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                for face_encoding in face_encodings:
                    students = Student.objects.all()
                    known_faces = [np.frombuffer(student.face_encoding) for student in students]
                    matches = face_recognition.compare_faces(known_faces, face_encoding)
                    
                    if True in matches:
                        student_index = matches.index(True)
                        student = students[student_index]
                        self.mark_attendance(student)
                        face_count += 1

            process_this_frame = not process_this_frame
            if face_count >= 5:
                break

        video_capture.release()
        return JsonResponse({'status': 'success'})

    def mark_attendance(self, student):
        current_time = datetime.now().time()
        current_subject = self.get_current_subject(current_time)
        
        if current_subject:
            Attendance.objects.create(
                student=student,
                subject=current_subject,
                present=True
            )

class AttendanceReportView(LoginRequiredMixin, View):
    def get(self, request):
        student = Student.objects.get(user=request.user)
        subjects = Subject.objects.filter(department=student.department, year=student.year, section=student.section)

        attendance_summary = []
        detailed_report = []

        today = timezone.now().date()
        trend_dates = []
        trend_percentages = []

        for subject in subjects:
            total = Attendance.objects.filter(subject=subject).values('date').distinct().count()
            attended = Attendance.objects.filter(subject=subject, student=student, present=True).count()
            percentage = round((attended / total * 100), 1) if total > 0 else 0

            attendance_summary.append({
                'subject_name': subject.name,
                'total_classes': total,
                'attended_classes': attended,
                'percentage': percentage
            })

            logs = Attendance.objects.filter(subject=subject, student=student).order_by('-date')
            detailed_report.append({
                'subject_name': subject.name,
                'entries': [{
                    'date': a.date.strftime("%B %d, %Y"),
                    'status': "Present" if a.present else "Absent",
                    'time': a.time.strftime("%I:%M %p") if a.time else "N/A"
                } for a in logs]
            })

        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            total = Attendance.objects.filter(student=student, date=date).count()
            present = Attendance.objects.filter(student=student, date=date, present=True).count()
            percent = round((present / total) * 100, 1) if total else 0
            trend_dates.append(date.strftime('%b %d'))
            trend_percentages.append(percent)

        context = {
            'attendance_summary': attendance_summary,
            'detailed_report': detailed_report,
            'dates': json.dumps(trend_dates),
            'percentages': json.dumps(trend_percentages),
        }
        return render(request, 'attendance_report.html', context)


class StudentDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        student = Student.objects.get(user=request.user)
        subjects = Subject.objects.filter(department=student.department, year=student.year, section=student.section)

        attendance_reports = []
        total_attended = total_classes = 0
        monthly_present = monthly_absent = 0
        weekly_present = weekly_absent = 0

        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        monthly_labels = []
        monthly_data = []

        for subject in subjects:
            subject_attendance = Attendance.objects.filter(subject=subject, student=student).order_by('date')

            classes = Attendance.objects.filter(subject=subject).values('date').distinct().count()
            attended = subject_attendance.filter(present=True).count()
            percentage = round((attended / classes * 100), 1) if classes > 0 else 0
            absent_dates = subject_attendance.filter(present=False).values_list('date', flat=True)

            attendance_reports.append({
                'subject': subject,
                'total_classes': classes,
                'attended_classes': attended,
                'classes_absent': len(absent_dates),
                'absent_dates': [d.strftime("%b %d") for d in absent_dates],
                'attendance_percentage': percentage
            })

            total_classes += classes
            total_attended += attended

            monthly_present += subject_attendance.filter(date__gte=month_ago, present=True).count()
            monthly_absent += subject_attendance.filter(date__gte=month_ago, present=False).count()

            weekly_present += subject_attendance.filter(date__gte=week_ago, present=True).count()
            weekly_absent += subject_attendance.filter(date__gte=week_ago, present=False).count()

        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            daily_total = Attendance.objects.filter(student=student, date=date).count()
            daily_present = Attendance.objects.filter(student=student, date=date, present=True).count()
            percent = round((daily_present / daily_total * 100), 1) if daily_total else 0
            monthly_labels.append(date.strftime("%b %d"))
            monthly_data.append(percent)

        overall = round((total_attended / total_classes * 100), 1) if total_classes > 0 else 0

        context = {
            'attendance_reports': attendance_reports,
            'overall_percentage': overall,
            'monthly_present': monthly_present,
            'monthly_absent': monthly_absent,
            'weekly_present': weekly_present,
            'weekly_absent': weekly_absent,
            'monthly_labels': json.dumps(monthly_labels),
            'monthly_data': json.dumps(monthly_data),
            'weekly_data': json.dumps([weekly_present, weekly_absent])
        }
        return render(request, 'student_dashboard.html', context)


class ProfileView(LoginRequiredMixin, TemplateView):

    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = Student.objects.get(user=self.request.user)
        context['student'] = student
        return context

class TimetableView(LoginRequiredMixin, TemplateView):
    template_name = 'timetable.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = Student.objects.get(user=self.request.user)

        # Define student_section before using it
        student_section = student.section

        # Get timetable entries for student's department, year and section
        timetable_entries = TimeTable.objects.filter(
            subject__department=student.department,
            subject__year=student.year,
            subject__section=student.section
        ).select_related('subject')

        # Define time slots
        time_slots = [
            {'start': '09:30', 'end': '10:30'},  # P1
            {'start': '10:30', 'end': '11:30'},  # P2
            {'start': '11:40', 'end': '12:40'},  # P3
            {'start': '12:40', 'end': '13:40'},  # P4
            {'start': '14:15', 'end': '15:15'},  # P5
            {'start': '15:15', 'end': '16:15'},  # P6
        ]

        # Define days
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']

        # Initialize timetable dictionary
        timetable = {day: {} for day in days}

        # Populate timetable
        for entry in timetable_entries:
            day = days[entry.day_of_week - 1]
            entry_time = entry.start_time.strftime('%H:%M')
            for i, slot in enumerate(time_slots):
                if entry_time == slot['start']:
                    timetable[day][i] = entry
                    break

        # Add all required context
        context.update({
            'time_slots': time_slots,
            'days': days,
            'timetable': timetable,
            'student_section': student_section,
            'student_roll': student.roll_number,
            'department': student.department,
            'year': student.year,
            # 'subjects': subjects  # Uncomment if you have defined 'subjects' above
        })

        return context
        roll_info = student.parse_roll_number()

        # Get all sections for the student's department and year
        sections = Student.objects.filter(
            department=student.department,
            year=student.year
        ).values_list('section', flat=True).distinct()

        # Get selected section (default to student's section)
        selected_section = self.request.GET.get('section', student.section)

        # Get timetable entries based on parsed roll number information
        timetable_entries = TimeTable.objects.filter(
            subject__department=student.department,
            subject__year=student.year,
            subject__section=selected_section
        ).select_related('subject')

        # Define time slots with 24-hour format
        time_slots = [
            {'start': '09:30', 'end': '10:30'},  # P1
            {'start': '10:30', 'end': '11:30'},  # P2
            {'start': '11:40', 'end': '12:40'},  # P3
            {'start': '12:40', 'end': '13:40'},  # P4
            {'start': '14:15', 'end': '15:15'},  # P5
            {'start': '15:15', 'end': '16:15'},  # P6
        ]

        days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
        timetable = {day: {} for day in days}

        for entry in timetable_entries:
            day = days[entry.day_of_week - 1]
            entry_time = entry.start_time.strftime('%H:%M')
            for i, slot in enumerate(time_slots):
                if entry_time == slot['start']:
                    timetable[day][i] = entry
                    break

        context.update({
            'time_slots': time_slots,
            'timetable': timetable,
            'days': days,
            'sections': sections,
            'selected_section': selected_section,
            'roll_info': roll_info  # Add roll number info to context
        })
        return context


@staff_member_required
def get_sections_by_department(request):
    department_id = request.GET.get('department')
    if department_id:
        sections = Section.objects.filter(department_id=department_id)
        data = [{'id': section.id, 'name': section.name} for section in sections]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

@staff_member_required
def get_subjects_by_department_section(request):
    department_id = request.GET.get('department')
    section_id = request.GET.get('section')
    subjects = Subject.objects.filter(
        department_id=department_id,
        section_id=section_id
    ).values('id', 'name')
    return JsonResponse({'subjects': list(subjects)})

@staff_member_required
def get_subjects_for_timetable(request):
    department = request.GET.get('department')
    
    if not department:
        return JsonResponse({'error': 'Department is required'}, status=400)
        
    subjects = Subject.objects.filter(department=department)
    subject_data = [{
        'id': subject.id,
        'name': f'{subject.code} - {subject.name}'
    } for subject in subjects]
    
    return JsonResponse({'subjects': subject_data})

def generate_report(request):
    # Create the HttpResponse object with PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'

    # Create the PDF object, using the response as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's a simple example:
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Attendance Report")
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Student: {request.user.username}")

    # Add more content as needed...
    p.drawString(100, 760, "This is a sample PDF report.")

    # Close the PDF object cleanly.
    p.showPage()
    p.save()
    return response