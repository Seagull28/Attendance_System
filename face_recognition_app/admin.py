from django.contrib import admin
from django import forms
from django.urls import path
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from .models import Student, Subject, Attendance, TimeTable, AttendanceReport, Department, Section

class TimeTableForm(forms.ModelForm):
    DAYS_OF_WEEK = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday')
    ]

    department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label=None)
    section = forms.ModelChoiceField(queryset=Section.objects.none(), empty_label=None)
    day_of_week = forms.ChoiceField(choices=DAYS_OF_WEEK)

    class Meta:
        model = TimeTable
        fields = ['department', 'section', 'subject', 'day_of_week', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'instance' in kwargs and kwargs['instance']:
            subject = kwargs['instance'].subject
            self.fields['department'].initial = subject.department
            self.fields['section'].initial = subject.section
            self.fields['section'].queryset = Section.objects.filter(department=subject.department)

        elif self.data.get('department'):
            try:
                department_id = int(self.data.get('department'))
                self.fields['section'].queryset = Section.objects.filter(department_id=department_id)
                if self.data.get('section'):
                    section_id = int(self.data.get('section'))
                    self.fields['subject'].queryset = Subject.objects.filter(
                        department_id=department_id,
                        section_id=section_id
                    ).order_by('code')
                else:
                    self.fields['subject'].queryset = Subject.objects.none()
            except (ValueError, TypeError):
                self.fields['section'].queryset = Section.objects.none()
                self.fields['subject'].queryset = Subject.objects.none()
        else:
            self.fields['section'].queryset = Section.objects.none()
            self.fields['subject'].queryset = Subject.objects.none()

@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    form = TimeTableForm
    list_display = ['get_path', 'get_subject_code', 'get_subject_name', 'day_of_week', 'start_time', 'end_time']
    list_filter = ['subject__department', 'subject__year', 'day_of_week']
    search_fields = ['subject__code', 'subject__name']
    ordering = ['subject__department', 'subject__year', 'day_of_week', 'start_time']

    def get_path(self, obj):
        return f"{obj.subject.department.code}/{obj.subject.year}/{self.get_day_name(obj.day_of_week)}/{obj.start_time.strftime('%H:%M')}"
    get_path.short_description = 'Path'
    get_path.admin_order_field = 'subject__department'

    def get_day_name(self, day_number):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        return days[day_number - 1] if 1 <= day_number <= 6 else 'Unknown'

    def get_subject_code(self, obj):
        return obj.subject.code
    get_subject_code.short_description = 'Subject Code'
    get_subject_code.admin_order_field = 'subject__code'

    def get_subject_name(self, obj):
        return obj.subject.name
    get_subject_name.short_description = 'Subject Name'
    get_subject_name.admin_order_field = 'subject__name'

    class Media:
        js = ('js/timetable_admin.js',)


# ✅ AJAX VIEWS
@staff_member_required
def get_sections_by_department(request):
    department_id = request.GET.get('department')
    sections = Section.objects.filter(department_id=department_id).values('id', 'name')
    return JsonResponse({'sections': list(sections)})

@staff_member_required
def get_subjects_by_department_section(request):
    department_id = request.GET.get('department')
    section_id = request.GET.get('section')
    subjects = Subject.objects.filter(
        department_id=department_id,
        section_id=section_id
    ).values('id', 'name')
    return JsonResponse({'subjects': list(subjects)})

# ✅ SAFELY APPEND CUSTOM URLS WITHOUT BREAKING DEFAULTS
original_get_urls = admin.site.get_urls

def custom_admin_urls():
    return [
        path('face_recognition_app/section/by-department/', get_sections_by_department),
        path('face_recognition_app/subject/by-department-section/', get_subjects_by_department_section),
    ] + original_get_urls()

admin.site.get_urls = custom_admin_urls


# ✅ Register remaining models

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'user', 'department', 'year', 'section')
    list_filter = ('department', 'year', 'section')
    search_fields = ('roll_number', 'user__username')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'year')
    list_filter = ('department', 'year')
    search_fields = ('code', 'name')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'present')
    list_filter = ('subject', 'date', 'present')

@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'total_classes', 'classes_attended', 'month', 'year')
    list_filter = ('subject', 'month', 'year')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('department', 'name', 'year', 'capacity')
    list_filter = ('department', 'year')
    search_fields = ('department__code', 'department__name')
