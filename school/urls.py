from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SchoolGradeViewSet, AcademicLoadViewSet

router = DefaultRouter()
router.register(r'grades', SchoolGradeViewSet, basename='manage-grades')
router.register(r'academic-loads', AcademicLoadViewSet, basename='academic-load')


urlpatterns = [
    path('', include(router.urls)),
]