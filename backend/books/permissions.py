from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return True if request.method in SAFE_METHODS else (request.user and request.user.is_staff)
