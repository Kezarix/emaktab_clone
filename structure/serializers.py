from rest_framework import serializers
from django.contrib.auth import get_user_model
from school.models import SchoolGrade
from .models import SupportMessage, SupportChat

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'fathers_name', 'email', 'phone', 'role')


class SchoolGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolGrade
        fields = '__all__'
        ref_name = 'StructureSchoolGrade'


class SupportMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)

    class Meta:
        model = SupportMessage
        fields = ['id', 'text', 'sender_name', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        chat_id = self.context['view'].kwargs.get('chat_id')

        try:
            chat = SupportChat.objects.get(pk=chat_id)
        except SupportChat.DoesNotExist:
            raise serializers.ValidationError("Chat not found")

        user = request.user

        is_chat_owner = (user.id == chat.user_id)
        is_helper = (getattr(user, 'role', None) in ['helper', 'admin'])

        if not is_chat_owner and not is_helper:
            raise serializers.ValidationError("You have no permission to write in this chat")

        attrs['chat'] = chat
        return attrs