from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import SchoolGrade, AcademicLoad
from .serializers import SchoolGradeSerializer, AcademicLoadSerializer
from structure.permissions import IsSystemAdmin


class SchoolGradeViewSet(viewsets.ModelViewSet):
    queryset = SchoolGrade.objects.select_related('class_teacher').all()
    serializer_class = SchoolGradeSerializer
    permission_classes = [IsAuthenticated]


class AcademicLoadViewSet(viewsets.ModelViewSet):
    queryset = AcademicLoad.objects.select_related('teacher', 'subject', 'school_grade').all()
    serializer_class = AcademicLoadSerializer
    permission_classes = [IsAuthenticated]
