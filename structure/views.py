from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from school.models import SchoolGrade
from .models import SupportChat, SupportMessage
from .serializers import (
    UserSerializer,
    SchoolGradeSerializer,
    SupportChatSerializer,
    SupportMessageSerializer,
)
from .permissions import IsSystemAdmin

User = get_user_model()


# ============================================================
# USERS (admin only)
# ============================================================

class UserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSystemAdmin]


# ============================================================
# SCHOOL GRADES (admin only)
# ============================================================

class SchoolGradeViewSet(viewsets.ModelViewSet):
    queryset = SchoolGrade.objects.select_related('class_teacher').all()
    serializer_class = SchoolGradeSerializer
    permission_classes = [IsSystemAdmin]


# ============================================================
# SUPPORT CHATS
# ============================================================

class SupportChatViewSet(viewsets.ModelViewSet):
    serializer_class = SupportChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return SupportChat.objects.none()
        role = getattr(user, 'role', None)
        if role in ['helper', 'admin']:
            return SupportChat.objects.select_related('user').all()
        return SupportChat.objects.select_related('user').filter(user=user)


class SupportMessageViewSet(viewsets.ModelViewSet):
    serializer_class = SupportMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        if not chat_id:
            return SupportMessage.objects.none()
        return SupportMessage.objects.select_related('sender', 'chat').filter(chat_id=chat_id)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)