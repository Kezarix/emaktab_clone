from datetime import datetime, time
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import permissions, viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from structure.models import SupportMessage
from structure.serializers import SupportMessageSerializer
from school.models import AcademicLoad

from .models import (
    Subject, StudyGroup, Schedule, CalendarLesson, Mark, HomeworkSubmission
)
from .permissions import IsTeacherOrAdminOrReadOnly
from .serializers import (
    StudentSerializer,
    SubjectSerializer,
    StudyGroupSerializer,
    ScheduleSerializer,
    CalendarLessonSerializer,
    AttendanceAndGradeSerializer,
    TeacherLessonSerializer,
    HomeworkSubmissionSerializer,
)

User = get_user_model()


# ============================================================
# HELPERS
# ============================================================

def get_role(user):
    return getattr(user, 'role', None) if user and user.is_authenticated else None


def teacher_major_id(user):
    """ID предмета (major), который ведёт учитель. None — если не задан."""
    return getattr(user, 'major_id', None)


def teacher_class_ids(user):
    """
    Классы, где учитель ведёт уроки ПО СВОЕМУ major.
    Если major не задан — пустой queryset.
    """
    major_id = teacher_major_id(user)
    if not major_id:
        return Schedule.objects.none().values_list('school_class_id', flat=True)
    return (
        Schedule.objects
        .filter(teacher=user, subject_id=major_id)
        .values_list('school_class_id', flat=True)
        .distinct()
    )


class IsTeacherRole(permissions.BasePermission):
    """teacher / head_teacher / director / admin / staff."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            request.user.is_superuser
            or request.user.is_staff
            or getattr(request.user, 'role', None) in
                ['teacher', 'head_teacher', 'director', 'admin']
        )


# ============================================================
# STUDENTS
# ============================================================

class StudentViewSet(ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [IsTeacherOrAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()

        qs = User.objects.filter(role='student').select_related('school_class')
        role = get_role(user)

        if role == 'student':
            return qs.filter(id=user.id)
        if role == 'parent':
            return qs.filter(parents=user)
        if role == 'teacher':
            return qs.filter(school_class_id__in=teacher_class_ids(user))
        if user.is_superuser or user.is_staff or role in ['admin', 'director', 'head_teacher']:
            return qs
        return qs.none()


# ============================================================
# SUBJECTS
# ============================================================

class SubjectViewSet(ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdminOrReadOnly]


# ============================================================
# STUDY GROUPS
# ============================================================

class StudyGroupViewSet(ModelViewSet):
    serializer_class = StudyGroupSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return StudyGroup.objects.none()
        role = get_role(user)
        qs = StudyGroup.objects.select_related('school_class')
        if user.is_superuser or user.is_staff or role in ['admin', 'director', 'head_teacher']:
            return qs
        if role == 'teacher':
            # только группы классов, где ведёт свой major
            return qs.filter(school_class_id__in=teacher_class_ids(user))
        if role == 'student':
            return qs.filter(school_class=user.school_class)
        return qs.none()


# ============================================================
# SCHEDULE
# ============================================================

class ScheduleViewSet(ModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Schedule.objects.none()

        role = get_role(user)
        qs = Schedule.objects.select_related('school_class', 'subject', 'teacher')

        if user.is_superuser or user.is_staff or role in ['admin', 'director', 'head_teacher']:
            return qs

        if role == 'teacher':
            major_id = teacher_major_id(user)
            if not major_id:
                return Schedule.objects.none()
            return qs.filter(teacher=user, subject_id=major_id)

        if role == 'student':
            return qs.filter(school_class=user.school_class)

        if role == 'parent':
            return qs.filter(
                school_class__in=user.children.values_list('school_class_id', flat=True)
            )

        return qs.none()


# ============================================================
# CALENDAR LESSONS
# ============================================================

class CalendarLessonViewSet(ModelViewSet):
    serializer_class = CalendarLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CalendarLesson.objects.none()

        role = get_role(user)
        qs = CalendarLesson.objects.select_related(
            'schedule__school_class', 'schedule__subject', 'schedule__teacher'
        )

        if user.is_superuser or user.is_staff or role in ['admin', 'director', 'head_teacher']:
            return qs

        if role == 'teacher':
            major_id = teacher_major_id(user)
            if not major_id:
                return CalendarLesson.objects.none()
            return qs.filter(
                schedule__teacher=user,
                schedule__subject_id=major_id,
            )

        if role == 'student':
            return qs.filter(schedule__school_class=user.school_class)

        if role == 'parent':
            return qs.filter(
                schedule__school_class__in=user.children.values_list('school_class_id', flat=True)
            )

        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        role = get_role(user)
        schedule_id = self.request.data.get('schedule')

        if role == 'teacher':
            if not schedule_id:
                raise ValidationError({"detail": "schedule is required."})
            try:
                sched = Schedule.objects.select_related('subject').get(id=schedule_id)
            except Schedule.DoesNotExist:
                raise ValidationError({"detail": "Schedule not found."})

            if sched.teacher_id != user.id:
                raise ValidationError({"detail": "This schedule is not yours."})

            if sched.subject_id != teacher_major_id(user):
                raise ValidationError({
                    "detail": "You can only create lessons for your own major."
                })

        date_input = self.request.data.get('date') or timezone.now().date().strftime('%Y-%m-%d')
        serializer.save(date=date_input)


# ============================================================
# ATTENDANCE / GRADE (read-mostly)
# ============================================================

class AttendanceAndGradeViewSet(ModelViewSet):
    serializer_class = AttendanceAndGradeSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Mark.objects.none()
        qs = Mark.objects.select_related('student', 'academic_load__subject')
        role = get_role(user)
        if user.is_superuser or user.is_staff or role in ['admin', 'director', 'head_teacher']:
            return qs
        if role == 'teacher':
            major_id = teacher_major_id(user)
            if not major_id:
                return Mark.objects.none()
            return qs.filter(
                academic_load__teacher=user,
                academic_load__subject_id=major_id,
            )
        if role == 'student':
            return qs.filter(student=user)
        if role == 'parent':
            return qs.filter(student__parents=user)
        return qs.none()


# ============================================================
# MARK
# ============================================================

class MarkViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceAndGradeSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeacherRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Mark.objects.none()

        qs = Mark.objects.select_related(
            'student', 'academic_load__subject', 'lesson'
        )
        role = get_role(user)

        if user.is_superuser or user.is_staff or role in ['admin', 'director', 'head_teacher']:
            return qs

        if role == 'teacher':
            major_id = teacher_major_id(user)
            if not major_id:
                return Mark.objects.none()
            return qs.filter(
                academic_load__teacher=user,
                academic_load__subject_id=major_id,
            )

        if role == 'student':
            return qs.filter(student=user)

        if role == 'parent':
            return qs.filter(student__parents=user)

        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        role = get_role(user)

        academic_load_id = self.request.data.get('academic_load')
        student_id = self.request.data.get('student')
        date_input = self.request.data.get('date')
        lesson_id = self.request.data.get('lesson')

        if not academic_load_id:
            raise ValidationError({"detail": "academic_load is required."})
        if not student_id:
            raise ValidationError({"detail": "student is required."})
        if not date_input:
            raise ValidationError({"detail": "date is required (YYYY-MM-DD)."})

        try:
            academic_load = AcademicLoad.objects.select_related(
                'teacher', 'school_grade', 'subject'
            ).get(id=academic_load_id)
        except AcademicLoad.DoesNotExist:
            raise ValidationError({"detail": "AcademicLoad not found."})

        try:
            student = User.objects.get(id=student_id, role='student')
        except User.DoesNotExist:
            raise ValidationError({"detail": "Student not found."})

        # 🔒 учитель — только свой major и свой academic_load
        if role == 'teacher':
            if academic_load.teacher_id != user.id:
                raise ValidationError({
                    "detail": "You can only grade your own academic loads."
                })
            if academic_load.subject_id != teacher_major_id(user):
                raise ValidationError({
                    "detail": "You can only grade your own subject (major)."
                })

        # 🔒 ученик должен быть из класса этого academic_load
        if student.school_class_id != academic_load.school_grade_id:
            raise ValidationError({
                "detail": "Student does not belong to this class."
            })

        # ---------- окно времени ----------
        lesson = None
        if lesson_id:
            try:
                lesson = CalendarLesson.objects.select_related('schedule').get(id=lesson_id)
            except CalendarLesson.DoesNotExist:
                raise ValidationError({"detail": "Lesson not found."})

            if role == 'teacher':
                if lesson.schedule.teacher_id != user.id:
                    raise ValidationError({"detail": "This lesson is not yours."})
                if lesson.schedule.subject_id != teacher_major_id(user):
                    raise ValidationError({
                        "detail": "This lesson is not for your subject."
                    })
        else:
            lesson = CalendarLesson.objects.filter(
                schedule__school_class=academic_load.school_grade,
                schedule__subject=academic_load.subject,
                date=date_input,
            ).first()

        if lesson and lesson.schedule and lesson.schedule.start_time:
            now = timezone.now()
            start = timezone.make_aware(
                datetime.combine(lesson.date, lesson.schedule.start_time)
            )
            end_of_day = timezone.make_aware(
                datetime.combine(lesson.date, time(23, 59, 59))
            )
            if now < start:
                raise ValidationError({"detail": "Cannot submit before the lesson starts."})
            if now > end_of_day:
                raise ValidationError({"detail": "Submission window has expired."})

        serializer.save(lesson=lesson)


# ============================================================
# SUPPORT MESSAGES (legacy — лучше использовать structure app)
# ============================================================

class SupportMessageViewSet(viewsets.ModelViewSet):
    serializer_class = SupportMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        user = self.request.user
        if not user.is_authenticated:
            return SupportMessage.objects.none()
        role = get_role(user)
        if role in ['helper', 'admin']:
            return SupportMessage.objects.filter(chat_id=chat_id)
        return SupportMessage.objects.filter(chat_id=chat_id, chat__user=user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


# ============================================================
# TEACHER LESSON (weekly)
# ============================================================

class TeacherLessonViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TeacherLessonSerializer
    permission_classes = [IsAuthenticated, IsTeacherRole]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CalendarLesson.objects.none()

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

        role = get_role(user)
        base_qs = CalendarLesson.objects.select_related(
            'schedule__school_class', 'schedule__subject', 'schedule__teacher'
        )

        if user.is_superuser or user.is_staff or role in ['admin', 'director', 'head_teacher']:
            qs = base_qs.filter(schedule__teacher_id=teacher_id) if teacher_id else base_qs
        elif role == 'teacher':
            major_id = teacher_major_id(user)
            if not major_id:
                return CalendarLesson.objects.none()
            qs = base_qs.filter(
                schedule__teacher=user,
                schedule__subject_id=major_id,
            )
        else:
            if teacher_id:
                qs = base_qs.filter(schedule__teacher_id=teacher_id)
            else:
                return CalendarLesson.objects.none()

        return qs.filter(date__range=[start_of_week, end_of_week]).order_by(
            'date', 'schedule__start_time'
        )


# ============================================================
# HOMEWORK SUBMISSIONS (full CRUD)
# ============================================================

class HomeworkSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = HomeworkSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return HomeworkSubmission.objects.none()

        role = get_role(user)
        qs = HomeworkSubmission.objects.select_related(
            'student', 'student__school_class',
            'lesson__schedule__subject', 'lesson__schedule__teacher',
        )

        if user.is_superuser or user.is_staff or role in ['admin', 'director', 'head_teacher']:
            pass

        elif role == 'teacher':
            major_id = teacher_major_id(user)
            if not major_id:
                return HomeworkSubmission.objects.none()
            qs = qs.filter(
                lesson__schedule__teacher=user,
                lesson__schedule__subject_id=major_id,
            )

        elif role == 'student':
            qs = qs.filter(student=user)

        elif role == 'parent':
            qs = qs.filter(student__parents=user)

        else:
            return HomeworkSubmission.objects.none()

        # query filters
        lesson_id = self.request.query_params.get('lesson')
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)

        student_id = self.request.query_params.get('student')
        if student_id:
            qs = qs.filter(student_id=student_id)

        date_param = self.request.query_params.get('date')
        if date_param:
            qs = qs.filter(lesson__date=date_param.rstrip('/'))

        subject_id = self.request.query_params.get('subject')
        if subject_id:
            qs = qs.filter(lesson__schedule__subject_id=subject_id)

        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        role = get_role(user)
        lesson = serializer.validated_data.get('lesson')

        if role == 'teacher' and lesson:
            if lesson.schedule.teacher_id != user.id:
                raise ValidationError({"detail": "This lesson is not yours."})
            if lesson.schedule.subject_id != teacher_major_id(user):
                raise ValidationError({
                    "detail": "This lesson is not for your subject."
                })

        if role == 'student':
            serializer.save(student=user)
        else:
            student = serializer.validated_data.get('student')
            serializer.save(student=student or user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        role = get_role(request.user)

        if role == 'student' and instance.student_id != request.user.id:
            return Response(
                {"detail": "You can only edit your own submission."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if role == 'teacher':
            if instance.lesson.schedule.teacher_id != request.user.id:
                return Response(
                    {"detail": "You can only edit submissions for your lessons."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if instance.lesson.schedule.subject_id != teacher_major_id(request.user):
                return Response(
                    {"detail": "This submission is not for your subject."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        role = get_role(request.user)

        if role == 'student' and instance.student_id != request.user.id:
            return Response(
                {"detail": "You can only delete your own submission."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if role == 'teacher':
            if instance.lesson.schedule.teacher_id != request.user.id:
                return Response(
                    {"detail": "You can only delete submissions for your lessons."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if instance.lesson.schedule.subject_id != teacher_major_id(request.user):
                return Response(
                    {"detail": "This submission is not for your subject."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return super().destroy(request, *args, **kwargs)