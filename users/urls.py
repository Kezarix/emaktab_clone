from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScheduleViewSet, UserViewSet, DashboardAPIView

router = DefaultRouter()

router.register(r'list', UserViewSet, basename='users-list')
router.register(r'schedules', ScheduleViewSet, basename='schedule')

urlpatterns = [
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path('', include(router.urls)),
]