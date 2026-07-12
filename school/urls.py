from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  SchoolGradeViewSet

router = DefaultRouter()
router.register(r'grades', SchoolGradeViewSet, basename='manage-grades')

urlpatterns = [
    path('', include(router.urls)),
]