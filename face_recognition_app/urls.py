from django.urls import path
from django.contrib.auth import views as auth_views
from face_recognition_app.views import (
    StudentDashboardView,
    AttendanceReportView,
    FaceCaptureView,
    ProfileView,
    TimetableView,
    get_subjects_for_timetable,
    get_sections_by_department,
    get_subjects_by_department_section,
    generate_report,
)

urlpatterns = [
    # 👤 Student Dashboard & Profile
    path('dashboard/', StudentDashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # 📊 Attendance Report
    path('dashboard/attendance-report/', AttendanceReportView.as_view(), name='attendance_report'),
    path('dashboard/generate-report/', generate_report, name='generate_report'),

    # 📸 Face Capture
    path('face-capture/', FaceCaptureView.as_view(), name='face_capture'),

    # 📅 Timetable
    path('timetable/', TimetableView.as_view(), name='timetable'),

    # 🔐 Authentication
    path(
        'change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='registration/change_password.html',
            success_url='/dashboard/profile/'
        ),
        name='change_password'
    ),

    # 🧠 Admin AJAX APIs
    path(
        'admin/face_recognition_app/timetable/get_subjects/',
        get_subjects_for_timetable,
        name='get_subjects_for_timetable'
    ),
    path(
        'admin/face_recognition_app/section/by-department/',
        get_sections_by_department,
        name='get_sections_by_department'
    ),
    path(
        'admin/face_recognition_app/subject/by-department-section/',
        get_subjects_by_department_section,
        name='get_subjects_by_department_section'
    ),
]
