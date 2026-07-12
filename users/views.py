from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from students.models import Schedule
from .serializers import UserListSerializer
from students.serializers import ScheduleSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff or user.role in ['admin', 'director', 'head_teacher']:
            return User.objects.all()
        return User.objects.filter(id=user.id)


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_superuser or user.is_staff or user.role in ['admin', 'director', 'head_teacher']):
            return Response(
                {"detail": "You do not have permission to modify the schedule."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)