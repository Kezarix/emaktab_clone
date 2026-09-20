from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from students.models import Schedule, Mark
from students.serializers import (
    ScheduleSerializer,
    AttendanceAndGradeSerializer,
    StudentBriefSerializer,
)
from .serializers import (
    UserListSerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
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
        if not (
            user.is_superuser or user.is_staff or
            getattr(user, 'role', None) in ['admin', 'director', 'head_teacher']
        ):
            return Response(
                {"detail": "You do not have permission to modify the schedule."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, 'role', None)

        if role == 'student':
            schedule = Schedule.objects.filter(
                school_class=user.school_class
            ) if user.school_class else Schedule.objects.none()
            marks = Mark.objects.filter(student=user).order_by('-id')[:10]
            return Response({
                'user': UserListSerializer(user).data,
                'today_schedule': ScheduleSerializer(schedule, many=True).data,
                'recent_marks': AttendanceAndGradeSerializer(marks, many=True).data,
            })

        if role == 'parent':
            children = user.children.all()
            payload = []
            for child in children:
                child_schedule = Schedule.objects.filter(
                    school_class=child.school_class
                ) if child.school_class else Schedule.objects.none()
                child_marks = Mark.objects.filter(student=child).order_by('-id')[:10]
                payload.append({
                    'child_info': UserListSerializer(child).data,
                    'today_schedule': ScheduleSerializer(child_schedule, many=True).data,
                    'recent_marks': AttendanceAndGradeSerializer(child_marks, many=True).data,
                })
            return Response({
                'user': UserListSerializer(user).data,
                'children': payload,
            })

        if role == 'teacher':
            schedule = Schedule.objects.filter(teacher=user)
            return Response({
                'user': UserListSerializer(user).data,
                'today_schedule': ScheduleSerializer(schedule, many=True).data,
            })

        # admin / director / head_teacher / clerk / helper
        return Response({
            'user': UserListSerializer(user).data,
            'role': role,
            'message': 'Management Dashboard',
        })
