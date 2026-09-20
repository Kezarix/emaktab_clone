from rest_framework import serializers
from django.contrib.auth import get_user_model
from school.models import SchoolGrade
from .models import SupportMessage, SupportChat

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'fathers_name',
            'email', 'phone', 'role',
        )
        ref_name = 'StructureUser'


class TeacherBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


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
        ref_name = 'StructureSchoolGrade'


class SupportMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)

    class Meta:
        model = SupportMessage
        fields = ['id', 'text', 'sender', 'sender_name', 'created_at']
        read_only_fields = ['sender']

    def validate(self, attrs):
        request = self.context.get('request')
        chat_id = self.context['view'].kwargs.get('chat_id')

        try:
            chat = SupportChat.objects.get(pk=chat_id)
        except SupportChat.DoesNotExist:
            raise serializers.ValidationError("Chat not found")

        user = request.user
        is_chat_owner = (user.id == chat.user_id)
        is_helper = getattr(user, 'role', None) in ['helper', 'admin']

        if not is_chat_owner and not is_helper:
            raise serializers.ValidationError("You have no permission to write in this chat")

        attrs['chat'] = chat
        return attrs


class SupportChatSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    messages = SupportMessageSerializer(many=True, read_only=True)

    class Meta:
        model = SupportChat
        fields = ['id', 'user', 'updated_at', 'messages']
        ref_name = 'StructureSupportChat'
