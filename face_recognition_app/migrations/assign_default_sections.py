from django.db import migrations

def assign_sections(apps, schema_editor):
    Subject = apps.get_model('face_recognition_app', 'Subject')
    Section = apps.get_model('face_recognition_app', 'Section')
    
    # For each subject without a section
    for subject in Subject.objects.filter(section__isnull=True):
        # Try to find a matching section
        section = Section.objects.filter(
            department=subject.department,
            year=subject.year,
            name='A'  # Default to section A
        ).first()
        
        if section:
            subject.section = section
            subject.save()

class Migration(migrations.Migration):
    dependencies = [
        ('face_recognition_app', '0003_subject_section'),  # Update this to your latest migration
    ]

    operations = [
        migrations.RunPython(assign_sections),
    ]
