from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SchoolGrade, AcademicLoad
from students.models import Subject

User = get_user_model()


class TeacherBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class SubjectBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class SchoolGradeSerializer(serializers.ModelSerializer):
    class_teacher = TeacherBriefSerializer(read_only=True)
    class_teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='teacher'),
        source='class_teacher',
        write_only=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = SchoolGrade
        fields = ['id', 'number', 'letter', 'class_teacher', 'class_teacher_id']
        ref_name = 'SchoolSchoolGrade'


class AcademicLoadSerializer(serializers.ModelSerializer):
    teacher = TeacherBriefSerializer(read_only=True)
    subject = SubjectBriefSerializer(read_only=True)
    school_grade = serializers.PrimaryKeyRelatedField(read_only=True)
    school_grade_info = SchoolGradeSerializer(source='school_grade', read_only=True)

    class Meta:
        model = AcademicLoad
        fields = ['id', 'teacher', 'subject', 'school_grade', 'school_grade_info']
        ref_name = 'SchoolAcademicLoad'
