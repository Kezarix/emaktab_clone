from rest_framework import serializers
from django.contrib.auth import get_user_model
from students.models import Mark, Schedule

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'fathers_name', 'phone', 'role', 'birth_date', 'school_class', 'is_staff'
        ]


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = '__all__'


class ChildDashboardSerializer(serializers.Serializer):
    child_info = UserListSerializer(read_only=True)
    today_schedule = ScheduleSerializer(many=True, read_only=True)
    recent_marks = MarkSerializer(many=True, read_only=True)


class StudentDashboardSerializer(serializers.Serializer):
    user = UserListSerializer(read_only=True)
    today_schedule = ScheduleSerializer(many=True, read_only=True)
    recent_marks = MarkSerializer(many=True, read_only=True)


class ParentDashboardSerializer(serializers.Serializer):
    user = UserListSerializer(read_only=True)
    children = ChildDashboardSerializer(many=True, read_only=True)


class TeacherDashboardSerializer(serializers.Serializer):
    user = UserListSerializer(read_only=True)
    today_schedule = ScheduleSerializer(many=True, read_only=True)