from datetime import datetime, time
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import permissions, viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .serializers import HomeworkSubmissionSerializer

from structure.models import SupportMessage
from structure.serializers import SupportMessageSerializer
from users.permissions import IsTeacher
from users.serializers import MarkSerializer
from .models import Subject, StudyGroup, Schedule, CalendarLesson, Mark, HomeworkSubmission
from .permissions import IsTeacherOrAdminOrReadOnly
from .serializers import (
    StudentSerializer,
    SubjectSerializer,
    StudyGroupSerializer,
    ScheduleSerializer,
    CalendarLessonSerializer,
    AttendanceAndGradeSerializer,
    TeacherLessonSerializer, HomeworkSubmissionSerializer
)

User = get_user_model()


class StudentViewSet(ModelViewSet):
    queryset = User.objects.filter(role='student')
    serializer_class = StudentSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.role == 'student':
            return queryset.filter(id=user.id)
        return queryset


class SubjectViewSet(ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdminOrReadOnly]


class StudyGroupViewSet(ModelViewSet):
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdminOrReadOnly]


class ScheduleViewSet(ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff or user.role in ['admin', 'director', 'head_teacher']:
            return Schedule.objects.all()
        if user.role == 'teacher':
            return Schedule.objects.filter(teacher=user)
        if user.role == 'student':
            return Schedule.objects.filter(school_class=user.school_class)
        return Schedule.objects.none()


class CalendarLessonViewSet(ModelViewSet):
    queryset = CalendarLesson.objects.all()
    serializer_class = CalendarLessonSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff or user.role in ['admin', 'director', 'head_teacher']:
            return CalendarLesson.objects.all()
        if user.role == 'teacher':
            return CalendarLesson.objects.filter(schedule__teacher=user)
        if user.role == 'student':
            return CalendarLesson.objects.filter(schedule__school_class=user.school_class)
        return CalendarLesson.objects.none()

    def perform_create(self, serializer):
        date_input = self.request.data.get('date')

        if not date_input:
            date_input = timezone.now().date().strftime('%Y-%m-%d')

        serializer.save(date=date_input)
class AttendanceAndGradeViewSet(ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = AttendanceAndGradeSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdminOrReadOnly]


class MarkViewSet(viewsets.ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsTeacher]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        is_present = self.request.data.get('is_present', False)

        lesson_id = self.request.data.get('lesson')
        if not lesson_id:
            raise ValidationError({"detail": "Lesson was not specified."})

        try:
            from students.models import CalendarLesson
            lesson = CalendarLesson.objects.get(id=lesson_id)
        except CalendarLesson.DoesNotExist:
            raise ValidationError({"detail": "The specified lesson was not found."})

        now = timezone.now()

        lesson_start_datetime = timezone.make_aware(
            datetime.combine(lesson.date, lesson.schedule.start_time)
        )

        end_of_day_datetime = timezone.make_aware(
            datetime.combine(lesson.date, time(23, 59, 59))
        )

        if now < lesson_start_datetime:
            raise ValidationError({
                "detail": "You cannot submit attendance or grades before the lesson starts!"
            })

        if now > end_of_day_datetime:
            raise ValidationError({
                "detail": "The submission time for this attendance has expired (only available until the end of the lesson's day)."
            })

        serializer.save(is_present=is_present, date=lesson.date)


class SupportMessageViewSet(viewsets.ModelViewSet):
    serializer_class = SupportMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        user = self.request.user

        if user.role in ['helper', 'admin']:
            return SupportMessage.objects.filter(chat_id=chat_id)
        return SupportMessage.objects.filter(chat_id=chat_id, chat__user=user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class TeacherLessonViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TeacherLessonSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    def get_queryset(self):
        user = self.request.user

        date_param = self.request.query_params.get('date')
        if date_param:
            date_param = date_param.rstrip('/')
            try:
                target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError({"detail": "Invalid date format. Use YYYY-MM-DD."})
        else:
            target_date = timezone.now().date()

        start_of_week = target_date - timezone.timedelta(days=target_date.weekday())
        end_of_week = start_of_week + timezone.timedelta(days=6)

        teacher_id = self.request.query_params.get('teacher_id')
        if teacher_id:
            teacher_id = teacher_id.rstrip('/')

        if user.is_superuser or user.is_staff or user.role in ['admin', 'director', 'head_teacher']:
            if teacher_id:
                qs = CalendarLesson.objects.filter(schedule__teacher_id=teacher_id)
            else:
                qs = CalendarLesson.objects.all()
        elif user.role == 'teacher':
            qs = CalendarLesson.objects.filter(schedule__teacher=user)
        else:
            if teacher_id:
                qs = CalendarLesson.objects.filter(schedule__teacher_id=teacher_id)
            else:
                return CalendarLesson.objects.none()

        return qs.filter(date__range=[start_of_week, end_of_week]).order_by('date', 'schedule__start_time')


class HomeworkSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'teacher' or user.is_staff:
            qs = HomeworkSubmission.objects.all()
        else:
            qs = HomeworkSubmission.objects.filter(student=user)

        date_param = self.request.query_params.get('date')
        if date_param:
            date_param = date_param.rstrip('/')
            qs = qs.filter(lesson__date=date_param)

        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)