from django.urls import path, include
from rest_framework.routers import DefaultRouter
from structure.views import (
    UserManagementViewSet, SchoolGradeViewSet,
)

router = DefaultRouter()
router.register(r'users', UserManagementViewSet)
router.register(r'grades', SchoolGradeViewSet)


urlpatterns = [
    path('', include(router.urls)),
]