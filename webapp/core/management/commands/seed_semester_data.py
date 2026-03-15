import os
import sys
import json
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")
django.setup()

from core.models import Course, Semester, Subject

def seed_data():
    # Attempt to read the JSON file
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "semester_data.json")
    if not os.path.exists(json_path):
        print(f"Error: Could not find {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # We need a primary course to attach these to
    course, created = Course.objects.get_or_create(
        course_name="B Tech Ed in IT",
        defaults={'status': 'active'}
    )
    if created:
        print(f"Created Course: {course.course_name}")

    for semester_key, subjects in data.items():
        # Extact semester number from 'semester1', 'semester2', etc.
        try:
            sem_no = int(semester_key.replace("semester", ""))
        except ValueError:
            print(f"Invalid semester key format: {semester_key}")
            continue

        semester, created = Semester.objects.get_or_create(
            course=course,
            semester_no=sem_no
        )
        if created:
            print(f"Created Semester {sem_no}")

        for subj in subjects:
            code = subj.get("code")
            name = subj.get("name")
            if not code or not name:
                continue

            subject, created = Subject.objects.update_or_create(
                subject_code=code,
                defaults={
                    'subject_name': name,
                    'course': course,
                    'semester': semester,
                }
            )
            if created:
                print(f"Created Subject: {code} - {name}")
            else:
                print(f"Updated Subject: {code} - {name}")

    print("Data import complete.")

if __name__ == "__main__":
    seed_data()
