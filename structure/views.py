
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User
from school.models import SchoolGrade

from .serializers import (
    UserSerializer,
    SchoolGradeSerializer
)
from .permissions import IsSystemAdmin


class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSystemAdmin]


class SchoolGradeViewSet(viewsets.ModelViewSet):
    queryset = SchoolGrade.objects.all()
    serializer_class = SchoolGradeSerializer
    permission_classes = [IsSystemAdmin]
