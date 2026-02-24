from django.urls import path
from . import views

urlpatterns = [
    path('subjects/<uuid:subject_id>/students/', views.teacher_view_students, name='teacher_view_students'),
]
