from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from students.models import Schedule, Mark
from .serializers import (
    UserListSerializer,
    ScheduleSerializer,
    StudentDashboardSerializer,
    ChildDashboardSerializer,
    ParentDashboardSerializer,
    TeacherDashboardSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff or getattr(user, 'role', None) in ['admin', 'director', 'head_teacher']:
            return User.objects.all()
        return User.objects.filter(id=user.id)


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_superuser or user.is_staff or getattr(user, 'role', None) in ['admin', 'director', 'head_teacher']):
            return Response(
                {"detail": "You do not have permission to modify the schedule."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = user.role

        if role == 'student':
            today_schedule = Schedule.objects.filter(school_class=user.school_class) if user.school_class else []
            recent_marks = Mark.objects.filter(student=user).order_by('-id')[:10]

            serializer = StudentDashboardSerializer({
                'user': user,
                'today_schedule': today_schedule,
                'recent_marks': recent_marks
            })
            return Response(serializer.data)

        elif role == 'parent':
            children_data = []
            for child in user.children.all():
                child_schedule = Schedule.objects.filter(school_class=child.school_class) if child.school_class else []
                child_marks = Mark.objects.filter(student=child).order_by('-id')[:10]

                children_data.append({
                    'child_info': child,
                    'today_schedule': child_schedule,
                    'recent_marks': child_marks
                })

            serializer = ParentDashboardSerializer({
                'user': user,
                'children': children_data
            })
            return Response(serializer.data)

        elif role == 'teacher':
            today_schedule = Schedule.objects.filter(teacher=user)

            serializer = TeacherDashboardSerializer({
                'user': user,
                'today_schedule': today_schedule
            })
            return Response(serializer.data)

        return Response({
            "user": user.username,
            "role": role,
            "message": "Панель администратора"
        })