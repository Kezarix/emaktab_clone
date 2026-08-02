from rest_framework import permissions


class IsAdminOrDirector(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(
            request.user.is_superuser or
            request.user.is_staff or
            getattr(request.user, 'role', None) in ['admin', 'director']
        )


class IsManagement(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(
            request.user.is_superuser or
            request.user.is_staff or
            getattr(request.user, 'role', None) in ['admin', 'director', 'head_teacher']
        )


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(
            request.user.is_superuser or
            request.user.is_staff or
            getattr(request.user, 'role', None) in ['admin', 'teacher']
        )


class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)

        user = request.user
        return bool(
            user and user.is_authenticated and (
                user.is_superuser or
                user.is_staff or
                getattr(user, 'role', None) in ['admin', 'director', 'head_teacher', 'teacher']
            )
        )