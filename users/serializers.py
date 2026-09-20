from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'fathers_name', 'phone', 'role', 'birth_date',
            'school_class', 'is_staff',
        ]
        ref_name = 'UsersUserList'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'fathers_name',
            'email', 'phone', 'role', 'password',
        )
        ref_name = 'StructureUser'

    def create(self, validated_data):
        password = validated_data.pop('password', None) or None
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
