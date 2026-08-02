from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet,
    SubjectViewSet,
    StudyGroupViewSet,
    ScheduleViewSet,
    CalendarLessonViewSet,
    AttendanceAndGradeViewSet,
    MarkViewSet,
    SupportMessageViewSet,
    TeacherLessonViewSet, HomeworkSubmissionViewSet
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'study-groups', StudyGroupViewSet, basename='studygroup')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'calendar-lessons', CalendarLessonViewSet, basename='calendarlesson')
router.register(r'attendance-grades', AttendanceAndGradeViewSet, basename='attendancegrade')
router.register(r'marks', MarkViewSet, basename='mark')
router.register(r'support-messages', SupportMessageViewSet, basename='supportmessage')
router.register(r'teacher-lessons', TeacherLessonViewSet, basename='teacher-lesson')
router.register(r'homework-submissions', HomeworkSubmissionViewSet, basename='homework-submission')

urlpatterns = [
    path('', include(router.urls)),
]