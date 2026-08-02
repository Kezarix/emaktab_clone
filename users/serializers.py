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