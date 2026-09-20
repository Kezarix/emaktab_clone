from django.urls import path, include
from rest_framework.routers import DefaultRouter
from structure.views import (
    UserManagementViewSet,
    SchoolGradeViewSet,
    SupportChatViewSet,
    SupportMessageViewSet,
)

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='structure-users')
router.register(r'grades', SchoolGradeViewSet, basename='structure-grades')
router.register(r'support-chats', SupportChatViewSet, basename='support-chat')
router.register(
    r'support-chats/(?P<chat_id>[^/.]+)/messages',
    SupportMessageViewSet,
    basename='support-message',
)

urlpatterns = [
    path('', include(router.urls)),
]