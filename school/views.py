from rest_framework import viewsets
from .models import SchoolGrade
from .serializers import  SchoolGradeSerializer
from structure.permissions import IsSystemAdmin


class SchoolGradeViewSet(viewsets.ModelViewSet):
    queryset = SchoolGrade.objects.all()
    serializer_class = SchoolGradeSerializer
    permission_classes = [IsSystemAdmin]