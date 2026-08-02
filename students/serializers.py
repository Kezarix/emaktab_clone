from django.apps import apps
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Subject, StudyGroup, Schedule, CalendarLesson, Mark
from rest_framework import viewsets, exceptions
from rest_framework.permissions import IsAuthenticated
from .models import HomeworkSubmission

User = get_user_model()
SchoolGradeModel = apps.get_model('school', 'SchoolGrade')


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'first_name', 'last_name',
            'email', 'phone', 'fathers_name', 'school_class', 'birth_date', 'parents'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        parents_data = validated_data.pop('parents', [])
        validated_data['role'] = 'student'
        user = User.objects.create_user(**validated_data)
        if parents_data:
            user.parents.set(parents_data)
        return user


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class StudyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyGroup
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.school_class:
            representation['school_class'] = ShortSchoolClassSerializer(instance.school_class).data
        return representation


class ShortSchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolGradeModel
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('curator', None)
        representation.pop('class_teacher', None)
        representation.pop('teacher', None)
        return representation


class ShortTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = (
            'id',
            'school_class',
            'subject',
            'teacher',
            'day_of_week',
            'start_time',
            'end_time',
            'classroom',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['day_of_week'] = instance.get_day_of_week_display()

        if instance.school_class:
            representation['school_class'] = ShortSchoolClassSerializer(instance.school_class).data

        if instance.subject:
            representation['subject'] = SubjectSerializer(instance.subject).data

        if instance.teacher:
            representation['teacher'] = ShortTeacherSerializer(instance.teacher).data

        return representation


class CalendarLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarLesson
        fields = '__all__'

    def validate(self, attrs):
        homework = attrs.get('homework')
        homework_file = attrs.get('homework_file')
        homework_url = attrs.get('homework_url')

        if not homework and not homework_file and not homework_url:
            raise serializers.ValidationError(
                "You must fill in at least one homework field: text, file, or URL."
            )

        return attrs


class AttendanceAndGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.student:
            representation['student'] = ShortTeacherSerializer(instance.student).data

            if instance.student.school_class:
                representation['school_class'] = ShortSchoolClassSerializer(instance.student.school_class).data

        return representation


class TeacherLessonSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(read_only=True)

    class Meta:
        model = CalendarLesson
        fields = ['id', 'date', 'schedule']



class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField(source='student.username')
    subject_name = serializers.ReadOnlyField(source='lesson.schedule.subject.name', default='Не указан')
    lesson_date = serializers.ReadOnlyField(source='lesson.date')
    lesson_time = serializers.ReadOnlyField(source='lesson.schedule.start_time')

    class Meta:
        model = HomeworkSubmission
        fields = [
            'id', 'lesson', 'student', 'subject_name',
            'lesson_date', 'lesson_time', 'text_answer',
            'file_answer', 'created_at'
        ]

    def validate(self, attrs):
        if not attrs.get('text_answer') and not attrs.get('file_answer'):
            raise serializers.ValidationError("You must write text or file answer")
        return attrs