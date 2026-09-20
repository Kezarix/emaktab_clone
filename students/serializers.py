from django.apps import apps
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Subject, StudyGroup, Schedule, CalendarLesson, Mark, HomeworkSubmission

User = get_user_model()
SchoolGradeModel = apps.get_model('school', 'SchoolGrade')


# ---------- Brief serializers ----------

class ShortSchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolGradeModel
        fields = ['id', 'number', 'letter']


class ShortTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class StudentBriefSerializer(serializers.ModelSerializer):
    school_class = ShortSchoolClassSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'school_class']


# ---------- Full serializers ----------

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'first_name', 'last_name',
            'email', 'phone', 'fathers_name', 'school_class', 'birth_date', 'parents',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False, 'allow_null': True},
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
    school_class = ShortSchoolClassSerializer(read_only=True)

    class Meta:
        model = StudyGroup
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    school_class = ShortSchoolClassSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    teacher = ShortTeacherSerializer(read_only=True)
    day_of_week_display = serializers.CharField(
        source='get_day_of_week_display', read_only=True
    )

    class Meta:
        model = Schedule
        fields = (
            'id', 'school_class', 'subject', 'teacher',
            'day_of_week', 'day_of_week_display',
            'start_time', 'end_time', 'classroom',
        )
        ref_name = 'StudentsSchedule'


class CalendarLessonSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(read_only=True)

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
    student = StudentBriefSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'),
        source='student',
        write_only=True,
    )

    value = serializers.ChoiceField(
        choices=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                 'S', 'I', 'A', 'T', 'L']
    )

    class Meta:
        model = Mark
        fields = '__all__'
        ref_name = 'StudentsAttendanceAndGrade'


class TeacherLessonSerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(read_only=True)

    class Meta:
        model = CalendarLesson
        fields = ['id', 'date', 'schedule']


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.username', read_only=True)
    subject_name = serializers.CharField(source='lesson.schedule.subject.name', read_only=True)
    lesson_date = serializers.DateField(source='lesson.date', read_only=True)
    lesson_time = serializers.TimeField(source='lesson.schedule.start_time', read_only=True)

    class Meta:
        model = HomeworkSubmission
        fields = [
            'id', 'lesson', 'student', 'student_name', 'subject_name',
            'lesson_date', 'lesson_time', 'text_answer',
            'file_answer', 'created_at',
        ]
        read_only_fields = ['student']

    def validate(self, attrs):
        if not attrs.get('text_answer') and not attrs.get('file_answer'):
            raise serializers.ValidationError("You must write text or file answer")
        return attrs


