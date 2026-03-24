"""
Management command: seed_users
Creates all students and teachers from Users.txt into the database.

Students → B Tech Ed in IT, 5th Semester, enrollment_year=2022
Teachers → role=teacher, subject assignment via TeacherSubject

Usage:
    python manage.py seed_users
"""

from django.core.management.base import BaseCommand
from core.models import User, Student, Course, Semester, Subject, TeacherSubject


COURSE_NAME = "B Tech Ed in IT"
SEMESTER_NO = 5
ENROLLMENT_YEAR = 2022

STUDENTS = [
    ("Smarika",   "Khatri",      "smarika.khatri@kusoed.edu.np"),
    ("Kabita",    "Katwal",      "kabita.katwal@kusoed.edu.np"),
    ("Rojista",   "Shrestha",    "rojista.shrestha@kusoed.edu.np"),
    ("Karan",     "Chaudhary",   "karan.chaudhary@kusoed.edu.np"),
    ("Akshit",    "Pokharel",    "akshit.pokharel@kusoed.edu.np"),
    ("Prabina",   "Budhathoki",  "prabina.budhathoki@kusoed.edu.np"),
    ("Suraj Kumar","Mahato",     "suraj.mahato@kusoed.edu.np"),
    ("Shristi",   "Shrestha",    "shristi.shrestha@kusoed.edu.np"),
    ("Rohan",     "Thapa",       "rohan.thapa@kusoed.edu.np"),
    ("Santosh",   "Bhatta",      "santosh.bhatta@kusoed.edu.np"),
    ("Raman",     "Neupane",     "raman.neupane@kusoed.edu.np"),
    ("Rajkumar",  "Pokharel",    "rajkumar.pokharel@kusoed.edu.np"),
    ("Salan",     "Maharjan",    "salan.maharjan@kusoed.edu.np"),
    ("Manjila",   "Silwal",      "manjila.silwal@kusoed.edu.np"),
    ("Govinda",   "Basak",       "govinda.basak@kusoed.edu.np"),
    ("Sandip",    "Ram",         "sandip.ram@kusoed.edu.np"),
    ("Samir",     "Tamang",      "samir.tamang@kusoed.edu.np"),
    ("Jeebesh",   "Khatri",      "jeebesh.khatri@kusoed.edu.np"),
    ("Bikash",    "Sapkota",     "bikash.sapkota@kusoed.edu.np"),
    ("Anand",     "Jaiswal",     "anand.jaiswal@kusoed.edu.np"),
    ("Dipshikha", "Ghimire",     "dipshikha.ghimire@kusoed.edu.np"),
    ("Trishna",   "Thapa",       "trishna.thapa@kusoed.edu.np"),
    ("Sajin",     "Ghimire",     "sajin.ghimire@kusoed.edu.np"),
]

# (firstname, lastname, email, subject_name)
TEACHERS = [
    ("Pratit Raj", "Giri",   "pratit.giri.teacher@kusoed.edu.np",   "Software Engineering"),
    ("Avinash",    "Maskey", "avinash.maskey.teacher@kusoed.edu.np", "Management Information System"),
]


def make_password_from_email(email):
    """Password = part before the '@', e.g. smarika.khatri"""
    return email.split("@")[0]


class Command(BaseCommand):
    help = "Seed students and teachers from Users.txt into the database"

    def handle(self, *args, **options):
        # ── 1. Ensure course exists ────────────────────────────────────────────
        course, created = Course.objects.get_or_create(course_name=COURSE_NAME)
        if created:
            self.stdout.write(self.style.SUCCESS(f"  [+] Course created: {COURSE_NAME}"))
        else:
            self.stdout.write(f"  [=] Course already exists: {COURSE_NAME}")

        # ── 2. Ensure semester exists ──────────────────────────────────────────
        semester, created = Semester.objects.get_or_create(
            course=course, semester_no=SEMESTER_NO
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"  [+] Semester {SEMESTER_NO} created"))
        else:
            self.stdout.write(f"  [=] Semester {SEMESTER_NO} already exists")

        # ── 3. Create students ─────────────────────────────────────────────────
        self.stdout.write("\n--- Creating Students ---")
        for firstname, lastname, email in STUDENTS:
            if User.objects.filter(email=email).exists():
                self.stdout.write(f"  [skip] {email} already exists")
                continue
            password = make_password_from_email(email)
            user = User.objects.create_user(
                email=email,
                password=password,
                firstname=firstname,
                lastname=lastname,
                role="student",
            )
            Student.objects.create(
                user=user,
                course=course,
                current_semester=SEMESTER_NO,
                enrollment_year=ENROLLMENT_YEAR,
            )
            self.stdout.write(
                self.style.SUCCESS(f"  [+] Student: {firstname} {lastname}  |  pw: {password}")
            )

        # ── 4. Create teachers ─────────────────────────────────────────────────
        self.stdout.write("\n--- Creating Teachers ---")
        for firstname, lastname, email, subject_name in TEACHERS:
            if User.objects.filter(email=email).exists():
                self.stdout.write(f"  [skip] {email} already exists")
                teacher_user = User.objects.get(email=email)
            else:
                password = make_password_from_email(email)
                teacher_user = User.objects.create_user(
                    email=email,
                    password=password,
                    firstname=firstname,
                    lastname=lastname,
                    role="teacher",
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [+] Teacher: {firstname} {lastname}  |  pw: {password}"
                    )
                )

            # ── 5. Ensure the subject exists and assign teacher ────────────────
            subject = Subject.objects.filter(
                subject_name__iexact=subject_name,
                course=course,
                semester=semester,
            ).first()

            if not subject:
                # Generate a short code from the subject name
                code_parts = [w[0].upper() for w in subject_name.split()]
                code = "".join(code_parts) + str(SEMESTER_NO)
                # Make sure code is unique
                base_code = code
                counter = 1
                while Subject.objects.filter(subject_code=code).exists():
                    code = f"{base_code}{counter}"
                    counter += 1

                subject = Subject.objects.create(
                    subject_code=code,
                    subject_name=subject_name,
                    course=course,
                    semester=semester,
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"    [+] Subject created: {subject_name} (code: {code})"
                    )
                )
            else:
                self.stdout.write(f"    [=] Subject already exists: {subject_name}")

            # Assign teacher to subject if not already assigned
            ts, created = TeacherSubject.objects.get_or_create(
                subject=subject, teacher=teacher_user
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"    [+] Assigned {firstname} {lastname} to {subject_name}"
                    )
                )
            else:
                self.stdout.write(
                    f"    [=] Assignment already exists for {firstname} {lastname}"
                )

        self.stdout.write(self.style.SUCCESS("\n[DONE] seed_users completed successfully!"))
