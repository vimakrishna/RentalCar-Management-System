from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff


class OwnerOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.user.is_staff or 
                obj.created_by == request.user
        )