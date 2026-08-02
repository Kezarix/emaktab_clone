from django.contrib.auth import get_user_model
from rest_framework import viewsets
from school.models import SchoolGrade

from .serializers import (
    UserSerializer,
    SchoolGradeSerializer
)
from .permissions import IsSystemAdmin

User = get_user_model()


class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSystemAdmin]


class SchoolGradeViewSet(viewsets.ModelViewSet):
    queryset = SchoolGrade.objects.all()
    serializer_class = SchoolGradeSerializer
    permission_classes = [IsSystemAdmin]